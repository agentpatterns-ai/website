---
title: "Scope-Matched Retrieval for Persisted Agent Skills"
term: "Scope Matching"
description: "Retrieve a persisted skill only for the task family whose evidence certified it. Holding the gate decisions fixed and changing only retrieval scope moved trajectory utility from 0.713 to 0.816 and harmful deployments from six of eight to none."
aliases:
  - family-scoped retrieval
  - certification-scoped memory
  - scope matching for agent memory
tags:
  - agent-design
  - memory
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-25
maturity: emerging
---

# Scope-Matched Retrieval for Persisted Agent Skills

> Retrieve a persisted skill only for the task family whose evidence certified it. Deploying a certified edit everywhere scored worse than learning nothing.

Scope matching splits one persistence decision into two. The gate that tested an edit settles whether it is supported; retrieval scope settles where it may be used. [Cheng et al. (2026)](https://arxiv.org/abs/2609.29144v1) measure the second decision on a 12-round code-repair stream over nine task families, holding the proposals and the acceptance decisions fixed and changing nothing but which tasks read the stored skill.

## When it applies

Your task stream has to revisit families. The benchmark "measures adaptation within recurring contracts" ([Cheng et al. 2026, §5.1](https://arxiv.org/abs/2609.29144v1)). A stream of one-off tasks never returns to a slot, so a per-family store accumulates nothing.

You have to be able to name the family at retrieval time. The paper's router classified held-out prompts at "100.0% accuracy (243/243)" ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)) because the families are procedurally templated. Open-world and wrong-slot routing are listed as future work ([§8](https://arxiv.org/abs/2609.29144v1)).

Certification has to be execution-grounded. The gate reads private exact-output tests and answer-free metamorphic checks, a channel reaching AUROC 0.998 ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)). Where a model judged its own proposals instead, 51.9% of what it accepted was harmful ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)).

The stored text also has to be family-specific. Scope costs nothing when the rule encodes one contract's quirk. It costs real transfer when the rule is general.

## Why it works

A regression gate can only test against evidence it holds, and it holds none for a family it has not seen. The authors state the limit of their own gate: it "cannot protect an unscoped global edit from interactions with task families that have not yet appeared" ([Cheng et al. 2026, §3.1](https://arxiv.org/abs/2609.29144v1)).

Every family in the global arm reads the same 360-character policy, so one accepted edit reaches all of them, and the family-level scores show the price. The accepted rule "raises boundary-family hidden utility by 0.398 on average, but simultaneously changes missing, rotation, tie-breaking, and chunk families by −0.461, −0.234, −0.148, and −0.117" ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)).

The scoped arm stores each accepted candidate in its originating family's slot, and a task from that family reads that slot while every other family reads the initial policy ([Cheng et al. 2026, §3.2](https://arxiv.org/abs/2609.29144v1)). Scope changes which policy is supplied, not the policy and not the decision. "The active policy remains exactly 360 characters" ([§3.2](https://arxiv.org/abs/2609.29144v1)), so the certified gain reaches its own family and nothing else moves. Across the 18-stream randomized-entry replication, mean non-current-family change is −0.047 globally against 0.000 scoped ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)).

A second effect follows, and it is the one I did not expect. The gate's own no-historical-regression clause stops blocking later edits, so acceptances rise from 12 to 63 across 27 streams ([Cheng et al. 2026, Table 6](https://arxiv.org/abs/2609.29144v1)).

## What the numbers show

Same accepted skills, same gate, different retrieval scope, across eight paired streams:

| Deployment | Mean trajectory utility | Accepted | Harmful |
|---|---|---|---|
| Static (learns nothing) | 0.775 [0.734, 0.814] | 0 | 0 |
| Global memory | 0.713 [0.653, 0.762] | 8 | 6 |
| Family-scoped retrieval | 0.816 [0.782, 0.852] | 8 | 0 |

Source: [Cheng et al. (2026), Table 4](https://arxiv.org/abs/2609.29144v1).

Read the first row before the third. Global memory scored below the agent that learned nothing, so the baseline a memory system has to beat is no memory. Over the full 27-stream extension the scoped arm leads by 0.063 [0.037, 0.094], with 0 of 63 acceptances harmful against 6 of 12 ([Table 6](https://arxiv.org/abs/2609.29144v1)).

## When this backfires

- Your task boundaries are fuzzy. Scoping trades a measured interference risk for an unmeasured routing risk, and the paper's routing was solved by construction ([Cheng et al. 2026, §6](https://arxiv.org/abs/2609.29144v1)). A wrong slot applies an edit where nothing certified it; a missed slot reverts to the initial policy.
- The store holds abstract meta-knowledge. Pooling memory across heterogeneous coding domains improved average performance by 3.7%, "primarily by transferring meta-knowledge, such as validation routines" ([Kim et al. 2026](https://arxiv.org/abs/2604.14004v1)). Pinning a validation routine to one slot throws that away.
- Interference is the wrong diagnosis. [Lin et al. (2026)](https://arxiv.org/abs/2608.22339v1) report the same symptom, with retrieved procedure skills raising "the wrong-tool margin by 47% over a memory-free baseline", then fix it by annotating each skill with applicability conditions instead of restricting retrieval. If your skills fail because their preconditions are unstated, scope buys nothing.
- You want the magnitudes to port. The study "covers inspectable scaffold edits with one frozen model and nine code-contract families" ([Cheng et al. 2026, §8](https://arxiv.org/abs/2609.29144v1)), in a v1 preprint posted on 24 September 2026. Take the direction and treat the numbers as a hypothesis about your own stream.

## Key Takeaways

- Record the scope at acceptance time, beside the evidence. An edit whose applicable scope you cannot name has not been certified, only observed to help once.
- Compare your memory system against the agent that persists nothing, not against a weaker memory system. Global memory lost to static by 0.062 here.
- Scoping is what let the gate keep accepting. If your self-improvement loop accepts one edit and then goes quiet, suspect the regression clause before the proposer.
- Budget for the router. It is the component this result assumes and the one your stream has to build.

## Related

- [Memory Transfer Learning: Cross-Domain Memory Reuse](memory-transfer-learning.md) — the opposite result for a different memory content type, where pooling across domains pays and abstraction level decides whether it does.
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — the prior question of whether to inject anything at all, where this page governs which stored item is eligible.
- [Weakest Consistent Learning: What Agent Loops Should Persist](weakest-consistent-learning.md) — chooses the content of the persisted rule, where this chooses its reach.
- [Subtask-Level Memory for Software Engineering Agents](subtask-level-memory.md) — the same scoping move keyed on reasoning stage instead of task family.
- [Tiered Memory Architecture: Episodic-to-Semantic Consolidation](tiered-memory-architecture.md) — promotion between tiers is the other point where an entry's reach widens, and it widens on re-use rather than on evidence.
