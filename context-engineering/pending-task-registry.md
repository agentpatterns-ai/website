---
title: "Pending Task Registry for Asynchronous Agent Tool Calls"
term: "Pending Task Registry"
description: "When an agent needs to track asynchronous work, a pending task registry binds model-chosen handles to calls and preserves those bindings throughout the conversation."
aliases:
  - async task registry
  - in-flight task registry
  - pending task handles
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-03
maturity: adopted
---

# Pending Task Registry for Asynchronous Agent Tool Calls

> A pending task registry binds handles to asynchronous calls when an agent needs to track work across turns and retrieve delayed results.

A pending task registry is the harness-side record binding every in-flight asynchronous tool call to a handle the model can name. The agent uses the handle to ask what is still running, and the harness returns each result on the call that started it.

## When this applies

The machinery pays back only under specific conditions. LiveKit sets the floor at work taking "more than a few seconds", naming a flight booking, a web search, and document processing as qualifying cases ([LiveKit, Async tools](https://docs.livekit.io/agents/logic/tools/async)). Two more conditions hold:

- The model can track pending state. GPT-4.1 led the AsyncTool benchmark at 38.06 overall, and going from two concurrent tasks to three dropped Gemini 2.5 Pro from 42.56 to 32.44 ([Shi et al., 2026](https://arxiv.org/abs/2605.27995v3)).
- The platform supports it. OpenAI's async tool calling is "supported by GPT-6 Astra and later models" and excludes hosted built-in tools ([OpenAI, Async tool calling](https://developers.openai.com/api/docs/guides/async-tool-calling)).

## How it works

Each implementation specifies a different part of the problem. Between them they cover four moves.

1. The model names the job. OpenAI recommends adding a `task_handle` to each async tool, and "your application binds it to the original API `call_id` and the running job" ([OpenAI](https://developers.openai.com/api/docs/guides/async-tool-calling)). The model supplies the name it later uses to wait.
2. The registry outlives the job. OpenAI's rule is to "Keep the registry for the entire conversation to prevent reuse of a completed task's handle" ([OpenAI](https://developers.openai.com/api/docs/guides/async-tool-calling)). That is what stops a stale result binding to a fresh request.
3. A shared tool reads job status. OpenRouter's built-in `task` tool is "a single fixed definition no matter how many async tools you register, so your tools' schemas stay untouched and the prompt cost stays flat" ([OpenRouter, Async Tools](https://openrouter.ai/docs/agent-sdk/call-model/async-tools)). When a cancellable tool is registered, LiveKit exposes `get_running_tasks()` and `cancel_task(call_id)`. These list and cancel only cancellable calls ([LiveKit](https://docs.livekit.io/agents/logic/tools/async)). Cancellation is opt-in and requires tools that can safely stop at any point.
4. Results arrive before status. OpenAI specifies the order: "Return each newly completed result on its original `call_id`, then return status on the wait call's own `call_id`" ([OpenAI](https://developers.openai.com/api/docs/guides/async-tool-calling)).

LiveKit distinguishes two positions for a delayed result. It ships separate instruction templates for a follow-up that "runs while the pending update is still the latest chat item" and for one that "runs after newer messages have arrived in the chat context" ([LiveKit](https://docs.livekit.io/agents/logic/tools/async)). One completion needs different framing depending on how far down the transcript it fell, which applies the recency effect [lost in the middle](lost-in-the-middle.md) describes to tool results.

## Example

This constructed illustration adapts [OpenAI's wait-tool example](https://developers.openai.com/api/docs/guides/async-tool-calling) to one price lookup. The price is illustrative.

The model emits a lookup and then waits for its handle:

```json
[
  {"type": "function_call", "name": "lookup_price", "async": true,
   "call_id": "call_widget",
   "arguments": "{\"sku\":\"WIDGET\",\"task_handle\":\"widget_price_1\"}"},
  {"type": "function_call", "name": "wait_for_tasks",
   "call_id": "call_wait",
   "arguments": "{\"task_handles\":[\"widget_price_1\"]}"}
]
```

The harness records `widget_price_1` against `call_widget` and starts the job before processing the wait. On completion, the next request's `input` contains:

```json
[
  {"type": "function_call_output", "call_id": "call_widget",
   "output": "{\"task_handle\":\"widget_price_1\",\"price_cents\":1200,\"currency\":\"USD\"}"},
  {"type": "function_call_output", "call_id": "call_wait",
   "output": "{\"status\":\"completed\",\"completed_task_handles\":[\"widget_price_1\"]}"}
]
```

The price returns on `call_widget` before the status returns on `call_wait`. The harness retains the completed handle in the conversation's registry.

## Why it works

The registry makes the link between a delayed result and its original call explicit. OpenAI binds each model-chosen handle to both the call and the running job ([OpenAI](https://developers.openai.com/api/docs/guides/async-tool-calling)). This lets the model request outstanding results by name.

The benchmark evidence locates the failure in that binding. AsyncTool's error analysis found "the model forgetting about ongoing tasks", which "results in a high rate of incompletion failures, despite the model's high accuracy in completing subtasks" ([Shi et al., 2026](https://arxiv.org/abs/2605.27995v3)). Agents that could do each piece lost track of which pieces were outstanding. Models without temporal awareness go further and advance within a task "sometimes fabricating parameters based on assumed outcomes from prior calls". Without observable pending state, a model may invent a result.

## When this backfires

- Duplicate detection that only sees a name. LiveKit can reject, replace, or confirm a repeat call, but "Duplicates are detected by tool name only, not by arguments" ([LiveKit](https://docs.livekit.io/agents/logic/tools/async)), so two legitimate concurrent calls to one tool collide.
- Completions you never wanted. Under OpenRouter's `detach` mode "Tasks keep running, and results are dropped" ([OpenRouter](https://openrouter.ai/docs/agent-sdk/call-model/async-tools)). Declining a completion is a supported option that the registry makes you pay for anyway.
- Agents where instructions suffice. Google's agent-as-a-tool documentation tells the model to "ignore 'pending' results" and "Do NOT call the same tool again while waiting for a complete result" ([Google Cloud, Agent as a tool](https://docs.cloud.google.com/gemini-enterprise-cx/cx-agent-studio/tool/agent-as-tool)). This documents a prompt-based alternative to explicit handle management. It depends on the model following those instructions.
- Signals the model should not carry. LiveKit routes filler speech around the model for work "the LLM doesn't need to track" ([LiveKit](https://docs.livekit.io/agents/logic/tools/async)). Not every progress event belongs in context.

Harrison Chase, who named this challenge, asks "What if it's paused waiting for human approval?" ([Chase, 2026](https://www.langchain.com/blog/context-engineering-challenges-late-2026)). The registry answers that without new machinery, because a pending question is another handle. OpenAI keeps the question "pending in the same registry used by the wait tool", and OpenRouter's deferred lifecycle covers "a human review queue", pausing at `status: 'awaiting_async_tools'` until some process completes the task ([OpenAI](https://developers.openai.com/api/docs/guides/async-tool-calling); [OpenRouter](https://openrouter.ai/docs/agent-sdk/call-model/async-tools)).

## Key Takeaways

- Measure your slowest tool before building any of this. Under a few seconds, a blocking call is the cheaper correct answer.
- Audit the handle namespace rather than the handle format. Reuse across an already-completed task is the failure the vendor rules single out.
- Check how your framework matches a duplicate before you depend on rejection. Name-only matching turns two valid concurrent calls into a collision.
- Budget for the buried-result case. If a completion can arrive after newer turns, one injection template for both positions is not enough.
- File a pending human answer as another registry entry rather than a separate mechanism, and return an explicit no-answer result on timeout so the model is not left waiting on a question nobody answered.

## Related

- [Stateful Iteration State-Carry](stateful-iteration-state-carry.md) — keeps loop state outside the transcript behind a read tool, the same move applied to iteration rather than concurrency
- [Silent Handoff Failure in Delegated Code Search](silent-handoff-failure-delegated-search.md) — what breaks when delegated work reports back badly, measured at the planner-to-subagent seam
- [Lost in the Middle](lost-in-the-middle.md) — why a result's position in context changes how the model treats it
- [Goal Recitation](goal-recitation.md) — rewrites objectives at the context tail to counter drift, the recency lever used deliberately
- [Subtask Boundaries Over Delegation](subtask-boundaries-over-delegation.md) — declaring a scope inline instead of spawning a child agent, the cheaper alternative to concurrency
