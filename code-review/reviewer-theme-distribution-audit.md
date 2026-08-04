---
title: "Reviewer Theme Distribution Audit for AI Code Review"
term: "Theme Distribution Audit"
description: "AI reviewers spend 30.8% of comments on best practices and 2.0% on security. Audit that theme mix against the comments your team resolves before re-weighting."
tags:
  - code-review
  - testing-verification
  - arxiv
  - tool-agnostic
aliases:
  - "code review theme distribution"
  - "AI reviewer comment mix audit"
  - "review theme re-weighting"
last_reviewed: 2026-08-03
maturity: emerging
---

# Reviewer Theme Distribution Audit for AI Code Review

> AI reviewers over-produce style comments and under-produce security ones. Audit the theme distribution against what your team resolves before re-weighting.

A theme distribution audit classifies your AI reviewer's recent comments against a review taxonomy, classifies which of your team's comments got resolved, and compares the two mixes. Run it on your own data. The published reference distribution comes from one engineering environment, and the authors state that its taxonomy, review gap, and metrics all reflect that organization's codebase, tooling, and review culture ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).

## The measured gap

ARCTIC derived a six-theme taxonomy from 18,000 human code reviews, then measured how AI reviewer output splits across the same themes ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).

| Theme | Human comments | AI comments |
|-------|----------------|-------------|
| Correctness and reliability | 44.4% | 25.5% |
| Code quality and maintainability | 19.2% | 22.9% |
| Security | 19.1% | 2.0% |
| Best practices and standards | 7.2% | 30.8% |
| Performance and efficiency | 6.6% | 2.7% |
| Code design | 3.6% | 16.2% |

Security is the largest inversion, at 19.1% of human comments against 2.0% of AI comments. Best practices and standards runs the other way, 7.2% human against 30.8% AI ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).

## Use resolution rates as the baseline

Comment share tells you where reviewers spend words, which is a different measurement from where developers act. A five-category study of human and LLM review comments found that readability, bug, and maintainability comments resolve at higher rates than code-design comments ([arXiv:2510.05450v1](https://arxiv.org/abs/2510.05450v1)). Suppressing readability output to chase the human comment mix can lower the share of comments your developers actually fix.

Human reviewers of agent-authored PRs show the same pull toward the supposedly low-value themes. A study of 19,450 inline comments across 3,177 agent-authored PRs found reviews concentrating on documentation gaps, refactoring needs, and styling alongside functional correctness ([arXiv:2601.19287v1](https://arxiv.org/abs/2601.19287v1)).

So run the audit in two passes. Classify the reviewer's last N comments against the taxonomy, then classify the comments your team resolved over the same window. The distance between those two distributions is your re-weighting target, and it is unlikely to match the published one.

## Three capabilities for agent-authored diffs

On a diff an agent wrote, the reviewer's question shifts from whether the code is correct to whether the agent did what was asked. ARCTIC splits that question into three parts ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)):

- Intent prediction infers why a change was made from conversation logs, change metadata, agent plans, and linked artifacts, without reading the diff. It scored 0.860 F1 against 0.844 for a single zero-shot prompt, at 6.4x the tokens ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).
- Drift detection backtranslates the diff into natural language and scores its distance from the inferred intent, reaching quadratic weighted kappa of 0.907 against human annotators on 118 diffs ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).
- Code spotlight ranks diff regions by review-worthiness through a generate-then-critic pass, improving quality estimation 2.4x over the baseline reviewer on 298 diffs at 5x fewer tokens ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).

Intent prediction is the prerequisite. It reads captured conversation and planning artifacts, so a team whose agents run without persisted prompts or plans has nothing for drift detection to compare against.

In the reported rollout, intent predictions drew 90.2% approval from 112 engineers, and showing the drift score reduced misalignment by a further 5.76 points (p = 0.026) across 193 diff pairs ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)). That comparison is quasi-experimental, with authors self-selecting into the group that saw the score, so treat the effect as directional.

## Why it works

