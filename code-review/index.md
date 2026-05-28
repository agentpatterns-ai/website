---
title: "Agentic Code Review Patterns and Review Architectures"
description: "Patterns for integrating AI agents into code review — from architecture and review loops to signal quality and PR integration."
tags:
  - code-review
last_reviewed: 2026-05-27
---

# Code Review

> Patterns for integrating AI agents into code review workflows.

## Pages

- [Agent-Assisted Code Review](agent-assisted-code-review.md) — Agent-assisted code review routes the mechanical first pass to an agent, reserving human reviewers for design and architecture judgment
- [Batched Suggestion Application](batched-suggestion-application.md) — Cluster mechanical agent suggestions and apply them as a single commit, with category-bounded batches and audit-trail discipline that prevent the workflow from becoming a rubber stamp
- [AIRA: Inspection Framework for AI-Generated Code](aira-inspection-framework.md) — A deterministic 15-check inspection framework targeting the failure-truthfulness patterns where AI-generated code preserves the appearance of functionality while silently degrading guarantees
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — Autonomous coding agents dramatically increase PR volume but face lower merge rates than humans — speed and quantity alone do not equal engineering value
- [Agent-Generated Code Maintenance Asymmetry](agent-code-maintenance-asymmetry.md) — AI-generated files receive about half the commit frequency of human-authored files, and the modification mix shifts from bug fixes to feature additions — a maintenance footprint that requires its own ownership and review policy
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged
- [Agent-Proposed Merge Resolution](agent-proposed-merge-resolution.md) — A merge conflict interaction contract where an agent resolves the conflict in a sandbox and the human confirms the result in a small number of clicks
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — Agentic code review replaces static diff analysis with a tool-calling architecture where the reviewer actively explores the repository
- [Cloud Parallel Review Pattern](cloud-parallel-review-pattern.md) — Fan out code review across multiple agents in a remote sandbox, verify each candidate finding against actual code behavior, then aggregate into a single severity-ranked review
- [Committee Review Pattern](committee-review-pattern.md) — Route agent-produced work through a panel of specialized reviewer agents — each applying a distinct lens — before accepting or iterating on the output
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — Empirical data from 3,109 PRs shows CRA-only review achieves a 45% merge rate versus 68% for human-only review — reviewer composition determines merge outcomes
- [Diff-Based Review](diff-based-review.md) — Review what changed, not the full output — mistakes live in the delta, and diffs compress review effort to the right scope
- [Human-AI Review Synergy](human-ai-review-synergy.md) — Empirical evidence from 278,790 code reviews shows AI and human reviewers have complementary but unequal strengths — structuring collaboration around these differences improves outcomes
- [Learned Review Rules](learned-review-rules.md) — Code review agents that extract rules from accepted and rejected PR feedback, applying them to future reviews automatically — demonstrated by Cursor's Bugbot
- [Review-Feedback-to-Rule Loop](review-feedback-to-rule-loop.md) — Convert recurring code review comments into mechanical checks — a lint rule, an AST boundary check, or an evaluator rubric line — so the same comment never needs to be written twice
- [PR Description Style as a Lever](pr-description-style-lever.md) — Treating PR description structure as a configurable agent parameter measurably affects reviewer engagement and merge outcomes
- [Predicting Reviewable Code](predicting-reviewable-code.md) — Predictive models can identify AI-generated functions likely to be deleted before reviewers spend time examining them
- [Review-Then-Apply CLI Flag](review-then-apply-cli-flag.md) — A CLI-flag variant where the same code-review command that scores findings also writes the patch — safe only with a calibrated rubric, a clean-tree guard, and template-shaped findings
- [Review-Then-Implement Loop](review-then-implement-loop.md) — Close the loop between AI code review and code generation — the reviewer identifies issues, a coding agent implements fixes, and a human reviews the result
- [Security Review Gap in AI-Authored PRs](security-review-gap-in-ai-prs.md) — Agent-authored security PRs cluster around six recurring CWE categories, 52.4% merge despite flaws, and commit-message quality stops predicting acceptance
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — Design AI code review to stay silent when it has nothing useful to say — high-signal feedback builds trust; exhaustive commenting destroys it
- [Tiered Code Review](tiered-code-review.md) — Route review effort by risk: AI handles the first pass on everything, non-critical code merges after AI-only review, and critical code escalates to mandatory human review
- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — Expose review depth as a per-PR dial backed by a published bug-discovery curve, so reviewers and routing policies trade thoroughness against cost on the runs that need it
- [Deferred Standards Enforcement via Review Agents](deferred-standards-enforcement.md) — Move post-hoc-checkable standards out of CLAUDE.md into a reviewer agent that runs at PR time, preserving implementation context budget for the task at hand
- [Agent-Driven PR Slicing](agent-driven-pr-slicing.md) — The agent that produced an in-flight branch proposes a logical decomposition into multiple smaller PRs at review time, using session intent rather than diff-only signals as the slicing signal
- [Structure-Aware Diff Labeling](structure-aware-diff-labeling.md) — A two-stage LLM pipeline labels diff hunks against a 12-type change taxonomy and refines cross-hunk relationships — useful where polyglot coverage outweighs determinism and cost
- [Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md) — A time-boxed inspection priority order — CI changes first, then duplicated utilities, then the critical path, then a failing-before test — for humans reviewing agent-authored PRs
