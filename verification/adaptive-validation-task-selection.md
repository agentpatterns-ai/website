---
title: "Adaptive Validation Task Selection"
description: "Concentrate each harness-tuning round on the validation tasks candidate harnesses disagree about, then reweight that subset score into a full-set estimate."
term: "Adaptive Validation Task Selection"
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - variance-weighted validation sampling
  - co-evolving validation task selection
last_reviewed: 2026-08-24
maturity: emerging
---

# Adaptive Validation Task Selection

> Concentrate each harness-tuning round's evaluation budget on the validation tasks candidate harnesses disagree about, then reweight that subset score into a full-set estimate.

Three conditions decide whether this technique saves anything. Your validation pool must be large enough that a 20% sample is still dozens of tasks. You must already have per-task outcome history, because the sampler weights each task by its historical success rate. Evaluation must also dominate the loop's cost rather than candidate generation. Miss any one of the three and you are adding an estimator to save a resource that was not scarce.

Test the first two together. Pull your last few candidates' per-task results and count the tasks all of them passed or all of them failed. That count is what you pay for and get no ranking information from.

## The problem it addresses

Harness optimization "iteratively rewrites the harness code based on validation performance, enabling substantial performance gains without updating the underlying model weights" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). The standard loop runs the full validation set at every iteration, so it keeps paying for tasks that every candidate now passes and tasks no candidate has ever passed. Neither kind of task can order two candidates.

Task-CoEvolve replaces the fixed full pass with a sampled one and still reports a like-for-like score ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)).

## How the sampling works

Each task carries a sampling weight built from its historical success rate `p̄_t`:

```
w_t = max(p̄_t · (1 − p̄_t), ℓ_t) + λ / √n_t
```

The first term is Bernoulli variance. The floor `ℓ_t` keeps never-solved tasks in the pool at a low rate instead of dropping them forever. The `λ/√n_t` term is an uncertainty bonus for tasks with few observations, and it carries the sampler through early iterations before any real history exists.

Because the harness changes every round, `p̄_t` changes with it: "As the harness evolves, the sampling distribution also changes to focus on informative tasks for the current harness" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)).

## Making scores comparable across rounds

Different iterations evaluate different subsets, so raw subset means cannot be compared. The paper reweights by inverse sampling probability, using a Hájek estimator where task success rates sit near 0 or 1, and an anchored-difference estimator elsewhere that scores each task's deviation from its historical rate rather than its raw outcome ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)).

Skip the reweighting and a round that happened to sample easier tasks looks like an improvement.

## Why it works

A task every candidate solves and a task every candidate fails produce identical outcome vectors across candidates, so neither can rank them. Bernoulli variance measures that directly: "The first term represents the Bernoulli variance, which is largest at p̄_t=0.5 and becomes zero when the task is always solved or always failed" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). Ranking information lives where outcomes disagree, and the sampler spends the budget there. [Variance-Based RL Sample Selection](variance-based-rl-sample-selection.md) applies the same principle to a gradient step; a search loop needs the estimator on top because it has to compare rounds.

## When this backfires

- Small suites. The reported gains come at 7% and 20% of pools of 89 and 130 tasks ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). Shrink the pool and the sampled subset shrinks with it, until estimator variance swamps the gap between two candidates. The paper does not report where that point falls.
- No outcome history. The weight depends on `p̄_t`. A fresh suite has none, so early rounds sample close to uniform.
- Large harness rewrites. The anchored-difference estimator anchors on historical success rates that a big rewrite invalidates. No source measures that case directly. The nearest is extrapolation across *models*, where benchmark-subset methods "fail just when it is most needed: at the evaluation frontier" and "none of the previous methods consistently beat a simple average over random samples" ([arXiv:2506.07673v2](https://arxiv.org/abs/2506.07673v2)). Those methods depend on model similarity within a calibration pool, which a harness revision has no counterpart to, so read the analogy as this page's reasoning rather than a reported result.
- Weaker regression detection. A task the harness always passes has zero Bernoulli variance, and zero floor with it: `ℓ_t` "equals a small positive constant ℓ for tasks that have never been solved and 0 otherwise" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). Its entire weight is the `λ/√n_t` uncertainty bonus. That is by design for ranking, and it is also the sampling rate at which a newly broken task gets checked.
- More rounds against the same holdout. Cheaper evaluation buys more iterations, and repeated adaptive queries against a fixed holdout erode its validity ([arXiv:1506.02629v2](https://arxiv.org/abs/1506.02629v2)). SEAGym reports that "frequent updates may fail to improve held-out performance, useful intermediate snapshots may collapse later" ([arXiv:2606.17546v1](https://arxiv.org/abs/2606.17546v1)).
- No sequential stopping. The authors name this one themselves: "A limitation is that Task-CoEvolve fixes how many tasks each candidate is evaluated on before seeing any of its results" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). It cannot cut a clearly-worse candidate short, nor buy more evidence on a close call.

Full-set evaluation stays the safer default when a full pass is cheap. On Terminal-Bench 2.1 the sampled loop came in "only about 1% lower in both settings, which corresponds to just one task out of 89" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)). The paper reads that as parity, and names why full search is favored here: "Terminal-Bench uses the validation accuracy itself as the final evaluation result. Therefore, Meta-Harness (Full Search) has an inherent advantage because it can evaluate all tasks at every iteration." The claim is parity at lower cost, not a better harness.

## Example

The paper's online text-classification run used 20 search iterations with 3 candidates each. At a 7% evaluation budget, "Task-CoEvolve improves the few-shot accuracy from 41.6% to 47.6% while using 16 times fewer samples than full-set search". At 20% it reached 49.3%, ahead of the naive fixed-subset baseline by 2.1 points. On Terminal-Bench 2.1, run at 10 iterations with 1 candidate each, it "matches the performance of full-set search using only 20% of the evaluations, while reducing the overall search cost by 67-80%" ([arXiv:2608.20169v1](https://arxiv.org/abs/2608.20169v1)).

Both runs are small. Ten iterations of one candidate is a shallow search, so read the Terminal-Bench figure as a single data point rather than a rate you can plan against.

## Key Takeaways

- Measure per-task variance on your own suite first; if most tasks sit at 0 or 1, that share of your evaluation spend settles nothing
- The sampler is only half the technique, and without inverse-probability reweighting the scores from different rounds are not comparable
- Reported savings are 80% of evaluations at parity on Terminal-Bench 2.1, from a 10-iteration search with one candidate per round
- Schedule a periodic full pass anyway, because the sampler stops watching the tasks the harness reliably passes
- A validation gain is not a transfer gain, so keep a held-out set the optimization loop never samples

## Related

- [Variance-Based RL Sample Selection](variance-based-rl-sample-selection.md) — the same variance argument applied to selecting RL training data
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing a suite to the decision it has to settle
- [Comparative Judging for Agent Configuration Ranking](comparative-judging-config-ranking.md) — ranking candidates when absolute scores are noisy
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — why a single favorable run is not a result
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — the held-out gap this technique widens
