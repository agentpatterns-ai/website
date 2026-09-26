---
title: "Choosing the Judge Model That Grades Your Agent Evals"
term: "Judge Bake-Off"
description: "Replay frozen agent traces past every candidate judge, score them against human labels, and read each dimension only as far as the oracle's size supports."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - judge model selection
  - evaluator bake-off
  - judge comparison
last_reviewed: 2026-09-26
maturity: emerging
---

# Choosing the Judge Model That Grades Your Agent Evals

> Replay frozen traces past every candidate judge and score them against human labels. Cost separates on five examples. Accuracy does not.

A judge bake-off is a controlled comparison. You capture a set of agent runs once, freeze them, and have every candidate judge score that identical set against labels a human wrote. The output tells you which judge to adopt, but only along the dimensions the design isolated. A small oracle isolates fewer of them than a results table suggests.

## When to run one, and when not to

Run one when you are about to swap the judge and the suite gates something a wrong verdict would ship.

Skip it while the rubric is still moving. Judge prompt wording alone, with the judge model held fixed, shifted measured harmful-response rates by up to 24.2 percentage points across a safety benchmark ([arXiv:2604.24074v1](https://arxiv.org/abs/2604.24074v1)). Wording is the larger term for most suites. Settle it before spending labels on a model comparison. Skip it too on a suite you read only as a delta between agent versions, where a bias landing equally on both arms cancels in the difference.

Cheapness on its own is not a reason either. When the judge is no more accurate than the model under test, "no debiasing method can decrease the required amount of ground truth labels by more than half", and the savings seen in practice sat below that ceiling ([arXiv:2410.13341v4](https://arxiv.org/abs/2410.13341v4)).

## What the comparison has to hold fixed

Frozen inputs, a human-written oracle, one rubric across every arm, and identical decoding across every arm. LangChain's public comparison of the Jev decision model against three LLM judges holds the first three, which makes it a worked example in both directions.

Its inputs were frozen: "For each example in the dataset, we captured the weather agent's response and stored the full output as a fixed example in LangSmith", so every judge scored byte-identical text and agent stochasticity left the comparison. Its oracle was human, and one rubric ran throughout: "we had a human reviewer label each fixed response against the same rubric" ([LangChain](https://blog.langchain.com/jev-agent-evals-langsmith/)).

Decoding is the control that slipped. LangChain states it plainly: "We did not set temperature, top-p, seed, or max tokens for the LLM judges, so each provider's defaults applied" ([LangChain](https://blog.langchain.com/jev-agent-evals-langsmith/)). In a five-temperature sweep, three autoregressive judges reached a McDonald's omega of 1.0 on every benchmark at temperature 0, against values as low as 0.421 at higher settings ([arXiv:2412.12509v2](https://arxiv.org/abs/2412.12509v2)). A variance gap measured against provider defaults mixes a model-class difference with a settings difference.

The shipped integration repeats the same gap. Its evaluator setup asks only for a provider and a model: "select TypeSafe as the Provider and `jev-latest` as the Model" ([LangChain](https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals)). LangChain also flags a data-retention caveat for that integration: "Note that TypeSafe does not currently offer zero data retention, so prompts and outputs sent for evaluation may be retained by the provider" ([LangChain](https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals)).

## What that experiment settled, and what it left open

| Dimension | Reported result | What the design supports |
|---|---|---|
| Cost | $0.00035 per call; $0.34 total against $28.17 for Claude Sonnet 4.6 | Settled. Every call is an independent measurement. |
| Latency | 0.44s mean | Settled, on the same grounds. |
| Score variance | Mean per-case variance 0.0000149, against competitors 92x to 913x higher | Confounded. The LLM arms ran at provider default decoding. |
| Accuracy | 100% oracle agreement against 99.8%, 96.4% and 80.0% | Unresolved. Five labeled items, one reviewer. |

Figures from [LangChain](https://blog.langchain.com/jev-agent-evals-langsmith/). The 500 repeated decisions per judge are 5 items scored 100 times. The project's own repository draws the same line: "the result describes this experiment; it is not a general ranking of judge accuracy" ([repro repository](https://github.com/danielgshea/jev-as-a-judge)).

## Why it works

A judge's error is invisible to the suite it grades, because the judge is what produces that suite's numbers. Sizing the error needs labels the judge did not generate, so the comparison runs against an independent oracle rather than against the agent's own scores. The resolution limit follows directly: with judge-oracle agreement `r`, "we could only reliably rank models for which the true score 𝔼s(m) differs by more than 2(1−r)" ([arXiv:2410.13341v4](https://arxiv.org/abs/2410.13341v4)). Freezing the traces is what makes `r` measurable at all, since it removes the agent as a source of variation and leaves judge behavior as the only thing moving.

That bound also explains the asymmetry in the table. Cost and latency are measured on every call, so 500 calls give 500 independent measurements of each. Accuracy is measured against 5 labeled items however many times they are re-scored, so the resolvable gap stays wide.

## When this backfires

- A vendor ran it. TypeSafe's own benchmark for Jev uses "the predictions of the largest, smartest, and most expensive external models as reference probabilities", and its LLM comparison wrapper "tends to be slower and more expensive than giving decisions without probabilities" ([TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev)). The oracle is a model and the opposing arm is handicapped.
- A raw match rate stands in for chance-corrected agreement. Across 21 judges and roughly 541,000 judgments, "kappa deflation between exact match and Cohen's kappa is universal (33--41 pp on MT-Bench)" ([arXiv:2606.19544v1](https://arxiv.org/abs/2606.19544v1)).
- One narrow task distribution stands in for yours. Five weather requests is a single domain, and judge "rankings shift by up to 14 positions across benchmarks" ([arXiv:2606.19544v1](https://arxiv.org/abs/2606.19544v1)).
- The winner is trusted because it is stable. Test-retest reliability above 0.95 coexisted with position bias above 0.10 in two production-deployed judges ([arXiv:2606.19544v1](https://arxiv.org/abs/2606.19544v1)).
- Single-trial scoring goes to production. Pairwise preferences flipped 13.6% of the time on re-run, and "11 repeated trials are needed for a majority vote to recover the 50-trial reference verdict with 95% probability on average" ([arXiv:2606.13685v1](https://arxiv.org/abs/2606.13685v1)).

## What to re-baseline after a swap

Re-baseline every threshold that was calibrated against the old judge. A new judge moves the score distribution, so pass marks, regression alerts, and any historical trend line shift with it. The swap does not always start with you. `jev-latest` is a floating alias, so the model behind the judge can change without you touching a config file ([LangChain](https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals)). Size the fresh human labeling by the power you need rather than by habit. Sample sizes for the human and model halves can be chosen to hit a target power, with more human ratings allocated where model predictability is lowest ([arXiv:2605.16354v1](https://arxiv.org/abs/2605.16354v1)).

## Key Takeaways

- Freeze the traces before comparing judges. Otherwise you measure agent variance and judge variance together.
- Hold decoding identical across arms, or the variance column reports a settings difference.
- Repetitions raise precision on each item and never raise the count of independent items, which is what the accuracy ranking rests on.
- Rank on chance-corrected agreement, not on raw match rate.
- Re-baseline every threshold after the swap, and budget the human labels by target power.

## Related

- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — measuring the error of the judge you already run, once it is chosen
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — replaying one judge over time to find its noise floor
- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — the bias a bake-off misses when every arm scores the same generator
- [Human-Review-Driven Curation of Golden Eval Datasets](human-review-golden-dataset-curation.md) — growing the labeled oracle this comparison depends on
- [Evaluator Templates: Portable Primitives for Agent Eval Suites](evaluator-templates.md) — the rubric layer to settle before comparing models
