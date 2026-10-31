---
title: "Durable Turn Log for Agent Crash Recovery"
term: "Durable Turn Log"
description: "Record an intent before every model and tool call and an outcome after it, so a replacement process resumes the turn from the log instead of restarting it. Assess logging overhead, lost work, and how interrupted effects can be recovered safely."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - write-ahead turn log
  - per-call intent and outcome log
  - durable agent turn resume
last_reviewed: 2026-10-23
maturity: emerging
---

# Durable Turn Log for Agent Crash Recovery

> A durable turn log records an intent before each call and an outcome after, so a replacement process resumes the turn.

Log every model and tool call twice, before and after, when losing a turn costs more than the two writes. Vercel's `durable-harness` is explicit about the shape: it "writes each step of a turn to a durable log. Before a model call or tool call runs, it records an intent, and when the call finishes, it records the outcome" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)). A replacement process reads the log rather than starting over. What that buys is narrower than the word durable suggests, so take the conditions first.

## When it pays

Assess these three conditions before choosing the recovery mechanism.

1. The process can die independently of the work. In the cloud, "the VM doesn't automatically record which model and tool calls completed or resume interrupted turns after a crash" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)). Function timeouts, queue redelivery, and deploys all end a process mid-turn.
2. The lost work is expensive. This reuse requires the outcome to have reached the durable log; an external operation can finish before that record is saved. "Completed calls never run again because their results are read from the log, so you're never billed twice for a finished model call's tokens" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)).
3. The side effects tolerate the ambiguity that remains. The log identifies calls with an intent but no recorded outcome, and completing that call exactly once belongs to the write contract.

## What the log records

Two records per call produce three distinguishable states on recovery: "After a crash, the log says what finished, what was running, and what never started" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)). Finished calls are replayed from their recorded results, calls that never started simply run, and only the middle class is ambiguous.

A harness that keeps its own session files does not give them up. Claude Code's transcript, Codex's rollout, and OpenCode's event store "have every record mirrored into the log, so a new function or Sandbox rebuilds them from it" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)). Where that workspace lives is a separate decision, and the same source notes that not every agent task needs a sandbox.

## Declaring replay safety per tool

Replay safety is a property of each tool, declared where the tool is defined. Two values cover it: "Interrupted tools marked `replay: 'safe'` run again. Any other tool comes back to the model as possibly run, and the model decides whether to check" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)). A lookup is safe to repeat. A refund is not, so "the model is told the call may have happened, so it can check before it tries again" ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)).

The second value reports uncertainty; it does not make the external write exactly-once. The model may need an idempotency key, a reliable status query, or human reconciliation.

## Why it works

Splitting one record into two converts a single bit, did this call run, into three states a recovering process can act on separately. The recorded outcome substitutes for re-execution, which is what durable-execution engines already rely on: "The return values of activity functions are always safe for replay because they're saved into the orchestration history" ([Azure durable orchestrator code constraints](https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-code-constraints)). [Event Sourcing for Agents](../../observability/event-sourcing-for-agents.md) covers that append-only form in general; the turn log applies it at the granularity of one model or tool call. Recording is not an optimization, because an agent's calls cannot be re-run to the same result. Temporal states the constraint: "A Workflow Definition must be deterministic to support replay. To handle non-deterministic operations like API calls, LLM/AI invocations, database queries, and other external interactions, put them in Activities" ([Temporal workflow definition](https://docs.temporal.io/workflow-definition)). A model call is exactly that, so a resumed turn can only read its result back.

## When this backfires

