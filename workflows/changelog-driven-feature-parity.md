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

Official documentation reflects current state, not arrival order. When you ask "does Copilot CLI support hooks now?" the answer from the docs is yes. What the docs don't show: Claude Code shipped hooks well before Copilot CLI matched with `preToolUse` in [v0.0.396 (2026-01-27)](https://github.com/github/copilot-cli/releases). That multi-month gap matters for your adoption planning.

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
| MCP server support | pre-2026 (exact version not in public changelog) | v0.0.337 (2025-10-08) | Both |
| [Plan mode](plan-first-loop.md) | pre-2026 (Shift+Tab) | v0.0.387 (2026-01-20, `/plan`) | Both |
| Skills / slash commands | pre-2026 (`SKILL.md` auto-discovery) | v0.0.371 (2025-12-18, `~/.copilot/skills/`) | Both |
| Hooks (lifecycle interception) | pre-2026 (14+ documented events) | v0.0.396 (2026-01-27, `preToolUse`) | Both |
| Plugin / extension system | Skills + marketplace | v0.0.392 (2026-01-22, `/plugin`) | Both |
| Parallel sub-agents | pre-2026 (`/batch`) | v0.0.374 (2026-01-02, Explore/Task agents) | Both |
| Custom agent definitions | pre-2026 (`.claude/agents/*.md`) | v0.0.353 (2025-10-28, `.github/agents/`) | Both |
| Permission system / autopilot | pre-2026 (hooks block with exit code 2) | v0.0.351 (2025-10-24); v0.0.399 `/allow-all` | Both |
| Cross-session memory | v2.1.59 (`/memory`) | v0.0.384 (2026-01-16, `store_memory` tool) | Both |
| Context compaction | pre-2026 (auto-compact) | v0.0.374 (2026-01-02, 95% threshold) | Both |
| Multi-model support | v2.1.68 (model picker) | v0.0.341+ (Claude, GPT, Gemini) | Both |
| Remote / background delegation | pre-2026 (`claude remote-control`; `/remote-control` in v2.1.79) | v0.0.353 (`/delegate`); v0.0.384 (`&` prefix) | Both |
| Worktree isolation | pre-2026 (`--worktree`, WorktreeCreate/Remove hooks) | — | Claude Code only |
| Auto-decomposition into parallel worktrees | pre-2026 (`/batch`, 5–30 units) | — | Claude Code only |
| [Agent teams](../tools/claude/agent-teams.md) (shared task list, direct messaging) | pre-2026, experimental | — | Claude Code only |
| HTTP hooks (POST/JSON via hooks) | v2.1.76+ (`type: "http"` on WorktreeCreate hook) | — | Claude Code only |
| Voice mode (STT, push-to-talk) | v2.1.69+ (20 languages) | — | Claude Code only |
| `/loop` with [cron scheduling](../tools/claude/session-scheduling.md) | pre-2026 | — | Claude Code only |
| Extended thinking effort controls | v2.1.80+ (`effort` frontmatter field) | — | Claude Code only |
| [Agent SDK](../tools/claude/agent-sdk.md) (TypeScript + Python) | pre-2026 | — | Claude Code only |
| `/research` command (exportable reports) | — | v0.0.417 (2026-02-25) | Copilot CLI only |
| `/review` command (built-in code review agent) | — | v0.0.388 (2026-01-20) | Copilot CLI only |
| `/chronicle` (standup / session history) | — | v0.0.419 (2026-02-27) | Copilot CLI only |
| [MCP Elicitations (structured form input)](../tool-engineering/mcp-elicitation.md) | — | v0.0.421 (experimental) | Copilot CLI only |
| Extensions via `@github/copilot-sdk` | — | v1.0.3 (experimental, 2026-03-09) | Copilot CLI only |
| Session usage metrics (`events.jsonl`) | — | v0.0.422 | Copilot CLI only |
| ACP server mode | — | v0.0.397 | Copilot CLI only |

## Key Cross-Matches in Detail

### Hooks

