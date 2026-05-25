---
title: "Observability Feedback Loop: A 7-Step Debug Runbook for Agents"
description: "A named runbook — query, correlate, reason, implement, restart, rerun, verify — that closes the loop on agent debugging by tying the verification predicate to the originating signal."
tags:
  - observability
  - workflows
  - testing-verification
  - tool-agnostic
aliases:
  - observability feedback loop
  - 7-step debug runbook
  - query correlate reason implement restart rerun verify
---

# Observability Feedback Loop: A 7-Step Debug Runbook

> A named runbook — query, correlate, reason, implement, restart, rerun, verify — that closes the loop on agent debugging by tying the verification predicate to the originating signal.

## What the Loop Is

When runtime observability is the source of truth, agents debug from execution evidence, not code inspection alone. The [walkinglabs harness-engineering SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/observability-feedback-loop.md) names seven explicit steps:

```mermaid
graph TD
    A[Query: pull the specific failing signal] --> B[Correlate: connect signal to owning layer]
    B --> C[Reason: name a falsifiable hypothesis]
    C --> D[Implement: change the smallest responsible layer]
    D --> E[Restart: confirm a clean restart path]
    E --> F[Rerun: same originating workload, not a proxy]
    F --> G[Verify: prior signal is absent]
    G -->|signal still present| A
```

