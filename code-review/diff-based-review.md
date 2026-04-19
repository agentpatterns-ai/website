---
title: "Diff-Based Review: Focus on Changes, Not Complete Outputs"
description: "Review what changed, not the full output — diff-based review focuses on what is new, compresses effort, and supports staged pipelines at PR boundaries."
tags:
  - testing-verification
  - tool-agnostic
  - code-review
---

# Diff-Based Review Over Output Review

> Review what changed, not the full output — mistakes live in the delta, and diffs compress review effort to the right scope.

## Why Diffs Are Easier to Review Than Complete Outputs

Reading a 500-word page and spotting one wrong claim is hard. Reading a 20-line diff and spotting it is easy. Review effort scales with what you read; error density is highest in what is new.

Design agent workflows so review happens at diff boundaries — pull requests, staged changes, comment threads — not on complete artifacts.

## The PR Model as Review Boundary

[GitHub Copilot's coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) produces output as pull requests. This is not incidental — PRs are the natural diff boundary for code review. The same structure applies to [content pipelines](../workflows/content-pipeline.md):

- Draft pages open as PRs against main
- Review agents comment on the PR diff, not on the full page
- Human approval gates on the merge diff, not on re-reading the artifact

The PR model enforces that review happens on changes, not on totals.

## Checkpoints and Known-Good States

[Claude Code's checkpointing](https://code.claude.com/docs/en/checkpointing) captures file state before each prompt. When agent work goes wrong, restore to a prior checkpoint, then use `git diff` against the working tree. The documented rewind options are "restore code", "restore conversation", or both — there is no built-in side-by-side diff view, and the docs note that checkpoints "complement but don't replace proper version control". Pair them with git to get reviewable diffs.

Structuring work around checkpoints keeps the diff scope predictable:

- One logical unit of work → one checkpoint interval → one `git diff` to review
- Multiple checkpoint intervals → multiple restore points → easier to bisect failures

## Review Fatigue and Output Size

Review fatigue grows with output size. An agent producing 2,000 lines across ten files gets reviewed less carefully than one producing 20 lines in a single file.

Designing for diff-based review means:

- Breaking agent work into small, independently reviewable units
- Committing checkpoints between logical stages
- Opening separate PRs for separate concerns rather than one large PR

The SmartBear/Cisco study of 2,500 reviews found defect detection peaks at 200–400 lines and drops off beyond that, with reviewers faster than 450 lines per hour below average in 87% of cases ([SmartBear, "Code Review at Cisco Systems"](https://static0.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf)).

## Staged Review

Multi-stage pipelines have multiple natural diff boundaries:

1. **Research stage** — diff the research notes against the issue description. Verify the researcher captured the right sources.
2. **Draft stage** — diff the draft against the research notes. Verify the writer only used sourced material.
3. **Revision stage** — diff the revised draft against the original draft. Verify reviewer feedback was applied correctly.

Each diff is small and reviewable in isolation. Reviewing a 10-line diff against a known state is far easier than reviewing the final artifact against nothing.

## When This Backfires

Diff-only review has blind spots. Graphite notes that diff-only reviewers "may miss violations of global invariants, API misuse, or architectural consistency problems", and that larger context is needed to catch cross-file issues like "a change in one module that breaks usage elsewhere" ([Graphite, "How much context do AI code reviews need?"](https://graphite.com/guides/ai-code-review-context-full-repo-vs-diff)). Pair diff-based review with codebase-aware checks when:

- **Cross-file invariants are at stake.** A one-line schema change looks trivial but can silently break downstream consumers — run a repo-wide search, type check, or contract test alongside the diff.
- **The PR spans many files from one AI session.** Reviewers who read only the diff must reassemble intent from disconnected fragments; require a clear PR description or split the change before reviewing.
- **The change touches architectural seams.** Refactors, interface migrations, and dependency upgrades change behavior that is not visible in the diff — supplement with full-file review of the seam and integration tests.

## Anti-Patterns

**Full output review** — asking a reviewer to read the complete artifact rather than the diff. The reviewer re-reads everything the previous stage already validated.

**Single large PR** — bundling an entire agent session's work into one PR. The diff is large, contains multiple concerns, and is harder to bisect when something is wrong.

**No checkpoints** — relying on human review as the only diff boundary. Without intermediate checkpoints, the first reviewable diff is the complete output.

## Example

The following shows a three-stage content pipeline where each handoff produces a small, reviewable diff rather than a full-artifact review.

After the research stage, the reviewer checks only what the researcher added:

```bash
# Compare research notes against the original issue
git diff main...research/issue-84-oauth-patterns -- docs/research/oauth-patterns.md
```

After the draft stage, the reviewer checks only what the writer used from research:

```bash
# Compare draft against research notes — verify no unsourced claims were added
git diff research/issue-84-oauth-patterns...draft/issue-84-oauth-patterns -- docs/patterns/oauth-patterns.md
```

After the revision stage, the reviewer checks only that feedback was applied:

```bash
# Compare revised draft against original draft — verify reviewer notes were addressed
git diff draft/issue-84-oauth-patterns...revision/issue-84-oauth-patterns -- docs/patterns/oauth-patterns.md
```

Each `git diff` is 10–30 lines. The reviewer never re-reads the full page — only the delta from the prior known-good state. The same pattern applies to code: GitHub Copilot's coding agent opens a PR per task, so the diff scope matches one unit of work.

## Key Takeaways

- Mistakes live in new content — diffs focus review on exactly that
- Design agent pipelines so review happens at PR and checkpoint boundaries, not on complete artifacts
- Review fatigue scales with output size; diff-based review keeps the review surface manageable
- Multiple small diffs are preferable to one large diff — they are easier to review and easier to bisect
- Staged pipelines have natural diff boundaries at each stage handoff

## Related

- [Incremental Verification: Check at Each Step, Not at the End](../verification/incremental-verification.md)
- [Deterministic Guardrails Around Probabilistic Agents](../verification/deterministic-guardrails.md)
- [Layered Accuracy Defense](../verification/layered-accuracy-defense.md)
- [GitHub Copilot](../tools/copilot/index.md)
- [Review-Then-Implement Loop for AI Agent Development](review-then-implement-loop.md)
- [Agent-Assisted Code Review: Agents as PR First Pass](agent-assisted-code-review.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [Committee Review Pattern](committee-review-pattern.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [Predicting Reviewable Code](predicting-reviewable-code.md)
- [Tiered Code Review: AI-First with Human Escalation](tiered-code-review.md)
- [Agent-Authored PR Integration and Merge Predictors](agent-authored-pr-integration.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md)
- [Human-AI Review Synergy in Agentic Code Review](human-ai-review-synergy.md)
- [Agent PR Volume vs. Value: The Productivity Paradox](agent-pr-volume-vs-value.md)
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md)
- [Self-Improving Code Review Agents — Learned Rules](learned-review-rules.md)
