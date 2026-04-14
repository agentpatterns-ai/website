---
title: "Cursor 3 Agents Window: Parallel Agents and Worktree Isolation"
description: "Run multiple agents simultaneously across local, cloud, worktree, and SSH environments from a single Agents Window in Cursor 3."
tags:
  - agent-design
  - cursor
aliases:
  - cursor parallel agents
  - cursor worktree isolation
---

# Cursor 3 Agents Window

> Run multiple agents simultaneously across isolated environments from a single control surface.

Cursor 3, released April 2, 2026, introduced the Agents Window as the central multi-agent interface. The window runs agents in parallel across local workspaces, cloud environments, git worktrees, and remote SSH, and is accessed via `Cmd+Shift+P → Agents Window` ([Cursor changelog 3.0](https://cursor.com/changelog/3-0); [Cursor 3 announcement](https://cursor.com/blog/cursor-3)). Agent Tabs inside the window let you view multiple chats side-by-side or in a grid.

## /worktree Command

The `/worktree` command creates a separate git worktree so changes happen in isolation ([Cursor changelog 3.0](https://cursor.com/changelog/3-0)). Each worktree is a distinct checkout of the repository at its own filesystem path, so multiple agents can edit different parts of the codebase simultaneously without conflicts.

Use `/worktree` when:

- Two agents need to modify overlapping files
- You want to compare implementations side-by-side on separate branches
- A long-running agent task should not block your main working directory

This is the same isolation mechanism Claude Code exposes through the [`--worktree` flag and `EnterWorktree`/`ExitWorktree` tools](../claude/batch-worktrees.md). Cursor surfaces it as a slash command in the Editor, available alongside the Agents Window.

## /best-of-n Command

The `/best-of-n` command runs the same task in parallel across multiple models, each in its own isolated worktree, then presents outputs side-by-side for selection ([Cursor changelog 3.0](https://cursor.com/changelog/3-0)). It targets prompt tuning and model benchmarking workflows.

## Design Mode

Design Mode, available in the Agents Window, lets you annotate and target UI elements directly in the browser during browser-automation tasks ([Cursor changelog 3.0](https://cursor.com/changelog/3-0)). Toggle with `⌘+Shift+D`; `Shift+drag` selects an area, `⌘+L` adds the selected element to the chat, `⌥+click` adds it to the input. The agent receives visual context — element identification, layout, interaction state — without a separate screenshot-and-describe step.

## Comparison with Claude Code

Both tools use git worktree isolation for parallel agents, but the interaction model differs:

| | Cursor 3 | Claude Code |
|---|---|---|
| Entry point | `/worktree` slash command | [`--worktree` CLI flag or `EnterWorktree` tool](../claude/batch-worktrees.md) |
| Parallel task management | Agents Window UI panel | [`/batch` command or manual terminal sessions](../claude/batch-worktrees.md) |
| Model comparison | `/best-of-n` command | No built-in equivalent |
| Browser automation assist | Design Mode overlay | No built-in equivalent |
| Remote execution | Cloud + SSH environments | claude.ai/code (cloud), no SSH native |

The Agents Window consolidates task assignment, status monitoring, and result review into one surface. Claude Code's `/batch` command achieves similar parallelism but outputs to the terminal and relies on branch/PR conventions for result collection.

## When This Backfires

Parallel-agent workflows degrade under specific conditions:

- **Sequential dependencies dominate.** When Agent B depends on Agent A's output, you cannot parallelize. For short tasks, orchestration overhead can exceed any speedup from fan-out.
- **Error cascades compound across chained agents.** Minor per-agent inaccuracies propagate and can solidify into system-level false consensus. The recent "From Spark to Fire" study models this as cascade amplification, topological sensitivity, and consensus inertia, and reports a baseline defense success rate of only 0.32 in unmitigated LLM multi-agent systems ([Zhang et al., 2026, arxiv:2603.04474](https://arxiv.org/abs/2603.04474)).
- **Tightly coupled refactors.** If two agents must touch overlapping code semantics (not just overlapping files), a single agent with one worktree usually beats fan-out — decomposition overhead outweighs isolation gains.
- **Large legacy monorepos.** Parallel agents in separate worktrees still share the context-window ceiling per agent. If each worktree's relevant surface area does not fit in context, any gains are offset by missed dependencies.
- **Cloud runtime costs.** Cloud agents consume metered VM time while running; long-lived parallel sessions can accumulate cost quickly. Budget and rate-limit cloud agents before fanning out.

If the workflow is a single tightly-coupled refactor, or if the codebase is a legacy monorepo where scoping context is hard, a single isolated worktree (Cursor or Claude Code) is usually a better fit than fan-out.

## Example

Running two agents in parallel — one refactoring a module, one writing tests — without conflicts:

```
/worktree "Refactor src/payments to use the repository pattern"
/worktree "Write integration tests for src/payments current API"
```

Each `/worktree` invocation creates a separate checkout. The payments refactor and the test suite work against their own branches; neither agent blocks or corrupts the other's state.

For model comparison on a high-stakes task:

```
/best-of-n "Generate the OpenAPI spec for the payments API"
```

Cursor runs the prompt across multiple models in parallel worktrees, then surfaces outputs side-by-side so you pick the result to keep.

## Key Takeaways

- The Agents Window manages multiple simultaneous agents across local, cloud, worktree, and SSH environments
- `/worktree` provides git-level filesystem isolation — the same mechanism Claude Code uses, via a different interface
- `/best-of-n` fans a task across models, each in its own worktree, for direct output comparison
- Design Mode accelerates browser automation by delivering visual context inline
- Parallel agents degrade under sequential dependencies, context-window limits, and error cascades — isolated single-agent worktrees often beat fan-out for tightly-coupled work

## Related

- [/batch & Worktrees](../claude/batch-worktrees.md)
- [Sub-Agents](../claude/sub-agents.md)
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [Worktree Isolation](../../workflows/worktree-isolation.md)
