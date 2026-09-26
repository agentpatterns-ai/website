---
title: "Trajectory-Aware Benchmark Subset Selection for Agents"
term: "Trajectory-Aware Subset Selection"
description: "Keep the benchmark's pass-count strata, then replace the random draw inside each one with the instances nearest that stratum's trajectory-embedding centroid."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "embedding-within-strata selection"
  - "outcome-grouped centroid selection"
last_reviewed: 2026-09-25
maturity: emerging
---

# Trajectory-Aware Benchmark Subset Selection for Agents

> Trajectory-aware subset selection keeps a benchmark's pass-count strata and replaces the random draw inside each one with the instances nearest that stratum's embedding centroid.

Six OpenHands runs over 500 SWE-Bench Verified instances consumed 3.44 billion tokens between them, 99.3% of that volume being input ([Ayyad et al., 2026, Table 8](https://arxiv.org/abs/2609.24928v1)). A 10% subset costs about 10% of that, so the live question is which 10%. Grouping instances by their historical pass count and sampling inside those groups gets the difficulty mix right and the behaviors wrong: stratification "controls the proportion of passes and fails in the subset, but does not control which instances are selected from each group" ([Ayyad et al., 2026, §6.1](https://arxiv.org/abs/2609.24928v1)). Picking the instances nearest each group's trajectory-embedding centroid fixes the second half, under four conditions.

## When it pays

- The subset is under 20% of the suite. At 30% on the framework-change dataset, stratified random sampling reached a median RMSE of 0.0208 against the centroid method's 0.0216, so the embedding pipeline bought nothing on average and only trimmed the tail ([Ayyad et al., 2026, Table 5](https://arxiv.org/abs/2609.24928v1)).
- Two or more recent full runs are on hand with their trajectories kept. One prior run collapses the grouping to pass and fail, which the authors call too coarse to lower average error. Three runs is their recommended target ([Ayyad et al., 2026, §7.1.3](https://arxiv.org/abs/2609.24928v1)).
- The framework has not changed since those runs. A framework change rewrites the behavior the embeddings recorded, and the authors expect a full run after one ([Ayyad et al., 2026, §7.1.3](https://arxiv.org/abs/2609.24928v1)).
- The decision reads a suite-level resolve rate. Worst-case error at a 10% subset is still around 9 percentage points ([Ayyad et al., 2026, §6.2](https://arxiv.org/abs/2609.24928v1)), so a movement smaller than that sits inside the estimator's own error.

## Three rungs, priced against each other

Each rung is measured on the same 1,000 distributions under temporal cross-validation, so past runs pick the subset and later runs grade it ([Ayyad et al., 2026, §5.2](https://arxiv.org/abs/2609.24928v1)).

| Selection rule, 5% subset | Median RMSE | Worst-case error |
|---|---|---|
| Uniform random | 0.1090 | 20.21% typical draw, 47.22% worst seed |
| Pass-count strata, random pick within | 0.0746 | 14.42% typical draw, 34.61% worst seed |
| Pass-count strata, centroid pick within | 0.0679 | 12.92%, one deterministic value |

Figures are the Multi-model dataset, six OpenHands runs on SWE-Bench Verified ([Ayyad et al., 2026, Tables 3, 4 and 6](https://arxiv.org/abs/2609.24928v1)).

Rung two does most of the work: pass-count grouping cut median RMSE 31–51% against uniform random, with a 1000/0/0 win record ([Ayyad et al., 2026, §6.1](https://arxiv.org/abs/2609.24928v1)). Rung three is what the tail costs. One grouping key fails outright. Source repository improved on random by under 2%, and crossing it with pass count came out worse than pass count alone, because it splits the suite into strata too small to sample.

Rung three needs one vector per instance. Strip the outcome words and repository names from each trajectory, embed every step's action and observation, then join the step embeddings' mean and standard deviation with the first, middle and last step into a single 3,840-dimension vector ([Ayyad et al., 2026, §4.2 and §4.3](https://arxiv.org/abs/2609.24928v1)).

## Why it works

Stratified sampling controls variance only along the variable that formed the groups. Inside each group the draw is still random, so a subset can carry the right difficulty mix and whatever behaviors chance supplied. The ablations separate those two jobs. Selecting geometrically over the whole suite with no pass-count grouping raised RMSE 30–37%, because the typical instance of the whole suite is whatever difficulty dominates it. Using the embeddings only to shortlist a pool 1.5 times the target size and then sampling from it raised RMSE 21–26%, because the sampling step throws the narrowing away ([Ayyad et al., 2026, Table 7](https://arxiv.org/abs/2609.24928v1)). Determinism alone is not the mechanism: a fixed rule over past outcomes with no embeddings falls behind random sampling from a 20% subset up, by 19–90% on mean RMSE ([Ayyad et al., 2026, §6.3](https://arxiv.org/abs/2609.24928v1)).

## When this backfires

- Sizing a random draw may beat picking a clever one. MINCE simulates over per-item logs from a few calibration models, finds the smallest subset whose accuracy drift stays inside a bound, then fixes a random sample at that size. It reached 12 times lower drift on MMLU than tinyBenchmarks while using 57 times fewer calibration models ([Das et al., 2026](https://arxiv.org/abs/2606.22826v1)).
- The pass label the grouping rests on is noisy. Of 1,815 annotated OpenHands trajectories, 10.7% of the passes came through regression cycles, blind retries or missing verification, and ranking eight model backends by process quality instead of pass rate moved some of them by as many as five positions ([Sahoo et al., 2026](https://arxiv.org/abs/2605.12925v3)). Between any two Multi-model runs, 21% of instances flip outcome ([Ayyad et al., 2026, §8.3](https://arxiv.org/abs/2609.24928v1)).
- Sanitizing the trajectories is standing manual work, and incomplete. After four sanitization phases a TF-IDF probe still predicted pass or fail from the cleaned text at 66–80% accuracy ([Ayyad et al., 2026, §4.2 and §8.3](https://arxiv.org/abs/2609.24928v1)).
- Centroid selection picks typical instances, so it can miss the failure modes a new architecture introduces. The authors reserve a tenth of each group's slots for the most distant instances when that is the risk ([Ayyad et al., 2026, §7.1.3](https://arxiv.org/abs/2609.24928v1)).
- The statistics are dependent by construction. Any two of the 1,000 synthetic distributions share about a third of their instances, which makes the Wilcoxon p-values optimistic; the authors say so and rest their conclusions on Cliff's delta instead ([Ayyad et al., 2026, §8.4](https://arxiv.org/abs/2609.24928v1)).
- The pick buys no extra saving. It optimizes for representativeness, and the 10% centroid subset consumed 10.48% of the run's tokens ([Ayyad et al., 2026, §6.4](https://arxiv.org/abs/2609.24928v1)).

## Example

One unlucky stratified draw at a 5% subset took 12 instances that all passed on the Kimi K2 run. It reported a subset resolve rate of 1.00 against the suite's 0.43, an error of 57 points. The centroid pick over the same pass-count groups reported 0.42, an error of 1 point ([Ayyad et al., 2026, §6.2](https://arxiv.org/abs/2609.24928v1)).

That is the whole case for rung three. A team reading the first number reverts a good agent update; a team reading the second ships it. Both readings cost the same: a 10% subset takes the six-run bill from 3.44 billion tokens to roughly 345 million ([Ayyad et al., 2026, §6.4](https://arxiv.org/abs/2609.24928v1)).

## Key Takeaways

- Group by exact pass count across prior runs first. That one change cut median resolve-rate error 31–51% against uniform random sampling, and it needs no embeddings.
- The random draw inside each group is what leaves the tail exposed. Stratification cut a 5% subset's typical worst-case error only from 20.21% to 14.42%.
- Spend the embedding pipeline below a 20% subset and nowhere else. At 30% the stratified baseline matched or beat it on average error in one of the two datasets.
- Do not group by repository. It improved on random by under 2%, and combining it with pass count was worse than pass count alone.
- Treat a properly sized random draw as the competitor to beat. A drift-sized random sample reached 12 times lower drift on MMLU than tinyBenchmarks did.

## Related

- [Adaptive Validation Task Selection](adaptive-validation-task-selection.md) — the opposite move, drawing a fresh subset each tuning round from candidate disagreement rather than freezing one between full runs
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the run-to-run variance a subset estimate sits on top of and does not measure
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — where the tasks come from when no public benchmark with usable history applies
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — the same artifact read for diagnosis instead of used as a selection signal
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — how to report a result whose spread across draws is the finding
