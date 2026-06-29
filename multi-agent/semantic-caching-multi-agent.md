---
title: "Semantic Caching for Multi-Agent Code Systems"
term: "Semantic Caching"
description: "Semantic caching with LLM-based equivalence detection achieves 67% cache hit rates and reduces token consumption by 40–60% with intent-driven filtering."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - multi-agent
last_reviewed: 2026-06-13
maturity: established
---

# Semantic Caching for Multi-Agent Code Systems

> Semantic caching with LLM-based equivalence detection achieves 67% cache hit rates in production and reduces token consumption by 40–60% when combined with intent-driven context filtering.

## The cost problem

Multi-agent systems multiply token costs. Each request can trigger several LLM calls across orchestrators, sub-agents, and reviewers. Exact-match caching helps little, because users rarely phrase the same query the same way. Semantic caching closes the gap: it detects equivalence rather than requiring exact repetition.

MeanCache (2025) finds that repeated queries make up about 31% of production LLM queries. That is the practical ceiling for semantic cache hit rates. ([arXiv:2403.02694](https://arxiv.org/abs/2403.02694))

## Semantic caching

Semantic caching replaces exact string matching with embedding-based similarity. Two queries count as equivalent when their embeddings pass a similarity threshold, whatever the surface phrasing.

One production deployment handling more than 10,000 natural-language-to-code queries reaches a 67% cache hit rate this way. ([arXiv:2601.11687](https://arxiv.org/abs/2601.11687))

### Dual-threshold mechanism

A single similarity threshold is not enough. Very close queries can be served directly, while weaker matches still gain from scaffolded reuse. A dual-threshold mechanism handles both:

| Similarity range | Action |
|-----------------|--------|
| `similarity >= upper_threshold` | Serve cached result directly — exact cache hit |
| `lower_threshold <= similarity < upper_threshold` | Reference-guided generation: scaffold response from cached result |
| `similarity < lower_threshold` | Full generation — no usable cache entry |

The middle tier draws value from partial matches that single-threshold systems throw away. ([arXiv:2601.11687](https://arxiv.org/abs/2601.11687))

### Open-source implementation

GPTCache is a production-ready open-source implementation. It supports pluggable embedding backends (ONNX, OpenAI, HuggingFace), vector stores (FAISS, Milvus), and LLM adapters. ([github.com/zilliztech/GPTCache](https://github.com/zilliztech/GPTCache))

## Intent-driven context filtering

Semantic caching cuts cost for repeat queries. Intent-driven filtering cuts cost for every query, whether it hits the cache or misses.

Classify the intent of the incoming query, then include only the schemas, tools, or documents that match it. A query about inventory analytics gets only inventory schemas; payment schemas are left out. This cuts tokens by 40–60% with no loss of accuracy. ([arXiv:2601.11687](https://arxiv.org/abs/2601.11687))

Anthropic's just-in-time [context engineering](../context-engineering/context-engineering.md) pattern applies the same idea in the architecture: agents keep lightweight references to available context and load only what they need at runtime. ([Anthropic: Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))

## Combining both mechanisms

The two techniques work independently of each other:

```mermaid
graph TD
    A[Incoming query] --> B[Intent classifier]
    B --> C[Filter context to relevant schemas/tools]
    C --> D[Semantic cache lookup]
    D -->|Hit ≥ upper threshold| E[Return cached result]
    D -->|Partial hit| F[Reference-guided generation with filtered context]
    D -->|Miss| G[Full generation with filtered context]
```

- Semantic caching serves or scaffolds responses from cached results on repeat queries.
- Intent-driven filtering shrinks the context window on every query.
- Used together, the savings stack: cached queries also pay a lower token cost on lookup.

## Distinction from provider prompt caching

Semantic caching and provider-level prompt caching complement each other rather than compete:

| | Semantic caching | Provider prompt caching |
|--|-----------------|------------------------|
| What is cached | Full query results | KV states of static prompt prefixes |
| Savings | Entire LLM call | Recomputation of unchanged prefix tokens |
| Hit condition | Semantic similarity | Exact byte-level prefix match |
| Implementation | Application layer | API parameter (`cache_control`) |

Anthropic's prompt caching cuts cost by 90% on cache hits for the static prefix (system prompt, tool definitions), at a 1,024–4,096 token minimum. ([Anthropic prompt caching docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)) Both can run at once: prompt caching cuts the per-call token cost, and semantic caching removes the call entirely on high-similarity hits.

## Applicability

The return is highest in systems with repetitive query patterns: analytics agents, code-generation pipelines, and customer support bots. Query mixes that vary widely see hit rates closer to the 31% baseline. ([arXiv:2403.02694](https://arxiv.org/abs/2403.02694))

## When this backfires

Every request pays for an embedding computation and a vector-store lookup before the cache decision. On low-repetition workloads this overhead raises mean latency without matching savings. A cache miss can cost more than 2× the latency of a direct LLM call. ([Catchpoint, 2025](https://www.catchpoint.com/blog/semantic-caching-what-we-measured-why-it-matters))

The pattern underperforms in three conditions:

1. Threshold instability: one similarity threshold across diverse query types produces either false positives (wrong cached responses served) or false negatives (valid matches missed). Mixed query types need per-intent thresholds.
2. Embedding drift on model updates: cached [embeddings](../context-engineering/retrieval-augmented-agent-workflows.md) are tied to a specific embedding model. When you replace that model, existing entries no longer match reliably, so you need a full cache flush and a warm-up period.
3. Cache invalidation: results that are correct when cached can go stale. A product inventory answer from Tuesday may be wrong by Thursday. Prompt caching caches computation, but semantic caches cache answers, so any domain where the ground truth changes needs explicit invalidation.

## Example

The following code uses GPTCache with a FAISS vector store and a dual-threshold configuration. It shows both the direct cache hit and the reference-guided generation tier for partial matches.

```python
from gptcache import cache
from gptcache.adapter import openai
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

# Configure dual-threshold semantic cache
onnx = Onnx()
data_manager = get_data_manager(
    CacheBase("sqlite"),
    VectorBase("faiss", dimension=onnx.dimension),
)

cache.init(
    embedding_func=onnx.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
    # upper_threshold: serve cached result directly
    # lower_threshold: reference-guided generation
    similarity_threshold=0.85,
)
cache.set_openai_key()

# First call — populates cache
response1 = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "List the top 3 inventory SKUs by sales volume"}],
)

# Semantically equivalent query — hits cache directly (no LLM call)
response2 = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What are the three best-selling inventory items?"}],
)
```

To add intent-driven context filtering before the cache lookup, classify the query and restrict the schema passed to the prompt:

```python
SCHEMA_MAP = {
    "inventory": ["inventory_items", "stock_levels", "reorder_points"],
    "payments":  ["invoices", "payment_methods", "transactions"],
}

def filter_context(query: str, all_schemas: list[str]) -> list[str]:
    intent = classify_intent(query)  # lightweight classifier, not an LLM call
    return SCHEMA_MAP.get(intent, all_schemas)

# Only inventory schemas are passed — payment tables excluded from context
relevant_schemas = filter_context(
    "List the top 3 inventory SKUs by sales volume",
    all_schemas=list({s for schemas in SCHEMA_MAP.values() for s in schemas}),
)
```

Combining both: the cache lookup uses filtered context as part of the prompt, so cached results also benefit from the reduced token footprint.

## Key Takeaways

- Semantic caching uses embedding-based equivalence detection — not exact match — achieving 67% hit rates on natural language inputs in production.
- A dual-threshold mechanism handles both exact hits (serve directly) and partial matches (reference-guided generation).
- Intent-driven context filtering reduces per-request token cost by 40–60% regardless of cache state.
- Semantic caching and provider prompt caching are orthogonal and can be used together.
- Highest return in high-repetition systems (analytics, code templates, support bots); ~31% of LLM queries are repeated queries in general production.

## Related

- [Prompt Caching as Architectural Discipline](../context-engineering/prompt-caching-architectural-discipline.md)
- [Static Content First: Maximizing Prompt Cache Hits](../context-engineering/static-content-first-caching.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
- [LLM Map-Reduce Pattern for Parallel Input Processing](llm-map-reduce.md)
