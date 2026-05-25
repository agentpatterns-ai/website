---
title: "Claude Code Review"
description: "Anthropic's managed multi-agent service that reviews every GitHub PR and posts inline findings — no subagent configuration required."
tags:
  - testing-verification
  - workflows
  - code-review
  - claude
---

# Claude Code Review

> A managed multi-agent review service that posts inline findings on every GitHub PR — no subagent configuration required.

## What It Is

[Code Review](https://code.claude.com/docs/en/code-review) is a first-party feature available on Teams and Enterprise plans. Once an admin enables it, reviews run automatically whenever a pull request opens or is updated. You write no orchestration code; Anthropic's infrastructure handles it.

Contrast with [DIY subagent review](../../code-review/agent-assisted-code-review.md): hand-rolling a review subagent requires defining the agent, configuring tool access, wiring CI, and maintaining it. Code Review is a managed service — the GitHub App is the only setup step.

## How the Review Runs

Per the [documentation](https://code.claude.com/docs/en/code-review), multiple specialized agents analyze the diff and surrounding codebase in parallel. Each focuses on a different issue class. A verification step checks flagged candidates against actual code behavior to filter false positives. Results are deduplicated, ranked by severity, and posted as inline comments. If no issues are found, Claude posts a confirmation comment.

Default focus is correctness: bugs that would break production, not formatting or missing test coverage (unless you add instructions for those).

Severity tags on findings:

| Marker | Level | Meaning |
|--------|-------|---------|
| 🔴 | Important | A bug that should be fixed before merging |
| 🟡 | Nit | A minor issue, not blocking |
| 🟣 | Pre-existing | A bug present in the codebase but not introduced by this PR |

Reviews [average 20 minutes and cost $15–25](https://code.claude.com/docs/en/code-review#pricing), scaling with PR size and codebase complexity.

## Setup

An admin installs the Claude GitHub App to the organization and selects which repositories to enable. Per repository, you choose a trigger:

- **After PR creation only** — one review per PR open or ready-for-review event
- **After every push to PR branch** — reviews on each commit; auto-resolves threads when the flagged code is fixed

The on-push trigger multiplies cost by push count. `claude.ai/admin-settings/claude-code` shows average cost per review per repository to make the trade-off visible.

## Customizing What Gets Flagged

Code Review reads two files from your repository root:

- **`CLAUDE.md`** — shared project instructions. Newly-introduced violations are flagged as nits. If a PR makes a `CLAUDE.md` statement outdated, Claude flags that too.
- **`REVIEW.md`** — review-only guidance for rules that would clutter `CLAUDE.md`.

`REVIEW.md` is auto-discovered at the repository root. Both files are additive on top of default correctness checks.

Example `REVIEW.md` content from the docs:

```markdown
## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible

## Skip
- Generated files under `src/gen/`
```

## The @claude PR Tagging Pattern

Comment `@claude review` on any open PR to trigger a review on demand. Use `@claude review once` for a single review without subscribing the PR to future pushes.

Recurring findings are a prompt to update `CLAUDE.md` or `REVIEW.md` — encoding the fix prevents the same issue class from appearing on future PRs.

## What Human Review Still Handles

Findings are non-binding: they never approve or block a PR and don't count toward required approvals. The agents focus on correctness — logic errors, security patterns, edge cases, regressions. Design decisions and architectural fit remain with human reviewers.

## Why It Works

Parallel specialization reduces cognitive load per agent. A single reviewer scanning a diff for security issues, logic correctness, edge cases, and regressions simultaneously must context-switch between incompatible mental models. Code Review assigns each issue class to a dedicated agent that builds context only for that domain. A verification step then cross-checks flagged candidates against actual code behavior before posting, filtering false positives without sacrificing recall.

## When This Backfires

- **Cost multiplies on push-heavy branches**: on-push trigger runs a full review per commit. A 15-push PR costs $225–375. Use `@claude review once` or "Once after PR creation" for high-churn branches.
- **False positives create noise**: verification filters many false positives but not all. Rate findings (👍/👎) to give Anthropic tuning signal; skipping ratings compounds noise over time.
- **Teams/Enterprise-only**: unavailable on free and Pro plans — use the [DIY subagent approach](../../code-review/agent-assisted-code-review.md) instead.
- **Advisory findings get dismissed**: non-binding, never blocking merges — teams under deadline pressure routinely ignore them.

## Key Takeaways

- Parallel specialized agents review every PR with no per-repository configuration beyond enabling it
- Default focus is correctness (bugs), not style — extend scope via `CLAUDE.md` or `REVIEW.md`
- Findings are advisory; they never block merges or substitute for required approvals
- On-push trigger auto-resolves threads when flagged code is fixed, at higher cost per PR
- `@claude review` triggers on-demand; `@claude review once` runs once without subscribing to future pushes

## Example

A team enables Code Review on a Python backend repository. The admin selects "After every push to PR branch" as the trigger. The repository contains:

**`CLAUDE.md`** (project-wide):

```markdown
- All public functions must have type annotations
- Use `logging` module, never `print()` for diagnostics
- SQL queries must use parameterized statements
```

**`REVIEW.md`** (review-specific):

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
