---
title: "In-Session Transcript Search: Navigating Long Agent Conversations"
description: "Claude Code's transcript-mode search (Ctrl+O then /, n, N) turns a long session transcript into a navigable index — the in-session counterpart to offline transcript analysis."
tags:
  - claude
  - observability
  - workflows
aliases:
  - transcript mode search
  - Ctrl+O search
---

# In-Session Transcript Search

> Press `Ctrl+O` to enter transcript mode in a Claude Code session, then use `/`, `n`, and `N` to jump to specific moments instead of scrolling linearly.

Long agent sessions make linear scrollback hostile. A one-hour Claude Code session can emit thousands of tool-output lines; recalling the moment a plan changed, a tool first errored, or a specific file was touched means re-reading until you find it. Transcript-mode search collapses that to a keystroke, and when fullscreen rendering is active it is the only way to search the conversation at all.

## What the Surface Provides

`Ctrl+O` toggles transcript mode — the view that shows verbose tool calls and output instead of the collapsed default. Inside transcript mode, navigation is `less`-style ([fullscreen reference](https://code.claude.com/docs/en/fullscreen#search-and-review-the-conversation)):

| Key | Action |
|-----|--------|
| `/` | Open search; type a substring, `Enter` to accept, `Esc` to cancel |
| `n` / `N` | Jump to next / previous match after the search bar closes |
| `j` / `k` or arrows | Scroll one line |
| `g` / `G` | Jump to top or bottom |
| `Ctrl+u` / `Ctrl+d` | Half-page scroll |
| `Space` / `b` | Full-page scroll |
| `[` | Write the full conversation to the terminal's native scrollback |
| `v` | Dump the conversation to `$VISUAL` or `$EDITOR` |
| `q` / `Esc` / `Ctrl+o` | Exit transcript mode |

Transcript search shipped in Claude Code v2.1.83 (2026-03-25): "Added transcript search — press `/` in transcript mode (`Ctrl+O`) to search, `n`/`N` to step through matches" ([changelog](https://code.claude.com/docs/en/changelog)). `Ctrl+O` was refined in v2.1.110 to toggle transcript mode only; the focus view moved to the separate `/focus` command ([changelog](https://code.claude.com/docs/en/changelog)).

## Anchors That Make Search Useful

Search is cheapest when you know what string to type. Useful anchors in a Claude Code transcript:

- **Tool error text** — `Error`, `exit code`, `ENOENT`, `timeout`
- **Plan revision boundaries** — `/plan`, the title of the plan file, or the phrase you used to request a new plan
- **File-first-touched** — the filename; the first hit is where the agent first read or edited it
- **Prompt boundaries** — a phrase from your own input; jump backward from the current turn to find where a topic started
- **Scheduled-task timestamps** — v2.1.84 added timestamp markers whenever `/loop` or `CronCreate` fires, which become natural section markers in long sessions ([changelog](https://code.claude.com/docs/en/changelog))

## When Search Is the Wrong Tool

Transcript search is session-scoped, substring-only, and lives in the fullscreen alternate screen buffer. It is not a replacement for:

- **Cross-session investigation.** Matching a symptom across multiple saved sessions requires grepping transcripts on disk or structured telemetry — see [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md).
- **Post-mortem analysis.** Once a session exits, the in-memory buffer is gone. Retrospective review of what the agent did and why belongs to [Using the Agent to Analyze Its Own Evaluation Transcripts](../verification/agent-transcript-analysis.md).
- **Legacy (non-fullscreen) rendering.** Fullscreen mode is opt-in via `/tui fullscreen` or `CLAUDE_CODE_NO_FLICKER=1`. In the default renderer the conversation is in the terminal's native scrollback, so `Cmd+F` and tmux copy mode already work; transcript-mode search does not apply ([fullscreen reference](https://code.claude.com/docs/en/fullscreen)).
- **Noisy sessions.** Substring search with no event-type filter surfaces every occurrence of generic tokens like `error` or `test`. For verbose builds or read-heavy sessions, use `[` to dump the conversation to the terminal's scrollback and grep it, or redirect the analysis to an offline transcript pass.

## Example

A 90-minute session fixing an auth race condition touched twelve files, ran the test suite six times, and produced one plan revision after the third failure. Recovering the plan-revision moment by scrolling is slow; by search it is one keystroke:

```text
Ctrl+O                    → enter transcript mode
/plan                     → first match: initial planning turn
n                         → skip to plan-revision turn
n                         → skip to post-revision edits
Esc                       → exit search
[                         → dump to terminal scrollback for Cmd+F across the session
q                         → return to prompt
```

The same pattern applies to finding the first occurrence of a test failure (`/FAIL`), the moment a specific file was first edited (`/<filename>`), or the turn where a scheduled task fired (`/loop` or the task-timestamp string).

## Key Takeaways

- Transcript search is in-session navigation, not persistent observability — it complements OTel traces and offline transcript analysis rather than replacing them
- `Ctrl+O` toggles transcript mode; `/`, `n`, `N` provide `less`-style search and match stepping
- `[` writes the full conversation into the terminal's native scrollback as an escape hatch into `Cmd+F`, tmux copy mode, and other native tools
- Fullscreen rendering must be on (`/tui fullscreen` or `CLAUDE_CODE_NO_FLICKER=1`) for transcript-mode search to exist
- Search is session-scoped and substring-only — cross-session and post-mortem work belong to different tools

## Related

- [Using the Agent to Analyze Its Own Evaluation Transcripts](../verification/agent-transcript-analysis.md)
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
- [Agent Debug Log Panel: Chronological Event Inspection for Session Debugging](agent-debug-log-panel.md)
- [Agent Debugging](agent-debugging.md)
- [Monitor Tool: Event Streaming from Background Scripts](../tools/claude/monitor-tool.md)
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md)
