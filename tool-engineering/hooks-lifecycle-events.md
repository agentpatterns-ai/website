---
title: "Hooks and Lifecycle Events: Intercepting Agent Behavior"
description: "Hooks run deterministic code at defined points in an agent's execution — before and after tool calls, at session boundaries — for enforcement and audit."
aliases:
  - How Hooks Work
  - Hook Lifecycle
  - Hook Lifecycle Events
tags:
  - agent-design
  - tool-agnostic
---

# Hooks and Lifecycle Events: Intercepting Agent Behavior

> Hooks run deterministic code at defined points in an agent's execution — before and after tool calls, at session boundaries — enabling enforcement, automation, and audit that instructions cannot guarantee.

!!! note "Also known as"
    **How Hooks Work** · **Hook Lifecycle** · **Hook Lifecycle Events**. For practical enforcement patterns using hooks, see [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md).

## The Role of Hooks

Instructions are processed by the model; hooks are processed by the shell. Under task pressure the model may deprioritize an instruction — a hook executes unconditionally. The runtime spawns the hook as a subprocess before (or after) the model acts, then proceeds or blocks based on its exit code and JSON response. The model cannot override hook logic through reasoning.

## Lifecycle Events

Agent runtimes expose hooks at these points:

| Event | When it fires | Can block |
|-------|--------------|-----------|
| `PreToolUse` | Before a tool call executes | Yes |
| `PostToolUse` | After a tool call completes | No |
| `UserPromptSubmit` | User sends a message | Yes (some tools) |
| `Stop` | Agent finishes a turn | No |
| `InstructionsLoaded` | CLAUDE.md or `.claude/rules/*.md` loads | No |
| `SubagentStart` / `SubagentStop` | Sub-agent spawns or completes | No |

`PreToolUse` enforces — it receives the tool name and inputs, can block, and returns a reason the model must adapt to. `PostToolUse` automates — observational, but triggers side effects like logging or linting.

See [Claude Code hooks](https://code.claude.com/docs/en/hooks) and [Copilot hooks](https://code.visualstudio.com/docs/copilot/customization/hooks).

## Hook Input and Output

Hooks receive event-context JSON on stdin:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm install lodash"
  }
}
```

`PreToolUse` blocks by returning:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use bun instead of npm"
  }
}
```

The `permissionDecisionReason` is surfaced to the model — write it as a redirect.

## Scoping

Matchers scope hooks to specific tools:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": ".claude/hooks/enforce-bun.sh"}]
    }]
  }
}
```

Un-matched hooks fire on every event of that type. Session-level events (`Stop`, `UserPromptSubmit`) don't support matchers.

## Hook Placement by Use Case

| Use case | Event | Approach |
|----------|-------|----------|
| Block disallowed commands | `PreToolUse` (Bash) | Deny + redirect |
| Enforce package manager | `PreToolUse` (Bash) | Match `npm`, redirect to `bun` |
| Auto-lint after edits | `PostToolUse` (Edit/Write) | Run linter |
| Audit tool calls | `PostToolUse` | Append to log |
| Notify on completion | `Stop` | Desktop notification |
| Scan for secrets | `PreToolUse` (Write) | Match content, deny if found |

## Agent Identity and Worktree Context

In multi-agent workflows (Claude Code v2.1.69), hook events carry extra context:

- **`agent_id` / `agent_type`** — distinguish main agent, sub-agents, and team members for per-agent enforcement or audit tagging.
- **`worktree`** — status hooks receive worktree name, path, and branch.

`InstructionsLoaded` fires when CLAUDE.md or `.claude/rules/*.md` load — log it to audit which files were in effect at session start.

## What Hooks Are Not For

Hooks enforce what the model should not decide. Avoid them for:

- **Creative choices** — architecture or style; model judgment is the point.
- **Conversation-dependent logic** — hooks see only the immediate tool call.
- **Complex workflows** — hooks are scripts; keep them short and deterministic.

## Configuration Levels

Configure at project level (`.claude/settings.json`, committed) or user level (`~/.claude/settings.json`, local). Project hooks travel with the repo and enforce team conventions.

## Key Takeaways

- Hooks execute in the shell — the model cannot override them
- `PreToolUse` enforces; `PostToolUse` automates
- Matchers scope hooks to specific tools; session events fire unconditionally
- Project hooks in `.claude/settings.json` enforce team conventions
- `InstructionsLoaded` audits which instruction files loaded at session start
- `agent_id` / `agent_type` enable per-agent enforcement in multi-agent workflows

## Example

Enforce `bun` over `npm` for every `Bash` call. The hook reads tool input from stdin, matches `npm` commands, and blocks with a redirect.

**`.claude/hooks/enforce-bun.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -qE '\bnpm\s+(install|ci|run|exec|init)\b'; then
  cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use bun instead of npm. Replace npm install with bun install, npm run with bun run."
  }
}
EOF
fi
```

**`.claude/settings.json`**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/enforce-bun.sh"
          }
        ]
      }
    ]
  }
}
```

When the agent runs `npm install lodash`, the hook denies the call and surfaces the redirect. The agent retries with `bun install lodash`.

## When This Backfires

Hooks are subprocesses — each matched call pays the startup cost, so a slow `PreToolUse` script delays every matched invocation.

- **The model routes around blocks**: hooks enforce at the tool-call boundary, not the intent boundary. Block `Write` and the model uses a `Bash` heredoc; block `rm` and it deletes via `perl -e 'unlink(...)'`. Denies need coverage of every tool that can achieve the same effect ([Boucle, *What Claude Code Hooks Can and Cannot Enforce*, 2026](https://dev.to/boucle2026/what-claude-code-hooks-can-and-cannot-enforce-148o)).
- **Enforcement doesn't follow into subagents, MCP, or pipe mode**: a hook that works in the parent session can silently fail in sub-agents, MCP server calls, or pipe mode. For boundaries that must hold everywhere, use OS-level controls — file permissions, network policy, containers.
- **Pattern match misses**: matchers that don't cover all variants (`npm` vs `npx` vs `npm.cmd`) let violations through silently.
- **Errors suppress feedback**: a hook that exits non-zero without valid JSON may have its error swallowed.
- **Re-entrancy loops**: a `PostToolUse` hook that invokes a tool can retrigger itself.
- **Non-deterministic input rewrites**: multiple `PreToolUse` hooks returning `updatedInput` for the same tool race — last to finish wins.
- **Scope creep**: un-scoped hooks fire on every event of that type, taxing all tool calls.

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Conditional Hook Execution](conditional-hook-execution.md)
- [Reactive Environment Hooks](reactive-environment-hooks.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
