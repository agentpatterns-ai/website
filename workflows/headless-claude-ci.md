---
title: "Headless Claude in CI: Using -p and --max-turns for Safe"
description: "Run Claude non-interactively in CI/CD pipelines using print mode (-p) and cap agentic steps with --max-turns to keep pipelines predictable and cost-bounded"
tags:
  - workflows
  - cost-performance
  - claude
  - github-actions
aliases:
  - "claude print mode"
  - "non-interactive Claude"
  - "claude -p CI"
---

# Headless Claude in CI: Using -p and --max-turns for Safe Pipeline Integration

> Run Claude non-interactively in CI/CD pipelines using print mode (`-p`) and cap agentic steps with `--max-turns` to keep pipelines predictable and cost-bounded.

## Print Mode

`claude -p "<prompt>"` runs Claude non-interactively and exits when done ([CLI reference](https://code.claude.com/docs/en/cli-reference)). Output goes to stdout.

Claude accepts piped stdin as context:

```bash
git diff main --name-only | claude -p "review these changed files for security issues"
```

No additional prompt engineering is needed — piped content arrives before the prompt is processed.

## Capping Agentic Steps

Without a turn limit, an agentic run can loop indefinitely on ambiguous tasks. `--max-turns <N>` sets a hard ceiling on reasoning steps and exits with an error when reached ([CLI reference](https://code.claude.com/docs/en/cli-reference)):

```bash
claude -p "run the test suite and fix any failures" --max-turns 5
```

`--max-turns` is only available in print mode. There is no default — without it, there is no limit.

## Machine-Readable Output

`--output-format json` wraps the response for downstream script consumption ([CLI reference](https://code.claude.com/docs/en/cli-reference)):

```bash
result=$(claude -p "summarize open issues" --output-format json)
```

| Format | Use case |
|---|---|
| `text` (default) | Terminal output |
| `json` | Script consumption |
| `stream-json` | Streaming event processing |

## GitHub Actions

The `anthropics/claude-code-action@v1` action runs Claude in GitHub Actions ([docs](https://code.claude.com/docs/en/github-actions)). The `claude_args` parameter passes any CLI flag through:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "/review"
    claude_args: "--max-turns 5"
```

Store the API key as a repository secret named `ANTHROPIC_API_KEY`. Install the Claude GitHub App via `/install-github-app` or manually from [github.com/apps/claude](https://github.com/apps/claude) to enable PR comments and commits ([docs](https://code.claude.com/docs/en/github-actions#setup)).

## Permissions in Non-Interactive Mode

`PermissionRequest` hooks do not fire in non-interactive mode ([hooks docs](https://code.claude.com/docs/en/hooks-guide#limitations)). For automated permission decisions, use `PreToolUse` hooks or `--allowedTools` to enumerate permitted tools explicitly:

```bash
claude -p "run lint and fix errors" \
  --allowedTools "Bash(bun run lint *)" "Edit" "Read"
```

`--dangerously-skip-permissions` disables all prompts ([CLI reference](https://code.claude.com/docs/en/cli-reference)). Use only in ephemeral, isolated runners where unintended writes have bounded [blast radius](../security/blast-radius-containment.md).

## Cost Control

Three flags limit spend in automated contexts ([CLI reference](https://code.claude.com/docs/en/cli-reference)):

| Flag | Effect |
|---|---|
| `--max-turns <N>` | Caps reasoning steps; exits with error at limit |
| `--max-budget-usd <amount>` | Stops at a dollar ceiling (print mode only) |
| `--model <alias>` | `sonnet` is lower cost than `opus` |

Set workflow-level timeouts in GitHub Actions as a second layer against hung jobs.

## Example

A GitHub Actions workflow that runs Claude on every pull request to review changed files, capped at 5 turns and $1.00 spend:

```yaml
name: claude-pr-review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Review the PR diff for bugs, security issues, and style violations. Summarize findings as PR comments."
          claude_args: "--max-turns 5 --max-budget-usd 1.00 --model sonnet"
```

This workflow combines `--max-turns`, `--max-budget-usd`, and `timeout-minutes` for three layers of cost and runtime protection.

## Key Takeaways

- `claude -p "<prompt>"` runs non-interactively; piped stdin is available as context before the prompt
- `--max-turns <N>` sets a hard ceiling on agentic steps with no default limit in print mode
- `--output-format json` makes responses machine-readable for downstream consumption
- `PermissionRequest` hooks do not fire non-interactively; use `PreToolUse` hooks or `--allowedTools`
- `--dangerously-skip-permissions` is appropriate only in isolated, ephemeral environments
- `anthropics/claude-code-action@v1` wraps this for GitHub Actions with `claude_args` passthrough

## Related

- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Worktree Isolation for Parallel Agent Sessions](worktree-isolation.md)
- [Parallel Agent Sessions](parallel-agent-sessions.md)
- [Continuous AI: Agentic CI/CD Pipelines](continuous-ai-agentic-cicd.md)
