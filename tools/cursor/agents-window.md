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

Cursor 3 (April 2, 2026) introduced the Agents Window as the central multi-agent interface. Each entry in the window is an independent agent operating in its own context window — local workspace, cloud environment, git worktree, or SSH remote. Results surface back to the panel when each agent finishes; you do not manage intermediate states or coordinate between agents manually. [unverified — specific UI mechanics pending source verification]

## /worktree Command

The `/worktree` command spawns an agent in an isolated git worktree. Each worktree is a separate checkout of the repository at its own filesystem path, so multiple agents can edit different parts of the codebase simultaneously without conflicts.

Use `/worktree` when:

- Two agents need to modify overlapping files
- You want to compare implementations side-by-side on separate branches
- A long-running agent task should not block your main working directory

This is the same isolation mechanism Claude Code uses via the `--worktree` flag and `EnterWorktree`/`ExitWorktree` tools — Cursor exposes it as a slash command within the Agents Window rather than a CLI flag.

## /best-of-n Command

The `/best-of-n` command runs the same task against multiple models or configurations in parallel and presents the outputs for comparison. It targets prompt tuning and model benchmarking workflows: you define the task once, Cursor fans it out across N agents, and you select the best result. [unverified — parameter syntax not confirmed in source]

## Design Mode

Design Mode overlays annotation controls on a live browser preview during browser automation tasks. The agent receives visual UI feedback — element identification, layout context, interaction state — without a separate screenshot-and-describe step. [unverified — opt-in vs. automatic behavior not confirmed]

## Comparison with Claude Code

Both tools use git worktree isolation for parallel agents, but the interaction model differs:

| | Cursor 3 | Claude Code |
|---|---|---|
| Entry point | `/worktree` slash command in Agents Window | `--worktree` CLI flag or `EnterWorktree` tool |
| Parallel task management | Agents Window UI panel | `/batch` command or manual terminal sessions |
| Model comparison | `/best-of-n` command | No built-in equivalent |
| Browser automation assist | Design Mode overlay | No built-in equivalent |
| Remote execution | Cloud + SSH environments | claude.ai/code (cloud), no SSH native |

The Agents Window consolidates task assignment, status monitoring, and result review into one surface. Claude Code's `/batch` command achieves similar parallelism but outputs to the terminal and relies on branch/PR conventions for result collection.

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

Cursor fans the prompt across multiple models, displays outputs side-by-side, and you pick the result to keep. [unverified — exact UI for result selection not confirmed]

## Key Takeaways

- The Agents Window manages multiple simultaneous agents across local, cloud, worktree, and SSH environments
- `/worktree` provides git-level filesystem isolation — the same mechanism Claude Code uses, via a different interface
- `/best-of-n` fans a task across models for direct output comparison — no Claude Code equivalent
- Design Mode accelerates browser automation by delivering visual context inline
- Both Cursor and Claude Code converge on worktree isolation as the primary parallelism primitive; Cursor adds a consolidated UI surface and model comparison tooling

## Unverified Claims

- Agents Window UI mechanics: specific limits on simultaneous agents, queue behavior, result aggregation details not confirmed against primary source
- `/best-of-n` parameter syntax (whether N is user-specified) not confirmed
- Design Mode activation model (opt-in vs. automatic) not confirmed
- SSH remote execution scope and authentication method not detailed in available sources

## Related

- [/batch & Worktrees](../claude/batch-worktrees.md)
- [Sub-Agents](../claude/sub-agents.md)
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [Worktree Isolation](../../workflows/worktree-isolation.md)