The steps are scaffolding. The load-bearing piece is the verification predicate at step 7 — *the originating signal is absent*, not "no errors now." This is the fix for the [trust-then-verify gap](https://code.claude.com/docs/en/best-practices).

## Prerequisites: The Minimum Stack

The loop assumes runtime signals exist and are queryable. The SOP enumerates the minimum: structured logs on startup and the critical path, metrics for latency and failure counts, traces for multi-step flows, query interfaces in dev, and one repeatable workload to rerun. Without this stack, there's nothing to query against. See [Making Observability Legible to Agents](observability-legible-to-agents.md) for wiring patterns.

## The Seven Steps

### 1. Query

Pull the specific signal that failed — a log line, a metric value, a trace span. Not "tail the logs." Claude Code contrasts the vague `"the build is failing"` with `"the build fails with this error: [paste error]"` ([best practices](https://code.claude.com/docs/en/best-practices)). The signal queried in step 1 is the same signal verified absent in step 7 — pick it deliberately.

### 2. Correlate

Connect the signal to the layer responsible. A front-end exception triggered by a back-end data shape lives in the back-end. If a [layered domain architecture](../agent-design/layered-mutability.md) is in use, name the layer explicitly — the layer assignment determines what gets edited in step 4.

### 3. Reason

Name a hypothesis with falsifiable predictions *before* editing. This is the entry point to [hypothesis-driven debugging](../agent-design/hypothesis-driven-debugging.md) — enumerate competing explanations, then identify which one the evidence supports. The hypothetico-deductive method Google SRE codifies in its [Effective Troubleshooting chapter](https://sre.google/sre-book/effective-troubleshooting/) names the same discipline. Skipping this step is the classic agent failure mode: hypothesis-implement-repeat cycles with no discrimination between competing causes.

### 4. Implement

Change the smallest responsible layer. Resist refactoring opportunism — unrelated improvements bundle in change risk and obscure which edit fixed the signal. Claude Code's guide phrases this as "address the root cause, don't suppress the error" ([best practices](https://code.claude.com/docs/en/best-practices)).

### 5. Restart

Confirm a clean restart path before testing the fix. Anthropic's harness engineering article ships this as an `init.sh` step in the session startup routine: "restart the development server and verify fundamental features are still working" ([harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). State that survives between runs — cached configs, in-memory queues, leaked DB rows — corrupts the verification in step 7.

### 6. Rerun

Exercise the same originating workload, not a simpler proxy. The discipline is to exercise the workload that *originally surfaced* the signal. A unit test passing while the integration scenario still fails is the most common false-positive pattern in this loop.

### 7. Verify

The verification predicate explicitly says "the prior signal is absent" — not "no errors now," not "the test suite is green." Anthropic's [best-practices guide](https://code.claude.com/docs/en/best-practices) calls verification predicates "the single highest-leverage thing you can do" for agent quality. The predicate is bound at step 1 and consumed at step 7 — the same signal, now absent.

## Why the Steps Are Named

A named procedure lets a human or upstream agent invoke "run the observability feedback loop on bug X" and have the steps be unambiguous. Each step produces an artefact (signal value, layer assignment, hypothesis, diff, restart log, rerun output, verification result) that the next step consumes, and a [trajectory log](trajectory-logging-progress-files.md) of those seven artefacts makes the debug session reviewable after the fact.

## Example

A repeatable bug: API returns 500 on `/users/me` after token refresh, intermittently.

- **Query** — the 500 carries `error_id=auth-token-stale-3f2a` in the response body and in the structured log line `level=error fn=refreshToken cause=stale_cache`. That `error_id` is the signal.
- **Correlate** — the log line is emitted by the auth middleware layer (`src/auth/middleware.ts`), not the route handler. The layer assignment is *middleware token-refresh*, not *route handler*.
- **Reason** — three hypotheses: (a) the cache invalidation runs after the refresh attempt, (b) the refresh request races a parallel refresh in another worker, (c) the cache TTL is shorter than the refresh window. Instrument with one log line per hypothesis ([hypothesis-driven debugging](../agent-design/hypothesis-driven-debugging.md)). The log fires for (a).
- **Implement** — invalidate the cache before the refresh attempt, not after. One-line change in `middleware.ts`.
- **Restart** — `init.sh` restarts the local API and verifies `/healthz` plus `/users/me` for an unauthenticated user. Both pass; clean restart confirmed.
- **Rerun** — exercise the original workload: authenticated session, idle past TTL, then `/users/me`. Not a unit test of the cache layer — the same end-to-end path that surfaced the 500.
- **Verify** — search structured logs for `error_id=auth-token-stale-3f2a` across the rerun window. Zero occurrences. Signal absent. Loop closes.

If verify had returned occurrences, the loop restarts at step 1 with the new signal value — not at step 4 with a different fix.

## When This Backfires

Three conditions where the procedure adds ceremony without proportional value:

1. **Fast feedback loops with clear stack traces** — when `npm test` reports a line number and the fix is obvious, explicit step-naming is overhead. The loop earns its keep when runtime evidence is needed to discriminate hypotheses.
2. **Single-layer, single-signal failures** — if the failure surfaces in one log line with full context and lives in one layer, "correlate to the layer" collapses to zero work.
3. **Exploratory bug hunts without a clear originating signal** — the loop's first step assumes a specific signal exists. For "feels slow sometimes" with no metric anchor, instrumentation comes first.

The rule from [research-plan-implement](../workflows/research-plan-implement.md): apply the seven-step loop when runtime evidence is the source of truth; compress it when the source of truth is the stack trace.

## Key Takeaways

- The seven steps are scaffolding; the verification predicate at step 7 — "the originating signal is absent" — is the load-bearing piece
- The signal you query for in step 1 is the same signal you verify the absence of in step 7. Bind them deliberately
- Skipping the restart step lets accumulated state corrupt the verification; skipping the rerun step lets a simpler proxy mask the real failure
- Compress the loop only when the failure surface is self-evident — the procedure is overhead when the stack trace already names the layer and cause
- A named procedure is invocable: "run the observability feedback loop on bug X" gives an agent unambiguous steps and checkpointable artefacts

## Related

- [Agent Debugging: Diagnosing Bad Agent Output](agent-debugging.md)
- [Hypothesis-Driven Debugging: Instrument Before You Patch](../agent-design/hypothesis-driven-debugging.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Trajectory Logging via Progress Files](trajectory-logging-progress-files.md)
- [Loop Detection](loop-detection.md)
- [Verification-Centric Development](../workflows/verification-centric-development.md)
- [Research, Plan, Implement](../workflows/research-plan-implement.md)
- [Layered Mutability](../agent-design/layered-mutability.md)
