---
title: "Constraint Tax: Tool Suppression Under JSON Schema Decoding"
description: "Co-enabling JSON-schema constrained decoding and tool calling silently suppresses tool invocation in open-weight models — schemas stay valid, tools never fire."
tags:
  - anti-pattern
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-25
maturity: emerging
---

# Constraint Tax: Tool Suppression Under JSON Schema Decoding

> Co-enabling JSON-schema constrained decoding and tool calling silently suppresses tool invocation in open-weight models — schema compliance stays high, tools never fire.

Tool Suppression is a reliability failure in open-weight LLMs served with grammar-based constrained decoding and tool calling in the same request. The model keeps returning schema-valid JSON, so monitoring looks healthy, while tool-call tokens become unreachable in the decoder — the agent silently stops acting. The effect is reproducible across multiple open-weight model families and deployment configurations ([Constraint Tax in Open-Weight LLMs (arxiv:2606.25605)](https://arxiv.org/abs/2606.25605)).

## When this applies

The failure mode surfaces when all of these hold:

- Open-weight serving stack with grammar-based decoding — vLLM grammar mode, llama.cpp grammars, Outlines, or llguidance compiling a JSON schema into a finite-state grammar
- Tool calling and structured output enabled in the same request, where the response schema does not enumerate the tool-call branch as a valid first-token sequence
- Multi-capability agent loops where a single turn might either call a tool or emit a final structured answer

Closed-weight vendor APIs that own the inference path document the combination as a supported workflow with explicit complexity limits ([Anthropic Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). The trap is specific to self-hosted stacks where the constrained-decoding layer is unaware of the tool-call grammar.

## Why it backfires

Grammar-based decoding compiles the JSON schema into a finite-state grammar. At each decoding step the server intersects the model's logits with the grammar's allowed-token set and zeroes the rest. Tool-calling formats begin with distinct opening tokens (`<tool_call>`, `{"tool_calls":`, vendor markers). If the response schema does not enumerate that branch as a valid first-token sequence, the mask sets those probabilities to zero — the constraint engine outranks the model's preferences by construction ([arxiv:2606.25605](https://arxiv.org/abs/2606.25605)).

The paper names the artifact Constraint Priority Inversion (CPI): schema satisfaction dominates action selection when constraints compete. Schema-compliance stays near 100% while tool-invocation rate collapses — the dashboard signals success and the agent stops acting. [Tam et al. (2024)](https://arxiv.org/abs/2408.02442) corroborate the broader pattern: stricter format constraints produce greater reasoning-accuracy degradation via the same mask mechanism.

## When this does not apply

The tax is not universal. Safe configurations:

- Closed-weight vendor APIs (Anthropic, OpenAI) that track combined-schema complexity and handle tool-call and JSON-output paths as documented features ([Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs))
- Schemas that explicitly reserve a tool-call variant as an allowed top-level branch — the grammar then permits the tool-call tokens
- Tool calling without structured response constraints — only tool arguments carry strict schema validation, so the tool-call entry tokens stay unmasked

In all other open-weight self-hosted configurations, validate empirically before shipping.

## Mitigations

The paper proposes Transparent Two-Pass Execution: decouple tool invocation from schema-constrained generation. Pass 1 runs without the response grammar so tool-call tokens remain reachable. Pass 2 applies the schema only to the final response, after tool results return ([arxiv:2606.25605](https://arxiv.org/abs/2606.25605)). Alternatives: extend the schema to reserve the tool-call branch, or evaluate tool calling and structured output separately before combining them. Add a tool-invocation-rate metric next to schema-compliance metrics so Constraint Priority Inversion is detectable in monitoring.

## Example

The suppression appears in vLLM-style serving when a JSON-mode response schema is passed alongside tool definitions:

```python
# Anti-pattern — open-weight + grammar JSON schema + tools in one request.
# The response schema enumerates only {"answer": str, "confidence": float};
# tool_calls is not a valid first-token branch, so the grammar mask zeroes
# the tool-call opening tokens. Tools are defined but never invoked.
response = client.chat.completions.create(
    model="open-weight-model",  # e.g. Llama / Mistral / Qwen variants
    tools=[weather_tool, search_tool],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["answer", "confidence"],
            },
        },
    },
    messages=[{"role": "user", "content": "What is the weather in Oslo?"}],
)
# Returns schema-valid JSON. tool_calls is always empty.
```

The two-pass mitigation:

```python
# Fix — pass 1 runs unconstrained so tools can fire; pass 2 applies the
# response schema only after tool results return.
draft = client.chat.completions.create(
    model="open-weight-model",
    tools=[weather_tool, search_tool],
    # no response_format — grammar masks do not touch tool-call tokens
    messages=[{"role": "user", "content": "What is the weather in Oslo?"}],
)
# Run any tool calls in draft.choices[0].message.tool_calls, append results
# to messages, then finalize with the schema applied:
final = client.chat.completions.create(
    model="open-weight-model",
    response_format={"type": "json_schema", "json_schema": {...}},
    messages=messages_with_tool_results,
)
```

Pair this with monitoring that tracks tool-invocation rate alongside schema-compliance rate so a future regression that re-enables the single-pass path is detectable.

## Key Takeaways

- Tool Suppression is a reproducible failure in open-weight stacks: schema-valid JSON with tool-invocation rate near zero
- The mechanism is grammar masks zeroing the tool-call opening tokens, not a model-preference failure
- Closed-weight vendor APIs document the combination as supported — the tax is specific to self-hosted grammar-decoding deployments
- Mitigate with two-pass execution, extend the schema to include a tool-call branch, or evaluate tool calling and structured output separately before combining them
- Monitor tool-invocation rate next to schema-compliance rate — single-axis monitoring hides Constraint Priority Inversion

## Related

- [Structured Output Constraints: Reducing Hallucination](../verification/structured-output-constraints.md) — the complementary benefit-side view; this page is the cost-side trade-off when combined with tool calling
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — another anti-pattern where a generally useful technique is applied without checking whether it helps the specific task
- [Dynamic Tool Fetching Breaks KV Cache](dynamic-tool-fetching-cache-break.md) — sibling failure where intuitive tool-side optimisation breaks a different layer (cache vs. decoding)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md) — tool-side design choices that affect agent reliability
- [Advanced Tool Use](../tool-engineering/advanced-tool-use.md) — broader reference for tool-calling reliability and harness design
