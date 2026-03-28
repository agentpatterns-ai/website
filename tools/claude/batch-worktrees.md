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

The `/batch` slash command orchestrates large-scale changes across a codebase in parallel. It researches the codebase, [decomposes the work into 5 to 30 independent units](https://code.claude.com/docs/en/skills), presents a plan for approval, then spawns one background agent per unit — each in an isolated git worktree.

Each agent works independently without interfering with other agents or your main working directory.

## --worktree Flag

The `--worktree` flag runs Claude Code in its own git worktree. Use this for manual parallel sessions — run multiple Claude Code instances on the same repo without conflicts. Project configs and [auto memory are shared across worktrees](https://code.claude.com/docs/en/memory) of the same repository.

## EnterWorktree / ExitWorktree

The `EnterWorktree` and `ExitWorktree` tools manage worktree sessions programmatically within an agent conversation:

- **`EnterWorktree`** — creates or enters an isolated git worktree, switching the agent's working directory to that worktree.
- **`ExitWorktree`** — cleanly leaves the worktree session and returns to the original working directory. Prior to v2.1.72, there was no dedicated exit mechanism; sessions had to be terminated rather than cleanly returned from. [unverified]

Typical lifecycle: enter the worktree, perform work, then exit to return to the parent context.

### Worktree Context in Hooks

Since v2.1.69, hook events fired during a worktree session include a `worktree` field containing: [unverified]

- **name** — the worktree identifier
- **path** — the filesystem path to the worktree
- **branch** — the branch checked out in the worktree

This allows hook commands to adapt behavior based on which worktree the agent is operating in.

## Background Agents

Run commands and agents in the background while continuing to work:

- Prefix commands with `&` to run in background [unverified]
- Use `/tasks` to view running background tasks [unverified]
- Use `/bashes` to view background shell commands [unverified]
- Use `/kill <task-id>` to stop background agents [unverified]

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

## Key Takeaways

- `/batch` decomposes large changes into parallel worktree-isolated units automatically
- `--worktree` provides manual worktree isolation for concurrent sessions
- `EnterWorktree` / `ExitWorktree` manage worktree sessions within agent conversations
- Hook events in worktree sessions include worktree name, path, and branch context
- Background agents let you continue working while agents execute [unverified]
- Cloud execution via claude.ai/code delegates to remote environments with automatic PR creation

## Unverified Claims

- Background agent commands (`&` prefix, `/tasks`, `/bashes`, `/kill <task-id>`) are described without a source link
- ExitWorktree availability claim (v2.1.72) has no source link
- Worktree context in hooks claim (v2.1.69) has no source link

## Related

- [Sub-Agents](sub-agents.md)
- [Hooks Lifecycle](hooks-lifecycle.md)
- [Worktree Isolation](../../workflows/worktree-isolation.md)
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [Developer Attention Management with Parallel Agents](../../human/attention-management-parallel-agents.md)
- [Agent Teams](agent-teams.md)
- [Extension Points](extension-points.md)
