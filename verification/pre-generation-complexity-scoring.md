---
title: "Pre-Generation Complexity Scoring for Code Reliability"
term: "Pre-Generation Complexity Scoring"
description: "Complexity read off generated code is caused by the failure it is meant to explain. Score the task from the prompt before the run, on a fixed rubric, and publish the score with its rater disagreement instead of as a cutoff."
aliases:
  - Prompt-Side Complexity Index
  - Pre-Generation Difficulty Scoring
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-20
maturity: emerging
---

# Pre-Generation Complexity Scoring for Code Reliability

> Complexity measured on generated code is caused by the failure it explains, so score the prompt before generation instead.

Pre-generation complexity scoring rates a coding task's structural demands from the prompt alone, on a fixed rubric, before any model writes code, and keeps that rating separate from whether the run passed. The point is the timing. A number computed on the model's output cannot be an independent measure of the task, because a failed run usually emits something short.

## Read the conditions before the number

One study built this index and published a breakpoint with it. Take the method and leave the number.

On a benchmark of 5,000 Python prompts scored before generation and solved by 21 models, mean pass rate breaks at composite 13.75, with 79.9% at or below and 87.6% above ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). That 7.6-point gap does not survive its own controls. Adding nine task-type fixed effects moves the breakpoint to 10.75 and shrinks the gap to 2.1 points; adding a control for which of two prompt sources a task came from moves it to 8.50 and flips the raw gap to −3.5 points ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). Switching from mean to median pooling lands on 10.75 again.

The authors say it outright: the breakpoint "is not a universal failure cutoff." Most of the pooled rebound turns out to be which prompts came from where. The benchmark's two source frames average composite 7.92 against 11.42 and pass rate 0.747 against 0.880, and at the pooled threshold the later frame supplies 39.9% of the prompts below it but 94.7% of those above ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). Neither frame on its own reproduces the pooled change.

## The defect it fixes

Plot agent pass rate against the cyclomatic complexity of the code the agent produced, and the x-axis is downstream of the y-axis. When a model fails, the output "is often a short stub, partial solution, syntax error, or otherwise broken program with low measured cyclomatic complexity" ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)), so a hard task lands in a low-complexity bin. The task then looks easy and the model looks unreliable on easy work.

The effect is large enough to see. Among 14,776 zero-pass generations with a computable complexity value, 4,216 of them (28.5%) pair a structurally nontrivial prompt with generated-output complexity of 10 or less ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). Better than a quarter of the failures are filed under the wrong difficulty.

The argument is not specific to cyclomatic complexity. It applies to any difficulty axis read off agent output, so check your own dashboards for patch size, diff scatter, files touched, and lines changed. If the agent gave up after one edit, the change is small.

## The six dimensions

The rubric scores each prompt 0 to 4 on six axes, summed to a 0-to-24 composite ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

| Dimension | Score 0 | Score 4 |
|---|---|---|
| Branching | No conditionals | Deeply nested or combinatorial |
| Iteration | None | Nested recursion or complex multi-pass |
| State | Stateless or single variable | Concurrent state tracking |
| Data structures | Primitives only | Multiple interacting complex structures |
| Edge cases | None | Combinatorial interacting checks |
| Composition | Single operation | Pipeline of interdependent algorithms |

Three design choices carry the method.

The rubric anchors on expected solution structure, not on difficulty for a model. Asking a rater how hard a task is for an LLM builds the outcome back into the measure, which is the defect the timing change was meant to remove. Code length and language idioms are excluded for the same reason ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

Six separate axes beat one holistic score, because they show where raters disagree. Four judges scored the prompts, disagreement was kept rather than averaged away, and composite inter-rater reliability came to ICC = 0.872 on the 4,998 prompts with all four ratings ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

The scorers sit outside the evaluated panel. None of the four judges is one of the 21 models being measured, which the authors adopt to reduce circularity between the systems assigning index values and those whose reliability is measured ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

The index also tracks structure rather than phrasing: across 150 plain-language paraphrases its rank correlation is Spearman ρ = 0.963, with 91.3% of pairs within one point ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

## Why it works

Output-side complexity is a post-treatment variable. The paper writes the dependence as `κ_obs = g(κ*, y, η)`, where measured complexity is a function of the latent task structure, the outcome, and noise, and notes that failed generations "often collapse to short programs with low measured complexity" ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). Stratifying pass rate by that quantity conditions on something the outcome caused. Part of the correlation you read back is the conditioning.

