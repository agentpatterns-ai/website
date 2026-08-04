---
title: "LLM-Driven Logical Retrieval: Boolean Queries over an Inverted Index"
term: "LLM-Driven Logical Retrieval"
description: "When the agent LLM is frontier-capable and the corpus has heavy lexical overlap, letting the LLM emit Boolean logical queries against an inverted index matches an agentic hybrid baseline at ~41x lower indexing cost and lower hallucination — but it underperforms hybrid on medium-scale multi-hop benchmarks and collapses under weaker generators."
aliases:
  - LogicalRAG
  - logical retrieval
  - LLM-authored Boolean retrieval
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
  - rag
last_reviewed: 2026-06-13
maturity: emerging
---

# LLM-Driven Logical Retrieval: Boolean Queries over an Inverted Index

> A frontier LLM emits AND/OR/NOT logical queries against an inverted index — matching hybrid retrieval at scale and 41× lower indexing cost.

## When this pattern applies

The pattern only holds under all four conditions:

- Frontier-capable agent LLM, able to plan multi-hop questions and author well-formed Boolean expressions. Weaker generators collapse — Search-R1 paired with BM25 reaches 3.86% on BrowseComp-Plus against the same retriever a frontier agent uses to reach 83.1% ([Chen et al., 2025](https://arxiv.org/abs/2508.06600); [Hsu, Yang, Lin, 2026](https://arxiv.org/abs/2605.10848)).
- Lexical-overlap-rich corpus — multi-hop QA over Wikipedia-style text, code, docs, log lines, where queries and target documents share surface forms. It weakens when one concept has many surface forms with no shared tokens.
- Construction cost matters — the index is rebuilt often, or indexing budget is constrained. A static, one-time index amortizes hybrid's build cost to zero, which erases the 41× indexing-cost advantage reported below.
- Hallucination on unanswerable queries is tracked — the Boolean "no match" gives a sharper unanswerable signal than a low cosine score.

Outside these conditions, an agentic hybrid baseline keeps a small accuracy edge and is the more conservative default.

## The architecture

LogicalRAG ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)) hands retrieval intent to the LLM and shrinks the backend to a faithful executor of that intent:

```mermaid
graph LR
    Q[User Question] --> A[Agent LLM]
    A -->|Boolean query| L[Logical Layer<br/>AND / OR / NOT<br/>title:entity<br/>quoted phrases]
    L --> I[Inverted Index]
    I -->|matched set| B[BM25 Rank]
    B -->|top-k docs| A
    A -->|next query or answer| O[Answer or Refine]
```

Retrieval runs in two phases. Boolean logic picks the eligible document set, then BM25 ranks within it. The interface exposes `AND`, `OR`, `NOT`, quoted phrases for exact matching, and field-targeting like `title:entity_name` ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)). The agent then iterates: it reads intermediate results, refines the query, and re-issues. The backend executes only what the LLM authors, with no notion of semantic similarity.

## Reported results

| Metric | LogicalRAG | Agentic Hybrid | Source |
|--------|------------|----------------|--------|
| Medium-scale accuracy (HotpotQA / 2WikiMultiHopQA / MuSiQue avg.) | 0.784 | 0.807 | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |
| KILT Wikipedia accuracy | 0.717 | 0.716 | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |
| KILT throughput (16 concurrent) | 152.5 QPS | 66.6 QPS | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |
| KILT mean latency | 74.9 ms | 230.5 ms | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |
| Index construction time | 1.27 h | 52.02 h | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |
| Hallucination rate (answer-unavailable) | 0.083 | 0.128 | [Zeng et al., 2026](https://arxiv.org/abs/2605.27123) |

The headline "matches hybrid" holds at KILT scale and on cost. On medium-scale multi-hop QA the pattern trails hybrid by 2.3 accuracy points. The trade is honest only when index-rebuild cost and unanswerable-query hallucination matter as much as raw accuracy.

## Why it works

The pattern moves retrieval precision from the index to the query author. Hybrid retrieval pays for precision twice — at indexing time (dense embeddings, HNSW graphs, sometimes graph construction) and at query time (vector similarity fused with BM25). LogicalRAG removes both costs. The frontier LLM that already plans multi-hop questions breaks them into Boolean predicates over fielded terms, and the inverted index looks up rather than guesses ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)).

Hallucination reduction follows the same mechanism. A Boolean empty set is a sharp not-found signal. A low cosine score is ambiguous — "no relevant document" versus "relevant document was paraphrased."

