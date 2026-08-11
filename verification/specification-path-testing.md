---
title: "Specification-Path Testing: Same Contract, Different History"
term: "Specification-Path Testing"
description: "Restating one requirement through a different revision history flips which tasks a coding agent passes, even when the overall pass rate holds flat."
aliases:
  - specification-path sensitivity
  - conditional path violation
  - contract-equivalent history testing
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-11
maturity: emerging
---

# Specification-Path Testing: Same Contract, Different History

> Requirement histories with the same final contract flip which tasks an agent gets right while the pass rate holds flat.

Specification-path testing runs one agent against several requirement histories that resolve to the same final contract, then reports which individual tasks changed outcome. It applies when a requirement reached its final form through amendment (split across turns, overridden, retracted and restated) rather than arriving consolidated. Under those conditions a pass-rate comparison tells you almost nothing, because the rate can hold steady while the set of passing tasks turns over underneath it.

## What the test holds constant

SpecPath built seven histories per task and confirmed by formal replay that each one resolves to an identical final contract ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)):

| Condition | What the history does |
|---|---|
| Direct | States the consolidated contract once |
| Duplicate | Repeats the same requirement inertly |
| Split | Introduces the requirement's atoms across separate turns |
| Override | Explicitly replaces an earlier stated behavior |
| Cancellation | Retracts a requirement, then restates it |
| Paraphrase-direct | Rewords the direct statement (wording control) |
| Length-matched | Adds neutral turns without any revision (context control) |

Repository, verifier, and execution policy stay fixed, so history is the only variable.

## Why rate parity is the wrong readout

Across five tasks, seven model deployments, and two scaffolds, the direct condition scored a 78.8% final-contract rate and the four alternative histories averaged 78.7% ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). Read as an aggregate, nothing happened.

The per-item view disagrees. Of 100 blocks that succeeded on the direct specification and were scored on all five core histories, 35 failed on at least one contract-equivalent history, a task-macro violation rate of 36.4% (95% CI 25.6 to 45.1%) ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). Gains and losses offset, so the average hides both. Report conditional agreement instead: given a task the agent passed on one history, how often does it still pass on the others.

That number qualifies the [equivalence testing](equivalence-testing-agent-config-changes.md) posture. An equivalence test bounds how far a change moved a rate, and two conditions can sit well inside the margin while disagreeing on a third of the individual tasks.

## Why it works

The paper declines to name a single cause. It reports the mechanism as unidentified and supports only a narrow claim: under a matched execution policy, contract-equivalent presentation can change which competent blocks stay correct ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). That framing makes path sensitivity a family of presentation effects, not a fault in how models handle retraction. The worst condition constrains the reading: duplicate, which repeats a requirement inertly with nothing retracted and nothing to misread, produced the largest variant-specific violation rate, while the wording and added-context controls moved little ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). What survives is a claim about conditioning rather than comprehension. The agent conditions on the transcript it was handed rather than on a resolved contract, so changing the transcript changes what it conditions on, and inert repetition is enough to do it. A separate study reaches the same conditioning result from the cost side, finding that prompt wording changed where agent effort was spent and inflated cost by up to 18 times with success rates unchanged ([Weinberger and Hozez, 2026](https://arxiv.org/abs/2608.01347v3)).

## When this backfires

- Single-turn work. With no amendment history there is no path to vary, and the test has nothing to measure.
- Throughput as the decision. The aggregate moved 0.1 points, so a team that cannot act on per-task attribution gains nothing.
- Treating the contract ledger as settled practice. SpecPath recommends recording each requirement with a stable identity, scope, polarity, and a status of active, superseded, or canceled, then states plainly that whether this reduces violations without costing direct accuracy remains to be tested ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). Adopting it is a bet on an untested hypothesis.
- Generalizing the headline number. The benchmark covers five Python repository clusters and scored 127 of 210 possible complete blocks, and the authors state the synthetic paths supply experimental control, not evidence of how often such histories occur ([Wu et al., 2026](https://arxiv.org/abs/2608.09799v1)). Do not expect 36.4% on your own backlog.
- Ledgers that drift. A requirement ledger helps only while someone keeps it synchronized with what the team actually agreed, and that upkeep is the recurring cost the [Spec Growth Engine](../workflows/spec-growth-engine.md) page documents. Adopting one converts an ambiguity problem into a maintenance problem.

## Example

Suppose conditional agreement comes back poor on a repository where feature requests routinely arrive as a chat thread of corrections. The response the evidence supports is narrow: stop handing the agent the thread, and hand it the resolved active contract instead.

Two shipped tools already work that way. OpenSpec proposes each change as a delta spec marking sections ADDED, MODIFIED, or REMOVED, then merges them into one living source-of-truth document at archive time ([intent-driven.dev, 2026](https://intent-driven.dev/knowledge/spec-kit-vs-openspec/)). The `agent-spec` CLI carries a requirement state machine with explicit governed transitions such as `agent-spec requirements transition REQ-101 --to accepted` ([ZhangHanDong, 2026](https://github.com/ZhangHanDong/agent-spec)).

Neither has been measured against conditional path violation. What consolidation buys with certainty is a controlled variable, so that a failure is attributable to the contract rather than to the route by which it arrived.

## Key Takeaways

- Two ways of stating the same requirement can produce identical pass rates and a different set of passing tasks. Rate parity is not behavioral equivalence.
- Conditional agreement is the metric: of the tasks that passed on one history, how many still pass on the others.
- Inert repetition was the worst condition tested, so this is not a problem confined to overrides and retractions.
- The contract ledger is the paper's hypothesis, not its result. Treat consolidation as variance control, not as a measured accuracy win.

## Related

- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — the rate-level framing this finding qualifies, and the right tool once you also report per-item agreement
- [Repository Perturbation as Context-Reasoning Diagnosis (RepoMirage)](repository-perturbation-context-reasoning-diagnosis.md) — the same semantics-preserving perturbation method applied to the repository instead of the requirement history
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — sampling, infrastructure, and orchestration state as variability sources; specification path is a fourth this taxonomy does not list
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — the adjacent multi-turn finding, where later turns change the target behavior rather than converging on one contract
- [Frozen Spec File](../instructions/frozen-spec-file.md) — the authoring-side artifact that fixes an active contract before the session starts
