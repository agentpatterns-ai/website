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

[Hooks](https://code.claude.com/docs/en/hooks) are configured in `settings.json` (user, project, or local scope). Each hook specifies an event, optional matchers to filter when it fires, and a command to execute. Exit code 2 blocks the operation and sends stderr back to Claude as feedback.

## Lifecycle Events

| Event | When |
|-------|------|
| `SessionStart` | Session begins |
| `SessionEnd` | Session ends |
| `InstructionsLoaded` | Instructions are loaded |
| `UserPromptSubmit` | User submits a prompt |
| `PermissionRequest` | A permission is requested |
| `PreToolUse` | Before a tool is called |
| `PostToolUse` | After a tool completes |
| `PostToolUseFailure` | After a tool call fails |
| `PreCompact` | Before context compaction |
| `Notification` | Claude sends a notification |
| `Stop` | Claude stops responding |
| `ConfigChange` | Configuration changes |
| `SubagentStart` | A sub-agent starts |
| `SubagentStop` | A sub-agent stops |
| `WorktreeCreate` | A worktree is created |
| `WorktreeRemove` | A worktree is removed |
| `TeammateIdle` | A teammate is about to go idle (teams) |
| `TaskCompleted` | A task is marked complete (teams) |

## Matchers

Matchers filter when hooks fire. For `PreToolUse` and `PostToolUse`, match on tool name (e.g., only fire for the Bash tool).

## Hooks vs Prompts

Hooks are deterministic "must-do" rules. CLAUDE.md instructions are probabilistic "should-do" suggestions. Use hooks when compliance is non-negotiable — formatting, security checks, validation. Use prompts when flexibility is acceptable.

The `/hooks` interactive command walks through setup.

## Example

The following `settings.json` snippet shows three hooks that together enforce a non-negotiable rule set: block dangerous shell commands before execution, auto-format Python files after every write, and save a progress snapshot when the session ends.

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": { "tool_name": "Bash" },
      "command": "bash ~/.claude/hooks/block-dangerous-commands.sh"
    },
    {
      "event": "PostToolUse",
      "matcher": { "tool_name": "Write", "file_pattern": "**/*.py" },
      "command": "ruff format \"${CLAUDE_TOOL_OUTPUT_FILE}\""
    },
    {
      "event": "SessionEnd",
      "command": "bash ~/.claude/hooks/save-progress-snapshot.sh"
    }
  ]
}
```

**`block-dangerous-commands.sh`** — exit 2 to block the call and send stderr to Claude

```bash
#!/usr/bin/env bash
COMMAND="$CLAUDE_TOOL_INPUT_COMMAND"
for pattern in "rm -rf /" "dd if=/dev" ":(){ :|:& }"; do
  if echo "$COMMAND" | grep -qF "$pattern"; then
    echo "Blocked: '${pattern}' is not permitted" >&2
    exit 2
  fi
done
```

The `PreToolUse` hook fires before every Bash call; exit code 2 cancels the tool call and sends the stderr message back to Claude as feedback. The `PostToolUse` hook fires after every Write call that matches `**/*.py`, running `ruff format` silently without blocking. The `SessionEnd` hook fires unconditionally when the session terminates, making it the right place to write progress files or close audit logs.

## Key Takeaways

- Hooks fire deterministically at 18 lifecycle events
- Exit code 2 blocks operations and provides feedback to Claude
- Use hooks for non-negotiable rules; use CLAUDE.md for flexible guidance
- Matchers let you scope hooks to specific tools or events

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
