---
title: "Cost-Quality Pareto Measurement for Agent Configurations"
term: "Cost-Quality Pareto Measurement"
description: "A measurement frame that plots each agent configuration as a (cost, quality) point and keeps only the non-dominated set — so a downgrade that trades quality for cost shows as a vertical drop off the frontier, not as a lower bill."
tags:
  - token-engineering
  - cost-performance
  - evals
  - tool-agnostic
last_reviewed: 2026-06-29
maturity: established
---

# Cost-Quality Pareto Measurement for Agent Configurations

> Cost-quality Pareto measurement plots each agent configuration on the non-dominated cost/quality frontier — quality-trading downgrades become visible.

Token engineering's premise — fewer, cheaper tokens *without* losing quality — depends on a frame that surfaces the *without*. Plotting each configuration's mean cost against its mean task quality and drawing the non-dominated frontier turns the trade-off into a graph: a cache-on or batch-API change moves a point left along the frontier, a model downgrade that loses quality drops it below the frontier ([Kapoor et al., "AI Agents That Matter", arXiv:2407.01502](https://arxiv.org/abs/2407.01502)). Without the joint plot, both changes register on the bill as "lower spend" and the quality regression hides until users complain. The mechanism formalises what [token-cost profiling for always-on workflows](token-cost-profiling-always-on-workflows.md) drives toward — the unit on which configurations are *compared*, not just measured.

## A configuration is the joint product

A configuration is the joint product of every knob that affects spend or quality on the same task:

- Model and tier — Claude Haiku 4.5, Sonnet 4.6, Opus 4.7; the Effective Tokens multiplier is `0.25 / 1.0 / 5.0` respectively ([GitHub Blog: Improving token efficiency in GitHub Agentic Workflows](https://github.blog/ai-and-ml/github-copilot/improving-token-efficiency-in-github-agentic-workflows/)).
- Reasoning effort — `low | medium | high` (or off) on reasoning models; an opt-in knob with its own cost slope ([HAL: Holistic Agent Leaderboard, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)).
- Context discipline — how much skill, tool, and rule context is loaded; sets the input-token floor.
- Cache regime — prompt-cache write/read multipliers stack with the model tier (Claude: write 1.25x at 5m, 2x at 1h; read 0.1x base input) ([Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)).
- Temporal tier — synchronous vs. Anthropic Batch API (50% off input and output, <24h SLA, typically <1h) ([Anthropic — Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)).
- Scaffold or harness — retry, escalation, multi-agent, tools enabled.

A single change to any knob is a new point on the plot. A Pareto sweep over even modest grids (3 models x 3 effort levels x 2 cache regimes x 2 batch tiers = 36 cells) is what makes the dominated configurations identifiable.

## The cost axis: USD per successful task

Three rules keep the cost axis comparable across cells.

- Denominate in USD per task, not raw tokens. Output tokens cost roughly 4-5x input on Claude (e.g., Sonnet 4.6: $3/MTok in, $15/MTok out) ([Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)). A token-count axis under-weights output-heavy configurations.
- Collapse the price components into one number. GitHub's Effective Tokens metric `ET = m × (input + 0.1 × cache_read + 4 × output)` (with `m = 0.25 Haiku, 1.0 Sonnet, 5.0 Opus`) is the production form: one scalar that ranks correctly across tier, output ratio, and cache hit rate ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/improving-token-efficiency-in-github-agentic-workflows/)). Convert ET to USD with the model's per-token price for the plot.
- Divide by successful, validated outputs. Retries and failed runs belong in the cost axis. If 100 user requests need 112 attempts to produce 100 valid responses, cost is `total_spend / 100`, not `total_spend / 112` ([LayerLens — LLM cost optimization in production systems](https://layerlens.ai/blog/llm-cost-optimization)). Raw spend over raw call count flatters configurations that fail and retry.

## The quality axis: pick one outcome metric

The quality axis depends on the task surface:

| Task surface | Quality metric | Example |
|---|---|---|
| Code generation / edit | Test pass rate on a fixed exercise set | Aider polyglot benchmark — percent correct over 225 Exercism exercises across 6 languages ([Aider leaderboards](https://aider.chat/docs/leaderboards/)) |
| Multi-step agent (web, research, science) | Task pass rate on a benchmark suite | HAL — nine benchmarks across coding, web navigation, science, customer service ([HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)) |
| Free-form generation | Rubric score from a judge — with caveats | Run-to-run variance must be measured; LLM-as-judge scores can drift with rubric wording ([LLM evaluation review, Weights & Biases](https://wandb.ai/onlineinference/genai-research/reports/LLM-evaluation-Metrics-frameworks-and-best-practices--VmlldzoxMTMxNjQ4NA)) |
| Structured extraction / classification | Field accuracy, precision/recall against a labelled set | Deterministic; no judge variance |

One axis per plot. Mixing surfaces collapses configurations that win on one task and lose on another.

## What the frontier looks like in practice

Two findings recur across published Pareto sweeps and constrain how to read the plot.

The frontier is sparse. Across 21,730 agent rollouts spanning nine models and nine benchmarks ($40,000 spend), HAL reports that less than one-third of tested models sit on the frontier for a given benchmark on average, and the most costly models are rarely Pareto-optimal ([HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)). A Q2 2026 cross-vendor study of 20 frontier models tracked across OpenRouter found that only six sat on the joint cost/quality/speed Pareto frontier — fourteen were dominated on every dimension by a cheaper or faster sibling, yet most still shipped production traffic ([Digital Applied — AI Model Efficient Frontier Q2 2026](https://www.digitalapplied.com/blog/ai-model-performance-vs-price-efficient-frontier-q2)). The implication: choosing on intuition overspends by reflex.

Higher reasoning effort frequently lowers accuracy. HAL: increased reasoning-token budget reduced accuracy in 21 of 36 model x benchmark settings tested ([HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)). Reasoning is a knob with its own Pareto sweep — the cheapest effort tier that holds quality is the default, not the highest one.

Kapoor et al.'s headline result on HumanEval: a simple warming-strategy baseline matched the LATS architecture's accuracy at roughly 2% of LATS's cost ([arXiv:2407.01502](https://arxiv.org/abs/2407.01502)). The Pareto frame is what makes that gap legible — without it, LATS's accuracy looks like a win.

## Why it works

The same change registers differently on a bill and on the frontier. A Batch-API switch holding quality is a horizontal move left along the frontier; a model downgrade losing 10 quality is a vertical move off it. The bill collapses both into "lower spend" and hides the regression until users complain. Kapoor et al. formalise the property as the non-dominated set under joint optimisation; HAL's empirical finding that the most expensive configurations are usually off-frontier is what makes the measurement load-bearing ([AI Agents That Matter, arXiv:2407.01502](https://arxiv.org/abs/2407.01502); [HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)).

## When this backfires

The frame breaks down under four conditions — they shape *when* to measure, not whether the measurement is meaningful.

- Low-traffic workflow. The sweep itself burns tokens. Sub-daily workflows usually fall below the threshold where the measurement amortises — the same precondition as [token-cost profiling for always-on workflows](token-cost-profiling-always-on-workflows.md). Below it, "switch to the obvious cheaper model and revisit when the bill arrives" beats a Pareto sweep.
- Noisy or misaligned quality metric. LLM-as-judge scores can swing run-to-run with rubric wording; proxy metrics (e.g., an optimality gap) can look strong while the underlying solution structurally fails ([component-level optimisation evaluation, arXiv:2510.16943](https://arxiv.org/pdf/2510.16943)). A frontier built on a smeared or misaligned quality axis lets dominated configurations appear Pareto-optimal. Pin a deterministic metric (test pass, field accuracy) before plotting; if the quality axis must be a judge, measure its variance first.
- Single-run sampling and optimizer's curse. Pareto plots built on one generation per configuration suffer the bias of taking maxima over noisy samples — accuracy estimates inflate up to 8.7% and cost up to 88% at G ≤ 10 generations ([The Capability Frontier, arXiv:2606.26836](https://arxiv.org/html/2606.26836v1)). Average over multiple runs per cell, or apply explicit bias correction; otherwise the frontier itself is wrong.
- Rapid model churn or non-token cost dominance. Frontier inference cost rising on the order of 18x per year and per-token prices dropping monthly mean a sweep's recommendation ages ([Digital Applied — Q2 2026](https://www.digitalapplied.com/blog/ai-model-performance-vs-price-efficient-frontier-q2)). When wall-clock, infra overhead, or session-runtime fees dominate token spend (e.g., low-volume Computer Use sessions billed on session-hours per [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)), a token-axis plot misranks; use USD per successful task instead of Effective Tokens.

## Example

A team running an always-on PR review agent wants to know whether dropping from Opus 4.7 to Sonnet 4.6 with prompt caching loses quality. They take a fixed set of 50 historical PRs with human-labelled "good review / missed-the-issue" ground truth, then sweep:

| Configuration | Cost / PR (USD) | Quality (review-pass rate on the 50 PRs) | On frontier? |
|---|---|---|---|
| Opus 4.7, effort high | $0.42 | 86% | yes |
| Opus 4.7, effort medium | $0.31 | 84% | no — dominated by Sonnet+cache |
| Sonnet 4.6, no cache | $0.11 | 78% | yes |
| Sonnet 4.6, +5m cache | $0.06 | 78% | yes |
| Sonnet 4.6, +5m cache, batch | $0.03 | 78% | yes (batch only valid for non-PR-blocking runs) |
| Haiku 4.5, +5m cache | $0.015 | 64% | yes |

Numbers above are illustrative of the shape — every cell needs three runs and bias correction before the verdict is load-bearing ([Capability Frontier, arXiv:2606.26836](https://arxiv.org/html/2606.26836v1)).

Two findings the bill alone would have hidden: Opus-medium-effort is dominated — Sonnet with caching matches its quality at one fifth the cost. And the Sonnet-to-Haiku move is *not* a horizontal shift on the frontier; it loses 14 percentage points of pass rate, which the bill alone would have reported as a 75% cost reduction. Either is acceptable depending on what the agent is for — the Pareto plot makes the choice explicit instead of letting a finance dashboard make it implicitly.

## Key Takeaways

- A configuration is the joint product of model x effort x context x cache x batch tier; the Pareto frontier is the only frame that compares them on cost and quality simultaneously.
- USD per successful task is the right cost axis. Effective Tokens (`m × (input + 0.1 × cache_read + 4 × output)`) is the production-ready intermediate; convert to USD for the plot ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/improving-token-efficiency-in-github-agentic-workflows/)).
- One quality axis per plot — test pass rate for code, task pass rate for multi-step agents, field accuracy for extraction; rubric/judge scores carry their own variance and need it measured first.
- Frontiers are sparse in practice — HAL finds the most costly models rarely Pareto-optimal; only a third of tested configurations sit on the frontier on average ([HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)).
- Increased reasoning effort lowered accuracy in 21 of 36 HAL settings — sweep effort too, never assume monotone ([HAL, arXiv:2510.11977](https://arxiv.org/abs/2510.11977)).
- Single-run sweeps inflate accuracy and cost estimates by up to 8.7% / 88% — average over multiple runs per cell or apply explicit bias correction ([Capability Frontier, arXiv:2606.26836](https://arxiv.org/html/2606.26836v1)).

## Related

- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the loop this measurement frame compares configurations within
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — the per-request routing pattern that consumes the map this page builds
- [Per-Plugin Token-Cost Attribution](../observability/plugin-token-cost-attribution.md) — per-component attribution that aggregates up to the cost axis on the plot
- [BYOK Model Token Visibility](../observability/byok-model-token-visibility.md) — in-IDE telemetry that supplies the per-turn input the cost axis needs on self-hosted routes
- [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md) — the guardrail this frame keeps honest: cuts that ignore the quality axis backfire
- [Comparative Judging for Agent Configuration Ranking](../verification/comparative-judging-config-ranking.md) — a more reliable way to rank configs on the noisy quality axis this plot builds, when the quality signal is a judge score
- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](../anti-patterns/cheaper-per-token-costlier-per-task.md) — the anti-pattern this measurement frame catches: a model swap chosen on price and benchmark instead of effective per-task cost
