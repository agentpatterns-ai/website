---
title: "Semantic Tool Output: Designing for Agent Readability"
description: "Return human-readable, contextually filtered output from agent tools to reduce hallucination and improve downstream call accuracy."
aliases:
  - Tool Output Design
  - Token-Efficient Tool Design
  - Agent-Friendly Output
tags:
  - context-engineering
  - agent-design
  - cost-performance
---

# Semantic Tool Output: Designing for Agent Readability

> Return human-readable, contextually filtered output from agent tools to reduce hallucination and improve downstream call accuracy.

!!! note "Also known as"
    Tool Output Design, Token-Efficient Tool Design, Agent-Friendly Output. For the cost angle — designing tool outputs to minimize token consumption — see [Token-Efficient Tool Design](token-efficient-tool-design.md).

## Why Output Design Matters

Agents reason over tool output as natural language. When tools return opaque identifiers, machine-oriented fields, or oversized payloads, agents are more likely to hallucinate values or make erroneous downstream calls. Output format is a reliability lever independent of model capability — a well-designed response schema consistently outperforms a poorly designed one even when the underlying tool logic is identical.

## Principles

### Replace Identifiers with Semantic Equivalents

UUIDs, MIME types, and internal codes are opaque to agents:

```json
{"id": "a3f4b2c1-...", "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
```

Replace them with the natural-language fields the agent will reason about:

```json
{"name": "Q3 Budget Review", "file_type": "Word document"}
```

The agent can now reference the object by name in subsequent calls and instructions without risk of miscopying a UUID.

### Return Only Contextually Relevant Fields

Omit data the agent will never use for the current task. A tool that returns all 40 fields of a user record when the agent only needs `name` and `email` wastes context on 38 irrelevant fields. Every extra field is a hallucination opportunity — the agent may reference, invent, or misinterpret fields it was not asked to act on.

Design output schemas to include only the fields that are decision-relevant for the tool's purpose. Provide expanded output as an optional mode, not a default.

### Implement Pagination and Filtering at the Tool Layer

Tools that return full datasets shift the filtering burden to the agent — which either hallucinates the filter logic or consumes the entire dataset in context. Instead:

- Accept filter parameters (`status=open`, `created_after=2024-01-01`) and apply them before returning results.
- Return a page of results with a cursor, not an unbounded list.
- Provide sensible defaults (`limit=20`) that prevent accidental context flooding.

This pattern lets the agent request exactly what it needs for the next decision rather than loading everything and discarding most of it.

### Use Enums for Response Granularity

When an agent might need different levels of detail at different points in a workflow, expose a `response_format` enum rather than always returning full or minimal output:

```json
{"response_format": "concise"}  // summary fields only
{"response_format": "detailed"} // full record with all fields
```

The agent selects the appropriate format based on its current context budget and task requirements, without you having to anticipate every combination in advance.

### Make Errors Actionable

Error responses should tell the agent what went wrong and how to fix it:

```json
{"error": "Invalid date range: end_date must be after start_date. Received start=2024-03-01, end=2024-02-01."}
```

Not:

```json
{"error": "400 Bad Request"}
```

An opaque error code forces the agent to guess the cause. A specific, corrective message allows it to self-correct on the next call without human intervention.

## Why It Works

LLMs process tool output as tokens in the context window and perform next-token prediction over those tokens. UUIDs and MIME type strings are arbitrary byte sequences with no semantic relationship to the concepts they represent — the model cannot reliably reconstruct or reference them without copying verbatim. Natural-language equivalents (names, human-readable types, formatted values) activate the model's existing world-knowledge associations, making reference in downstream calls far more accurate. Reducing context to decision-relevant fields also narrows the set of tokens the model must attend to, which lowers the probability of the model conflating or misattributing fields from different parts of the record.

## When This Backfires

Semantic filtering at the tool layer has failure modes:

- **Under-specification**: A task-specific schema omits a field the agent unexpectedly needs. The agent either hallucinates the value or must make an additional round-trip call to retrieve it — sometimes more expensive than returning the full record once.
- **Mismatch between `concise` and `detailed`**: When a `response_format` enum is exposed but the agent misjudges which mode to request, it operates on incomplete data without knowing it. Prompting the agent to reason about its data needs before calling the tool reduces this risk.
- **Schema drift**: A tool's "clean default" is often shaped by the first use case implemented. As agents are given new tasks, the default schema becomes misaligned without explicit versioning or opt-in expansion.

When tool output scope is genuinely unpredictable across callers, a richer default with well-named fields is safer than a narrow schema that forces multiple calls.

## Anti-Pattern: Developer-Convenience Output

Tools built for developer debugging often return everything: raw database records, full object graphs, internal identifiers, and debug fields. This is appropriate for a developer reading output in a terminal. It is the wrong default for an agent consuming output in a context window.

The fix is not to strip developer-useful data, but to separate concerns: a `debug` mode for developer use, a clean default for agent use.

## Example

A `get_customer` tool returns a full database record by default:

```json
{
  "id": "cust_8f3a91b2-47c1-4e2d-b891-3c5d7a2e0f14",
  "name": "Acme Corp",
  "email": "billing@acme.com",
  "plan": "enterprise",
  "stripe_id": "cus_NffrFeUfNV2Hib",
  "created_at": "2023-06-15T09:30:00Z",
  "updated_at": "2024-11-02T14:22:31Z",
  "metadata": {"segment": "mid-market", "csm_id": "emp_442"},
  "feature_flags": ["beta_dashboard", "v2_api"],
  "billing_address": { "line1": "123 Main St", "city": "Portland", "state": "OR", "zip": "97201" },
  "mrr_cents": 249900
}
```

An agent asked to "email Acme Corp their current plan details" needs three fields. Returning all twelve forces it to parse irrelevant data and risks it hallucinating references to `stripe_id` or `feature_flags` in the email. Redesign the tool to return a semantic, filtered response:

```json
{
  "name": "Acme Corp",
  "email": "billing@acme.com",
  "plan": "Enterprise",
  "monthly_price": "$2,499.00"
}
```

The agent now has exactly what it needs — a human-readable name, the contact address, and a formatted price — with no opaque identifiers to misinterpret.

## Key Takeaways

- Replace opaque identifiers with semantic equivalents the agent can reference naturally.
- Return only the fields that are decision-relevant for the tool's purpose.
- Apply filtering and pagination at the tool layer, not in the agent's reasoning.
- Use a `response_format` enum to let the agent match output depth to context budget.
- Write error messages that diagnose the problem and specify the correction.

## Related

- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — semantic output is one of four ACI design principles; affordances, constraints, and error prevention are the other three
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [CLI Scripts as Agent Tools: Return Only What Matters](cli-scripts-as-agent-tools.md)
- [Context Compression Strategies](../context-engineering/context-compression-strategies.md)
- [Controlling Agent Output: Concise Answers, Not Essays](../agent-design/controlling-agent-output.md)
- [Machine-Readable Error Responses for AI Agents (RFC 9457)](rfc9457-machine-readable-errors.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md)
- [Tool Description Quality](tool-description-quality.md)
