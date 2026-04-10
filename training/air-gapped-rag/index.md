---
title: "Air-Gapped RAG Training Series"
description: "Hands-on pathway for building a fully offline retrieval-augmented generation system — from threat model to production deployment, for regulated and sensitive environments."
tags:
  - training
  - security
  - workflows
  - tool-agnostic
---

# Air-Gapped RAG Training Series

> A nine-module hands-on pathway for building a production-ready RAG system that runs entirely offline — no cloud APIs, no data egress, no external dependencies.

This series targets developers in regulated industries, classified environments, or sensitive IP contexts where cloud AI is prohibited or unacceptable. Each module is a 60–90 minute hands-on session covering one layer of the stack.

## Modules

| # | Module | Focus |
|---|--------|-------|
| 1 | [Overview and When to Use It](overview.md) | Isolation levels, threat model, cost and quality tradeoffs |
| 2 | [Architecture Fundamentals](architecture-fundamentals.md) | Seven pipeline stages, coupling map, hardware sizing |
| 3 | [Document Ingestion and Parsing](document-ingestion-and-parsing.md) | Parser comparison, OCR, table extraction, metadata |
| 4 | [Chunking Strategies](chunking-strategies.md) | Fixed, recursive, semantic, hierarchical, late chunking |
| 5 | [Local Embeddings and Vector Stores](local-embeddings-vector-stores.md) | Model selection, Chroma, Qdrant, LanceDB, FAISS |
| 6 | [Retrieval and Re-Ranking](retrieval-and-reranking.md) | Dense, BM25, hybrid RRF, cross-encoders, nDCG@10 |
| 7 | [Local LLM Inference](local-llm-inference.md) | llama.cpp, Ollama, vLLM, ExLlamaV2, quantization, context budget |
| 8 | [Grounding, Citations, and Evaluation](grounding-citations-evaluation.md) | Grounding prompts, entailment checks, offline judges |
| 9 | [Deployment, Operations, and Compliance](deployment-operations-compliance.md) | Signing, CVE scanning, audit logs, HIPAA/SOC 2/FedRAMP |

## Reference Stack

Hands-on exercises across the series use one consistent stack so a reader can build the pipeline end-to-end without reconciling tool choices between modules. Every component is Apache 2.0 or MIT licensed, runs on a single laptop, and has no runtime network dependency:

- **Framework**: [Haystack 2.x](https://github.com/deepset-ai/haystack) (`haystack-ai`) — the `Pipeline` + `Component` model maps 1:1 onto the seven-stage architecture in Module 2, and pipelines serialize to YAML for security-review audit trails
- **Embeddings**: [`nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) via [sentence-transformers](https://github.com/UKPLab/sentence-transformers), wrapped by Haystack's `SentenceTransformersDocumentEmbedder`
- **Vector store**: [Qdrant](https://github.com/qdrant/qdrant) in local persistent mode via [`qdrant-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/qdrant) — dense + sparse vectors enabled at collection creation
- **Reranker**: [`bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) via Haystack's `SentenceTransformersSimilarityRanker`
- **Generation**: `qwen2.5:7b` (Q4_K_M) via [Ollama](https://github.com/ollama/ollama), invoked through [`ollama-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ollama)'s `OllamaGenerator`
- **Parsing**: Haystack's built-in `PyPDFToDocument` / `DOCXToDocument` / `HTMLToDocument` converters for the baseline; [`docling`](https://github.com/DS4SD/docling) via [`docling-haystack`](https://github.com/DS4SD/docling-haystack) for complex layouts
- **Evaluation**: Haystack's `FaithfulnessEvaluator` and `ContextRelevanceEvaluator` backed by a local `OllamaGenerator` judge; [RAGAs](https://github.com/explodinggradients/ragas) with [HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model) as the alternative path
- **Deployment**: pipelines serialized as YAML and served via [Hayhooks](https://github.com/deepset-ai/hayhooks) behind a FastAPI endpoint, packaged as signed OCI containers

Each module presents its full decision space in comparison tables — the reference stack above is the path the runnable code follows. Substitute components as you go; the comparison tables explain what changes when you do. Because Haystack is the abstraction layer, swapping Qdrant for LanceDB (for example) is a one-component edit rather than a module rewrite.

### Why Haystack for air-gapped deployment

Four properties earn Haystack its place at the top of this stack:

1. **Small audit surface.** `haystack-ai` core plus five or six explicit integration packages is the whole direct dependency list. No meta-packages pulling in hundreds of transitive integrations. Every component can be traced to a specific, pinnable PyPI package with a specific maintainer.
2. **YAML-serializable pipelines.** `pipeline.dumps()` produces a configuration document a security reviewer can read top to bottom without reading Python. Diff across versions, sign, store in configuration management, reproduce builds from YAML alone.
3. **No telemetry by default.** `haystack-ai` 2.x does not emit telemetry and makes no outbound calls during normal operation. [Verify against the specific release you pin — Haystack 1.x had opt-out telemetry; 2.x dropped it but the exact behavior of some integrations should be audited per-release.]
4. **Component model matches the pipeline mental model.** The seven stages in Module 2 map directly to Haystack Components. There is no impedance mismatch between the teaching and the runnable code.

## Constraints

All modules use only locally-runnable tools. No cloud API calls appear anywhere in the series. The hardware baseline is a 16 GB laptop with no GPU — a modest GPU accelerates embedding and generation stages, but nothing in the runnable code requires one.

For defence and classified environments, Module 9 adds the compliance layer: SBOM generation, FIPS 140-3 cryptography, STIG-hardened base images, NIST SP 800-53 control mappings, and RMF artifact templates (SSP, SAR, POA&M).

## Prerequisites

Familiarity with basic RAG concepts (retrieval, chunking, embeddings) is assumed. No prior offline deployment experience required. Python 3.10+, Docker, and a working Ollama install are used throughout.
