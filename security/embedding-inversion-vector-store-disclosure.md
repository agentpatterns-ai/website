---
title: "Embedding Inversion: Vector Stores as a Source-Text Disclosure Surface"
term: "Embedding Inversion"
description: "Stored embeddings can be partially inverted to reconstruct source text, so a vector index is a copy of the corpus — the LLM08:2025 confidentiality slice that access-control and poisoning defenses miss."
tags:
  - security
  - agent-design
  - tool-agnostic
  - rag
aliases:
  - vec2text attack
  - vector store source text recovery
  - LLM08 embedding inversion
last_reviewed: 2026-06-02
maturity: established
---

# Embedding Inversion: Vector Stores as a Source-Text Disclosure Surface

> Stored embeddings can be partially inverted to reconstruct source text — a vector index is a copy of the corpus, not metadata.

Embedding inversion uses a learned decoder to map a stored vector back to its source text, reported at 92% exact recovery on 32-token inputs from `text-embedding-ada-002` ([Morris et al., EMNLP 2023](https://arxiv.org/abs/2310.06816)). It is the confidentiality slice of [OWASP LLM08:2025 Vector and Embedding Weaknesses](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) — distinct from the access slice (cross-tenant retrieval) and the integrity slice (knowledge-base poisoning).

## When the Threat Is Real

The 92% headline holds only under narrow conditions. Recovery rates degrade sharply outside the inverter's training regime ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)):

| Condition | Effect on recovery |
|---|---|
| Input length matches inverter training length (e.g. 32 tokens) | High — 92% exact match, BLEU ~83 on MSMARCO ([Morris et al., 2023](https://arxiv.org/abs/2310.06816)) |
| In-domain text (Quora, MSMARCO) | High — 95.1 BLEU on Quora ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)) |
| Out-of-domain text (SciFact) | Collapses — Token F1 9.14 ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)) |
| Off-training length | Collapses — model trained on 32 tokens fails on 128 ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)) |
| High-entropy strings (passwords) | Limited — 36% Easy, 22% Medium, 4% Hard with `ada-ms-128` ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)) |

The viable threat surface is short-form, in-distribution text — chat snippets, ticket titles, support messages, names, log lines. Long-form documents in unusual domains face a far smaller attack.

## Why Access Control Alone Is Not Enough

The access slice ([multitenant-rag-authorization-gap](multitenant-rag-authorization-gap.md)) gates *retrieval responses*. The poisoning slice ([rag-architecture-poisoning-robustness](rag-architecture-poisoning-robustness.md)) gates *retrieval inputs*. Neither addresses the case where the **index itself leaks** — via a misconfigured vector database, an exposed admin API, an insider, or an intercepted replication channel.

