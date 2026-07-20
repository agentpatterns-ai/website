---
title: "Cheaper-Per-Token Model Upgrades That Cost More Per Task"
term: "Sticker-Price Model Upgrade"
description: "A model upgrade with a lower per-token price and better benchmarks can still cost more per agentic task when it burns far more tokens per run than the model it replaces."
tags:
  - anti-pattern
  - cost-performance
  - testing-verification
  - tool-agnostic
aliases:
  - sticker-price model upgrade
  - per-token price fallacy
last_reviewed: 2026-07-07
maturity: emerging
---

# Cheaper-Per-Token Model Upgrades That Cost More Per Task

> A model upgrade that is cheaper per token and better-benchmarked can still cost more per task when it burns more tokens on agentic work.

The anti-pattern is not upgrading models. It is deciding the upgrade from the pricing page and the leaderboard, then skipping the one measurement that settles it: effective cost per successful task on your own agentic workload.

## The trap

A new model version ships with a lower per-token price and higher benchmark scores. Both signals point the same way, so the team adopts it fleet-wide without measuring. The cost dashboard is expected to drop; instead it climbs.

Microsoft's AX team ran this experiment across 150 agent tasks in 15 scenarios, comparing two Claude Sonnet versions through GitHub Copilot Chat in VS Code. The newer model was [33% cheaper per token in every category — input $3.00 to $2.00, output $15.00 to $10.00, cached input $0.30 to $0.20 per million tokens](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades). It also [consumed about 12x more tokens at the median on architecture tasks and 10x more on code-upgrade tasks, with one architecture run reaching 47x the typical volume](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades). On code upgrades the effective price inverted: [$2.01 per run against $0.55 for the older model, 3.7x more expensive](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades). Quality did not rescue the trade either — the older model scored [90% on the idiomatic-code dimension against 78% for the newer one](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades).

## Why it works

Per-token price is a unit price, not a per-task price: effective cost per task is that unit price times the tokens a task consumes, and a model version can change the second factor by an order of magnitude while dropping the first. Benchmarks score single-turn answer quality, not agentic token efficiency — the tokens and steps a model spends to finish a multi-step task — so a model that benchmarks higher and prices lower can still be more verbose inside an agent loop, where the [roughly 12x rise in tokens per task](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades) swamps a 33% price cut. This differs from a tokenizer swap, where a fixed per-prompt count change is the mechanism ([Tokenizer Swap Tax](../../token-engineering/tokenizer-swap-tax.md)); here the driver is behavioral verbosity on multi-step work.

The remedy is measurement: denominate cost in USD per successful task on your own scenarios, plot it against a quality metric, and let that number decide — the [cost-quality Pareto frame](../../token-engineering/cost-quality-pareto-measurement.md) is the standing form of the comparison.

## When this backfires

Treating every upgrade as suspect is its own waste. The sticker-price heuristic is fine, and the measurement is not worth its cost, when:

- The workload is single-turn and non-agentic. The token-inflation mechanism needs a multi-step loop; a one-shot completion tracks the per-token price closely.
- The workload is low-volume or one-off. The eval harness can cost more than any spend delta it surfaces, the same threshold as [token-cost profiling for always-on workflows](../../token-engineering/token-cost-profiling-always-on-workflows.md).
- There is no representative workload yet. On a greenfield system, the leaderboard and price are the only signals until real traffic exists.
- Non-token costs dominate. When latency, session-hour fees, or infra overhead outweigh token spend, a per-task token comparison misranks.

## Example

Before — upgrade judged on per-token price and benchmark (the anti-pattern):

```python
# Sonnet 5 is 33% cheaper per token and scores higher on benchmarks.
per_token_price_drop = 0.33   # cheaper unit price + better leaderboard
decision = "adopt fleet-wide"  # never measured on the real workload
```

After — upgrade judged on effective cost per successful task:

```python
# Measured on the team's own code-upgrade scenarios:
old_cost_per_run = 0.55   # Sonnet 4.6
new_cost_per_run = 2.01   # Sonnet 5 — ~12x more tokens at the median
# 3.7x more expensive per task despite the 33% cheaper token price
decision = "keep the older model for this workload"
```

The numbers are the measured Microsoft AX figures; the point is that only the second block could have caught the inversion ([Microsoft AX](https://developer.microsoft.com/blog/not-all-model-upgrades-are-upgrades)).

## Key Takeaways

- A lower per-token price and a higher benchmark score are not evidence of lower effective cost — measure USD per successful task on your own agentic workload before switching.
- The mechanism is behavioral verbosity: a newer model can burn an order of magnitude more tokens per multi-step task, swamping a unit-price cut, because benchmarks do not score agentic token efficiency.
- Skip the measurement only for single-turn, low-volume, or greenfield work where the per-token price still tracks effective cost.

## Related

- [Cost-Driven Model Routing Without Quality Monitoring](cost-routing-without-quality-monitoring.md) — the sibling failure of trusting a green cost dashboard while quality silently regresses
- [Perceived Model Degradation](perceived-model-degradation.md) — the vibes-versus-evals failure on the other side of a model change
- [Cost-Quality Pareto Measurement for Agent Configurations](../../token-engineering/cost-quality-pareto-measurement.md) — the standing measurement frame that surfaces this inversion
- [Tokenizer Swap Tax](../../token-engineering/tokenizer-swap-tax.md) — the distinct token-count mechanism this page must not be conflated with
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — routing by task complexity once the per-task numbers are known
- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — the same unit-price-versus-billed-cost gap, on a bolt-on context-reduction layer instead of a model swap
