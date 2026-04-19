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

Agents reason over tool output as natural language. When tools return opaque identifiers, machine-oriented fields, or oversized payloads, they waste context and make it harder for the model to extract what matters ([Anthropic, *Writing effective tools for agents*](https://www.anthropic.com/engineering/writing-tools-for-agents)). Output format is a reliability lever independent of model capability.

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

Resolving alphanumeric UUIDs to semantic language (or even a 0-indexed scheme) "significantly improves Claude's precision in retrieval tasks by reducing hallucinations" ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)). The agent can then reference the object by name without miscopying an identifier.

### Return Only Contextually Relevant Fields

Omit data the agent will never use. A tool returning 40 fields when the agent needs `name` and `email` wastes context on 38 irrelevant fields, and every extra field is a hallucination opportunity — the agent may reference, invent, or misinterpret fields it was not asked to act on. Anthropic's tool-use guidance is to return only high-signal information and include only the fields Claude needs for its next step ([Claude API docs, *Tool use*](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)). Design schemas around decision-relevant fields, and expose expanded output as an optional mode.

### Implement Pagination and Filtering at the Tool Layer

Tools that return full datasets shift filtering to the agent, which either hallucinates the filter or loads the entire dataset into context. Anthropic recommends "some combination of pagination, range selection, filtering, and/or truncation with sensible default parameter values" for any response that can grow large ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)). In practice:

- Accept filter parameters (`status=open`, `created_after=2024-01-01`) and apply them before returning results.
- Return a page of results with a cursor, not an unbounded list.
- Provide sensible defaults (`limit=20`) that prevent accidental context flooding.

### Use Enums for Response Granularity

When an agent needs different levels of detail at different points, expose a `response_format` enum ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)) rather than always returning full or minimal output:

```json
{"response_format": "concise"}  // summary fields only
{"response_format": "detailed"} // full record with all fields
```

The agent selects the appropriate format based on its current context budget and task requirements.

### Make Errors Actionable

Error responses should tell the agent what went wrong and how to fix it:

```json
{"error": "Invalid date range: end_date must be after start_date. Received start=2024-03-01, end=2024-02-01."}
```

Not:

```json
{"error": "400 Bad Request"}
```

Errors should "clearly communicate specific and actionable improvements, rather than opaque error codes or tracebacks" ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)), letting the agent self-correct on the next call without human intervention.

## Why It Works

LLMs do next-token prediction over the tool output in context. UUIDs and MIME strings are arbitrary byte sequences with no semantic relationship to the concepts they represent — the model cannot reliably reconstruct or reference them without copying verbatim. Natural-language equivalents activate existing world-knowledge associations, making downstream reference more accurate. Narrowing output to decision-relevant fields also shrinks the attention surface, lowering the chance of conflating or misattributing fields from different parts of the record.

## When This Backfires

Semantic filtering at the tool layer has failure modes:

- **Under-specification**: a task-specific schema omits a field the agent unexpectedly needs. The agent either hallucinates the value or makes an extra round-trip — sometimes more expensive than returning the full record once.
- **Concise/detailed mismatch**: when `response_format` is exposed but the agent picks the wrong mode, it operates on incomplete data without knowing it. Prompting the agent to reason about its data needs before calling the tool reduces this risk.
- **Schema drift**: a "clean default" shaped by the first use case becomes misaligned as new tasks arrive, unless you version the schema or gate expansion behind opt-in.

When output scope is genuinely unpredictable across callers, a richer default with well-named fields is safer than a narrow schema that forces multiple calls.

## Anti-Pattern: Developer-Convenience Output

Tools built for developer debugging often return everything — raw database records, full object graphs, internal identifiers, debug fields. That is fine for a developer reading a terminal. It is the wrong default for an agent consuming output in a context window. The fix is not to strip developer-useful data, but to separate concerns: a `debug` mode for developer use, a clean default for agent use.

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
