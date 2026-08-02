---
title: "Comparative Judging for Agent Configuration Ranking"
term: "Comparative Judging"
description: "Rank agent configs by best-worst comparative judging plus a Plackett-Luce utility model instead of averaging noisy absolute scores — for bake-offs where the goal is picking the winner."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - best-worst config ranking
  - MaxDiff agent evaluation
  - Plackett-Luce config ranking
last_reviewed: 2026-07-07
maturity: emerging
---

# Comparative Judging for Agent Configuration Ranking

> Rank agent configs by a judge's best-worst picks fed to a utility model, not by averaging noisy absolute scores.

Use comparative judging when the goal is to select the winning config in a bake-off and the quality signal is a noisy judge score. It replaces the mean of per-config absolute scores with two steps: a best-worst elicitation that asks a judge only for the strongest and weakest output in each batch, and a Plackett-Luce utility model that turns those choices into a global ranking ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)). The technique answers "which config wins," not "does this config clear a bar" — pick it for the first question, keep absolute scoring for the second.

## How the method works

1. Best-worst elicitation. For each test item, run a small sampled batch of configs, anonymize their outputs, and ask the judge to pick only the single best and single worst. This is Maximum Difference (MaxDiff) scaling — it avoids an artificial 1-to-10 scale and forces judgment where variation actually matters ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)).
2. Fitting a Plackett-Luce model. The model, from the Bradley-Terry family, converts each best/worst choice into a per-config utility score and returns a full ranking rather than a top-1. It can encode both main effects (how strong each factor is alone) and interaction effects (how a model, prompt, and tool behave in combination) ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)).

The output is a utility scale where a win over a strong config counts for more than a win over a weak one, so the ranking reflects who beat whom, not who scored high against soft alternatives.

## Why it works

Relative judgments remove three error sources that absolute scoring introduces: scale-region bias, where annotators favor one part of the scale; disagreement between annotators about what a 7 means; and drift in a single annotator's scale over time. Best-worst scaling controls all three, and at an equal annotation budget it is measurably more reliable than a rating scale ([Kiritchenko and Mohammad, 2017](https://arxiv.org/abs/1712.01765)). The same edge holds for model judges: LLM judges make more reliable relative calls than absolute pointwise scores ([Judging the Judges, 2024](https://arxiv.org/abs/2406.07791)). The Plackett-Luce step then aggregates local best/worst picks into one utility scale by weighting each win by the strength of the config it beat ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)).

## When this backfires

Comparative judging beats averaging only under specific conditions. It is worse than absolute scoring when:

- You need a threshold, not a ranking. Gating a release on a pass rate ("ship if the config clears 90%") needs a calibrated magnitude that a utility ranking cannot give — pair it with [pass@k and pass^k](pass-at-k-metrics.md) instead.
- Configs are correlated or near-duplicate. Plackett-Luce assumes independence of irrelevant alternatives; two variants of the same prompt violate it, distorting the utility estimates unless a nested or mixed model is used ([Bradley-Terry survey, 2026](https://arxiv.org/abs/2601.14727)).
- The comparison budget is tiny. Reliable utilities need many best-worst judgments. The source experiment's three-way interaction estimate had a 95% confidence interval of [0.023, 0.635] across 499 runs — wide enough that the ranking is not yet trustworthy ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)).
- The judge has uncontrolled position bias. LLM position bias is strongest exactly at the close calls that decide a ranking, so without swapping output order across permutations the ranking can reflect prompt position rather than quality ([Judging the Judges, 2024](https://arxiv.org/abs/2406.07791)).

## Example

The source article ran an invoice-extraction bake-off over combinations of model, prompt, and tool, sampling five configs per document across 100 documents ([Towards Data Science](https://towardsdatascience.com/stop-ranking-agent-configs-by-average-score/)). Config 5 (a systematic-planner prompt) had the highest main-effect sum at +0.201 — the value an average-of-components ranking would have rewarded. But once interaction penalties were applied, its total utility was −0.066, while Config 7 won at +0.431. Averaging the component strengths would have crowned the config that the comparative model ranked below zero, because the winning signal was the three-way interaction between model, prompt, and tool, not any factor alone.

## Key Takeaways

- Comparative judging ranks configs by best-worst (MaxDiff) elicitation plus a Plackett-Luce utility model, not by averaging absolute scores.
- Reach for it when selecting a bake-off winner with a noisy judge; keep absolute scoring when you need a pass/fail threshold.
- It works because relative judgments remove scale-region bias, inter-judge disagreement, and scale drift that pointwise scoring introduces ([Kiritchenko and Mohammad, 2017](https://arxiv.org/abs/1712.01765)).
- It backfires on correlated configs (IIA violations), tiny comparison budgets, and judges with uncontrolled position bias.
- Component strength is not configuration strength — interaction effects can flip the winner, as Config 5's positive main effect and negative total utility show.

## Related

- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md) — the absolute-threshold metric to keep when you need a pass/fail bar rather than a ranking.
- [Cost-Quality Pareto Measurement for Agent Configurations](../token-engineering/cost-quality-pareto-measurement.md) — builds the cost/quality points; comparative judging gives a more reliable ranking on the noisy quality axis.
- [Quality Score Rubric and Simplification Log for Agent Harnesses](../patterns/agent-design/quality-score-rubric.md) — the absolute A/B/C/D rubric this technique is the comparative alternative to.
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — what the judge should score in each best-worst batch: the end state, not the path.
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md) — why single-run scores are unstable, the noise comparative judging is built to survive.
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — how to build and size the suite whose scores this technique ranks.
