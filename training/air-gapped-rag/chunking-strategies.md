---
title: "Air-Gapped RAG: Chunking Strategies"
description: "Compare fixed-size, recursive, semantic, hierarchical, and late chunking for offline RAG pipelines — understand the trade-offs and when each strategy earns its cost."
tags:
  - training
  - context-engineering
  - tool-agnostic
---

# Air-Gapped RAG: Chunking Strategies

> Chunking is the highest-leverage decision in a RAG pipeline — bad chunks sabotage retrieval regardless of embedding model quality or re-ranker sophistication.

This module covers the five main chunking strategies, their offline-specific constraints, empirical trade-offs, and a decision framework for matching strategy to document type. Runnable code uses Haystack's [`DocumentSplitter`](https://docs.haystack.deepset.ai/docs/documentsplitter) and related preprocessors — the same classes as the indexing pipeline in [Module 2](architecture-fundamentals.md#assembling-the-pipeline-in-haystack).

---

## Why Chunking Determines Retrieval Quality

Embeddings compress text into fixed-length vectors. A dense retriever finds chunks whose embedding is close to the query embedding. If a chunk mixes two topics, its embedding averages them — it matches neither query well. If a chunk splits a sentence mid-thought, the embedding loses the sentence's meaning.

The problem compounds in air-gapped deployments: you cannot call a cloud re-ranker to fix retrieval misses after the fact. Your chunking strategy must carry the load that cloud pipelines outsource to downstream correction.

---

## Strategy Comparison

