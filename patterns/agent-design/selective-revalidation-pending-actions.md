---
title: "Selective Revalidation for Pending Agent Actions"
term: "Selective Revalidation"
description: "Record the executable conditions that justified a pending agent action, then recheck only the conditions a state change can reach, under the three preconditions that make it safer than replanning."
tags:
  - agent-design
  - tool-agnostic
  - reliability
  - arxiv
aliases:
  - decision conflict detection
  - premise revalidation
  - selective recheck
last_reviewed: 2026-09-09
maturity: emerging
---

# Selective Revalidation for Pending Agent Actions

> Record the conditions that justified a pending action, then recheck only those a state change reaches, separating version conflicts from decision conflicts.

Selective revalidation stores a pending action with the conditions that justify it, written as deterministic checks over named fields of the state the agent read. When that state changes before the action fires, the harness re-evaluates only the conditions the change can reach. ATR, the system that names this split, records "the explicit, executable conditions that justify a pending action and rechecks only the conditions affected by a change before releasing the external operation" ([Lyu, Ren, Lai and Liu, arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)).

The distinction it draws is the useful part. Any detected change is a version conflict. Only a change that falsifies the justification is a decision conflict. Optimistic concurrency control finds the first and stops: it "can report that an agent read version 11 while the resource is now at version 12", but does "not know whether the changed field matters to the refund" ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)). An agent that treats every version conflict as a decision conflict aborts because a customer renamed themselves.

## When this applies

Three things have to be true before selectivity is safer than replanning on any change.

Dependency capture has to be complete, or deliberately over-approximated. The authors measure the cost of a miss: randomly omitting the sole critical dependency edge at 1%, 5% and 10% omission produced false-allow rates of 0.95%, 5.05% and 9.97% ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)). Their conclusion is that "selective validation is safe only when dependency capture is complete or conservatively over-approximated". A read that reaches state through a helper the harness cannot instrument is a hole with a measured false-allow rate behind it.

The conditions have to be executable. Each carries a validator function and a validator version, and a model-authored condition counts for nothing until it maps to one. "The customer seemed satisfied" has no validator, so it cannot be a condition.

The target has to bind the checked state to the commit. Validation runs in the agent's process, then the validated versions travel to the target, which must verify them atomically through "a target-side transaction or compare-and-set" (CAS) ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)). Against an API with no conditional write, the recheck passes and the effect still races a concurrent writer.

## The four outcomes

Re-evaluation returns one of four verdicts, and the most severe one wins ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)).

| Outcome | Fires when | Effect |
|---|---|---|
| KEEP | No recorded condition is falsified and no refresh rule fires | Release the action unchanged |
| REFRESH | A rule updates presentation or derived metadata; no decision condition is false | Refresh the metadata, release the action |
| REPLAN | The current intent is no longer justified, though the task may still be feasible | Hand the task back to the agent |
| BLOCK | A safety, authority, policy, or irreversible-effect condition is false, missing, contradictory, or unverifiable | Do not release the effect |

Most harnesses collapse those four to retry or abort, which is why a renamed customer and a halved refund limit get the same treatment. The taxonomy is worth adopting ahead of any machinery.

## Why it works

A validator runs against the current observation, so it reports whether the justification survives rather than whether the record moved. The cost saving is a separate effect and comes from the graph. Conditions are edges running from reads to pending actions, so a change reaches only the conditions in its affected closure. In ten durable SQLite checkpoint and resume cells, the system evaluated 0.6 conditions per change against 6.0 for a full rescan, and its latency stopped tracking unrelated reads: 8.8 to 9.3 microseconds as reads grew from 13 to 4,093, where the rescan went 12.1 to 2595.9 microseconds ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)).

## When this backfires

The dependency graph is hand-declared, and hand-declared dependency graphs decay. Incremental build systems run the same "recheck only what is affected" shape, and missing dependencies are a known defect class. Lyu et al. summarize the prior work: missing dependencies "prevent GNU Make from recompiling programs after they have been modified ... resulting in incorrect incremental builds", citing Licker and Rice (2019), and 52.68% of build errors in C-based projects are dependency-related, citing Seo et al. (2014) ([Lyu, Li, Zhang, Zhang, Rong and Rigger, arXiv:2404.13295v2](https://arxiv.org/abs/2404.13295v2)). A stale build is annoying. A refund released on a stale condition is not.

Replanning is often cheaper than the machinery. Throwing the pending intent away and re-deciding from current state is always sound, needs no graph and no validators, and cannot produce a false allow from a missed read. The speed argument for selectivity is the gap between 9.3 and 2595.9 microseconds, under 3 milliseconds, on a workflow that just waited hours for a human ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)). With tens of pending actions and a model call to spare, write no conditions.

Policy churn breaks it silently. Change what a spending limit means without bumping the validators, and actions decided under the old rule still pass the recheck.

Treat the evidence as feasibility, not proof. The 210,000 executions ran on one host with deterministic workloads and developer-authored validators, and the authors say they "establish controlled feasibility, not production generality or automatic extraction of the required conditions" ([arXiv:2609.08015v1](https://arxiv.org/abs/2609.08015v1)).

## Key Takeaways

- Split the two questions before building anything. A version check tells you the state moved; a condition check tells you the action is no longer justified.
- KEEP, REFRESH, REPLAN and BLOCK are adoptable as a review taxonomy before any dependency graph exists.
- Watch the false-allow rate, because it tracks dependency capture rather than validator quality: omitting the one critical dependency edge 1% of the time cost 0.95% false allows.
- Without a target-side transaction or compare-and-set, a passing recheck still loses to a concurrent writer.
- If replanning costs one model call and pending actions are rare, this pattern is unpaid engineering.

## Related

- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the operational shape this pattern sits inside, where state outlives the session that read it
- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — the same write-path check without the recorded justification or the selectivity
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — the duplicate-effect half of the problem, which revalidation detects but does not solve
- [ACID for Agent Repository State](acid-for-agent-repository-state.md) — transaction properties applied to an agent's own commits
- [Approval Gate Granularity](approval-gate-granularity.md) — where the pause that opens the stale-state window comes from
