---
title: "Reactive Environment Hooks: CwdChanged and FileChanged"
term: "Reactive Environment Hooks"
description: "CwdChanged and FileChanged hook events reload environment managers like direnv when the agent changes directory or edits a config file."
tags:
  - agent-design
  - claude
  - tool-engineering
aliases:
  - reactive hooks
  - CwdChanged hook
  - FileChanged hook
last_reviewed: 2026-05-27
maturity: adopted
---

# Reactive Environment Hooks: CwdChanged and FileChanged

> CwdChanged and FileChanged hooks let the agent trigger shell-level side effects in response to directory changes and file modifications — the same trigger model that direnv and similar tools use — without requiring a prompt.

## The problem

You work across projects with different toolchains — Node versions, Python environments, Nix shells. With Claude Code you have two options: pre-configure the environment before the session, or prompt the agent to reload it after each directory change. Neither is reliable. Pre-configuration is fragile, and prompts are easy to forget.

Claude Code [v2.1.83](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) added two state-change hook events to fix this. [`CwdChanged`](https://code.claude.com/docs/en/hooks) fires when the agent's working directory changes. [`FileChanged`](https://code.claude.com/docs/en/hooks) fires when a watched file changes on disk. Both are observational — they cannot block execution. But both can write to `CLAUDE_ENV_FILE`, the same environment persistence mechanism `SessionStart` uses. That lets a hook pass shell variables to every later Bash tool call.

## CwdChanged

Fires after every working directory change, for example when the agent runs `cd`. No matcher is supported. It fires unconditionally.

Input payload:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/my-project/src",
  "hook_event_name": "CwdChanged"
}
```

The `cwd` field holds the new directory path. Use it to detect which project the agent has entered, then load the matching environment.

## FileChanged

Fires when a watched file is created, modified, or deleted. The `matcher` field lists which filenames to watch, as pipe-separated literal names. These are not regex patterns, unlike PreToolUse and PostToolUse matchers.

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

## Environment persistence via CLAUDE_ENV_FILE

Both events expose the `CLAUDE_ENV_FILE` environment variable. Write `KEY=value` lines to this file and the variables persist into the agent's later Bash calls — the same mechanism `SessionStart` hooks use. Without it, environment changes made inside a hook script never reach Claude Code's tool execution context.

```bash
# Inside any CwdChanged or FileChanged hook:
export MY_VAR="value"
echo "MY_VAR=$MY_VAR" >> "$CLAUDE_ENV_FILE"
```

## Example

Auto-load [direnv](https://direnv.net/) whenever the agent changes directory. direnv reads `.envrc` files and exports environment variables scoped to that directory tree. This is the main use case for `CwdChanged`.

`.claude/hooks/sync-direnv.sh`:

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

`.claude/settings.json`:

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

With this in place, moving into any project subdirectory reloads that directory's `.envrc` automatically — the Node version, Python virtualenv, AWS profile, or any other variable direnv manages.

For `FileChanged`, use the same `CLAUDE_ENV_FILE` pattern, but scope the hook to specific config filenames:

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

## When this backfires

- direnv not available: the hook silently does nothing when direnv is absent. On Windows dev containers or minimal CI images, you need a fallback or a different environment loader.
- Malformed `.envrc`: `direnv allow` succeeds, but `direnv export bash` fails on syntax errors in `.envrc`. The hook exits 0, `CLAUDE_ENV_FILE` receives no writes, and the agent proceeds with a stale environment. No error surfaces.
- CwdChanged fires unconditionally: every `cd` triggers the hook, including directory changes inside a single task. On repos with many subdirectories, this adds latency to each directory change.
- Observational constraint: hooks cannot block the agent. If environment loading fails, the next Bash call runs in the wrong environment, with no signal to the agent.
- FileChanged is blind to Bash-driven edits: `FileChanged` only fires for changes made by Claude Code's Edit and Write tools, not for files changed through the Bash tool ([claude-code#44925](https://github.com/anthropics/claude-code/issues/44925)). If the agent runs `mise use`, appends to `.envrc` with a shell redirect, or otherwise edits a watched file through Bash, the hook does not fire and the environment stays stale. Trigger a reload yourself, or rely on `CwdChanged` instead.

## Key Takeaways

- `CwdChanged` fires on every directory change — no matcher, no blocking, observational only
- `FileChanged` matches literal filenames (pipe-separated); use it to reload config when tracked files change
- Write to `CLAUDE_ENV_FILE` to persist environment variables to subsequent Bash calls — without it, hook-level changes don't propagate
- Both events compose with existing PreToolUse/PostToolUse hooks; they add a new trigger class (state-change) to the lifecycle
- direnv is the canonical integration: one hook covers all toolchain switching for the entire repo tree

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation](on-demand-skill-hooks.md)
- [PostToolUse BSD/GNU Detection](posttooluse-bsd-gnu-detection.md)
