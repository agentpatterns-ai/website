---
title: "Tool-Call Success as Workflow Effect Evidence"
term: "External-Effect Anomaly"
description: "A workflow whose every tool call succeeded can still leave the wrong effects standing outside. Eight anomalies name the gap; MCP annotations express one."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - external-effect anomalies
  - agent-tool boundary anomalies
  - effect-safety guarantee profiles
last_reviewed: 2026-09-17
maturity: emerging
---

# Tool-Call Success as Workflow Effect Evidence

> A workflow whose every tool call returned success can still leave the wrong set of effects standing in the outside world.

Per-call success is evidence about one call. Workflow correctness is a property of the effects that survive, checked against how the workflow resolved. Retries, speculative branches, concurrent workers, and partial failures sit between the two, so "required effects may be missing or duplicated, aborted effects may survive, and committed effects may depend on provisional state that is later withdrawn" ([Trofimov & Novikov, arXiv:2609.15397v1](https://arxiv.org/abs/2609.15397v1)). Reading a green call log as proof the world is right is the mistake.

## When the belief is expensive

Four conditions have to hold at once before any of this reaches you.

- The workflow externalizes more than one effect: payments, bookings, outbound messages, deployments.
- Those effects are hard or impossible to reverse, so an abort cannot undo them.
- Nothing pauses for a human between the calls and the resolution.
- The tools come from somewhere you do not control, so you cannot add semantics they decline to publish.

Drop any one and most of the catalog below goes out of reach. A read-only tool surface has nothing to make inconsistent, and a confirmation step on every write resolves the uncertainty cases for free.

## Eight anomalies in three families

The catalog is built the way classical isolation levels were, by enumerating the ways control is lost rather than collecting incidents. Each family closes by construction: three reactions a runtime can take under an unresolved outcome, three ways an effect can relate to its resolution point, two kinds of outside participant it can meet ([arXiv:2609.15397v1](https://arxiv.org/abs/2609.15397v1)).

| Anomaly | The forbidden pattern | What the boundary must supply |
|---|---|---|
| A1 Duplicated | One logical operation externalizes twice | Authoritative convergence on one outcome |
| A2 Missing | The workflow commits without a required effect | Authoritative outcome; atomic multi-effect participation |
| A3 Orphaned compensation | Compensation issued under an unknown outcome | Outcome resolution before compensating |
| A4 Residue | An aborted workflow leaves a surviving effect | Residue prevention or safe neutralization |
| A5 Premature | An effect that may not survive goes out before resolution | Pre-externalization observation or control |
| A6 Contaminated speculation | A committed effect depends on an effect that does not survive | Dependency observability and commit control |
| A7 Conflicting | Unordered non-commuting effects from independent executions | Shared-resource coordination |
| A8 Phantom compensation | An outside party's reaction to a compensated effect survives | Control of external observability |

Only A1 to A3 turn on an outcome the runtime cannot confirm. The other five need no ambiguous response at all: they come from the structure of the execution, or from meeting something outside it. That is what makes per-call assertions such poor cover. A6 is the sharpest of them. In the paper's case a branch reserves a room, a second branch sends invitations naming it, the second branch commits, and the reservation is then canceled. The paper calls this "the effect-world analogue of a *dirty read*" and notes the harm "would arise even if those invitations were themselves reversible". The contamination is causal, so reversibility does not reach it.

The families also give you a target to name. Excluding A1 to A3 is unknown-safe, A4 is compensation-safe (which assumes compensations are correct and succeed), A5 and A6 are speculation-safe, and A7 and A8 need an externally-mediated boundary. Compensation-safe is sometimes the ceiling: an agent negotiating for a user "cannot learn the counterparty's reaction without sending an offer, so the action must precede the observation and full gating is unavailable".

## Why it works

The gap is a level mismatch, and no amount of per-call checking closes it. An effect history "separates execution and external events from the runtime's knowledge of their outcomes", so a success response is an observation about the call, while safety is judged one level up against the set of effects that survived ([arXiv:2609.15397v1](https://arxiv.org/abs/2609.15397v1)). The facts needed up there are properties of the operation below: whether an effect occurred, whether it can be compensated, staged, or safely reordered. A shared interface rarely carries them.

Where the boundary carries no evidence, the limit stops being an engineering gap. Over an unreliable channel the runtime "cannot learn in bounded time whether an effect took place, the classical exactly-once barrier at the agent-tool boundary", and every move available to it lands on one of the anomalies. "Re-issuing risks A1, committing risks A2, compensating risks A3, and aborting without compensation risks A4 if the effect occurred." Waiting sidesteps the choice by giving up resolution.

## What the boundary declares today

A census of 98,291 tools from the official MCP registry, snapshot 2026-07-27, measured the four annotations the specification defines. The fields are emitted widely: 74.0% of tools serialize at least one and 61.7% serialize all four ([arXiv:2609.15397v1](https://arxiv.org/abs/2609.15397v1)). What they carry is thinner than that suggests. `destructiveHint` is set on 65.8% of tools, but "just 12.9% of tools carry an applicable classification, and only 3.1% assert an actual destructive operation", because the rest are read-only, where the field means nothing. One signature (read-only, non-destructive, idempotent, open-world) covers 39.9% of tools, and the next most common is no annotation at all, at 26.0%.

Scored against the eight capabilities, the vocabulary rates A1 as "Limited: idempotence hint only" and every other row as "No". Read that as a fact about declarations, not behavior: "Tools may enforce stronger semantics internally (deduplication, idempotency keys) than any annotation surfaces; that safety remains unusable to a runtime that only sees the interface." The hints were never built to bear the weight. MCP's own guidance is that "annotations are not guaranteed to faithfully describe tool behavior, and clients must treat them as untrusted unless they come from a trusted server" ([MCP, Tool Annotations as Risk Vocabulary](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)).

## Example

An agent books a trip against a 1500 EUR budget and runs the two bookings in parallel to cut latency.

**Before** — both calls succeed and the budget invariant still breaks:

```
externalize(book_flight, 900 EUR)   # succeeds
externalize(book_hotel,  700 EUR)   # succeeds
abort(BookTrip)                     # 1600 > 1500
cmp(book_hotel)                     # hotel canceled
=> survives(flight): non-refundable ticket, workflow aborted
```

"Each operation completed correctly in isolation, yet the surviving external state is inconsistent with the intended workflow outcome" ([arXiv:2609.15397v1](https://arxiv.org/abs/2609.15397v1)). A per-call assertion passes twice here, and A4 still lands.

**After** — the invariant is checked before anything irreversible goes out:

```
quote(book_flight) -> 900 EUR       # no externalization
hold(book_hotel, expiry) -> 700 EUR # provisional, declared expiry
check 900 + 700 > 1500              # invariant fails first
abort(BookTrip)                     # hold lapses; nothing survives
```

A read-only quote avoids externalizing at all, and an expiring hold "replaces the final effect with a provisional one whose visibility, expiry, and release semantics are declared". Both are tool-side capabilities, which is why this reads as a contract question rather than an orchestration one.

## When this backfires

Chasing exclusion is not free, and four situations make it the wrong spend.

- Read-only surfaces. The census numbers above imply this is the common case. Gating machinery there costs context and buys nothing.
- Tools you merely consume. Staging, commutativity, and visibility control are declared at the tool. A consuming team can add a client-side idempotency key and a postcondition read, and the rest of the table needs a vendor.
- Latency budgets. Speculation-safe execution gates effects that may not survive, which removes the parallel booking that motivated the trip example in the first place.
- Unknown economics. The paper puts "a cost model that prices anomalies against their compensations" in future work, so nothing here tells you when speculation and early release are worth their residue.

The protocol is also moving underneath the census, which was taken on 2026-07-27. In MCP's release-candidate Tasks extension, "a server can answer `tools/call` with a task handle, and the client drives it with `tasks/get`, `tasks/update`, and `tasks/cancel`" ([MCP release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)). That is the status endpoint A2 and A3 turn on. It adds no idempotency key, compensation contract, staging control, or commutativity rule, so the other six rows stand.

## Key Takeaways

- Write the assertion against the effects that survived the workflow's resolution, not against the call log. The two disagree in five of the eight anomalies.
- Name the profile you are buying before you build. Unknown-safe, compensation-safe, speculation-safe, and externally-mediated are four different budgets, and negotiation workloads cannot reach past the second.
- Under an unresolved outcome every available reaction maps to an anomaly, so a better retry policy is the wrong place to look. The fix is a boundary that resolves the outcome.
- Before relying on an annotation, check whether it is applicable rather than present. Emission rates on this vocabulary run far ahead of the rate at which a field means anything.

## Related

- [Tool Operability: Interfaces That Survive a Lost Response](../agent-design/tool-operability-lost-responses.md) — the single-call half, where one lost response makes committed and uncommitted state indistinguishable; this page covers the effects left standing across a whole workflow.
- [Multi-Agent Shared State Isolation Anomalies](multi-agent-shared-state-isolation-anomalies.md) — the same anomaly-catalog method applied to a runtime's shared internal state, which is the read side this page's model excludes.
- [Idempotent Agent Operations: Safe to Retry](../agent-design/idempotent-agent-operations.md) — the caller-side discipline A1 depends on, and which the boundary has to declare before a runtime can rely on it.
- [Fleet-Level Irreversibility Budgets for Agent Effects](../agent-design/fleet-irreversibility-budget.md) — governing irreversible effects by aggregate exposure rather than per-workflow resolution.
- [Run-Status vs Task-Status Confusion in Autonomous Agent Runs](run-status-vs-task-status-confusion.md) — the same shape one layer out, where a clean harness exit is read as the task having succeeded.
