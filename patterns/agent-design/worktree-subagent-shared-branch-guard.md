---
title: "Worktree-Isolated Subagents and the Shared-Branch Guard"
description: "Claude Code 2.1.326 makes worktree-isolated subagents refuse some Bash git commands that can rewrite branches shared with the checkout; sessions are exempt."
tags:
  - agent-design
  - claude
aliases:
  - shared-branch guard
  - worktree branch-rewrite refusal
applies_to: "claude-code@2.1.326"
last_reviewed: 2026-11-21
maturity: emerging
status: current
---

# Worktree-Isolated Subagents and the Shared-Branch Guard

> Worktrees check out their own branches but share every branch ref. Claude Code 2.1.326 refuses some branch-rewriting git commands in isolated subagents, not sessions.

Claude Code 2.1.326 "Changed subagents isolated in a worktree to refuse, in any repository, some git commands in Bash that can rewrite branches shared with your checkout; sessions are not affected" ([changelog](https://code.claude.com/docs/en/changelog#2-1-326)). The entry names no command. It covers subagents, Bash, and "some" commands, so a design that needs the exact list cannot read it from the release.

## Why a worktree shares branches with the checkout

A worktree is "a separate checkout on its own branch" ([Common workflows](https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-worktrees)), with its own files and `HEAD`. The branch refs themselves sit in one place: "In general, all pseudo refs are per-worktree and all refs starting with `refs/` are shared" ([git-worktree](https://git-scm.com/docs/git-worktree)). Branches live under `refs/heads/`, and the manual's own example resolves `refs/heads/master` into the main repository's `.git`. So a branch moved from a subagent's worktree moves for the main checkout and every sibling too. Claude Code's docs say the same of the directory: "git commands in a worktree write to the main repository’s shared `.git` directory" ([Worktrees](https://code.claude.com/docs/en/worktrees#what-worktrees-share-with-the-main-checkout)).

Git guards one case itself. Even with `-f`, `git branch` "refuses to change an existing branch" that is checked out in another worktree linked to the same repository ([git-branch](https://git-scm.com/docs/git-branch)). That wording names only a branch checked out in another worktree. By it, a branch no worktree has checked out, such as the default branch while your checkout sits on a feature branch, gets no such refusal.

## What changed, and what stays outside

Isolation also runs four checks, which "read the path an edit targets, the directory a command runs in, and the text of the command" ([Worktrees](https://code.claude.com/docs/en/worktrees#how-claude-code-enforces-isolation)). The git-redirect check blocks git pointed at the main checkout through `git -C`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE`, or a `cd`. A ref update such as `git update-ref refs/heads/main HEAD`, run from inside the worktree, needs no redirect: its working directory is the worktree, and its write lands in the shared `.git`. The 2.1.326 entry defines its target by effect, commands that "can rewrite branches shared with your checkout", not by where they run.

| Outside the 2.1.326 refusal | Source |
|---|---|
| Sessions, including one started with `--worktree` | "sessions are not affected" ([changelog](https://code.claude.com/docs/en/changelog#2-1-326)); an isolated session still gets the four checks |
| PowerShell | The entry says "in Bash"; the docs give PowerShell "only the working-directory check" ([Worktrees](https://code.claude.com/docs/en/worktrees#how-claude-code-enforces-isolation)) |
| Commands the release does not list | "some git commands" |

The isolation guard has missed command shapes before. 2.1.299 "Fixed worktree-isolated sessions accepting some awk programs the isolation guard should refuse", and 2.1.309 fixed "some locale-prefixed commands" ([changelog](https://code.claude.com/docs/en/changelog)).

## Designing parallel subagent work around it

- Give each subagent its own branch and keep its commits there. A subagent worktree branches by default from your default branch, "rather than the parent session’s `HEAD`" ([Sub-agents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)).
- Move shared branches only from the parent: merging, fast-forwarding an integration branch, deleting a kept branch. A subagent that needs one returns the request instead. For the main checkout, the docs say "run the command yourself in a terminal outside the session" ([Errors](https://code.claude.com/docs/en/errors#command-blocked-by-the-worktree-isolation-checks)).
- Keep your own deny rules or hooks for the moves you must never see. The release list is unpublished, so it cannot stand in for one.

## Why it works

Git splits state per worktree: `HEAD` and the index belong to each tree, and `refs/` belongs to all of them ([git-worktree](https://git-scm.com/docs/git-worktree)). The four checks test paths and command text, and a branch rewrite run in place passes the path tests. A refusal keyed to "branches shared with your checkout" covers the shared half of the split.

## When this backfires

- Your fan-out has subagents rebase a stack or advance a shared integration branch. Those calls can now meet refusals, and the orchestrator has to own the move.
- The main conversation runs in a worktree session. The 2.1.326 refusal does not apply there.
- A team treats the guard as complete. "Some" commands, Bash only, and a record of gap fixes say otherwise.
- The steelman: every subagent worktree already checks out its own branch, and git refuses `branch -f` on a branch checked out elsewhere. For a fan-out that never touches shared branches, the guard changes little and each refusal costs a retry.

## Key Takeaways

- Each worktree checks out its own branch, but every branch ref under `refs/heads/` is shared, so a ref update in one worktree changes the branch every other worktree sees.
- 2.1.326 refuses "some" branch-rewriting Bash git commands in subagents only; sessions are not affected.
- Put every shared-branch move in the parent, and back the unlisted guard with your own deny rules.

## Related

- [Treating a Worktree as a Safety Boundary](../anti-patterns/worktree-as-safety-boundary.md) — why a worktree separates code, not authority
- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](../../workflows/worktree-isolation.md) — the base workflow this guard tightens
- [Write Boundaries Ship as a Setting, Read Boundaries as a Prompt](write-boundary-as-setting.md) — another Claude Code fence that covers some tools, not the filesystem
- [Claude Code Sub-Agents for Delegating Complex Tasks](../../tools/claude/sub-agents.md) — `isolation: worktree` and other subagent fields