This fits a broader retrieval-side-dominance trend: retriever choice exerts more influence than generator choice for SE-task RAG with high identifier-query overlap ([Ke et al., 2026](https://arxiv.org/abs/2605.14503)), and tuned BM25 plus a frontier agent matches dense retrieval on deep-research benchmarks ([Hsu, Yang, Lin, 2026](https://arxiv.org/abs/2605.10848)).

## When this backfires

- Sub-frontier generator — weaker LLMs cannot plan Boolean decompositions. The same BM25 index that supports 83.1% under a frontier agent supports 3.86% under Search-R1 on BrowseComp-Plus ([Hsu, Yang, Lin, 2026](https://arxiv.org/abs/2605.10848); [Chen et al., 2025](https://arxiv.org/abs/2508.06600)). The pattern is a precision-cost migration, not a free optimization.
- Semantic-gap queries — natural-language paraphrases against identifier-heavy documents ("deduplicate while preserving order" → `unique_ordered`) have near-zero lexical overlap. Logical operators cannot bridge that without a thesaurus or expansion step.
- Synonym-heavy corpora — medical, legal, multilingual, and consumer-product corpora where one concept has many surface forms. BM25's insensitivity to synonymy is well documented, so agents author speculative `OR` chains to compensate.
- Static-index, query-rate-dominated workloads — when the index is built once and serves billions of queries, the 41× build-time win amortizes to zero and the medium-scale 2.3-point gap dominates.
- Latency-sensitive workloads — every logical query is an inference call, so dense retrieval with a single round-trip can beat multi-turn Boolean refinement on tail latency.

## Example

A team running an agentic RAG system over 10M technical-documentation pages, frontier LLM in the loop, index rebuilt nightly to track product churn.

Before — agentic hybrid with dense plus BM25 fusion:

```yaml
retrieval:
  type: agentic-hybrid
  dense:
    embedder: text-embedding-3-large
    vector_db: managed-hnsw
  sparse:
    backend: bm25
  fusion: reciprocal-rank
  rerank: bge-reranker-v2-m3
indexing:
  nightly_build_hours: 38
  monthly_infra_usd: 18000
agent:
  query_pattern: free-text
```

After — LLM-authored Boolean queries over inverted index:

```yaml
retrieval:
  type: logical
  backend: inverted-index
  operators: [AND, OR, NOT, "quoted phrases", "field:value"]
  rank: bm25
indexing:
  nightly_build_hours: 0.9
  monthly_infra_usd: 1100
agent:
  query_pattern: boolean-logical
  examples:
    - 'title:"rate limit" AND (429 OR "too many requests") NOT deprecated'
    - '"event_loop" AND asyncio NOT "twisted"'
```

The "after" configuration trades about 2 accuracy points (only at medium scale; it matches at large scale) for a 42× reduction in nightly build time and a roughly 3× latency win at the query path. You keep frontier LLM authoring; the migration is the retrieval interface, not the agent. Re-evaluate hallucination rate on a held-out unanswerable-query set before committing — the 0.083 versus 0.128 hallucination delta is the second load-bearing benefit beyond raw cost ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)).

## Key Takeaways

- LogicalRAG moves retrieval precision from the index to the query author: a frontier LLM emits AND/OR/NOT and field-scoped queries against a plain inverted index ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)).
- The pattern matches an agentic hybrid baseline at KILT-scale Wikipedia (0.717 vs. 0.716) and trails it on medium-scale multi-hop QA (0.784 vs. 0.807); the win is cost (41× faster indexing) and hallucination rate (0.083 vs. 0.128), not raw accuracy ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)).
- Evaluate this pattern by checking hallucination rate on answer-unavailable queries specifically — that is where its gap over hybrid concentrates ([Zeng et al., 2026](https://arxiv.org/abs/2605.27123)).
- Benchmark your specific agent model on Boolean decomposition before switching — Search-R1 + BM25 collapses to 3.86% where a frontier agent reaches 83.1% on the same index ([Hsu, Yang, Lin, 2026](https://arxiv.org/abs/2605.10848); [Chen et al., 2025](https://arxiv.org/abs/2508.06600)).
- When corpora have high lexical overlap, weight retriever choice over generator upgrades — the broader SE-task RAG evidence shows retriever choice dominates outcomes there ([Ke et al., 2026](https://arxiv.org/abs/2605.14503)).

## Related

- [Component-Wise RAG Prioritization for Software Engineering Tasks](rag-component-prioritization-software-engineering.md) — retriever-dominance mechanism with BM25 as the SE-task default
- [Lexical-First Retrieval for Agentic Search](../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — independent evidence that BM25 + frontier agent matches dense retrieval in deep-research loops
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — alternative structured-retrieval interface that pushes precision onto a typed schema rather than logical operators
- [Structured Domain Retrieval](structured-domain-retrieval.md) — knowledge-graph + case-based retrieval that captures hierarchical relationships flat vector search misses
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the JIT-context pattern this retrieval interface plugs into
- [Codebase-Derived Pattern Libraries as Agent Context](codebase-pattern-library-context.md) — tunes *what* is in the retrieval corpus (vetted in-house code) rather than *how* queries are authored
