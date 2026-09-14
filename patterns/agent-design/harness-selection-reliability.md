---
title: "Reliability of an Automatically Selected Agent Harness"
term: "Harness Selection Reliability"
description: "Automated harness tuning picks one run out of many, so report the worst run and the lower-quantile selected lift alongside the mean."
tags:
  - agent-design
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - harness selection variance
  - reliable lift reporting
  - selected-harness reliability
last_reviewed: 2026-09-11
maturity: emerging
---

# Reliability of an Automatically Selected Agent Harness

> A search that tunes an agent harness picks one run out of many, so report what that pick is worth in the unlucky case.

Automated harness tuning produces two numbers, and the headline usually quotes the wrong one. Mean held-out lift says how the search procedure performs on average across runs. What you deploy is the harness from the single run you picked, and that pick is itself a draw. When the search is noisy, the two numbers come apart.

## The conditions where this matters

Three conditions have to hold before selection variance is worth measuring. The search is stochastic and you run it more than once. The scorecard you select against is small, or graded by a simulator rather than by a fixed assertion. The winning harness ships without anyone reading its diff per run. Miss one and a single held-out number is an honest summary; the extra runs buy a confidence interval nobody acts on.

Where all three hold, the gap gets wide. On the τ²-Retail benchmark, the BH-MW optimizer found the joint-best individual harness at 23.0 percentage points over the baseline. Its worst run lost 13.5 points, only 58% of its runs gained anything, and the lift a deployer would get in the unlucky fifth-percentile case was −1.2 points. PRISM-MW found a lower peak of 21.6 points, but its worst run still gained 5.4 and its fifth-percentile selected lift was 10.1 ([Zhao et al., arXiv:2609.05736v2](https://arxiv.org/abs/2609.05736v2), Table 2). The paper's verdict on BH: "a strong explorer, an unreliable selector."

## What to report

| Number | The question it answers |
|---|---|
| Mean held-out lift | How does the search do on average? |
| Worst-run lift | What does the worst harness in the batch cost? |
| Fraction of runs with positive lift | How often does the search help at all? |
| Lower-quantile selected lift at budget B | What is the pick worth in the unlucky case, given what you can afford? |

The last row is the paper's RelLift₉₅(B), defined as "the lower (1−γ)-quantile of selected held-out lift over repeated uses of the same protocol, estimated by bootstrap over observed optimizer runs" ([arXiv:2609.05736v2](https://arxiv.org/abs/2609.05736v2)). Each bootstrap draw takes the N runs the budget affords, picks the one with the best pre-scorecard score, and records that run's held-out lift.

## Why it works

Selection is the causal step, not search. You pick the run that maximizes a proxy score "computed without access to" the held-out scorecard ([arXiv:2609.05736v2](https://arxiv.org/abs/2609.05736v2)), so a run that scored high by luck wins the argmax as readily as one that generalizes. Bootstrapping the selection procedure prices that gap instead of averaging it away.

Constraining what the optimizer may write shrinks the same variance. Middleware edits in the study were limited to three guarded intercepts at the tool boundary: "silent correction, rewriting malformed arguments before execution; error blocking, returning an explicit tool error so the model can retry; and prerequisite blocking, checking conversation or state history before allowing a call." Lifting that restriction on τ²-Retail dropped mean lift from 14.9 to 4.7 points, took the worst run from +5.4 to −4.7, and cut the fifth-percentile selected lift from 10.1 to 2.7 ([arXiv:2609.05736v2](https://arxiv.org/abs/2609.05736v2), Table 3). BH, the one optimizer whose middleware edits stayed unconstrained, scored below its own prompt-only variant on both τ² tasks.

## When this backfires

- Run the search once and the quantile is undefined rather than noisy. One run is not a distribution.
- The estimate can cost more than the tuning it qualifies. The protocol budgets up to 16 runs per arm, and logged inner-model cost per run spans $2 to $167 across the optimizers measured ([arXiv:2609.05736v2](https://arxiv.org/abs/2609.05736v2), Table 2).
- A stable tail over a broken scorecard proves the search is reproducible, not that the harness is good. An audit of agentic benchmarks found that "TAU-bench counts empty responses as successful," and that setup and reward-design issues shift measured performance "by up to 100% in relative terms" ([Zhu et al., arXiv:2507.02825v5](https://arxiv.org/abs/2507.02825v5)).
- The evidence is offline. The study's stated scope excludes "production traffic, changing user populations, long-running memory, adversarial users, or business-specific safety policies," and no experiment re-optimizes against failures that a previously optimized harness produced.
- Two τ²-Telecom rows were scored outside the benchmark-native pass^4 path, so cross-arm Telecom comparisons carry an orchestration caveat the authors state in their limitations.

## Key Takeaways

- A high peak and a reliable pick are different properties. An optimizer can hold the first and fail the second.
- Report four numbers for a tuned harness: mean lift, worst-run lift, fraction of runs with positive lift, and the lower-quantile lift of the selected run at your budget.
- Narrowing what the optimizer may edit is a reliability control, not only a safety one. Unconstrained middleware edits lost to prompt-only edits on both τ² tasks.
- The tail estimate is only as good as the scorecard beneath it. Audit the reward design before you trust a stable quantile.

## Related

- [Harness Hill-Climbing](harness-hill-climbing.md) — the eval-driven search loop this reporting discipline sits on top of
- [Isometric Harness Ablation](isometric-harness-ablation.md) — attributing a score change to one harness subsystem at a fixed model
- [Agent Runtime Middleware](agent-runtime-middleware.md) — the pre/post handler pipeline that tool-boundary edits live in
- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — the hand-written form of prerequisite blocking
- [Reflective Prompt Evolution with Pareto Selection (GEPA)](gepa-reflective-prompt-evolution.md) — one of the optimizer families measured under this protocol
- [pass@k and pass^k Metrics](../../verification/pass-at-k-metrics.md) — the reliability-sensitive scoring the τ² domains use
