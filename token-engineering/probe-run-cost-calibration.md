---
title: "Probe-Run Calibration for Predicting Agent Token Spend"
term: "Probe-Run Cost Calibration"
description: "One measured run at a fixed configuration cuts median error in predicting an agentic coding task's token spend from 161% to 36%, for about eleven cents."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - probe run cost prediction
  - single-run cost calibration
  - specification cost curve
last_reviewed: 2026-08-27
maturity: emerging
---

# Probe-Run Calibration for Predicting Agent Token Spend

> One measured run calibrates a cost curve, cutting median error in predicting an unseen coding task's token spend from 161% to 36%.

Probe-run calibration estimates what an agentic coding task will cost by measuring one run at a fixed configuration, then scaling a cost curve learned from other tasks. In a 2,700-run study across five SWE-bench Verified tasks, predicting a held-out task's spend from the other four was a median 161% off. One probe run at $0.11 cut that to 36% ([Smékal, arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).

## When it pays

Three conditions have to hold before the probe is worth running.

The workload has to repeat. The method learns a shape from tasks you already measured, marking which specification and effort combinations sit at the expensive end; the probe supplies only the absolute level for a new task. With no prior tasks there is no shape to calibrate.

Reasoning effort has to be low. The spread between the most and least expensive specification narrows from 2.13x at low effort to 1.67x at high and 1.61x at max ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). At max effort the prompt decides less, so there is less to gain.

You have to be unable to guess. Cutting a full eight-section specification down to a bare user story raised spend 29.7% overall, but "the same cut costs 13% on one task and 115% on another", which is why the paper's own advice is that "a practitioner should measure their own task rather than assume its cost sensitivity a priori" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).

## You cannot reason your way to the answer

The study cut seven of the template's sections one at a time, keeping the header throughout. Five of those removals could not be separated from noise — every interval includes zero: success criteria -5.4% [-12.7, +2.4], key entities -3.3% [-9.2, +2.8], assumptions -3.1% [-9.9, +5.1], edge cases -2.6% [-9.5, +4.3], functional requirements -2.4% [-11.8, +5.8] ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). Only the wholesale cut registered, at +29.7% with an interval running from +5.1% to +58.7%.

One section moved a different metric. Removing the Given/When/Then acceptance scenarios raised turns 7.0% [+1.6, +14.1], while removing the abstract success criteria had no measurable effect. Concrete scenarios buy something the abstract restatement does not.

The awkward result sits at the other end. The least structured prompt, a raw failing-test transcript, was cheapest of the eleven variations at low effort on four of five tasks, at 0.73x to 1.10x the full specification ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). Completeness is not the lever, so the answer has to be measured rather than argued.

## Why it works

Detail you leave out of the prompt gets bought back through reasoning and exploration. The authors put the mechanism directly: "At low effort, information withheld from the prompt is recovered by model reasoning, and that reasoning is what the missing section costs. At max effort the model reasons extensively regardless of the prompt details, so supplying the same information changes little" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). Same for the failing-test result: that transcript "names the file and test that must pass, and that localization substitutes for the discovery turns a prose specification leaves to the agent."

The cost of those turns lands on the output side. At the studied pricing and a 96.3% cache hit rate, "Output tokens are 2.7% of tokens processed but 51.1% of dollars", so input-side moves like prompt compression "address a small fraction of spend, whereas reducing turns addresses the majority of cost" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). A probe measures the thing that carries the money.

## When this backfires

- Max reasoning effort. At 1.61x spread the prompt is nearly a rounding error against the reasoning budget.
- A reproducible failing test already exists. Hand it over and skip the specification exercise; the transcript already carries the localization.
- Single-run A/B comparisons. Repeats within one specification and effort have "a median geometric standard deviation of ×1.34", so a one-run difference is inside the noise, and ranking is less stable still — split the fifteen repeats of a cell in half and the two orderings correlate at a mean Spearman of 0.41, projecting to 0.58 at the full fifteen ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).
- A different price schedule or cache hit rate. The output-heavy cost split "depends on the price schedule and cache hit rate rather than on the agent alone, so these percentages do not directly apply to other models or inference stacks" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).
- Treating 36% as precision. It is a median absolute percentage error over 32 held-out settings per task, not a confidence bound on any estimate.
- Generalizing past five tasks, one model, one scaffold. "Our study uses a single model, which is a core limitation" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).

## Example

The probe in the study was one run of the full specification at low thinking effort, on the task about to be priced, costing $0.11. It predicted the mean log cost across the other 32 specification-and-effort settings for that task.

Applied to your own workload, the loop is four steps:

1. Measure a handful of tasks you already run, across the specification forms and effort levels you actually use. That gives the shape.
2. For a new task, run it once at a fixed reference configuration and record the cost.
3. Scale the learned shape by that measurement to estimate the remaining configurations.
4. Re-measure when the model, harness, or price schedule changes, because the shape was fitted under all three.

Two-thirds of settings landed within 50% of actual after the single probe ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). That is enough to choose between configurations whose costs differ by 2x, and not enough to sign a budget.

## Key Takeaways

- Prediction is cheap and guessing is expensive: 161% median error without a probe, 36% with one, for $0.11 ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)).
- The 29.7% headline is a poor planning number. Per-task sensitivity ran 13% to 115%, so the study's own recommendation is to measure your own workload.
- No single specification section's removal produced a measurable cost effect, and the least structured prompt was often the cheapest. Argue about spec completeness and you will argue about the wrong variable.
- Better specifications move the mean, not the spread. Run-to-run variance held at 1.34x regardless, so comparisons still need repeats.
- The lever shrinks as reasoning effort rises, from 2.13x at low effort to 1.61x at max.

## Related

- [Request Shaping to Cut Wasted Agent Turns](request-shaping-wasted-turns.md) — what to put in the request once you know phrasing is worth tuning
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the measurement loop for spend you already incur, rather than spend you are forecasting
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — the frame that stops a cheaper configuration hiding a quality regression
- [Deliberation-Inducing Cues That Multiply Reasoning Cost](../patterns/anti-patterns/deliberation-inducing-prompt-cues.md) — phrasings that inflate reasoning tokens rather than retrieval turns
- [Reasoning Budget Allocation](../patterns/agent-design/reasoning-budget-allocation.md) — the effort knob whose level decides how much any of this matters
