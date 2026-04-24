---
title: "Exception Handling and Recovery Patterns for AI Coding Agents"
description: "Progressive failure response for coding agents: self-correct, fallback, degrade gracefully, escalate. Practical patterns from git-based recovery to model-driven adaptation."
tags:
  - agent-design
  - reliability
  - tool-agnostic
---

# Exception Handling and Recovery Patterns

> Agents fail. The question is whether they fail forward (recover and continue) or fail catastrophically (corrupt state, lose progress, repeat work).

Exception handling for coding agents is a progressive escalation — self-correct, fallback, degrade gracefully, escalate — that absorbs tool errors, model failures, and crashes without losing accumulated work.

## The Progressive Failure Hierarchy

```mermaid
graph LR
    A[Self-Correct] --> B[Fallback]
    B --> C[Degrade Gracefully]
    C --> D[Escalate]
    style A fill:#2d5a2d
    style B fill:#4a4a1a
    style C fill:#5a3a1a
    style D fill:#5a1a1a
```

**Self-correct**: detect the error and retry or adjust. Most tool errors resolve here — a failed file read triggers a path correction, a syntax error triggers a fix.

**Fallback**: when the primary approach fails repeatedly, switch to an alternative strategy or model.

**Degrade gracefully**: deliver partial results rather than failing entirely.

**Escalate**: surface the failure to a human with enough context. Last resort, not first response.

## Git-Based Recovery

Git is the primary recovery mechanism for coding agents. Anthropic's approach for long-running agents ([multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)):

- **Commit frequently** — each commit is a checkpoint
- **Write progress files** (e.g., `claude-progress.txt`) that survive session crashes — see [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md)
- **Revert to known-good states** with `git revert`

Git operations are cheap, atomic, and reversible. See [Rollback-First Design](rollback-first-design.md) for the broader principle.

## Model-Driven Error Adaptation

Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) reports that telling the model a tool is failing and letting it adapt works "surprisingly well" — the model reroutes without explicit fallback logic in the harness.

The simplest strategy: catch the tool error, include the message in the agent's next context, let the model decide. This outperforms rigid retry logic for novel failure modes.

!!! warning "When model-driven adaptation fails"
    This breaks down for **silent failures** — the agent produces output without detecting the underlying error (stale data, partial writes, skipped validation). The model has to *know* something went wrong. Add output validation and freshness checks for failure modes the model cannot observe directly.

## Durable Execution

For agents that must survive process crashes, durable execution frameworks checkpoint state after every step:

**LangGraph** provides [three durability modes](https://docs.langchain.com/oss/python/langgraph/durable-execution):

| Mode | Behavior | Use case |
|------|----------|----------|
| `exit` | Persist only at graph exit | Human-in-the-loop gates |
| `async` | Persist asynchronously while next step runs | Long-running research |
| `sync` | Persist synchronously before each step | Mission-critical workflows |

State is checkpointed to a configurable backend (Postgres, DynamoDB, others); after a crash, the agent resumes from the last checkpoint.

**DBOS** takes a decorator-based approach: [`@DBOS.workflow` and `@DBOS.step`](https://docs.dbos.dev/typescript/reference/workflows-steps) persist execution state automatically with exactly-once semantics.

Both solve the same problem: a 30-minute run should not lose all progress to a crash.

## Model Fallback

When a model provider fails, route to an alternative. LangChain's [`ModelFallbackMiddleware`](https://docs.langchain.com/oss/python/langchain/middleware/built-in) chains models automatically (`Primary → Fallback 1 → Fallback 2`), handling outages and rate limits — though different models may produce different results for the same prompt.

## Circuit Breakers for Tool Calls

A circuit breaker tracks consecutive failures for a tool and disables it after a threshold.

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: N consecutive failures
    Open --> HalfOpen: Timeout expires
    HalfOpen --> Closed: Probe succeeds
    HalfOpen --> Open: Probe fails
```

**Closed**: calls proceed, failures are counted. **Open**: calls are blocked, agent uses alternatives. **Half-open**: a single probe tests recovery.

Most coding agents use a lighter-weight version: count failures, tell the model the tool is unreliable, and let model-driven adaptation handle routing. Full state machines are more common in multi-agent systems with shared tool infrastructure.

## The Rollback-Over-Prevention Philosophy

Let agents make recoverable mistakes rather than preventing all mistakes: sandbox execution, review gates before permanent effects, session trees for fork/explore/discard, checkpoints at every meaningful boundary. Restrictive permissions limit capability more than they reduce risk. See [Rollback-First Design](rollback-first-design.md).

## When This Backfires

The progressive hierarchy adds latency and complexity. These conditions favor failing fast instead:

- **Short-lived tasks with no side effects** — a task under 30 seconds with no external writes gains nothing from recovery logic; retry overhead exceeds the benefit.
- **Cascading failures in multi-agent systems** — when agents share infrastructure (databases, queues, tool APIs), recovery attempts amplify load on stressed components. Circuit breakers and backpressure must be coordinated across agents, not per-agent.
- **Silent corruption without validation** — recovery requires detection. Writing to external systems without output validation means an agent that "recovers" may compound bad state. Fail fast to a human when intermediate state cannot be verified.

## Example

A coding agent tasked with refactoring a module hits a test failure after changing a function signature:

1. **Self-correct** — the agent reads the test error, identifies the mismatched argument, and fixes the call site. Tests pass.
2. On the next file, the same refactor produces a circular import. The agent retries twice, fails both times.
3. **Fallback** — the agent abandons the automated refactor for that file and applies a manual re-export to break the cycle.
4. A third file depends on an external service that is down. The agent cannot run integration tests.
5. **Degrade gracefully** — the agent commits the passing unit-tested changes and leaves the integration-dependent file unchanged, noting the skip in its progress log.
6. The agent encounters a permissions error trying to update a protected config file.
7. **Escalate** — the agent opens a draft PR with its completed work and flags the config change for human review, including the error message and the intended edit.

Throughout, the agent commits after each successful file change (`git commit -m "refactor: update signature in <file>"`), so any revert affects only one file.

## Related

- [Rollback-First Design](rollback-first-design.md)
- [Agent Circuit Breaker](agent-circuit-breaker.md) — per-tool state machine implementation with configuration thresholds
- [Circuit Breakers](../observability/circuit-breakers.md)
- [Idempotent Agent Operations](idempotent-agent-operations.md)
- [Agent Harness](agent-harness.md)
- [Harness Engineering](harness-engineering.md)
- [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md)
- [Loop Detection](../observability/loop-detection.md)
- [Trajectory Logging and Progress Files](../observability/trajectory-logging-progress-files.md)
- [Agent Backpressure](agent-backpressure.md)
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md)
- [Agent Self-Review Loop](agent-self-review-loop.md)
