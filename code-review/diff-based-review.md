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

Reading a 500-word page and spotting one wrong claim is hard. Reading a 20-line diff and spotting it is easy. Review effort scales with the size of what you read; error density is highest in what is new.

Agent-driven workflows should be designed so human review happens at diff boundaries — pull requests, staged changes, comment threads — not on complete artifacts.

## The PR Model as Review Boundary

[GitHub Copilot's coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) produces output as pull requests. This is not incidental — PRs are the natural diff boundary for code review. The same structure applies to [content pipelines](../workflows/content-pipeline.md):

- Draft pages open as PRs against main
- Review agents comment on the PR diff, not on the full page
- Human approval gates on the merge diff, not on re-reading the artifact

The PR model enforces that review happens on changes, not on totals.

## Checkpoints and Known-Good States

[Claude Code's checkpointing](https://code.claude.com/docs/en/checkpointing) automatically captures file state before each user prompt. When agent work goes wrong, you can restore code to a prior checkpoint, then use `git diff` to compare the restored state against the current working tree. Checkpoints do not provide a built-in diffing view [unverified — this claim about Claude Code checkpointing is not confirmed by cited documentation] — pair them with git to get reviewable diffs.

Structuring work around checkpoints keeps the diff scope predictable:

- One logical unit of work → one checkpoint interval → one `git diff` to review
- Multiple checkpoint intervals → multiple restore points → easier to bisect failures

## Review Fatigue and Output Size

Review fatigue grows with output size, not diff size. An agent that produces 2,000 lines across ten files will be reviewed less carefully than an agent that produces 20 lines in one file — full-artifact review does not scale.

Designing for diff-based review means:

- Breaking agent work into small, independently reviewable units
- Committing checkpoints between logical stages
- Opening separate PRs for separate concerns rather than one large PR

A series of five 20-line PRs gets better review coverage than one 100-line PR [unverified — no formal study on review quality vs. diff size, but consistent with code review best practice literature].

## Staged Review

Multi-stage pipelines have multiple natural diff boundaries:

1. **Research stage** — diff the research notes against the issue description. Verify the researcher captured the right sources.
2. **Draft stage** — diff the draft against the research notes. Verify the writer only used sourced material.
3. **Revision stage** — diff the revised draft against the original draft. Verify reviewer feedback was applied correctly.

Each diff is small, focused, and reviewable in isolation. Reviewing the final published page against nothing is the hardest review; reviewing a 10-line diff against a known state is the easiest.

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