- Short, cheap turns. Two durable writes per call plus a queue backstop recover work a plain retry would redo in seconds. Vercel publishes no overhead figure, so the trade cannot be sized from the source.
- A tool call that outlives the backstop. The queue handing off the turn is at-least-once: "Consumer timeouts: If your function processes a message but doesn't acknowledge it before the visibility timeout expires, Vercel assumes the delivery failed and redelivers the message" ([Vercel Queues concepts](https://vercel.com/docs/queues/concepts)). Without a separate ownership or concurrency control, redelivery can overlap a still-running consumer. The intent/outcome log alone does not distinguish that case from a dead process.
- An interrupted write that is not idempotent. Telling the model a call may have run does not make it recoverable. In Li et al.'s late-commit and redelivery episodes, the frontier models duplicate in 56% and 74% respectively. The authors conclude that "model-side reasoning can at best decline to act (escalate, or report the operation as uncertain); it cannot complete the task exactly once on a key-less write" ([Li, arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). The same study reports that "agents reported success in 90% of the episodes in which they had duplicated an effect", so a reported success is not reliable evidence against duplication. What moved the rate was the contract: given a write that accepts an idempotency key, "agents attach them in 98% of episodes and the duplicate rate falls from 28% to 4% with no other change". Which layer owns that gap is covered in [Exactly-Once Enforcement Layer](exactly-once-enforcement-layer.md).
- A deploy between the crash and the resume. The log was written against one tool set and is replayed against another. Replay compatibility must survive the change: "The Workflow Definition can change in very limited ways once there is a Workflow Execution depending on it" ([Temporal workflow definition](https://docs.temporal.io/workflow-definition)).
- A misdeclared `replay: 'safe'`. The flag is a human judgement kept in the tool definition. A lookup that also writes a non-idempotent audit row may not be safe to repeat, and nothing in the log catches the mistake.

Coarser recovery is a real alternative. OpenClaw keeps conversations and transcripts "in the per-agent SQLite database", and a running root session at graceful shutdown "Receives one resume input at the next startup" ([OpenClaw restart recovery](https://docs.openclaw.ai/gateway/restart-recovery)). That is session-level resume after a graceful shutdown, not a per-call replay guarantee after a crash.

## Example

The declaration sits beside the tool, so the policy is reviewable with the code that implements it. For a coding agent, Vercel marks a tool that reads a file or checks CI status as `'safe'`, and a tool that posts a PR comment as `'never'`. Its published code example uses an order service, where the same two values separate a lookup from a refund ([Vercel, 2026](https://vercel.com/blog/making-every-harness-durable)):

```ts
const tools: HostTool[] = [
  {
    name: 'get_order',
    description: 'Looks up an order',
    replay: 'safe', // safe to run again after a crash
    inputSchema: { type: 'object', properties: { id: { type: 'string' } }, required: ['id'] },
    execute: async ({ id }) => JSON.stringify(await getOrder(id)),
  },
  {
    name: 'refund_order',
    description: 'Refunds an order',
    replay: 'never', // never runs twice
    inputSchema: { type: 'object', properties: { id: { type: 'string' } }, required: ['id'] },
    execute: async ({ id }) => JSON.stringify(await refundOrder(id)),
  },
];
```

Two tools of the same shape get opposite automatic replay behavior from one field. The source comment "never runs twice" describes this replay policy; it is not an exactly-once guarantee for an external refund or a new model-issued call.

## Key Takeaways

- Record intent and outcome when recovery needs to distinguish these states. A single completion record cannot separate a call that never started from one that was interrupted.
- Budget the log against expected loss per turn: measure logging overhead against the cost and frequency of repeated work.
- Declare `replay` on every tool at definition time, and re-audit the `'safe'` set whenever a tool gains a side effect.
- Buy exactly-once from the write contract, typically an idempotency key. The log's possibly-run signal is a warning you route onward, not protection.
- Compare your backstop's redelivery window against your longest tool call before trusting the handoff, because a slow call looks identical to a dead process.

## Related

- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the session-level version of the same split, where the append-only log holds the authoritative state
- [Exactly-Once Enforcement Layer: Model, Harness or Contract](exactly-once-enforcement-layer.md) — which layer has to own a duplicate write when a read-back cannot settle it
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — designing the operations that a `'safe'` declaration asserts something about
- [Dual-Write Append-Mirror for Agent Transcript Externalization](dual-write-append-mirror-transcript.md) — getting the transcript off the local disk without blocking the agent on the remote store
