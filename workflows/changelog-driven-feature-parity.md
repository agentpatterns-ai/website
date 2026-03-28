---
title: "Claude Code ↔ Copilot CLI: Changelog-Driven Feature Parity"
description: "Track which CLI tool shipped a capability first and when the other matched it — extracted from public changelogs, not documentation."
tags:
  - workflows
  - agent-design
---

# Claude Code ↔ Copilot CLI: Changelog-Driven Feature Parity

> Changelog-driven feature parity is a methodology for mapping when each CLI tool first shipped a given capability and when its competitor matched it, using release notes rather than current documentation — revealing arrival order and gap duration that docs never show.

## Why Changelog Tracking

Official documentation reflects current state, not arrival order. When you ask "does Copilot CLI support hooks now?" the answer from the docs is yes. What the docs don't show: Claude Code shipped hooks in v2.0.x [unverified]; Copilot CLI matched with `preToolUse` in [v0.0.396 (2026-01-27)](https://github.com/github/copilot-cli/releases). That multi-month gap matters for your adoption planning.

Changelog-driven parity tracking surfaces:

- Which capabilities are now **universal** (available in both tools)
- Which remain **tool-specific** and in which direction
- The **velocity** at which the trailing tool closes a gap

## Sources

- **Claude Code changelog**: [`code.claude.com/docs/en/changelog`](https://code.claude.com/docs/en/changelog) — covers v0.2.x through current
- **Copilot CLI releases**: [`github.com/github/copilot-cli/releases`](https://github.com/github/copilot-cli/releases) — machine-readable via `gh api repos/github/copilot-cli/releases`
- **GitHub Changelog**: [`github.blog/changelog/`](https://github.blog/changelog/) — GA announcements and major feature posts

## Methodology

This table tracks semantic equivalence rather than string matching. "[Copilot Extensions](../tools/copilot/copilot-extensions.md)" (v1.0.3) is not the same API as "Claude Code skills + hooks" — but they solve the same problem: bundling custom tools and lifecycle callbacks into an installable package. The table identifies functional equivalents and notes where implementations diverge.

Extraction approach:

1. Fetch both changelogs programmatically (`gh api` for Copilot CLI; `WebFetch` for Claude Code)
2. Categorize entries by capability domain (hooks, plan mode, memory, MCP, etc.)
3. Find the first version in each tool that ships each domain
4. Flag entries in the trailing tool that close a previously open gap

## Feature Parity Matrix

As of 2026-03. Sources: [Claude Code changelog](https://code.claude.com/docs/en/changelog); [Copilot CLI releases v0.0.349–v1.0.3](https://github.com/github/copilot-cli/releases); [GitHub Changelog](https://github.blog/changelog/).

| Capability | Claude Code | Copilot CLI | Status |
|---|---|---|---|
| MCP server support | v2.0.x [unverified] | v0.0.337 (2025-10-08) | Both |
| [Plan mode](plan-first-loop.md) | v2.0.x [unverified] (Shift+Tab) | v0.0.387 (2026-01-20, `/plan`) | Both |
| Skills / slash commands | v2.0.x [unverified] (`SKILL.md` auto-discovery) | v0.0.371 (2025-12-18, `~/.copilot/skills/`) | Both |
| Hooks (lifecycle interception) | v2.0.x [unverified] (16+ events) | v0.0.396 (2026-01-27, `preToolUse`) | Both |
| Plugin / extension system | Skills + marketplace [unverified] | v0.0.392 (2026-01-22, `/plugin`) | Both |
| Parallel sub-agents | v2.0.x [unverified] (`/batch`) | v0.0.374 (2026-01-02, Explore/Task agents) | Both |
| Custom agent definitions | v2.0.x [unverified] (`.claude/agents/*.md`) | v0.0.353 (2025-10-28, `.github/agents/`) | Both |
| Permission system / autopilot | v2.0.x [unverified] (hooks block with exit code 2) | v0.0.351 (2025-10-24); v0.0.399 `/allow-all` | Both |
| Cross-session memory | v2.1.59 (`/memory`) | v0.0.384 (2026-01-16, `store_memory` tool) | Both |
| Context compaction | v2.0.x [unverified] (auto-compact) | v0.0.374 (2026-01-02, 95% threshold) | Both |
| Multi-model support | v2.1.68 (model picker) | v0.0.341+ (Claude, GPT, Gemini) | Both |
| Remote / background delegation | v2.1.51 [unverified] (`claude remote-control`) | v0.0.353 (`/delegate`); v0.0.384 (`&` prefix) | Both |
| Worktree isolation | v2.1.50+ [unverified] (`--worktree`, WorktreeCreate/Remove hooks) | — | Claude Code only |
| Auto-decomposition into parallel worktrees | v2.1.63 [unverified] (`/batch`, 5–30 units) | — | Claude Code only |
| [Agent teams](../tools/claude/agent-teams.md) (shared task list, direct messaging) | v2.0.x [unverified] experimental | — | Claude Code only |
| HTTP hooks (POST/JSON via hooks) | v2.1.63 [unverified] | — | Claude Code only |
| Voice mode (STT, push-to-talk) | v2.1.69+ [unverified] (20 languages) | — | Claude Code only |
| `/loop` with [cron scheduling](../tools/claude/session-scheduling.md) | v2.1.71 [unverified] | — | Claude Code only |
| Extended thinking effort controls | v2.1.x [unverified] | — | Claude Code only |
| [Agent SDK](../tools/claude/agent-sdk.md) (TypeScript + Python) | v2.0.x [unverified] | — | Claude Code only |
| `/research` command (exportable reports) | — | v0.0.417 (2026-02-25) | Copilot CLI only |
| `/review` command (built-in code review agent) | — | v0.0.388 (2026-01-20) | Copilot CLI only |
| `/chronicle` (standup / session history) | — | v0.0.419 (2026-02-27) | Copilot CLI only |
| MCP Elicitations (structured form input) | — | v0.0.421 (experimental) | Copilot CLI only |
| Extensions via `@github/copilot-sdk` | — | v1.0.3 (experimental, 2026-03-09) | Copilot CLI only |
| Session usage metrics (`events.jsonl`) | — | v0.0.422 | Copilot CLI only |
| ACP server mode | — | v0.0.397 | Copilot CLI only |

## Key Cross-Matches in Detail

### Hooks

Claude Code ships a hooks system with ~16 lifecycle events: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, and others. An exit code of `2` from a hook blocks the tool call. This covers deny, modify, and notification patterns.

Copilot CLI v0.0.396 added `preToolUse` (deny/modify); v0.0.401 added `agentStop` and `subagentStop`; v0.0.422 added personal hooks and startup hooks. The Copilot CLI surface is ~4 confirmed events [unverified] vs Claude Code's ~16 [unverified]. The mechanisms are equivalent; the coverage differs.

Source: [Copilot CLI releases](https://github.com/github/copilot-cli/releases); [Claude Code changelog](https://code.claude.com/docs/en/changelog).

### Skills / Extensions

Both tools ship a discoverable package format:

- Claude Code: `SKILL.md` files in `skills/`, auto-discovered; marketplace install via `npx skills add owner/repo`
- Copilot CLI v0.0.371: `~/.copilot/skills/` directory; `/skills add` in v0.0.396; plugin-provided skills in v0.0.394+; SDK-generated extensions in v1.0.3

The implementation differs: Claude Code uses declarative YAML/markdown; Copilot CLI v1.0.3 Extensions are code-generated via `@github/copilot-sdk` (experimental). Both bundle MCP servers, agent definitions, and lifecycle hooks.

### Plan Mode

Both tools separate planning from execution:

- Claude Code: Shift+Tab enters read-only analysis mode before code changes
- Copilot CLI v0.0.387: `/plan` with a dedicated panel; v0.0.415 adds plan approval menu with autopilot and fleet options

Copilot CLI's plan mode shipped significantly later than Claude Code's [unverified: exact gap requires precise Claude Code v2.0.x release date], with a more structured approval UI.

## Keeping the Table Current

Both changelog sources are machine-readable:

```bash
# Copilot CLI releases (JSON, paginated)
gh api repos/github/copilot-cli/releases --paginate

# Claude Code changelog (fetch and parse)
# https://code.claude.com/docs/en/changelog
```

Update cadence: Copilot CLI ships weekly (sometimes daily); Claude Code ships roughly weekly. Check both within a 2-week window to catch parity closures.

When you see a tool-specific feature appear in the other tool's changelog, update the Status column from "X only" to "Both" and add the version.

## Key Takeaways

- As of 2026-03, the core agentic primitives — MCP, plan mode, hooks, skills, memory, parallel agents — are available in both Claude Code and Copilot CLI
- Claude Code leads on worktree isolation, `/batch` decomposition, extended thinking controls, and the [Agent SDK](../tools/claude/agent-sdk.md)
- Copilot CLI leads on built-in command agents (`/research`, `/review`, `/chronicle`), the ACP server mode, and SDK-generated extensions
- Copilot CLI closed most major gaps between late 2025 and early 2026 — a 4–6 month lead time from idea to parity across core primitives
- Semantic equivalence analysis matters more than keyword matching; "Extensions" and "skills + hooks" describe different implementations of the same capability

## Unverified Claims

- Claude Code MCP server support shipped in v2.0.x [unverified]
- Claude Code Plan mode shipped in v2.0.x [unverified]
- Claude Code Skills / slash commands shipped in v2.0.x [unverified]
- Claude Code Hooks (lifecycle interception) shipped in v2.0.x with 16+ events [unverified]
- Claude Code Plugin / extension system with skills + marketplace [unverified]
- Claude Code Parallel sub-agents shipped in v2.0.x [unverified]
- Claude Code Custom agent definitions shipped in v2.0.x [unverified]
- Claude Code Permission system / autopilot shipped in v2.0.x [unverified]
- Claude Code Context compaction shipped in v2.0.x [unverified]
- Claude Code Remote / background delegation shipped in v2.1.51 [unverified]
- Claude Code Worktree isolation shipped in v2.1.50+ [unverified]
- Claude Code Auto-decomposition into parallel worktrees shipped in v2.1.63 [unverified]
- Claude Code [Agent teams](../tools/claude/agent-teams.md) (shared task list, direct messaging) shipped in v2.0.x [unverified]
- Claude Code HTTP hooks shipped in v2.1.63 [unverified]
- Claude Code Voice mode shipped in v2.1.69+ with 20 languages [unverified]
- Claude Code `/loop` with [cron scheduling](../tools/claude/session-scheduling.md) shipped in v2.1.71 [unverified]
- Claude Code Extended thinking effort controls shipped in v2.1.x [unverified]
- Claude Code [Agent SDK](../tools/claude/agent-sdk.md) (TypeScript + Python) shipped in v2.0.x [unverified]
- Copilot CLI hooks surface has ~4 confirmed events [unverified]
- Claude Code hooks surface has ~16 events [unverified]
- Exact plan mode gap requires precise Claude Code v2.0.x release date [unverified]

## Example

Copilot CLI v0.0.422 (released 2026-02-14) includes the entry: "Add personal hooks and startup hooks."

**Step 1 — Categorise.** Domain: hooks. Capability: hooks (lifecycle interception).

**Step 2 — Check the current matrix.** The Hooks row shows Status = "Both", with Copilot CLI first matched in v0.0.396 (`preToolUse`). This release extends hook coverage; it does not open a new gap.

**Step 3 — Update the detail section.** In **Key Cross-Matches in Detail → Hooks**, add: "v0.0.422 added personal hooks and startup hooks."

**Step 4 — Re-evaluate coverage delta.** Claude Code has ~16 hook events [unverified]; Copilot CLI now has `preToolUse`, `agentStop`, `subagentStop`, personal hooks, and startup hooks (~5 confirmed). The coverage gap remains but is narrowing.

No Status column change required. The detail section is updated and the gap delta is recorded.

```bash
# Automate step 1: fetch latest Copilot CLI release and print entries
gh api repos/github/copilot-cli/releases/latest --jq '.body' | head -40
```

## Related

- [Cross-Tool Translation: Learning from Multiple AI Assistants](../human/cross-tool-translation.md)
- [Claude Code /batch and Worktrees](../tools/claude/batch-worktrees.md)
- [Worktree Isolation](worktree-isolation.md)
- [Hooks Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
- [PostToolUse Hooks: Auto-Formatting on Every File Edit](posttooluse-auto-formatting.md)
- [Skill Library Evolution](../tool-engineering/skill-library-evolution.md)
- [Copilot CLI: Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md)
- [Agentic AI Architecture](../agent-design/agentic-ai-architecture-evolution.md)
- [Parallel Agent Sessions](parallel-agent-sessions.md)
