---
title: "Claude Code Review"
description: "Anthropic's managed multi-agent review for GitHub pull requests: availability, triggers, REVIEW.md tuning, usage-based cost, and how findings relate to approvals."
tags:
  - workflows
  - code-review
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-26
status: current
---

# Claude Code Review

> Claude Code Review is a managed service that reviews GitHub pull requests with several agents and posts findings as inline comments.

## What it is

[Code Review](https://code.claude.com/docs/en/code-review) is a first-party service for GitHub repositories. It is [generally available](https://code.claude.com/docs/en/claude-ship#who-can-use-claude-ship) on [Team and Enterprise plans](https://code.claude.com/docs/en/code-review#availability). It is not available to organizations with Zero Data Retention or the HIPAA configuration, and not yet to those using customer-managed encryption keys.

An Owner of your Claude organization [turns it on](https://code.claude.com/docs/en/code-review-setup). Reviews run on Anthropic infrastructure, so you add no workflow files. [DIY subagent review](../../code-review/agent-assisted-code-review.md) leaves that wiring to you.

## How the review runs

Several agents [examine the diff and the surrounding code](https://code.claude.com/docs/en/code-review#how-reviews-work) in parallel. A verification step checks the candidate findings against the code and filters out false positives. The remaining findings are deduplicated and ranked by severity. The review posts inline comments, a summary, and a check run named Claude Code Review. It reads code without building or running it.

By default the focus is correctness: bugs that would break production, not formatting preferences or missing test coverage.

Findings carry [one of three severity levels](https://code.claude.com/docs/en/code-review-pull-requests#severity-levels):

| Marker | Level | Meaning |
|--------|-------|---------|
| 🔴 | Important | A bug that should be fixed before merging |
| 🟡 | Nit | A minor issue, worth fixing but not blocking |
| 🟣 | Pre-existing | A bug in the codebase that this PR did not introduce |

Code Review has [no flat per-review price](https://code.claude.com/docs/en/code-review-costs). It bills token usage through usage credits, separately from your plan's included usage. Cost scales with the review level, the size of the change, the complexity of the surrounding code, and the number of candidate issues to verify. The levels are Quick, Standard (the default), and Deep.

## Setup

A Claude organization Owner turns on Code Review in the Claude Ship settings and [chooses repositories](https://code.claude.com/docs/en/code-review-setup#turn-on-code-review). Installing the Claude GitHub App takes an owner of the GitHub organization. Each repository has a [Review runs setting](https://code.claude.com/docs/en/code-review-setup#set-when-reviews-run):

- Once after PR creation: a review when a pull request is opened, reopened, or marked ready for review
- After every push: reviews on pushes to the pull request branch. A repository added through the Add a repository dialog starts here, unless its GitHub organization is covered as a whole
- Manual: no review on open or push, so someone requests one with a comment

Automatic reviews skip drafts and pull requests from forks. After some pushes, Code Review [keeps the earlier result](https://code.claude.com/docs/en/code-review-pull-requests#when-a-push-keeps-the-earlier-result) instead of reviewing again. A later review resolves its own earlier thread when it [judges the issue fixed](https://code.claude.com/docs/en/code-review-pull-requests#respond-to-findings). A [Claude Approvals](https://code.claude.com/docs/en/approvals) policy file can start reviews that this setting would not, and stop automatic ones. The admin settings show each repository's [average cost per review](https://code.claude.com/docs/en/code-review-costs#estimate-your-spend).

## Customizing what gets flagged

Code Review reads [two kinds of file](https://code.claude.com/docs/en/code-review-customize):

- `CLAUDE.md`: project context, read from the repository root and the parent directories of each changed file. A violation becomes a finding at whichever severity level fits the issue.
- `REVIEW.md`: review-only instructions at the repository root. On a protected branch, you can also add one in most subdirectories.

Code Review reads `REVIEW.md` [from the base or default branch](https://code.claude.com/docs/en/code-review-customize#which-branch-review-md-is-read-from), never from the pull request's own changes. When it reads the root file from a protected default branch, it honors instructions there that lower severity, exclude findings, or cap nits.

The local [`/code-review`](https://code.claude.com/docs/en/code-review-local#what-the-review-reads-and-edits) command follows your `CLAUDE.md` but does not read `REVIEW.md`. Put guidance meant for both in `CLAUDE.md`.

## The @claude PR tagging pattern

With write access to the repository, you can steer reviews on an open pull request with [comment commands](https://code.claude.com/docs/en/code-review-pull-requests#comment-commands):

| Comment | Effect |
|---------|--------|
| `@claude review` or `@claude review once` | One review, with no subscription |
| `@claude review always` | A review, plus reviews on later pushes |
| `@claude review stop` | Ends that subscription |

Put the command at the start of a new top-level comment. In an After every push repository, a comment cannot stop reviews. On a pull request from a fork, `always` does not subscribe.

When you disagree with a kind of finding that keeps coming back, ask a maintainer to add a [`REVIEW.md` rule](https://code.claude.com/docs/en/code-review-pull-requests#respond-to-findings).

## What human review still handles

By itself, a review [doesn't approve or block the pull request](https://code.claude.com/docs/en/code-review), and its check run does not conclude as a failure. Its result counts toward approvals in a repository whose Claude Approvals policy file uses it. If branch protection requires conversation resolution, [resolve each finding's thread](https://code.claude.com/docs/en/code-review-pull-requests#respond-to-findings) before you merge.

To gate on findings yourself, [parse the severity counts](https://code.claude.com/docs/en/code-review-pull-requests#read-the-result-from-a-script) from the check run in your own CI.

The default focus is correctness, so give design decisions and architectural fit to a human reviewer. The service [can miss bugs and vulnerabilities](https://code.claude.com/docs/en/code-review), so keep your tests and scanners.

## Why it works

Finding and checking are separate steps, so a false positive has to get past [verification](https://code.claude.com/docs/en/code-review#how-reviews-work) to reach you. A [reproduce-before-report gate](../../code-review/reproduce-before-report-verification-gate.md) is the same split in a pipeline you build.

## When this backfires

- Push-heavy branches: After every push [multiplies cost by the number of pushes](https://code.claude.com/docs/en/code-review-costs#how-often-reviews-run). Use Once after PR creation or Manual for high-churn branches.
- Exhausted budget: Code Review [skips reviews](https://code.claude.com/docs/en/code-review-costs#limit-your-spend) when a spend limit or the usage credit balance runs out, and comments on the pull request.
- Ignored findings: you can [merge without responding](https://code.claude.com/docs/en/code-review-pull-requests#respond-to-findings) unless your repository rules require it.
- Other plans: without Team or Enterprise, run `/code-review` locally or build [DIY subagent review](../../code-review/agent-assisted-code-review.md).

## Example

The customization docs give [this `REVIEW.md`](https://code.claude.com/docs/en/code-review-customize#example-review-md) for a backend service. It redefines Important, caps nits, skips generated files, and adds repository checks. The severity, skip, and cap instructions depend on the protected default branch described above.

```markdown
# Review instructions

## What Important means here

Reserve Important for findings that would break behavior, leak data,
or block a rollback: incorrect logic, unscoped database queries, PII
in logs or error messages, and migrations that aren't backward
compatible. Style, naming, and refactoring suggestions are Nit at
most.

## Cap the nits

Report at most five Nits per review.

## Do not report

- Anything CI already enforces: lint, formatting, type errors
- Generated files under `src/gen/` and any `*.lock` file
- Test-only code that intentionally violates production rules

## Always check

- New API routes have an integration test
- Log lines don't include email addresses, user IDs, or request bodies
- Database queries are scoped to the caller's tenant
```

## Key Takeaways

- Check the repository's Review runs setting before assuming a pull request was reviewed; drafts and forks need a comment command
- Budget by repository average, because there is no flat price and review after every push multiplies it
- A rule written only in `REVIEW.md` is missing from your local `/code-review` runs; move it to `CLAUDE.md` if both need it
- A review alone neither approves nor blocks, so read your Claude Approvals policy and branch rules to know what its result changes
- With write access, use `@claude review` for one review and `@claude review always` to subscribe the pull request

## Related

- [Agent-Assisted Code Review](../../code-review/agent-assisted-code-review.md)
- [Claude Code Sub-Agents](sub-agents.md)
- [/code-review Default Scope](code-review-local-scope.md)
- [Claude Code Hooks](hooks-lifecycle.md)
- [Claude Code Extension Points](extension-points.md)
- [Memory and CLAUDE.md](https://code.claude.com/docs/en/memory)
