---
title: "Claude Code Review"
description: "Anthropic's managed multi-agent service that reviews every GitHub PR and posts inline findings — no subagent configuration required."
tags:
  - testing-verification
  - workflows
  - code-review
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-13
status: current
---

# Claude Code Review

> A managed multi-agent review service that posts inline findings on every GitHub PR — no subagent configuration required.

## What it is

[Code Review](https://code.claude.com/docs/en/code-review) is a first-party feature, available as a research preview on Team and Enterprise plans (not on organizations with Zero Data Retention enabled). Once an admin enables it, reviews run automatically whenever a pull request opens or updates. You write no orchestration code; Anthropic's infrastructure handles it.

Contrast this with [DIY subagent review](../../code-review/agent-assisted-code-review.md): hand-rolling a review subagent means you define the agent, configure tool access, wire up CI, and maintain it. Code Review is a managed service, so installing the GitHub App is the only setup step.

## How the review runs

Per the [Code Review documentation](https://code.claude.com/docs/en/code-review), multiple specialized agents analyze the diff and surrounding codebase in parallel. Each agent focuses on a different issue class. A verification step then checks flagged candidates against actual code behavior to filter false positives. Claude deduplicates the results, ranks them by severity, and posts them as inline comments. If it finds no issues, it posts a confirmation comment.

Default focus is correctness: bugs that would break production, not formatting or missing test coverage (unless you add instructions for those).

Severity tags on findings:

| Marker | Level | Meaning |
|--------|-------|---------|
| 🔴 | Important | A bug that should be fixed before merging |
| 🟡 | Nit | A minor issue, not blocking |
| 🟣 | Pre-existing | A bug present in the codebase but not introduced by this PR |

Reviews [average 20 minutes and cost $15–25](https://code.claude.com/docs/en/code-review#pricing), and scale with PR size and codebase complexity.

## Setup

An admin installs the Claude GitHub App to the organization and selects which repositories to enable. Per repository, you choose a trigger:

- Once after PR creation: one review per PR open or ready-for-review event
- After every push: a review on each commit, which auto-resolves threads when the flagged code is fixed
- Manual: no automatic reviews; a review starts only when someone comments `@claude review` or `@claude review once` on the PR

The on-push trigger multiplies cost by push count. To make the trade-off visible, `claude.ai/admin-settings/claude-code` shows average cost per review per repository.

## Customizing what gets flagged

Code Review reads two files from your repository root:

- `CLAUDE.md`: shared project instructions. Claude flags newly-introduced violations as nits. If a PR makes a `CLAUDE.md` statement outdated, Claude flags that too.
- `REVIEW.md`: review-only guidance for rules that would clutter `CLAUDE.md`.

Code Review auto-discovers `REVIEW.md` at the repository root. Both files add to the default correctness checks.

Example `REVIEW.md` content from the docs:

```markdown
## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible

## Skip
- Generated files under `src/gen/`
```

## The @claude PR tagging pattern

Comment `@claude review` on any open PR to trigger a review on demand. Use `@claude review once` for a single review without subscribing the PR to future pushes.

Recurring findings are a prompt to update `CLAUDE.md` or `REVIEW.md`. Encoding the fix stops the same issue class from appearing on future PRs.

## What human review still handles

Findings are non-binding: they never approve or block a PR, and they do not count toward required approvals. The agents focus on correctness: logic errors, security patterns, edge cases, and regressions. Design decisions and architectural fit stay with human reviewers.

## Why it works

Parallel specialization reduces the work each agent does. A single reviewer scanning a diff for security issues, logic correctness, edge cases, and regressions at once must context-switch between incompatible mental models. Code Review automates the per-domain split that [DIY subagent review](../../code-review/agent-assisted-code-review.md) builds by hand: it assigns each issue class to a dedicated agent that builds context only for that domain. A verification step then cross-checks flagged candidates against actual code behavior before posting, which filters false positives without sacrificing recall.

## When this backfires

- Cost multiplies on push-heavy branches: the on-push trigger runs a full review per commit. A 15-push PR costs $225–375. Use `@claude review once` or "Once after PR creation" for high-churn branches.
- False positives create noise: verification filters many false positives but not all. Rate findings (👍/👎) to give Anthropic a tuning signal; skipping ratings compounds noise over time.
- Teams and Enterprise only: the feature is unavailable on free and Pro plans, so use the [DIY subagent approach](../../code-review/agent-assisted-code-review.md) instead.
- Advisory findings get dismissed: findings are non-binding and never block merges, so teams under deadline pressure routinely ignore them.

## Key Takeaways

- Parallel specialized agents review every PR with no per-repository configuration beyond enabling it
- Default focus is correctness (bugs), not style — extend scope via `CLAUDE.md` or `REVIEW.md`
- Findings are advisory; they never block merges or substitute for required approvals
- On-push trigger auto-resolves threads when flagged code is fixed, at higher cost per PR
- `@claude review` triggers on-demand; `@claude review once` runs once without subscribing to future pushes

## Example

A team enables Code Review on a Python backend repository. The admin selects "After every push to PR branch" as the trigger. The repository contains:

`CLAUDE.md` (project-wide):

```markdown
- All public functions must have type annotations
- Use `logging` module, never `print()` for diagnostics
- SQL queries must use parameterized statements
```

`REVIEW.md` (review-specific):

```markdown
## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible
- No raw SQL — use the ORM query builder

## Skip
- Generated files under `src/gen/`
- Vendored dependencies under `third_party/`
```

A developer opens a PR adding a new `/users/export` endpoint. Code Review posts three inline findings:

1. A parameterized SQL query that concatenates user input into the `ORDER BY` clause — flagged as a bug
2. The new endpoint has no integration test — flagged as a nit (per `REVIEW.md`)
3. A `print("debug")` statement left in the handler — flagged as a nit (per `CLAUDE.md`)

The developer fixes all three and pushes. Code Review re-runs and auto-resolves the three threads. A human reviewer then focuses on whether the export format and pagination strategy fit the product requirements.

## Related

- [Agent-Assisted Code Review](../../code-review/agent-assisted-code-review.md)
- [Claude Code Sub-Agents](sub-agents.md)
- [Claude Code Hooks](hooks-lifecycle.md)
- [Claude Code Extension Points](extension-points.md)
- [Memory and CLAUDE.md](https://code.claude.com/docs/en/memory)
