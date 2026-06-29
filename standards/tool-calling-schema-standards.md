---
title: "Tool Calling Schema Standards for AI Agent Development"
description: "Tool definitions across providers converge on JSON Schema, but field names, strict modes, and capability constraints differ in ways that matter when porting."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - standards
aliases:
  - Tool Schema Design
  - Subagent Schema-Level Tool Filtering
  - Tool Minimalism
last_reviewed: 2026-05-27
maturity: established
---

# Tool Calling Schema Standards

> Tool definitions across providers converge on JSON Schema with name, description, and parameters — but field names, strict modes, and capability constraints differ in ways that matter when porting tools between systems.

!!! info "Also known as"
    Subagent Schema-Level Tool Filtering, Tool Minimalism, Tool Schema Design

## The shared core

Every major provider defines tools with the same structure: a name, a natural-language description, and a JSON Schema object that describes the input parameters. The model reads the description to decide when to call the tool. It uses the parameter schema to generate valid arguments.

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

## Provider schema comparison

| Field | OpenAI | Anthropic | Gemini | MCP |
|-------|--------|-----------|--------|-----|
| Tool name | `name` | `name` | `name` | `name` |
| Description | `description` | `description` | `description` | `description` |
| Parameters key | `parameters` | `input_schema` | `parameters` | `inputSchema` |
| Schema standard | JSON Schema | JSON Schema | OpenAPI-compatible | JSON Schema |
| Strict mode | `strict: true` | `strict: true` | N/A | N/A |
| Wrapper | `{"type": "function", "function": {...}}` | Top-level object | `functionDeclarations[]` | Top-level object |

Sources: [OpenAI function calling](https://developers.openai.com/docs/guides/function-calling), [Anthropic tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use), [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling), [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

## Description quality matters most

The `description` field has the greatest effect on tool calling reliability. Models use it to decide whether to call a tool and how to populate parameters. A vague description causes incorrect tool selection. A missing parameter description causes hallucinated arguments.

Anthropic's guidance on [building effective agents](https://www.anthropic.com/research/building-effective-agents) recommends treating tool descriptions with the same care as human-facing UX. Include example usage, edge cases, input format requirements, and clear boundaries from other tools.

## Strict mode

Both OpenAI and Anthropic support `strict: true` on tool definitions. When you enable it, the provider [guarantees](https://developers.openai.com/docs/guides/structured-outputs) that generated arguments conform exactly to the provided JSON Schema. This removes type mismatches and missing required fields.

Strict mode constraints:

- All properties must be listed in `required`
- `additionalProperties` must be `false` on every object

Use strict mode in production when invalid tool parameters would cause downstream failures.

## MCP as convergence point

MCP tool definitions use `inputSchema` (JSON Schema). Any MCP-compatible host can consume them — Copilot, Claude Code, Cursor, and others. A tool defined once in an MCP server works across all hosts without per-provider schema translation.

This makes MCP the practical convergence standard. You write the tool definition once, and every compatible agent can discover and call it through the [MCP server manifest](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

## Schema design guidance

- Keep schemas flat. Deeply nested objects increase token count and can make parsing harder. Prefer top-level properties over nested structures.
- Describe every parameter. A `description` on each property tells the model what value to provide. Without it, the model guesses from the parameter name alone.
- Use absolute identifiers. Anthropic found that [requiring absolute filepaths](https://www.anthropic.com/research/building-effective-agents) instead of relative paths removed an entire class of agent errors ([poka-yoke principle](../tool-engineering/poka-yoke-agent-tools.md)).
- Minimize parameter count. Each extra parameter raises the chance of an incorrect argument. Consolidate related fields where you can.

## Example

The same `get_weather` tool defined for each provider:

OpenAI:

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

Anthropic:

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

Gemini:

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

MCP:

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

## When this backfires

- Vendor-specific schema features: some providers support schema extensions beyond core JSON Schema. Gemini accepts OpenAPI-compatible constraints. OpenAI's strict mode requires `additionalProperties: false` on every nested object. Designing for portability means avoiding these extensions, trading expressiveness for compatibility.
- Strict mode schema constraints: OpenAI and Anthropic strict mode requires all properties to be listed in `required`. This prevents using optional fields with defaults in ways that feel natural in JSON Schema. Tools that rely heavily on optional parameters need a redesign to use strict mode.
- MCP overhead in local integrations: MCP adds a client-server protocol layer. For a tool that only ever runs in one host (for example, a Claude Code-only tool), defining a full MCP server adds operational overhead with no portability benefit. Inline tool definitions in the host's native format are simpler.

## Key Takeaways

- All providers converge on JSON Schema for tool parameters, but the wrapping structure and field names differ (`parameters` vs `input_schema` vs `inputSchema`).
- Description quality has the highest impact on tool calling reliability — treat descriptions as agent-facing UX.
- Strict mode (`strict: true`) eliminates schema conformance errors in production but requires all properties to be marked `required`.
- MCP tool definitions serve as a write-once, run-anywhere convergence point across compatible hosts.
- Flat schemas with per-parameter descriptions and absolute identifiers reduce agent errors.

## Related

- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [OpenAPI as Agent Tool Specification](openapi-agent-tool-spec.md)
- [Agent Definition Formats](agent-definition-formats.md)
- [Agent Skills Standard](agent-skills-standard.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md)
- [Tool Descriptions as Onboarding](../tool-engineering/tool-descriptions-as-onboarding.md) — writing tool descriptions with implicit context agents need
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md)
