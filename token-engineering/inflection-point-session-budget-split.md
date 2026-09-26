---
title: "Splitting an Agent Token Budget at the Scaling Inflection Point"
term: "Scaling Inflection Point"
description: "Locate the per-session budget where an agent's marginal quality gain drops below repeated sampling, then split the total budget into that many parallel sessions instead of running one long one."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - scaling inflection point allocation
  - Elo-per-token analysis
  - parallel session budget split
last_reviewed: 2026-09-24
maturity: emerging
---

# Splitting an Agent Token Budget at the Scaling Inflection Point

> Past the budget where a session's marginal quality gain falls below repeated sampling, a fresh parallel session buys more than more tokens.

Three conditions gate this technique, and most agent work fails at least one. Intermediate solutions need a continuous automated score. The per-session budget has to reach the crossing point, which the paper's worked task puts at 38M tokens. The task shape has to recur often enough to pay back the profiling runs. Miss one and a single long session is the better spend.

## The three conditions

Liu et al. picked FrontierCS, ALE-Bench, MLS-Bench and FlashInfer-Bench because all four have "task-specific, deterministic automated evaluators", and note that "None relies on an LLM-as-a-judge or subjective human ratings" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)). A pass-or-fail task produces no curve to measure and no way to rank K finished sessions against each other.

Scale is the second gate. The crossing on the paper's worked task sits at 38M tokens, and even the smallest split it compares, ten sessions of 10M tokens, "far exceeds Kimi K2.7's 256K-token context window" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)). Below the crossing the ordering reverses: "One session leads at small budgets, while interior allocations overtake it at larger budgets."

Third, the measurement has to amortize. Profiling one system on one task took five independent sessions at a 100M-token target, and a cheaper domain-level curve does not substitute: "the slope crossing of Kimi K2.7's FrontierCS domain curve does not align with the 38M-token inflection point of Polyomino Packing" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)).

## Finding the crossing

Record the best solution the agent holds at each token budget, not the one it finally submits. Raw scores do not combine across tasks, so convert them to ratings: each budget's best submission plays pairwise against the others, and a Bradley-Terry model aggregates those within-task orderings into one Elo scale ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)).

The line to compare that curve against is proved, not fitted: solving a problem k times independently and keeping the best produces an Elo that grows linearly in log compute, at 400 Elo per decade of tokens ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)). The scaling inflection point is the last budget at which your measured curve is steeper than that line. Below it, extending the current session returns more per token; above it, an independent session does.

The allocation rule reads straight off the point. For a total budget B and a crossing at b, run K = max(1, round(B / b)) sessions in parallel and stop when their combined usage reaches B.

## Why it works

The causal account is a sticky basin. Early in a session the agent commits to what the authors describe as "an algorithmic idea, code structure, or high-level strategy that becomes increasingly difficult to abandon as context accumulates" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)). Inside one basin, the best score after T samples grows to leading order as the basin mean plus its standard deviation times the square root of 2 log T, so multiplying session depth by any fixed factor moves that term by only O(1 / sqrt(log T)). Differences between basins do not shrink at all. The limit result follows: for two independent sessions at budgets T and cT, the probability that the deeper one wins approaches one half.

So more tokens in the current session buy within-basin refinement, and that term is flattening. A new session redraws the basin, which is where the variance worth sampling still sits.

The human comparison shows the flattening is a harness limit rather than a task ceiling. On shared AtCoder Heuristic Contest tasks "the strongest historical human contestants improve superlinearly over contest time", which the authors read as "substantial headroom after agents slow down" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)).

## When this backfires

- No continuous scorer. Standing in an LLM judge imports the failure modes of pairwise ranking, where applying these algorithms "as constructed in the context of LLM evaluation introduces several challenges" ([Daynauth et al., 2025](https://arxiv.org/abs/2411.14483v2)). You then fit a curve that measures the judge.
- Ordinary session sizes. A 200K-token coding session sits two orders of magnitude below the measured crossing, where the paper's own comparison puts one session ahead.
- Serial work. The rule assumes independent sessions whose single best result is returned. K sessions editing one repository produce K diffs that do not compose.
- One plausible approach. Where a framework or an obvious fix forces the solution shape, resampling redraws the same basin and buys only the term the mechanism says is shrinking.
- Accumulated state is the asset. Sinha et al. trace failures on longer tasks to "mistakes in execution, rather than an inability to reason", and report a self-conditioning effect where "models become more likely to make mistakes when the context contains their errors from prior turns", which "thinking mitigates". They close on "the massive benefits of scaling model size and sequential test-time compute for long-horizon tasks" ([Sinha et al., 2026](https://arxiv.org/abs/2509.09677v3)). On that reading the fix is context hygiene, not a restart.

## Example

On FrontierCS Polyomino Packing with Kimi Code and Kimi K2.7, the measured crossing is 38M tokens. For a 100M-token budget the rule gives K = round(100 / 38) = 3, so three sessions run in parallel until their combined usage reaches 100M tokens. Against the two extremes, that allocation gained +264 joint-Elo over a single 100M-token session and +355 over ten 10M-token sessions ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)). MLS-Bench reproduces the direction: the inflection-point allocation beats both one long session and ten short ones.

The same shape holds for specialized strategies rather than only general agents. AdaEvolve "leads Kimi Code by more than 300 Elo near 100K tokens", then "the three methods lie within ~20 Elo of one another" by Kimi Code's last checkpoint, and test-time training on `gpt-oss-20b` shows "a brief period of faster-than-sampling scaling, followed by diminishing returns" ([Liu et al., 2026](https://arxiv.org/abs/2609.15309v1)).

## Key Takeaways

- Score the best solution held at each budget, not the submitted one, or the flattening is invisible until the run ends.
- Repeated sampling is the reference line, at 400 Elo per decade of tokens; a session is worth extending only while it beats that slope.
- Splitting below the crossing loses. Check where your budget sits before applying the rule, because one session leads at small budgets.
- The crossing is task-level. A domain-level curve measured on sibling tasks did not predict it, so the profiling cost is per task shape.
- A flat curve is a reason to restart or change the harness, never evidence the task is exhausted.

## Related

- [Convergence Detection in Iterative Agent Refinement](../loop-engineering/convergence-detection.md) — stopping signals for refinement loops that have no scalar score to curve-fit
- [Calibrated Early Termination and Warm Restart for Agent Runs](../loop-engineering/early-termination-and-warm-restart.md) — killing runs predicted to fail, the complementary reason to end a session early
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — the comparison frame one level up, across configurations rather than budget splits
- [Recursive Best-of-N Delegation](../patterns/multi-agent/recursive-best-of-n-delegation.md) — the selection step this rule depends on, applied at each node of a delegation tree
- [Effective Feedback Compute (EFC) for Harness Comparison](../patterns/agent-design/effective-feedback-compute.md) — an alternative scaling coordinate that credits informative feedback instead of raw tokens
