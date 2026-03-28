---
title: "Tool Calling Schema Standards for AI Agent Development"
description: "Tool definitions across providers converge on JSON Schema, but field names, strict modes, and capability constraints differ in ways that matter when porting."
tags:
  - agent-design
  - cost-performance
aliases:
  - Tool Schema Design
  - Subagent Schema-Level Tool Filtering
  - Tool Minimalism
---

# Tool Calling Schema Standards

> Tool definitions across providers converge on JSON Schema with name, description, and parameters — but field names, strict modes, and capability constraints differ in ways that matter when porting tools between systems.

!!! info "Also known as"
    Subagent Schema-Level Tool Filtering, Tool Minimalism, Tool Schema Design

## The Shared Core

Every major provider defines tools using the same structural pattern: a name, a natural-language description, and a JSON Schema object describing the input parameters. The model reads the description to decide when to call the tool, and uses the parameter schema to generate valid arguments.

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "<parameters_field>": {
    "type": "object",
    "properties": {
      "location": { "type": "string", "description": "City name" }
    },
    "required": ["location"]
  }
}
```

The `<parameters_field>` key is where providers diverge.

## Provider Schema Comparison

| Field | OpenAI | Anthropic | Gemini | MCP |
|-------|--------|-----------|--------|-----|
| Tool name | `name` | `name` | `name` | `name` |
| Description | `description` | `description` | `description` | `description` |
| Parameters key | `parameters` | `input_schema` | `parameters` | `inputSchema` |
| Schema standard | JSON Schema | JSON Schema | OpenAPI-compatible | JSON Schema |
| Strict mode | `strict: true` | `strict: true` | N/A | N/A |
| Wrapper | `{"type": "function", "function": {...}}` | Top-level object | `functionDeclarations[]` | Top-level object |

Sources: [OpenAI function calling](https://developers.openai.com/docs/guides/function-calling), [Anthropic tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use), [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling), [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

## Description Quality Matters Most

The `description` field has the highest impact on tool calling reliability. Models use it to decide *whether* to call a tool and *how* to populate parameters. A vague description causes incorrect tool selection; a missing parameter description causes hallucinated arguments.

Anthropic's guidance on [building effective agents](https://www.anthropic.com/research/building-effective-agents) recommends treating tool descriptions with the same care as human-facing UX — including example usage, edge cases, input format requirements, and clear boundaries from other tools.

## Strict Mode

Both OpenAI and Anthropic support `strict: true` on tool definitions. When enabled, the provider [guarantees](https://developers.openai.com/docs/guides/structured-outputs) that generated arguments conform exactly to the provided JSON Schema — eliminating type mismatches and missing required fields.

Strict mode constraints:

- All properties must be listed in `required`
- `additionalProperties` must be `false` on every object

Use strict mode in production when invalid tool parameters would cause downstream failures.

## MCP as Convergence Point

MCP tool definitions use `inputSchema` (JSON Schema) and are consumed by any MCP-compatible host — Copilot, Claude Code, Cursor, and others. A tool defined once in an MCP server works across all hosts without per-provider schema translation.

This makes MCP the practical convergence standard: write the tool definition once, and every compatible agent can discover and call it through the [MCP server manifest](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

## Schema Design Guidance

- **Keep schemas flat.** Deeply nested objects increase token count and parsing errors [unverified]. Prefer top-level properties over nested structures.
- **Describe every parameter.** A `description` on each property tells the model what value to provide. Without it, the model guesses from the parameter name alone.
- **Use absolute identifiers.** Anthropic found that [requiring absolute filepaths](https://www.anthropic.com/research/building-effective-agents) instead of relative paths eliminated an entire class of agent errors ([poka-yoke principle](../tool-engineering/poka-yoke-agent-tools.md)).
- **Minimize parameter count.** Each additional parameter increases the probability of an incorrect argument. Consolidate related fields when possible.

## Example

The same `get_weather` tool defined for each provider:

**OpenAI**

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get current weather for a location. Returns temperature in Celsius and conditions.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": { "type": "string", "description": "City name, e.g. 'London'" }
      },
      "required": ["location"],
      "additionalProperties": false
    },
    "strict": true
  }
}
```

**Anthropic**

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location. Returns temperature in Celsius and conditions.",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": { "type": "string", "description": "City name, e.g. 'London'" }
    },
    "required": ["location"]
  }
}
```

**Gemini**

```json
{
  "functionDeclarations": [{
    "name": "get_weather",
    "description": "Get current weather for a location. Returns temperature in Celsius and conditions.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": { "type": "string", "description": "City name, e.g. 'London'" }
      },
      "required": ["location"]
    }
  }]
}
```

**MCP**

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location. Returns temperature in Celsius and conditions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": { "type": "string", "description": "City name, e.g. 'London'" }
    },
    "required": ["location"]
  }
}
```

The logic is identical across all four; only the wrapper structure and the parameters key name differ.

## Key Takeaways

- All providers converge on JSON Schema for tool parameters, but the wrapping structure and field names differ (`parameters` vs `input_schema` vs `inputSchema`).
- Description quality has the highest impact on tool calling reliability — treat descriptions as agent-facing UX.
- Strict mode (`strict: true`) eliminates schema conformance errors in production but requires all properties to be marked `required`.
- MCP tool definitions serve as a write-once, run-anywhere convergence point across compatible hosts.
- Flat schemas with per-parameter descriptions and absolute identifiers reduce agent errors.

## Unverified Claims

- Deeply nested objects increase token count and parsing errors [unverified]

## Related

- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [OpenAPI as Agent Tool Specification](openapi-agent-tool-spec.md)
- [Agent Definition Formats](agent-definition-formats.md)
- [Agent Skills Standard](agent-skills-standard.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md)
- [Consolidate Agent Tools](../tool-engineering/consolidate-agent-tools.md)
- [Tool Descriptions as Onboarding](../tool-engineering/tool-descriptions-as-onboarding.md) — writing tool descriptions with implicit context agents need
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md)
- [Plugin and Extension Packaging](plugin-packaging.md)
