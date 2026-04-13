---
title: "Conditional Hook Execution: Filter Hooks by Tool Pattern"
description: "Use the if field on Claude Code hook handlers to match tool name and arguments together, skipping the subprocess entirely for non-matching calls."
tags:
  - agent-design
  - workflows
  - claude
---

# Conditional Hook Execution: Filter Hooks by Tool Pattern

> Use the `if` field on hook handlers to declare which tool calls a hook applies to — preventing subprocess spawns for non-matching calls without embedding filter logic in the hook script itself.

## The Problem

Claude Code hooks run synchronously in the agent loop. A `PreToolUse` hook registered on `Bash` fires for every Bash call — including trivial reads like `ls` or `echo` — and spawns a subprocess each time. With many hooks registered or in long sessions, this adds measurable overhead to every turn.

Before v2.1.85, the workaround was to put the filter inside the hook script:

```bash
#!/bin/bash
COMMAND=$(jq -r '.tool_input.command')
# Only act on git commands — exit early otherwise
if ! echo "$COMMAND" | grep -qE '^git '; then
  exit 0
fi
# ... enforcement logic
```

This still spawns a subprocess to immediately exit. The filtering happens inside the process, not before it.

## The `if` Field

Claude Code v2.1.85 introduced an `if` field on individual hook handlers. It uses [permission rule syntax](https://code.claude.com/docs/en/permissions) — the same syntax as `allow`/`deny` rules — to filter by both tool name and arguments. The full `if` field behavior is documented in the [hooks reference](https://code.claude.com/docs/en/hooks-guide#filter-by-tool-name-and-arguments-with-the-if-field).

The execution flow:

```
Tool call fires
  → Matcher checks tool name (e.g., "Bash")
    → if condition checks tool name + arguments (e.g., "Bash(git *)")
      → Hook handler spawns only when both match
```

When `if` does not match, the handler process is never spawned. The filter is evaluated in Claude Code's process before any subprocess is launched.

## Configuration

**Before** — inline filter inside the script:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-git.sh"
          }
        ]
      }
    ]
  }
}
```

**After** — declarative `if` field on the handler:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git *)",
            "command": ".claude/hooks/validate-git.sh"
          }
        ]
      }
    ]
  }
}
```

The hook script no longer needs to handle non-git Bash calls — they never reach it.

## Syntax

The `if` value follows `ToolName(argument_pattern)`:

| `if` value | Matches |
|------------|---------|
| `Bash(git *)` | Bash calls where the command starts with `git` |
| `Bash(rm *)` | Bash calls where the command starts with `rm` |
| `Edit(*.ts)` | Edit calls on TypeScript files |
| `Write(src/*)` | Write calls targeting the `src/` directory |
| `Write(**.py)` | Write calls on any Python file (recursive glob) |

The `if` field is only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`. On session-level events, a hook with `if` set never runs.

Compound commands (`ls && git push`) and env-var prefixes (`FOO=bar git push`) are handled correctly — the pattern is matched against each subcommand independently, so `Bash(git *)` does not match `ls && git push` as a single string.

## Composing Multiple Hooks

The `if` field makes it practical to register multiple targeted handlers under a single event, each with its own condition:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git push*)",
            "command": ".claude/hooks/block-push-main.sh"
          },
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": ".claude/hooks/block-rm.sh"
          },
          {
            "type": "command",
            "if": "Bash(npm *)",
            "command": ".claude/hooks/enforce-bun.sh"
          }
        ]
      }
    ]
  }
}
```

Each handler fires only for its matching call pattern. A `git status` call matches the `Bash` matcher but triggers none of the handlers — no subprocesses are spawned.

## When This Backfires

The `if` field is not always the right choice:

- **Version pinning requirement**: the `if` field requires Claude Code v2.1.85 or later. Teams running mixed or older installations must keep the filter inside the hook script to avoid silently skipping hooks on earlier versions.
- **Reduced observability**: a hook that never spawns leaves no trace — no subprocess, no log entry. In-script filtering at least exits with code 0 and can log its decisions. If you need an audit trail of every hook evaluation (including non-matches), keep the filter inside the script.
- **Pattern mismatch on edge cases**: permission-rule syntax uses a single `*` that matches across spaces, so `Bash(git *)` matches `git push origin main` as expected but also matches `git` with any multi-word argument. Test patterns against your actual command set before relying on them in production hooks.

## Key Takeaways

- The `if` field filters hook handlers before spawning a subprocess — non-matching calls have zero overhead
- Syntax is `ToolName(argument_pattern)`, using the same permission-rule format as allow/deny rules
- Works on tool events only (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`)
- Compose multiple targeted handlers under one matcher instead of one handler with branching script logic
- Introduced in Claude Code v2.1.85; earlier versions ignore the `if` field and run the hook on every matched call

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PostToolUse Hook for BSD/GNU CLI Incompatibilities](posttooluse-bsd-gnu-detection.md)
- [Reactive Environment Hooks: CwdChanged and FileChanged](reactive-environment-hooks.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
