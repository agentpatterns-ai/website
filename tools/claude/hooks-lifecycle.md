---
title: "Claude Code Hooks: Deterministic Lifecycle Automation"
description: "Claude Code hooks run deterministic automation at lifecycle points — shell commands, HTTP calls, or LLM prompts that fire on configured events."
aliases:
  - "Claude Code hooks"
  - "lifecycle hooks"
  - "lifecycle events"
tags:
  - agent-design
  - instructions
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-08
status: current
---

# Claude Code Hooks

> Claude Code hooks are deterministic automation at lifecycle points — shell commands, HTTP calls, or LLM prompts that fire on specific events.

Learn it hands-on: [Hooks — Deterministic Guardrails](https://learn.agentpatterns.ai/harness-engineering/hooks-deterministic-guardrails/) — guided lesson with quizzes.

## How they work

You configure [hooks](https://code.claude.com/docs/en/hooks) in `settings.json` at user, project, or local scope. They live under a top-level `hooks` object keyed by event name. Each matcher group pairs a `matcher` string with one or more `hooks` handlers of `type: "command"`, `http`, `prompt`, or `agent`. Hook input arrives on stdin as JSON rather than through environment variables, so scripts typically pipe stdin through `jq` to read tool input fields ([reference](https://code.claude.com/docs/en/hooks)).

Hooks are deterministic because the harness runs them, not the model. The harness invokes them at fixed points in the request loop: `PreToolUse` before it dispatches a tool call, `PostToolUse` after it receives the result, independent of any sampling. That guarantee makes exit code 2 a reliable block for `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, and config-change events. For post-tool and notification events, exit code 2 feeds stderr back to Claude without blocking, because the action has already run ([reference](https://code.claude.com/docs/en/hooks)). Beyond stderr, `Stop` and `SubagentStop` hooks can now return `hookSpecificOutput.additionalContext`. This gives Claude feedback and continues the turn without counting as a hook error. It inverts the earlier limit, where only `PostToolUse` hooks could inject context ([Claude Code changelog v2.1.163](https://code.claude.com/docs/en/changelog)).

## Lifecycle events

Claude Code fires 25+ hook events across session, prompt, tool, subagent, task, compaction, worktree, config, and file-change lifecycles. A representative subset:

| Event | When |
|-------|------|
| `SessionStart` | Session begins or resumes |
| `UserPromptSubmit` | User submits a prompt, before processing |
| `PreToolUse` | Before a tool call (exit 2 blocks) |
| `PermissionRequest` | Before a permission dialog |
| `PermissionDenied` | After [auto mode](auto-mode.md) denies a tool call |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `PreCompact` / `PostCompact` | Around context compaction |
| `SubagentStart` / `SubagentStop` | Around subagent runs |
| `TaskCreated` / `TaskCompleted` | Around task-tool lifecycle |
| `Stop` / [`StopFailure`](../../tool-engineering/stopfailure-hook.md) | Turn ends cleanly or via API error |
| `ConfigChange` | Settings change during a session |
| [`CwdChanged` / `FileChanged`](../../tool-engineering/reactive-environment-hooks.md) | Working dir or watched file changes |
| `WorktreeCreate` / `WorktreeRemove` | Around worktree operations |

See the [official event list](https://code.claude.com/docs/en/hooks) for the complete set and per-event matcher semantics.

## Matchers

A matcher is a string. `"*"` or an empty string matches everything. A plain identifier or pipe-separated list (`"Bash"`, `"Write|Edit"`) matches exactly. Anything with other characters parses as a JavaScript regex. What the matcher filters depends on the event — tool name for `PreToolUse` / `PostToolUse`, session source (`startup`, `resume`, `clear`, `compact`) for `SessionStart`, notification type for `Notification`, and so on ([reference](https://code.claude.com/docs/en/hooks)).

## Hooks vs prompts

Hooks are deterministic "must-do" rules — they run as shell commands regardless of the model's choices ([hooks guide](https://code.claude.com/docs/en/hooks-guide)). CLAUDE.md instructions are probabilistic "should-do" suggestions. Use hooks when compliance is non-negotiable — formatting, security checks, validation. Use prompts when flexibility is acceptable.

The `/hooks` interactive command walks through setup.

## Example

This `settings.json` snippet shows three hooks that enforce one non-negotiable rule set: block dangerous shell commands before they run, auto-format Python files after every Write or Edit, and save a progress snapshot when the session ends.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-commands.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/ruff-format.sh"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/save-progress-snapshot.sh"
          }
        ]
      }
    ]
  }
}
```

`block-dangerous-commands.sh` — hook input arrives on stdin as JSON; exit 2 blocks the call

```bash
#!/usr/bin/env bash
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)
for pattern in "rm -rf /" "dd if=/dev" ":(){ :|:& }"; do
  if echo "$COMMAND" | grep -qF "$pattern"; then
    echo "Blocked: '${pattern}' is not permitted" >&2
    exit 2
  fi
done
```

`ruff-format.sh` — read the edited path from stdin and format it in place

```bash
#!/usr/bin/env bash
FILE=$(jq -r '.tool_input.file_path' < /dev/stdin)
[[ "$FILE" == *.py ]] && ruff format "$FILE"
```

The `PreToolUse` hook fires before every Bash call. Exit code 2 cancels the call and sends the stderr message back to Claude as feedback. The `PostToolUse` hook fires after every Write or Edit call, then the script filters to `.py` files and runs `ruff format`. The `SessionEnd` hook has no matcher and fires whenever the session ends, so it is the right place to write progress files or close audit logs.

## When this backfires

Hooks are the wrong tool when the rule they encode is aspirational rather than absolute. Common failure modes:

- Hidden global state. A misbehaving agent is often a hook silently rewriting, blocking, or reformatting files. Hooks stay invisible in the transcript unless they exit non-zero, so debugging can take longer than the hook saves.
- Brittle schema coupling. Hook scripts parse `tool_input` JSON. When a tool's schema changes in a new Claude Code release — new field names, renamed events, added matcher semantics — scripts fail silently or block valid calls.
- Over-scoped blocks. A `PreToolUse` Bash blocker that matches `rm` with a substring check blocks `rm node_modules` and `echo "term"`. The false positives push users to disable the hook rather than live with them.
- Performance tax. Every `PostToolUse` hook runs synchronously on the hot path, so a slow formatter or network call slows every edit. Move expensive work to `SessionEnd` or out-of-band jobs.
- CLAUDE.md would have worked. If the rule bends gracefully under load — prefer a style, avoid a phrase — a prompt instruction fails softer than a hook rejection and keeps the model in the loop.

## Key Takeaways

- Hooks fire deterministically at documented lifecycle events across session, tool, subagent, compaction, worktree, and file-change phases
- Hook input arrives on stdin as JSON — scripts use `jq` to read `tool_input` fields
- Exit code 2 blocks `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, and config-change events; for post-hooks and notifications it only feeds stderr back to Claude
- Use hooks for non-negotiable rules; use CLAUDE.md for flexible guidance
- Matchers are strings (exact, pipe-separated, or regex) whose meaning depends on the event

## Related

- [Hooks vs Prompts](../../instructions/hooks-vs-prompts.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../../tool-engineering/hook-catalog.md)
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](../../tool-engineering/precompact-hook-compaction-veto.md) — using `PreCompact` exit 2 or `decision: block` to defer compaction past mid-task work
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](posttooluse-auto-formatting.md)
- [Extension Points: When to Use What](extension-points.md)
- [Sub-Agents](sub-agents.md)
- [Claude Agent SDK](agent-sdk.md)
- [Claude Code /batch and Worktrees](batch-worktrees.md)
