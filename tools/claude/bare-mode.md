---
title: "Claude Code --bare Flag"
description: "The --bare flag strips Claude Code down to its core tools and skips all local configuration discovery, making scripted calls reproducible across every machine."
aliases:
  - "claude bare mode"
  - "claude --bare flag"
  - "headless CI agent mode"
tags:
  - claude
  - workflows
  - github-actions
---

# Claude Code `--bare` Flag

> Skip all local configuration discovery for deterministic, faster scripted calls.

Added in [v2.1.81 (March 20, 2026)](https://code.claude.com/docs/en/changelog), `--bare` is the recommended mode for all scripted and SDK uses of Claude Code. Anthropic has stated it will become the default for `-p` in a future release ([headless docs](https://code.claude.com/docs/en/headless)).

## What `--bare` Skips

Without `--bare`, `claude -p` loads the same context as an interactive session: hooks from `~/.claude`, MCP servers from `.mcp.json`, CLAUDE.md files, skills, plugins, and auto-memory. On a developer's machine this is useful; in CI it is a liability — a teammate's local hook or an MCP server in the repo can change behavior between runs.

`--bare` skips all of that ([CLI reference](https://code.claude.com/docs/en/cli-reference)):

| Skipped | Why it matters |
|---------|---------------|
| Hooks (`~/.claude`, project) | Local hooks don't contaminate CI runs |
| MCP servers | `.mcp.json` entries don't connect |
| Skills and plugins | No skill-walk on startup |
| Auto-memory | No `~/.claude/memory` reads |
| CLAUDE.md discovery | Project instructions don't load automatically |

Claude retains access to Bash, file read, and file edit tools. Everything else must be passed explicitly.

## Authentication

Bare mode skips OAuth and keychain reads. Authentication must come from one of ([headless docs](https://code.claude.com/docs/en/headless)):

- `ANTHROPIC_API_KEY` environment variable
- An `apiKeyHelper` in the JSON passed to `--settings`
- Provider credentials for Bedrock, Vertex, or Foundry (standard provider auth applies)

This prevents accidental OAuth token usage in CI — a common failure mode when `--bare` is absent and a developer's keychain auth is silently used.

## Adding Context Back Selectively

Because `--bare` skips everything, you load only what the task actually needs ([headless docs](https://code.claude.com/docs/en/headless)):

| To add | Flag |
|--------|------|
| System prompt additions | `--append-system-prompt`, `--append-system-prompt-file` |
| Settings file | `--settings <file-or-json>` |
| MCP servers | `--mcp-config <file-or-json>` |
| Custom agents | `--agents <json>` |
| Plugin directory | `--plugin-dir <path>` |

## Performance

`--bare -p` is approximately 14% faster to the first API request compared to standard `-p` ([changelog](https://code.claude.com/docs/en/changelog)). For CI pipelines that run Claude on every push or PR, this compounds across many invocations. `--bare` also sets the `CLAUDE_CODE_SIMPLE` environment variable ([CLI reference](https://code.claude.com/docs/en/cli-reference)), which downstream scripts can read to detect bare-mode context.

## When This Backfires

`--bare` is deliberately blunt. It strips everything and asks you to add back what you need. That is the right default for reproducible scripts, but it is the wrong default in these cases:

- **CI is meant to mirror the repo's configured environment.** If your team relies on a checked-in `.mcp.json`, project hooks in `.claude/`, or repo-scoped skills for the CI task itself, `--bare` will silently skip them. You must re-add each one with `--mcp-config`, `--settings`, and `--plugin-dir`, and keep those flags in sync with the project config.
- **The task depends on CLAUDE.md context.** Project CLAUDE.md files often encode repo conventions (naming, test commands, style rules). A bare run has none of that and will happily violate them. If you need that context, re-inject it via `--append-system-prompt-file`.
- **You already use `ANTHROPIC_API_KEY` and a locked-down `settings.json`.** If your non-bare `-p` runs are already deterministic — no local hooks, no auto-memory, explicit API key — `--bare` mostly adds flag noise for the ~14% startup saving. Measure before adopting it.

## Example

```yaml
name: security-review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - name: Run security review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff origin/main --name-only | \
            claude --bare -p "Review the listed files for security issues. Output findings as a markdown list." \
              --allowedTools "Read" \
              --max-turns 5 \
              --output-format json | jq -r '.result'
```

`--bare` keeps the run isolated. `--allowedTools "Read"` restricts Claude to reading files only. `--max-turns 5` caps the agentic loop. The result is a reproducible review step that behaves identically on every machine.

## Key Takeaways

- `--bare` skips hooks, MCP servers, skills, plugins, auto-memory, and CLAUDE.md — only flags you pass take effect
- Authentication requires `ANTHROPIC_API_KEY` or equivalent; OAuth and keychain are disabled
- `--bare -p` is ~14% faster to first API request than standard `-p`
- Use `--settings`, `--mcp-config`, and other flags to selectively add back what the task needs
- `--bare` is the recommended mode for scripted calls and will become the default for `-p`

## Related

- [Headless Claude in CI](../../workflows/headless-claude-ci.md)
- [Feature Flags & Environment Variables](feature-flags.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Extension Points: When to Use What](extension-points.md)
- [Claude Agent SDK](agent-sdk.md)
