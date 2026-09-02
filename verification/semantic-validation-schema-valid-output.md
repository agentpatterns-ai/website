---
title: "Semantic Validation for Schema-Valid Agent Output"
term: "Semantic Validation"
description: "Schema conformance guarantees an agent's JSON parses and types check, and says nothing about the values. Check identifiers against a register, values against a real bound, and fields against each other."
tags:
  - testing-verification
  - tool-agnostic
aliases:
  - post-conformance output validation
  - validation beyond JSON schema
last_reviewed: 2026-09-01
maturity: adopted
---

# Semantic Validation for Schema-Valid Agent Output

> A schema check proves an agent's output parses and types correctly. It proves nothing about the values, so check those separately.

Anthropic's structured-outputs documentation states the guarantee in format terms: responses are "Always valid: No more `JSON.parse()` errors" and "Type safe: Guaranteed field types and required fields" ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). No line claims the values are right, and none could. Constrained decoding shapes the token stream and never consults the world those values describe.

## When a semantic check pays for itself

A post-conformance check works only when it has something to compare a value against. Three anchors qualify:

- A register the process already holds. Package indexes, API catalogs, and customer tables all support a membership test.
- A bound that is real rather than defensive. A transaction date cannot be in the future; a line number cannot exceed the file it cites.
- A second field in the same payload. A total that must equal the sum of its items, or a `status` of `resolved` that requires a non-null `resolution`.

Where none of the three exists, no local check separates a correct answer from a plausible wrong one, so route the record to a human instead.

## Three classes that pass a schema

Invented identifiers are the cleanest case: a fabricated name is a well-formed string, and `type: string` accepts every string. Patil et al. define the test that catches it: "We define a hallucination as an API call that is not a sub-tree of any API in the database — invoking an entirely imagined tool." Measuring APIBench in 2023, they put GPT-4 zero-shot at 36.55% on TorchHub, 37.16% on HuggingFace, and 78.65% on TensorFlow Hub ([Gorilla](https://arxiv.org/abs/2305.15334v1)). Rates move with the model; the class does not. At supply-chain scale, across 576,000 generated code samples, hallucinated package names ran to "at least 5.2% for commercial models and 21.7% for open-source models" ([Spracklen et al.](https://arxiv.org/abs/2406.10279v3)).

Impossible values are the second class, arriving when a required field has no answer in the source. Benjamin Nweke reports models filling a required `transaction_date` with the current date when the source document carries none, and measures the mismatch at "2 to 3% of a given week's volume" ([Towards Data Science](https://towardsdatascience.com/your-llm-can-return-perfect-json-and-still-be-wrong/)).

Inconsistent field pairs are the third: each field is legal alone, the combination is not, and only a rule reading both can see it. An evidence span whose `line_end` precedes its `line_start` is the shape, two valid integers describing an impossible range, and checking cited spans against the document's bounds is exactly the validator a [typed generation contract](typed-generation-contract.md) specifies.

## Why it works

An anchor converts a question no local check can answer into one it can. "Is this the right package?" needs the world; "is this name in the index?" needs a lookup. That substitution is the whole of Patil et al.'s definition, and it is why the check has to be attached to a register rather than reasoned about ([Gorilla](https://arxiv.org/abs/2305.15334v1)).

The second half is the feedback channel. Olausson et al. found that "self-repair is bottlenecked by the model's ability to provide feedback on its own code", with larger gains once feedback quality was raised ([Olausson et al.](https://arxiv.org/abs/2306.09896v5)). A validator error is external and precise, so it supplies the input self-critique cannot generate. Instructor wires that path: a Pydantic `field_validator` raises, and "Failed validations are automatically retried with the error message" up to `max_retries` ([Instructor](https://github.com/567-labs/instructor)).

## When this backfires

- The value's truth lives outside the process. A customer ID that exists, satisfies every format rule, and belongs to someone else passes every local check.
- The rule already fits in the schema. `enum`, `minimum`, `maximum`, and `pattern` belong in the contract the decoder enforces; a second copy only drifts.
- The field is inferred rather than extracted. A derived rate has no source span, so an evidence field invites a fabricated citation, and Nweke measured evidence fields pushing "output tokens up by roughly a third".
- The input genuinely lacks the field. Retry cannot succeed, and Nweke caps at two for that reason. Nullability does not rescue the case, because larger models "often output incorrect answers instead of abstaining" when the context does not support one ([Joren et al.](https://arxiv.org/abs/2411.06037v3)).
- The validator is stricter than reality. A rule tight enough to catch fabrications rejects unusual-but-correct values, and the reject queue becomes the new failure.

One framing to avoid: schema mode is not established as harmful to answer quality. Park et al. show constrained decoding can distort the model's distribution toward outputs that are "grammatical but appear with likelihoods that are not proportional to the ones given by the LLM, and so ultimately are low-quality" ([Park et al.](https://arxiv.org/abs/2405.21047v3)). Geng et al. measured the opposite on task accuracy, with Guidance about three points above the unconstrained baseline on three reasoning tasks ([JSONSchemaBench](https://arxiv.org/abs/2501.10868v3)). Rest the case for a semantic layer on what the guarantee omits, not on a quality cost.

## Example

An agent proposes a dependency. The schema accepts the payload because both fields are strings, and whether the name resolves on PyPI is not a question the schema is able to ask:

**Before** — conformance only:

```json
{ "package": "requests-retry-async", "version": "2.1.0" }
```

**After** — the same contract with a membership test attached:

```python
from pydantic import BaseModel, field_validator

class Dependency(BaseModel):
    package: str
    version: str

    @field_validator("package")
    def package_must_exist(cls, v: str) -> str:
        if not index.contains(v):      # the anchor: a register the process holds
            raise ValueError(f"no such package: {v}")
        return v
```

Called through Instructor with `max_retries=2`, a failed lookup sends `no such package: …` back to the model instead of sending the name to `pip` ([Instructor](https://github.com/567-labs/instructor)).

## Key Takeaways

- Schema conformance is a complete signal about shape and a null signal about value; treat the two guarantees separately.
- A semantic check needs an anchor: a register to look up, a bound that is physically real, or a second field to compare against.
- Invented identifiers are the class schemas structurally cannot catch, because every fabricated name satisfies `type: string`.
- Deterministic validator errors beat self-critique as retry feedback, which is the input Olausson et al. found self-repair lacking.
- Cap retries and escalate when the input has no answer to give; nullable fields do not make models abstain.
- Where no anchor exists, route the record to a human rather than adding a layer that looks like verification.

## Related

- [Structured Output Constraints: Reducing Hallucination Surface](structured-output-constraints.md) — the case for schemas in the first place; this page picks up where its conformance guarantee stops
- [Typed Generation Contracts for Grounded Extraction](typed-generation-contract.md) — the anchor case where the value does have a source span to quote
- [Typed Schemas at Agent Boundaries for Multi-Agent Systems](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md) — enforcing the shape half at handoffs
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — why a check that runs beats an instruction that asks
- [Phantom Symbol Detection for LLM API Migration](phantom-symbol-detection.md) — the identifier class applied to imports and method names in migration code
- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](../security/slopsquatting-hallucinated-package-names.md) — what an unchecked invented identifier costs downstream
