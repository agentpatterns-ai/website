---
title: "Minimum-Cost Evidence Selection for Agent Changes (Assurance Envelopes)"
term: "Assurance Envelope"
description: "Choose which prior tests, type checks and proofs an agent restores for a change by naming the properties the change must preserve, then accepting a selection only when forward chaining from it reaches every one."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "task-conditioned assurance envelope"
  - "minimum-cost evidence selection"
last_reviewed: 2026-09-17
maturity: emerging
---

# Minimum-Cost Evidence Selection for Agent Changes (Assurance Envelopes)

> An assurance envelope is the least-cost set of prior evidence whose forward-chaining closure re-establishes every property a change must preserve.

Earlier runs leave a repository full of machine-produced evidence: passing tests, type-check results, discharged contracts, static-analysis verdicts, traces. Restoring all of it for the next change carries irrelevant history, and dropping the wrong piece leaves a property that change depends on unsupported. An assurance envelope settles that by fixing the acceptance rule first: a selection counts only when forward chaining from it derives every obligation you named ([Goswami, 2026](https://arxiv.org/abs/2609.16302v1)).

## When this applies

It returns little unless three conditions hold.

1. You can state the obligations before you select. The formulation takes them as input, and building a complete requirement set "remains an external requirements and change-impact problem" ([Goswami, 2026, §2.1](https://arxiv.org/abs/2609.16302v1)). Selection against an incomplete set returns "sufficient" for the wrong requirements.
2. Some properties need several pieces of evidence together. Where every property has one independent source, the problem is weighted set cover and a coverage table answers it, as in [coverage-aware skill selection](../context-engineering/coverage-aware-skill-selection.md). The conjunctive case is where a table stops working.
3. Your properties have few alternative routes. Count the suites that cover one property: redundant derivations, not graph size, drive the solve cost.

## How the selection works

Write down the change's obligations, not its code dependencies, which is what [pre-change impact analysis](pre-change-impact-analysis.md) maps. An obligation reads: the build succeeds, an interface contract holds, a rejected action never commits. Record each piece of evidence, what it directly establishes, and how pieces combine ([Goswami, 2026, §2](https://arxiv.org/abs/2609.16302v1)).

That gives a directed graph: AND steps where several pieces must hold together, OR alternatives where a property has more than one route. Apply those combination rules to a candidate selection until nothing new appears; the selection is sufficient when the result contains every obligation. Ask for the cheapest selection that passes, then re-run the closure on the answer rather than trusting what produced it. Where the closure cannot reach a required property, report that no envelope exists instead of returning the nearest subset. Failed trace evidence is kept as provenance but does not establish the positive obligation, so a trace task over it is infeasible ([Goswami, 2026, §3.1](https://arxiv.org/abs/2609.16302v1)).

## Why it works

Obligations differ in kind, not in strength. A compiler establishes a type judgment; a monitor establishes a property over bounded traces. "Evidence for one obligation does not substitute for another unless an explicit rule connects them" ([Goswami, 2026, §2](https://arxiv.org/abs/2609.16302v1)). The rules are explicit and the graph is finite and acyclic, so forward chaining terminates on a definite answer. A missing premise of a conjunction is therefore detectable. A representation holding only pairwise "evidence X supports property Y" links cannot detect it. Flattening the AND steps that way produced selections that closure rejected in 135 of 267 task evaluations, falsely covering 3,765 roots. None of it landed in the families that contain no conjunction ([Goswami, 2026, Table 2](https://arxiv.org/abs/2609.16302v1)). The closure check carries this; the optimizer only proposes.

## When this backfires

- Two of the eight benchmark families save nothing. Median support reduction is zero for the conjunctive-chain and shared-support families, whose skeletons require every leaf ([Goswami, 2026, §5.2](https://arxiv.org/abs/2609.16302v1)).
- Redundant derivations dominate size. Median solve time stayed under 20 ms at 500 evidence leaves on one test machine, but all three instances with ten alternative derivations per target timed out at 100 leaves, returning a valid selection with a best bound of zero ([Goswami, 2026, §5.4](https://arxiv.org/abs/2609.16302v1)).
- Smaller is measured, cheaper is not. The reductions "do not measure lower token use, verification runtime, money, or human effort" ([Goswami, 2026, §5.2](https://arxiv.org/abs/2609.16302v1)), and no experiment tests whether an agent given the envelope performs better.
- Shrinking an evidence set has a known cost. Test-suite reduction "has almost always a negative impact on the effectiveness of RTS, yet a positive impact on efficiency" ([Ruland and Lochau, 2022](https://arxiv.org/abs/2207.12733v1)). Selectors also inherit their dependency map's errors: NameRTS "selects all affected tests for 99.6% of commits, with only rare misses", and the compared BabelRTS "is safe for 76.6% of commits" ([Wang, Pradel and Liu, 2026](https://arxiv.org/abs/2605.25356v1)).
- Whether old evidence still applies after source, dependency or compiler change is out of scope ([Goswami, 2026, §7.2](https://arxiv.org/abs/2609.16302v1)). A stale leaf stays selectable.
- Obligation sets and inference rules are hand-written, and "may omit real requirements or encode a bridge too strongly" ([Goswami, 2026, §8](https://arxiv.org/abs/2609.16302v1)). The envelope certifies what you asked, not that you asked for enough.

## Example

One Rust artifact, one evidence graph, three tasks. Only the required properties change ([Goswami, 2026, Table 1](https://arxiv.org/abs/2609.16302v1)):

| Fixture and task | Selected evidence | Cost | Result |
|---|---|---|---|
| C, local change | build, local-state | 2 | Trace evidence omitted |
| C, change to trace behavior | build, local-state, trace | 3 | Same artifact, one extra root, one extra leaf |
| B, change to trace behavior | none | – | No sufficient envelope: trace evidence failed |

Local evidence covers 30 prespecified state and event pairs; trace evidence covers 781 event sequences to depth four; no rule derives trace success from local success ([Goswami, 2026, §3.1](https://arxiv.org/abs/2609.16302v1)). The third row is the output worth having. A coverage table would have reported the trace property as covered, because a failed check is still a check.

## Key Takeaways

- Pick evidence against the change's obligations, not against the code's dependency graph, and write the obligations down first.
- Record how evidence combines. Pairwise "supports" links silently convert a required conjunction into two alternatives.
- Accept a selection only after forward chaining from it reaches every obligation, and re-run that check independently of whatever chose the set.
- Treat "no sufficient evidence exists" as a reportable result and route it to a human, rather than returning the closest subset.
- Expect a smaller set, not a cheaper run. Cardinality reduction is what the evidence supports today.

## Related

- [Pre-Change Impact Analysis](pre-change-impact-analysis.md) — selects tests from a code-to-test dependency map, the alternative selection criterion
- [Coverage-Aware Skill Selection Under a Token Budget](../context-engineering/coverage-aware-skill-selection.md) — the independent-coverage case this technique's negative result is about
- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](evidence-gated-lifecycle-control.md) — demands fresh evidence at each gate rather than restoring prior evidence
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md) — walks a finished run backwards from claim to evidence
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md) — where the evidence an envelope later selects gets produced
