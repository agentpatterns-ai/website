---
title: "PostToolUse Hooks: Auto-Formatting on Every File Edit"
description: "Configure a PostToolUse hook to run formatters automatically after every file Claude writes, removing the round-trip cost of prompting Claude to fix style."
tags:
  - workflows
  - claude
---

# PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit

> Configure a `PostToolUse` hook so that formatting and linting run automatically after every file Claude writes or edits, removing the round-trip cost of prompting Claude to fix style.

## The Problem

Claude does not automatically reformat files to match project style after writing them. The typical responses to this:

- Prompt Claude to run the formatter after each edit — burns tokens on a predictable, mechanical task
- Run formatters manually — easy to forget, breaks flow
- Accept inconsistent formatting in agent-produced code — creates noise in diffs and review

All three are worse than moving enforcement to the infrastructure layer. A `PostToolUse` hook runs the formatter once, unconditionally, after every file write, regardless of whether Claude or a human made the edit.

## How PostToolUse Hooks Work

[`PostToolUse`](https://code.claude.com/docs/en/hooks) fires after a tool call succeeds. For file-editing tools (`Edit`, `Write`, `NotebookEdit`), Claude Code passes a JSON object to the hook on stdin that includes `tool_input.file_path` — the path to the file just written.

The hook extracts that path and passes it to the formatter:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

The `"Edit|Write"` matcher is a regex that limits the hook to file-editing tools only. Without a matcher, the hook would fire on every tool call including `Bash`, `Read`, and `Glob`.

## Composing Multiple Quality Checks

Multiple hooks on the same event [fire in parallel](https://code.claude.com/docs/en/hooks#hook-execution). If you need a specific sequence — formatter first, then linter — chain them in a single command:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FILE=$(jq -r '.tool_input.file_path') && npx prettier --write \"$FILE\" && npx eslint --fix \"$FILE\""
          }
        ]
      }
    ]
  }
}
```

For language-specific formatting, use file extension matching in the command rather than in the matcher (the matcher filters on tool name, not file path):

```bash
#!/bin/bash
# .claude/hooks/format-by-type.sh
FILE=$(jq -r '.tool_input.file_path')

case "$FILE" in
  *.py)  black "$FILE" ;;
  *.ts|*.tsx|*.js|*.jsx)  npx prettier --write "$FILE" ;;
  *.go)  gofmt -w "$FILE" ;;
  *.rs)  rustfmt "$FILE" ;;
esac
```

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format-by-type.sh"
          }
        ]
      }
    ]
  }
}
```

Use `$CLAUDE_PROJECT_DIR` to reference hook scripts by absolute path, regardless of the working directory when the hook fires ([docs](https://code.claude.com/docs/en/hooks#reference-scripts-by-path)).

## Async Formatting for Long-Running Formatters

By default, `PostToolUse` hooks [block the agent loop until the command completes](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background). For formatters that take more than a few seconds, set `"async": true` to run the formatter in the background without blocking Claude's next step:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format-by-type.sh",
            "async": true
          }
        ]
      }
    ]
  }
}
```

For most formatters (`black`, `prettier`, `gofmt`) the blocking default is appropriate — they run in milliseconds and the agent benefits from seeing the formatted result before continuing.

## Hook Configuration Location

Add the hook to `.claude/settings.json` in the project root to share it with the team via version control. The hook then applies to every contributor's Claude Code session, not just yours:

| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes — commit to repo |
| `.claude/settings.local.json` | Single project | No — gitignored |

Project-level hooks make formatting automatic for all team members without any per-user setup ([docs](https://code.claude.com/docs/en/hooks#hook-locations)).

## PostToolUse vs PreToolUse for Formatting

`PostToolUse` is the correct event for formatting — the file must exist and be written before a formatter can run. `PreToolUse` on the same tools fires before the write and cannot access the file content Claude is about to write.

`PostToolUse` hooks also cannot block the tool call (the file is already written). They are side-effect hooks, not gates. If you want to block writes to specific files, use [`PreToolUse` with a file path check](https://code.claude.com/docs/en/hooks#pretooluse) instead.

## Key Takeaways

- `PostToolUse` with an `"Edit|Write"` matcher fires after every file write and receives `tool_input.file_path` on stdin
- Extract the path with `jq -r '.tool_input.file_path'` and pass it to the formatter directly — no glob scanning needed
- Chain formatter and linter in one command to enforce ordering; parallel handlers fire concurrently
- Use a script with file-extension dispatch for multi-language projects
- Commit the hook to `.claude/settings.json` to share it across the team with no per-user configuration
- Set `"async": true` only for formatters that are slow enough to noticeably block the agent loop

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
- [Architecting a Central Repo for Shared Agent Standards](central-repo-shared-agent-standards.md)
- [Claude Code ↔ Copilot CLI: Changelog-Driven Feature Parity](changelog-driven-feature-parity.md)
