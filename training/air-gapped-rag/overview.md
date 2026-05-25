---
title: "Air-Gapped RAG: Overview and When to Use It"
description: "What air-gapped RAG is, the isolation levels it covers, when it is required vs. over-engineering, and the realistic cost and quality tradeoffs against cloud-based alternatives."
tags:
  - training
  - security
  - workflows
  - tool-agnostic
aliases:
  - offline RAG deployment
  - on-premises RAG
  - air-gapped retrieval augmented generation
---

# Air-Gapped RAG: Overview and When to Use It

> Air-gapped RAG keeps every component of the retrieval-augmented generation stack — documents, embeddings, vector store, and inference — within a network boundary you control, satisfying regulations and threat models that cloud alternatives cannot.

---

## What "Air-Gapped" Actually Means

The term covers a spectrum of network isolation, not a single standard:

| Level | Description | Example use case |
|-------|-------------|------------------|
| **Fully offline** | No network interfaces connected to any external network. Data moves only via physical media. | Classified, SCIFs, industrial control systems |
| **Internal network** | Connected to an internal LAN but no internet egress. Outbound traffic is blocked at the perimeter. | Regulated enterprise, air-gapped R&D labs |
| **DMZ deployment** | Segmented between internal and external networks by two firewall layers. Controlled inbound only. | Government contractors, healthcare portals |

