---
title: "Claude Code /code-review: What It Reviews With No Target"
description: "Claude Code 2.1.329 reviews the whole branch on most models when /code-review has no target; the local-review page words the default differently."
tags:
  - claude
  - code-review
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-21
status: current
---

# Claude Code /code-review: What It Reviews With No Target

> Per the 2.1.329 changelog, `/code-review` with no target reviews the whole branch on most models; the local-review page words it differently.

Claude Code 2.1.329 (November 19, 2026) changed `/code-review` with no target "on most models to review the whole branch against the default branch, and fixed it losing the diff on multi-commit branches" ([Claude Code changelog, 2.1.329](https://code.claude.com/docs/en/changelog#2-1-329)). The same release made a review of a pull request URL, or of a PR number with `--fix`, stop when `gh pr diff` is refused or fails. The local-review page words the no-target default differently, so check your version and pass a target when the scope matters.

## What 2.1.329 changed

Three of the changelog entries that touch `/code-review` in this release change what it reviews or when it stops ([changelog, 2.1.329](https://code.claude.com/docs/en/changelog#2-1-329)):

| Change | Verbatim entry | Holds when |
|---|---|---|
| Default scope | "Changed `/code-review` with no target on most models to review the whole branch against the default branch, and fixed it losing the diff on multi-commit branches" | No target is typed, and the model is one of "most models" (the entry does not list them) |
| PR failure | "Changed `/code-review <pr number> --fix`, and `/code-review` given a pull request URL, to stop without reviewing when `gh pr diff` is refused or fails" | The target is a PR number with `--fix`, or a PR URL |
| PR number | "Fixed `/code-review <pr number>` sometimes reviewing the checked-out branch instead of the pull request without saying so: it now reads the pull request with `gh pr diff`, or says when it can't" | The target is a PR number |

## What the local-review page says

The [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local) page, read on November 21, 2026, states the no-target default this way: "With no target, `/code-review` reviews your branch's commits ahead of its upstream branch plus your uncommitted changes. If the branch has no upstream, Claude compares against `main`, or against the previous commit."

That sentence names an upstream branch as the base. The changelog names the default branch. The page's sentence carries no model condition, and neither source says which models count as "most models". Treat the two as unreconciled until the page changes or you test your own setup.

The page does state the scope of `/code-review ultra`, the cloud review: "your current branch against the repository's default branch, plus uncommitted and staged changes in the working tree". Passing a branch name, such as `/code-review ultra develop`, compares against that base instead.

## Choosing a target

Text typed after the effort level and flags reaches Claude "as the review target" ([local-review page](https://code.claude.com/docs/en/code-review-local)). The page lists these forms:

| To review | Type |
|---|---|
| Your current branch and uncommitted changes | `/code-review` |
| Your last 15 commits | `/code-review HEAD~15..HEAD` |
| One branch against another | `/code-review main...my-feature` |
| A single commit | `/code-review abc1234^..abc1234` |
| A pull request by number | `/code-review 1234` |
| A file or directory path | `/code-review src/auth` |

Pass a range or a branch pair when you want a fixed base, whatever the default does on your version. Pass a PR number or URL to review a pull request that is not checked out.

## When this backfires

- The base differs from the one you assumed. A whole-branch review includes every commit on the branch, including ones you reviewed earlier. Use a range such as `HEAD~15..HEAD` to review only recent work.
- Your version or model falls outside the change. The entry says "most models" and lists none, and it does not say what scope other models review.
- A PR review stops. With `--fix` or a PR URL, a refused or failed `gh pr diff` ends the run with no review. A run that stopped is not a clean review, as [Failed Reviewer Is Not a Clean Pass](../../patterns/multi-agent/failed-reviewer-not-clean-pass.md) describes for fan-out reviewers.
- The two sources disagree. If you document your team's workflow from the local-review page alone, it may describe the upstream base while your version uses the default branch.

## Key Takeaways

- The 2.1.329 changelog sets the no-target default to the whole branch against the default branch, on "most models" it does not list.
- The local-review page names the upstream branch as the base, so the two sources differ. Pass an explicit target when the base matters.
- A PR URL, or a PR number with `--fix`, stops without a review when `gh pr diff` is refused or fails. Treat a stopped run as not reviewed.
- Range and branch-pair targets such as `HEAD~15..HEAD` and `main...my-feature` fix the base.

## Related

- [Claude Code Review](code-review.md) — the managed GitHub service, a separate feature from the local command
- [Tunable Effort Levels for Code Review Agents](../../code-review/tunable-review-effort.md) — the effort levels a review runs at
- [Review-Then-Implement Loop for AI Agent Development](../../code-review/review-then-implement-loop.md) — what `/code-review --fix` applies after the review
- [Diff-Based Review Over Output Review](../../code-review/diff-based-review.md) — review what changed, not the full output
- [Failed Reviewer Is Not a Clean Pass](../../patterns/multi-agent/failed-reviewer-not-clean-pass.md) — record a reviewer that did not run as not run
