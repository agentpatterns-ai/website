---
title: "Agentic Code Review Patterns and Review Architectures"
description: "Patterns for integrating AI agents into code review — from architecture and review loops to signal quality and PR integration."
tags:
  - code-review
---

# Code Review

> Patterns for integrating AI agents into code review workflows.

## Pages

- [Agent-Assisted Code Review](agent-assisted-code-review.md) — Agent-assisted code review routes the mechanical first pass to an agent, reserving human reviewers for design and architecture judgment
- [AIRA: Inspection Framework for AI-Generated Code](aira-inspection-framework.md) — A deterministic 15-check inspection framework targeting the failure-truthfulness patterns where AI-generated code preserves the appearance of functionality while silently degrading guarantees
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — Autonomous coding agents dramatically increase PR volume but face lower merge rates than humans — speed and quantity alone do not equal engineering value
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged
- [Agent-Proposed Merge Resolution](agent-proposed-merge-resolution.md) — A merge conflict interaction contract where an agent resolves the conflict in a sandbox and the human confirms the result in a small number of clicks
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — Agentic code review replaces static diff analysis with a tool-calling architecture where the reviewer actively explores the repository
- [Cloud Parallel Review Pattern](cloud-parallel-review-pattern.md) — Fan out code review across multiple agents in a remote sandbox, verify each candidate finding against actual code behavior, then aggregate into a single severity-ranked review
- [Committee Review Pattern](committee-review-pattern.md) — Route agent-produced work through a panel of specialized reviewer agents — each applying a distinct lens — before accepting or iterating on the output
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — Empirical data from 3,109 PRs shows CRA-only review achieves a 45% merge rate versus 68% for human-only review — reviewer composition determines merge outcomes
- [Diff-Based Review](diff-based-review.md) — Review what changed, not the full output — mistakes live in the delta, and diffs compress review effort to the right scope
- [Human-AI Review Synergy](human-ai-review-synergy.md) — Empirical evidence from 278,790 code reviews shows AI and human reviewers have complementary but unequal strengths — structuring collaboration around these differences improves outcomes
- [Learned Review Rules](learned-review-rules.md) — Code review agents that extract rules from accepted and rejected PR feedback, applying them to future reviews automatically — demonstrated by Cursor's Bugbot
- [PR Description Style as a Lever](pr-description-style-lever.md) — Treating PR description structure as a configurable agent parameter measurably affects reviewer engagement and merge outcomes
- [Predicting Reviewable Code](predicting-reviewable-code.md) — Predictive models can identify AI-generated functions likely to be deleted before reviewers spend time examining them
- [Review-Then-Implement Loop](review-then-implement-loop.md) — Close the loop between AI code review and code generation — the reviewer identifies issues, a coding agent implements fixes, and a human reviews the result
- [Security Review Gap in AI-Authored PRs](security-review-gap-in-ai-prs.md) — Agent-authored security PRs cluster around six recurring CWE categories, 52.4% merge despite flaws, and commit-message quality stops predicting acceptance
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — Design AI code review to stay silent when it has nothing useful to say — high-signal feedback builds trust; exhaustive commenting destroys it
- [Tiered Code Review](tiered-code-review.md) — Route review effort by risk: AI handles the first pass on everything, non-critical code merges after AI-only review, and critical code escalates to mandatory human review
- [Deferred Standards Enforcement via Review Agents](deferred-standards-enforcement.md) — Move post-hoc-checkable standards out of CLAUDE.md into a reviewer agent that runs at PR time, preserving implementation context budget for the task at hand
