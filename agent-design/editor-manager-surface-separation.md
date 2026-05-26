---
title: "Editor and Manager Surface Separation in Agent IDEs"
description: "When you run more than one agent at a time, the editor and the orchestration dashboard serve different attention modes — collapsing them into one chat panel breaks both."
tags:
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - editor manager surface
  - two-surface agent UX
  - agent dashboard vs editor
last_reviewed: 2026-05-27
---

# Editor and Manager Surface Separation in Agent IDEs

> A two-surface UX pattern: an Editor for tactical edits and a Manager for dispatching and monitoring parallel agents. The pattern matters once concurrency exceeds one.

The editor-and-manager pattern splits an agent IDE into two surfaces — an Editor View coupled to cursor and buffer for inline edits, and a Manager Surface (dashboard, agents window, or mission control) for dispatching, monitoring, and reviewing autonomous agents running in parallel across editor, terminal, and browser. Four major dev tools converged on this shape between October 2025 and May 2026: Google Antigravity (Editor View + Manager Surface, [Google I/O 2026](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/)), Cursor 3 (Agents Window replaced Composer, [Cursor 3 Agents Window](../tools/cursor/agents-window.md)), GitHub Copilot ([inline agent mode](../tools/copilot/inline-agent-mode.md) + Mission Control, [Agent Mission Control](../tools/copilot/agent-mission-control.md)), and Claude Code (interactive session + `claude agents`, [Claude Code agent view](https://code.claude.com/docs/en/agent-view)).

## When This Pattern Applies

Benefit scales with concurrency, not with how often you use an agent:

- **Concurrency > 1** — two or more agent tasks running simultaneously need per-task state at a glance, not state buried in chat transcripts.
- **Long-running tasks** — tasks taking minutes to hours that emit intermediate artifacts (screenshots, recordings, transcripts) cannot be watched from the editor; the Manager Surface holds them as scannable rows.
- **Heterogeneous task mix** — one agent reviewing a PR, another fixing a flaky test, a third on docs — the surface lets you pin attention to whichever needs you next.

At-most-one-agent workflows where most work is inline tab-completion get nothing — the dashboard round trip is pure cost and the tab goes stale.

## The Two Attention Modes

| Surface | Attention shape | What the UI optimises for |
|---------|-----------------|---------------------------|
| Editor | Tight buffer-cursor coupling; character-level latency | Inline completion, minimal chrome, fast feedback against one file |
| Manager | Loose coupling across N parallel tasks; minutes-to-hours horizon | Scannable per-task state, at-a-glance progress, ignorable most of the time |

Claude Code's agent view illustrates the Manager mode: each row's one-line summary is Haiku-generated and refreshes at most every fifteen seconds, "so the row can tell you what the session is doing, what it needs, or what it produced without opening the transcript" ([Claude Code agent view](https://code.claude.com/docs/en/agent-view)). Aggregation is the point — raw transcripts are the wrong granularity for orchestration.

## Cross-Tool Convergence

| Tool | Editor Surface | Manager Surface |
|------|----------------|-----------------|
| Google Antigravity | Editor View | Manager Surface ([Google I/O 2026](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/)) |
| Cursor 3 | Inline editor and chat (`Cmd+I`) | Agents Window across local, cloud, worktree, SSH ([Cursor 3 Agents Window](../tools/cursor/agents-window.md)) |
| GitHub Copilot | [Inline agent mode](../tools/copilot/inline-agent-mode.md) ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)) | Mission Control ([GitHub Changelog 2025-10-28](https://github.blog/changelog/2025-10-28-a-mission-control-to-assign-steer-and-track-copilot-coding-agent-tasks/)) |
| Claude Code | Interactive `claude` session | `claude agents` view ([Claude Code agent view](https://code.claude.com/docs/en/agent-view)) |

Detail varies — Cursor's window "resembl[es] a Kubernetes dashboard rather than a chat window," Claude Code's is a terminal list grouped by Pinned / Ready for review / Needs input / Working / Completed — but the structural choice is the same: aggregated per-agent state lives outside the editor.

## Why It Works

Tactical editing and strategic orchestration have different attention shapes, and a single chat panel optimises for neither. Inline edits need a tight buffer-cursor loop with minimal chrome; orchestration needs scannable state the developer can glance at and ignore. One panel produces the worst-of-both case: too noisy when an agent emits dozens of tool calls per minute, too sparse when a parallel task finishes and there is no signal to notice. Microsoft Design names the fix directly: "a chat template has no pattern for making agent steps visible… the architectural fix is separating the conversation from the activity stream" ([Microsoft Design — UX design for agents](https://microsoft.design/articles/ux-design-for-agents/)). The convergence across four independent vendors between October 2025 and May 2026 — none of them coordinating — is itself evidence.

## When This Backfires

The pattern is not free:

- **Solo, single-agent workflows.** Never running more than one agent makes the Manager Surface overhead — the dashboard round trip adds work without paying back.
- **No concurrency primitive.** A Manager Surface without worktree, sandbox, or session isolation is theatre. Claude Code, Cursor, and Antigravity all back the surface with [worktree](../tools/claude/batch-worktrees.md) or sandbox isolation; tools without it get cost without benefit.
- **Heavy inline-edit workflows.** When most agent use is tab-completion or single-cursor refactors, the Manager Surface stays unopened — pure learning-curve and real-estate cost.
- **First 30 days.** New users mis-route work to the wrong surface (drafting orchestration prompts inline, asking for one-line refactors from the dashboard). Surface clarity is a learning cliff.
- **Terminal-first workflows.** Developers in tmux already have separate panes for dispatch and monitoring; the pattern is most additive when the host UI lacks window management.

A second counter-concern is fragmentation: each surface flip is "a micro-interruption that forces the brain to reload context" ([Arya — Hidden Cost of Too Many AI Tools](https://arya.ai/blog/ai-context-fragmentation)). The pattern only pays when the Manager Surface's scannability gain exceeds per-flip switch cost — exactly the threshold concurrency > 1 captures.

## Example

The convergent designs across tools all expose the same surface-to-attention-mode mapping. Claude Code's `claude agents` view is the most documented:

```text
Pinned
  ✽ clawd walk cycle          Write assets/sprites/clawd-walk.png           3m

Ready for review
  ∙ jump physics              github.com/example/game/pull/2048          ●  2h

Needs input
  ✻ power-up design           needs input: double jump or wall climb?       1m

Working
  ✽ collision detection       Edit src/physics/CollisionSystem.ts           2m
  ✢ playtest level 3          run 12 · all checkpoints cleared           in 4m

Completed
  ✻ title screen              result: menu, options, and credits done       9m
```

Each row is a separate agent session, grouped by what attention it needs. The developer scans the Manager Surface for `Needs input` rows, attaches with `Enter` to enter the full conversation for the one row that requires their judgment, then `←` back to the dashboard. The editor surface — opened by `claude` directly — stays available for tactical work that does not warrant a dispatched session ([Claude Code agent view](https://code.claude.com/docs/en/agent-view)).

## Key Takeaways

- The two-surface pattern split between Editor and Manager has converged across Antigravity, Cursor, Copilot, and Claude Code between October 2025 and May 2026 — it is now the dominant agent-IDE UX shape for parallel agent work.
- The benefit is conditional on concurrency. Below one parallel agent, the Manager Surface adds overhead; above one, it absorbs context-switching cost that a chat panel cannot.
- The two surfaces map to two attention modes: tight buffer-cursor coupling for inline edits, loose scannable state for orchestration. A single chat panel cannot satisfy both — it becomes too noisy for editing and too sparse for orchestration.
- A Manager Surface is only as useful as the concurrency primitive behind it. Without worktree-style or environment-isolated parallel execution, the dashboard is theatre.
- The surface separation has a learning-curve cost — new users mis-route work to the wrong surface for ~30 days before the mapping becomes intuitive.

## Related

- [Cursor 3 Agents Window](../tools/cursor/agents-window.md) — the Cursor-specific instance of the Manager Surface; the cross-tool comparison anchors much of this page
- [Agent Mission Control for Orchestrating Agent Tasks](../tools/copilot/agent-mission-control.md) — GitHub Copilot's Manager Surface for parallel agent tasks
- [VS Code Agents App: Agent-Native Parallel Task Execution](vscode-agents-parallel-tasks.md) — companion analysis of VS Code's headless agent panel; the same pattern applied to a different host editor
- [Developer Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md) — the human-factors side: why the Manager Surface absorbs scheduling cost that a chat panel cannot
- [Background TODO Agent](background-todo-agent.md) — pattern for asynchronous tasks that the Manager Surface is built to host
