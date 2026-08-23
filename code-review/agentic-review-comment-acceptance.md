---
title: "Agentic Review Comment Acceptance"
term: "Review Comment Acceptance"
description: "Only about a third of agentic code-review comments get accepted in the wild — rejections track suggestion validity, so design for a high false-positive rate and measure acceptance, not comment volume."
tags:
  - code-review
  - testing-verification
  - human-factors
  - arxiv
  - tool-agnostic
last_reviewed: 2026-07-24
maturity: emerging
---

# Agentic Review Comment Acceptance

> Only about a third of agentic code-review comments get accepted — rejections track suggestion validity, so design for a high false-positive rate and measure acceptance.

Agentic reviewers post comments faster than developers accept them. A study of CodeRabbit in the wild mined 31,073 review-and-feedback pairs across 10,191 pull requests and 239 repositories. Developers accepted 36.4% of the comments, discussed 7.3%, and rejected 56.3% ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)). A review agent that comments on your PRs is, on this evidence, wrong more often than it is right. Treat a high false-positive rate as the operating condition.

## What the reception data shows

Rejections are driven by suggestion validity, not comment count. The study attributes rejected comments to invalid suggestions — false positives, redundant observations, and out-of-scope recommendations — plus misalignment with the developer's intent and coding practices ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)).

Not all comment types fare equally. Agentic reviews concentrated more on functional concerns than on evolvability-related comments, yet the evolvability comments carried higher invalidity rates ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)). The agent is on firmer ground flagging what breaks than judging what is "cleaner."

Low comment-level uptake is not unique to this tool. A separate study of 278,790 code reviews found developers adopt AI suggestions at 16.6% against 56.5% for human suggestions ([arXiv:2603.15911](https://arxiv.org/abs/2603.15911v1)), and a signal-ratio study found 12 of 13 code-review agents average below 60% actionable comments ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196v1)). The reception gap is a property of current agentic review, not one vendor.

## Two practical levers

Measure acceptance, do not assume it. Track accept, discuss, and reject rates per repository and per comment type, the same instrumentation [signal over volume](signal-over-volume-in-ai-review.md) calls for. An acceptance rate you have not measured is a value you are assuming.

Pre-filter for validity. Rejection is predictable: lightweight machine-learning features reached up to 76% F1 for predicting which comments developers would reject ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)). That makes a suppression layer feasible — score a candidate comment before it posts and drop the likely-invalid ones, rather than throttling volume blindly.

## Why it works

A review comment earns action only when it names a real defect the developer agrees is worth fixing in this change. Agentic reviewers over-produce plausible-but-invalid suggestions, especially on evolvability, where "better" is contextual, so the marginal comment is more likely noise than signal. Developers reject on validity grounds regardless of comment volume ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)). Because invalidity is the cause, comment quality governs acceptance, which is exactly why the reject signal is learnable from lightweight features. Optimizing validity moves the acceptance rate; adding or trimming volume alone does not.

## When this backfires

Optimizing for acceptance rate is the wrong target in several conditions:

- High-recall, high-stakes review. On security or critical-path code, tolerating false positives to avoid a missed defect is correct. A low acceptance rate here is a deliberate trade, not a failure to fix ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)).
- Tuned or learning-loop deployments. Once an agent is scoped to repository conventions and fed accept/reject feedback via [learned review rules](learned-review-rules.md), its acceptance rate moves. The 56.3% wild baseline overstates rejection for a calibrated deployment.
- Low comment volume. Acceptance-rate measurement is noisy below enough comments per repository and per comment type to be stable; small teams may lack the data.
- Single-tool generalization. The figures are CodeRabbit-specific across 239 repositories ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)); other agentic reviewers and other stacks accept and reject at materially different rates.

## Key Takeaways

- Developers accepted 36.4% of agentic review comments, discussed 7.3%, and rejected 56.3% across 31,073 comments in the wild ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316)).
- Rejection tracks suggestion validity — false positives, redundancy, out-of-scope, intent misalignment — not comment volume.
- Functional comments are accepted more than evolvability comments, which carry higher invalidity rates.
- Rejection is predictable (up to 76% F1 from lightweight features), so a validity pre-filter is feasible.
- Measure acceptance per repository and comment type. Do not assume value from comment count.

## Related

- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the design principle this reception data grounds: raise validity, treat silence as valid output
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — the PR-level counterpart: signal ratio and merge outcomes rather than per-comment acceptance
- [Inline Suggestion Attachment](inline-suggestion-attachment.md) — what raises action once validity is handled: a ready-to-apply patch outranks clearer prose as a resolution lever
- [Learned Review Rules](learned-review-rules.md) — persist accept/reject signals to suppress recurring invalid comments automatically
- [Human-AI Review Synergy](human-ai-review-synergy.md) — the 16.6% vs 56.5% adoption baseline behind the reception gap
- [Tiered Code Review](tiered-code-review.md) — route high-stakes diffs where a low acceptance rate is an accepted trade

## Sources

- [arXiv:2607.03316](https://arxiv.org/abs/2607.03316) — Lin, Liang, Thongtanunam, Tantithamthavorn (2026): "Is Agentic Code Review Helpful? Mining Developers' Feedback to CodeRabbit Reviews in the Wild" — 31,073 comment/feedback pairs, 10,191 PRs, 239 repositories.
- [arXiv:2604.03196](https://arxiv.org/abs/2604.03196v1) — Chowdhury et al. (2026): code-review-agent signal-ratio study; 12 of 13 CRAs below 60% actionable.
- [arXiv:2603.15911](https://arxiv.org/abs/2603.15911v1) — 278,790 code reviews: AI suggestion adoption 16.6% versus 56.5% for human suggestions.
