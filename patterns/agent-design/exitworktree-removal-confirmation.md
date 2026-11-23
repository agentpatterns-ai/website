---
title: "Confirming Before an Agent Removes a Worktree With Unsaved Work"
term: "Worktree Removal Confirmation"
description: "Since Claude Code 2.1.327, ExitWorktree asks before removing a worktree that may hold unsaved work, and is refused where nobody can answer unless a rule or mode allows it. Check git status in your own scripts."
tags:
  - agent-design
  - automation
  - testing-verification
  - claude
aliases:
  - ExitWorktree confirmation
  - worktree removal guard
  - unsaved work worktree check
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-23
maturity: emerging
status: current
---

# Confirming Before an Agent Removes a Worktree With Unsaved Work

> Since Claude Code 2.1.327, `ExitWorktree` asks before it removes a worktree that may hold unsaved work. In don't-ask mode or with nobody to answer, the removal is refused unless an allow rule, auto mode or bypass permissions mode allows it.

Claude Code 2.1.327 (November 17, 2026) "Changed `ExitWorktree` to ask before removing a worktree that may hold unsaved work; refused in don't-ask mode or with nobody to answer, unless an allow rule, auto or bypass permissions mode allows it" ([changelog 2.1.327](https://code.claude.com/docs/en/changelog#2-1-327)). The stakes are in the worktrees page: removing a worktree "deletes the worktree directory and its branch, along with all the work in them" ([worktrees](https://code.claude.com/docs/en/worktrees#clean-up-worktrees)).

## The three outcomes

The entry names three cases. The third row is my reading of the entry, not a quote.

| Case | Outcome | Source |
|---|---|---|
| A person can answer | `ExitWorktree` asks first | "ask before removing a worktree that may hold unsaved work" |
| Don't-ask mode, or nobody to answer | The removal is refused | "refused in don't-ask mode or with nobody to answer" |
| An allow rule, auto mode or bypass permissions mode applies | The removal goes ahead (inference) | "unless an allow rule, auto or bypass permissions mode allows it" |

The entry does not say whether auto mode's classifier still reviews the call, or whether an allow rule also skips the question when a person is present. The permissions reference says "Rules are evaluated in order: deny, then ask, then allow" ([permissions](https://code.claude.com/docs/en/permissions)), which fits the reading but does not name `ExitWorktree`.

Don't-ask mode shows why the second row refuses and does not guess. In that mode Claude Code "auto-denies every tool call that would otherwise prompt you", though "a mod you installed can still approve some of those calls" ([permission modes](https://code.claude.com/docs/en/permission-modes)). A removal that needs an answer is refused, and I expect the worktree to stay on disk (inference). [Deny-fallback permissions](deny-fallback-unattended-permissions.md) covers the same trade for every tool.

## What counts as unsaved work

The 2.1.327 entry says "may hold unsaved work" and does not define it. The worktrees page describes what Claude checks when you exit an interactive worktree session: "changed or untracked files, uncommitted work inside checked-out submodules, and new commits" ([worktrees](https://code.claude.com/docs/en/worktrees#clean-up-worktrees)). When Claude Code "can't count the worktree's changes or can't inspect its submodule checkouts", the same page says it prompts instead of removing the worktree automatically.

That section describes the exit dialog, not the tool. I expect the tool to apply the same checks (inference). The worktrees page as fetched on 2026-11-23 does not mention the `ExitWorktree` prompt.

The tools reference disagrees on the surface. As fetched on 2026-11-23, its table lists `ExitWorktree` with "No" in the "Permission required" column ([tools reference](https://code.claude.com/docs/en/tools-reference)). Neither source says which is current, so test the prompt on your version before you rely on it.

Two other entries show removal has more guards. 2.1.326 changed `ExitWorktree` to "refuse removing a worktree while a background subagent or shell command may still be running in it, unless Claude passes `discard_changes`" ([changelog 2.1.326](https://code.claude.com/docs/en/changelog#2-1-326)). 2.1.330 fixed `ExitWorktree` "deleting a worktree that another running Claude Code session was working in" ([changelog 2.1.330](https://code.claude.com/docs/en/changelog#2-1-330)).

## Unattended runs

A non-interactive run has nobody to answer. The worktrees page says `-p` runs "have no exit prompt, so Claude doesn't clean up their worktrees", and to remove one you run `git worktree remove` ([worktrees](https://code.claude.com/docs/en/worktrees#clean-up-worktrees)). For a worktree that a sweep kept, it adds `--force` "if the worktree has uncommitted changes or untracked files" ([worktrees](https://code.claude.com/docs/en/worktrees#worktree-locks-and-manual-removal)). Cleanup in those runs falls to your script, so the script needs its own check.

Subagent worktrees follow a different rule. Claude Code removes one "automatically when the subagent finishes without changes", and a worktree with changes "stays on disk until the periodic sweep" can remove it "without losing work" ([worktrees](https://code.claude.com/docs/en/worktrees#isolate-subagents-with-worktrees)).

Suppose you add an allow rule for `ExitWorktree` so an unattended run can clean up. The entry says an allow rule lets the removal through. I read that as a rule for the whole tool, because the entry does not say you can limit a rule to clean worktrees (inference). Pair the rule with a check that runs first.

## Check before you remove

Git already refuses the unsafe case. `git worktree remove` removes only "clean worktrees (no untracked files and no modification in tracked files)", and it "refuses to remove an unclean worktree unless --force is used" ([git-worktree](https://git-scm.com/docs/git-worktree)). The rule for your script is to never pass `--force`.

Add a check so the script says why it stopped. `git status --porcelain` gives "an easy-to-parse format for scripts" that "will remain stable across Git versions" ([git-status](https://git-scm.com/docs/git-status)). By default `git status` shows untracked files, so empty output means nothing to report. The example below is mine, not Claude Code's check:

```sh
wt=../agent-task-1
base=origin/main

if [ -n "$(git -C "$wt" status --porcelain)" ]; then
  echo "unsaved changes in $wt, keeping it" >&2
  exit 1
fi

ahead=$(git -C "$wt" rev-list --count "$base"..HEAD)
if [ "$ahead" -gt 0 ]; then
  echo "$ahead commits in $wt not on $base, keeping it" >&2
  exit 1
fi

git worktree remove "$wt"
```

`git rev-list --count` prints "a number stating how many commits would have been listed" ([git-rev-list](https://git-scm.com/docs/git-rev-list)). Pick the base that matches where you push. A branch that is pushed but not merged still counts against `origin/main`, so the script keeps its worktree. That errs on the safe side.

`git status` lists ignored files only with `--ignored` ([git-status](https://git-scm.com/docs/git-status)). A local `.env` is usually ignored, and removal deletes the whole directory (inference from the worktrees page quote above). The changelog entry does not say whether Claude Code counts ignored files as unsaved work.

Since 2.1.323, the macOS and Linux sandbox makes "`git worktree add`, `move` and `remove` now fail read-only" ([changelog 2.1.323](https://code.claude.com/docs/en/changelog#2-1-323)). If your agent runs this script through its sandboxed Bash tool, run it from the orchestrator instead (inference). [Worktree isolation](../../workflows/worktree-isolation.md) has the setup.

## When this backfires

- The prompt trains people to approve. If agents exit worktrees often, a person answers the same question many times. [Ask-everything policies](../anti-patterns/ask-everything-permission-policies.md) describe that failure. Keep the question for removals that fail your own check.
- A broad allow rule or bypass mode removes the guard. The entry lists both as ways past the refusal. [Bypass permissions overriding an allowlist](../anti-patterns/bypass-permissions-overrides-allowlist.md) covers the wider risk.
- Refusals leave worktrees behind. I expect a refused removal to keep the directory and its branch (inference), so unattended runs pile up worktrees until a person clears them.
- The check misses unsaved work that git does not report as changes in the worktree, such as ignored files. The script above does not cover them.

## Key Takeaways

- `ExitWorktree` asks before removing a worktree that may hold unsaved work (2.1.327). In don't-ask mode, or with nobody to answer, the removal is refused.
- An allow rule, auto mode or bypass permissions mode lets it through, on my reading of the entry. It does not say whether auto mode still reviews the call.
- In `-p` runs Claude does not clean up worktrees, so your script owns removal. Check `git status --porcelain` and the commit count first, and never pass `--force`.
- Test the prompt on your version. The tools reference, as fetched on 2026-11-23, lists `ExitWorktree` with "No" in its "Permission required" column.

## Related

- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — what an unattended run does with a prompt nobody can answer
- [Allowing One Skill to Run in Scheduled Tasks and /loop](unattended-skill-allow-rule.md) — the same ask-then-allow-rule shape for skills
- [Worktree-Isolated Subagents and the Shared-Branch Guard](worktree-subagent-shared-branch-guard.md) — the 2.1.326 git refusal in isolated worktrees
- [Worktree Isolation](../../workflows/worktree-isolation.md) — creating and removing worktrees for parallel agents
- [Claude Code /batch and Worktrees](../../tools/claude/batch-worktrees.md) — the `EnterWorktree` and `ExitWorktree` tools
