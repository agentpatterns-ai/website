---
title: "Reviewer Habituation in Agent PR Review"
term: "Reviewer Habituation"
description: "Repeat exposure to AI-authored PRs shifts within-reviewer approval rates up and comment volume down — diagnose with three co-moving signals and counter with structural guards, not exhortation."
aliases:
  - within-reviewer scrutiny decay
  - longitudinal reviewer habituation
  - AI PR approval drift
tags:
  - code-review
  - human-factors
  - testing-verification
  - arxiv
  - tool-agnostic
last_reviewed: 2026-06-24
maturity: emerging
---

# Reviewer Habituation in Agent PR Review

> Repeat exposure to agent PRs lifts a reviewer's approval rate and cuts comments while latency grows — three co-moving signals separate habituation from trust gain.

## When this pattern applies

The longitudinal decay shows up only under repeat within-reviewer exposure to agent-authored PRs over months. A team where each reviewer sees fewer than ten agent PRs per quarter, or where revert telemetry feeds back to specific approvals, will not see this curve. The risk concentrates in the opposite conditions: sustained queues of plausible-looking agent PRs reviewed by the same people, with weak revert visibility ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)).

## The measured effect

A within-reviewer longitudinal study on the AIDev dataset followed 400 repeat reviewers and 11,429 reviews over seven months, comparing each reviewer's early and late review episodes ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)):

| Signal | Direction | Magnitude |
|--------|-----------|-----------|
| Approval rate (paired within-reviewer) | up | 30.1% → 36.8% (p < 10⁻⁶) |
| Approval rate gap, first versus tenth experience decile | up | +14.5 percentage points |
| Inline-comment volume per review | down | 22% (p = 0.0014) |
| Median review latency | up | 3.5× |

Source dataset and methodology: AIDev ([arXiv:2602.09185](https://arxiv.org/abs/2602.09185)). The study controls for calendar time and reports PR size held flat across the window, closing the two obvious confounders — that agents simply got better, or that diffs got smaller.

## The three-signal diagnostic

Approval going up while comments go down can mean two opposite things. Rational trust calibration: the reviewer has learned which agent code is safe and is correctly approving more, faster, with less commentary. Habituation: the reviewer is offloading scrutiny under load while approving more, slowly, with less commentary. The signal that separates them is review latency direction. A 3.5× rise in time-to-decision alongside falling comments is incompatible with confident pattern-recognition; it is consistent with avoidance ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)). Track all three together — a single rising-approval-rate dashboard hides the difference.

## Why it works

Repeat exposure to plausibly-shaped agent output anchors a low-defect prior even when actual defect rates have not moved. Once the prior is anchored, the cognitive cost of overriding it — opening files, tracing the critical path, demanding evidence — rises faster than the perceived payoff, while the verbal commitment to "reviewing" stays intact. The result is reflexive habituation rather than trust calibration ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)). The pattern is the within-reviewer counterpart to two static effects this site already documents: alert fatigue past the rubber-stamp threshold ([Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md)) and signal-ratio decay below 60% actionable comments ([CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md)). What is new is time: an individual reviewer's curve, not a population's snapshot.

## Structural guards outperform exhortation

The three signals are stable enough to design against, but no individual reviewer can correct habituation by trying harder — the mechanism is sub-deliberate ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)). Effective countermeasures move the work, not the resolve:

- Rotate the reviewer-of-record on agent PRs. Fresh reviewers carry unaged priors. The same agent PR pool reviewed by a rotating panel breaks the within-reviewer anchoring the paper measures.
- Route by risk, not by queue order. A learned diff-risk threshold and mandatory human review on high-risk diffs ([Risk-Score Threshold Calibration](risk-score-threshold-calibration.md)) keeps the highest-stakes PRs out of the habituated channel.
- Shrink the scope per PR. Smaller diffs cost less to inspect properly, so the cost-of-scrutiny side of the trade-off falls before the reviewer adapts away from it ([Law of Triviality in AI PRs](../patterns/anti-patterns/law-of-triviality-ai-prs.md)).
- Make reverts visible per approver. Revert and incident telemetry attached to specific approvals creates the consequence loop whose absence the paper identifies as the conditions under which habituation grows ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)).

## When this backfires

The longitudinal-decay finding rests on a single workshop preprint ([arXiv:2606.22721](https://arxiv.org/abs/2606.22721)) with no independent replication, and the proposed structural guards each carry their own load. Mandatory rotation across reviewers who lack repo context produces the credibility gap that pushes CRA-only review to a 45% merge rate against 68% for human-only ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196)). Hard size gates split atomic refactors into incoherent fragments ([Law of Triviality in AI PRs](../patterns/anti-patterns/law-of-triviality-ai-prs.md)). Adversaries calibrated to a learned risk-score threshold can structure malicious diffs into the auto-approved tier ([Risk-Score Threshold Calibration](risk-score-threshold-calibration.md)). And in regulated domains where human sign-off is itself the compliance act, "habituation" is the wrong frame: the approval is structurally mandatory regardless of cognitive state.

## Key Takeaways

- Within-reviewer approval rates rise (30.1% → 36.8%, p < 10⁻⁶) while comment volume falls 22% and latency triples — three co-moving signals that distinguish habituation from rational trust gain.
- The 14.5 pp gap between first and tenth review episode for the same reviewer is the within-person effect; the population snapshot misses it.
- The mechanism is sub-deliberate, so structural guards (rotation, risk-routing, scope limits, revert telemetry) outperform exhortation.
- The finding is single-source (workshop preprint, AIDev dataset) — treat the size of the response as proportional to your repeat-exposure conditions.

## Related

- [Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md) — the inspection priority order habituation degrades over time
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — composition-level evidence that complements the within-reviewer measurement here
- [Human-AI Review Synergy](human-ai-review-synergy.md) — adoption-rate baseline (16.6% vs 56.5%) that habituation pulls in the opposite direction
- [Risk-Score Threshold Calibration for Auto-Approval](risk-score-threshold-calibration.md) — the route-by-risk guard against habituated channels
- [Law of Triviality in AI PRs](../patterns/anti-patterns/law-of-triviality-ai-prs.md) — the static rubber-stamp anti-pattern; this page is its within-reviewer longitudinal counterpart

## Sources

- [arXiv:2606.22721](https://arxiv.org/abs/2606.22721) — Yu, Liu, Jiang, Jia, Wang, Qian, Chen (June 2026): "Habituation at the Gate: Rising Approval and Declining Scrutiny in Human Review of AI Agent Code", KDD 2026 SE 3.0 Workshop.
- [arXiv:2602.09185](https://arxiv.org/abs/2602.09185) — Li et al. (2026): "AIDev: Studying AI Coding Agents on GitHub" — source dataset.
- [arXiv:2604.03196](https://arxiv.org/abs/2604.03196) — Chowdhury et al. (2026): CRA-only review and the merge-rate gap.
