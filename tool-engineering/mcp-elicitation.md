---
title: "MCP Elicitation: Servers Requesting Structured Input Mid-Task"
description: "How MCP servers collect structured user input mid-task via elicitation, and how Elicitation and ElicitationResult hooks let you automate, validate, or block those requests."
tags:
  - tool-engineering
  - claude
---

# MCP Elicitation: Servers Requesting Structured Input Mid-Task

> MCP elicitation lets servers pause a tool call and request structured input from the user — and Claude Code hooks let you intercept, auto-fill, validate, or suppress those requests.

## Elicitation vs. Upfront Parameters

Tool schemas specify inputs statically at registration time. Some inputs are only knowable mid-task — after the server has inspected state, resolved dependencies, or reached a decision point. Elicitation covers that gap: the server requests structured input at the moment it needs it, not before.

| Approach | When inputs are known | Trade-off |
|----------|----------------------|-----------|
| Tool schema parameter | At tool registration | Good for predictable inputs; breaks for context-dependent ones |
| Elicitation | Mid-task, on demand | Accurate for contextual inputs; interrupts headless workflows |

Use elicitation when the valid values or required fields depend on server-side state that cannot be known when the tool is called.

## How Elicitation Works

When an MCP server triggers elicitation, Claude Code [fires two hook events](https://code.claude.com/docs/en/hooks.md):

1. **`Elicitation`** — fires when the server requests input; receives the form definition
2. **`ElicitationResult`** — fires after the user fills the form, before the response is sent to the server

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

## Hook Actions

An `Elicitation` hook can return three actions via `hookSpecificOutput`:

```json
{ "hookSpecificOutput": { "hookEventName": "Elicitation", "action": "accept",
    "content": { "entity_name": "User Profile", "description": "Primary user entity" } } }
```

| Action | Effect |
|--------|--------|
| `accept` with `content` | Auto-fills the form and sends the response without showing the dialog |
| `decline` | Rejects the elicitation; the server receives a declined response |
| `cancel` | Cancels the entire operation |

`ElicitationResult` fires after user input and can modify, validate, or reject values before they reach the server — using the same action/content structure.

## Headless Automation Pattern

In CI pipelines or non-interactive agents, any elicitation dialog would block indefinitely. Configure an `Elicitation` hook to auto-accept with known values for the relevant MCP server — this prevents the dialog from appearing entirely.

**`.claude/settings.json`** — auto-fill elicitation for a known server:

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

**`auto-fill-memory-elicitation.sh`**:

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

## Validation Pattern

`ElicitationResult` is the insertion point for sanitizing or enforcing policy on user-provided values before they reach an external MCP server:

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

## When This Backfires

**Client support is not universal.** Elicitation was added to the MCP spec in June 2025. Not all clients implement it — clients that don't will either block silently, return a "Method not found" error, or crash during the capability handshake. Verify client support before designing a tool that depends on elicitation. [GitHub Copilot in VS Code supports it](https://github.blog/ai-and-ml/github-copilot/building-smarter-interactions-with-mcp-elicitation-from-clunky-tool-calls-to-seamless-user-experiences/); other hosts vary.

**Headless pipelines stall without a hook.** Any elicitation request in a CI or non-interactive agent context blocks indefinitely unless an `Elicitation` hook is pre-configured to auto-accept or decline. The tool call hangs — it does not time out on its own. The fix is an explicit hook (see Headless Automation Pattern above), but that requires anticipating every server that might elicit and configuring coverage in advance.

**Schema complexity is deliberately limited.** Elicitation only supports flat primitive fields (`text`, `number`, `boolean`, `select`). Conditional fields, nested objects, and array inputs are not expressible in the elicitation form schema. If the required input is structurally complex, elicitation is the wrong mechanism — model it as a tool parameter or use a multi-step tool sequence instead.

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
- [Override Interactive Commands](override-interactive-commands.md)