Claude Code ships a hooks system with 14+ lifecycle events (per the [Claude Code changelog](https://code.claude.com/docs/en/changelog)): `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStart`, and others. An exit code of `2` from a hook blocks the tool call. This covers deny, modify, and notification patterns.

Copilot CLI v0.0.396 added `preToolUse` (deny/modify); v0.0.401 added `agentStop` and `subagentStop`; v0.0.422 added personal hooks and startup hooks. The Copilot CLI surface is approximately 5 confirmed events vs Claude Code's 14+ documented events (per the [Claude Code changelog](https://code.claude.com/docs/en/changelog)). The mechanisms are equivalent; the coverage differs.

Source: [Copilot CLI releases](https://github.com/github/copilot-cli/releases); [Claude Code changelog](https://code.claude.com/docs/en/changelog).

### Skills / Extensions

Both tools ship a discoverable package format:

- Claude Code: `SKILL.md` files in `skills/`, auto-discovered; marketplace install via `npx skills add owner/repo`
- Copilot CLI v0.0.371: `~/.copilot/skills/` directory; `/skills add` in v0.0.396; plugin-provided skills in v0.0.394+; SDK-generated extensions in v1.0.3

The implementation differs: Claude Code uses declarative YAML/markdown; Copilot CLI v1.0.3 Extensions are code-generated via `@github/copilot-sdk` (experimental). Both bundle MCP servers, agent definitions, and lifecycle hooks.

### Plan Mode

Both tools separate planning from execution:

- Claude Code: Shift+Tab enters [Plan Mode](plan-mode.md), a read-only analysis mode before code changes
- Copilot CLI v0.0.387: `/plan` with a dedicated panel; v0.0.415 adds plan approval menu with autopilot and fleet options

Copilot CLI's plan mode (v0.0.387, January 2026) shipped after Claude Code's Shift+Tab plan mode, which predates the public changelog window (pre-2026), with a more structured approval UI.

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

## When This Backfires

Changelog-driven parity tracking is only as good as the changelogs themselves:

- **Silent features**: Both tools frequently ship capabilities without changelog entries or under generic labels like "minor improvements." Version-pinning a feature to a specific release may be incorrect if it landed earlier via a quiet update.
- **Semantic equivalence disputes**: Deciding that "Claude Code skills + hooks" is functionally equivalent to "Copilot CLI Extensions" requires judgment calls that other practitioners may contest. The table encodes one perspective; implementations differ in ways that matter for specific use cases.
- **Staleness rate**: Both tools ship weekly or faster. A parity matrix accurate today may misclassify features as "tool-specific" within a week. Treat the table as a snapshot requiring regular refresh, not a durable reference.

## Example

Copilot CLI v0.0.422 (released 2026-02-14) includes the entry: "Add personal hooks and startup hooks."

**Step 1 — Categorise.** Domain: hooks. Capability: hooks (lifecycle interception).

**Step 2 — Check the current matrix.** The Hooks row shows Status = "Both", with Copilot CLI first matched in v0.0.396 (`preToolUse`). This release extends hook coverage; it does not open a new gap.

**Step 3 — Update the detail section.** In **Key Cross-Matches in Detail → Hooks**, add: "v0.0.422 added personal hooks and startup hooks."

**Step 4 — Re-evaluate coverage delta.** Claude Code has 14+ documented hook events (per the [Claude Code changelog](https://code.claude.com/docs/en/changelog)); Copilot CLI now has `preToolUse`, `agentStop`, `subagentStop`, personal hooks, and startup hooks (~5 confirmed). The coverage gap remains but is narrowing.

No Status column change required. The detail section is updated and the gap delta is recorded.

```bash
# Automate step 1: fetch latest Copilot CLI release and print entries
gh api repos/github/copilot-cli/releases/latest --jq '.body' | head -40
```

## Related

- [Cross-Tool Translation: Learning from Multiple AI Assistants](../human/cross-tool-translation.md)
- [CLI → IDE → GitHub: Context Ladder](cli-ide-github-context-ladder.md)
- [Claude Code /batch and Worktrees](../tools/claude/batch-worktrees.md)
- [Worktree Isolation](worktree-isolation.md)
- [Hooks Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
- [PostToolUse Hooks: Auto-Formatting on Every File Edit](posttooluse-auto-formatting.md)
- [Skill Library Evolution](../tool-engineering/skill-library-evolution.md)
- [Copilot CLI: Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md)
