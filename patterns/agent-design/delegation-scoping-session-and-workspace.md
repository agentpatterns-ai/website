---
title: "Delegation Scoping: Session Relationship and Workspace"
term: "Delegation Scoping"
description: "Scoping delegated work takes two independent choices: whether the task belongs to the current session's deliverable, and whether it needs repository files."
tags:
  - agent-design
  - multi-agent
  - tool-agnostic
aliases:
  - session relationship and workspace
  - dispatch-time delegation scoping
  - delegated work scoping
last_reviewed: 2026-10-07
maturity: emerging
status: current
---

# Delegation Scoping: Session Relationship and Workspace

> Scoping a delegated task takes two separate choices: whether it belongs to the current session's deliverable, and whether it needs repository files.

Delegation scoping is the dispatch-time decision about where a delegated task's results land and what filesystem it gets. VS Code 1.140 states the rule: "Make two separate decisions when you ask an agent to delegate work. First, decide whether the task belongs to the current session's plan or deliverable. Then specify a workspace only if the task needs repository files, and request a worktree only if file changes need isolation" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)). The second decision does not follow from the first, and the worktree is a third choice narrower than both.

## When the choice is yours

Three conditions decide whether the choice reaches you at all.

Your harness still asks you about the worktree. Codex ships the opposite default, and the 0.156.0 release notes record that "worktree support is now enabled by default" ([Codex 0.156.0 release notes](https://github.com/openai/codex/releases/tag/rust-v0.156.0)). Claude Code decides for you too: a session dispatched from agent view "moves into a worktree of its own before it edits files" ([Run agents in parallel](https://code.claude.com/docs/en/agents)). Where the harness decides, your lever is the base ref rather than the isolation flag.

A workspace-free session exists. That is an Agent Host concept: in the remote-delegation tools, "Sessions have no workspace unless you specify one" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)). The Claude Code and Codex pages cited here document no equivalent. Their second axis reads as which folder rather than whether.

Per-chat folders are turned on. "Multi-folder sessions are experimental and disabled by default", and you set them per harness in user-scoped `settings.json`. There is "no UI for adding a folder or choosing the folder of a peer chat" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)). Until that setting is on, every peer chat shares the parent's folder and the second axis collapses.

## The two axes

| Belongs to the current deliverable | Needs repository files | Dispatch |
|---|---|---|
| Yes | No | Peer chat in this session, reusing the current workspace and checkout |
| Yes | Yes | Peer chat; add a worktree once it writes |
| No | No | Independent session with no workspace |
| No | Yes | Independent session; name the folder, add a worktree once it writes |

A peer chat that reuses the checkout suits "research, planning, or related work that doesn't need isolated file changes". Compare approaches in parallel and each peer chat takes its own fresh worktree, so "Each approach gets its own branch, changes, and pull request" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)).

## Why it works

The axes stay separate because they govern separate resources. The folder is the unit that carries session state: "Each chat uses its folder for its terminal, tasks, changes, pull request, and Agent merge state. Chats that use the same folder share that state" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)).

Worktrees govern write collision instead. They "give each session a separate git checkout, so parallel sessions each edit their own copy of the files". Claude Code asks that collision question on its own, as "Do the tasks touch the same files?", apart from who coordinates the work. Where isolation is unavailable, the docs fall back to partitioning files by hand. "Agent teams don't isolate teammates in worktrees", so you partition the work and give each teammate a different set of files ([Run agents in parallel](https://code.claude.com/docs/en/agents)).

## When this backfires

- File-changing work goes to a peer chat that reuses the checkout. Both chats then share one set of changes, one pull request, and one merge state.
- An independent session gets a worktree it never needed. Naming an existing folder adds no checkout; a worktree does: "A worktree is a fresh checkout, so initialize your development environment there" ([Claude Code worktrees](https://code.claude.com/docs/en/worktrees)).
- A worktree is requested for work that must read the parent's uncommitted changes. The default base branches "from the repository's default branch on the remote, usually `main`, so the worktree starts from a clean tree matching the remote" ([Claude Code worktrees](https://code.claude.com/docs/en/worktrees)). Setting `worktree.baseRef` to `"head"` carries "your unpushed commits and feature-branch state", but not uncommitted edits, so the agent still misses that work. Commit first, or skip the worktree.
- A workspace-free session turns out to need the repository. It "doesn't inherit the source folder", and the delegation tools "do not clone or copy the originating workspace" ([VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140)).

Josh McKinney's practice reference argues the opposite default, to "Give each independent agent task its own workspace and execution identity", and conditions it the same way: "Isolation has setup cost. For tiny read-only questions, a side session may be enough" ([Isolate Agent Workspaces](https://www.joshka.net/practice/patterns/isolate-agent-workspaces/)). Default-isolate is the safer error when you cannot tell whether the task writes.

## Example

The release notes give a prompt for each end of the grid. The first keeps the work in this session and on this checkout, and states the read-only constraint:

```text
Create a peer chat in this session that reuses the current workspace and
checkout to review the authentication flow. Do not modify files.
```

The second moves the work out of the session entirely and gives it no files at all:

```text
Create an independent session with no workspace to research licensing
options for a separate project.
```

Both come from [VS Code 1.140 release notes](https://code.visualstudio.com/updates/v1_140). Neither asks for a worktree, because neither writes.

## Key Takeaways

- Decide session relationship and workspace need separately. One answer cannot serve both.
- A peer chat that reuses the checkout is for work that does not change files. The shared checkout is the reason.
- Add a worktree for the write case only. It costs a fresh checkout and its environment setup.
- Check what your harness already decided. Codex enables worktrees by default; an agent-view session relocates before it edits.
- A worktree branched fresh from the remote default branch cannot see your unpushed commits. Set the base ref to `"head"` to carry them. Uncommitted edits stay invisible either way.

## Related

- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md) — the prior question of whether to delegate at all.
- [Delegation Threshold Calibration for Orchestrator Agents](delegation-threshold-calibration.md) — where an orchestrator sets its delegate-or-inline line.
- [Cross-Session Peer Messaging with a Posture-Keyed Inbox Gate](cross-session-peer-messaging.md) — passing findings between sessions once they exist.
- [Lazy Worktree Isolation](../../workflows/lazy-worktree-isolation.md) — when a harness enters the worktree instead of asking.
- [Treating a Worktree as a Safety Boundary](../anti-patterns/worktree-as-safety-boundary.md) — what worktree isolation does not contain.
