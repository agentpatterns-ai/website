---
title: "Copilot Unified Sessions View and CLI Agent in JetBrains IDEs"
description: "JetBrains chat-window registry aggregating CLI agent, agent mode, custom agent, and sub-agent sessions into one filterable list — useful above one concurrent agent and behind real isolation."
tags:
  - agent-design
  - copilot
  - workflows
aliases:
  - copilot unified sessions
  - jetbrains sessions view
  - copilot cli agent in ide
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
---
# Copilot Unified Sessions View and CLI Agent in JetBrains

> A chat-window session registry that aggregates CLI agent, agent mode, custom agent, and sub-agent runs into one filterable list — the value scales with concurrency and the isolation primitive behind it, not with how often the developer uses Copilot.

The unified sessions view is the JetBrains chat window's per-agent-type registry, surfaced alongside a locally-running Copilot CLI agent that the IDE can dispatch into a worktree or workspace ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)). Each row shows title, agent type, elapsed time, and status, filterable by agent type or status. The two features shipped together — the CLI agent is the new invocation surface; the sessions view is the registry that catches sessions from it, agent mode, inline agent mode, custom agents, and sub-agents.

## When This Pattern Applies

Three conditions gate the value:

- **Concurrency > 1.** A registry listing one row is overhead. The pattern pays when two or more agents are in flight — typical when a CLI agent runs in the background while inline agent mode handles tactical edits.
- **Multiple invocation surfaces in use.** JetBrains exposes at least three Copilot surfaces — chat-panel [agent mode](agent-mode.md), [inline agent mode](inline-agent-mode.md), and the CLI agent ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)). One row per session removes the "which surface did I start that run on?" problem.
- **Backed by an isolation primitive.** The CLI agent exposes worktree isolation (separate git worktree, review before apply) or workspace isolation (changes apply to the current workspace) ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)). A sessions list without isolation behind it is decoration — parallel rows that step on each other's files cannot run in parallel.

## What the View Aggregates

The chat-window registry shows sessions from every Copilot agent surface running locally in JetBrains:

| Source | What appears as a row |
|--------|----------------------|
| CLI agent | A dispatched run with selected model and isolation mode |
| Agent mode | A chat-panel agent run |
| Custom agents | Any user-defined agent invoked through the agent picker |
| Sub-agents | Agents spawned by another agent during a run |

Each row exposes the four scannable fields — title, agent type, elapsed time, status — plus filter dropdowns for agent type and status ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)). The aggregation key is `agent type + session ID`, so the same conversation never appears twice when invoked from a different surface.

## Cross-Tool Convergence

The pattern of "sessions view as a registry across invocation surfaces" converged across four tools in roughly six months — none of them coordinating.

