---
title: "Air-Gapped RAG: Local Embeddings and Vector Stores"
description: "How to choose and run open embedding models locally, and select a vector store where every embedding lives on your hardware."
tags:
  - training
  - tool-agnostic
  - cost-performance
---

# Air-Gapped RAG: Local Embeddings and Vector Stores

> Choose, run, and persist embeddings entirely on your hardware — no cloud API calls, no vendor lock-in.

This is the "no cloud dependencies" stage of the air-gapped RAG pipeline. Every embedding is generated locally; every vector lives in local storage. The main decision points are which embedding model to run and which vector store to use. Both involve real trade-offs between retrieval quality, storage cost, compute, and operational complexity.

Runnable code wires embedders and document stores into a [Haystack](https://github.com/deepset-ai/haystack) indexing pipeline. Every embedder is a `SentenceTransformersDocumentEmbedder` variant; every store is a Haystack `DocumentStore` via its dedicated integration package. Swapping any of them is a one-component edit.

---

## Embedding Models

[sentence-transformers](https://github.com/UKPLab/sentence-transformers) is the standard Python library for local embedding inference. It wraps any Hugging Face model with a two-line API and handles tokenization, batching, and device placement. Haystack's `SentenceTransformersDocumentEmbedder` and `SentenceTransformersTextEmbedder` are thin Component wrappers around it — install both with `pip install haystack-ai sentence-transformers`.

### Model Comparison

Five families cover most air-gapped deployments:

| Model | Dims | Context | Notes |
|-------|------|---------|-------|
| [bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5) | 1024 | 512 | Top MTEB for its size class; English-only |
| [nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) | 768 | 8192 | Long context; Matryoshka support; Apache 2.0 |
| [e5-large-v2](https://huggingface.co/intfloat/e5-large-v2) | 1024 | 512 | Strong retrieval; requires instruction prefix |
| [e5-mistral-7b-instruct](https://huggingface.co/intfloat/e5-mistral-7b-instruct) | 4096 | 32768 | Highest MTEB scores; requires ~14GB VRAM |
| [multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large) | 1024 | 512 | 100+ languages; use when corpus is multilingual |

Sources: [BAAI/bge-large-en-v1.5 paper (arXiv 2309.07597)](https://arxiv.org/abs/2309.07597), [E5 model variants (microsoft/unilm)](https://github.com/microsoft/unilm/tree/master/e5).

**Decision rule**: start with `nomic-embed-text-v1.5` (the series [reference stack](index.md#reference-stack)) for English corpora on CPU or modest GPU. `bge-large-en-v1.5` is a strong alternative when 1024 dimensions are acceptable and you do not need long context. Use `e5-mistral-7b-instruct` only when retrieval quality is the primary constraint and 14GB+ VRAM is available.

### Dimensionality Trade-offs

Higher dimensions store more semantic information and typically improve retrieval quality — but at a direct cost to storage and compute.

| Dims | Storage per 1M docs | Compute | Use case |
|------|---------------------|---------|----------|
| 384 | ~1.5 GB | Fastest | Prototyping, resource-constrained edge |
| 768 | ~3 GB | Fast | Standard production |
| 1024 | ~4 GB | Moderate | Quality-sensitive retrieval |
| 4096 | ~16 GB | Slow | Maximum quality, GPU required |

Storage figures are for float32 vectors. Use float16 to halve storage with minimal quality loss [unverified].

### Matryoshka Embeddings

Some models support [Matryoshka Representation Learning (MRL)](https://arxiv.org/abs/2205.13147), which encodes information at coarse-to-fine granularities within a single vector. You can truncate the embedding to a smaller dimension at query time with minimal quality degradation — for example, using 256 dimensions instead of 768 for a 3x storage reduction.

`nomic-embed-text-v1.5` explicitly supports MRL. Haystack exposes the underlying sentence-transformers options via `model_kwargs`:

```python
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

embedder = SentenceTransformersDocumentEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    truncate_dim=256,               # reduce from 768 to 256 for storage savings
    model_kwargs={"trust_remote_code": True},
    device="cpu",
)
embedder.warm_up()                  # load the model weights before first use
```

Matching the dimension on the `QdrantDocumentStore` side is mandatory — truncate to 256 at embed time, create the collection with `embedding_dim=256`. Changing the truncate_dim mid-pipeline invalidates the entire index.

---

## Vector Stores

Five stores cover the local deployment spectrum from simple to production-ready:

| Store | Deployment | Persistence | Metadata Filter | Hybrid Search | Notes |
|-------|-----------|-------------|-----------------|---------------|-------|
| [Chroma](https://github.com/chroma-core/chroma) | In-process | SQLite | Yes | No | Simplest dev experience |
| [Qdrant](https://github.com/qdrant/qdrant) | In-process or server | On-disk | Yes | Yes (sparse+dense) | Best filtering granularity; **series reference** |
| [LanceDB](https://github.com/lancedb/lancedb) | In-process | Lance columnar | Yes | Yes (FTS+vector) | Lowest disk footprint per vector |
| [FAISS](https://github.com/facebookresearch/faiss) | Library only | Manual serialization | No | No | Fastest raw ANN; no built-in ops |
| [Weaviate](https://github.com/weaviate/weaviate) | Docker | On-disk | Yes | Yes (BM25+vector) | Heaviest operational footprint |

### Qdrant (series reference stack)

[Qdrant](https://github.com/qdrant/qdrant) runs in-process via its Python client and is the vector store the rest of this series builds on. Hybrid retrieval (Module 6) and the deployment stack (Module 9) both assume a Qdrant collection. Haystack wraps it via [`qdrant-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/qdrant) — install with `pip install qdrant-haystack`:

```python
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

document_store = QdrantDocumentStore(
    path="/data/qdrant_db",       # local persistent mode; pass url="..." for server mode
    index="documents",
    embedding_dim=768,            # matches nomic-embed-text-v1.5
    use_sparse_embeddings=True,   # enables dense + sparse hybrid retrieval in Module 6
    recreate_index=False,         # never clobber an existing index by accident
)
```

Qdrant supports sparse vectors alongside dense vectors, enabling hybrid BM25-equivalent + semantic search without a separate keyword index. Filtering uses structured JSON payload fields with `must`, `should`, and `must_not` clauses — the most expressive filtering API in this group. Haystack surfaces the full filter language through the retriever's `filters` parameter.

Best for: deployments that need production-level filtering, hybrid retrieval, or will eventually scale to a server deployment. Configure `use_sparse_embeddings=True` at `QdrantDocumentStore` construction time — adding sparse vectors later requires a collection migration outside Haystack.

### Chroma

[Chroma](https://github.com/chroma-core/chroma) runs in-process with zero configuration. Haystack wraps it via [`chroma-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/chroma):

```python
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

document_store = ChromaDocumentStore(
    persist_path="/data/chroma_db",
    collection_name="documents",
    distance_function="cosine",
)
```

Best for: prototyping and single-machine deployments where operational simplicity matters more than query throughput. Note: `ChromaDocumentStore` does not expose sparse vectors, so hybrid retrieval in Module 6 requires wrapping a keyword index (e.g., `InMemoryBM25Retriever` populated from the same documents) alongside the Chroma store and fusing with `DocumentJoiner`.

### LanceDB

[LanceDB](https://github.com/lancedb/lancedb) stores vectors in the columnar Lance format, which enables zero-copy reads and efficient analytics queries over the embedding corpus. Wrap it in a Haystack custom Component or use LlamaIndex's LanceDB integration directly; there is no first-party `lancedb-haystack` package as of writing [unverified — check the [Haystack integrations catalog](https://haystack.deepset.ai/integrations) for current status].

Best for: large corpora where storage efficiency matters, or when you need SQL-style filtering over metadata. For a Haystack-native alternative with similar strengths, use Qdrant's server mode with the `payload_index_selector` configured for your hot metadata fields.

### FAISS

[FAISS](https://github.com/facebookresearch/faiss) is a library for approximate nearest-neighbor search — not a database. It provides the fastest raw vector search (IVF, HNSW, PQ indexes) but has no built-in metadata storage, no update/delete support, and no persistence API.

Haystack does not wrap FAISS as a first-class `DocumentStore` in 2.x — the older `FAISSDocumentStore` from Haystack 1.x is not available in 2.x. Use `InMemoryDocumentStore` for small corpora, or Qdrant for anything larger; FAISS is only worth the wrapping cost when raw search throughput is the dominant constraint.

---

## Example: Full Indexing Pipeline

The reference stack's indexing pipeline, end-to-end. This is the code you run once per corpus refresh — parse, clean, chunk, embed (dense + sparse), and write to Qdrant:

```python
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersSparseDocumentEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

document_store = QdrantDocumentStore(
    path="/data/qdrant_db",
    index="documents",
    embedding_dim=768,                   # nomic-embed-text-v1.5
    use_sparse_embeddings=True,
    recreate_index=False,
)

indexing = Pipeline()
indexing.add_component("converter", PyPDFToDocument())
indexing.add_component("cleaner", DocumentCleaner(
    remove_empty_lines=True,
    remove_extra_whitespaces=True,
))
indexing.add_component("splitter", DocumentSplitter(
    split_by="sentence", split_length=5, split_overlap=1,
))
indexing.add_component("dense_embedder", SentenceTransformersDocumentEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    device="cpu",
    model_kwargs={"trust_remote_code": True},
))
indexing.add_component("sparse_embedder", SentenceTransformersSparseDocumentEmbedder(
    model="prithivida/Splade_PP_en_v1",
    device="cpu",
))
indexing.add_component("writer", DocumentWriter(document_store=document_store))

indexing.connect("converter.documents", "cleaner.documents")
indexing.connect("cleaner.documents", "splitter.documents")
indexing.connect("splitter.documents", "dense_embedder.documents")
indexing.connect("dense_embedder.documents", "sparse_embedder.documents")
indexing.connect("sparse_embedder.documents", "writer.documents")

# Run against a directory of PDFs
from pathlib import Path
pdfs = [str(p) for p in Path("corpus").glob("*.pdf")]
indexing.run({"converter": {"sources": pdfs}})

# Serialize the pipeline for audit
with open("pipelines/indexing.yaml", "w") as f:
    f.write(indexing.dumps())
```

Dimension 768 matches `nomic-embed-text-v1.5`. If you swap to `bge-large-en-v1.5`, change `embedding_dim` on the `QdrantDocumentStore` to 1024 and re-create the index — embedding dimension is the single tightest coupling in the pipeline. Both values must move together, or retrieval silently returns nonsense.

---

## Key Takeaways

- Haystack's `SentenceTransformersDocumentEmbedder` + `SentenceTransformersTextEmbedder` pair wraps all major open embedding models with no cloud dependencies; the split lets you add query-side instruction prefixes without touching the indexing side
- Start with `nomic-embed-text-v1.5` for balanced quality/compute and long context; `bge-large-en-v1.5` is a strong alternative for English-only at 1024 dimensions; reserve `e5-mistral-7b-instruct` for GPU-rich deployments where retrieval quality dominates
- Matryoshka-capable models (nomic-embed-text-v1.5) let you trade storage for speed at index time via `truncate_dim`, but the dimension choice is permanent — retruncating invalidates the index
- `QdrantDocumentStore` with `use_sparse_embeddings=True` is the reference stack; `ChromaDocumentStore` is simpler but drops sparse support; Weaviate, Elasticsearch, and PGVector are available as first-party Haystack integrations when the deployment constraints demand them
- FAISS is not a Haystack 2.x first-class store — `InMemoryDocumentStore` is the lightweight path for prototyping, Qdrant for anything production-shaped
- Haystack pipelines serialize to YAML — the full indexing pipeline above becomes ~40 lines of `pipelines/indexing.yaml` that a security reviewer can audit end-to-end

## Unverified Claims

- Float16 quantization of vectors halves storage with minimal quality loss — no primary source confirmed during research

## Related

- [Air-Gapped RAG: Overview and When to Use It](overview.md)
- [Air-Gapped RAG: Architecture Fundamentals](architecture-fundamentals.md)
- [Air-Gapped RAG: Document Ingestion and Parsing](document-ingestion-and-parsing.md)
- [Air-Gapped RAG: Chunking Strategies](chunking-strategies.md)
- [Air-Gapped RAG: Retrieval and Re-Ranking](retrieval-and-reranking.md)
- [Air-Gapped RAG: Local LLM Inference](local-llm-inference.md)
