---
title: "Pre-Write Change Intent Admission (Claim Plane)"
term: "Pre-Write Change Intent Admission"
description: "Parallel agents declare a versioned change intent — base commit, typed resources, dependencies — and a deterministic control plane admits, constrains, or refuses it before any write."
aliases:
  - pre-write admission control
  - versioned change intent declaration
  - committed and contingent write scope
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-04
maturity: emerging
---

# Pre-Write Change Intent Admission (Claim Plane)

> Agents declare base commit and write scope before coding; a deterministic control plane admits, constrains, or refuses each claim before any byte changes.

Pre-write change intent admission moves interference detection ahead of the write. Each parallel worker declares a versioned change intent — an exact base commit, typed resources, dependencies, and the operations it plans — and a control plane decides whether that claim can coexist with the intents already active ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)). The distinction it rests on is between an integration conflict, which you can only see after both agents have written code, and an authority conflict, which two active workers already have the moment they claim incompatible rights over the same surface.

The first published evidence was a six-pair feasibility check. A 30-pair, three-seed study of 360 executions has since measured the payoff ([Claim Plane confirmatory study, 2026](https://arxiv.org/abs/2608.00947v1)): static Claim Plane raised the pair pass rate from 23.3% to 50.0% and integration success from 65.6% to 96.7%.

## When this pattern applies

Three conditions have to hold before the protocol earns its cost:

- You control an enforceable write boundary. Claim Plane routes file operations through a broker with exact capabilities, so an ordinary write does not imply delete or rename. Where a runtime exposes tool-call hooks, an adapter enforces this directly; where it does not, you fall back to isolated worktrees plus diff verification and "the guarantee is correspondingly weaker because direct host writes may bypass the control plane" ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909v1)).
- Your planner can declare scope accurately. Admission compares typed resources, so a planner that cannot predict which files, symbols, or contracts a task will touch either blocks legitimate edits or over-declares and serializes unrelated work.
- Contention is high enough to pay for the protocol. [Worktree isolation](../../workflows/worktree-isolation.md) already separates two agents working on different modules, so the declaration layer buys nothing until they genuinely collide.

If any of the three fails, prefer [cohesion-aware task partitioning](cohesion-aware-task-partitioning.md) upstream or an optimistic scheme like [CRDT-based observation-driven coordination](crdt-observation-driven-coordination.md).

## Committed and contingent scope

The declaration splits into two kinds of authority. A committed operation reserves write ownership now and participates in admission immediately. A contingent operation names a surface the worker might need later; it is tracked as a read premise but reserves nothing ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)).

That split exists to defuse a planner trade-off. Declaring narrowly preserves parallelism but blocks legitimate supporting edits; declaring broadly preserves recall but serializes unrelated work. When a worker first tries to mutate a contingent surface, the control plane promotes only the concrete path or region requested — never the whole declared pattern — and re-runs the same admission logic inside one transaction. If admission fails, the mutation is denied and the intent is left untouched, so failed speculation cannot quietly widen a worker's write rights.

Admission returns a decision from a fixed vocabulary rather than a yes or no. Beyond independent and serialize, it can admit an overlap governed by a shared contract, record one worker as dependent on another's contract, allow parallel work confined to disjoint declared regions, or track a premise so it can invalidate a dependent later. Unknown overlapping writes fail closed.

## Why it works

