---
title: "Air-Gapped RAG: Local LLM Inference"
description: "Compare inference engines and quantization formats for offline RAG answer synthesis — hardware sizing from laptop to multi-GPU server, with context window budget guidance."
tags:
  - training
  - cost-performance
  - tool-agnostic
---

# Air-Gapped RAG: Local LLM Inference

> Answer synthesis is the hardest hardware tradeoff in air-gapped RAG — model quality scales directly with hardware cost, and quantization format determines how much model you can fit.

Local LLM inference for air-gapped RAG is the process of running an open-weight generation model entirely on-premise — no cloud API — to synthesize answers from retrieved documents. Two choices dominate cost and quality: the inference engine (which sets hardware compatibility, throughput, and batching behavior) and the quantization format (which sets how much model fits in available memory). The runnable examples use Haystack's `OllamaGenerator`; any Haystack generator component slots into the same pipeline graph, so the comparison tables below double as a guide to which Haystack component class maps to each engine.

---

## The Core Tradeoff

An air-gapped RAG system has no cloud API to fall back on. The inference quality ceiling is set by the largest model your hardware can run at an acceptable speed. Two levers control this:

1. **Inference engine** — determines hardware compatibility, throughput, and operational complexity
2. **Quantization format** — determines how much VRAM (or RAM) a given model consumes

These levers interact: some quantization formats only work with specific engines, and the right engine depends on whether you are running one user or one hundred.

---

## Inference Engine Comparison

Five engines cover the main deployment scenarios. All run fully offline. The Haystack component column names the generator class that wraps each engine:

