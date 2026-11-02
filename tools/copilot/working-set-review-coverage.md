---
title: "Copilot Working Set Review Misses Terminal File Edits"
description: "VS Code's Copilot working set excludes terminal edits. Reconcile Keep and Undo decisions with Git changes before you approve agent work."
tags:
  - copilot
  - code-review
  - testing-verification
term: "Copilot Working Set Review Coverage"
applies_to: "vscode@1.144"
last_reviewed: 2026-10-31
status: current
---

# Copilot Working Set Review Misses Terminal File Edits

> Copilot's VS Code working set excludes terminal edits, so Keep and Undo review needs a separate check against repository changes.

The working set records Copilot edits made through agent tools. VS Code 1.144 explicitly excludes changes made through terminal commands. Reviewers therefore need another source of changed files before approving the result ([VS Code 1.144 release notes](https://code.visualstudio.com/updates/v1_144#_review-copilot-file-edits-with-the-working-set-experimental)).

## Coverage of per-edit decisions

Inline Keep and Undo controls act on individual changes. The working set also supports file-level and bulk decisions. Controls are experimental and enabled by default in the editor. Set `chat.editor.workingSet.enabled` to `false` for the Changes pill. In the Agents window, use the Changes view to discard files ([VS Code 1.144 release notes](https://code.visualstudio.com/updates/v1_144#_review-copilot-file-edits-with-the-working-set-experimental)).

Do not infer that an empty working set means the repository is unchanged. The documented terminal exclusion makes that conclusion unsafe. This is a coverage check to add to [diff-based review](../../code-review/diff-based-review.md), before you assess whether the code is correct.

## Reconcile the review with Git

Use this procedure in the session's actual checkout. Record existing changes before the task so you can distinguish your edits from the agent's work.

1. Pause the agent. Run the commands below at the repository root while edits are stopped.
2. Compare Git's changed paths and hunks with the working set. Inspect missing edits even when the file appears in both.
3. Make Keep or Undo decisions for recorded edits. Inspect each untracked file before deciding whether to include it.
4. Run the commands again after those decisions. Review the final state and run the project's checks before approval.

```bash
git status --short --untracked-files=all
git diff
git diff --cached
```

`git diff` shows unstaged tracked changes; `git diff --cached` shows staged changes. Read both so staging does not hide part of your review ([Git diff documentation](https://git-scm.com/docs/git-diff)). The status command lists individual untracked files, but normally excludes ignored files. Inspect new file contents separately, and check ignored outputs when they matter to the task ([Git status documentation](https://git-scm.com/docs/git-status)).

If the agent commits during the task, also compare against the commit recorded before it started. Git supports comparing a working tree against a named commit and comparing two commits. An empty local diff after a commit does not cover the committed change ([Git diff documentation](https://git-scm.com/docs/git-diff)).

Budget for another pass. Keep it scoped to files and changes that the working set did not cover. Use [incremental verification](../../verification/incremental-verification.md) for behavior checks after the file review.

## Key Takeaways

- Treat the working set as a partial record of edits.
- Review staged changes and untracked files alongside unstaged changes.
- Check the final repository state after Keep or Undo decisions.
- Include committed changes when the agent commits during the task.

## Related

- [Verifying Agent Changes in the Copilot App](copilot-app-diff-terminal-browser.md) — the separate app's diff, terminal, and browser panels
- [Diff-Based Review Over Output Review](../../code-review/diff-based-review.md) — scope review to changes against a known state
- [Incremental Verification](../../verification/incremental-verification.md) — check behavior at intermediate steps
