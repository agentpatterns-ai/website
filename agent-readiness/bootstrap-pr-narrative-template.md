---
title: "Bootstrap PR Narrative Template"
description: "Generate issue, PR, and commit message templates that scaffold the visible-thinking discipline the audit checks for — Why/What/Trade-offs PR sections, structured commit trailers, issue-as-spec scaffold — and wire them through CLAUDE.md/AGENTS.md so agents pick them up by default."
tags:
  - tool-agnostic
  - workflows
  - code-review
  - instructions
aliases:
  - PR template scaffold
  - visible thinking scaffold
  - issue and PR template bootstrap
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-pr-narrative-template/`

# Bootstrap PR Narrative Template

> Scaffold the templates that drive the merge-rate gains the audit measures — issue spec format, Why/What/Trade-offs PR body, structured commit trailers — and wire them so agents emit them by default.

!!! info "Harness assumption"
    Templates land in GitHub-recognized paths (`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `.gitmessage`) and pointer rules in `CLAUDE.md`/`AGENTS.md` so the agent picks them up at session start. Translate paths for GitLab (`.gitlab/issue_templates/`, `.gitlab/merge_request_templates/`), Bitbucket, and other forges. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Run when the project receives agent-authored PRs at any cadence. Skip on solo or inner-source repos with no external reviewers, on squash-merge-only repos where per-commit narration collapses (template still helps the PR body, but the commit-trailer step is no-op), and on trivial-PR-dominated repos (dependency bumps, formatting) where templates add friction without proportional value — see [`pr-description-style-lever`](../code-review/pr-description-style-lever.md) §When This Backfires.

PR description structure varies systematically by agent and correlates with merge rate at p<0.001 ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), via [`pr-description-style-lever`](../code-review/pr-description-style-lever.md)). [`audit-pr-narrative-quality`](audit-pr-narrative-quality.md) detects when the discipline is missing; this runbook installs the scaffolds that produce it. Rules from [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md), [`pr-description-style-lever`](../code-review/pr-description-style-lever.md), and [`agent-commit-attribution`](../workflows/agent-commit-attribution.md).

## Step 1 — Detect Existing Templates

```bash
# Forge templates already shipped
ls -la .github/ISSUE_TEMPLATE/ 2>/dev/null
ls -la .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md 2>/dev/null
ls -la .gitlab/issue_templates/ .gitlab/merge_request_templates/ 2>/dev/null

# Existing commit message template
git config --get commit.template
ls -la .gitmessage 2>/dev/null

# PR-narrative pointer in agent instructions
grep -lE 'Pull Request|PR Convention|## PR|PR Description' CLAUDE.md AGENTS.md .github/copilot-instructions.md 2>/dev/null
```

Decision rules:

- **All four artifacts present and reference the Why/What/Trade-offs structure** → run [`audit-pr-narrative-quality`](audit-pr-narrative-quality.md) instead; this runbook has nothing to add
- **Templates exist but use a different structure** (e.g., a generic checklist) → ask before overwriting; offer to layer the narrative sections in
- **Greenfield (no templates)** → proceed with all six steps below
- **Squash-merge-only repo** → skip Step 4 (commit template) and add a note in the PR template that absorbs commit-level rationale

## Step 2 — Generate the Issue Specification Template

Create `.github/ISSUE_TEMPLATE/feature.yml` so agents see the same scaffold humans do when an issue is opened:

```yaml
name: Feature or change request
description: Spec for an agent-implementable change
title: "[FEAT] "
labels: ["needs-triage"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem
      description: What is the user-visible or system-level issue this change addresses? One paragraph.
    validations: { required: true }
  - type: textarea
    id: success-criteria
    attributes:
      label: Success criteria
      description: How will the change be verified? Tests, metrics, manual steps. List each criterion as a bullet.
    validations: { required: true }
  - type: textarea
    id: constraints
    attributes:
      label: Constraints
      description: Hard boundaries the implementation must respect — files off-limits, APIs to preserve, performance ceilings, security requirements.
    validations: { required: true }
  - type: textarea
    id: risks
    attributes:
      label: Risks and unknowns
      description: What could break? Data migrations, breaking-change surface, areas the agent should escalate rather than guess.
```

