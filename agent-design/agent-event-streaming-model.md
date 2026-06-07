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
last_reviewed: 2026-06-01
---

# Agent Event Streaming: Consumer Contract Above the Tokens

> A typed event stream the harness emits at decision points. UIs subscribe to this contract instead of raw token deltas, surviving model and harness swaps.

An agent event stream is the typed, ordered sequence of events the harness emits at decision points: tool dispatched, tool returned, sub-agent spawned, state updated, run finished. It sits above the LLM's token-level SSE ([Claude API streaming](https://docs.claude.com/en/build-with-claude/streaming): `message_start`, `content_block_delta`, `content_block_stop`) and below the app's domain model — the contract lives where the agent decides, not where the model emits letters.

## Token Stream vs Agent Stream

| Stream | Producer | Granularity | Vocabulary | Stability across model/harness swap |
|--------|----------|-------------|-----------|-------------------------------------|
| Token | LLM SDK | One token chunk per delta | Provider-specific (`content_block_delta`, `delta.text`) | Breaks on model swap ([Claude API streaming](https://docs.claude.com/en/build-with-claude/streaming)) |
| Agent | Harness | One event per decision | Semantic verbs (`RunStarted`, `ToolCallStart`, `StateDelta`) | Survives model swap ([AG-UI events](https://docs.ag-ui.com/concepts/events)) |

LangGraph names both modes: `stream_mode="messages"` yields token chunks; `stream_mode="updates"` "emits an event after every agent step" ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)). Production deployments subscribe to both — tokens drive the typing animation, updates drive tool indicators, sub-agent tabs, and approval prompts.

## The Event Vocabulary

The AG-UI Protocol — an open standard with integrations across LangGraph, CrewAI, Google ADK, Pydantic AI, and others — groups events into seven categories ([AG-UI events](https://docs.ag-ui.com/concepts/events)):

- **Lifecycle**: `RunStarted`, `StepStarted`, `StepFinished`, `RunFinished`, `RunError` — bounds and progress markers carrying `threadId`, `runId`, and an optional `parentRunId`.
- **Tool Call**: `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolCallResult`. The Vercel AI SDK Data Stream Protocol uses the same shape with different names — `tool-input-start`, `tool-input-delta`, `tool-input-available`, `tool-output-available` ([Vercel AI SDK](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol)).
- **Text Message**: `TextMessageStart`, `TextMessageContent`, `TextMessageEnd` — message-level streaming above tokens.
- **State**: `StateSnapshot`, `StateDelta` — typed shared store between agent and frontend, event-sourced.
- **Reasoning**: `ReasoningStart`, `ReasoningMessageContent`, `ReasoningMessageEnd` — LangChain normalises Anthropic `thinking` and OpenAI `reasoning` blocks into one `reasoning` content-block type ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)).
- **Activity**, **Special** (Custom, Raw) — escape hatches for harness-specific work.

The categories are the load-bearing design choice. Subscribe by category — "render all Tool Call events" — and the consumer survives new event types within it. Hardcode names and it does not.

## Why It Works

The agent stream inverts consumer stability. A token-stream consumer commits to LLM-output deltas — when the harness adds a sub-agent spawn, a guardrail, or a tool retry, none appear in the token stream, so the consumer infers them only by parsing the assembled message. An agent-stream consumer commits to harness-decision verbs, so it renders affordances — approval modals, sub-agent tabs, retry indicators — directly rather than reconstructing them from tokens ([AG-UI events](https://docs.ag-ui.com/concepts/events)). Swapping the LLM (Anthropic → Gemini → OpenAI) replaces the token stream but leaves the verbs intact — the abstraction inversion event-sourcing applies to databases ([Fowler, EventSourcing](https://martinfowler.com/eaaDev/EventSourcing.html)), at the harness/LLM boundary.

## Versioning the Event Schema

Event-driven consumers outlive the producer code, so the vocabulary needs additive-only evolution ([theburningmonk, event versioning strategies](https://theburningmonk.com/2025/04/event-versioning-strategies-for-event-driven-architectures/)). The Confluent compatibility taxonomy applies directly: new event types and optional fields are safe (consumers ignore unknowns); renames and removals break every consumer at once because each event carries semantic weight ([Confluent schema compatibility](https://developer.confluent.io/patterns/event-stream/schema-compatibility/)). When a shape must change, ship an upcaster at the consumer boundary. The discipline matters more than in a Kafka pipeline because each event renders in a user-facing UI.

## When This Backfires

The pattern adds a vocabulary-design and versioning obligation that does not pay off everywhere. Stay with raw token streams when:

- **Pure conversational chat UIs** — step events at the bubble layer hide the time-to-first-token signal users expect. Reported TTFT with token streaming is typically 200–500 ms versus a 5–30 s wait for the full response without it ([thefrontkit, streaming UI guide](https://thefrontkit.com/blogs/what-is-streaming-ui-in-ai-applications)); dropping that channel makes the interface feel broken even when latency is unchanged.
- **Single-harness, single-vendor stacks** — the portability benefit disappears; raw SDK events (Anthropic SSE, OpenAI deltas) are cheaper.
- **Ad-hoc payloads that mirror harness internals** — if `tool_call_started` carries the harness's node name, retry count, or framework-specific tool ID, the UI couples to the harness; the vocabulary must be designed semantically, not echoed from the runtime.
- **Renames are tolerated** — without additive-only discipline, event-stream consumers degrade *worse* than token-stream ones because each event carries semantic weight ([theburningmonk](https://theburningmonk.com/2025/04/event-versioning-strategies-for-event-driven-architectures/)).

The dominant production shape runs both streams in parallel ([LangChain streaming docs](https://docs.langchain.com/oss/python/langchain/streaming)). The agent stream replaces tokens only when the product is agent-as-coworker — IDE pair, research dashboard, ops console — not agent-as-chatbot.

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
