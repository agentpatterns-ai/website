---
title: "Agent Determinism Moves to the Last Unconstrained Axis"
term: "Last Unconstrained Axis"
description: "Constraining an agent's tool sequence while leaving the plan as free text can lower run-to-run reproducibility, because the unconstrained axis then carries all the variance."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - last unconstrained axis
  - partial harness determinism
  - structured planning validation
last_reviewed: 2026-08-29
maturity: emerging
---

# Agent Determinism Moves to the Last Unconstrained Axis

> Constraining an agent's tool sequence without validating its plan schema can lower reproducibility, because the last unconstrained axis becomes the only one that varies.

Strict run-to-run reproducibility is a conjunction over every axis of the execution trace, so the least-constrained axis sets the score. Constraining axes that already agree cannot raise it, and the control machinery you add perturbs the axis you left alone. Dhage measured that outcome: a first-pass deterministic harness made reproducibility significantly worse in two of four model-by-task cells, and better in one ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)).

## When this applies

The evidence is narrow. Check all three conditions before acting on it:

- You need exact-match trace reproducibility, not just a correct answer. The metric is "the strict fraction of runs whose complete execution trace exactly matches the group's modal trace" ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)). Audit replay needs it; most product work does not.
- The task is a linear state machine with deterministic ground truth. The study covers "two synthetic tasks, both linear four-state pipelines," and does "not evaluate branching, data-dependent, or judgment-based tasks."
- The backing model has capacity to spare, and you can measure latency on it before and after (see [when this backfires](#when-this-backfires)).

## What the four cells showed

The first-pass harness bound finite-state execution, one authorized tool per state, output validation, and bounded retry. It logged the planning step as free text. Reproducibility Rate at N=100 ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)):

| Task | Model | Baseline | Harness | Harness plus plan schema |
|---|---|---|---|---|
| finance_ecl | Qwen-2.5-7B | 0.91 | 0.93 (no effect) | 0.980 |
| legal_clause | Qwen-2.5-7B | 0.79 | 0.68 (worse, p=0.038) | 1.000 |
| finance_ecl | Gemma-3-27B | 0.42 | 0.55 (better, p=0.006) | 1.000 |
| legal_clause | Gemma-3-27B | 0.56 | 0.38 (worse, p<0.001) | 1.000 |

Task success reached 1.00 in three of the four cells once the plan carried a schema, and 0.98 in the fourth.

## Why it works

The Determinism Index decomposes into four sub-scores: Plan Stability, Tool Path Consistency, State Transition Stability, and Output Consistency. The trace diagnostic found the last three "were already at or near ceiling under both Baseline and Harness whenever a run succeeded," while "Plan Stability, however, remained low and highly variable in both conditions...because the harness logs the model's free-text plan but does not constrain its content or wording" ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)). The conclusion he draws is the mechanism: "Plan-text wording became, in effect, the only axis capable of driving an exact-match Reproducibility Rate result away from 1.0."

That is also why a partial harness can score worse than none. Retry and state machinery change the plan text the model emits, and the plan text was carrying the whole result.

## Applying the diagnosis

1. Decompose your variance by axis first, because one aggregate number cannot say which axis to fix ([variability layer decomposition](../../verification/sampling-state-agent-variability-layers.md)).
2. Find the axis that is not at ceiling. If tool path and outputs already match across runs, more tool constraints buy nothing.
3. Constrain that axis with a validator, not a prompt. Dhage's fix made the agent "emit a plan as a JSON array of `{state, intended_tool}` objects" checked against the finite-state graph before any tool ran.
4. Re-measure per model. Token cost fell in all four of Dhage's cells, between 14.8% and 16.7%.

## When this backfires

- Schema and tool calling together can stop the agent acting. Li, Zhang and Lv reproduced open-weight models that "cease invoking tools despite maintaining high schema compliance," because JSON Schema constraints "are compiled into grammar-based token masks, causing tool-call tokens to become unreachable during decoding" ([Li et al., 2026](https://arxiv.org/abs/2606.25605v1)). That is the combination this pattern recommends.
- Models near their limits lose accuracy under a schema. Haiku dropped 36.2pp under standard token budgets, largely from truncation, and GPT-4o-mini dropped 28.0pp with extended budgets that eliminated it, and the authors' remedy is to "think first, format later" ([Fan, 2026](https://arxiv.org/abs/2606.09410v1)) — the opposite ordering to validating a plan before execution. [Natural language tool selection](natural-language-tool-selection.md) covers the wider cost on weak models.
- Latency is model-dependent and can be large. Against baseline, Gemma-3-27B ran 47.0% and 41.4% slower under the plan schema while Qwen-2.5-7B ran 14.2% and 24.7% faster ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)).
- Branching work is outside the evidence. The study evaluated only linear pipelines and does "not evaluate branching, data-dependent, or judgment-based tasks" ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)), so a fixed state-and-tool plan schema is untested against a plan whose shape depends on the data.
- Your infrastructure is not the one measured. Dhage pinned API providers and "discarded infrastructure-driven failures," and still ran on "a third-party aggregation layer rather than direct, locally-controlled inference" ([Dhage, 2026](https://arxiv.org/abs/2608.26197v1)). A 1.000 measured that way is an upper bound; count those failures and see [simulation and replay testing](../../workflows/simulation-replay-testing.md) for what replay does not reproduce.
- The evidence is one single-author v1 preprint: four cells, two synthetic tasks, two open-weight models. The mechanism transfers; the numbers do not.

## Key Takeaways

- Exact-match reproducibility is set by the weakest axis, so constraining the axes that already match cannot improve it.
- A partial harness can score worse than no harness. Two of four cells degraded significantly before the plan carried a schema.
- Price the fix per model. On the same change one model ran up to 24.7% faster and the other up to 47.0% slower.
- Skip the exercise when you need a correct output rather than an identical trace.

## Related

- [Isometric Harness Ablation](isometric-harness-ablation.md) — remove one harness subsystem at a time to find which one carries the score
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — the model is a harness variable, which is why the latency split here is not an anomaly
- [Natural Language Tool Selection (NLT)](natural-language-tool-selection.md) — the case against forcing structured output on models that are weak at it
- [Decomposing Agent Output Variability by Layer](../../verification/sampling-state-agent-variability-layers.md) — attribute variance to a layer before choosing a mitigation
- [Stochastic-Deterministic Boundary as First-Class Contract](stochastic-deterministic-boundary.md) — where the validator sits between an LLM proposal and a system effect