Reviewer attention is a fixed budget spent across a diff whose regions differ sharply in how much scrutiny they repay, so a reviewer that comments evenly spends most of that budget where it buys nothing. Spotlight makes the ranking explicit: a generation stage triages the diff into candidate regions, and a critic stage validates each one on claim correctness, intent alignment, framework rules, actionability, and a senior-engineer acceptance bar. The gain comes from pruning rather than from deeper analysis, which is why quality estimation rose 2.4x while token use fell 5x ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)). Drift detection runs on a separate mechanism. Intent is inferred from conversation and metadata while the summary is backtranslated from the code, so the two descriptions are independent and their disagreement is informative without any correctness oracle.

## When this backfires

- No review corpus of your own. The reference distribution came from 18,000 reviews inside a single engineering environment, and the paper limits its transferability claim to the methodology ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)). Without comparable history you import another company's review culture as a target.
- Comment share used as the baseline. Readability and maintainability comments resolve at higher rates than design comments ([arXiv:2510.05450v1](https://arxiv.org/abs/2510.05450v1)), so cutting them to match the human mix lowers the actionable share of your reviewer's output.
- No captured intent signal. Intent prediction reads conversation logs, change metadata, agent plans, and linked artifacts ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)). Teams that persist none of those get no usable drift score.
- Gating on a middle drift score. The moderate and significant buckets score 0.341 to 0.409 F1 while the extremes are reliable ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)). Automate on the ends of the scale only.
- Standards-bound codebases. Where a style rule is itself the compliance artifact, cutting the best-practices category removes the output the review exists to produce.
- Delivery format left unchanged. Across 54,791 comments from five coding agents, an attached inline suggestion was the strongest predictor of resolution ([arXiv:2607.21997v2](https://arxiv.org/abs/2607.21997v2)). Theme re-weighting alone moves less than it appears to.

## Key Takeaways

- Theme mix is a measurable property of a reviewer, so treat a lopsided distribution as a defect with an owner rather than a tuning preference.
- Build both sides of the comparison from your own history. The published distribution is single-organization and its authors claim transferability only for the method.
- Baseline on the comments your team resolved rather than the comments your team wrote; readability and maintainability resolve more often than design ([arXiv:2510.05450v1](https://arxiv.org/abs/2510.05450v1)).
- Intent capture is the prerequisite for drift detection. No persisted prompts, plans, or task links means no reference to backtranslate against.
- Automate on extreme drift scores only. The middle buckets score 0.341 to 0.409 F1 ([arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1)).

## Related

- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the volume half of the same problem: silence as a valid review outcome, where this page governs the mix
- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — the per-comment reception data that makes resolution rate, rather than comment count, the right baseline
- [Security Review Gap in AI-Authored PRs](security-review-gap-in-ai-prs.md) — what the 2.0% security share leaves uncovered on agent-authored changes
- [Human-AI Review Synergy](human-ai-review-synergy.md) — the adoption-rate gap behind low uptake of AI review output
- [Inline Suggestion Attachment](inline-suggestion-attachment.md) — the delivery lever that competes with theme re-weighting for resolution gains

## Sources

- [arXiv:2607.29516v1](https://arxiv.org/abs/2607.29516v1) — Maddila et al. (2026): "From Code Review to Code Critique: Intent, Drift, and Spotlight for AI-Generated Diffs at Scale" (ARCTIC).
- [arXiv:2510.05450v1](https://arxiv.org/abs/2510.05450v1) — Goldman et al. (2025): "What Types of Code Review Comments Do Developers Most Frequently Resolve?"
- [arXiv:2601.19287v1](https://arxiv.org/abs/2601.19287v1) — Haider and Zimmermann (2026): "Understanding Dominant Themes in Reviewing Agentic AI-authored Code".
- [arXiv:2607.21997v2](https://arxiv.org/abs/2607.21997v2) — Cynthia et al. (2026): "Go Home Copilot, You're Drunk: Understanding Developer Responses to Agent-Generated Code Review Comments".
