---
title: "Typed Generation Contracts for Grounded Extraction"
term: "Typed Generation Contract"
description: "Split a wrong grounded answer into context-sufficient and context-insufficient failures first, then make the extraction half checkable with typed fields, verbatim evidence spans, and a validator that runs."
tags:
  - testing-verification
  - tool-agnostic
  - rag
  - arxiv
last_reviewed: 2026-07-28
maturity: emerging
aliases:
  - generation contract
---

# Typed Generation Contracts for Grounded Extraction

> Split a wrong grounded answer by whether the context held it, then make the extraction half checkable with typed fields and verbatim evidence spans.

## Split the failure before you pick a fix

A wrong answer from a retrieval-grounded step belongs to one of two classes, and they have opposite fixes. Either the retrieved context contained the answer and the step still emitted the wrong value, or the context never contained it. Better retrieval fixes the second and does nothing for the first. A typed output contract fixes the first and cannot manufacture what retrieval failed to deliver.

Both classes are large, so the split is worth measuring rather than assuming. [Joren et al.](https://arxiv.org/abs/2411.06037) formalize the test as a "sufficient context" autorater — an automated judge that decides whether the answer is inferable from the retrieved passages alone — and report 54.8% of their instances as context-sufficient against 45.2% insufficient. Within the sufficient half, strong models still err: Gemini 1.5 Pro answered 84.1% correctly, abstained 1.6% of the time, and hallucinated 14.3%; GPT-4o scored 82.5 / 4.8 / 12.7 and Claude 3.5 Sonnet 85.7 / 11.1 / 3.2.

Do not carry the stronger claim that most grounded hallucinations are extraction errors. [RAGTruth](https://arxiv.org/abs/2401.00396), a corpus of roughly 18,000 responses annotated span by span, separates content that conflicts with the context from content baseless in it and finds that for question answering "the generation of information baseless in the context was significantly more prevalent than the generation of information conflicting." Mis-extraction is a real and addressable class. It is not established as the dominant one.

## What the contract declares

A typed generation contract makes each emitted field carry three things instead of a bare value ([Towards Data Science](https://towardsdatascience.com/most-rag-hallucinations-are-extraction-errors-seven-patterns-for-a-typed-generation-contract/)):

- A declared type, so a duration parses as a duration and an amount carries its currency and unit.
- An evidence span — the line range in the source document plus the verbatim quote the value came from.
- Explicit nullability, as separate flags for whether an answer was found at all and whether it was found completely.

The contract only pays off when a validator actually runs against it. That validator checks that cited line spans fall inside the document's bounds, that the quoted text matches those lines verbatim, and that each value parses under its declared format. Skip the validator and the structure signals a verification that never happens.

## Why it works

The contract converts an unverifiable claim into one with a machine-checkable postcondition. Free text can only be checked semantically, which means running another model and inheriting its error rate. A typed value plus a line range plus a verbatim quote can be checked with a range comparison and a string containment test.

Two independent results show why the mechanical step, not the schema, carries the weight. Self-reported citations are unreliable when nothing checks them: on the ELI5 dataset in the [ALCE benchmark](https://arxiv.org/abs/2305.14627), even the best models lacked complete citation support 50% of the time. And once grounding is annotated at span level it becomes learnable — the RAGTruth authors fine-tuned a comparatively small model to hallucination-detection performance competitive with prompt-based GPT-4 ([Niu et al.](https://arxiv.org/abs/2401.00396)). The span makes the failure addressable; the type makes the check cheap.

## When this backfires

- Retrieval is the actual bottleneck. Where the answer was never retrieved, the contract reports "not found" at best and fabricates a span at worst. [Joren et al.](https://arxiv.org/abs/2411.06037) put that case at 45.2% of instances.
- The field requires inference rather than lookup. A derived rate or a normalized category has no verbatim span to point at, and [Tam et al.](https://arxiv.org/abs/2408.02442) find a significant decline in reasoning ability under format restrictions, with stricter constraints degrading more.
- You lean on the model's own not-found flag as the abstention gate. Models abstain rarely even when they should — 1.6% to 11.1% on context-sufficient cases and 50% to 61.5% on insufficient ones ([Joren et al.](https://arxiv.org/abs/2411.06037)) — so the flag under-reports absence.
- The validator is never built. A self-reported span that nothing checks carries ALCE's failure rate under the appearance of provenance.
- Extraction volume is low. Schema design, span plumbing, and validator maintenance are fixed costs that hand inspection can undercut.

## Example

Any agent step that reads a tool response and emits a structured field is doing extraction, so the contract applies to tool-result parsing as much as to document question answering.

An agent asked which test failed can return a bare conclusion, which nothing downstream can check:

```json
{ "failing_test": "test_auth_expiry" }
```

Under a typed generation contract the same step must cite where it read that, and declare absence explicitly:

```json
{
  "failing_test": "test_auth_expiry",
  "evidence": { "line_start": 1187, "line_end": 1187,
                "quote": "FAILED tests/test_auth.py::test_auth_expiry" },
  "answer_found": true,
  "complete_answer_found": false
}
```

A validator now confirms line 1187 exists in the captured log and that the quoted string appears there verbatim. A fabricated test name fails the containment check without any model in the loop, and the false `complete_answer_found` flag tells the caller that other failures may remain unreported.

## Key Takeaways

- Classify a wrong grounded answer by context sufficiency first, because retrieval fixes and extraction fixes solve different halves.
- Both halves are large — the Joren et al. sample split 54.8% sufficient against 45.2% insufficient, and strong models still hallucinated inside the sufficient half.
- The claim that most grounded hallucinations are extraction errors is not established — RAGTruth finds baseless content outweighing context conflict in question answering.
- A typed generation contract declares a type, a verbatim evidence span, and explicit nullability per field.
- The validator is the load-bearing part — a declared contract nobody checks buys the appearance of provenance, not the substance.
- Do not use the contract on inference-bearing fields or as a substitute for an abstention gate the model cannot reliably drive.

## Related

- [Structured Output Constraints: Reducing Hallucination Surface](structured-output-constraints.md) — the general case for schemas over free text; this page narrows it to the extraction step and adds provenance
- [Generative Provenance Records for Tool-Using Agents](generative-provenance-records.md) — the same evidence-span idea applied per output sentence across a tool trajectory
- [Per-Line Requirement Citations for Hallucination Detection](per-line-requirement-citations.md) — the code-generation counterpart, citing requirement IDs instead of document spans
- [RAG/Agent Reliability Problem Map](rag-agent-reliability-problem-map.md) — the wider failure taxonomy this diagnostic slots into
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — why the validator, not the schema, is what makes the contract hold
