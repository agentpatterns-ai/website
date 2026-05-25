---
title: "Agent Event Streaming: Consumer Contract Above the Tokens"
description: "Subscribe UIs to harness-decision events — tool calls, sub-agents, run lifecycle — instead of raw LLM token deltas so the contract survives model and harness swaps."
tags:
  - agent-design
  - observability
  - tool-agnostic
aliases:
  - agent stream
  - agent-step events
  - agent event stream
---

# Agent Event Streaming: Consumer Contract Above the Tokens

> A typed event stream emitted by the harness — run started, tool called, sub-agent spawned, state updated, run finished — that UIs subscribe to instead of, or alongside, raw LLM token deltas, so the consumer contract survives model and harness swaps.

An agent event stream is the typed, ordered sequence of events the harness emits at decision points: tool dispatched, tool returned, sub-agent spawned, state updated, run finished. It sits above the LLM's token-level SSE ([Claude API streaming](https://docs.claude.com/en/build-with-claude/streaming): `message_start`, `content_block_delta`, `content_block_stop`) and below the application's domain model. The contract lives where the agent decides, not where the model emits letters.

## Token Stream vs Agent Stream

| Stream | Producer | Granularity | Vocabulary | Stability across model/harness swap |
|--------|----------|-------------|-----------|-------------------------------------|
| Token | LLM SDK | One token chunk per delta | Provider-specific (`content_block_delta`, `delta.text`) | Breaks on model swap ([Claude API streaming](https://docs.claude.com/en/build-with-claude/streaming)) |
| Agent | Harness | One event per decision | Semantic verbs (`RunStarted`, `ToolCallStart`, `StateDelta`) | Survives model swap ([AG-UI events](https://docs.ag-ui.com/concepts/events)) |

LangGraph names both modes: `stream_mode="messages"` yields token chunks; `stream_mode="updates"` "emits an event after every agent step" ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)). Production deployments subscribe to both — `stream_mode=["updates", "messages"]` — because tokens drive the typing animation while updates drive tool indicators, sub-agent tabs, and approval prompts.

## The Event Vocabulary

The AG-UI Protocol — an open standard with integrations across LangGraph, CrewAI, Microsoft Agent Framework, Google ADK, AWS Strands, Pydantic AI, and LlamaIndex — groups events into seven categories ([AG-UI events](https://docs.ag-ui.com/concepts/events)):

- **Lifecycle**: `RunStarted`, `StepStarted`, `StepFinished`, `RunFinished`, `RunError` — bounds and progress markers; carry `threadId`, `runId`, and an optional `parentRunId` for branching.
- **Tool Call**: `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolCallResult`. The Vercel AI SDK Data Stream Protocol uses the same shape with different names — `tool-input-start`, `tool-input-delta`, `tool-input-available`, `tool-output-available` ([Vercel AI SDK Stream Protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol)).
- **Text Message**: `TextMessageStart`, `TextMessageContent`, `TextMessageEnd` — message-level streaming above the token stream.
- **State**: `StateSnapshot`, `StateDelta` — typed shared store between agent and frontend, with event-sourced diffs.
- **Reasoning**: `ReasoningStart`, `ReasoningMessageContent`, `ReasoningMessageEnd` — normalised across Anthropic `thinking` and OpenAI `reasoning` blocks into one `reasoning` content-block type by LangChain ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)).
- **Activity** and **Special** (Custom, Raw) — escape hatches for harness-specific work.

The categories are the load-bearing design choice. Subscribe by category — "render all Tool Call events" — and the consumer survives new event types within the category. Hardcode individual type names and it does not.

## Why It Works

The agent stream inverts consumer stability. A token-stream consumer commits to LM-output deltas — when the harness adds a sub-agent spawn, a guardrail, or a tool retry, none of those events appear in the token stream; the consumer can only infer them by parsing the assembled message. An agent-stream consumer commits to harness-decision verbs (run started, tool called, state updated). The contract sits where state changes happen, so the consumer renders meaningful affordances — approval modals, sub-agent tabs, retry indicators — without reconstructing them from tokens ([AG-UI events](https://docs.ag-ui.com/concepts/events)). Swapping the LLM (Anthropic → Gemini → OpenAI) replaces the token stream entirely but leaves the agent stream's verbs intact, because the harness emits them — the same abstraction inversion event-sourcing applies to databases ([Fowler, EventSourcing](https://martinfowler.com/eaaDev/EventSourcing.html)), adapted to the harness/LLM boundary.

## Versioning the Event Schema

Event-driven consumers outlive the producer code, so the vocabulary needs additive-only evolution ([theburningmonk, event versioning strategies](https://theburningmonk.com/2025/04/event-versioning-strategies-for-event-driven-architectures/)). The Confluent compatibility taxonomy applies directly: new event types and new optional fields are safe (consumers ignore unknowns); renames and removals break every consumer at once because each event carries semantic weight that cannot be silently re-derived ([Confluent schema compatibility](https://developer.confluent.io/patterns/event-stream/schema-compatibility/)). When a payload shape must change, ship an upcaster at the consumer boundary that translates the old event into the new shape. The discipline matters more here than in a typical Kafka pipeline because each agent event renders in an end-user UI — schema drift breaks the user-visible surface.

## When This Backfires

The pattern adds a vocabulary-design and versioning obligation that does not pay off for every product. Stay with raw token streams (or operator-only event streams) when:

- **Pure conversational chat UIs** — replacing token streaming with step events at the bubble layer hides the time-to-first-token signal users expect. Reported TTFT with token streaming is typically 200–500 ms versus a 5–30 s wait for the entire response without it ([thefrontkit, streaming UI guide](https://thefrontkit.com/blogs/what-is-streaming-ui-in-ai-applications)) — dropping that feedback channel makes the interface feel broken even when total latency is unchanged.
- **Single-harness, single-vendor stacks** — the portability benefit disappears; consuming the raw SDK events (Anthropic SSE, OpenAI deltas) is cheaper.
- **Ad-hoc payloads that mirror harness internals** — if `tool_call_started` carries the harness's node name, retry count, or framework-specific tool ID, the UI couples to the harness; vocabulary must be designed semantically, not whatever the runtime emits.
- **Backward-incompatible renames are tolerated** — without additive-only discipline, event-stream consumers degrade *worse* than token-stream consumers because each event carries semantic weight ([theburningmonk](https://theburningmonk.com/2025/04/event-versioning-strategies-for-event-driven-architectures/)).

The dominant production shape is to run both streams in parallel — `stream_mode=["updates", "messages"]` ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)). The agent stream replaces tokens only when the product is explicitly agent-as-coworker (IDE pair, research dashboard, ops console) rather than agent-as-chatbot.

## Example

In LangGraph v1.2+, subscribing to both streams yields step events from the update channel and token chunks from the message channel, distinguished by `chunk["type"]` ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)):

```python
async for chunk in graph.astream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["updates", "messages"],
):
    if chunk["type"] == "updates":
        # Agent stream: one event per node — model, tools, model again
        for step, data in chunk["data"].items():
            print(f"step={step}")
    elif chunk["type"] == "messages":
        # Token stream: AIMessageChunk and tool_call_chunk deltas
        token, metadata = chunk["data"]
```

The Vercel AI SDK Data Stream Protocol carries the same separation over SSE — tool-call lifecycle events are explicit parts of the stream, separate from text deltas ([Vercel AI SDK Stream Protocol](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol)):

```
data: {"type":"tool-input-start","toolCallId":"call_abc","toolName":"getWeather"}
data: {"type":"tool-input-delta","toolCallId":"call_abc","inputTextDelta":"San Francisco"}
data: {"type":"tool-input-available","toolCallId":"call_abc","toolName":"getWeather","input":{"city":"San Francisco"}}
data: {"type":"tool-output-available","toolCallId":"call_abc","output":{"weather":"sunny"}}
data: {"type":"finish-step"}
```

A frontend subscribing only to `tool-*` parts renders a tool-call indicator; a frontend subscribing only to text deltas renders the assistant bubble. The same backend feeds both — the discipline is keeping the event names and field shapes additive over time.

## Key Takeaways

- An agent event stream is a typed event sequence at harness decision points (`RunStarted`, `ToolCallStart`, `StateDelta`, `RunFinished`); the consumer contract one layer above LLM token SSE ([AG-UI events](https://docs.ag-ui.com/concepts/events), [Claude API streaming](https://docs.claude.com/en/build-with-claude/streaming)).
- The convergent vocabulary across AG-UI, LangGraph, and the Vercel AI SDK groups events into lifecycle, tool-call, text-message, state, reasoning, and custom/special categories — subscribe by category, not by individual event name.
- The mechanism is abstraction inversion: the harness is the event source of truth; token streams and DOM updates are projections. Model swaps change the projection, not the contract.
- Versioning is the load-bearing obligation. Additive-only changes survive; renames and removals break every consumer at once because each event carries product meaning ([theburningmonk](https://theburningmonk.com/2025/04/event-versioning-strategies-for-event-driven-architectures/), [Confluent schema compatibility](https://developer.confluent.io/patterns/event-stream/schema-compatibility/)).
- Most production deployments run both streams — token deltas for the chat bubble, step events for everything else. Replace tokens with events only when the product is agent-as-coworker, not agent-as-chatbot ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming), [thefrontkit, streaming UI guide](https://thefrontkit.com/blogs/what-is-streaming-ui-in-ai-applications)).

## Related

- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md) — the underlying loop whose step boundaries the agent stream exposes
- [Delta Channels: Bounded Checkpoint Storage for Append-Only Agent State](delta-channels-checkpoint-storage.md) — runtime-side delta primitive; the agent stream is the consumer-side counterpart
- [Event Sourcing for Agents](../observability/event-sourcing-for-agents.md) — server-side append-only event log; the agent stream is its consumer-facing projection
- [Agent Debug Log Panel: Chronological Event Inspection](../observability/agent-debug-log-panel.md) — operator UI built on the same event stream, separate from the user-facing transcript
- [Agent Loop Middleware](agent-loop-middleware.md) — where harness-decision events are emitted from in practice — middleware nodes at loop boundaries