| Strategy | Cost | Structural awareness | Haystack component | Air-gapped constraint | Best for |
|----------|------|---------------------|--------------------|----------------------|----------|
| Fixed-size (word/char) | Lowest | None | `DocumentSplitter(split_by="word")` | None | Homogeneous prose, rapid prototyping |
| Sentence-aware | Low | Hierarchy-aware | `DocumentSplitter(split_by="sentence")` | None | Default for most documents |
| Passage / paragraph | Low | Paragraph-aware | `DocumentSplitter(split_by="passage")` | None | Pre-formatted technical docs |
| Semantic | Medium | Meaning-aware | `NLTKDocumentSplitter` + custom semantic boundary component | Local embed model at index time | Mixed-topic documents |
| Hierarchical (parent-child) | Low-medium | Structure-preserving | `HierarchicalDocumentSplitter` | None | Precision + context trade-off |
| Late chunking | High | Long-range context | Custom component wrapping [jina-embeddings-v2](https://github.com/jina-ai/late-chunking) | Long-context local embed model | Documents with pronouns, cross-refs |

---

## Fixed-Size Chunking

Haystack's `DocumentSplitter(split_by="word", split_length=N, split_overlap=M)` splits by word count with configurable overlap. No structural awareness — splits wherever the boundary falls.

```python
from haystack.components.preprocessors import DocumentSplitter

splitter = DocumentSplitter(split_by="word", split_length=200, split_overlap=40)
result = splitter.run(documents=docs)
```

**Cost**: pure string manipulation — no embedding calls beyond the ones the Embed stage already makes on the resulting chunks. Nothing extra during chunking itself.

**Weakness**: splits mid-sentence or mid-table. A 200-word chunk that starts mid-paragraph has no heading signal — its embedding is semantically dilute.

**When to use**: rapid iteration, homogeneous prose (news articles, transcripts), or when you need a deterministic, debuggable split for comparison against a smarter strategy. Sentence-aware splitting (next section) is the better default for almost everything — use word-based as a baseline only when you specifically need the determinism.

**Parameters**: start at 200–300 words with 20% overlap. For legal or academic documents, 400–800 words; for FAQ content, 100–200 words. Word counts in `DocumentSplitter` are not exact token counts — expect 1.3–1.5 tokens per word for English text on BPE tokenizers; pad downward from the embedding model's declared max.

---

## Sentence-Aware Splitting

`DocumentSplitter(split_by="sentence", split_length=N, split_overlap=M)` groups N consecutive sentences per chunk. Sentence boundaries come from NLTK or a regex fallback — the splitter respects sentence endings rather than cutting mid-clause.

```python
splitter = DocumentSplitter(
    split_by="sentence",
    split_length=5,       # 5 sentences per chunk
    split_overlap=1,      # 1-sentence overlap between chunks
)
```

This preserves sentence-level semantic units. A paragraph with five short sentences becomes one chunk. A long explanatory paragraph with complex reasoning becomes two or three chunks that each contain whole sentences.

**Cost**: the tokenizer pass for sentence detection is negligible on CPU. No extra computation over word-based splitting in practice.

**Weakness**: variable chunk sizes. Five long sentences of dense legal text might exceed the embedding model's max tokens; five short dialogue lines might fit in a quarter of the window.

**When to use**: **this is the default for the reference stack**. Sentence-aware adds no measurable cost over word-based, measurably reduces boundary cuts, and gives the embedding model clean semantic units to work with. A February 2026 benchmark placed sentence-aware 512-token splitting first at 69% end-to-end accuracy across diverse document types, outperforming semantic and hierarchical strategies on that test set [unverified — source not directly accessed].

---

## Passage / Paragraph Splitting

`DocumentSplitter(split_by="passage")` uses blank-line paragraph boundaries as split points. Each passage becomes one or more chunks depending on `split_length` (measured in passages).

Useful for pre-formatted technical documentation where paragraph breaks already align with conceptual boundaries — API references, structured specifications, or any corpus where the author has already chosen good split points. Weak on free-flowing prose where paragraph boundaries are inconsistent.

---

## Semantic Chunking

Haystack 2.x does not ship a built-in semantic chunker — the strategy needs an embedding model at index time, so it is wrapped as a custom Component that embeds each sentence, computes cosine distance between consecutive sentence embeddings, and inserts a chunk boundary wherever distance exceeds a configurable threshold.

A minimal custom component (full implementation in [Haystack custom component docs](https://docs.haystack.deepset.ai/docs/custom-components)):

```python
from haystack import component, Document
from sentence_transformers import SentenceTransformer
import numpy as np

@component
class SemanticChunker:
    def __init__(self, model: str, threshold_percentile: float = 95.0):
        self.model = SentenceTransformer(model)
        self.threshold_percentile = threshold_percentile

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]) -> dict:
        out: list[Document] = []
        for doc in documents:
            sentences = doc.content.split(". ")  # use NLTK for production
            if len(sentences) < 2:
                out.append(doc)
                continue
            embs = self.model.encode(sentences, normalize_embeddings=True)
            distances = [1 - np.dot(embs[i], embs[i+1]) for i in range(len(embs)-1)]
            threshold = np.percentile(distances, self.threshold_percentile)
            chunks, current = [], [sentences[0]]
            for i, d in enumerate(distances):
                if d > threshold:
                    chunks.append(". ".join(current))
                    current = [sentences[i+1]]
                else:
                    current.append(sentences[i+1])
            chunks.append(". ".join(current))
            for chunk in chunks:
                out.append(Document(content=chunk, meta=doc.meta))
        return {"documents": out}
```

Three threshold modes are common: percentile (split above the X percentile; recommended: 95), standard deviation (split above X standard deviations; recommended: 3), and interquartile (recommended: 1.5). Standard deviation mode produces more predictable chunk sizes.

**Air-gapped constraint**: semantic chunking calls an embedding model at index time, not just at query time. In an offline deployment you need a local embedding model running during ingestion — the same model you use for query embedding works, but you must provision inference capacity for the full corpus ingestion pass.

**Cost**: O(n) embedding calls during indexing, where n is sentence count. For a 10,000-page corpus this is non-trivial on CPU-only hardware.

**Weakness**: does not universally outperform sentence-aware splitting. A NAACL 2025 study found that fixed 200-word chunks matched or exceeded semantic chunking on several retrieval benchmarks [unverified — source paper not directly accessed].

**When to use**: documents with abrupt topic shifts that fall within paragraphs — technical specs that mix narrative and tabular data, transcripts where speakers change subject mid-paragraph.

---

## Hierarchical (Parent-Child) Chunking

Index small child chunks for retrieval precision; return the larger parent document to the LLM for answer generation.

Haystack ships `HierarchicalDocumentSplitter` which produces two tiers of documents from one input: fine-grained leaves (embedded for retrieval) and coarser ancestors (returned to the LLM after matching). The splitter tracks parent-child relationships via document IDs in the `meta` dict.

```python
from haystack.components.preprocessors import HierarchicalDocumentSplitter

splitter = HierarchicalDocumentSplitter(
    block_sizes={5, 20},   # 5-sentence leaves, 20-sentence parents
    split_overlap=1,
    split_by="sentence",
)
result = splitter.run(documents=docs)
# result["documents"] contains both leaves and parents;
# leaves carry `_parent_id` in meta for later expansion at query time
```

At query time, use a combination of retriever + a custom expansion step that replaces each retrieved leaf with its parent before the chunks reach the generator. The pattern is a small custom component wrapping a document-store lookup by parent ID.

**Air-gapped constraint**: none beyond the base embedding model. No extra inference beyond what sentence-aware splitting requires.

**Why this works**: small chunks embed more precisely (less semantic dilution). Large parent chunks give the LLM enough surrounding context to synthesize accurate answers without hallucinating missing information.

**Weakness**: doubles storage — both child and parent chunks must be stored. The parent store can share the same `DocumentStore` if you filter by element type in `meta`, or use a separate in-memory docstore for just the parents.

**When to use**: when retrieval precision matters more than storage cost, and documents are long enough that flat chunking loses inter-sentence context. Technical documentation, long-form reports, policy documents.

---

## Late Chunking

Late chunking reverses the standard pipeline. Instead of split → embed, it embeds first, then splits.

The full document is fed to a long-context embedding model ([jina-embeddings-v2](https://github.com/jina-ai/late-chunking) at 8192 tokens). The transformer processes all tokens with full cross-document attention. Then mean pooling is applied over chunk boundaries — each chunk gets an embedding derived from token representations that already contain document-wide context.

This preserves anaphoric references ("it", "they", "this approach") and cross-section dependencies that split-then-embed loses. A chunk containing "Its population exceeds 3.85 million" has no referent when split in isolation. Late chunking's embeddings carry the entity ("Berlin") from earlier in the document.

**Empirical results** ([arxiv:2409.04701](https://arxiv.org/abs/2409.04701), [jina-ai/late-chunking](https://github.com/jina-ai/late-chunking)):

| Dataset | Standard chunking (nDCG@10) | Late chunking (nDCG@10) |
|---------|-----------------------------|-------------------------|
| SciFact | 64.20% | 66.10% |
| FiQA2018 | 33.25% | 33.84% |
| NFCorpus | 23.46% | 29.98% |

Gains correlate with document length — short, self-contained chunks benefit less.

**Air-gapped constraint**: requires a long-context local embedding model. `jina-embeddings-v2-small-en` runs on CPU but fitting an 8192-token document in a single forward pass is memory-intensive. Plan for at least 16 GB RAM for batch ingestion on CPU; GPU significantly reduces wall-clock time [unverified — no official hardware requirements published].

**When to use**: documents with dense cross-references, legal contracts with defined terms, technical papers with abbreviations defined at the top. The cost is justified when pronoun/reference resolution is a frequent retrieval failure mode.

---

## Decision Framework

Start with sentence-aware splitting, 5 sentences per chunk, 1-sentence overlap. Measure retrieval precision and recall on a representative sample of your corpus before changing strategy.

```
Document type → recommended starting configuration

Short, homogeneous prose (FAQs, news)      → DocumentSplitter(split_by="word", split_length=200)
Structured docs (tech docs, reports)       → DocumentSplitter(split_by="sentence", split_length=5)
Pre-formatted technical reference          → DocumentSplitter(split_by="passage", split_length=2)
Mixed-topic documents                      → custom SemanticChunker component
Long docs needing precision + context      → HierarchicalDocumentSplitter(block_sizes={5, 20})
Dense cross-references, pronouns           → custom LateChunking component (requires long-context model)
```

Switch to a more complex strategy only when retrieval metrics on your actual corpus show the simpler approach is the bottleneck. Embedding model choice, query construction, and re-ranking all interact with chunk quality — measure in combination.

---

## Example

Hierarchical parent-child indexing using Haystack's `HierarchicalDocumentSplitter` with the series [reference stack](index.md#reference-stack) — Qdrant for vectors, sentence-transformers for embeddings:

```python
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import HierarchicalDocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

# Qdrant in local persistent mode — same store as Module 5
document_store = QdrantDocumentStore(
    path="/data/qdrant_db",
    index="documents",
    embedding_dim=768,
    use_sparse_embeddings=False,  # hierarchical example keeps dense-only for clarity
    recreate_index=False,
)

indexing = Pipeline()
indexing.add_component("converter", PyPDFToDocument())
indexing.add_component("splitter", HierarchicalDocumentSplitter(
    block_sizes={5, 20},      # 5-sentence leaves (embedded), 20-sentence parents (returned)
    split_overlap=1,
    split_by="sentence",
))
indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    device="cpu",
))
indexing.add_component("writer", DocumentWriter(document_store=document_store))

indexing.connect("converter.documents", "splitter.documents")
indexing.connect("splitter.documents", "embedder.documents")
indexing.connect("embedder.documents", "writer.documents")

indexing.run({"converter": {"sources": ["corpus/policy.pdf"]}})
```

Every component runs locally — no external API calls. The `HierarchicalDocumentSplitter` writes both the 5-sentence leaves and their 20-sentence parents to the same `QdrantDocumentStore` with a `block_size` field in `meta`; at query time, filter on `block_size == 5` for dense retrieval and dereference `_parent_id` to pull the matching parent blocks before passing context to the generator.

The corresponding query-side expansion lives in Module 6, where the custom `ParentDocumentExpander` component sits between the reranker and the prompt builder.

---

## Key Takeaways

- Recursive character splitting is the correct default — hierarchy-awareness adds zero extra cost over fixed-size
- Semantic chunking adds index-time embedding cost; benchmark on your corpus before assuming it improves results over recursive splitting
- Hierarchical parent-child retrieval decouples retrieval precision from LLM context size — use it when long-document context is lost with flat chunking
- Late chunking preserves cross-document references but requires a long-context local embedding model with substantial RAM
- In air-gapped deployments, semantic and late chunking require local embedding inference during ingestion — plan hardware capacity for the full corpus pass
- Establish a recursive baseline first; switch strategies only when retrieval metrics show the current approach is the bottleneck

## Unverified Claims

- Semantic chunking performance relative to fixed-size: the claim that fixed 200-word chunks matched or exceeded semantic chunking on several benchmarks is attributed to a NAACL 2025 study; the original paper was not directly accessed to confirm this finding
- Recursive splitting February 2026 benchmark at 69% accuracy: cited from web search summaries; the original benchmark source was not directly accessed
- Late chunking RAM requirement of 16 GB for CPU ingestion: no official hardware specifications were published by Jina AI; this is a practitioner estimate based on model size

## Related

- [Document Ingestion and Parsing](document-ingestion-and-parsing.md) — previous module: extract structure before chunking
- [Retrieval-Augmented Agent Workflows](../../context-engineering/retrieval-augmented-agent-workflows.md)
- [Prompt Compression](../../context-engineering/prompt-compression.md)
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md)
