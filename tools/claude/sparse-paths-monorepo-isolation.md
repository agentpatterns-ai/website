---
applies_to: "claude-code@2.x"
title: "Sparse-Checkout Worktrees for Monorepo Agent Isolation"
description: "Use worktree.sparsePaths to limit an agent's file-system view to one service subtree — reducing context noise, startup time, and accidental blast radius in large monorepos."
tags:
  - agent-design
  - claude
last_reviewed: 2026-06-13
---

# Sparse-Checkout Worktrees for Monorepo Agent Isolation

> Sparse-checkout worktrees (`worktree.sparsePaths`) restrict an agent's working tree to one monorepo subtree, so it cannot touch unrelated services.

## The problem

An agent in a full monorepo checkout sees noise from every service. Glob results, file listings, and search outputs span the entire repo. An agent assigned to the payments service still sees ML infrastructure, frontend assets, and shared tooling. It cannot use that context, and it may change those files by accident.

[Worktree isolation](../../workflows/worktree-isolation.md) solves the multi-agent collision problem. It does not solve the scope problem. Each agent still works on a full repo checkout.

## worktree.sparsePaths

Claude Code's [`worktree.sparsePaths` setting](https://code.claude.com/docs/en/settings#worktree-settings) (added in [v2.1.76](https://code.claude.com/docs/en/changelog)) sets up git sparse-checkout in cone mode when `claude --worktree` creates a new worktree. Only the listed directories are written to disk.

```json
{
  "worktree": {
    "sparsePaths": [
      "packages/payments",
      "shared/utils",
      "config"
    ]
  }
}
```

Place this in `.claude/settings.json` (shared with the team) or `~/.claude/settings.json` (personal default).

When it creates the worktree, Claude Code runs `git sparse-checkout set --cone` with these paths. Files outside the listed directories are not written to disk. The agent cannot read or write them, and they do not appear in file listings or glob results.

A companion setting, `worktree.symlinkDirectories`, symlinks large directories such as `node_modules` and `.cache` from the main repo into each worktree, rather than copying them:

```json
{
  "worktree": {
    "sparsePaths": ["packages/payments", "shared/utils"],
    "symlinkDirectories": ["node_modules", ".cache"]
  }
}
```

## Effects on agent behavior

| Behavior | Without sparsePaths | With sparsePaths |
|----------|-------------------|-----------------|
| File listings | Entire repo | Listed directories only |
| Glob results | Repo-wide | Scoped to sparse cone |
| Read outside cone | Returns file | File not present on disk |
| Write outside cone | Succeeds | File not present; write fails |
| Startup time | Full checkout | Only listed paths written |

The filesystem enforces the scope constraint, not the agent. The agent cannot widen its own view. It would need a new worktree with updated `sparsePaths`.

## When to use

Use `worktree.sparsePaths` when:

- The monorepo has more than a few thousand files, and agents show slow startup or noisy search results
- Agent tasks stay within a known service or package
- You want hard isolation, so agents physically cannot touch sibling services

Skip it when:

- The task crosses service boundaries (API contract changes, cross-service refactors), because the narrow cone blocks reads it needs
- The repo is small enough that a full checkout is fast and noise is not a problem

## Trade-offs

Blast radius stays small. Agents cannot write outside the sparse cone, so an agent cannot corrupt a sibling service's files by accident.

Cross-service tasks cannot complete. Any task that reads or writes paths outside the declared cone fails. You recreate the worktree with wider `sparsePaths` to take on cross-service work, and this friction is intentional.

Path drift is the cost of committing the setting. If `sparsePaths` lives in `.claude/settings.json`, it applies to all worktrees, whatever the task. For a repo where most tasks are payments-scoped, that helps. For a repo with varied task domains, keep `sparsePaths` in personal settings, or override it per task at session start.

## Pairing with EnterWorktree and ExitWorktree

The [`EnterWorktree` and `ExitWorktree` tools](batch-worktrees.md#enterworktree-exitworktree) ([changelog](https://code.claude.com/docs/en/changelog)) let an agent manage a worktree session inside its conversation. A sub-agent can enter a sparse worktree scoped to its assigned service, finish its task, and exit. The orchestrator does not have to manage the worktree lifecycle in a shell script.

## Example

A monorepo contains `packages/auth`, `packages/payments`, `packages/notifications`, and shared libraries under `shared/`. An agent team is refactoring the payments service.

Project settings commit a scoped sparse cone:

```json
{
  "worktree": {
    "sparsePaths": [
      "packages/payments",
      "shared/types",
      "shared/db"
    ],
    "symlinkDirectories": ["node_modules"]
  }
}
```

Each `claude --worktree` invocation creates a worktree that contains only the payments package and the two shared directories it depends on. The agent's file search, glob results, and diff outputs stay within that cone. Agents assigned to `packages/auth` use a separate worktree with a different `sparsePaths` list — or a user-level setting that does not restrict scope.

## Key Takeaways

- `worktree.sparsePaths` uses git cone-mode sparse-checkout to restrict an agent's filesystem view to the declared directories.
- Files outside the cone are not present on disk — the constraint is enforced at the OS level, not by the agent.
- Combine with `worktree.symlinkDirectories` to avoid duplicating large shared directories.
- Cross-service tasks require wider `sparsePaths`; the intentional friction prevents accidental boundary violations.

## Related

- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](../../workflows/worktree-isolation.md)
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [Single-Branch Git for Agent Swarms](../../workflows/single-branch-git-agent-swarms.md)