| Tool | Sessions surface | Aggregation scope |
|------|------------------|-------------------|
| GitHub Copilot for JetBrains | Unified sessions view in chat window | CLI agent, agent mode, custom agents, sub-agents ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)) |
| Claude Code | `claude agents` agent view (research preview) | Every background session across all projects, per-user supervisor process, persisted across sleep and IDE close ([Claude Code agent view](https://code.claude.com/docs/en/agent-view)) |
| Cursor 3 | Agents Window | Local, worktree, cloud, SSH agents in one window ([Cursor 3 changelog](https://cursor.com/changelog/3-0)) |
| GitHub Copilot (cloud agent) | Mission Control | Cloud coding agent tasks across repositories ([GitHub Changelog 2025-10-28](https://github.blog/changelog/2025-10-28-a-mission-control-to-assign-steer-and-track-copilot-coding-agent-tasks/)) |

The JetBrains unified view is the local-CLI sibling of [Mission Control](agent-mission-control.md): same registry pattern, different scope. Five days after the JetBrains view shipped, GitHub made cross-device remote control of CLI sessions GA — a session started in the JetBrains view can be steered from GitHub Mobile or github.com ([GitHub Changelog 2026-05-18](https://github.blog/changelog/2026-05-18-remote-control-for-copilot-cli-sessions-now-generally-available-on-mobile-web-and-vs-code/)).

## Why It Works

A developer's running-agent inventory is the bottleneck on parallel agent work, not the agent itself. Once an agent runs unattended, the limiting resource is the developer's ability to notice when one needs input, finishes, or stalls. A chat log loses signal as session count grows. Aggregating sessions into a scannable list keyed by agent type plus session ID solves the noticing bottleneck at the cost of a second surface to learn. Claude Code's agent view documents the same mechanism: row summaries are generated by a Haiku-class model so "the row can tell you what the session is doing, what it needs, or what it produced without opening the transcript" ([Claude Code agent view](https://code.claude.com/docs/en/agent-view)). Cross-vendor convergence across Claude Code, Copilot JetBrains, Cursor 3, and Windsurf in six months ([RedMonk 2025-12-22](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)) is independent evidence the bottleneck is real.

## When This Backfires

- **At-most-one-concurrent-agent workflows.** A list with one row is pure overhead. Inline-edit-heavy developers who never run two agents at once get a registry that never filters anything.
- **No real isolation behind the rows.** Workspace isolation mode applies changes directly to the current workspace; two parallel workspace-isolation rows touching the same files race and clobber. Worktree isolation is required for genuine parallelism — the same condition the [editor-manager surface separation](../../agent-design/editor-manager-surface-separation.md) pattern depends on.
- **Business and Enterprise tenants without the policy on.** Admins must enable the Editor preview features policy before users see the surface ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)). Teams that don't get the announce-without-availability worst case.
- **Terminal-fluent developers on multi-IDE workflows.** `tmux` panes per task already give scannable per-agent state cross-IDE. The CLI was the cross-tool primitive; embedding it in one IDE breaks that — what runs in JetBrains today does not run identically in Eclipse or Xcode.
- **Session amnesia masking.** A scannable list of one-off sessions can make the symptom — agents that forget everything between sessions — feel manageable when the deeper problem is memory across sessions ([RedMonk 2025-12-22](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)). The registry organises sessions; it does not give them shared memory.

## Example

A developer opens JetBrains, switches the chat panel to the agent picker, selects Copilot CLI agent with worktree isolation, and submits:

```
Investigate why test_user_signup_flow is flaky on CI. Reproduce locally,
identify the race, and propose a fix.
```

The CLI agent dispatches in a fresh worktree. The session appears in the unified sessions view with status `Working` and elapsed time ticking. The developer switches the agent picker to agent mode and starts a second task — refactoring the assertion helper — in workspace isolation against the current branch.

The view now shows two rows, filterable by agent type:

```text
Working
  CLI agent       investigate flaky test_user_signup_flow      4m
  Agent mode      refactor assert_user_state helper            1m
```

When the CLI agent moves to `Needs input`, the developer attaches to that row, answers, detaches, and returns to the registry — both sessions stay live, no chat log to scroll, no terminal pane to find.

## Key Takeaways

- The JetBrains unified sessions view is a chat-window registry keyed by `agent type + session ID`, aggregating CLI agent, agent mode, custom agents, and sub-agents into one filterable list ([GitHub Changelog 2026-05-13](https://github.blog/changelog/2026-05-13-introducing-copilot-cli-agent-and-unified-sessions-view-in-github-copilot-for-jetbrains-ides)).
- It shipped paired with a locally-running CLI agent that offers worktree or workspace isolation modes from the agent picker.
- The value is conditional: concurrency > 1, multiple invocation surfaces in use, and real isolation behind the rows. Below those thresholds the view is overhead.
- The pattern converged independently across Copilot JetBrains, Claude Code's `claude agents` agent view, Cursor 3's Agents Window, and Windsurf's Agent Command Center between November 2025 and May 2026.
- A unified view organises sessions but does not give them shared memory — session amnesia remains the underlying complaint developers report most ([RedMonk 2025-12-22](https://redmonk.com/kholterhoff/2025/12/22/10-things-developers-want-from-their-agentic-ides-in-2025/)).
- Business and Enterprise tenants require admin enablement of the Editor preview features policy before the surface is visible.

## Related

- [Editor and Manager Surface Separation in Agent IDEs](../../agent-design/editor-manager-surface-separation.md) — the broader two-surface pattern the unified sessions view is one instance of
- [Agent Mission Control](agent-mission-control.md) — the cloud-coding-agent counterpart of the JetBrains local view
- [Copilot Inline Agent Mode in JetBrains](inline-agent-mode.md) — one of the invocation surfaces the view aggregates
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md) — the standalone CLI behaviour that the IDE-hosted CLI agent wraps
- [Remote Session Control for Local CLI Agents](../../agent-design/remote-session-control.md) — cross-surface session control that pairs with the registry
