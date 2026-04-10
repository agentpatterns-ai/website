---
title: "Air-Gapped RAG: Retrieval and Re-Ranking"
description: "Dense, sparse, and hybrid retrieval strategies for air-gapped RAG — when each layer earns its latency and compute cost, and how to measure the difference."
tags:
  - training
  - context-engineering
  - tool-agnostic
---

# Air-Gapped RAG: Retrieval and Re-Ranking

> Pure vector similarity fails on exact-token queries; pure BM25 fails on paraphrased ones — hybrid retrieval covers both failure modes, and re-ranking recovers top-k quality when it matters most.

This module covers the retrieval layer of an air-gapped RAG pipeline. You will learn when dense retrieval breaks down, how BM25 compensates, how to fuse both with Reciprocal Rank Fusion (RRF), and when a cross-encoder re-ranker justifies its latency cost. All components run locally — no cloud API calls anywhere in the pipeline. Runnable code wires dense retrieval, sparse retrieval, fusion, and reranking into one [Haystack](https://github.com/deepset-ai/haystack) query pipeline against the Qdrant collection built in [Module 5](local-embeddings-vector-stores.md).

---

## Dense Retrieval: Where It Fails

Dense retrieval embeds queries and documents into fixed-dimensional vectors and retrieves by cosine similarity (or dot product/Euclidean distance). It handles paraphrased queries well because semantically equivalent phrases land near each other in the embedding space.

It breaks on keyword-heavy queries. If a user searches for `CVE-2024-12345`, `ERROR_CODE_0x8007007E`, or a product SKU, the embedding model may return thematically related documents rather than the document that contains the exact token string. The embedding space clusters by meaning, not by character sequence. Technical corpora — logs, code references, compliance documents — are full of these exact-match requirements.

**Distance metrics** — cosine similarity, dot product, and Euclidean distance — differ in what they optimize. Cosine ignores magnitude and compares direction; use it when document length varies widely. Dot product is faster but magnitude-sensitive; use it with normalized vectors. Euclidean is sensitive to high-dimensional sparsity and rarely the best default for text embeddings.

---

## Sparse Retrieval: BM25 Fundamentals

BM25 (Best Match 25) is an inverted-index ranking function that scores documents by term frequency (TF), inverse document frequency (IDF), and a length normalization factor. No embeddings, no GPU — it runs on an inverted index that scales to billions of documents on commodity hardware.

BM25 scores exact token matches precisely and is immune to the semantic gap that breaks dense retrieval. A query for `CVE-2024-12345` will surface every document containing that exact string, ranked by how prominently the term appears.

It fails on paraphrased queries. "Memory leak" and "heap exhaustion" share zero token overlap — BM25 scores them as unrelated. Out-of-vocabulary terms, synonyms, and domain-specific abbreviations that differ from document vocabulary all produce poor recall.

**When sparse beats dense**: exact identifier lookup (CVE IDs, error codes, product names), queries where character sequence is semantically significant, corpora with high terminology consistency.

---

## Hybrid Retrieval: Reciprocal Rank Fusion

Running BM25 and dense retrieval in parallel and fusing the results covers both failure modes. The standard fusion algorithm is Reciprocal Rank Fusion (RRF).

**RRF formula**: for each document d across retrievers r₁...rₙ:

```
score(d) = Σ  1 / (k + rank_r(d))
```

Where `rank_r(d)` is the position of document d in retriever r's ranked list, and `k` is a smoothing constant (default: 60). Documents not returned by a retriever are excluded from that retriever's contribution.

RRF works on rank position, not raw scores, so it handles incompatible score scales cleanly — BM25 produces integer-range scores, cosine similarity produces floats in [−1, 1]. No normalization step needed.

The `k=60` default was established empirically and works well across diverse datasets. A lower k gives disproportionate weight to top-ranked results from a single retriever; a higher k distributes weight more evenly. Adjust k when one retriever consistently dominates on your specific corpus.

**Performance**: on keyword-heavy corpora, hybrid RRF achieves nDCG@10 of 0.89 versus 0.88 for BM25 alone and 0.58 for dense alone, with up to 20.4% recall@1K gain over dense-only baselines ([source](https://medium.com/@robertdennyson/dense-vs-sparse-vs-hybrid-rrf-which-rag-technique-actually-works-1228c0ae3f69)).

**Implementation**: [Qdrant](https://github.com/qdrant/qdrant), [Weaviate](https://github.com/weaviate/weaviate), and [Elasticsearch](https://github.com/elastic/elasticsearch) all support hybrid search (BM25 + vector) natively in self-hosted deployments with no cloud dependency. Qdrant and Weaviate expose RRF fusion directly; Elasticsearch's `rrf` query parameter is documented in the [Elasticsearch REST API reference](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion).

---

## Cross-Encoder Re-Ranking

RRF fuses two independent rank lists — each retriever scores documents without seeing the query-document pair together. A cross-encoder re-ranker scores each (query, document) pair jointly, capturing fine-grained relevance signals the bi-encoder model misses.

**How it works**: take the top-k candidates from the hybrid retriever (typically k=20–50), pass each (query, candidate) pair through the cross-encoder, re-sort by cross-encoder score, return the top-n.

**Cost**: cross-encoder re-ranking adds ~100–200ms latency per query for ~30 candidates [unverified — varies by hardware and batch size]. It cannot run in parallel — it requires the retrieval stage to complete first.

**Models for air-gapped deployment**:

- [`bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) (BAAI) — 0.6B parameters, multilingual, LoRA fine-tuned with flash attention. The series [reference stack](index.md#reference-stack). Runs on CPU for small candidate sets; a GPU is recommended above 50 candidates.
- [`jina-reranker-v2-base-multilingual`](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual) — achieves 81.33% Hit@1 at ~188ms end-to-end, making it the only top-tier model meeting sub-200ms budgets [unverified — benchmark conditions vary].
- [`bge-reranker-large`](https://huggingface.co/BAAI/bge-reranker-large) — adds approximately 2 nDCG@10 points over v2-m3 but doubles inference latency [unverified].

**When re-ranking earns its cost**:
- nDCG@10 measured below your quality threshold without re-ranking
- Queries are nuanced, multi-faceted, or contain implicit criteria
- Initial retrieval scores cluster tightly (hard to distinguish top results by score alone)
- Latency budget allows 100–200ms additional overhead

**When to skip re-ranking**:
- Simple factual queries where position-1 retrieval is consistently correct
- Corpus under ~1,000 well-organized documents
- Strict sub-200ms total latency requirement AND retrieval quality is already acceptable
- Initial retrieval scores are widely spread (top result is already clearly differentiated)

---

## Query Expansion: HyDE

[Hypothetical Document Embeddings (HyDE)](https://arxiv.org/abs/2212.10496) is an optional layer for semantically vague queries. The LLM generates a hypothetical answer to the query — a "fake" document that captures what a real answer would look like — and that hypothetical document is embedded and used for retrieval instead of the bare query.

The hypothetical document is longer and richer than the original query, which helps bridge the semantic gap between short queries and longer documents in the embedding space. HyDE is particularly useful when users phrase queries as questions ("How do I configure…?") rather than as document-matching strings.

**Air-gapped constraint**: HyDE requires a local LLM inference call before retrieval, adding end-to-end latency. Use the same Ollama-served model that [Module 7 (Local LLM Inference)](local-llm-inference.md) sets up for answer synthesis — run it with a small `max_tokens` budget (100–200 tokens is enough for a HyDE stub) so the added latency is bounded.

**When HyDE helps**: short, vague queries; question-form queries; corpora with long, dense documents. When to skip it: exact-token queries (CVE IDs, error codes) where the bare query already matches precisely; strict latency budgets; small corpora.

---

## Measuring Retrieval Quality

Use nDCG@10 (Normalized Discounted Cumulative Gain at 10) to compare retrieval strategies before and after each layer.

nDCG = DCG / IDCG, where:
- **DCG** sums the graded relevance scores of the top-10 results, discounting by log₂ of rank position
- **IDCG** is the DCG of a perfect ranking (best possible ordering)
- Score ranges from 0 (worst) to 1 (perfect)

nDCG rewards putting the most relevant document first and penalizes burying it at rank 7. It supports graded relevance (highly relevant, somewhat relevant, irrelevant) rather than binary.

Build a small labeled evaluation set: 30–50 queries with human-graded relevance judgments for your specific corpus. Measure nDCG@10 at each layer — dense only, hybrid RRF, hybrid + re-rank — to confirm each addition improves quality before accepting its latency cost.

---

## Hands-On: Hybrid Retrieval with Haystack + Qdrant + bge-reranker-v2-m3

This exercise assembles a Haystack query pipeline with three retrieval layers and measures nDCG@10 at each step. The same collection from [Module 5](local-embeddings-vector-stores.md#example-full-indexing-pipeline) is the input — no re-indexing required.

**Prerequisites**:

- A `QdrantDocumentStore` populated by the Module 5 indexing pipeline, with `use_sparse_embeddings=True` set at construction time. The sparse field is what enables BM25-equivalent retrieval alongside dense vector search.
- An evaluation set of 30+ queries with relevance labels (see "Measuring Retrieval Quality" above).
- `pip install haystack-ai qdrant-haystack sentence-transformers`.

**Step 1 — Load the document store and build the dense-only baseline**

```python
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

document_store = QdrantDocumentStore(
    path="/data/qdrant_db",
    index="documents",
    embedding_dim=768,
    use_sparse_embeddings=True,
    recreate_index=False,
)

dense_only = Pipeline()
dense_only.add_component("text_embedder", SentenceTransformersTextEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True},
    device="cpu",
))
dense_only.add_component("retriever", QdrantEmbeddingRetriever(
    document_store=document_store,
    top_k=10,
))
dense_only.connect("text_embedder.embedding", "retriever.query_embedding")

baseline = dense_only.run({"text_embedder": {"text": "CVE-2024-12345 remediation"}})
```

**Step 2 — Upgrade to hybrid RRF**

Add a sparse query embedder and a second retriever. `DocumentJoiner` handles the fusion with no score normalization required:

```python
from haystack.components.embedders import SentenceTransformersSparseTextEmbedder
from haystack.components.joiners import DocumentJoiner
from haystack_integrations.components.retrievers.qdrant import QdrantSparseEmbeddingRetriever

hybrid = Pipeline()
hybrid.add_component("dense_query", SentenceTransformersTextEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True},
    device="cpu",
))
hybrid.add_component("sparse_query", SentenceTransformersSparseTextEmbedder(
    model="prithivida/Splade_PP_en_v1",
    device="cpu",
))
hybrid.add_component("dense_retriever", QdrantEmbeddingRetriever(
    document_store=document_store, top_k=20,
))
hybrid.add_component("sparse_retriever", QdrantSparseEmbeddingRetriever(
    document_store=document_store, top_k=20,
))
hybrid.add_component("joiner", DocumentJoiner(
    join_mode="reciprocal_rank_fusion",
    top_k=20,
    weights=[0.5, 0.5],   # equal weight to dense and sparse contributions
))

hybrid.connect("dense_query.embedding", "dense_retriever.query_embedding")
hybrid.connect("sparse_query.sparse_embedding", "sparse_retriever.query_sparse_embedding")
hybrid.connect("dense_retriever.documents", "joiner.documents")
hybrid.connect("sparse_retriever.documents", "joiner.documents")

result = hybrid.run({
    "dense_query":  {"text": "CVE-2024-12345 remediation"},
    "sparse_query": {"text": "CVE-2024-12345 remediation"},
})
print([d.content for d in result["joiner"]["documents"]])
```

`join_mode="reciprocal_rank_fusion"` uses the standard RRF formula with `k=60` [verify default against the `haystack-ai` release you pin]. Weights shift the contribution of each retriever without changing the algorithm; start at 0.5/0.5 and only adjust if one retriever consistently dominates on your corpus.

**Step 3 — Add cross-encoder reranking**

Prepend `SentenceTransformersSimilarityRanker` between the joiner and the output. The ranker re-scores the top-20 candidates with `bge-reranker-v2-m3` and emits the top-5:

```python
from haystack.components.rankers import SentenceTransformersSimilarityRanker

hybrid.add_component("ranker", SentenceTransformersSimilarityRanker(
    model="BAAI/bge-reranker-v2-m3",
    top_k=5,
    device="cpu",
    model_kwargs={"torch_dtype": "float16"},  # halves memory on supported hardware
))

hybrid.connect("joiner.documents", "ranker.documents")

result = hybrid.run({
    "dense_query":  {"text": "CVE-2024-12345 remediation"},
    "sparse_query": {"text": "CVE-2024-12345 remediation"},
    "ranker":       {"query": "CVE-2024-12345 remediation"},
})
```

Note the three components receive the same query text as separate inputs. This is explicit on purpose: the dense embedder, sparse embedder, and cross-encoder all need the raw query, and Haystack's typed wiring prevents you from accidentally passing an embedding to a component expecting text.

**Step 4 — Measure nDCG@10**

Haystack 2.x ships `DocumentNDCGEvaluator` for document-level ranking metrics. Build one evaluator, run it against each pipeline variant, and compare:

```python
from haystack.components.evaluators import DocumentNDCGEvaluator

evaluator = DocumentNDCGEvaluator()

# For each query in your golden set:
#   ground_truth_documents = [relevant docs for this query]
#   retrieved_documents    = [docs returned by the pipeline]
ndcg_result = evaluator.run(
    ground_truth_documents=[golden_docs_query_1, golden_docs_query_2, ...],
    retrieved_documents=[pipeline_out_query_1, pipeline_out_query_2, ...],
)
print(f"nDCG@10: {ndcg_result['score']:.4f}")
```

Compare nDCG@10 across: dense-only baseline, hybrid RRF, hybrid + rerank. Reject each layer if it does not improve nDCG@10 on your evaluation set — your specific corpus may differ from published benchmarks.

**Step 5 — Serialize the pipeline for audit**

```python
with open("pipelines/query.yaml", "w") as f:
    f.write(hybrid.dumps())
```

The resulting YAML file is the audit artifact for this pipeline. It names every Component class, its parameters (models, top_k values, weights), and the exact wiring between them. A security reviewer can read it top to bottom without knowing Python, diff it across versions, and block any change that introduces a network-bearing component.

---

## Key Takeaways

- Dense retrieval misses on exact-token queries; BM25 misses on paraphrased queries. Hybrid RRF covers both with no score normalization overhead — use it as the default for technical corpora.
- RRF score = Σ 1/(60 + rank). It operates on rank positions, not raw scores, making it robust to incompatible score scales across retrievers.
- Cross-encoder re-ranking adds ~100–200ms latency per query and requires the full retrieval pass to complete first. Add it only when nDCG@10 measurements confirm retrieval quality failures that exceed your latency budget's tolerance.
- `bge-reranker-v2-m3` runs offline at 0.6B parameters. On CPU, cap the candidate set at 50 documents; use GPU above that.
- HyDE helps on vague, question-form queries but adds a local LLM inference call. Skip it when queries contain exact identifiers or when latency is critical.
- Measure nDCG@10 on a labeled evaluation set before and after adding each layer. Published benchmarks reflect average corpora — verify improvements on your own data.

## Unverified Claims

- Cross-encoder re-ranking latency of ~100–200ms for 30 candidates — varies significantly by hardware, model size, and batch implementation. Benchmark on your target hardware before committing.
- `bge-reranker-large` adds ~2 nDCG@10 points over v2-m3 at double the inference latency — unverified; no canonical benchmark source confirmed.
- Jina Reranker v2 achieves 81.33% Hit@1 at ~188ms — benchmark conditions not independently verified.

## Related

**Within this training series**

- [Overview and When to Use Air-Gapped RAG](overview.md)
- [Architecture Fundamentals](architecture-fundamentals.md)
- [Chunking Strategies](chunking-strategies.md)
- [Local Embeddings and Vector Stores](local-embeddings-vector-stores.md)
- [Local LLM Inference](local-llm-inference.md)

**Reference pages**

- [Context Engineering](../../context-engineering/context-engineering.md)
- [Lost in the Middle](../../context-engineering/lost-in-the-middle.md)
