---
title: "MCP Elicitation: Servers Requesting Structured Input Mid-Task"
term: "MCP Elicitation"
description: "How MCP servers collect structured user input mid-task via elicitation, and how Elicitation and ElicitationResult hooks let you automate, validate, or block those requests."
tags:
  - tool-engineering
  - claude
  - mcp
last_reviewed: 2026-06-13
maturity: established
---

# MCP Elicitation: Servers Requesting Structured Input Mid-Task

> MCP elicitation lets servers pause a tool call to request structured input; Claude Code hooks intercept, auto-fill, validate, or suppress those requests.

## Elicitation versus upfront parameters

Tool schemas set inputs statically at registration time. Some inputs are only known mid-task, after the server inspects state, resolves dependencies, or reaches a decision point. Elicitation covers that gap: the MCP server requests structured input when it needs it, not before.

| Approach | When inputs are known | Trade-off |
|----------|----------------------|-----------|
| Tool schema parameter | At tool registration | Good for predictable inputs; breaks for context-dependent ones |
| Elicitation | Mid-task, on demand | Accurate for contextual inputs; interrupts headless workflows |

Use elicitation when the valid values or required fields depend on server-side state that cannot be known when the tool is called.

## Why it works

Sometimes a required field depends on state the server only discovers at runtime: the set of existing entities, the result of a lookup, the branch of a decision tree. Encoding that field as a static parameter forces the server to accept a wider input than it supports, or to reject calls after the fact. Elicitation resolves the mismatch. It pauses the in-flight call, describes the missing fields as a form, and lets the client supply values. The `Elicitation` and `ElicitationResult` hooks sit at the two boundaries of that pause: before the user sees the form, and after the user responds. They give automation a place to substitute, validate, or suppress input without changing the server or the tool schema.

## How elicitation works

When an MCP server triggers elicitation, Claude Code [fires two hook events](https://code.claude.com/docs/en/hooks.md):

1. `Elicitation` fires when the server requests input, and receives the form definition.
2. `ElicitationResult` fires after the user fills the form, before the response goes to the server.

The `Elicitation` hook payload includes the MCP server name, the tool name, and an `elicitation_form` object with field definitions:

```json
{
  "hook_event_name": "Elicitation",
  "mcp_server_name": "memory",
  "tool_name": "mcp__memory__create_entities",
  "elicitation_form": {
    "fields": [
      { "name": "entity_name", "label": "Entity Name", "type": "text", "required": true },
      { "name": "description", "label": "Description", "type": "text", "required": false }
    ]
  }
}
```

Both hooks match on MCP server name, so you can apply different behavior per server.

## Hook actions

An `Elicitation` hook can return three actions through `hookSpecificOutput`:

```json
{ "hookSpecificOutput": { "hookEventName": "Elicitation", "action": "accept",
    "content": { "entity_name": "User Profile", "description": "Primary user entity" } } }
```

| Action | Effect |
|--------|--------|
| `accept` with `content` | Auto-fills the form and sends the response without showing the dialog |
| `decline` | Rejects the elicitation; the server receives a declined response |
| `cancel` | Cancels the entire operation |

`ElicitationResult` fires after user input. It can modify, validate, or reject values before they reach the server, using the same action and content structure.

## Headless automation pattern

In CI pipelines or non-interactive agents, any elicitation dialog would block indefinitely. Configure an `Elicitation` hook to auto-accept with known values for the relevant MCP server, which stops the dialog from appearing at all.

`.claude/settings.json`, to auto-fill elicitation for a known server:

```json
{
  "hooks": {
    "Elicitation": [
      {
        "matcher": "memory",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/auto-fill-memory-elicitation.sh"
          }
        ]
      }
    ]
  }
}
```

`auto-fill-memory-elicitation.sh`:

```bash
#!/usr/bin/env bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

if [ "$TOOL" = "mcp__memory__create_entities" ]; then
  jq -n '{hookSpecificOutput: {hookEventName: "Elicitation", action: "accept",
    content: {entity_name: "auto", description: "Created by automation"}}}'
else
  exit 0  # Fall through to interactive dialog for other tools
fi
```

## Validation pattern

`ElicitationResult` is the place to sanitize user-provided values, or enforce policy on them, before they reach an external MCP server:

```bash
#!/usr/bin/env bash
INPUT=$(cat)
NAME=$(echo "$INPUT" | jq -r '.user_response.entity_name // empty')

# Reject empty or suspiciously short names
if [ ${#NAME} -lt 3 ]; then
  jq -n '{hookSpecificOutput: {hookEventName: "ElicitationResult", action: "decline"}}'
  exit 0
fi

# Sanitize: strip leading/trailing whitespace
CLEAN=$(echo "$NAME" | xargs)
jq -n --arg name "$CLEAN" \
  '{hookSpecificOutput: {hookEventName: "ElicitationResult", action: "accept",
    content: {entity_name: $name}}}'
```

## When this backfires

Client support is not universal. Elicitation was added to the MCP spec in June 2025. Not all clients implement it. A client that does not will either block silently, return a "Method not found" error, or crash during the capability handshake. Verify client support before you design a tool that depends on elicitation. [GitHub Copilot in VS Code supports elicitation](https://github.blog/ai-and-ml/github-copilot/building-smarter-interactions-with-mcp-elicitation-from-clunky-tool-calls-to-seamless-user-experiences/); other hosts vary.

Headless pipelines stall without a hook. Any elicitation request in a CI or non-interactive context blocks indefinitely, unless an `Elicitation` hook is set in advance to auto-accept or decline. The call hangs and does not time out. The fix is an explicit hook (see the headless automation pattern above), but it means anticipating every server that might elicit.

Schema complexity is limited by design. Elicitation supports only flat primitive fields: `text`, `number`, `boolean`, and `select`. The elicitation form schema cannot express conditional fields, nested objects, or array inputs. If the required input is structurally complex, model it as a tool parameter or use a multi-step tool sequence instead.

Gateways and proxies can break elicitation without warning. Many MCP gateways relay only client-to-server traffic, so server-to-client messages like `elicitation/create` have no path back and are dropped. A LiteLLM bug report in March 2026 documents this: servers that work standalone stop eliciting once a gateway fronts them for centralized auth ([BerriAI/litellm#23761](https://github.com/BerriAI/litellm/issues/23761)). Check that your gateway proxies bidirectional JSON-RPC and keeps stateful sessions before you front an eliciting server.

## Key Takeaways

- Elicitation collects structured input mid-task, after the server knows what it needs — unlike tool schema parameters, which are defined at registration time.
- The `Elicitation` hook intercepts before the dialog appears; the `ElicitationResult` hook intercepts after the user responds.
- Both hooks match on MCP server name, enabling per-server behavior.
- In headless contexts, an `Elicitation` hook that auto-accepts prevents pipeline stalls.
- `ElicitationResult` is the correct place to validate or sanitize user input before it reaches an external server.

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [MCP Client/Server Architecture](mcp-client-server-architecture.md)
- [MCP Server Design: Building Agent-Friendly Servers](mcp-server-design.md)
- [MCP Client Design](mcp-client-design.md)
- [Judging MCP Capability Readiness by Client Adoption](mcp-capability-readiness.md)
- [Override Interactive Commands](override-interactive-commands.md)
