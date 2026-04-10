---
title: "Air-Gapped RAG: Grounding, Citations, and Evaluation"
description: "Enforce grounded answers with citation requirements, detect ungrounded claims with offline entailment checks, and build a measurable quality loop using local LLM judges and golden query sets."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
---

# Air-Gapped RAG: Grounding, Citations, and Evaluation

> Without grounding enforcement and offline evaluation, an air-gapped RAG system produces confident hallucinations with no mechanism to detect or measure them.

This module covers the three-layer quality loop that makes air-gapped RAG output auditable: grounding prompts that force citation, post-generation entailment checks that detect ungrounded claims, and an offline eval pipeline using local judge models. Because air-gapped environments (regulated, classified) cannot route data to cloud eval services, every component in this loop runs entirely offline. Runnable code uses Haystack's built-in evaluators — `FaithfulnessEvaluator`, `ContextRelevanceEvaluator`, `LLMEvaluator`, and the document-ranking evaluators — backed by the same local `OllamaGenerator` used for answer synthesis.

---

## Layer 1: Grounding Prompts

The generation model produces hallucinations when retrieved context is insufficient and it falls back to training-data priors. Two prompt-level constraints prevent this.

### Structured Output as the Contract

Free-text responses with inline `[1]` references require parsing before verification. Structured JSON output separates the answer from its citation list and enables programmatic entailment checking without fragile text parsing. The whole module uses one contract:

```python
from pydantic import BaseModel

class Citation(BaseModel):
    chunk_id: int     # 1-indexed, matches the [N] in the SOURCES block
    quote: str        # verbatim span from the chunk that supports the claim

class GroundedAnswer(BaseModel):
    answer: str | None         # None when refused
    citations: list[Citation]  # empty when refused
    refused: bool = False      # True when no chunk supports an answer
    refusal_reason: str | None = None  # e.g., "insufficient_context"
```

