---
title: "Harness Translation Reference"
description: "Map the agent-readiness library's Claude Code paths, config schemas, and lifecycle events to their equivalents in Cursor, Aider, GitHub Copilot, and Gemini CLI — so non-Claude-Code projects can apply the same runbooks."
tags:
  - tool-agnostic
  - instructions
aliases:
  - harness translation table
  - cursor copilot aider equivalents
  - cross-harness paths
---

# Harness Translation Reference

> Map the agent-readiness library's Claude Code paths, config schemas, and lifecycle events to their equivalents in other harnesses.

The runbooks in this library [target Claude Code](index.md#assumptions) for templates and config schemas. The principles are tool-agnostic, but the file paths and event names differ per harness. This page is the lookup the per-page admonitions point to when they say "translate to your harness's equivalents."

Coverage is honest, not exhaustive: cells with primary-source citations are listed; cells without are marked **—** (no native equivalent confirmed) or **see official docs** (likely exists, not yet sourced here). Contributions welcome.

## When to use this page

- You hit a runbook step that hardcodes `.claude/...` and you're on a different harness
- You're auditing a multi-harness project (e.g., a repo wired for both Claude Code and Cursor)
- You're translating a runbook into a packaged skill / rule / extension for your harness

## Core translation table

| Concept | Claude Code | Cursor | Aider | GitHub Copilot | Gemini CLI |
|---------|-------------|--------|-------|----------------|------------|
| Project instructions, root | `CLAUDE.md` ([docs](https://docs.claude.com/en/docs/claude-code/memory)) | `.cursor/rules/*.mdc` or `.cursorrules` ([docs](https://docs.cursor.com/context/rules)) | `.aider.conf.yml`, repo-relative ([docs](https://aider.chat/docs/config/aider_conf.html)) | `.github/copilot-instructions.md` ([docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)) | `GEMINI.md` ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md)) |
| Subdirectory instructions | `<dir>/CLAUDE.md` or `<dir>/AGENTS.md` ([docs](https://docs.claude.com/en/docs/claude-code/memory#how-claude-looks-up-memories)) | `.cursor/rules/<scope>.mdc` with `globs:` frontmatter ([docs](https://docs.cursor.com/context/rules)) | — | — | `<dir>/GEMINI.md` ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md)) |
| Cross-tool instruction file | `@AGENTS.md` import in `CLAUDE.md` (open standard, [agents.md](https://agents.md)) | reference `AGENTS.md` from a `.cursor/rules/` file | reference via `--read AGENTS.md` flag | reference `AGENTS.md` from `copilot-instructions.md` | reference via `GEMINI.md` |
| MCP server config | `.mcp.json` (project) or `.claude/settings.json mcpServers` ([docs](https://docs.claude.com/en/docs/claude-code/mcp)) | `.cursor/mcp.json` ([docs](https://docs.cursor.com/context/mcp)) | — (no native MCP) | preview; varies by surface ([docs](https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-skillsets)) | preview; varies by surface |
| Permission allowlist | `.claude/settings.json` `permissions.{allow,deny,ask}` ([docs](https://docs.claude.com/en/docs/claude-code/settings)) | see Cursor settings docs | CLI flags (`--read`, `--no-auto-commit`, `--auto-commits`) ([docs](https://aider.chat/docs/config/options.html)) | org/repo-level Copilot policies ([docs](https://docs.github.com/en/copilot/managing-copilot/managing-policies-and-features-for-your-enterprise)) | see official docs |
| Lifecycle hooks directory | `.claude/hooks/` ([docs](https://docs.claude.com/en/docs/claude-code/hooks)) | see Cursor hooks docs (Beta as of writing — [Cursor changelog](https://cursor.com/changelog)) | — (no native hook system) | — (no in-session hook lifecycle; use Actions for PR-time) | — |
| Pre-completion verification gate | `Stop` event hook ([docs](https://docs.claude.com/en/docs/claude-code/hooks#stop)) | see Cursor hooks docs | run via wrapper script around `aider` invocation | PR-time CI checks (no in-session gate) | wrapper script around `gemini` invocation |
| On-demand skills | `.claude/skills/<name>/SKILL.md` ([docs](https://docs.claude.com/en/docs/claude-code/skills)) | `.cursor/rules/<name>.mdc` (closest analogue; rules file with description triggers) | — (closest: system-prompt fragments via `--read`) | custom modes / agents ([docs](https://docs.github.com/en/copilot/using-github-copilot/copilot-chat/using-modes-in-copilot-chat)) | slash commands ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/commands.md)) |
| Sub-agents / role agents | `.claude/agents/<name>.md` ([docs](https://docs.claude.com/en/docs/claude-code/sub-agents)) | `.cursor/agents/<name>.md` (Cursor sub-agents — verify against current docs) | separate `aider` invocations with different `--read` files | custom modes ([docs](https://docs.github.com/en/copilot/using-github-copilot/copilot-chat/using-modes-in-copilot-chat)) | — |
| Per-session state directory | `.claude/state/` (convention; gitignored) | per-project Cursor state | none — aider sessions are stateless beyond chat history | none | none |
| Egress / network restriction | `.claude/settings.json` `permissions.deny` for `Bash(curl:*)` etc. ([docs](https://docs.claude.com/en/docs/claude-code/settings#permissions)) | OS firewall + Cursor permissions | OS firewall (no native config) | org-level policies | OS firewall |

**Citation honesty**: every cell either cites a primary source or is marked **—** (no native equivalent that the author has verified). Cells that say "see Cursor hooks docs" without a deep-link mean the harness has the feature but the exact path/schema was not verified at write time — verify against the linked tool docs before relying on it.

## Per-harness notes

### Cursor

- Rules live in `.cursor/rules/*.mdc` (preferred) or the legacy `.cursorrules` at repo root
- Each `.mdc` rule can scope to file globs via `globs:` frontmatter, which is the closest equivalent to subdirectory `CLAUDE.md`
- MCP servers are configured per-project in `.cursor/mcp.json` and globally in `~/.cursor/mcp.json` ([docs](https://docs.cursor.com/context/mcp))
- Hooks are a newer addition (Beta) — verify the event taxonomy and registration mechanism against the Cursor changelog before applying [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) or [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md)

### Aider

- Aider is a chat-mode CLI tool, not a long-running harness with a hook lifecycle
- "Permissions" are CLI flags: `--read` for read-only context, `--no-auto-commit` to gate writes, `--auto-commits` (default off in some modes) to control git side effects
- No native MCP support — external services must be wrapped as command-line tools the agent invokes
- The agent-readiness pages that target lifecycle events ([`bootstrap-hooks-scaffold`](bootstrap-hooks-scaffold.md), [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md), [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md)) do not have direct Aider equivalents; close the same intent via wrapper scripts or git pre-commit hooks

### GitHub Copilot

- Project instructions go in `.github/copilot-instructions.md` ([docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)); subdirectory variants are not currently supported
- Copilot's lifecycle is split across surfaces (Chat, Workspace, CLI, coding agent) — there is no single "session" with hooks the way Claude Code or Cursor expose
- Permission gating is org/repo-level via Copilot Enterprise policies, not in-repo config
- Pre-completion verification is handled at PR review time, not in-session — run [`bootstrap-eval-suite`](bootstrap-eval-suite.md) as a CI check on PRs that touch agent-customizable files
- MCP support varies by surface and is in preview at the time of writing

### Gemini CLI

- Project instructions go in `GEMINI.md` at the repo root, with subdirectory variants supported ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md))
- Gemini CLI is newer — the harness extensibility surface (hooks, sub-agents, skills) is less established than Claude Code or Cursor
- Slash commands are the closest analogue to skills ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/commands.md))
- Verify against the official docs before applying any runbook beyond [`bootstrap-agents-md`](bootstrap-agents-md.md) and [`audit-secrets-in-context`](audit-secrets-in-context.md)

## Translating a runbook

When applying a Claude-Code-shaped runbook to another harness:

1. Read the [Assumptions](index.md#assumptions) section
2. Map the runbook's paths against the table above — substitute every `.claude/...` reference with the harness's equivalent
3. For any cell marked **—**, check whether the runbook's intent (what the file or event is *for*) can be satisfied by a different mechanism in your harness (CI check, wrapper script, OS-level enforcement)
4. If you build out a parallel template for your harness, contribute it back — the agent-readiness library is open to per-harness rubrics and config templates

## Contributions

Filling the gaps is the highest-leverage way to make this library usable across harnesses. Specifically valuable:

- Cursor: verified hook event taxonomy and `.cursor/settings.json` permission schema
- Aider: best-practice patterns for wrapping `aider` invocations with pre/post checks
- Copilot: confirmed MCP integration paths once GA
- Gemini CLI: confirmed extensibility surfaces as the harness matures

File an issue or PR with primary-source citations.

## Related

- [Assumptions](index.md#assumptions) — when to apply a runbook on a non-Claude-Code project
- [AGENTS.md Standard](../standards/agents-md.md) — the cross-harness instruction file
- [Instruction File Ecosystem](../instructions/instruction-file-ecosystem.md) — how the various tool-specific instruction files relate
- [Hooks Lifecycle](../tools/claude/hooks-lifecycle.md) — Claude Code's lifecycle events in depth
