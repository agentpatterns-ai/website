---
title: "Agentic Code Review Patterns and Review Architectures"
description: "Patterns for integrating AI agents into code review — from architecture and review loops to signal quality and PR integration."
tags:
  - code-review
  - index
  - tool-agnostic
last_reviewed: 2026-06-10
---

# Code Review

> Patterns for integrating AI agents into code review workflows.

As agents author more pull requests, review tooling is moving toward the surface where work is already tracked: Linear's Diffs feature brings code review inside the issue tracker, letting agents generate bulk diffs while keeping a human accountable for what merges ([Linear — Diffs](https://linear.app/changelog/2026-05-27-linear-diffs)). The patterns below cover the architectures and review loops that keep that accountability intact.

## Pages

- [Agent-Assisted Code Review](agent-assisted-code-review.md) — Agent-assisted code review routes the mechanical first pass to an agent, reserving human reviewers for design and architecture judgment
- [Agent Self-Review Loop](agent-self-review-loop.md) — Agents review their own output — running code review, security scanning, and quality checks — before submitting work for human review
- [Batched Suggestion Application](batched-suggestion-application.md) — Cluster mechanical agent suggestions and apply them as a single commit, with category-bounded batches and audit-trail discipline that prevent the workflow from becoming a rubber stamp
- [AIRA: Inspection Framework for AI-Generated Code](aira-inspection-framework.md) — A deterministic 15-check inspection framework targeting the failure-truthfulness patterns where AI-generated code preserves the appearance of functionality while silently degrading guarantees
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — Autonomous coding agents dramatically increase PR volume but face lower merge rates than humans — speed and quantity alone do not equal engineering value
- [Ecosystem-Level Integration Friction Governance](ecosystem-level-integration-friction-governance.md) — Govern AI coding agents at the repository level — integration friction concentrates roughly twice as much for agent PRs as for human PRs, so per-agent benchmarks underweight the risk that actually accumulates
- [Agent-Generated Code Maintenance Asymmetry](agent-code-maintenance-asymmetry.md) — AI-generated files receive about half the commit frequency of human-authored files, and the modification mix shifts from bug fixes to feature additions — a maintenance footprint that requires its own ownership and review policy
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged
- [Agent-Proposed Merge Resolution](agent-proposed-merge-resolution.md) — A merge conflict interaction contract where an agent resolves the conflict in a sandbox and the human confirms the result in a small number of clicks
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — Agentic code review replaces static diff analysis with a tool-calling architecture where the reviewer actively explores the repository
- [Bounded Tool Surfaces for Code Review Agents](bounded-tool-surface-review-agents.md) — Cap what each review tool can return and fix file-to-criteria dispatch outside the model — a large precision and cost win that is paid for in recall
- [Cloud Parallel Review Pattern](cloud-parallel-review-pattern.md) — Fan out code review across multiple agents in a remote sandbox, verify each candidate finding against actual code behavior, then aggregate into a single severity-ranked review
- [Reproduce-Before-Report Verification Gate](reproduce-before-report-verification-gate.md) — Place an independent verifier between reviewer findings and the user so only candidates that can be reproduced against actual code behavior are reported
- [Committee Review Pattern](committee-review-pattern.md) — Route agent-produced work through a panel of specialized reviewer agents — each applying a distinct lens — before accepting or iterating on the output
- [Evidence-Grounded Disagreement in Agentic Code Review](evidence-grounded-disagreement.md) — A reviewer-critic loop only beats a single reviewer once every objection must cite code; the naive form scored worse than one reviewer on real pull-request diffs
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — Empirical data from 3,109 PRs shows CRA-only review achieves a 45% merge rate versus 68% for human-only review — reviewer composition determines merge outcomes
- [Preempting Agentic PR Rejection by Failure-Mode Category](preempting-agentic-pr-rejection.md) — A 14-reason rejection taxonomy explains why 46% of agentic fix PRs fail, and only implementation and CI categories respond to preemption prompts
- [Diff-Based Review](diff-based-review.md) — Review what changed, not the full output — mistakes live in the delta, and diffs compress review effort to the right scope
- [Human-AI Review Synergy](human-ai-review-synergy.md) — Empirical evidence from 278,790 code reviews shows AI and human reviewers have complementary but unequal strengths — structuring collaboration around these differences improves outcomes
- [Learned Review Rules](learned-review-rules.md) — Code review agents that extract rules from accepted and rejected PR feedback, applying them to future reviews automatically — demonstrated by Cursor's Bugbot
- [Review-Feedback-to-Rule Loop](review-feedback-to-rule-loop.md) — Convert recurring code review comments into mechanical checks — a lint rule, an AST boundary check, or an evaluator rubric line — so the same comment never needs to be written twice
- [PR Description Style as a Lever](pr-description-style-lever.md) — Treating PR description structure as a configurable agent parameter measurably affects reviewer engagement and merge outcomes
- [Predicting Reviewable Code](predicting-reviewable-code.md) — Predictive models can identify AI-generated functions likely to be deleted before reviewers spend time examining them
- [Review-Then-Implement Loop](review-then-implement-loop.md) — Close the loop between AI code review and code generation — the reviewer identifies issues, a coding agent implements fixes, and a human reviews the result; covers the dialog, CLI-flag (in-process auto-fix), and cloud-agent direct-apply variants
- [Security Review Gap in AI-Authored PRs](security-review-gap-in-ai-prs.md) — Agent-authored security PRs cluster around six recurring CWE categories, 52.4% merge despite flaws, and commit-message quality stops predicting acceptance
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — Design AI code review to stay silent when it has nothing useful to say — high-signal feedback builds trust; exhaustive commenting destroys it
- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — Only about a third of agentic review comments get accepted in the wild — rejections track suggestion validity, so design for a high false-positive rate and measure acceptance, not volume
- [Inline Suggestion Attachment](inline-suggestion-attachment.md) — Attaching a ready-to-apply patch is the strongest measured predictor that an agent review comment gets resolved, but only where the finding is diff-verifiable — a one-click patch on a false positive is a one-click defect
- [Tiered Code Review](tiered-code-review.md) — Route review effort by risk: AI handles the first pass on everything, non-critical code merges after AI-only review, and critical code escalates to mandatory human review
- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — Expose review depth as a per-PR dial backed by a published bug-discovery curve, so reviewers and routing policies trade thoroughness against cost on the runs that need it
- [Risk-Score Threshold Calibration for Auto-Approval](risk-score-threshold-calibration.md) — Expose the auto-approval cutoff on a learned diff-risk score as an explicit yield-vs-safety knob, with revert and incident telemetry to recalibrate it
- [Deferred Standards Enforcement via Review Agents](deferred-standards-enforcement.md) — Move post-hoc-checkable standards out of CLAUDE.md into a reviewer agent that runs at PR time, preserving implementation context budget for the task at hand
- [Instruction-Aware Automated Code Review](instruction-aware-automated-review.md) — Wire AGENTS.md or REVIEW.md into the automated reviewer so its findings enforce documented team conventions — works only for rules the reviewer can mechanically verify from a diff
- [Agent-Driven PR Slicing](agent-driven-pr-slicing.md) — The agent that produced an in-flight branch proposes a logical decomposition into multiple smaller PRs at review time, using session intent rather than diff-only signals as the slicing signal
- [Structure-Aware Diff Labeling](structure-aware-diff-labeling.md) — A two-stage LLM pipeline labels diff hunks against a 12-type change taxonomy and refines cross-hunk relationships — useful where polyglot coverage outweighs determinism and cost
- [Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md) — A time-boxed inspection priority order — CI changes first, then duplicated utilities, then the critical path, then a failing-before test — for humans reviewing agent-authored PRs
- [Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md) — Repeat exposure to AI-authored PRs shifts within-reviewer approval rates up and comment volume down — diagnose with three co-moving signals and counter with structural guards, not exhortation
- [AI Label as Reviewer Attention Redistribution](ai-label-attention-redistribution.md) — Surfacing the LLM label and the originating prompt raises reviewer fixation time +33–60% and shifts strategy toward criteria-based or prompt-guided review, but the eye-tracking proxy for inspection thoroughness does not move
- [Reviewer Theme Distribution Audit for AI Code Review](reviewer-theme-distribution-audit.md) — AI reviewers put 30.8% of comments into best practices and 2.0% into security; audit that theme mix against the comments your own team resolves before re-weighting
- [Capturing Dismissal Reasons for Agent Review Findings](dismissal-reason-capture.md) — Record why a human rejected an agent review finding, in a closed vocabulary read back per rule — the two conditions that separate a precision measurement from an extra click
