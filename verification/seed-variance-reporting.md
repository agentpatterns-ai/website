---
title: "Seed-Variance Reporting and Measurable-Range Eval Design"
term: "Seed-Variance Reporting"
description: "An eval effect that changes size with the random seed is a range to report, and a cell pinned at a floor or ceiling is a design fault to fix before any verdict."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - seed-sensitive eval results
  - measurable-range eval design
  - reporting the seed range
last_reviewed: 2026-08-09
maturity: adopted
---

# Seed-Variance Reporting and Measurable-Range Eval Design

> An eval result that moves with nothing but the random seed carries a seed range, and that range is the reportable finding.

Seed-variance reporting means publishing the spread of a result across seeds rather than the run that looked like an effect. It comes with a design precondition: every accuracy cell in the comparison has to sit inside the band where the contrast is attributable, away from both the floor and the ceiling. A number from outside that band describes the instrument, not the system under test.

## When the discipline applies

Three conditions decide whether this is executable for you.

- Seed control. Braintrust's negative-transfer study served base weights and a LoRA adapter from one vLLM process, which is what made a second seed possible ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)). Without it you can report a run-to-run range but cannot reproduce a specific run.
- A sample large enough for a spread to mean something. Over 13 matched pairs, excluding one capped pair moved a reported interaction from −0.077 to −0.167 ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)). A reproducibility study of reasoning benchmarks sets the bar higher, calling bootstrapping over 30 runs "a minimal standard for reliable evaluation" ([Hochlehnert et al., arXiv:2504.07086v2](https://arxiv.org/abs/2504.07086v2)).
- A contrast that a bound would destroy. Rare-event rates and zero-event arms sit at the floor on purpose, and [equivalence testing](equivalence-testing-agent-config-changes.md) turns one into a usable bound.

## Report the range, not the favorable run

Braintrust ran the same 13 matched pairs at two seeds. Seed 1 gave −0.462 with a bootstrap interval of [−0.692, −0.231], clearing every numerical rule the author had fixed in advance. Seed 0 gave −0.077 with an interval of [−0.769, 0.615], spanning zero. That is close to 0.4 of movement on identical tasks with only the seed changed ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)).

Both numbers came from one instrument, so the range is the result.

## Check the measurable range first

Set the band before scoring and treat a cell outside it as a design fault. Braintrust required every accuracy cell between 10% and 90%. Two successive designs failed that rule: a pilot where the adapter scored 0 of 8 on both tasks, and a holdout where both conditions scored 5 of 5 on the treatment task. Each apparent effect came from saturation rather than the contrast ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)).

The band belongs to your instrument and is not a constant. A permutation diagnostic for position bias is statistically detectable only inside a roughly 60% to 95% base-accuracy window, and outside it "absence of signal there should be read as not measurable, not unbiased" ([Tamba, arXiv:2607.20864v1](https://arxiv.org/abs/2607.20864v1)).

## Score the mechanism, not only the outcome

Add a measure of what the system did alongside whether it was right. Braintrust matched each numeric answer to the strategy that would produce it: correct answers averaged 2.23, double-counting 10.53, and counting every mentioned name near 22, with the signatures separating in 30 of 30 tasks. Accuracy swung 0.4 across seeds while the double-counting difference stayed at 0.0 in every run ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)).

Emit those labels during the run. That study could not reconstruct its central trajectory check afterwards: 20 of 104 traces were truncated and none carried run, seed, or episode identifiers ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)).

## Why it works

A paired difference-of-differences over a small sample has coarse granularity, so one flipped pair moves the headline by several points. Across 20 independent runs of nine models, "Pass@1 values show surprisingly high standard deviation—ranging from 5 to 15 percentage points across seeds", and on a 30-question benchmark "a change in just one question shifts Pass@1 by 2.5–3.3 percentage points" ([Hochlehnert et al., arXiv:2504.07086v2](https://arxiv.org/abs/2504.07086v2)). A categorical strategy label resists that swing because a perturbation big enough to flip an exact-match answer rarely carries it across a several-unit gap between classes. Near a bound the metric's variance is compressed instead, so a gap between conditions cannot be attributed to the contrast rather than to saturation ([Tamba, arXiv:2607.20864v1](https://arxiv.org/abs/2607.20864v1)).

## When this backfires

- Stacks where you cannot pin a seed. Re-running gives a run-to-run range that also carries infrastructure nondeterminism, so the spread is not attributable to sampling. Attribute it by layer first ([variability layer decomposition](sampling-state-agent-variability-layers.md)).
- Budget-bound programs. Eight reruns per cell takes a $40,000 agent-leaderboard sweep to roughly $320,000 ([EvalEval Coalition, 2026](https://evalevalai.com/research/2026/04/29/eval-costs-bottleneck/)). On a reversible decision, one run plus an honest interval beats precision nobody uses.
- Two seeds treated as a variance estimate. A spread across two runs bounds nothing, and quoting it as though it did repeats the original error at one remove.
- Measurements taken at a bound by design. A prespecified equivalence study saw no unauthorized tool call across 840 trajectories and reported an interaction interval of ±4.34 percentage points inside a ±7.01-point margin fixed in advance ([Xu and Wu, arXiv:2608.03169v1](https://arxiv.org/abs/2608.03169v1)).
- Variance dominated by something other than sampling. Where kernel and hardware drift or stochastic external tools carry the spread, fixing the seed neither reproduces nor characterizes it.

## Example

The same 13 matched pairs, rerun at a second seed, with the mechanism measure beside the accuracy measure ([Braintrust, 2026](https://www.braintrust.dev/blog/rlm-harness-negative-transfer)):

| Run | Interaction | Bootstrap 95% interval | Double-counting difference |
|---|---|---|---|
| Seed 0 | −0.077 | [−0.769, 0.615] | 0.0 (2 of 13 in each condition) |
| Seed 1 | −0.462 | [−0.692, −0.231] | 0.0 (1 of 13 in each condition) |
| Both seeds, 104 episodes | −0.269 | not reported | 0.0 |

Seed 1 alone reads as a confirmed effect. The pair of rows reads as an unstable accuracy metric over a stable mechanism, which is the honest summary.

## Key Takeaways

- Fix the reporting unit before the run: the seed range, not the best seed. Two seeds is the minimum that exposes instability and is still too few to bound it.
- Write the measurable band into the decision criteria alongside the effect threshold, so a saturated cell stops the study rather than producing a headline.
- Pair every outcome metric with a categorical measure of what the system did, and separate the classes wide enough that noise cannot cross the gap.
- Emit run, seed, and episode identifiers on every trace at run time. The trajectory check you skip is the one you cannot reconstruct.
- When the budget buys one run, publish the interval you have and call the result a prior.

## Related

- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — which layer a spread comes from, once you know it exists
- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — how to get a usable bound from a zero-event arm
- [Eval Blind Spots](eval-blind-spots.md) — structural gaps in what the harness can observe
- [pass@k and pass^k Metrics](pass-at-k-metrics.md) — aggregate metrics for run-to-run spread you cannot attribute