A bug-report template (`.github/ISSUE_TEMPLATE/bug.yml`) follows the same shape with `Reproduction` and `Expected vs actual` substituted for `Success criteria` and `Constraints`. Both templates make the issue itself the reviewable record of intent ([`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Issues as Specifications).

## Step 3 — Generate the PR Description Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Why
<!-- The problem or opportunity that motivated the change. Link the issue. -->

## What changed
<!-- Concrete description of the implementation: files, modules, key decisions. -->

## Trade-offs
<!-- Alternatives considered. Reasons for the chosen path. State "None considered" only if true. -->

## Verification
<!-- Tests run. Manual steps. Screenshots if UI. Output of relevant CI checks. -->

## Breaking changes
<!-- "None" or explicit list with migration notes. -->

## Agent attribution
<!-- If an agent authored this PR: model, session reference, originating issue. -->
```

The four mandatory sections (Why, What changed, Trade-offs, Verification) are the structure correlated with merge-rate gains ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), via [`pr-description-style-lever`](../code-review/pr-description-style-lever.md)). The Agent attribution section pairs with Step 4 — see [`agent-commit-attribution`](../workflows/agent-commit-attribution.md).

## Step 4 — Generate the Commit Message Template

Create `.gitmessage` at the repo root:

```
<type>(<scope>): <one-sentence summary>

# Why this change (the decision, not the diff)

# Trade-offs and alternatives considered

# Agent trailers — uncomment and fill if an agent authored this commit
# Co-authored-by: <agent-bot> <noreply@example.com>
# Agent-Session: <session-id>
# Model: <model-id>
# Task-Reference: #<issue-number>
```

Wire it as the default for the project:

```bash
git config commit.template .gitmessage
```

Document the trailers in `AGENTS.md` so they survive across machines and agents. Skip this step on squash-merge-only repos — per-commit narration collapses into the PR body on merge, making the template noise ([`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §When This Backfires).

## Step 5 — Wire Pointer into Agent Instructions

Add a `## PR Conventions` section to `AGENTS.md` (and re-export through `CLAUDE.md` via `@AGENTS.md`) so the agent picks up the templates at session start:

```markdown
## PR Conventions

- Issue spec: open from `.github/ISSUE_TEMPLATE/feature.yml`. The four fields (Problem, Success criteria, Constraints, Risks) are the reviewable record of intent — fill them before delegating implementation.
- PR body: follow `.github/PULL_REQUEST_TEMPLATE.md` — Why, What changed, Trade-offs, Verification, Breaking changes are required. Do not delete a section; mark "None" if not applicable.
- Commit messages: follow `.gitmessage`. Narrate the decision, not the diff. Add `Agent-Session`, `Model`, and `Task-Reference` trailers on every commit you author.
- Branch names: `<type>/<scope>-<short-slug>` — never generic names like `agent-fix-1` (loses signal per [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Branch Naming).
```

This is the load-bearing wire-up: forge templates without an agent-instruction pointer let the agent default to model-baked PR style, which varies sharply across agents ([`pr-description-style-lever`](../code-review/pr-description-style-lever.md) §Structural Differences).

## Step 6 — Smoke Test

Verify the templates fire:

```bash
# Issue template surfaces in `gh issue create --web`
gh issue create --template feature.yml --title "smoke" --body "test" --dry-run 2>&1 | head -5

# PR template populates the body
gh pr create --draft --title "smoke" --body-file .github/PULL_REQUEST_TEMPLATE.md --dry-run 2>&1 | head -5

# Commit template loads
git commit --allow-empty --no-edit 2>&1 | head -5  # opens editor with template

# Agent picks up the pointer
grep -A1 "PR Conventions" AGENTS.md
```

If the agent-instruction grep returns no match, Step 5 did not land — fix before declaring done.

## Idempotency

Re-running detects existing templates in Step 1 and skips generation. If a template exists with a different structure, surface the diff to the user and ask before merging. The `git config commit.template` setting is idempotent — re-setting to the same path is a no-op.

## Output Schema

```markdown
# Bootstrap PR Narrative Template — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | .github/ISSUE_TEMPLATE/feature.yml | 4-field spec |
| Created | .github/ISSUE_TEMPLATE/bug.yml | reproduction-first |
| Created | .github/PULL_REQUEST_TEMPLATE.md | Why / What / Trade-offs / Verification / Breaking / Attribution |
| Created | .gitmessage | trailer block included |
| Modified | AGENTS.md | added PR Conventions section |
| Modified | .git/config | commit.template = .gitmessage |

Smoke test: <pass/fail>
Squash-merge-only repo: <yes/no — Step 4 skipped if yes>
```

## Related

- Paired audit: [Audit PR Narrative Quality](audit-pr-narrative-quality.md)
- [Visible Thinking in AI-Assisted Development](../observability/visible-thinking-ai-development.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](../code-review/pr-description-style-lever.md)
- [Agent Commit Attribution](../workflows/agent-commit-attribution.md)
- [Bootstrap Agent Commit Attribution](bootstrap-agent-commit-attribution.md)
- [Bootstrap Human Review Gate (PR)](bootstrap-human-review-gate-pr.md)
