---
title: "Claude Code for Automated and Assisted Code Review"
description: "A managed multi-agent review service that posts inline findings on every GitHub PR — no subagent configuration required. Code Review is a first-party feature"
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

The contrast with [DIY subagent review](../../code-review/agent-assisted-code-review.md) is architectural: a hand-rolled review subagent requires defining the agent, configuring tool access, wiring it into CI, and maintaining it. Code Review is a managed service — the GitHub App integration is the only setup step.

## How the Review Runs

Per the [documentation](https://code.claude.com/docs/en/code-review), multiple specialized agents analyze the diff and surrounding codebase in parallel. Each agent focuses on a different class of issue. A verification step then checks flagged candidates against actual code behavior to filter false positives. Results are deduplicated, ranked by severity, and posted as inline comments on the specific lines where issues were found. If no issues are found, Claude posts a short confirmation comment.

The default focus is correctness: bugs that would break production. Code Review does not flag formatting preferences or missing test coverage unless you instruct it to.

Severity tags on findings:

| Marker | Level | Meaning |
|--------|-------|---------|
| 🔴 | Normal | A bug that should be fixed before merging |
| 🟡 | Nit | A minor issue, not blocking |
| 🟣 | Pre-existing | A bug present in the codebase but not introduced by this PR |

Reviews average 20 minutes and cost $15–25, scaling with PR size and codebase complexity [unverified].

## Setup

An admin installs the Claude GitHub App to the organization and selects which repositories to enable. Per repository, you choose a trigger:

- **After PR creation only** — one review per PR open or ready-for-review event
- **After every push to PR branch** — reviews on each commit; auto-resolves threads when the flagged code is fixed

The on-push trigger provides continuous feedback and automatic thread cleanup, but multiplies cost by the number of pushes. The admin settings table at `claude.ai/admin-settings/claude-code` shows average cost per review per repository, which makes the trade-off visible before you commit to a trigger mode.

## Customizing What Gets Flagged

Code Review reads two files from your repository root:

- **`CLAUDE.md`** — shared project instructions used across all Claude Code tasks. Code Review treats newly-introduced violations of `CLAUDE.md` rules as nit-level findings. If a PR makes a `CLAUDE.md` statement outdated, Claude flags that too.
- **`REVIEW.md`** — review-only guidance. Use this for rules that are strictly about what to flag or skip during review and would clutter your general `CLAUDE.md`.

`REVIEW.md` is auto-discovered at the repository root with no additional configuration. Both files are additive on top of the default correctness checks.

Example `REVIEW.md` content from the docs:

```markdown
## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible

## Skip
- Generated files under `src/gen/`
```

## The @claude PR Tagging Pattern

A secondary pattern: tagging `@claude` on a teammate's PR to propose `CLAUDE.md` updates [unverified]. When a review surfaces a recurring issue — a naming convention that's not yet documented, an architectural decision that should be codified — a `@claude` mention can draft the corresponding `CLAUDE.md` change as part of the same review thread.

This turns review findings into norm refinement: issues caught in review become permanent constraints preventing recurrence.

## What Human Review Still Handles

Code Review findings are non-binding: they never approve or block a PR, and do not count toward required approval counts. Existing review workflows stay intact.

The agents focus on correctness — logic errors, security patterns, edge cases, regressions. Design decisions, architectural fit, and product trade-offs remain with human reviewers.

## Key Takeaways

- Code Review runs a fleet of parallel specialized agents on every PR with no per-repository configuration beyond enabling it
- Default focus is correctness (bugs), not style — extend scope via `CLAUDE.md` or `REVIEW.md`
- Findings are severity-tagged and advisory; they never block merges or substitute for required approvals
- The on-push trigger provides automatic thread resolution when flagged code is fixed, at higher cost
- Tagging `@claude` on PRs to propose `CLAUDE.md` updates turns review findings into shared norm refinement

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

## Unverified Claims

- Reviews average 20 minutes and cost $15–25, scaling with PR size and codebase complexity [unverified]
- Tagging `@claude` on a teammate's PR to propose `CLAUDE.md` updates [unverified]

## Related

- [Agent-Assisted Code Review](../../code-review/agent-assisted-code-review.md)
- [Claude Code Sub-Agents](sub-agents.md)
- [Claude Code Hooks](hooks-lifecycle.md)
- [Claude Code Extension Points](extension-points.md)
- [Memory and CLAUDE.md](https://code.claude.com/docs/en/memory)