Request this schema in Haystack by configuring [`OllamaGenerator`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ollama) with `generation_kwargs={"format": GroundedAnswer.model_json_schema()}` — Ollama validates the JSON output against the [Pydantic](https://github.com/pydantic/pydantic) schema and retries on failure. Alternative: use Haystack's `JsonSchemaValidator` component downstream of the generator to re-ask up to N times on malformed output. [Unverified: all Ollama model versions support Pydantic schema enforcement equally — verify against the specific model you serve.]

### Require Citations in Every Response

Instruct the model to attribute every claim to a specific retrieved chunk. The system prompt references the `GroundedAnswer` contract above:

```
SYSTEM:
You are a document question-answering assistant.
Rules:
1. Return a JSON object matching this schema:
   {
     "answer": str | null,
     "citations": [{"chunk_id": int, "quote": str}, ...],
     "refused": bool,
     "refusal_reason": str | null
   }
2. Answer only using the provided source chunks.
3. Every factual sentence in `answer` must have at least one entry in `citations`
   whose `chunk_id` is the source and whose `quote` is a verbatim span from that chunk.
4. If no chunk contains relevant information, return:
   {"answer": null, "citations": [], "refused": true,
    "refusal_reason": "insufficient_context"}
5. Do not add information from outside the provided chunks.

SOURCES:
[1] {chunk_1_text}
[2] {chunk_2_text}
[3] {chunk_3_text}

USER: {query}
```

This forces the model to trace each claim to a chunk at generation time rather than mixing retrieved facts with training priors.

### Refusal Threshold

When retrieved chunks do not contain relevant information, the model should refuse rather than speculate. Two mechanisms complement each other:

**Retrieval-side**: Filter out any chunk whose similarity score falls below a threshold before populating the context window. If no chunks pass the threshold, skip generation entirely and return the structured refusal directly.

**Prompt-side**: Even above-threshold chunks may not answer the specific question. The system prompt rule above instructs the model to refuse explicitly rather than construct a plausible-sounding answer from tangential chunks.

Calibrate the similarity threshold against your golden query set (see Layer 3). Too low: irrelevant chunks enter the context and increase hallucination. Too high: legitimate queries are refused.

---

## Layer 2: Post-Generation Faithfulness Checking

The grounding prompt reduces hallucination but does not eliminate it — models occasionally cite a chunk number without the claim actually appearing in that chunk. A post-generation faithfulness check catches this mechanically. Haystack ships two evaluators that cover this layer end-to-end: `FaithfulnessEvaluator` (LLM-as-judge against a local generator) and a custom NLI-based component for deterministic alternatives.

### FaithfulnessEvaluator backed by a local judge

`FaithfulnessEvaluator` is an `LLMEvaluator` subclass that asks a judge model: "for each statement in the prediction, is it supported by at least one of the context documents?" It scores each statement and returns a fractional faithfulness score per query.

The built-in evaluator's default generator is OpenAI. For offline use, pass a local `OllamaGenerator` as the `chat_generator` argument — the evaluator delegates all judge calls to that component, so no network access occurs:

```python
from haystack.components.evaluators import FaithfulnessEvaluator
from haystack_integrations.components.generators.ollama import OllamaChatGenerator

judge = OllamaChatGenerator(
    model="qwen2.5:7b",
    url="http://localhost:11434",
    generation_kwargs={"temperature": 0.0, "num_predict": 256},
)

faithfulness = FaithfulnessEvaluator(chat_generator=judge)

result = faithfulness.run(
    questions=[query],
    contexts=[[doc.content for doc in retrieved_documents]],
    predicted_answers=[generated_answer],
)
print(f"faithfulness: {result['individual_scores'][0]:.2f}")
```

The score is the fraction of statements in the prediction that the judge confirms as grounded in the context. Log the per-statement breakdown (`result["results"]`) to see exactly which claims the judge flagged as ungrounded.

### NLI alternative for deterministic scoring

A smaller, faster alternative is a Natural Language Inference (NLI) cross-encoder wrapped as a custom Haystack component. This runs in CPU-bounded milliseconds and is fully deterministic, at the cost of narrower semantic coverage than an LLM judge:

```python
from haystack import component, Document
from sentence_transformers import CrossEncoder

@component
class NLIFaithfulnessEvaluator:
    """
    Score each (claim, chunk) pair via an NLI cross-encoder.
    Returns fraction of claims entailed by at least one cited chunk.
    """
    # https://huggingface.co/cross-encoder/nli-deberta-v3-small
    # id2label: {0: "contradiction", 1: "entailment", 2: "neutral"}
    LABELS = ["contradiction", "entailment", "neutral"]
    ENTAILMENT_IDX = 1

    def __init__(self, model: str = "cross-encoder/nli-deberta-v3-small"):
        self.model = CrossEncoder(model)

    @component.output_types(score=float, per_claim=list[bool])
    def run(self, claims: list[str], contexts: list[list[Document]]) -> dict:
        per_claim: list[bool] = []
        for claim, chunks in zip(claims, contexts):
            texts = [chunk.content for chunk in chunks]
            logits = self.model.predict([(text, claim) for text in texts])
            labels = logits.argmax(axis=1)
            per_claim.append(any(label == self.ENTAILMENT_IDX for label in labels))
        score = sum(per_claim) / len(per_claim) if per_claim else 0.0
        return {"score": score, "per_claim": per_claim}
```

Two things this component gets right that a naive first pass often does not: `logits.argmax(axis=1)` returns a label per (chunk, claim) pair (a flat `.argmax()` on the 2D matrix returns a single scalar into the flattened array — silently wrong), and `ENTAILMENT_IDX = 1` matches `nli-deberta-v3` ordering rather than assuming `entailment` is the last index.

**Verify `id2label` against the specific model version you use before trusting this ordering** — different NLI checkpoints use different label orders, and a silent swap of `entailment` and `neutral` produces faithfulness scores that look plausible but are inverted.

### Integration Point

Run either evaluator as a post-generation filter before returning the answer to the caller. Log all below-threshold results with the chunk IDs, claim text, and query — this data feeds directly into your golden query set (see Layer 3).

For production systems in regulated environments, surface flagged results to the reviewer interface rather than silently suppressing them. The user should know when a claim could not be verified against the retrieved context.

---

## Layer 3: Offline Evaluation with a Local Judge

A golden query set with a measurable quality loop detects regression after prompt changes, model upgrades, or corpus updates. Because data cannot leave the air-gapped environment, all eval components run offline.

### Building the Golden Query Set

Start with 20 queries sourced from:

- **Real failure cases**: queries where your system produced a wrong or refused answer during testing — the highest-signal inputs because they represent proven failure modes
- **Known-answer queries**: questions with a verifiable correct answer in your document corpus — enables automatic grading without a judge
- **Boundary queries**: queries that should trigger refusal (topic not covered in corpus) and queries that should be answered (topic clearly present)

Each entry in the golden set has:

```yaml
- id: doc-policy-section-4
  query: "What is the data retention period for audit logs?"
  expected_answer: "90 days"          # for known-answer grading
  should_refuse: false
  relevant_chunks: [12, 13]           # chunk IDs that contain the answer
```

The `relevant_chunks` field enables context precision and context recall scoring independently of the generation step — you can verify retrieval quality without running the generation model.

### Haystack Evaluators (primary path)

Haystack 2.x ships a set of first-class evaluators covering every RAG quality metric. Each evaluator is a Component that runs offline against a local judge generator or an embedding model:

| Haystack evaluator | What it measures | Judge required |
|---|---|---|
| `FaithfulnessEvaluator` | Fraction of answer statements supported by context | LLM (local `OllamaChatGenerator`) |
| `ContextRelevanceEvaluator` | Fraction of context chunks relevant to the query | LLM (local `OllamaChatGenerator`) |
| `SASEvaluator` (Semantic Answer Similarity) | Embedding-cosine between predicted and ground-truth answers | Embedding model (local `SentenceTransformers`) |
| `DocumentNDCGEvaluator` | Ranking quality of retrieved documents vs. ground truth | None — deterministic |
| `DocumentMRREvaluator` | Mean reciprocal rank of first relevant document | None — deterministic |
| `DocumentMAPEvaluator` | Mean average precision across retrieved documents | None — deterministic |
| `AnswerExactMatchEvaluator` | Exact string match against ground-truth answer | None — deterministic |
| `LLMEvaluator` | Arbitrary custom judge prompt with structured output | LLM (local `OllamaChatGenerator`) |

Wire them into a Haystack evaluation pipeline that runs alongside your golden query set:

```python
from haystack import Pipeline
from haystack.components.evaluators import (
    FaithfulnessEvaluator,
    ContextRelevanceEvaluator,
    DocumentNDCGEvaluator,
    SASEvaluator,
)
from haystack_integrations.components.generators.ollama import OllamaChatGenerator

judge = OllamaChatGenerator(
    model="qwen2.5:7b",
    url="http://localhost:11434",
    generation_kwargs={"temperature": 0.0, "num_predict": 256},
)

eval_pipeline = Pipeline()
eval_pipeline.add_component("faithfulness", FaithfulnessEvaluator(chat_generator=judge))
eval_pipeline.add_component("context_relevance", ContextRelevanceEvaluator(chat_generator=judge))
eval_pipeline.add_component("ndcg", DocumentNDCGEvaluator())
eval_pipeline.add_component("sas", SASEvaluator(
    model="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu",
))

# Run the RAG pipeline first to get predictions, then feed them into the evaluators
questions = [item["query"] for item in golden_set]
ground_truth_answers = [item["expected_answer"] for item in golden_set]
ground_truth_documents = [item["relevant_chunks"] for item in golden_set]

# Collect pipeline outputs for each query
predicted_answers, retrieved_documents = [], []
for item in golden_set:
    result = rag.run({
        "dense_query":  {"text": item["query"]},
        "sparse_query": {"text": item["query"]},
        "ranker":       {"query": item["query"]},
        "prompt":       {"query": item["query"]},
    })
    predicted_answers.append(result["llm"]["replies"][0])
    retrieved_documents.append(result["ranker"]["documents"])

scores = eval_pipeline.run({
    "faithfulness":      {"questions": questions,
                          "contexts":  [[d.content for d in docs] for docs in retrieved_documents],
                          "predicted_answers": predicted_answers},
    "context_relevance": {"questions": questions,
                          "contexts":  [[d.content for d in docs] for docs in retrieved_documents]},
    "ndcg":              {"ground_truth_documents": ground_truth_documents,
                          "retrieved_documents":    retrieved_documents},
    "sas":               {"ground_truth_answers": ground_truth_answers,
                          "predicted_answers":    predicted_answers},
})

print(f"faithfulness      : {scores['faithfulness']['score']:.3f}")
print(f"context_relevance : {scores['context_relevance']['score']:.3f}")
print(f"nDCG@10           : {scores['ndcg']['score']:.3f}")
print(f"SAS               : {scores['sas']['score']:.3f}")
```

Store results in a local time-series file (JSON or CSV). Compare the current run against the previous baseline. Gate releases on a minimum faithfulness threshold — 0.80 is a reasonable starting point for regulated environments; raise it as your corpus and prompts stabilize. Serialize the evaluation pipeline to YAML (`eval_pipeline.dumps()`) and commit it alongside the indexing and query pipelines — three YAML files capture the entire RAG system state.

### RAGAs (alternative path)

[RAGAs](https://github.com/explodinggradients/ragas) is a mature evaluation framework with overlapping metrics. By default, RAGAs uses OpenAI as the LLM judge. For offline use, RAGAs supports [HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model) — a free, open-source T5 classifier deployable entirely locally — as the faithfulness judge. [RAGAs faithfulness documentation](https://github.com/explodinggradients/ragas/blob/main/docs/concepts/metrics/available_metrics/faithfulness.md). The exact integration class and import path depend on your RAGAs version [unverified — consult the current RAGAs source for the precise API]; the model itself loads via HuggingFace and runs on CPU with `device="cpu"`.

Use RAGAs when you want HHEM-2.1-Open specifically (the Haystack built-ins do not ship this judge out of the box), or when you are comparing against a team already using RAGAs in a non-air-gapped environment and want comparable numbers. For greenfield deployments the Haystack built-ins are the simpler path.

### Trade-offs: Local Judge vs. Cloud Judge

A local 7B or small classifier judge does not match GPT-4 accuracy. Accept this trade-off explicitly: the goal is a consistent, reproducible signal for regression detection, not absolute accuracy. A faithfulness score that decreases from 0.87 to 0.71 across a prompt change is actionable even if the absolute value is not calibrated to human judgment.

To calibrate your local judge, manually score 20–30 (claim, chunk) pairs and compare against the judge's output. If local and human labels agree on ≥80% of cases, the judge is reliable enough for regression tracking.

---

## Example

A minimal grounding and eval loop for a 20-query golden set against the series [reference stack](index.md#reference-stack). The query pipeline is the one from [Module 7](local-llm-inference.md#extend-the-query-pipeline-with-promptbuilder--ollamagenerator); the evaluation pipeline runs a `FaithfulnessEvaluator` over its outputs using the same `OllamaChatGenerator` as judge.

**Golden set format:**

```yaml
# golden_set.yaml — version-controlled alongside the pipelines
- id: doc-policy-section-4
  query: "What is the data retention period for audit logs?"
  expected_answer: "90 days"
  should_refuse: false
  relevant_chunks: ["12", "13"]    # chunk IDs that contain the answer
- id: out-of-scope-query
  query: "Who wrote the constitution?"
  expected_answer: null
  should_refuse: true
  relevant_chunks: []
```

**Run the RAG pipeline and evaluate with Haystack:**

```python
import yaml
from haystack import Pipeline
from haystack.components.evaluators import FaithfulnessEvaluator, DocumentNDCGEvaluator
from haystack.dataclasses import Document
from haystack_integrations.components.generators.ollama import OllamaChatGenerator

# Load golden set
with open("golden_set.yaml") as f:
    golden = yaml.safe_load(f)

# Load the RAG query pipeline from YAML (built in Module 7)
with open("pipelines/query.yaml") as f:
    rag = Pipeline.loads(f.read())

# Load the document store so we can hydrate the ground-truth chunk IDs
document_store = rag.get_component("dense_retriever").document_store

# Run the RAG pipeline over every query
questions, predicted_answers, retrieved_documents, ground_truth_documents = [], [], [], []
for item in golden:
    if item["should_refuse"]:
        continue   # refusal cases are scored separately below
    result = rag.run({
        "dense_query":  {"text": item["query"]},
        "sparse_query": {"text": item["query"]},
        "ranker":       {"query": item["query"]},
        "prompt":       {"query": item["query"]},
    })
    questions.append(item["query"])
    predicted_answers.append(result["llm"]["replies"][0])
    retrieved_documents.append(result["ranker"]["documents"])
    # Hydrate ground-truth documents from the store by chunk ID
    gt_docs = document_store.filter_documents(
        filters={"field": "id", "operator": "in", "value": item["relevant_chunks"]},
    )
    ground_truth_documents.append(gt_docs)

# Build the evaluation pipeline
judge = OllamaChatGenerator(
    model="qwen2.5:7b",
    url="http://localhost:11434",
    generation_kwargs={"temperature": 0.0, "num_predict": 256},
)
evaluation = Pipeline()
evaluation.add_component("faithfulness", FaithfulnessEvaluator(chat_generator=judge))
evaluation.add_component("ndcg", DocumentNDCGEvaluator())

scores = evaluation.run({
    "faithfulness": {
        "questions": questions,
        "contexts":  [[d.content for d in docs] for docs in retrieved_documents],
        "predicted_answers": predicted_answers,
    },
    "ndcg": {
        "ground_truth_documents": ground_truth_documents,
        "retrieved_documents":    retrieved_documents,
    },
})

print(f"faithfulness: {scores['faithfulness']['score']:.3f}")
print(f"nDCG@10     : {scores['ndcg']['score']:.3f}")

# Score refusal correctness separately
refusal_correct = 0
for item in golden:
    if not item["should_refuse"]:
        continue
    result = rag.run({
        "dense_query":  {"text": item["query"]},
        "sparse_query": {"text": item["query"]},
        "ranker":       {"query": item["query"]},
        "prompt":       {"query": item["query"]},
    })
    if "insufficient context" in result["llm"]["replies"][0].lower():
        refusal_correct += 1

refusal_cases = sum(1 for item in golden if item["should_refuse"])
print(f"refusal rate: {refusal_correct}/{refusal_cases}")
```

The whole loop is ~60 lines, and every non-boilerplate line is a Haystack Component invocation. No bespoke entailment math, no hand-rolled NLI label ordering — the evaluators handle both.

---

## Key Takeaways

- Require citations in the system prompt and use structured JSON output via `OllamaGenerator`'s schema-enforcement mode — free-text responses make programmatic verification fragile
- Add a refusal path for both retrieval-side (similarity threshold) and prompt-side (explicit instruction) to prevent speculation from training priors
- Haystack's `FaithfulnessEvaluator` backed by a local `OllamaChatGenerator` judge gives you per-statement grounding scores without writing any entailment code by hand — the custom NLI component is the deterministic alternative when you need reproducible scores at CPU latency
- Golden query sets start at 20 queries sourced from real failures and known-answer cases; `should_refuse` entries verify the refusal path
- Haystack evaluators (`FaithfulnessEvaluator`, `ContextRelevanceEvaluator`, `DocumentNDCGEvaluator`, `SASEvaluator`) cover every RAG quality metric out of the box; RAGAs with HHEM-2.1-Open is the alternative path when you want HHEM specifically
- Gate releases on a minimum faithfulness threshold and store results as a time-series — absolute accuracy matters less than detecting regression direction
- Three YAML files (`indexing.yaml`, `query.yaml`, `evaluation.yaml`) capture the entire system state; commit them alongside the signed container releases

## Unverified Claims

- All Ollama model versions support Pydantic schema enforcement equally — verify against the specific model version you serve before relying on structured output in production.
- Specific CPU throughput of `cross-encoder/nli-deberta-v3-small` for a 20-query eval run — benchmarked on specific hardware not confirmed; test against your target hardware.
- The exact RAGAs integration class/import path for HHEM-2.1-Open as a faithfulness judge varies by version — consult the current RAGAs source for the precise API before using in production.
- Whether [TruLens](https://github.com/truera/trulens)' local provider support covers Ollama-served models directly without an adapter layer — consult TruLens documentation for current provider list.

## Related

- [Architecture Fundamentals](architecture-fundamentals.md) — pipeline stages and the hallucination failure mode at Stage 7
- [Local LLM Inference](local-llm-inference.md) — model selection, quantization, and serving for the generation stage
- [Retrieval and Re-Ranking](retrieval-and-reranking.md) — improving context precision before grounding applies
- [Deployment, Operations, and Compliance](deployment-operations-compliance.md) — operationalizing the eval loop in production
- [Writing Your First Eval Suite](../eval-driven-development/writing-first-eval-suite.md) — golden query set methodology
- [Grading Strategies](../eval-driven-development/grading-strategies.md) — choosing between code-based, LLM-as-judge, and human graders
