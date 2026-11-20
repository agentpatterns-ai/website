---
title: "Pricing a Context Change Across the Cache-Read Range"
term: "Cache-Price Range Evaluation"
description: "Rolling observation masking raised cost 116% at a tenth-price cache and cut it 19% with no discount, on one model and scaffold. Price each context change at both ends."
tags:
  - token-engineering
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - cache-aware context cost evaluation
  - cached input price crossover
  - prefix cache break-even for context removal
last_reviewed: 2026-11-19
maturity: emerging
---

# Pricing a Context Change Across the Cache-Read Range

> Adding or removing context can raise or cut an agent's bill depending on the cache-read price, so price each change at both ends.

Rolling observation masking (keep the latest ten observations, mask the rest) raised cost by 116% when a cached input token costs a tenth of an uncached one (c=0.1) and cut it by 19% with no discount (c=1). That is Qwen3.6-27B in mini-SWE-agent on 201 fresh SWE-bench Verified tasks, with output priced at 4 times uncached input (p=4) ([Yang et al., 2026](https://arxiv.org/abs/2611.22238v1), §5, Table 1).

Limits:

- All models are open models served locally, five of seven from the Qwen family, with thinking disabled where supported. The paper says its results "do not establish how frontier API agents or longer reasoning budgets would behave" (Limitations).
- Prices are applied to recorded token streams. The accounting does not reproduce expiry, write charges or eviction (Limitations).

## The break-even rule

Removing B tokens saves c·B on each of R remaining requests. The S tokens after the change point lose their cache hit once, at an extra (1−c) each. Removal pays when R·c·B > (1−c)·S (Equation 2). The paper notes the rule holds future actions fixed and is "not a guarantee about an agent that reacts to the edit."

## Adding context

An evidence package (about 14K tokens of retrieved code, replaced by a location index at the first edit or turn 8) cut read and search commands by 32% on 80 Verified tasks (Qwen3.6-27B). Cost rose 36% at c=0.1 and 25% at c=1 (Table 1). Across the ten rows of Table 4, the c=0.1 rise runs from +25% to +95%.

Resolution on those 80 tasks moved +3.8 points under the official harness. On 217 fresh tasks it was equivalent to no change within ±5 points (§4). Replacing the package with its index, computed by Equation 2 on logged runs, pays in 91% to 97% of runs at c=0.1 and saves a quarter of the cost.

## Removing context

| Method, setting | Cost at c=0.1 | Cost at c=1 |
|---|---|---|
| Rolling masking, mini-SWE-agent, 201 tasks, Qwen3.6-27B | +116% | −19% |
| Rolling masking, SWE-agent, 115 tasks, Qwen3.6-27B | +101% | −29% |
| Break-even masking, 201 tasks, two Qwen models | +2.8%, +1.8% | −26%, −21% |

Rolling masking crosses over near c=0.5 on the 201 tasks. The break-even policy's upper bounds (+8.3%, +11.4%) miss its 5% non-inferiority margin (§5).

A fixed-action replay splits the premium. At c=0.1 in mini-SWE-agent, +90 of the +116% is direct cache cost, and the rest is the agent's changed behavior, mostly re-reading masked content. In SWE-agent about half is direct (+52 of +101%).

The paper's summary claim has a scope: "a method cheaper at the four corners of the current API range (c∈{0.025,0.1}, p∈{4,6}) is cheaper throughout it; none of the 33 combinations we ran was." It does not say removal never pays at c=0.1. The introduction adds that digest masking saved 17% at c=0.1 for GLM-4.7-Flash.

## Measurement trap

Conditions of one task that run side by side on one server share cached prefixes. Counting those hits hid most of the evidence package's premium on Verified: it measured +8%, and +36% once they were removed. Run alone, each condition's own counts give +29% (§2).

## Where removal paid

- GLM-4.7-Flash averages 171 steps (115 tasks). Break-even masking cost 12.7% less than no masking at c=0.1, and rolling masking still cost 38% more. Context-limit failures fell from 21 runs to 4 to 6 (§5, App. I).
- A billed study found the opposite sign. On Gemini 2.5 Flash through Vertex, where cache hits are "up to 10× cheaper", rolling masking (ten observations, 250-turn limit) cut instance cost from $0.41 to $0.18 (−56.1%, non-thinking) on SWE-bench Verified ([Lindenbauer et al., 2025](https://arxiv.org/abs/2508.21433v3), Table 1).

## What to do

1. Replay logged runs with actions held fixed. Price uncached input, cached input and output separately, at your provider's cache-read multiplier and at c=1.
2. Confirm with a live A/B on separate servers, counting only each run's own cache hits.
3. Ship the change only if it wins at your multiplier.

## When this backfires

- You serve without prefix caching or pay c=1. Rolling masking saved 19% and 25% for two Qwen models there (§5).
- Runs are long, so R is large. GLM above is the case.
- Runs hit the context limit. Removal then fixes correctness, not cost.

## Key Takeaways

- A cost result without its cache-read multiplier is incomplete. Report c and p with every figure.
- The 116% belongs to per-turn rolling masking. Break-even masking stayed near no masking at c=0.1 (+2.8%, +1.8%).
- Check for shared caches before you trust a cost ablation.

## Related

- [Observation Masking](../context-engineering/observation-masking.md)
- [Prompt Caching: Architectural Discipline for Agents](../context-engineering/prompt-caching-architectural-discipline.md)
- [Batched Context Eviction](../context-engineering/batched-context-eviction.md)
- [Executed Prefill Accounting](../context-engineering/executed-prefill-accounting.md)
- [Token Reduction Is Not Cost Reduction](../patterns/anti-patterns/token-reduction-not-cost-reduction.md)
- [The Four Terms That Decide What an Agent Task Costs](four-term-agent-cost-model.md)
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
