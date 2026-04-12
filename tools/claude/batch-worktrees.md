---
title: "Claude Code /batch and Worktrees for AI Agent Development"
description: "Parallel execution at scale — decompose large changes into independent units, each in an isolated worktree. The /batch command orchestrates parallel agents."
tags:
  - agent-design
  - workflows
  - claude
---

# Claude Code /batch and Worktrees

> Parallel execution at scale — decompose large changes into independent units, each in an isolated worktree.

## /batch

[`/batch` is a bundled skill](https://code.claude.com/docs/en/commands) that orchestrates large-scale changes across a codebase in parallel. It researches the codebase, decomposes the work into 5 to 30 independent units, presents a plan for approval, then spawns one background agent per unit — each in [an isolated git worktree](https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees). Each agent implements its unit, runs tests, and opens a pull request.

Each agent works independently without interfering with other agents or your main working directory.

## --worktree Flag

The [`--worktree` (`-w`) flag](https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) creates an isolated worktree under `<repo>/.claude/worktrees/<name>` on a new branch `worktree-<name>` (branching from `origin/HEAD`) and starts Claude in it. Use this for manual parallel sessions — run multiple Claude Code instances on the same repo without conflicts. Project configs and [auto memory are shared across worktrees](https://code.claude.com/docs/en/memory) of the same repository.

### Why worktrees work

Git worktrees let multiple working directories share a single object database while keeping independent index and working-tree state. Each worktree has its own `HEAD`, branch, and checkout, so parallel edits cannot collide on disk, but all commits remain visible from the main repository's history. [Git's own worktree documentation](https://git-scm.com/docs/git-worktree) covers the underlying model.

## EnterWorktree / ExitWorktree

The `EnterWorktree` and `ExitWorktree` tools let an agent manage worktree sessions mid-conversation:

- **`EnterWorktree`** — creates a new worktree under `.claude/worktrees/`, branches from `HEAD`, and switches the session's working directory into it.
- **`ExitWorktree`** — leaves the worktree session and returns to the parent working directory. If no changes exist, the worktree and its branch are [cleaned up automatically](https://code.claude.com/docs/en/common-workflows#worktree-cleanup); if commits or uncommitted changes exist, Claude Code prompts to keep or remove.

Typical lifecycle: enter the worktree, perform work, then exit to return to the parent context.

### Worktree Hooks

Worktree events fire the [`WorktreeCreate` and `WorktreeRemove` hook events](https://code.claude.com/docs/en/hooks#worktreecreate), which also replace the default `git worktree` logic entirely when configured — useful for non-git version control (Perforce, Mercurial) or for branching off a non-default ref.

## Background Agents

`/batch` spawns [one background agent per unit](https://code.claude.com/docs/en/commands), so you can continue working in the foreground while units execute. To inspect or manage them, use [`/tasks` (also available as `/bashes`)](https://code.claude.com/docs/en/commands) to list and manage background tasks.

## Claude Code on the Web

[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) (claude.ai/code) lets you select a GitHub repo, describe a task, and Claude works in a remote environment — automatically creating a PR when done. Multiple tasks run in parallel across different repos.

## Example

Migrate all Python 3.8 type hints to 3.10+ syntax across a monorepo:

```bash
# /batch decomposes the task and spawns parallel worktree agents
claude /batch "Update all type hints in src/ from typing.Optional, typing.List, etc. to PEP 604 and built-in generics"
```

Claude researches the codebase, identifies 12 modules that need changes, presents a plan, then spawns 12 agents — each in its own worktree editing a separate module. Each agent commits to its own branch, and results are collected when all agents finish.

For manual parallel sessions:

```bash
# Terminal 1: refactor auth module in an isolated worktree
claude --worktree "Refactor src/auth to use dependency injection"

# Terminal 2: update tests in a separate worktree (no conflicts)
claude --worktree "Add integration tests for the payments service"
```

## When This Backfires

Parallel worktree decomposition is not free. The steelman for a single sequential agent is strong when:

- **Units aren't truly independent** — if the planned slices touch shared files or depend on one another's output, the parallel agents race on merge, and you pay review cost on 12+ PRs instead of one.
- **Review throughput is the bottleneck** — 12 small PRs consume more human review attention than one larger PR, and reviewers lose the cross-cutting context that explains why the changes belong together.
- **The repo lacks fast, hermetic tests** — each worktree agent runs tests in isolation; on repos with slow CI or flaky integration tests, the parallel fan-out multiplies CI cost and flake surface area.
- **The change is exploratory** — when the right shape of the refactor isn't known yet, a plan decomposed into 5–30 units locks in a premature design that later units can't cheaply revise.
- **Disk or file-watcher limits bite** — dozens of worktrees each run `node_modules` / `.venv` installs and can exhaust file-watcher quotas (`inotify` on Linux, `fs.inotify.max_user_watches`) or disk space on laptops.

For tightly-coupled refactors, a single agent with `--worktree` isolation (no fan-out) keeps the isolation benefit without the decomposition cost.

## Key Takeaways

- `/batch` decomposes large changes into parallel worktree-isolated units automatically
- `--worktree` provides manual worktree isolation for concurrent sessions
- `EnterWorktree` / `ExitWorktree` manage worktree sessions within agent conversations
- `WorktreeCreate` / `WorktreeRemove` hooks can replace the default worktree logic for non-git VCS
- `/tasks` (alias `/bashes`) lists and manages background tasks while you keep working
- Cloud execution via claude.ai/code delegates to remote environments with automatic PR creation
- Parallel decomposition adds review and merge cost — prefer a single worktree for tightly-coupled changes

## Related

- [Sub-Agents](sub-agents.md)
- [Hooks Lifecycle](hooks-lifecycle.md)
- [Worktree Isolation](../../workflows/worktree-isolation.md)
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [Developer Attention Management with Parallel Agents](../../human/attention-management-parallel-agents.md)
- [Agent Teams](agent-teams.md)
- [Extension Points](extension-points.md)
