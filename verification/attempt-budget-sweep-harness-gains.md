---
title: "Attempt-Budget Sweep for Harness Changes"
term: "Attempt-Budget Sweep"
description: "A harness change measured at one attempt budget can reverse at another. Sweep k, add a larger-model reference arm, and stratify by task difficulty."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - multi-budget harness scoring
  - elicitation versus expansion
  - pass@k sweep for harness optimization
last_reviewed: 2026-10-23
maturity: emerging
---

# Attempt-Budget Sweep for Harness Changes

> A harness change scored at one attempt budget can reverse at another, so sweep the budgets your deployment uses.

An attempt-budget sweep scores one harness change at several values of *k* instead of at pass@1 alone. Run the old and the changed harness *n* times over the same tasks, then read pass@*k* across the range.

The two curves can swap places partway along it. On LawBench an optimized GPT-OSS-20B harness led the GPT-OSS-120B baseline by 16.05 pp at pass@1, trailed it by 4.00 pp at pass@64, and gave up its advantage at *k*=11 ([Kim et al., arXiv:2610.27889v1](https://arxiv.org/abs/2610.27889v1)).

## When the sweep is worth its cost

The sweep in that paper spent 64 to 128 complete rollouts per task, so it has to earn the compute.

It earns that when the production system draws on more than one attempt. The paper names two cases: generated solutions used for self-training, and verifier-based selection. Coverage matters in both because it "captures the breadth of tasks for which a successful example or solution is available" ([Kim et al., §3.2](https://arxiv.org/abs/2610.27889v1)). Transfer to a new domain is the easiest case to justify, since the crossover arrives early there. A transferred text-classification harness held small pass@1 advantages on two out-of-distribution datasets, and both reversed at *k*=2 ([Kim et al., §5.3](https://arxiv.org/abs/2610.27889v1)).

A one-shot agent that never retries and never reuses a success has a different answer. pass@1 is the metric it deploys on. On LawBench the optimized 20B harness leads the larger 120B baseline by 16 pp at pass@1.

## What the sweep needs besides more attempts

Add a reference arm: the original harness on a larger model from the same family, or at higher reasoning effort. Without it the sweep shows only that the change beat its own predecessor, not whether a model upgrade was cheaper.

Then stratify by the difficulty labels your suite already carries, because the pooled curve hides the hard subset. On the hard subsets of HotpotQA and AppWorld, "none of the selected harnesses exceeds its stronger reference at any evaluated attempt budget" ([Kim et al., §5.2](https://arxiv.org/abs/2610.27889v1)). This half holds at a single attempt too: scaling produced larger mean hard-group pass@1 gains than harness optimization on all three benchmark panels.

Re-aiming the optimizer at hard questions did not repair it. Hard pass@1 rose from 56.88% to 59.28% against the 32B reference's 59.51%, while pass@128 stayed at 73.17%, so "the gain amounts to more frequent success without an increase in the number of hard questions solved within 128 attempts" ([Kim et al., §5.2](https://arxiv.org/abs/2610.27889v1)).

## Why it works

pass@1 and pass@*k* read two different quantities off one set of rollouts: mean accuracy, and the expected fraction of tasks solved at least once in *k* attempts. [pass@k and pass^k](pass-at-k-metrics.md) covers the pair in full. "A harness can therefore achieve higher mean accuracy but low coverage, by repeatedly solving the same tasks without obtaining successes on additional ones" ([Kim et al., §3.2](https://arxiv.org/abs/2610.27889v1)).

The paper suggests the answer depends on whether a change can alter what the agent observes. On static prediction the harness mainly reshapes how the solver uses a fixed input. On LawBench, the clearest static case, the gain came from making existing successes more frequent. On a dynamic task the harness also shapes actions and therefore the next observation. In that paper's HotpotQA run, the base harness reused the question as its second retrieval query. It never reached the "George Litto" abstract across 128 rollouts. Querying the newly resolved bridge entity instead reached it in 125 of 128, "turning previously inaccessible external evidence into usable context" ([Kim et al., §5.1](https://arxiv.org/abs/2610.27889v1)).

## When this backfires

- Small discrete label spaces inflate the tail of the curve. On tasks with discrete answers, pass@k at large k "reflects the increasingly higher chance of success in the limit of the number of trials rather than genuine reasoning, and can therefore be misleading" ([Dragoi et al., arXiv:2510.08325v2](https://arxiv.org/abs/2510.08325v2)). Read a crossover against a uniform-guessing baseline, and note where that guard runs out: it "is not applicable to LawBench and USPTO, which require open-ended structured outputs" ([Kim et al., Appendix C.2](https://arxiv.org/abs/2610.27889v1)).
- One optimization run settles nothing. Gains varied between runs, and the spread across three runs per benchmark "includes evaluation and preparation; it does not isolate optimizer variance" ([Kim et al., Appendix C.1](https://arxiv.org/abs/2610.27889v1)).
- A suite with no difficulty labels cannot be stratified honestly. The paper used dataset-level proxies on text classification, "informed by the success distributions" ([Kim et al., §5.2](https://arxiv.org/abs/2610.27889v1)).

## Example

LawBench, read from the task sets rather than from the curve. Of the 53 tasks the baseline harness solved at least once within 64 attempts, the optimized harness retained 49, lost 4, and newly solved 7. Those retained tasks supplied 21.02 pp of its 25.14 pp pass@1 gain, and the gain over the baseline narrowed to 3.00 pp at pass@64 ([Kim et al., §5.1](https://arxiv.org/abs/2610.27889v1)).

The harness made known-reachable tasks much more reliable and moved the reachable set by a handful of tasks. Both are true, and which one belongs in the review depends on whether the system gets one attempt or sixty-four.

## Key Takeaways

- Report the pass@*k* curve for a harness change and name the *k* where it crosses the baseline or the reference. On LawBench that crossing sat at *k*=11, so the deployment's attempt limit changes which system leads.
- Check transfer as its own measurement. On out-of-distribution datasets the reversal arrived at the second attempt, not at *k*=64.
- Skip the sweep for a one-shot agent and spend those rollouts on a difficulty-stratified pass@1 comparison against the larger model instead.

## Related

- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md) — the metric definitions this sweep reads across a range
- [PASS@(k,T): Evaluate RL for Agents Along Sampling and Interaction Depth](pass-at-k-t-agentic-rl-eval.md) — the same multi-budget diagnosis where RL post-training, not the harness, is the intervention
- [Harness Hill-Climbing: Eval-Driven Iterative Improvement of Agent Harnesses](../patterns/agent-design/harness-hill-climbing.md) — the optimization loop whose score this sweep re-reads
- [Isometric Harness Ablation: Rank Subsystem Investment by Removing One at a Time](../patterns/agent-design/isometric-harness-ablation.md) — which harness subsystem to change before measuring it
- [Size Agent Comparisons by Run-to-Run Variance](size-agent-comparisons-by-run-variance.md) — how many runs each arm of the comparison needs
