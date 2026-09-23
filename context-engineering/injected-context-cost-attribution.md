---
title: "Injected-Context Cost Attribution in Agent Workflows"
term: "Injected-Context Cost Attribution"
description: "Tokenize each node's prompt twice, with and without retrieved memory, to split billed input tokens into what the node carries and what it was handed."
aliases:
  - memory injection cost
  - two-pass token attribution
  - Total Cost of Agency
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-22
maturity: emerging
---

# Injected-Context Cost Attribution in Agent Workflows

> Tokenize each node's prompt twice, with and without retrieved memory, and the difference is the injected cost your tracer reports as one number.

Injected-context cost attribution measures how many of a node's billed input tokens came from memory rather than from the node's own prompt. Assemble the prompt twice, once from the base components alone and once with retrieved context included, tokenize both with the provider's own tokenizer, and subtract ([Singh et al., arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)). The measurement is cheap, and it reports something worth acting on under three conditions.

## Check these conditions first

- Your workflows run three nodes deep or more. A source node injects nothing by the structure of the graph: across 1,112 observations of the first node class, the recorded injected-token count was exactly zero in every case. Injection's share of billed cost climbed from 8.4 percent at depth two to 27.6 percent at depth six ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)).
- Model routing is already settled. The same study reports that "total workflow cost is dominated by model tier assignment". Seven of its eight ablation conditions span $0.00740 to $0.00744 per task, a band the authors decline to rank; the eighth costs $0.00998 because its tier assigner escalates nodes ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)). Measure memory after routing, not before.
- Your prompts are assembled explicitly before dispatch. The two passes run in "a decorator around the prompt-assembly step", so the method reaches "any framework that assembles the prompt explicitly before dispatch and any provider exposing a tokenizer" ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)), and nothing else.

## The two passes

```text
inject(v) = count(base_prompt(v) + retrieved_memory(v)) - count(base_prompt(v))
```

Both calls are non-billable token counts that run no inference. They add roughly ten milliseconds per node against inference latencies of eighty to three thousand milliseconds, and the first pass returns base-prompt volume as a by-product ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)). That by-product is the denominator you report the injected share against.

## Why it works

A node writes its output back to the memory tier, where it becomes part of the next node's injection. Injected volume accumulates along the topological order while per-node output length does not, so the share of the bill climbs with depth even when a capacity-bounded retrieval window holds the absolute count to a straight line. A linear fit over depths two through six gives R² = 0.9974 and a slope of 150 tokens per level ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)).

The subtraction is exact because both passes run one tokenizer over one assembly point and differ only in whether memory is present, so subword-boundary error cancels. Word and character proxies have no such property, and the authors call them "systematically wrong by a variable margin" on agent output made of identifiers and structured text rather than prose.

## What the number points at

Retrieval window capacity is the lever the measurement exposes. Cutting the warm window from 32 entries to 2 at fixed tier lowered injected tokens per task from 1,074 to 766, a 28.7 percent reduction ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)).

Read that in tokens, not dollars. Cost per task fell 6.7 percent, of which only 4.1 percentage points is attributable to the token cut; a shorter prompt can also shorten the output, and the authors did not instrument that. Accuracy moved from 0.600 to 0.570, which they read as stochastic variation. Two settings establish that the lever acts and in which direction. They say nothing about where the trade turns bad.

## When this backfires

- Shallow graphs. Below three nodes deep you instrument a quantity that the graph structure already holds near zero ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)), and the fix you would reach for next, a smaller retrieval window, has almost nothing to evict.
- Percentages carried to another provider. The injected share looked nearly tier-independent only because one price list prices input and output in the same ratio at both tiers, "a property of one price list, not a law". Token counts transfer; share-of-cost figures must be recomputed.
- A bill already dominated by a cached prefix. Prompt caching cut agentic API costs 41 to 80 percent across three providers on DeepResearch Bench ([Lumer et al., arXiv:2601.06007v2](https://arxiv.org/abs/2601.06007v2)), but by caching the large static system prompt: "Additional caching of conversation history and tool calls provides marginal incremental benefit for cost." Caching shrinks the base-prompt term rather than the injected one, so an injected share computed against an uncached bill overstates the dollar headroom left.
- Magnitudes read as universal. Every figure comes from 200 enterprise workflow tasks over synthetic data, one provider, one framework, uncached, graded by a keyword recall the authors treat "as a guard rather than as a result" ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)). The shape transfers. The numbers are local.

## Example

The same benchmark, decomposed two ways. The denominator decides how large the line looks.

| Denominator | Injected share | Basis |
|---|---|---|
| Variable cost an optimizer can move (inference plus injection) | 13.6% | Measured directly |
| Full billed cost (base prompt plus inference plus injection) | 11.8% | Derived from a profiler mean, "accurate to roughly a point" |

Quote the first when arguing about what to tune, the second when arguing about an invoice. The base prompt was the larger input line here, at 1,233 tokens against 1,073 injected ([arXiv:2609.23790v1](https://arxiv.org/abs/2609.23790v1)).

## Key Takeaways

- Split each node's input tokens into base prompt and injected memory with two non-billable tokenizer passes, and report both from the same instrumentation point.
- Expect the injected share to grow with graph depth rather than with the work the graph performs, because each node's output becomes the next node's injection.
- Settle model routing before you measure memory. Reassigning tiers moved per-task cost by more than a third where the memory transforms moved it by under one percent.
- Judge a retrieval-window change on token counts at fixed tier. A dollar change spanning a tier reassignment mixes a price move into a volume move.
- Recompute every share-of-cost figure on your own price list, and treat uncached magnitudes as an upper bound if you cache a large static prefix.

## Related

- [Measuring Reacquisition Cost Under Context Compaction](reacquisition-cost-measurement.md) — the other half of the memory bill, counted in extra tool calls rather than injected tokens.
- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md) — the mitigation that shrinks the base-prompt term this attribution separates out.
- [Context-Usage Attribution](../observability/context-usage-attribution.md) — the same split taken by configuration source inside one agent's window.
- [Token-Cost Profiling for Always-On Agentic Workflows](../token-engineering/token-cost-profiling-always-on-workflows.md) — the surrounding instrument-attribute-fix-verify loop this measurement plugs into.
- [Recursive Sub-Agent Delegation: Depth Limits](../patterns/multi-agent/recursive-sub-agent-delegation-depth.md) — the design decision that sets the depth this cost scales with.