Most enterprise air-gapped RAG deployments are the "internal network" variant — internet-blocked but internally reachable. Fully offline deployments require sneakernet updates and are rare outside classified environments. Per [Wikipedia's definition](https://en.wikipedia.org/wiki/Air_gap_(networking)), a true air gap requires physical isolation from any externally connected network; practitioners often use the term loosely for any on-premises deployment.

---

## When Air-Gapped Is Required

Air-gapped deployment is not a preference — in the following contexts it is a compliance or legal necessity:

**Regulated industries with data residency mandates**

- **HIPAA**: Sending protected health information (PHI) to any external AI service endpoint is a covered disclosure. On-premises deployment keeps PHI within the covered entity's infrastructure.
- **ITAR / FedRAMP**: Organizations handling controlled unclassified information (CUI) or ITAR-regulated content are often explicitly prohibited from using commercial cloud AI services. [Source: ITAR/FedRAMP requirements for CUI handling](https://www.docsie.io/blog/articles/on-prem-ai-documentation-assistant-2026/)
- **GDPR**: Cross-border data transfers require Standard Contractual Clauses or adequacy decisions. Any query against a dataset containing PII that routes through a non-EU provider is a potential violation. [Source: GDPR cross-border transfer rules](https://aidatagateway.com/articles/ai-data-compliance-gdpr-hipaa)

**Classified and sensitive environments**

- Classified environments (SECRET, TS/SCI) have no lawful cloud option — the data cannot leave the accredited enclave.
- Sensitive IP (unreleased patents, M&A due diligence, trade secrets) where even BAAs and DPAs leave residual risk.

**Edge and disconnected deployments**

- Devices operating without reliable internet: field equipment, vessels, remote sites, embedded systems.
- Real-time operational requirements where cloud latency (100–500ms per LLM call) is unacceptable.

---

## When Air-Gapped Is Over-Engineering

Air-gapped RAG carries substantial setup and maintenance costs. Avoid it when:

- The documents contain no regulated data and your cloud provider's BAA/DPA covers applicable obligations.
- Privacy concerns are addressed by the cloud provider's contractual terms — minor sensitivity does not warrant full isolation.
- The primary motivation is control or cost, not a regulatory or threat model requirement — hybrid architectures (on-premises retrieval, private-cloud inference) often address these at lower operational cost.
- You are prototyping or in early evaluation — cloud RAG has a 1–2 day setup vs. weeks for a hardened on-premises stack.

The cost of getting this wrong runs in both directions: deploying cloud RAG when regulation requires local deployment creates legal liability; deploying air-gapped RAG when it is unnecessary creates operational overhead that compounds across every maintenance cycle.

---

## Threat Model

Air-gapped RAG addresses a specific threat model. Understanding its scope prevents both under-investment and false confidence.

**What it defends against**

- Data exfiltration via the inference API: queries and retrieved content never leave your network boundary.
- Third-party model provider data retention: cloud providers typically retain request logs, and exact retention windows depend on the provider's DPA and contract tier — queries are part of that telemetry surface unless a zero-retention agreement is in place.
- Supply chain risk from cloud model updates: a provider can silently modify model behavior; a pinned local model version does not change without your action.
- Internet-facing attack surface: an internally-only reachable RAG system cannot be queried from the public internet.

**What remains in scope**

- Insider threat: a user with legitimate access to the local system can exfiltrate documents or query results.
- Embedding leakage within the perimeter: if your retrieval layer is accessible to multiple internal services, embedding similarity queries can leak document structure. [Source: Privacy-Aware RAG, arxiv 2503.15548](https://arxiv.org/abs/2503.15548)
- Physical access: fully offline systems are vulnerable to physical media attacks.
- Prompt injection through ingested documents: malicious content in the document corpus can manipulate retrieval and generation — isolation from the internet does not neutralize this vector. See [Prompt Injection Threat Model](../../security/prompt-injection-threat-model.md).

---

## Cost and Quality Tradeoffs

### Setup and maintenance burden

A cloud RAG stack (OpenAI embeddings + Pinecone + GPT-4) can be functional in a day. An equivalent air-gapped stack requires: hardware procurement or VM provisioning, OS hardening, container orchestration, local model download and serving configuration, vector store setup, document pipeline construction, and an operational runbook. The ICSA 2026 on-premises RAG blueprint estimates the architecture at six distinct service components with separate scaling and maintenance profiles. [Source: On-Premises RAG Blueprint, arxiv 2604.01395](https://arxiv.org/abs/2604.01395)

### Model quality

The quality gap between local and cloud models has narrowed substantially:

- **Embeddings**: [`nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) (137M parameters, fully open-source) matches or exceeds OpenAI's [`text-embedding-ada-002` and `text-embedding-3-small`](https://platform.openai.com/docs/guides/embeddings) on MTEB short and long-context benchmarks. [Source: Nomic AI](https://www.nomic.ai/news/nomic-embed-text-v1)
- **Generation**: 7B–13B parameter models on consumer or workstation GPUs produce acceptable results for structured document Q&A. A 7B Q4-quantized model requires approximately 5GB VRAM at 4K context. [Source: Local LLM guide](https://developers.redhat.com/articles/2025/09/30/vllm-or-llamacpp-choosing-right-llm-inference-engine-your-use-case)
- **Remaining gap**: Frontier tasks — multi-step reasoning, cross-document synthesis, ambiguous queries — still show a measurable quality gap vs. GPT-4 class cloud models. For well-scoped enterprise document Q&A, this gap is often acceptable.

### Hardware cost

| Scale | Minimum hardware | Approximate cost |
|-------|-----------------|-----------------|
| Single developer / prototype | 16GB RAM, 8GB VRAM GPU | ~$1,500 (GPU) |
| Small team (10 concurrent users) | 64GB RAM, 24GB VRAM GPU | ~$5,000–$8,000 |
| Production (100+ concurrent users) | Multi-GPU server, NVMe storage | Multi-GPU server class — confirm with vendor quotes before budgeting |

Hardware costs are one-time but maintenance, power, and operations are ongoing. Compare against cloud API costs at expected query volume before committing.

---

## Pathway Overview

This module is the opening unit of a nine-module series. Each module is a 60–90 minute hands-on session covering one layer of the stack:

1. **Overview and When to Use It** ← this module
2. Architecture Fundamentals — components, data flow, deployment topology
3. Document Ingestion and Parsing — PDF, Word, HTML at scale without cloud OCR
4. [Chunking Strategies](chunking-strategies.md) — fixed, semantic, hierarchical, and their retrieval tradeoffs
5. Local Embeddings and Vector Stores — model selection, ChromaDB, LanceDB, Milvus
6. Retrieval and Re-Ranking — BM25, dense retrieval, hybrid, cross-encoders
7. Local LLM Inference — Ollama, vLLM, llama.cpp, hardware sizing
8. Grounding, Citations, and Evaluation — source attribution, faithfulness scoring, evals
9. Deployment, Operations, and Compliance — logging, access control, audit trails

All modules use only locally-runnable tools. No cloud API calls appear anywhere in the series.

---

## Example

A legal firm stores client contracts and case documents. Counsel wants to query this corpus using natural language. The constraints: attorney-client privilege prohibits third-party processing; [ABA Formal Opinion 512](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-october/aba-ethics-opinion-generative-ai-offers-useful-framework/) and state-bar guidance treat sending client confidences to a third-party generative AI tool as a disclosure event that requires informed consent and adequate safeguards.

The deployment is a single [Haystack](https://github.com/deepset-ai/haystack) pipeline (matches the series [reference stack](index.md#reference-stack)):

- Framework: `haystack-ai` 2.x — one `Pipeline` wires every stage and serializes to a YAML file bar-association counsel can audit alongside the firm's other written policies
- Document ingestion: `PyPDFToDocument` and `DOCXToDocument` converters for the baseline, [`docling`](https://github.com/DS4SD/docling) for complex filings, all running in a Hayhooks container
- Embeddings: [`nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) via `SentenceTransformersDocumentEmbedder`, weights pre-downloaded to the firm's on-premises server
- Vector store: [Qdrant](https://github.com/qdrant/qdrant) in local persistent mode with both dense and sparse vectors enabled (`QdrantDocumentStore`)
- LLM inference: `qwen2.5:7b` (Q4_K_M) served by [Ollama](https://github.com/ollama/ollama), invoked via `OllamaGenerator` — no internet access configured at the OS level
- Evaluation: `FaithfulnessEvaluator` backed by the same local LLM, run nightly against a golden query set of prior attorney-reviewed answers

A query like "Which contracts include arbitration clauses expiring before 2027?" flows through the Haystack pipeline entirely on the firm's network. The pipeline YAML is version-controlled in the firm's document-management system; each signed container release ships with a matching SBOM so the firm's IT auditor can map every dependency to an approved software list.

---

## Key Takeaways

- "Air-gapped" covers a spectrum: fully offline, internal-network-only, and DMZ deployments each have different operational profiles and appropriate use cases.
- Air-gapped is required when regulation explicitly prohibits third-party data processing (HIPAA PHI, ITAR CUI, classified environments) or when the threat model demands it — not as a default for privacy preferences.
- The quality gap between local and cloud models has narrowed: `nomic-embed-text-v1.5` matches OpenAI's older embedding models on MTEB; 7B parameter models are viable for structured document Q&A.
- Setup and maintenance costs are substantially higher than cloud RAG — the operational overhead compounds. Quantify this before committing.
- Air-gapped isolation does not neutralize all vectors: insider threat, prompt injection through ingested documents, and embedding leakage within the perimeter remain in scope.

---

## Related

- [Prompt Injection Threat Model](../../security/prompt-injection-threat-model.md)
- [Defense in Depth for Agent Safety](../../security/defense-in-depth-agent-safety.md)
- [Lethal Trifecta Threat Model](../../security/lethal-trifecta-threat-model.md)
