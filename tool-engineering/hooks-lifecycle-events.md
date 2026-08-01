---
title: "Hooks and Lifecycle Events: Intercepting Agent Behavior"
term: "Hooks and Lifecycle Events"
description: "Hooks run deterministic code at defined points in an agent's execution — before and after tool calls, at session boundaries — for enforcement and audit."
aliases:
  - How Hooks Work
  - Hook Lifecycle
  - Hook Lifecycle Events
tags:
  - agent-design
  - tool-agnostic
  - tool-engineering
last_reviewed: 2026-07-16
maturity: established
---

# Hooks and Lifecycle Events: Intercepting Agent Behavior

> Hooks run deterministic code at defined points in an agent's execution — around tool calls and session boundaries — enforcing what instructions cannot guarantee.

Related lesson: [Hooks & Deterministic Lifecycle Enforcement](https://learn.agentpatterns.ai/tool-engineering/hooks-and-deterministic-enforcement/) — this concept features in a hands-on lesson with quizzes.

!!! note "Also known as"
    How Hooks Work · Hook Lifecycle · Hook Lifecycle Events. For enforcement patterns that use hooks, see [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md).

!!! info "Canonical home for hooks content"
    Canonical entry point for "hooks" content site-wide — hook pages elsewhere link here for the lifecycle model rather than restate it (see [Related](#related)).

## The role of hooks

The model processes instructions. The shell runs hooks. Under task pressure the model may deprioritize an instruction, but a hook always runs. The runtime spawns the hook as a `PreToolUse` or `PostToolUse` subprocess before or after the model acts. It then proceeds or blocks based on the hook's exit code and JSON response. The model cannot override hook logic through reasoning.

## Lifecycle events

Agent runtimes expose hooks at these points:

| Event | When it fires | Can block |
|-------|--------------|-----------|
| `PreToolUse` | Before a tool call executes | Yes |
| `PostToolUse` | After a tool call completes | No |
| `UserPromptSubmit` | User sends a message | Yes (some tools) |
| `Stop` | Agent finishes a turn | No |
| `InstructionsLoaded` | CLAUDE.md or `.claude/rules/*.md` loads | No |
| `SubagentStart` / `SubagentStop` | Sub-agent spawns or completes | No |

`PreToolUse` enforces. It receives the tool name and inputs, can block the call, and returns a reason the model must adapt to. `PostToolUse` automates. It only observes, but it can trigger side effects like logging or linting.

See [Claude Code hooks](https://code.claude.com/docs/en/hooks) and [Copilot hooks](https://code.visualstudio.com/docs/copilot/customization/hooks). Cursor exposes the same turn-lifecycle surface for its cloud agents — `beforeSubmitPrompt`, `afterAgentResponse`, `afterAgentThought`, `subagentStart`, `stop`, and compaction events — so agents can build self-correcting loops around these points ([Cursor changelog](https://cursor.com/changelog/side-chat)).

## Hook input and output

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

The model sees the `permissionDecisionReason`, so write it as a redirect.

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

Un-matched hooks fire on every event of that type. Session-level events such as `Stop` and `UserPromptSubmit` do not support matchers.

## Hook placement by use case

| Use case | Event | Approach |
|----------|-------|----------|
| Block disallowed commands | `PreToolUse` (Bash) | Deny + redirect |
| Enforce package manager | `PreToolUse` (Bash) | Match `npm`, redirect to `bun` |
| Auto-lint after edits | `PostToolUse` (Edit/Write) | Run linter |
| Audit tool calls | `PostToolUse` | Append to log |
| Notify on completion | `Stop` | Desktop notification |
| Scan for secrets | `PreToolUse` (Write) | Match content, deny if found |

## Agent identity and worktree context

In multi-agent workflows (Claude Code v2.1.69), hook events carry extra context:

- `agent_id` / `agent_type` — distinguish the main agent, sub-agents, and team members for per-agent enforcement or audit tagging
- `worktree` — status hooks receive the worktree name, path, and branch

`InstructionsLoaded` fires when CLAUDE.md or `.claude/rules/*.md` load. Log it to audit which files were in effect at session start.

## What hooks are not for

[Hooks enforce what the model should not decide](../instructions/hooks-vs-prompts.md). Avoid them for:

- Creative choices like architecture or style, where model judgment is the point
- Conversation-dependent logic, since a hook sees only the immediate tool call
- Complex workflows — hooks are scripts, so keep them short and deterministic

## Configuration levels

Configure at project level (`.claude/settings.json`, committed) or user level (`~/.claude/settings.json`, local). Project hooks travel with the repo and enforce team conventions.

## FAQ

**If the model cannot override a hook, can it route around one?**

Yes. Hooks enforce at the tool-call boundary, not the intent boundary. Block `Write` and the model reaches for a `Bash` heredoc; block `rm` and it deletes through `perl -e 'unlink(...)'`. A deny only holds when it covers every tool capable of the same effect, so enumerate the alternatives rather than blocking the most obvious one.

**Do hooks still fire inside sub-agents, MCP calls, and pipe mode?**

Not reliably. A hook that works in the parent session can silently fail in sub-agents, MCP server calls, or pipe mode. For a boundary that must hold everywhere, put it below the agent: OS-level controls such as file permissions, network policy, and containers. Widening the matcher is not a substitute, since un-scoped hooks fire on every event of that type and tax all tool calls.

**What does not belong in a hook?**

Anything that needs judgment or conversation. Creative choices such as architecture and style are exactly where model judgment is the point. Conversation-dependent logic fails because a hook sees only the immediate tool call. Complex workflows do not fit either, since hooks are scripts and stay short and deterministic. Hooks enforce what the model should not decide.

## Key Takeaways

- Hooks execute in the shell — the model cannot override them
- `PreToolUse` enforces; `PostToolUse` automates
- Matchers scope hooks to specific tools; session events fire unconditionally
- Project hooks in `.claude/settings.json` enforce team conventions
- `InstructionsLoaded` audits which instruction files loaded at session start
- `agent_id` / `agent_type` enable per-agent enforcement in multi-agent workflows

## Example

Enforce `bun` over `npm` for every `Bash` call. The hook reads tool input from stdin, matches `npm` commands, and blocks with a redirect.

`.claude/hooks/enforce-bun.sh`:

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

`.claude/settings.json`:

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

## When this backfires

Hooks are subprocesses. Each matched call pays the startup cost, so a slow `PreToolUse` script delays every matched invocation.

- The model routes around blocks. Hooks enforce at the tool-call boundary, not the intent boundary. Block `Write` and the model uses a `Bash` heredoc; block `rm` and it deletes via `perl -e 'unlink(...)'`. Denies need to cover every tool that can achieve the same effect ([Boucle, *What Claude Code Hooks Can and Cannot Enforce*, 2026](https://dev.to/boucle2026/what-claude-code-hooks-can-and-cannot-enforce-148o)).
- Enforcement does not follow into sub-agents, MCP, or pipe mode. A hook that works in the parent session can silently fail in sub-agents, MCP server calls, or pipe mode. For boundaries that must hold everywhere, use OS-level controls such as file permissions, network policy, and containers.
- Pattern-match misses. Matchers that do not cover all variants, such as `npm`, `npx`, and `npm.cmd`, let violations through silently.
- Errors suppress feedback. A hook that exits non-zero without valid JSON may have its error swallowed.
- Re-entrancy loops. A `PostToolUse` hook that invokes a tool can retrigger itself.
- Non-deterministic input rewrites. When several `PreToolUse` hooks return `updatedInput` for the same tool, they race and the last to finish wins.
- Scope creep. Un-scoped hooks fire on every event of that type, taxing all tool calls.

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Conditional Hook Execution](conditional-hook-execution.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md)
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md)
- [Enforcing Agent Behavior with Hooks](../instructions/enforcing-agent-behavior-with-hooks.md) — block, rewrite, and completion-gate patterns built on these lifecycle events