| Engine | Throughput | Hardware | Quantization | Haystack component | Best for |
|--------|-----------|----------|--------------|---------------------|----------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Single-digit t/s on CPU; higher with GPU offload | CPU, GPU, Apple Silicon, RISC-V | GGUF (1.5–8 bit) | `LlamaCppGenerator` via [`llama-cpp-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/llama_cpp) | Any hardware, maximum portability |
| [Ollama](https://github.com/ollama/ollama) | Same as llama.cpp (wraps it) | macOS, Windows, Linux | GGUF via llama.cpp | `OllamaGenerator` / `OllamaChatGenerator` via [`ollama-haystack`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ollama) — **series reference** | Developer workstations, quick setup |
| [vLLM](https://github.com/vllm-project/vllm) | State-of-the-art batch throughput via PagedAttention | NVIDIA GPU primary; AMD, Apple Silicon, x86 CPU | GPTQ, AWQ, GGUF, FP8, INT4 | `OpenAIGenerator` pointed at vLLM's OpenAI-compatible endpoint (`base_url="http://localhost:8000/v1"`) | Multi-user, production GPU servers |
| [ExLlamaV2](https://github.com/turboderp/exllamav2) | 257 t/s on RTX 4090 for a 7B model at Q3 | NVIDIA GPU (CUDA required) | EXL2, GPTQ | Custom Component wrapper | Single-GPU, highest single-stream throughput |
| [TGI](https://github.com/huggingface/text-generation-inference) | High via continuous batching | NVIDIA, AMD, Intel, TPU | GPTQ, AWQ, FP8, bitsandbytes | `HuggingFaceTGIGenerator` (deprecated) | Legacy deployments only — now in maintenance mode |

**llama.cpp** ([ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)) is the foundational engine. It runs on virtually any hardware — Apple Silicon via Metal, NVIDIA via CUDA, AMD via HIP, and pure CPU via AVX/AVX2. Layer offloading allows partial GPU acceleration when the model does not fit entirely in VRAM: layers assigned to GPU run at full speed; remaining layers run on CPU. This hybrid mode makes it uniquely suited to air-gapped deployments where hardware is fixed and unpredictable.

**Ollama** ([ollama/ollama](https://github.com/ollama/ollama)) wraps llama.cpp with a model registry and a REST API at `localhost:11434`. `ollama run qwen2.5:7b` downloads the GGUF model, starts the server, and exposes an OpenAI-compatible endpoint. The simplicity cost is control: Ollama manages model loading and parameters, offering fewer tuning knobs than llama.cpp directly.

**vLLM** ([vllm-project/vllm](https://github.com/vllm-project/vllm)) is the right choice for multi-user deployments. [PagedAttention](https://arxiv.org/abs/2309.06180) eliminates memory fragmentation, enabling continuous batching across concurrent requests. It supports over 200 model architectures and all major quantization formats. For a single developer, it is over-engineered; for ten concurrent RAG users on a shared GPU server, it is the correct default.

**ExLlamaV2** ([turboderp/exllamav2](https://github.com/turboderp/exllamav2)) delivers the highest single-stream token throughput on consumer NVIDIA GPUs via its EXL2 quantization format. It is NVIDIA-only (CUDA required) and best suited to single-user deployments where maximizing response speed matters more than concurrent request handling.

**TGI** ([huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference)) was a widely cited production engine but is now in maintenance mode. The TGI project now recommends vLLM and [SGLang](https://github.com/sgl-project/sglang) for new deployments. Avoid starting new air-gapped deployments on TGI.

---

## Quantization Format Comparison

Quantization reduces model weight precision to fit larger models into available memory. The four formats in active use trade memory against inference quality and hardware dependency.

| Format | Bit depths | Memory savings | Engine support | Hardware requirement |
|--------|-----------|----------------|----------------|---------------------|
| GGUF | 1.5–8 bit | Up to ~75% vs FP16 | llama.cpp, Ollama, vLLM | CPU or any GPU |
| AWQ | 4-bit INT (FP16 compute) | ~75% vs FP16; 3× stated | vLLM, AutoAWQ | GPU (CUDA 11.8+, Compute Cap 7.5+) |
| GPTQ | 2–8 bit | 75–87% vs FP16 | vLLM, ExLlamaV2, AutoGPTQ | GPU |
| EXL2 | 2–8 bit (mixed per-layer) | Variable; adaptive | ExLlamaV2 | NVIDIA GPU (CUDA) |

**GGUF** is the standard format for air-gapped deployments without a dedicated GPU. It runs on CPU and supports hybrid CPU+GPU inference when partial VRAM is available. The naming convention encodes quantization level: `Q4_K_M` means 4-bit with K-quants medium quality; `Q8_0` is 8-bit, near-lossless. For a given model, higher Q values give better quality at higher memory cost. [llama.cpp](https://github.com/ggerganov/llama.cpp) is the reference implementation.

**AWQ** (Activation-Aware Weight Quantization) stores weights in INT4 but dequantizes to FP16 during inference. The [MIT-developed](https://github.com/mit-han-lab/llm-awq) approach delivers 2.7× speedup over FP16 on an RTX 4090 for LLaMA-3-8B. The dequantization overhead flips: at small batch sizes (typical for RAG), AWQ is faster than FP16; at large batches (compute-bound), FP16 has the edge. GPU required; CPU-only deployments cannot use AWQ.

**GPTQ** (Generative Pre-trained Transformer Quantization) calibrates quantization against a small dataset to minimize error introduced per layer. EXL2 is based on the same optimization method as GPTQ but applies mixed precision per layer — important weights receive more bits, per the [ExLlamaV2 documentation](https://github.com/turboderp/exllamav2). The result: a 70B model at 2.55 bits-per-weight fits on a single 24GB GPU and produces coherent output.

**EXL2** is the format to choose when you have a single NVIDIA GPU and want maximum single-stream throughput for one user. ExLlamaV2 at Q3 achieves 257 t/s for a 7B model on an RTX 4090, per the [ExLlamaV2 project README](https://github.com/turboderp/exllamav2). Controlled head-to-head comparisons against llama.cpp at the same precision on the same hardware are scarce; treat EXL2's speed advantage as context-dependent rather than a universal multiplier.

---

## Hardware Sizing by Tier

Match model size and quantization to your hardware tier. The numbers below are practical starting points.

| Tier | Hardware example | Viable model size | Recommended format | Engine |
|------|-----------------|------------------|--------------------|--------|
| Laptop (no GPU) | 16 GB RAM, CPU only | 7B Q4 | GGUF Q4_K_M | llama.cpp or Ollama |
| Workstation (consumer GPU) | 24 GB VRAM (RTX 3090/4090) | 13–30B Q5, or 70B at EXL2 ~2.5 bpw | GGUF Q5_K_M or EXL2 | llama.cpp, ExLlamaV2 |
| Single-GPU server | 80 GB VRAM (A100/H100) | 70B Q4 or 70B FP16 | GGUF or AWQ | vLLM |
| Multi-GPU server | 2–8× GPU | 70B+ FP16, 405B quantized | FP16 or AWQ | vLLM with tensor parallelism |

For RAG answer synthesis, 7B Q4 on a laptop produces usable quality for internal queries over well-structured documents. Quality gaps appear on ambiguous queries where the model must reconcile conflicting retrieved passages; moving to a larger model (13B+ or 30B) at the same quantization generally helps, though the size of the gain depends on the retriever and the reranking stage. Evaluate on your own query set before committing to a hardware tier.

---

## Context Window Budget

A model's context window must accommodate system prompt, retrieved chunks, and output space. Budget these explicitly.

For a 128K context model ([Llama 3.1](https://github.com/meta-llama/llama3), [Qwen 2.5](https://github.com/QwenLM/Qwen2.5)):

| Slot | Typical token budget | Notes |
|------|---------------------|-------|
| System prompt | 500–1,000 | Role, output format instructions |
| Retrieved chunks | 10,000–40,000 | 5–20 chunks × 500–2,000 tokens each |
| Query + conversation history | 500–2,000 | Grows with multi-turn |
| Output buffer | 1,000–4,000 | Leave room for the answer |

The retrieved chunk budget is the primary variable. A conservative deployment uses 10 chunks of 500 tokens (5,000 tokens), leaving most of the window available. An aggressive deployment injects 20 chunks of 2,000 tokens (40,000 tokens), which requires a model with reliable long-context performance — not all quantized models at aggressive bit depths retain full attention at long context.

For models with 4K context (Llama 2, older Mistral), retrieved content must fit in roughly 2,000–3,000 tokens: 3–6 short chunks maximum. Prefer 128K-context models for RAG unless hardware forces otherwise.

---

## Batching and Concurrency

Single-user and multi-user deployments have structurally different requirements.

**Single-user**: llama.cpp and Ollama are sufficient. Requests arrive serially; no batching needed. ExLlamaV2 maximizes per-request speed if you have an NVIDIA GPU.

**Multi-user (concurrent requests)**: vLLM's PagedAttention and continuous batching are purpose-built for this scenario. Under concurrent load, a naive engine queues requests and processes them serially — throughput per user degrades linearly with concurrency. vLLM maintains near-constant per-user latency up to a hardware-determined saturation point by filling batches with tokens from multiple requests simultaneously.

---

## Hands-On: Full RAG Pipeline with OllamaGenerator

`qwen2.5:7b` is the generation model in the series [reference stack](index.md#reference-stack) — it trades sensibly against RAG quality for structured document Q&A while fitting on a single 16 GB VRAM GPU at Q4_K_M.

### Bring up Ollama

```bash
# Pull and run — Ollama downloads the GGUF model on first call.
# Pre-download on a network-connected host before air-gapping.
ollama run qwen2.5:7b
```

Ollama stores models in `~/.ollama/models`. In a fully air-gapped environment, pre-download the GGUF file, place it in that directory, and import it with `ollama create <name> --file <modelfile>`. Set `OLLAMA_MODELS` to a controlled path if you need the store somewhere other than the home directory.

### Extend the query pipeline with PromptBuilder + OllamaGenerator

Take the hybrid retrieval + reranking pipeline from [Module 6](retrieval-and-reranking.md) and extend it with a prompt builder and generator. The result is the full query-side pipeline the series targets — ~40 lines of component declarations and connections:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import (
    SentenceTransformersTextEmbedder,
    SentenceTransformersSparseTextEmbedder,
)
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import SentenceTransformersSimilarityRanker
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import (
    QdrantEmbeddingRetriever,
    QdrantSparseEmbeddingRetriever,
)
from haystack_integrations.components.generators.ollama import OllamaGenerator

PROMPT_TEMPLATE = """\
Answer the question using only the numbered sources below. Cite every fact with [N].
If no source supports the answer, reply: "Insufficient context." Do not use any
information that is not in the sources.

{% for doc in documents %}
[{{ loop.index }}] {{ doc.content }}
{% endfor %}

Question: {{ query }}
Answer:"""

document_store = QdrantDocumentStore(
    path="/data/qdrant_db",
    index="documents",
    embedding_dim=768,
    use_sparse_embeddings=True,
    recreate_index=False,
)

rag = Pipeline()
rag.add_component("dense_query", SentenceTransformersTextEmbedder(
    model="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"trust_remote_code": True},
    device="cpu",
))
rag.add_component("sparse_query", SentenceTransformersSparseTextEmbedder(
    model="prithivida/Splade_PP_en_v1", device="cpu",
))
rag.add_component("dense_retriever", QdrantEmbeddingRetriever(
    document_store=document_store, top_k=20,
))
rag.add_component("sparse_retriever", QdrantSparseEmbeddingRetriever(
    document_store=document_store, top_k=20,
))
rag.add_component("joiner", DocumentJoiner(
    join_mode="reciprocal_rank_fusion", top_k=20,
))
rag.add_component("ranker", SentenceTransformersSimilarityRanker(
    model="BAAI/bge-reranker-v2-m3", top_k=5, device="cpu",
))
rag.add_component("prompt", PromptBuilder(template=PROMPT_TEMPLATE))
rag.add_component("llm", OllamaGenerator(
    model="qwen2.5:7b",
    url="http://localhost:11434",
    generation_kwargs={
        "temperature": 0.1,   # deterministic for RAG Q&A
        "num_predict": 512,   # cap the answer length
        "num_ctx": 8192,      # context window (tokens)
    },
))

rag.connect("dense_query.embedding", "dense_retriever.query_embedding")
rag.connect("sparse_query.sparse_embedding", "sparse_retriever.query_sparse_embedding")
rag.connect("dense_retriever.documents", "joiner.documents")
rag.connect("sparse_retriever.documents", "joiner.documents")
rag.connect("joiner.documents", "ranker.documents")
rag.connect("ranker.documents", "prompt.documents")
rag.connect("prompt.prompt", "llm.prompt")

query = "Which contracts have arbitration clauses expiring before 2027?"
result = rag.run({
    "dense_query":  {"text": query},
    "sparse_query": {"text": query},
    "ranker":       {"query": query},
    "prompt":       {"query": query},
})
print(result["llm"]["replies"][0])
```

`pipeline.dumps()` serializes this graph to ~80 lines of YAML — the audit artifact that accompanies every signed release. The YAML names every Component class, its parameters, and the wiring between them.

### Binding and air-gap verification

By default Ollama binds to `0.0.0.0:11434`, exposing its API on every network interface. Two correct configurations:

- **Bare-metal host**: set `OLLAMA_HOST=127.0.0.1:11434` to restrict the API to localhost. A second process on the same host can still reach it; a peer on the LAN cannot. Haystack's `OllamaGenerator(url="http://localhost:11434")` resolves `localhost` to the loopback interface, which matches the bound address.
- **Container**: keep the default `0.0.0.0` binding *inside* the container, and do not publish the port to the host (omit `-p 11434:11434` or set `ports` to an internal-only mapping in docker-compose). The container network boundary replaces the localhost boundary — other services on the same compose network reach Ollama, the host does not expose it. In this configuration, pass `url="http://llm:11434"` (the compose service name) to the `OllamaGenerator`.

Audit bindings after start: `ss -tlnp | grep 11434`.

### Swapping Ollama for vLLM without rewriting the pipeline

`OllamaGenerator` and vLLM's OpenAI-compatible endpoint are interchangeable from the Haystack pipeline's perspective. To switch to a production vLLM deployment, replace one component:

```python
from haystack.components.generators import OpenAIGenerator

# Remove OllamaGenerator, add OpenAIGenerator pointed at the local vLLM server
rag.remove_component("llm")
rag.add_component("llm", OpenAIGenerator(
    model="Qwen/Qwen2.5-7B-Instruct-AWQ",
    api_base_url="http://localhost:8000/v1",
    api_key="unused",   # required field, vLLM ignores it
    generation_kwargs={"temperature": 0.1, "max_tokens": 512},
))
rag.connect("prompt.prompt", "llm.prompt")
```

No other component changes. Indexing pipeline untouched. Every downstream module (grounding, evaluation, deployment) works the same way with either backend.

### Using the same model for HyDE

If Module 6 enabled HyDE for vague query expansion, the same Ollama instance serves both roles — instantiate a second `OllamaGenerator` with `generation_kwargs={"num_predict": 200, "temperature": 0.3}` (shorter, slightly more creative) and wire it into a pre-retrieval sub-pipeline that feeds the hypothetical answer into the text embedders instead of the raw query. Reusing one Ollama model keeps memory pressure predictable and avoids doubling the VRAM budget.

---

## Key Takeaways

- Match engine to deployment shape: llama.cpp/Ollama for portability and CPU-compatible hardware, vLLM for multi-user GPU servers, ExLlamaV2 for single-user maximum throughput on NVIDIA
- GGUF is the default format for air-gapped deployments — it runs on CPU, supports hybrid CPU+GPU, and covers the widest hardware range; AWQ and EXL2 require a capable GPU but deliver better throughput when one is available
- TGI is in maintenance mode — avoid it for new deployments; vLLM is the production-grade successor
- Budget context explicitly: system prompt + retrieved chunks + output space must fit within the model's context limit; for RAG, 128K-context models (Llama 3.1, Qwen 2.5) give significant headroom over 4K models
- Quantization at Q4 sacrifices some quality but enables models two to three times larger than FP16 on the same hardware; for RAG over structured documents, the quality tradeoff is usually acceptable
- For multi-user deployments, vLLM's continuous batching is not optional — without it, concurrency degrades throughput linearly
- In Haystack, the choice between Ollama and vLLM is a one-component edit: `OllamaGenerator` and `OpenAIGenerator` (pointed at vLLM's OpenAI-compatible endpoint) slot into the same pipeline graph. Swap the component, re-dump the YAML, re-sign the artifact — every other stage stays identical

## Related

- [Air-Gapped RAG: Retrieval and Re-Ranking](retrieval-and-reranking.md)
- [Air-Gapped RAG: Grounding, Citations, and Evaluation](grounding-citations-evaluation.md)
- [Air-Gapped RAG: Document Ingestion and Parsing](document-ingestion-and-parsing.md)
