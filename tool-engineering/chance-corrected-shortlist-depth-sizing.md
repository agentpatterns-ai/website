---
title: "Chance-Corrected Shortlist Depth Sizing for Tool Retrieval (Bits-over-Random)"
term: "Chance-Corrected Shortlist Depth Sizing"
description: "Bits-over-Random measures whether your tool-retrieval shortlist depth beats random selection at that depth — the missing chance-corrected metric between fixed-K heuristics and adaptive per-query depth."
tags:
  - tool-engineering
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - Bits-over-Random
  - BoR shortlist sizing
  - chance-corrected tool retrieval
last_reviewed: 2026-06-10
maturity: adopted
---

# Chance-Corrected Shortlist Depth Sizing

> Bits-over-Random measures whether a tool-retrieval shortlist of depth K beats random selection at that depth — the chance-corrected sizing metric.

## When this applies

Adaptive shortlist depth is the right control problem only when four conditions hold. If any fails, a small fixed-K (Anthropic suggests "three to five most-used tools always loaded" — [Anthropic, Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)) is usually simpler and equal-or-better.

| Condition | Why it matters |
|---|---|
| Strong-enough retrieval scorer | Weak scorer (MetaTool BM25, found@1=33%) expands the BoR policy to K ≈ 80 from a ~100-tool registry — "adaptive" degrades into "show everything" ([Repantis et al., 2026 §5](https://arxiv.org/html/2605.24660v2)) |
| Heterogeneous query difficulty | Wins come from skipping easy queries cheaply and going deeper on hard ones. Uniformly hard or uniformly easy traffic has no slack. |
| Control of the depth decision | The policy needs per-step similarity scores. Opaque hosted tool-search endpoints hide that surface. |
| Tool presence is the failure mode | BoR measures whether the gold tool appears, not whether the LLM calls it with right arguments. Argument-construction errors are unaffected (§5). |

This page covers retrieval-shortlist sizing at inference time. It sits next to which tools exist at all ([Tool Minimalism](tool-minimalism.md)) and whether to retrieve any tool ([Tool Necessity Probing](tool-necessity-probing.md)).

## The fixed-K problem

Most tool-retrieval and MCP tool-search systems hard-code one shortlist depth (`top_k=5` is canonical) for every query. Two failure modes meet in the middle:

- Too few tools — the correct tool ranks below K and never appears
- Too many tools — selection accuracy degrades from distractor overload

A fixed K assumes the gold tool's expected rank is independent of query difficulty. It is not — hard queries push the gold tool deeper. On ToolBench's hard queries (gold ranked 6th–20th), fixed-K=5 finds 0% while a BoR-trained adaptive policy recovers 16.7% ([Repantis et al., 2026 §5](https://arxiv.org/html/2605.24660v2)).

The aggregate hides this: on the same run fixed-K=5 wins 64.7% aggregate coverage vs the BoR agent's 61.9% at K=4.4 average. Without a chance-corrected metric, you have no way to tell whether your fixed-K is appropriately sized for your registry and scorer.

## What Bits-over-Random measures

`BoR = log₂(P_obs / P_rand)`

- `P_obs` is the observed retrieval success rate at depth K
- `P_rand` is the probability of success by random selection at the same depth K
- For single-relevant-tool queries from an N-tool registry, the random baseline simplifies to `P_rand = K/N`

Each bit of BoR represents one doubling of selectivity over random chance. `BoR = 0` means the retriever performs at random. `BoR = 3` means it is 8× better than random at that depth. Because `P_rand` rises as K grows, the metric self-prunes excess depth without an engineered penalty — finding the gold tool at depth 50 from a 100-tool registry earns far less BoR than finding it at depth 5 ([Repantis et al., 2026 §3](https://arxiv.org/html/2605.24660v2)).

This property lets BoR run an adaptive depth policy without hand-tuned penalty terms.

## Why it works

Recall@K — the standard retrieval metric — has no intrinsic depth penalty. As K approaches the registry size N, recall trivially saturates toward 1, so the metric cannot tell you whether deeper search is useful work or gaming the metric — the exact motivation for chance-correction in [Repantis et al., 2026 §3](https://arxiv.org/html/2605.24660v2). BoR fixes this by subtracting the random baseline `K/N`, which scales with both K and N. The causal mechanism is the chance correction: as K grows, the entropy reduction from "the tool was in this set" shrinks, so the metric naturally rewards finding the tool at small K and discounts finding it at large K.

An RL policy trained on this reward learns to expand K only when the per-step similarity-score gap suggests deeper search will pay. The paper's agent observes the top score, the gap between top and current, the score spread, current depth k, registry size N, and the BoR ceiling at depth k. It chooses STOP or CONTINUE. At STOP it earns `−log₂(P_rand(k_stop))` bits when the relevant tool is found, with a 0.01-per-step continuation cost ([§4](https://arxiv.org/html/2605.24660v2)). BoR is therefore both a metric and a reward shape that yields a depth-limiting policy by construction.

## Numbers from the paper

| Setting | Fixed-K | BoR agent | Notes |
|---|---|---|---|
| BFCL (370 tools, BM25 scorer) | K=50: 90.8% | K=7.4 avg: 90.3±2.4% | ~7× less depth at matched coverage |
| BFCL Claude Sonnet 4.6 tool-choice validation | K=5: 87.1% | K=2.2: 93.1±0.5% | Adaptive lists improve LLM selection accuracy |
| BFCL Claude Sonnet 4.6, medium-difficulty queries | K=5: 60.9% | 76.8±2.5% | Widening gap as queries get harder |
| ToolBench (3,251 tools) | K=5: 64.7% | K=4.4 avg: 61.9±0.6% | Fixed-K wins aggregate |
| ToolBench hard queries (rank 6–20) | K=5: 0% | 16.7±4.3% | The asymmetric failure mode |
| ToolBench very-hard queries (rank 21+) | K=5: 0% | 0.2% | Retrieval model is the bottleneck |

All numbers from [Repantis et al., 2026 §5](https://arxiv.org/html/2605.24660v2).

The Claude Sonnet 4.6 row is the load-bearing practitioner result: adaptive depth lifts end-to-end tool-choice accuracy by 6 points overall and 16 points on medium-difficulty queries — these are LLM-side wins, not retrieval-only wins.

## When this backfires

- Weak retrieval scorer. The metric is honest about scorer quality, which means a weak scorer turns the adaptive policy into a "show everything" policy. The MetaTool BM25 case expanded to K ≈ 80 with only 1.04 bits of selectivity — at that depth the system is paying the prompt-bloat cost without the targeting benefit ([§5](https://arxiv.org/html/2605.24660v2)).
- Closed/hosted retrieval endpoints. If your tool search runs inside a hosted provider's tool-loading layer with no per-step similarity surface, you cannot run the RL policy. BoR remains useful as an offline diagnostic for your current fixed-K, but the adaptive payoff requires inference-time control.
- Argument-correctness dominates. The work measures whether the gold tool appears in the shortlist. If your long-tail failures are bad arguments to the right tool, depth sizing has near-zero marginal impact — invest in schema and description quality ([Tool Description Quality](tool-description-quality.md)) instead.
- Very-hard queries (gold rank 21+). Recovery drops to 0.2% — at that retrieval depth the bottleneck is the retrieval model itself, not shortlist length. No amount of depth tuning saves you.
- Model-rotation overhead. Like other learned classifiers in the tool-augmented stack, the RL policy needs retraining when the embedding model, scorer, or registry distribution shifts. For teams whose model cadence is faster than their retraining cadence, the fixed-K=5 number is "good enough" and the simpler engineering wins.

In tension with this paper's adaptive-depth recommendation, [ToolChoiceConfusion (arXiv:2606.06284)](https://arxiv.org/abs/2606.06284) finds that across 102 tasks against a 100-tool menu, minimal causal filtering cuts token cost ~90% with no success drop. The two results are reconcilable: ToolChoiceConfusion's gains come from removing causally-irrelevant tools the model would never legitimately use; BoR's gains come from including the right tool when query difficulty pushes its rank deeper. Both can be true on the same stack, but the practitioner ordering is: prune the registry first, then size the shortlist.

## Using BoR without the RL policy

The metric is more broadly applicable than the adaptive depth controller. For most teams the practical use is diagnostic: instrument your current fixed-K retrieval, log `P_obs` at the chosen K, compute `BoR = log₂(P_obs / (K/N))`, and decide whether your fixed-K is appropriately sized.

- If BoR is high (≥3–4 bits) at small K, your fixed-K is reasonable and adaptive policy adds little
- If BoR is low (≤1 bit) at all K, your scorer is the problem — neither fixed nor adaptive depth fixes a weak scorer
- If BoR is high at small K on easy queries but collapses on hard queries, you have the heterogeneous workload that adaptive depth was designed for

This is the same diagnostic posture as [MCP alwaysLoad](mcp-eager-vs-jit-loading.md), which classifies servers by hit rate and selection accuracy: instrument first, then adapt the policy.

## Key Takeaways

- Bits-over-Random measures whether retrieval at depth K beats random at depth K: `BoR = log₂(P_obs / (K/N))` ([Repantis et al., 2026](https://arxiv.org/abs/2605.24660))
- Fixed shortlist depth has an asymmetric failure mode: it wins on easy queries cheaply and loses 100% on hard queries where the gold tool ranks past K
- The chance correction is the load-bearing primitive — Recall@K trivially saturates as K → N and cannot guide depth choice
- Adaptive depth meaningfully helps when scorer is strong, workload is heterogeneous, you control the depth decision, and tool *presence* (not argument-correctness) is the failure mode
- Use BoR as a diagnostic on a fixed-K stack before reaching for an adaptive policy — most teams stop at the diagnostic

## Related

- [Tool Minimalism and High-Level Prompting](tool-minimalism.md)
- [Tool Necessity Probing](tool-necessity-probing.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](mcp-eager-vs-jit-loading.md)
- [Lexical-First Retrieval for Agentic Search](lexical-first-retrieval-for-agentic-search.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
