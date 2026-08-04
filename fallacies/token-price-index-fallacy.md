---
title: "The Token Price Index Fallacy in Agent Cost Planning"
term: "Token Price Index Fallacy"
description: "A blended price-per-token index measures where a market routes its work, not what models cost, so reading one as a vendor price signal misplans agent budgets."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - fallacies
aliases:
  - token price index fallacy
  - blended price per token fallacy
  - price per token is not a price
last_reviewed: 2026-08-03
maturity: emerging
---

# The Token Price Index Fallacy in Agent Cost Planning

> A blended price-per-token index tracks where a market routes its work, so a flat reading tells you nothing about what models cost.

The token price index fallacy is the belief that a published price-per-token figure reports what models charge. Every such index is an average over a basket of models, so its value moves when the basket weights move and not only when prices do. A team that reads a flat or rising index as a statement about vendor pricing ends up planning its budget against a number that mostly describes other companies' routing decisions.

## The belief

Price per token across a large production gateway was flat in June 2026, after rising almost 20% in May ([Vercel, 2026-07-13](https://vercel.com/blog/ai-gateway-production-index-july-2026)). You conclude the long decline in inference prices has stalled, so waiting for the next price cut is finished and routing is the lever that remains. That conclusion is sound. The reasoning behind it is wrong, and the same source says so.

Open-weight models ran 29% of that gateway's tokens in June, up from 11% in April, on under 4% of spend. Vercel is explicit about what that did to the average: "That alone should have pulled the price per token down. But as cheap volume rose in June, so too did closed-weight frontier prices", up about 12% per token, and "They offset each other, so the average price per token was flat" ([Vercel, 2026-07-13](https://vercel.com/blog/ai-gateway-production-index-july-2026)).

A flat print is what two large opposing moves look like once they cancel. A team that held its own mix fixed through June got no such offset, and paid the full 12% rise on whatever share of its tokens sat on frontier models.

## Three indices, three directions

Published token-price indices disagree because each one holds something different constant. The readings below are as published, and they are not all from the same month.

| Index | What it holds constant | Reading, as published |
|---|---|---|
| [Vercel AI Gateway](https://vercel.com/blog/ai-gateway-production-index-july-2026) | Nothing. Realized spend divided by tokens routed, weighted by actual usage | June 2026: flat, after a rise of almost 20% in May |
| [BenchLM frontier sub-index](https://benchlm.ai/token-price-index) | A 3:1 input-to-output blend, median across current flagship models | August 2026: 12 against a March 2023 base of 100, and up 36.4% year on year |
| [BenchLM budget and mid-tier](https://benchlm.ai/token-price-index) | The same rule, applied to small and workhorse models | August 2026: budget up 90.5% year on year while mid-tier fell 35.8% |
| [Epoch AI](https://epoch.ai/data-insights/llm-inference-price-trends) | Capability. The cheapest model clearing a fixed benchmark score | March 2025: falling between 9x and 900x per year, median 50x |

Read the third row against the second. Two tiers of one index, built by one team under one rule, moved in opposite directions over the same 12 months. Measured at fixed capability instead, prices fell fast enough across six benchmarks that Epoch AI flagged its own steepest trends as unlikely to persist ([Epoch AI, 2025-03-12](https://epoch.ai/data-insights/llm-inference-price-trends)).

None of these numbers is wrong. They answer different questions, and at most one of them is the question you have.

## Why it works

A usage-weighted index is total spend divided by total tokens, and both terms move. Silicon Data states the property of its own daily index plainly: it is "weighted by where usage is concentrated", so that "when demand shifts toward premium models, expenditure rises; when capable lower-cost models gain adoption, the market becomes more cost-efficient" ([Silicon Data](https://www.silicondata.com/products/silicon-index/llm-token-expenditure-index)). The published figure is realized cost-to-serve, not any provider's list price. The reader's error is treating a quantity with two degrees of freedom as though it had one.

Fixing the weights relocates the choice rather than escaping it. BenchLM holds the input-to-output ratio at 3:1, then lets constituents "enter at launch and exit when superseded", so its tier medians recompose as the market does ([BenchLM Token Price Index](https://benchlm.ai/token-price-index)). Its frontier tier sits 88% below its March 2023 base and up 36.4% year on year at once, because a basket of today's flagships is not a basket of 2023's.

## When this backfires

Chasing this correction has its own failure conditions.

- Single-model deployments. If you run one model on one tier, your realized rate is that model's list price. There is no mix to decompose, and a blended-rate dashboard reports a number the pricing page already gives you.
- No routing headroom. Regulatory model pinning, reproducibility-gated CI, or a single-vendor contract can put the cheap tier out of reach. Knowing your rate is mix-driven changes nothing you can act on, and waiting for list-price cuts really is the only remaining lever.
- Optimizing the blended rate. Your own blended price per token falls whenever volume moves to cheap models, whatever the rework costs. It is a worse target than spend per completed task and leads directly into [cost-driven routing without quality monitoring](../patterns/anti-patterns/cost-routing-without-quality-monitoring.md).
- Month-to-month reading. The Vercel series went up almost 20% in May and flat in June. Replanning routing against prints that noisy produces thrash rather than savings.

## What to measure instead

Split the one number into two, both computed on your own traffic.

1. Your realized blended rate, as spend divided by tokens. It is an output of your routing, so treat any change as a question about your mix before it is a question about vendors.
2. Your per-tier list prices and your share of volume on each tier, kept apart. A 12% frontier increase stays invisible in a blended rate while cheap volume grows, and it is the line item that moved.

Routing mix is not the only wedge between list price and what you pay. Cache-hit rate moves the same gap on the input side, and the orchestration layer owns it ([harness-controlled token economics](../token-engineering/harness-token-economics.md)). Both belong in the same reconciliation.

## Key Takeaways

- A price-per-token index is a weighted average, so its movement confounds vendor pricing with everyone's routing behavior.
- Published indices disagree on sign in the same window, including two tiers of the same index, because each holds something different constant.
- The index misleads hardest in the case that matters most: while your frontier volume share is climbing, a flat market blend is reporting someone else's substitution as your price stability.
- An index can still be useful once you stop asking it about price. Treat a move in it as news about how the market is routing, and check it against your own mix.

## Related

- [The Model Preference Fallacy](model-preference-fallacy.md) — the adjacent measurement error, where bare-chat tallies get read as a stable model preference and then drive routing
- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](../patterns/anti-patterns/cheaper-per-token-costlier-per-task.md) — the same confusion one level down, at a single model's sticker price rather than a market index
- [Harness-Controlled Token Economics](../token-engineering/harness-token-economics.md) — the other wedge between list price and what you pay, where cache discipline sets the effective input price
- [Cost-Quality Pareto Measurement for Agent Configurations](../token-engineering/cost-quality-pareto-measurement.md) — the frame that stops a mix-driven cost drop from hiding a quality regression
- [Routing Decision Framework](../token-engineering/routing-decision-framework.md) — once you accept your rate is set by routing, this picks which routing pattern fits your dominant signal
