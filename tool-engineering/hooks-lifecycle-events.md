---
title: "Hooks and Lifecycle Events: Intercepting Agent Behavior"
description: "How Hooks Work · Hook Lifecycle · Hook Lifecycle Events. For practical enforcement patterns using hooks, see Hook Catalog: Guardrails, Sandboxing, and CLI"
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

Instructions are processed by the model; hooks are processed by the shell. A model under task pressure may deprioritize an instruction — a hook executes unconditionally. Hooks enforce rules that cannot tolerate exceptions.

This works because hooks are shell subprocesses spawned by the agent runtime, not messages routed through the model's context window. The runtime intercepts the event before (or after) the model acts on it, runs the hook script, and only proceeds — or blocks — based on the hook's exit code and JSON response. The model never sees the hook logic and cannot override it through reasoning or instruction-following.

## Lifecycle Events

Agent runtimes expose hooks at several lifecycle points:

| Event | When it fires | Can block |
|-------|--------------|-----------|
| `PreToolUse` | Before any tool call executes | Yes |
| `PostToolUse` | After a tool call completes | No (observational) |
| `UserPromptSubmit` | When the user sends a message | Yes (in some tools) |
| `Stop` | When the agent finishes a turn | No |
| `InstructionsLoaded` | When CLAUDE.md or `.claude/rules/*.md` files are loaded | No |
| `SubagentStart` / `SubagentStop` | When a sub-agent is spawned or completes | No |

`PreToolUse` is the primary enforcement point — it receives tool name and inputs, can block execution, and returns a reason the model must adapt to. `PostToolUse` is the primary automation and audit point — it cannot block but triggers side effects like logging, linting, and notifications.

Claude Code's hook system is documented at [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks). GitHub Copilot's coding agent exposes `SessionStart`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, and `Stop` hooks — documented at [code.visualstudio.com/docs/copilot/customization/hooks](https://code.visualstudio.com/docs/copilot/customization/hooks).

## Hook Input and Output

Hooks receive JSON on stdin with the event context:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm install lodash"
  }
}
```

A `PreToolUse` hook blocks by returning:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use bun instead of npm"
  }
}
```

The `permissionDecisionReason` is surfaced to the model — write it as a clear redirect.

## Scoping

Hooks can be scoped with matchers to fire only for specific tools:

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

A hook without a matcher fires for every event of that type. Session-level events (`Stop`, `UserPromptSubmit`) do not support matchers.

## Hook Placement by Use Case

| Use case | Event | Approach |
|----------|-------|----------|
| Block disallowed commands | `PreToolUse` (Bash) | Exit with deny + redirect |
| Enforce package manager | `PreToolUse` (Bash) | Pattern match, deny npm, redirect to bun |
| Auto-lint after edits | `PostToolUse` (Edit/Write) | Run linter, write results to disk |
| Audit all tool calls | `PostToolUse` | Append to audit log |
| Notify on completion | `Stop` | Send desktop notification |
| Scan for secrets | `PreToolUse` (Write) | Pattern match file content, deny if found |

## Agent Identity and Worktree Context

Hook events carry additional context fields for per-agent observability in multi-agent workflows (v2.1.69):

- **`agent_id` and `agent_type`** — distinguish between main agent, sub-agents, and team members for per-agent enforcement or audit tagging.
- **`worktree`** — status hook commands receive worktree name, path, and branch info, enabling worktree-aware behavior.

`InstructionsLoaded` fires when CLAUDE.md or `.claude/rules/*.md` files are loaded — use it to log which instruction files loaded at session start for configuration consistency auditing.

## What Hooks Are Not For

Hooks enforce what the model should not decide. They are not suited for:

- **Creative choices** — architecture decisions, style preferences — model judgment is the point
- **Conversation-dependent logic** — hooks receive only the immediate tool call context, not conversation history
- **Complex workflows** — hooks are scripts, not agents; keep them short and deterministic

## Configuration Levels

Configure hooks at project level (`.claude/settings.json`, committed) or user level (`~/.claude/settings.json`, local only). Project hooks travel with the repo and enforce team conventions.

## Key Takeaways

- Hooks execute in the shell — they cannot be overridden by model task pressure
- `PreToolUse` is the enforcement point; `PostToolUse` is the automation point
- Matchers scope hooks to specific tools; session events fire unconditionally
- Project-level hooks in `.claude/settings.json` enforce team conventions for all contributors
- `InstructionsLoaded` enables auditing which instruction files loaded at session start
- `agent_id`/`agent_type` fields enable per-agent enforcement in multi-agent workflows

## Example

Enforce `bun` over `npm` for every `Bash` tool call. The hook script reads the tool input from stdin, checks for `npm` commands, and blocks with a redirect.

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

When the agent runs `npm install lodash`, the hook denies the call and the model sees: *"Use bun instead of npm. Replace npm install with bun install, npm run with bun run."* The agent retries with `bun install lodash`.

## When This Backfires

Hooks are shell subprocesses — every tool call that matches a hook incurs the subprocess startup cost. In latency-sensitive workflows, a hook that spawns a slow script on `PreToolUse` delays every matched tool invocation.

Specific failure conditions to watch for:

- **Pattern match misses**: Regex or string matchers that don't cover all variants of a disallowed command (e.g., `npm` vs `npx` vs `npm.cmd` on Windows) allow violations to slip through silently.
- **Hook errors suppress feedback**: If a hook exits non-zero without printing a valid JSON response, the runtime may silently swallow the error, leaving the agent with no redirect and no explanation.
- **Re-entrancy loops**: A `PostToolUse` hook that itself invokes a tool (e.g., runs a linter via Bash) can trigger the same hook recursively, causing infinite loops unless the hook checks the invoking context.
- **Scope creep**: Hooks without matchers fire for every event of that type. An un-scoped `PreToolUse` hook that performs expensive work degrades all tool calls, not just the targeted ones.

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Conditional Hook Execution](conditional-hook-execution.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PostToolUse Hook for BSD/GNU CLI Incompatibilities](posttooluse-bsd-gnu-detection.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md)
