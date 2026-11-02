---
title: "Judge a Technique Against a Budget-Matched Best-of-n Baseline"
term: "Budget-Matched Best-of-n Baseline"
description: "Score a code-quality technique against best-of-n sampling at the same call budget, on a measure the technique does not optimize. One of 66 techniques beat it in one study."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - compute-matched sampling baseline
  - best-of-n control arm
  - matched-budget technique comparison
last_reviewed: 2026-10-31
maturity: emerging
---

# Judge a Technique Against a Budget-Matched Best-of-n Baseline

> Run best-of-n sampling at the same call budget as the technique, then score both on a measure the technique does not optimize.

A technique that claims better code quality is compared with one call to the model, which has no retry and no choice among candidates. The technique spends more calls, so the comparison mixes technique with extra compute. A budget-matched baseline removes the confound. Draw n samples and keep the best one by a ranker. Set n to the technique's call-equivalent budget. A call-equivalent is one generated sample, or one feedback or reviewer turn.

Kadam ran this control against the code-quality literature. A review of 628 primary studies found that "compute, variance and contamination are rarely reported". A re-evaluation then ran ten techniques on four models at equal call-equivalent budgets of four, eight or sixteen ([Kadam, arXiv:2610.38977v1](https://arxiv.org/abs/2610.38977v1)). The paper is a single-author preprint. This page rests on its abstract, its introduction, and the compute ledger in Supplementary Material S12.

## What the control showed

At matched budgets, best-of-n sampling with an analyzer-weighted ranker "matches or beats prompting, planning, self-refinement, a reviewer agent and retrieval on measures the ranker does not optimize" ([Kadam, abstract](https://arxiv.org/abs/2610.38977v1)). The introduction counts this as 13 to 16 of 16 cells at four calls (four models, four metrics). Analyzer counts agree at eight and sixteen calls ([Kadam, §1](https://arxiv.org/abs/2610.38977v1)).

Two techniques did beat it, and only on one measure. An analyzer feedback loop and fine-tuning "beat it only on analyzer issue counts". A judge also rated the analyzer loop's code lower on every model ([Kadam, §1](https://arxiv.org/abs/2610.38977v1)). The loop improved the number it was fed.

The head-to-head widened the field to 66 techniques on Gemma 4 31B. One of 66 beat best-of-n on its primary target beyond the 95% interval, "a rate consistent with chance" ([Kadam, abstract](https://arxiv.org/abs/2610.38977v1)).

At one call, quality prompting raised analyzer issue counts and left complexity and judge scores almost unchanged. Quality instructions and planning raised maintainability issues on every model ([Kadam, §1](https://arxiv.org/abs/2610.38977v1)).

## How to apply it

1. Count the technique's call-equivalents per task. Each sample and each feedback, planning, or reviewer turn counts. Count a retrieval step only when it invokes the model. Use the maximum budget, not billed requests. On some open-model APIs one request returns several samples. Iterative methods that stop early use less than the budget ([Kadam, Supplementary Material S12](https://arxiv.org/abs/2610.38977v1)).
2. Run best-of-n with n equal to that budget, on the same tasks and models. The paper used budgets of 4, 8, and 16.
3. Choose the evaluation measures before you look at results. Include at least one the technique, and the baseline's ranker, did not use as a signal. A complexity metric, a judge model, or a security scanner the loop never saw all qualify.
4. Report correctness with the quality gains. The review found that "gains often come with unchanged or unreported correctness" ([Kadam, abstract](https://arxiv.org/abs/2610.38977v1)).
5. Run each arm more than once and report the interval. A single run cannot separate a technique from a lucky draw. See [Size Agent Comparisons by Run-to-Run Variance](size-agent-comparisons-by-run-variance.md).

## Check the benchmark before blaming the technique

On HumanEval+, which the author calls "a likely contaminated benchmark near its ceiling", large correctness losses appeared. They "do not appear on contests held after the models' training cutoffs" ([Kadam, abstract](https://arxiv.org/abs/2610.38977v1)). On LiveCodeBench Pro, no technique changed correctness beyond the 95% interval ([Kadam, §1](https://arxiv.org/abs/2610.38977v1)).

The finding does not say that techniques are safe for correctness. A drop on a likely contaminated benchmark may not carry over to fresh tasks. Confirm it on tasks released after the model's cutoff. [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) covers the wider check.

## Why it works

Best-of-n is the plainest way to spend extra calls. A technique that spends the same calls has to beat it to show it adds more than compute. Scoring on an unoptimized measure closes the second gap. A technique tuned against an analyzer can lower the analyzer count without an independent improvement in the code. The review notes that "single automated quality signals are gamed" ([Kadam, abstract](https://arxiv.org/abs/2610.38977v1)).

## When this backfires

- The ranker is analyzer-weighted, so the baseline is not neutral on analyzer issue counts. On that one measure the analyzer loop and fine-tuning beat it, which is why the unoptimized measure matters.
- The paper counts budget in call-equivalents. A reviewer pass that reads a long diff and a short sampling call cost different tokens and latency, so equal budgets are not equal spend. Match tokens as well if cost is the question.
- Best-of-n needs a ranker you can run. Where no cheap automatic signal exists for your quality target, the baseline costs more to build than the technique.
- This is one preprint on code from one set of benchmarks. The 1-of-66 figure and the chance reading are the author's. Repeat the control on your tasks before you drop a technique.

## Key Takeaways

- Set n to the technique's call-equivalent budget and run the best-of-n arm on the same tasks.
- At equal call-equivalent budgets of 4, 8, or 16, best-of-n with an analyzer-weighted ranker matched or beat prompting, planning, self-refinement, and a reviewer agent. It did the same against retrieval. The measures were ones the ranker did not optimize.
- A gain on the signal a technique optimizes is not a quality gain. Add a measure it never saw.
- Confirm a correctness loss on tasks released after the model's cutoff before you reject a technique on a saturated benchmark.
- Treat one study's 1-of-66 rate as a prompt to run the control, not as a verdict on any one technique.

## Related

- [Measure Agent Experience Against a Bare Baseline](ax-bare-baseline-lift-drag.md) — The same discipline for agent-friendly changes: score against a run with nothing added, and report cost beside quality.
- [Attempt-Budget Sweep for Harness Changes](attempt-budget-sweep-harness-gains.md) — Sweeps the attempt count k, because a harness change can reverse between budgets.
- [Blind Resampling Over Self-Repair in Small Code Models](../loop-engineering/blind-resampling-over-self-repair.md) — A matched-budget design that shows resampling beating repair for small models.
- [A Separate Critic Over Completion-Time Self-Checking](separate-critic-over-self-recheck.md) — Compares verification layers by task success and cost, not by code-quality measures.
- [Gate Best-of-k Selection on Compliance Before Score](compliance-gated-best-of-k-selection.md) — What the ranker in a best-of-n baseline should reject before it picks.
- [Search-Set Harness Gain as Capability Evidence](../patterns/anti-patterns/search-set-gain-as-capability-evidence.md) — Why a tuned harness's gain shrinks once the baseline gets the same inference budget.
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — The wider check behind the HumanEval+ finding.
