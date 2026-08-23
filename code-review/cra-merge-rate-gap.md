---
title: "CRA-Only Review and the Merge Rate Gap"
description: "Empirical data from 3,109 PRs shows CRA-only review achieves a 45% merge rate versus 68% for human-only review — reviewer composition determines merge outcomes, not just comment quality."
term: "CRA Merge Rate Gap"
tags:
  - code-review
  - arxiv
  - tool-agnostic
aliases:
  - Code Review Agent Merge Rate
  - CRA Signal Ratio
last_reviewed: 2026-05-27
maturity: emerging
---

# CRA-Only Review and the Merge Rate Gap

> CRA-only reviewed PRs merge at 45.20% versus 68.37% for human-only reviewed PRs — a 23-point gap explained by low signal ratios, not tool failure.

## The evidence

An empirical study of 3,109 PRs from the AIDev dataset (HuggingFace-hosted repositories) measures how reviewer composition affects merge outcomes ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196v1)). The study sorts each PR by reviewer type — CRA-only, human-only, or mixed — and tracks the merge rate.

| Reviewer Composition | Merge Rate |
|----------------------|-----------|
| Human-only | 68.37% |
| Human-dominated mixed | 67.99% |
| CRA-only | 45.20% |

The 23-point merge rate gap contradicts industry claims that CRAs can manage 80% of open source PRs without human involvement ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196v1)).

## Why CRA-only reviews underperform

### The signal ratio problem

The study introduces a signal ratio metric: the fraction of CRA comments that are actionable, from 0.0 (all noise) to 1.0 (all signal). The study groups PRs into four bands:

- 0 to 30%: fewer than one-third of comments are actionable
- 31 to 59%: more noise than signal
- 60 to 79%: more signal than noise
- 80 to 100%: mostly actionable

Among closed CRA-only PRs, 60.2% fall into the 0 to 30% band. Across 13 CRAs studied, 12 show average signal ratios below 60% ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196v1)).

When most comments are noise, developers stop acting on them. PRs stall and are abandoned.

### Adoption rate baseline

This finding matches adoption rate data from a separate study of 278,790 code reviews: developers adopt AI suggestions at 16.6% versus 56.5% for human suggestions ([arXiv:2603.15911](https://arxiv.org/abs/2603.15911v1)). Low adoption follows from a low signal ratio — if most comments are not actionable, most comments are not adopted. The same low uptake appears at the level of individual comments in [agentic review comment acceptance](agentic-review-comment-acceptance.md).

## What mixed composition recovers

Human-dominated mixed reviews (CRA plus at least one human reviewer) reach a 67.99% merge rate — nearly the same as human-only. Adding a single human reviewer to a CRA-reviewed PR recovers most of the merge rate deficit.

The paper does not identify the mechanism. Regardless of what any single comment says, reviewer composition alone predicts merge outcomes.

## Practical implications

Do not deploy CRA-only review as a substitute for human review. The 23-point merge rate gap is the outcome. Treating CRA approval as equal to human approval produces more PR abandonment.

Use the signal ratio as a CRA calibration metric. Before trusting a CRA deployment, measure whether most of its comments are actionable. Fewer than 60% actionable is the measured threshold below which PR outcomes degrade.

Configure CRAs narrowly. Broad, general-purpose review generates the most noise. Narrow CRA configurations — scoped to security vulnerabilities, style violations, or specific checklist items — cut noise volume and raise the signal ratio. See [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md).

Mixed composition is the practical baseline. CRA-first review with required human approval before merge recovers the merge rate. The CRA handles the mechanical first pass; the human provides the credibility signal and design judgment. See [Tiered Code Review](tiered-code-review.md).

## Key Takeaways

- A CRA-only reviewed PR merges at roughly two-thirds the rate of a human-reviewed one (45.20% vs. 68.37%) — treat CRA-only review as a partial pass that still needs a human check
- 60.2% of closed CRA-only PRs had fewer than 30% actionable comments — audit a CRA's comment history alongside its pass/fail verdict before trusting an approval
- Signal ratio is the lever, not vendor choice: 12 of 13 CRAs sit below 60%, so constraining what the agent may comment on moves the number further than switching tools
- One human reviewer is the cheapest available fix, recovering the merge rate to 67.99%. Route CRA output to a person rather than trying to raise CRA autonomy
- Do not size human review headcount off vendor claims of 80% CRA self-sufficiency — plan review capacity from measured merge outcomes instead

## When this backfires

CRA-only review performs closest to human-only when the CRA is narrowly scoped and the repository has low merge-rate stakes. Three conditions favor CRA-only:

- Bot-generated PRs: dependency bumps, automated refactors, and chore PRs where merge criteria are explicit and mechanical
- Signal ratio above 80%: if you have calibrated a CRA to exceed this threshold on your codebase, the 60.2% abandonment finding may not apply
- Low-volume, low-risk contexts: internal tooling repositories where abandonment is acceptable and human review bandwidth is the binding constraint

The study measured the 23-point gap on HuggingFace-hosted ML and AI repositories; it does not establish that the gap generalizes to other software domains. The study validated the signal ratio as a calibration metric across 13 CRAs — whether it transfers equally to CRA tools outside that set is not confirmed.

## Related

- [Human-AI Review Synergy](human-ai-review-synergy.md) — adoption rate data (16.6% vs. 56.5%) and complexity effects that explain why CRA comments produce lower merge credibility
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — design principle for raising signal ratio: silence as valid output, confidence thresholds, severity filtering
- [Tiered Code Review](tiered-code-review.md) — risk-based routing that provides the structural framework for CRA-first plus human-last review
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — agent-as-author merge rates; this page covers agent-as-reviewer — complementary data points
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — collaboration signals (reviewer engagement, force pushes, change size) that predict merge success for agent-authored PRs; logistic regression on same AIDev dataset
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md) — how PR description structure (not just reviewer composition) affects merge outcomes using the same AIDev dataset
- [Agent-Assisted Code Review](agent-assisted-code-review.md) — prescriptive guide for structuring the AI first pass
- [Committee Review Pattern](committee-review-pattern.md) — multi-agent verification as an alternative to single CRA deployment

## Sources

- [arXiv:2604.03196](https://arxiv.org/abs/2604.03196) — Chowdhury et al. (2026): "From Industry Claims to Empirical Reality: An Empirical Study of Code Review Agents in Pull Requests" — MSR 2026 Mining Challenge
- [arXiv:2603.15911](https://arxiv.org/abs/2603.15911) — related study: 278,790 code reviews quantifying AI vs. human suggestion adoption rates