Two causes, both structural. First, timing: an integration conflict becomes visible only after both workers have spent inference and test budget, while an authority conflict is decidable from a declared base commit, typed resources, and dependencies before a single byte is written ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)). Moving the decision earlier converts wasted inference into a cheap refusal. Second, separation of proposal from authority: the planner may be probabilistic, but admission, promotion, leases, fencing, and verification are deterministic and auditable, so a mis-predicting planner cannot expand its own rights. This is the same systems argument [SWE-agent](https://arxiv.org/abs/2405.15793) made for single agents — the execution interface and the invariants around tool actions change outcomes independently of the model.

The coordination penalty it targets is measured: across more than 600 collaborative coding tasks, [CooperBench](https://arxiv.org/abs/2601.13295) reports roughly 30% lower success when two agents split work than when one agent does both.

## Example

The paper's reference authorization rule shows where the enforcement point sits. Every mutation is checked against current committed authority first, and a contingent surface must survive re-admission before it is touched:

```text
function AUTHORIZE_MUTATION(intent I, mutation m):
    if committed_scope(I) covers m:
        validate lease, intent version, capability, fencing token
        execute through broker and record tree transition
        return SUCCESS
    if contingent_scope(I) covers m:
        I' <- promote only the concrete path/region required by m
        if ADMIT(I', current active intents) succeeds atomically:
            re-attest broker to I'
            execute m
            return SUCCESS
        return BLOCK
    return BLOCK
```

Adapted from Appendix A of [Nikolaev (2026)](https://arxiv.org/abs/2607.21909). An undeclared mutation falls through both branches and is refused.

## When this backfires

- Serialization is the common outcome, not the exception. In the paper's six-pair check, the arm that treated all planned scope as committed passed 6 of 6 pairs, but only by serializing all 6. Plain always-serial execution passed 4 of 6, and the dynamic-scope arm the paper introduces passed 3 of 6 with 7 promotions and 2 fail-closed blocks ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909v1)). The author reports one safe parallel case that was conservatively serialized and labels the run a debugging signal. The 30-pair study qualifies that picture: static admission passed 60.0% of conflict-labeled pairs against 6.7% for the baseline, and the paper records the limits of selective concurrency alongside the gain ([Claim Plane confirmatory study, 2026](https://arxiv.org/abs/2608.00947v1)).
- Blocking is expensive when transactions are long. An agent holds authority across minutes of inference, so a pessimistic gate blocks far longer than a database lock would — the cost regime behind [multi-agent shared state isolation anomalies](../anti-patterns/multi-agent-shared-state-isolation-anomalies.md). [CoAgent](https://arxiv.org/abs/2606.15376v1) argues the opposite design from that premise, advisory notification plus targeted repair, and reports staying within 5% of serial correctness at 1.4x speedup where two-phase locking and optimistic concurrency control give up nearly all concurrency gains.
- High-recall planners lower precision. Declaring many bounded contingent regions reduces undeclared writes, but the paper reports it also makes static policy far more conservative and blurs region boundaries ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)).
- Language coverage is thin. The prototype is Python-first for typed symbol and callable extraction; the protocol is language-agnostic, but the author notes that useful semantic analysis elsewhere needs language adapters that do not yet exist ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)).
- Single-host only. The reference lease and operating-system lock give authority on one host; fleets need a network-authoritative store plus a distributed lease and fencing sequence ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)).
- Most coordination loss is not a write conflict. CooperBench attributes the bulk of collaborative failure to jammed communication and wrong expectations about a partner's plan ([CooperBench, 2026](https://arxiv.org/abs/2601.13295)). An authority layer refuses bad writes; it does not correct a wrong model of what the other agent is doing.

Pre-write admission is also not a replacement for merge, tests, or review. It is one more enforcement layer meant to surface unsafe concurrency earlier ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909)).

## Key Takeaways

- Pre-write admission decides whether two workers may hold incompatible rights over a surface before either writes, rather than repairing the collision at merge ([Nikolaev, 2026](https://arxiv.org/abs/2607.21909))
- Committed scope reserves authority now; contingent scope reserves nothing until the first attempted mutation triggers a narrowed promotion and atomic re-admission
- A rejected promotion leaves the intent unchanged, so a planner that guesses wrong cannot widen its own write authority
- The mechanism only binds where writes cross an enforceable boundary; without tool-call hooks or a broker, direct host writes bypass the control plane
- A 30-pair, three-seed study puts static admission at a 50.0% pair pass rate against a 23.3% baseline and 96.7% integration success, with the largest gain on conflict-labeled pairs ([Claim Plane confirmatory study, 2026](https://arxiv.org/abs/2608.00947v1))

## Related

- [Observation-Driven Coordination: CRDT-Based Parallel Agent Code Generation](crdt-observation-driven-coordination.md)
- [Verify-Gated Completion as Admission Control](verify-gated-completion-admission-control.md)
- [Cohesion-Aware Task Partitioning for Multi-Agent Coding](cohesion-aware-task-partitioning.md)
- [File-Based Agent Coordination](file-based-agent-coordination.md)
- [Multi-Agent Shared State Isolation Anomalies](../anti-patterns/multi-agent-shared-state-isolation-anomalies.md)
