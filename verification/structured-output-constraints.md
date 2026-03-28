---
title: "Structured Output Constraints: Reducing Hallucination"
description: "Constrain agent output with templates and schemas to reduce hallucination surface. Required fields and JSON schemas make gaps detectable rather than invisible."
tags:
  - testing-verification
  - tool-agnostic
---

# Structured Output Constraints: Reducing Hallucination Surface

> Constrain agent output with templates and schemas to reduce the degrees of freedom available for error.

## The Problem with Blank Pages

A blank page is an invitation to hallucinate. When an agent has unlimited output freedom, it fills that freedom with confident-sounding prose, invented citations, and plausible-but-wrong details.

Structured output constraints reduce hallucination surface by giving the agent a template to fill rather than a blank page.

## How Constraints Reduce Hallucination

Each structural constraint removes a degree of freedom:

- **Required sections** — the agent must address each section. Missing sections become visible.
- **Required fields** — a "sources" field forces the agent to name sources. An empty sources field is detectable. A paragraph with invisible sourcing gaps is not.
- **Type constraints** — if the output must be valid JSON, the agent cannot produce narrative padding around the answer.
- **Enum values** — if a verdict field must be "PASS" or "FAIL", the agent cannot hedge with "mostly pass" or produce a non-binary answer.

## Structured Output for Code

[Claude's structured output support](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) allows constraining responses to a JSON schema. When the schema requires specific fields, the model cannot omit them or substitute narrative for structured data.

Example review output schema:
```json
{
  "verdict": "PASS | FAIL",
  "issues": [
    {
      "severity": "critical | high | medium | low",
      "description": "...",
      "fix": "..."
    }
  ],
  "notes": []
}
```

This format is machine-readable, downstream-processable, and rejects hedging. The agent either produces a valid schema or fails.

## Page Templates as Structural Constraints

Document templates impose the same constraints on prose output that JSON schemas impose on data output. A content page template with required sections — title, summary blockquote, content sections, Key Takeaways, Related — forces the agent to populate each section explicitly.

Required sections act as checklists:

- A "Sources" section forces citation behavior
- An "Unverified Claims" section forces explicit marking of uncertain knowledge
- A "Key Takeaways" section forces distillation rather than padding

Without these sections, the agent decides what to include and what to skip. With them, gaps are visible — an empty section is detectable; missing sections are detectable.

[Claude Code skills](https://code.claude.com/docs/en/skills) use template files in skill directories to constrain agent output format.

## Research Note Templates

Research notes benefit from structure as much as output pages:

```markdown
## Findings
- Finding 1 [source URL]
- Finding 2 [source URL]

## Unverified
- Claim without a source [unverified]

## Angle
One-sentence summary of what this research supports
```

Each field has a clear purpose. The "Unverified" section forces the researcher to separate sourced from unsourced before handing off.

## Trade-offs

Structure reduces hallucination surface but constrains legitimate flexibility. The right level of structure depends on the task:

- High-stakes, automatable tasks (code review output, schema generation) benefit from tight schema constraints
- Creative or exploratory tasks (early ideation, open-ended research) may need looser structure to avoid forcing artificial answers into ill-fitting fields
- Progressive structuring — loose template first, tighter schema after validation — can balance both needs [unverified]

Too much structure produces compliant but hollow output: the agent fills every field with something rather than nothing, but the content is low-quality filler. Too little structure produces unverifiable output.

## Anti-Pattern

Asking an agent to "write about X" with no structural guidance. The agent will produce plausible prose with no verifiable properties. You cannot check whether all claims are sourced, whether the required sections are present, or whether the verdict is actionable, because none of these were required.

## Example

A code-review agent without output constraints produces free-form prose:

```
The code looks generally fine. There might be a race condition
in the handler but it's probably okay for most use cases.
```

Adding a JSON schema constraint forces the agent into a machine-validatable structure:

```json
{
  "verdict": "FAIL",
  "issues": [
    {
      "severity": "high",
      "file": "server/handler.go",
      "line": 42,
      "description": "Unsynchronized read of shared counter in request handler",
      "fix": "Wrap counter access in a mutex or use atomic operations"
    }
  ],
  "notes": ["No other issues found"]
}
```

The constrained version cannot hedge, cannot omit the verdict, and must attach a severity and fix to each issue. An empty issues array with a FAIL verdict is an obvious contradiction a downstream check can catch.

## Key Takeaways

- Templates reduce hallucination surface by removing degrees of freedom from the output
- Required fields force explicit handling of gaps — empty or missing fields are detectable
- JSON schemas and enum constraints make agent output machine-validatable
- Page templates and research note templates impose the same constraints on prose that schemas impose on data
- The trade-off: tight structure can produce compliant but hollow output — calibrate to the task
- Anti-pattern: "write about X" with no structural guidance

## Related

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md)
- [Layered Accuracy Defense](layered-accuracy-defense.md)
- [Data Fidelity Guardrails](data-fidelity-guardrails.md)
- [Diff-Based Review Over Output Review](../code-review/diff-based-review.md)
- [Incremental Verification](incremental-verification.md)
- [Verification Ledger](verification-ledger.md)
- [Risk-Based Task Sizing](risk-based-task-sizing.md)
