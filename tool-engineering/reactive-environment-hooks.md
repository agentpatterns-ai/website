---
title: "Reactive Environment Hooks: CwdChanged and FileChanged"
description: "Use CwdChanged and FileChanged hook events to automatically reload environment managers like direnv when the agent changes directory or edits a config file — without requiring a prompt."
tags:
  - agent-design
  - claude
aliases:
  - reactive hooks
  - CwdChanged hook
  - FileChanged hook
---

# Reactive Environment Hooks: CwdChanged and FileChanged

> CwdChanged and FileChanged hooks let the agent trigger shell-level side effects in response to directory changes and file modifications — the same trigger model that direnv and similar tools use — without requiring a prompt.

## The Problem

Developers using Claude Code across projects with different toolchains — Node versions, Python environments, Nix shells — must either pre-configure the environment before the session or manually prompt the agent to reload it after a directory change. Neither option is reliable: pre-configuration is fragile, and prompts are easy to forget.

Claude Code v2.1.83 added two state-change hook events that address this: [`CwdChanged`](https://code.claude.com/docs/en/hooks) fires when the agent's working directory changes; [`FileChanged`](https://code.claude.com/docs/en/hooks) fires when a watched file is modified on disk. Both are observational — they cannot block execution — but they have access to `CLAUDE_ENV_FILE`, the same environment persistence mechanism used by `SessionStart`, which lets hooks propagate shell variables to all subsequent Bash tool calls.

## CwdChanged

Fires after every working directory change (e.g., after the agent runs `cd`). No matcher is supported — it fires unconditionally.

Input payload:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project/src",
  "hook_event_name": "CwdChanged"
}
```

The `cwd` field contains the new directory path. Use it to detect which project the agent has entered and load the appropriate environment.

## FileChanged

Fires when a watched file is created, modified, or deleted. The `matcher` field specifies which filenames to watch using pipe-separated literal names — not regex patterns, unlike PreToolUse/PostToolUse matchers.

Input payload:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project",
  "hook_event_name": "FileChanged",
  "file_path": "/Users/my-project/.env",
  "change_type": "modified"
}
```

`change_type` is one of `"created"`, `"modified"`, or `"deleted"`.

## Environment Persistence via CLAUDE_ENV_FILE

Both events expose the `CLAUDE_ENV_FILE` environment variable. Writing `KEY=value` lines to this file persists variables into the agent's subsequent Bash invocations — the same mechanism `SessionStart` hooks use. Without this, environment changes made inside a hook script don't reach Claude Code's tool execution context.

```bash
# Inside any CwdChanged or FileChanged hook:
export MY_VAR="value"
echo "MY_VAR=$MY_VAR" >> "$CLAUDE_ENV_FILE"
```

## Example

Auto-load [direnv](https://direnv.net/) whenever the agent changes directory. direnv reads `.envrc` files and exports environment variables scoped to that directory tree — the canonical use case for `CwdChanged`.

**`.claude/hooks/sync-direnv.sh`**:

```bash
#!/bin/bash

if command -v direnv &> /dev/null; then
  direnv allow
  if [ -n "$CLAUDE_ENV_FILE" ]; then
    eval "$(direnv export bash)" >> "$CLAUDE_ENV_FILE"
  fi
fi

exit 0
```

**`.claude/settings.json`**:

```json
{
  "hooks": {
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/sync-direnv.sh"
          }
        ]
      }
    ]
  }
}
```

With this in place, moving into any project subdirectory automatically reloads the directory's `.envrc` — Node version, Python virtualenv, AWS profile, or any other variable direnv manages.

For `FileChanged`, use the same `CLAUDE_ENV_FILE` pattern but scope the hook to specific config filenames:

```json
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": ".env|.envrc|.env.local",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/sync-direnv.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## Key Takeaways

- `CwdChanged` fires on every directory change — no matcher, no blocking, observational only
- `FileChanged` matches literal filenames (pipe-separated); use it to reload config when tracked files change
- Write to `CLAUDE_ENV_FILE` to persist environment variables to subsequent Bash calls — without it, hook-level changes don't propagate
- Both events compose with existing PreToolUse/PostToolUse hooks; they add a new trigger class (state-change) to the lifecycle
- direnv is the canonical integration: one hook covers all toolchain switching for the entire repo tree

## Unverified

- nvm, rbenv, and pyenv are implied by the direnv pattern but are not individually listed as examples in the official documentation

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PostToolUse BSD/GNU Detection](posttooluse-bsd-gnu-detection.md)