Scoring the prompt cuts the arrow. The index is fixed before the evaluated system acts, so nothing the model does can move it. The authors name this precisely: "the central design choice is temporal rather than causal" ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).

Timing is the whole of the claim. Fixing it removes a mechanical dependence and grants nothing about accuracy or causality, and the paper tests both and settles neither. The six dimensions fail their joint exclusion restrictions badly when used as instruments, with a Sargan statistic of 411.32 on five degrees of freedom against an expected value near five, so the authors "make no causal interpretation" of those estimates ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). What survives is a clean measurement, not an explanation.

A second study puts a price on the same timing. PET-Select predicts code complexity and "uses code complexity as a proxy to classify queries and select the most appropriate PET", reporting up to 1.9% higher pass@1 with 74.8% fewer tokens on MBPP and HumanEval ([Wang et al., 2024](https://arxiv.org/abs/2409.16416v1)). A rough score, known before you spend, is still worth having.

## When this backfires

Judge agreement is the one to watch. On a calibration set deliberately enriched for judge disagreement, with LLM scores hidden, a human grader's agreement with the ensemble was ICC(2,1) = 0.395 and Pearson r = 0.408, with a systematic offset of −1.18 points ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). Four judges agreeing at 0.872 while agreeing with a person at 0.395 is what shared method looks like, not what correctness looks like. Rubric-based judging has a known failure of that shape: classifiers trained on rubric text alone, with no access to the response being evaluated, predict judge outputs at nontrivial accuracy, and judges "often fail to reliably update their decisions" when the response or the criterion is reversed ([Bagaria et al., 2026](https://arxiv.org/abs/2609.02942v1)).

A keyword count may be enough, and the study's own numbers are why. On its low-end discrimination check, a plain structural keyword count separated the two easiest reference tiers by +0.58 against the rubric's +0.61 ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)), and 30 surface linguistic metrics predict LLM performance on a requirements task at R² between 0.38 and 0.42 ([Motger et al., 2026](https://arxiv.org/abs/2608.27621v1)). Four judge calls per prompt has to beat free, and on that one head-to-head it barely did. Buy the rubric for its interpretable axes and its visible disagreement, or do not buy it.

Four more conditions narrow where a score means anything.

- A backlog of one kind of work. Most of the pooled signal was the task mix, so little survives inside one category.
- Routing by a threshold. Per-model breakpoints span 7.75 to 14.25 and five of 21 models move the wrong way across their own ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). The authors call these scores "diagnostic summaries, not deployment rules without prospective validation."
- Comparing across sampling frames. The two frames above differ by 3.5 composite points and 13 points of pass rate, so a score is comparable within a frame and not obviously across one.
- Extrapolating past the calibrated range. An audit-clean extension added 351 prompts at the two thin display bins but only 14 above them ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)). The top of the scale stays unresolved, which is where a team would most want to use it.

## Key Takeaways

- Any difficulty axis computed from agent output is caused by the outcome plotted against it. Over a quarter of zero-pass generations in one study land in the wrong difficulty bin for that reason ([Hernandez and Zhao, 2026](https://arxiv.org/abs/2609.19616v1)).
- Score the task from the prompt, before the run, on axes that describe expected solution structure rather than expected difficulty for a model.
- Report the score as an instrument. Publish the rubric, the per-bin support counts, the rater disagreement, and the curve under alternative pooling, then let a reader decide what it means for their mix.
- Do not carry a threshold across task types, prompt sources, or models. Every one of those controls moved the published breakpoint, and one reversed its sign.
- Check the cheap baseline first. A keyword count nearly matched the four-judge rubric on the one head-to-head test reported.

## Related

- [Static Difficulty Estimation for Agent Issue Triage](static-difficulty-estimation-issue-triage.md) — the ranking problem this measurement discipline feeds, where the strongest published predictors turn out to be computed on the reference solution.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the companion check on the y-axis, for when a regime gap is smaller than the benchmark's own variance.
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — how to report run-to-run spread so a per-bin mean is legible.
- [Risk-Based Task Sizing for Agent Verification Depth](risk-based-task-sizing.md) — the after-the-change counterpart, sizing review effort by what a file controls.
- [Pre-Execution Failure Scoring with a Draft Model (Speculative Uncertainty)](speculative-uncertainty-draft-model-gate.md) — the same "score before you act" idea moved inside the run, where the input is the agent's own emitted tokens.
