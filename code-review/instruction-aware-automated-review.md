---
title: "Instruction-Aware Automated Code Review"
description: "Wire AGENTS.md or REVIEW.md into the automated reviewer so its findings enforce documented team conventions: works only for rules the reviewer can mechanically verify."
term: "Instruction-Aware Code Review"
tags:
  - code-review
  - instructions
  - tool-agnostic
aliases:
  - AGENTS.md-aware review
  - convention-aware reviewer
  - instruction-file code review
last_reviewed: 2026-06-28
maturity: emerging
---

# Instruction-Aware Automated Code Review

> Feed the team's instruction file into the review agent so its findings enforce documented conventions the reviewer can mechanically verify.

Instruction-aware automated review wires a repository's instruction file — `AGENTS.md`, `CLAUDE.md`/`REVIEW.md`, or the equivalent — into the system prompt of the automated reviewer at PR time. The reviewer flags violations of documented conventions instead of a generic rubric. The pattern pays off only when conventions are mechanically checkable from a diff and the instruction file is short enough to stay attention-budget-positive.

## When to apply

The pattern is qualified: it works under specific conditions and backfires outside them. Apply when all three hold:

- The convention is reviewable from a diff. The rule can be checked by reading changed lines plus a small amount of surrounding context: "new API routes have an integration test", "log calls must use structured logging, not f-string interpolation", "database queries are scoped to the caller's tenant". Vague directives ("be careful", "be thoughtful about naming") cannot be enforced and dilute the rules that can ([GitHub Blog: Mastering Instructions Files](https://github.blog/ai-and-ml/github-copilot/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)).
- A deterministic linter cannot already cover it. Naming, formatting, and import order belong in `eslint`, `ruff`, `gofmt`, or a custom AST rule. Those give the same verdict every run for zero per-PR tokens. Reserve the reviewer for rules a linter cannot express: cross-file invariants, architectural patterns, severity recalibration.
- The instruction file stays short. GitHub documents that files "over ~1,000 lines can lead to inconsistent behavior" and that "very long instruction files may result in some instructions being overlooked" ([GitHub Blog: Mastering Instructions Files](https://github.blog/ai-and-ml/github-copilot/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)). Anthropic warns "length has a cost: a long `REVIEW.md` dilutes the rules that matter most" ([Claude Code Review docs](https://code.claude.com/docs/en/code-review)).

## How tools wire it up

The mechanism is the same across tools: the reviewer's system prompt is constructed at PR time, and the instruction file is injected into it. Only the file path differs.

| Tool | Files read at review time | Behavior |
|------|---------------------------|----------|
| GitHub Copilot code review | `AGENTS.md` at repo root; `.github/copilot-instructions.md`; `.github/instructions/*.instructions.md` | Reads `AGENTS.md` automatically; previously truncated instructions over 4000 characters, limit removed 2026-06-12 ([GitHub Changelog 2026-06-12](https://github.blog/changelog/2026-06-12-copilot-code-review-new-configurations-and-controls/)) |
| Claude Code Review (managed) | `CLAUDE.md` (all directory levels); `REVIEW.md` at repo root | `CLAUDE.md` violations surface as *nit*; `REVIEW.md` is "injected into the system prompt of every agent in the review pipeline as the highest-priority instruction block" ([Claude Code Review docs](https://code.claude.com/docs/en/code-review)) |
| Cursor Bugbot | Accumulated learned rules from accept/reject feedback | Reviewer-specific rules are stored per repo and prepended to context — see [learned review rules](learned-review-rules.md) |

GitHub's launch of `AGENTS.md` support for Copilot code review on 2026-06-18 is the trigger that made this pattern visible across tools: the reviewer "will read `AGENTS.md` from the root of your repository and use relevant instructions from that file when generating review feedback" ([GitHub Changelog 2026-06-18](https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements/)).

## Why it works

The mechanism is project-specific rubric injection: the review agent's system prompt is assembled before the diff arrives, and the instruction file becomes part of it. Anthropic documents this directly: `REVIEW.md` "is injected into the system prompt of every agent in the review pipeline as the highest-priority instruction block, taking precedence over the default review guidance" ([Claude Code Review docs](https://code.claude.com/docs/en/code-review)). The reviewer judges the diff against the team's documented rubric instead of a generic correctness baseline, which catches repo-specific rules the default reviewer would miss and suppresses false positives on intentional patterns the team has codified. The same injection mechanism applies to Copilot reading `AGENTS.md`.

The pattern composes with deterministic linters rather than replacing them: linters catch what they can deterministically, the instruction-aware reviewer handles the rest. It also composes with [learned review rules](learned-review-rules.md): Cursor's Bugbot accumulates accept/reject signals into a per-repo rule set that is similarly prepended to context, an empirically-grown variant of the same mechanism ([Cursor: Bugbot learned rules](https://cursor.com/blog/bugbot-learning)).

## Example

A backend service uses `REVIEW.md` to recalibrate severity for its risk profile, cap nit volume, skip generated files, and add three repo-specific checks. The reviewer applies these as the highest-priority instructions; the default rubric falls underneath ([Claude Code Review docs](https://code.claude.com/docs/en/code-review)).

```markdown
# Review instructions

## What Important means here

Reserve Important for findings that would break behavior, leak data,
or block a rollback: incorrect logic, unscoped database queries, PII
in logs or error messages, and migrations that aren't backward
compatible. Style, naming, and refactoring suggestions are Nit at
most.

## Cap the nits

Report at most five Nits per review. If you found more, say "plus N
similar items" in the summary instead of posting them inline.

## Do not report

- Anything CI already enforces: lint, formatting, type errors
- Generated files under `src/gen/` and any `*.lock` file
- Test-only code that intentionally violates production rules

## Always check

- New API routes have an integration test
- Log lines don't include email addresses, user IDs, or request bodies
- Database queries are scoped to the caller's tenant
```

The "Do not report" block points to CI as the enforcement surface for lint and formatting — exactly the rules the reviewer cannot mechanically verify as well as a deterministic linter. The "Always check" block lists repo-specific invariants the linter cannot express.

## When this backfires

- Conventions a deterministic linter already enforces. Routing naming, formatting, or import-order rules through the reviewer trades a free, deterministic gate for a per-PR token cost and a probabilistic verdict: the reviewer "may not follow every instruction perfectly every time" ([GitHub Blog: Mastering Instructions Files](https://github.blog/ai-and-ml/github-copilot/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)). The reviewer-as-enforcement-surface case only pays off for rules a linter cannot mechanically express.
- Vague directives. "Be thoughtful about naming", "be careful with errors", and similar additions add "noise that confuses the LLM" without giving the reviewer anything to check ([GitHub Blog: Mastering Instructions Files](https://github.blog/ai-and-ml/github-copilot/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files/)). Each one consumes attention budget for zero enforcement.
- Instruction file bloat past the dilution threshold. Files over ~1,000 lines produce "inconsistent behavior" per GitHub; a long instruction file "dilutes the rules that matter most" per Anthropic. Teams that drop their full style guide into `AGENTS.md` to "feed the reviewer" predictably make the reviewer worse. The top-priority rules now compete for attention with hundreds of mechanically-checkable ones that belong elsewhere.
- Single-file conflation of authoring and review surfaces. Anthropic ships two files (`CLAUDE.md` and `REVIEW.md`) precisely because authoring instructions and review instructions have different priorities. When a team treats `AGENTS.md` as the source of truth for both, an authoring rule change implicitly changes review behavior without explicit review-of-the-review. For tools that read only one file, partition the file into clearly-labeled authoring and review sections, or accept the drift risk.
- No PR gate or no automated reviewer enabled. The pattern requires an automated review step. In direct-commit workflows or repositories where the automated reviewer is disabled, the instruction file has no enforcement surface: the documented rules stay documented and unenforced. See [Deferred Standards Enforcement](deferred-standards-enforcement.md) for the related risk when the review step is missing.

## Key Takeaways

- The instruction file becomes the highest-priority block in the reviewer's system prompt, so an outdated or wrong rule in it produces confidently wrong verdicts. Keep `AGENTS.md`/`REVIEW.md` as accurate as any other reviewed artifact ([Claude Code Review docs](https://code.claude.com/docs/en/code-review)).
- Check which file your tool reads before adding rules. Copilot wants `AGENTS.md` at the repo root, Claude Code Review wants its own `REVIEW.md`, and Cursor Bugbot wants neither. It learns from accept/reject feedback instead.
- Apply only when the rule is reviewable from a diff, is not better served by a deterministic linter, and the instruction file fits inside the documented dilution thresholds (~1,000 lines per GitHub).
- Vague directives, mechanically-checkable rules, and bloated instruction files all degrade reviewer signal. Strip them out before adding more.
- Anthropic's `CLAUDE.md`/`REVIEW.md` split shows why authoring and review surfaces benefit from separation; single-file tools require an explicit internal partition to avoid silent drift.

## Related

- [Deferred Standards Enforcement via Review Agents](deferred-standards-enforcement.md) — the complementary split: which standards live in `CLAUDE.md` vs `REVIEW.md`
- [Learned Review Rules](learned-review-rules.md) — accumulated accept/reject rules as an empirically-grown variant of the same injection mechanism
- [Review-Feedback-to-Rule Loop](review-feedback-to-rule-loop.md) — promoting recurring comments into deterministic checks, when the linter route is correct
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the reason cap-the-nits and skip rules matter at all
- [Standards as Agent Instructions](../instructions/standards-as-agent-instructions.md) — the authoring-side counterpart
- [AGENTS.md as a Table of Contents, Not an Encyclopedia](../instructions/agents-md-as-table-of-contents.md) — the length discipline that keeps instruction-aware review working
