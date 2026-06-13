---
title: "Lazy Worktree Isolation: Enter the Worktree on First Write, Not on Dispatch"
term: "Lazy Worktree Isolation"
description: "Background agent sessions start in the parent checkout and relocate into an isolated git worktree only on the first Edit or Write tool call."
tags:
  - workflows
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-12
status: current
---

# Lazy Worktree Isolation: Enter the Worktree on First Write, Not on Dispatch

> Background agent sessions start in the parent checkout and relocate into an isolated git worktree only on the first Edit or Write tool call.

The default in Claude Code v2.1.139+ is *lazy*, not eager: "Every background session, whether started from agent view, `/bg`, or `claude --bg`, starts in your working directory. Before editing files, Claude moves the session into an isolated git worktree under `.claude/worktrees/`" ([agent-view docs](https://code.claude.com/docs/en/agent-view#how-file-edits-are-isolated)). Read-only research costs nothing in worktree overhead; write-intent is the latch that triggers the relocation.

## The Eager-on-Dispatch Failure Mode

Eager isolation provisions a worktree for every session at dispatch — research-only sessions pay the same fixed cost as write-bound sessions. A worktree is a fresh checkout, so per-worktree env setup runs every time: `npm install`, `.venv` creation, the `.worktreeinclude` copy of `.env`/`.env.local` ([worktrees docs §Copy gitignored files](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees)). A Cursor background-agents report measured "9.82 GB of disk space" consumed in a 20-minute session on a roughly 2 GB codebase from automatic worktree creation; six concurrent agents on the same repo project out to 30+ GB ([Zylos Research summary](https://zylos.ai/research/2026-02-22-git-worktree-parallel-ai-development)). That cost is what eager-on-dispatch pays for every session whether or not it writes. Lazy isolation pays it only for sessions that demonstrate write intent.

## Three Implementation Layers

The laziness contract is not a single feature — it composes three layers in the Claude Code agent harness.

### Layer 1: Detection

The harness watches for the first Edit, Write, MultiEdit, or NotebookEdit tool call. Read, Grep, Glob, and Bash never trip the latch. The trigger is the agent's *demonstrated* intent to modify state, not its declared intent at dispatch.

### Layer 2: Skip-Rule Evaluation

Before relocating, the harness checks three skip rules. The relocation is suppressed when any holds ([agent-view docs](https://code.claude.com/docs/en/agent-view#how-file-edits-are-isolated)):

1. **Already inside a linked worktree.** "The session is already inside a linked git worktree, whether Claude created it under `.claude/worktrees/` or you created it with `git worktree add` somewhere else." Composability with the user's own `git worktree` workflow — the latch never nests.
2. **Not a git repo and no `WorktreeCreate` hook.** "The working directory isn't a git repository and no `WorktreeCreate` hook is configured." Outside git, "sessions write to the working directory directly and aren't isolated from each other" — the docs warn that parallel sessions in this mode collide. Configure a `WorktreeCreate` hook to restore isolation under SVN, Perforce, or Mercurial ([worktrees docs §Non-git version control](https://code.claude.com/docs/en/worktrees#non-git-version-control)).
3. **Write target outside the working directory.** "The write is outside the working directory." A session writing to `~/notes` or `/tmp` does not get relocated — the worktree only protects edits inside the project tree.

Each skip rule encodes a *do nothing more than necessary* invariant. The latch fires only when the relocation would actually change isolation properties.

### Layer 3: `EnterWorktree` Relocation

If no skip rule fires, the harness invokes its internal `EnterWorktree` tool. It creates `.claude/worktrees/<session-id>/`, branches from `origin/HEAD` — or local `HEAD` if `worktree.baseRef: "head"` is set ([worktrees docs §Choose the base branch](https://code.claude.com/docs/en/worktrees#choose-the-base-branch)) — copies `.worktreeinclude` files, then re-runs the original edit against the new path. The session's working directory has now changed under it: subsequent reads, writes, and tool calls resolve against `.claude/worktrees/<session-id>/`.

## Triggers and Constraints

The lazy-vs-off axis is a project-level setting, not a hardcode. From Claude Code v2.1.143+, setting `worktree.bgIsolation` to `"none"` in `.claude/settings.json` disables Layers 2 and 3 entirely ([agent-view docs](https://code.claude.com/docs/en/agent-view#how-file-edits-are-isolated)):

```json
{
  "worktree": {
    "bgIsolation": "none"
  }
}
```

With this set, "background sessions then edit your working copy directly without moving into a worktree first." Use it for repos where worktrees are impractical — large `node_modules` trees that resist symlinking, file-watcher quotas (`fs.inotify.max_user_watches`) that crash at the second worktree, or build systems that hardcode paths relative to the original checkout.

For sub-agent dispatch, the equivalent eager mode is `isolation: worktree` in the sub-agent's frontmatter ([sub-agents docs](https://code.claude.com/docs/en/sub-agents)). That setting opts the sub-agent into worktree creation at dispatch, before any write — useful when you know the sub-agent will definitely write and want to skip the latch's transition step.

## Multi-Tool Coverage

Claude-Code-specific. The lazy latch, `worktree.bgIsolation`, and `WorktreeCreate` hook are documented surfaces in Claude Code v2.1.139+ ([agent-view](https://code.claude.com/docs/en/agent-view), [worktrees](https://code.claude.com/docs/en/worktrees)). Copilot CLI uses a different primitive — per-agent OS workspaces — that resolves the same isolation problem at the OS/container layer rather than the VCS layer ([Workspace vs Worktree Isolation in Copilot CLI](https://www.kenmuse.com/blog/workspace-vs-worktree-isolation-in-copilot-cli/)); in that model the lazy-vs-eager axis belongs to the workspace manager, not git. Cursor's background agents create eager worktrees by default with no documented lazy mode.

## Why It Works

Lazy isolation works because file-system isolation is *only* needed for writes. Reads against the parent checkout are race-free as long as no other session is editing the same inode, and worktrees share the git object database so a worktree of the same SHA is logically indistinguishable from the parent for read purposes ([git worktree docs](https://git-scm.com/docs/git-worktree)). The fixed cost of `git worktree add` plus per-worktree env init only buys you something when a session actually writes. Deferring the cost until that demonstration of intent is the same defer-until-needed reasoning that justifies JIT compilation in [agent runtimes](../agent-design/agent-jit-compilation.md): pay for the heavyweight setup only when the lighter-weight path can no longer satisfy the request.

## When This Backfires

Lazy isolation has costs eager-on-dispatch does not have:

- **Write-bound fan-outs pay the latch overhead for nothing.** When `/batch` decomposes work into 5–30 modify-and-test units, every sub-agent will write — the latch fires in every session, and the extra code branch saves zero disk. For these workflows, set `isolation: worktree` on the sub-agent ([sub-agents docs](https://code.claude.com/docs/en/sub-agents)) so the worktree is created at dispatch. See [Claude Code /batch and Worktrees](../tools/claude/batch-worktrees.md) and its *When This Backfires* section for the broader fan-out trade-off.
- **The transition has a known recovery-path bug.** Issue [#62372](https://github.com/anthropics/claude-code/issues/62372) documents that the `bgIsolation` guard tells agents to call `EnterWorktree`, but the tool's schema is deferred and must be fetched via `ToolSearch` first; without that, the agent hits `InputValidationError` and stalls. The lazy design introduces a transition surface that eager-on-dispatch doesn't have.
- **Orchestrators that snapshot cwd at dispatch break silently.** The session's working directory changes under it on first write. Any hook, transcript writer, or path-recording orchestrator that captured cwd at session start now points at the parent checkout, not the worktree. Coordinating the invariant across the harness is non-trivial.
- **Non-git repos without a `WorktreeCreate` hook get no isolation.** The second skip rule routes writes straight to the working copy. Parallel sessions race. The docs warn but the default is unsafe for parallel non-git workflows ([issue #60418](https://github.com/anthropics/claude-code/issues/60418) tracks the docs gap).

## Example

A background session investigates a flaky test, finds the failure is in a shared helper, and submits a one-line fix. The latch fires exactly once — on the fix.

```text
$ claude --bg "investigate the flaky SettingsChangeDetector test"
backgrounded · 7c5dcf5d · investigate-flaky-test

# Session cwd: /home/user/project   (parent checkout)
# Tool calls so far: Read (10), Grep (4), Bash (2), Read (6)
# Disk overhead: 0 bytes — no worktree exists

# Agent decides the bug is in src/util/clock.ts and calls Edit:
# Edit(file_path="src/util/clock.ts", old_string=..., new_string=...)

# Lazy latch fires:
#   1. git worktree add .claude/worktrees/7c5dcf5d/ -b worktree-7c5dcf5d
#   2. Session cwd -> /home/user/project/.claude/worktrees/7c5dcf5d/
#   3. Re-run Edit against src/util/clock.ts in the new worktree
#   4. Subsequent Read/Edit/Bash resolve against the worktree path
```

A read-only investigation that ends in *no* fix never creates a worktree — the latch was armed and never fired. A fan-out of ten such sessions where eight find the bug elsewhere and only two write produces two worktrees, not ten.

## Key Takeaways

- Lazy isolation is the documented default for background sessions in Claude Code v2.1.139+ — the worktree is created on the first Edit/Write, not at dispatch.
- Three skip rules encode the *do nothing more than necessary* invariant: already in a worktree, no git and no hook, write outside cwd.
- `worktree.bgIsolation: "none"` (v2.1.143+) disables the latch entirely for repos where worktrees are impractical — the design is a setting, not a hardcode.
- A `WorktreeCreate` hook generalises the laziness contract beyond git to SVN, Perforce, and Mercurial.
- Write-bound fan-outs save nothing and add a transition surface — use eager `isolation: worktree` on sub-agents that will definitely write.

## Related

- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](worktree-isolation.md)
- [Sparse-Checkout Worktrees for Monorepo Agent Isolation](../tools/claude/sparse-paths-monorepo-isolation.md)
- [Parallel Agent Sessions](parallel-agent-sessions.md)
- [Claude Code /batch and Worktrees](../tools/claude/batch-worktrees.md)
