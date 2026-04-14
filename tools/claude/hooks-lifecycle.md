---
title: "Claude Code Hooks: Deterministic Lifecycle Automation"
description: "Deterministic automation at lifecycle points — shell commands, HTTP calls, or LLM prompts that fire on specific events. Hooks are configured in settings.json"
aliases:
  - "Claude Code hooks"
  - "lifecycle hooks"
  - "lifecycle events"
tags:
  - agent-design
  - instructions
  - claude
---

# Claude Code Hooks

> Deterministic automation at lifecycle points — shell commands, HTTP calls, or LLM prompts that fire on specific events.

## How They Work

[Hooks](https://code.claude.com/docs/en/hooks) are configured in `settings.json` (user, project, or local scope) under a top-level `hooks` object keyed by event name. Each matcher group pairs a `matcher` string with one or more `hooks` handlers of `type: "command"`, `http`, `prompt`, or `agent`. Hook input arrives on stdin as JSON rather than through environment variables, so scripts typically pipe stdin through `jq` to extract tool input fields ([reference](https://code.claude.com/docs/en/hooks)).

Hooks are deterministic because the harness — not the model — runs them at fixed points in the request loop: the harness invokes `PreToolUse` before dispatching a tool call and `PostToolUse` after receiving the result, independent of any sampling. That guarantee is what makes exit code 2 a reliable block for `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, and config-change events; for post-tool and notification events, exit code 2 feeds stderr back to Claude without blocking because the action has already run ([reference](https://code.claude.com/docs/en/hooks)).

## Lifecycle Events

Claude Code fires 25+ hook events across session, prompt, tool, subagent, task, compaction, worktree, config, and file-change lifecycles. A representative subset:

| Event | When |
|-------|------|
| `SessionStart` | Session begins or resumes |
| `UserPromptSubmit` | User submits a prompt, before processing |
| `PreToolUse` | Before a tool call (exit 2 blocks) |
| `PermissionRequest` | Before a permission dialog |
| `PermissionDenied` | After auto-mode denies a tool call |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `PreCompact` / `PostCompact` | Around context compaction |
| `SubagentStart` / `SubagentStop` | Around subagent runs |
| `TaskCreated` / `TaskCompleted` | Around task-tool lifecycle |
| `Stop` / `StopFailure` | Turn ends cleanly or via API error |
| `ConfigChange` | Settings change during a session |
| `CwdChanged` / `FileChanged` | Working dir or watched file changes |
| `WorktreeCreate` / `WorktreeRemove` | Around worktree operations |

See the [official event list](https://code.claude.com/docs/en/hooks) for the complete set and per-event matcher semantics.

## Matchers

A matcher is a string: `"*"` or empty matches all; a plain identifier or pipe-separated list (`"Bash"`, `"Write|Edit"`) matches exactly; anything with other characters is parsed as a JavaScript regex. What the matcher filters depends on the event — tool name for `PreToolUse` / `PostToolUse`, session source (`startup`, `resume`, `clear`, `compact`) for `SessionStart`, notification type for `Notification`, and so on ([reference](https://code.claude.com/docs/en/hooks)).

## Hooks vs Prompts

Hooks are deterministic "must-do" rules. CLAUDE.md instructions are probabilistic "should-do" suggestions. Use hooks when compliance is non-negotiable — formatting, security checks, validation. Use prompts when flexibility is acceptable.

The `/hooks` interactive command walks through setup.

## Example

The following `settings.json` snippet shows three hooks that together enforce a non-negotiable rule set: block dangerous shell commands before execution, auto-format Python files after every Write or Edit, and save a progress snapshot when the session ends.

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

**`block-dangerous-commands.sh`** — hook input arrives on stdin as JSON; exit 2 blocks the call

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

**`ruff-format.sh`** — read the edited path from stdin and format it in place

```bash
#!/usr/bin/env bash
FILE=$(jq -r '.tool_input.file_path' < /dev/stdin)
[[ "$FILE" == *.py ]] && ruff format "$FILE"
```

The `PreToolUse` hook fires before every Bash call; exit code 2 cancels the tool call and sends the stderr message back to Claude as feedback. The `PostToolUse` hook fires after every Write or Edit call, then the script filters to `.py` files and runs `ruff format`. The `SessionEnd` hook has no matcher and fires unconditionally when the session terminates, making it the right place to write progress files or close audit logs.

## When This Backfires

Hooks are the wrong tool when the rule they encode is aspirational rather than absolute. Common failure modes:

- **Hidden global state.** A misbehaving agent is often a hook silently rewriting, blocking, or reformatting files. Because hooks are invisible in the transcript unless they exit non-zero, debugging can take longer than the hook saves.
- **Brittle schema coupling.** Hook scripts parse `tool_input` JSON; when a tool's schema changes in a new Claude Code release (new field names, renamed events, added matcher semantics), scripts fail silently or block legitimate calls.
- **Over-scoped blocks.** A `PreToolUse` Bash blocker that matches `rm` with a substring check will block `rm node_modules` and `echo "term"` — pushing users to disable the hook entirely rather than accept the false positives.
- **Performance tax.** Every `PostToolUse` hook runs synchronously on the hot path; a slow formatter or network call inflates every edit. Move expensive work to `SessionEnd` or async out-of-band jobs.
- **CLAUDE.md would have worked.** If the rule bends gracefully under load (prefer a style, avoid a phrase), a prompt instruction fails softer than a hook rejection and keeps the model in the loop.

## Key Takeaways

- Hooks fire deterministically at documented lifecycle events across session, tool, subagent, compaction, worktree, and file-change phases
- Hook input arrives on stdin as JSON — scripts use `jq` to read `tool_input` fields
- Exit code 2 blocks `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, and config-change events; for post-hooks and notifications it only feeds stderr back to Claude
- Use hooks for non-negotiable rules; use CLAUDE.md for flexible guidance
- Matchers are strings (exact, pipe-separated, or regex) whose meaning depends on the event

## Related

- [Sub-Agents](sub-agents.md)
- [Agent Teams](agent-teams.md)
- [Claude Agent SDK](agent-sdk.md)
- [Claude Code /batch and Worktrees](batch-worktrees.md)
- [Extension Points: When to Use What](extension-points.md)
- [Session Scheduling](session-scheduling.md)
- [Hooks vs Prompts](../../verification/hooks-vs-prompts.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../../tool-engineering/hook-catalog.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../../workflows/posttooluse-auto-formatting.md)