ALGEN shows that an attacker holding a leaked index plus ~30 paired (text, embedding) samples exceeds Rouge-L 20 on reconstruction; ~1,000 samples reaches Rouge-L ~45 — with no access to the original embedding model or query API ([Yin et al., 2025](https://arxiv.org/abs/2502.11308)). Black-box post-exfiltration recovery is the realistic threat model. Encryption-at-rest does not close it: embeddings are decrypted at query time, and inversion runs on the live vector ([OWASP LLM08:2025](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/)).

## Why It Works

Dense text embeddings (≥768 dimensions) preserve fine-grained semantic and lexical signal — the property retrieval relies on. The signal that makes a vector a good retrieval key is the same signal a learned decoder uses to map it back. Morris et al. frame inversion as *controlled generation: generating text that, when re-embedded, is close to a fixed point in latent space* — an iterative decode-then-re-embed loop that converges whenever the embedding's fingerprint is unique enough ([Morris et al., EMNLP 2023](https://arxiv.org/abs/2310.06816)). An embedding is not a hash; it is a lossy but highly recoverable encoding.

## Controls

Layer defenses against the realistic threat model — the index leaks and the attacker holds it offline:

| Control | What it does | Source |
|---|---|---|
| **Treat the index as confidential as the corpus** | Same ACLs, audit, retention as the source documents | [OWASP LLM08:2025](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) |
| **Gaussian noise on stored vectors** | λ≈0.01 perturbation defeats vec2text while preserving retrieval — the cheapest practical defense | [Seputis et al., 2025](https://arxiv.org/abs/2507.07700) |
| **Never embed secrets** | API keys, passwords, and high-entropy short strings face the strongest password-recovery vector; scrub before embedding | [Seputis et al., 2025](https://arxiv.org/abs/2507.07700) |
| **Projection / mutual-information defense** | Heavier options like Eguard report ~95% token-level protection without major utility loss | [Zhou et al., 2024](https://arxiv.org/abs/2411.05034) |
| **Index access logging** | An inversion attack starts with an index read; logging turns silent confidentiality failure into a detectable event | [OWASP LLM08:2025](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) |

## Example

The Gaussian-noise defense as a one-line addition to the indexing pipeline. The noise is applied at write time so the stored vectors are already perturbed when an attacker reads them.

**Before** — raw embeddings stored:

```python
vectors = [embed(chunk) for chunk in chunks]
qdrant.upsert(collection="docs", points=vectors)
```

**After** — λ=0.01 Gaussian noise applied before storage:

```python
import numpy as np

LAMBDA = 0.01  # tune against your retrieval-quality benchmarks

def noisy(v):
    return v + np.random.normal(0, LAMBDA, size=v.shape)

vectors = [noisy(embed(chunk)) for chunk in chunks]
qdrant.upsert(collection="docs", points=vectors)
```

The noise level must be calibrated against retrieval Precision@K on the deployment workload — λ too small leaves inversion viable, λ too large degrades search ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)).

## When This Backfires

- **The index is not the attacker's path.** Most teams hit cross-tenant retrieval (the access slice) long before they hit embedding inversion. The cross-tenant probe-leak rate is 98–100% on un-gated retrieval ([Arceo and Narsing, 2026](https://arxiv.org/abs/2605.05287)); inversion requires the attacker to first exfiltrate the index. Close the access slice first.
- **Embedding model and corpus are out-of-distribution.** Long documents, technical jargon, code, and non-English text all degrade recovery rates by an order of magnitude ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)). For these corpora, inversion is a low-priority residual risk after access and poisoning are addressed.
- **Tuning Gaussian noise without measurement.** λ=0.01 is the published sweet spot for one specific paper's setup. Without measuring retrieval Precision@K and inversion success on your own corpus, the parameter is guesswork — the defense can silently break retrieval or silently fail to defend ([Seputis et al., 2025](https://arxiv.org/abs/2507.07700)).
- **Encryption-only is the defense.** Encryption protects the index at rest but not at query time; inversion attacks operate on decrypted vectors. An encrypted-only deployment fails an LLM08 confidentiality audit and provides a false sense of safety ([OWASP LLM08:2025](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/)).

## Key Takeaways

- Vector indexes are derivative copies of the source corpus, not metadata — the LLM08 confidentiality slice that access control and poisoning defenses do not address.
- The strongest published recovery (~92% on 32-token text) holds only under narrow conditions; out-of-domain and off-training-length inputs collapse to single-digit Token F1.
- Black-box attacks (ALGEN) need only ~30 paired samples to bootstrap, so a leaked index plus any public-corpus overlap is sufficient — the attacker does not need the original embedding model.
- The cheap defense is λ≈0.01 Gaussian noise on stored vectors; tune against your own retrieval benchmarks rather than copying the published constant.
- For most teams the priority order is: close access (cross-tenant retrieval), then poisoning (KB write controls), then confidentiality (this page). Skipping the first two to harden the third is a misallocation.

## Related

- [Multitenant RAG: Closing the Relevance-Authorization Gap](multitenant-rag-authorization-gap.md)
- [RAG Architecture as a Poisoning Robustness Decision](rag-architecture-poisoning-robustness.md)
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
