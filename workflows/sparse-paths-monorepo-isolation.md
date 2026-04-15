---
title: "Sparse-Checkout Worktrees for Monorepo Agent Isolation"
description: "Use worktree.sparsePaths to limit an agent's file-system view to one service subtree — reducing context noise, startup time, and accidental blast radius in large monorepos."
tags:
  - agent-design
  - workflows
  - claude
---

# Sparse-Checkout Worktrees for Monorepo Agent Isolation

> Restrict an agent's working tree to a single service subtree in a large monorepo using `worktree.sparsePaths` — so the agent sees only the files it needs and cannot accidentally touch unrelated services.

## The Problem

Agents working inside a full monorepo checkout accumulate noise from every service. Glob results, file listings, and search outputs span the entire repo. An agent assigned to the payments service will encounter ML infrastructure, frontend assets, and shared tooling — context it cannot use and may accidentally modify.

[Worktree isolation](worktree-isolation.md) solves the multi-agent collision problem. It does not solve the scope problem: each agent still operates on a full repo checkout.

## worktree.sparsePaths

Claude Code's [`worktree.sparsePaths` setting](https://code.claude.com/docs/en/settings#worktree-settings) (added in [v2.1.76](https://code.claude.com/docs/en/changelog)) configures git sparse-checkout in cone mode when `claude --worktree` creates a new worktree. Only the listed directories are written to disk.

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

When the worktree is created, Claude Code runs `git sparse-checkout set --cone` with these paths. Files outside the listed directories are not written to disk — the agent cannot read or write them, and they do not appear in file listings or glob results.

A companion setting, `worktree.symlinkDirectories`, symlinks large directories like `node_modules` and `.cache` from the main repo into each worktree instead of duplicating them:

```json
{
  "worktree": {
    "sparsePaths": ["packages/payments", "shared/utils"],
    "symlinkDirectories": ["node_modules", ".cache"]
  }
}
```

## Effects on Agent Behavior

| Behavior | Without sparsePaths | With sparsePaths |
|----------|-------------------|-----------------|
| File listings | Entire repo | Listed directories only |
| Glob results | Repo-wide | Scoped to sparse cone |
| Read outside cone | Returns file | File not present on disk |
| Write outside cone | Succeeds | File not present; write fails |
| Startup time | Full checkout | Only listed paths written |

The scope constraint is enforced at the filesystem level, not by the agent. The agent cannot expand its own view — it would need a new worktree with updated `sparsePaths`.

## When to Use

Use `worktree.sparsePaths` when:

- The monorepo has more than a few thousand files and agents show sluggish startup or noisy search results
- Agent tasks are bounded to a known service or package
- You want hard isolation: agents physically cannot touch sibling services

Skip it when:

- The task explicitly crosses service boundaries (API contract changes, cross-service refactors) — the narrow cone will block necessary reads
- The repo is small enough that full checkout is fast and noise is not a problem

## Trade-offs

**Blast radius**: Agents cannot write outside the sparse cone. An agent cannot accidentally corrupt a sibling service's files.

**Cross-service tasks**: Any task that requires reading or writing paths outside the declared cone cannot complete. The worktree must be recreated with wider `sparsePaths` to accommodate cross-service work — this is intentional friction.

**Path drift**: If `sparsePaths` is committed to `.claude/settings.json`, it applies to all worktrees regardless of task. For a repo where most tasks are payments-scoped, this is a win. For a repo with variable task domains, keep `sparsePaths` in personal settings or override per-task at session start.

## Pairing with EnterWorktree / ExitWorktree

The [`EnterWorktree` and `ExitWorktree` tools](https://code.claude.com/docs/en/changelog) enable programmatic worktree session management within an agent conversation. A sub-agent can enter a sparse worktree scoped to its assigned service, complete its task, and exit — without the orchestrator needing to manage worktree lifecycle in a shell script.

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

- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](worktree-isolation.md)
- [Parallel Agent Sessions](parallel-agent-sessions.md)
- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md)
