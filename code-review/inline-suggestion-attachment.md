---
title: "Inline Suggestion Attachment in Agent Code Review"
term: "Inline Suggestion Attachment"
description: "Attaching a ready-to-apply patch is the strongest measured predictor that an agent review comment gets resolved, but attach one only where the finding is mechanically verifiable: a one-click patch on a false positive is a one-click defect."
tags:
  - code-review
  - human-factors
  - arxiv
  - tool-agnostic
aliases:
  - applicable suggestions in agent review
  - code suggestion attachment
  - suggestion blocks on review comments
last_reviewed: 2026-07-28
maturity: emerging
---

# Inline Suggestion Attachment

> Attaching a ready-to-apply inline suggestion moves agent review comments to resolution more than clearer prose does, where the finding is mechanically verifiable.

Attach an inline code suggestion to an agent review comment and developers act on it more often than on the same finding written as better prose. A study of agent-generated review comments across 342 Python repositories analyzed 54,713 of them from Copilot, Cursor, and Codex: comments carrying an inline suggestion resolved at 75.5% against 64.5% without, and suggestion attachment was the strongest predictor in the model at odds ratio 1.617 ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)). Clarity scored 1.022. Prose quality is measurably not the lever.

## Attach only where the finding is mechanically checkable

The attachment decision is a gate, not a default. A suggestion block lowers the cost of acting, which is useful only when acting is the right outcome, so apply it under three conditions:

- The finding is verifiable from the diff alone. A missing null check, a wrong comparison operator, an unhandled error path. Where correctness can be confirmed by reading the patch, cheap acceptance is cheap correctness.
- The fix is localized. One hunk, one call site, no dependent edits elsewhere. A suggestion that is only part of the change invites a partial application.
- The surrounding code is simple enough to review at a glance.

Where those conditions fail (design disagreements, cross-file refactors, anything contestable), post prose and no patch. Among the comments core developers left unresolved, over 72% were rejected on intentional-design-decision grounds ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)); a diff-shaped suggestion cannot carry an architectural argument, and dressing an opinion as a mechanical fix invites the wrong kind of agreement.

## What the model actually ranks

Every variable that reduces interpretive work moves resolution. Every variable that adds prose does not.

| Predictor | Odds ratio | Direction |
|---|---|---|
| Inline code suggestion | 1.617 | Raises resolution |
| Conciseness | 1.059 | Raises resolution |
| Relevance | 1.046 | Raises resolution |
| Clarity | 1.022 | Raises resolution |
| Comment length (log) | 0.926 | Lowers resolution |
| Has explanation | 0.593 | Lowers resolution |

All values from [arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2); every row is significant at p<0.05. The length penalty is sharper on functional-issue comments at 0.855. Read the explanation row carefully: among comments that carry explanations, two explanation types peak at 71.7% usefulness. The finding is that more prose does not buy action, which is a narrower claim than explaining being pointless.

Resolution rates varied by agent: Copilot 72.9%, Cursor 67.2%, Codex 54.8% ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)).

## Why it works

An inline suggestion changes what the comment asks of the developer. Prose requires them to interpret the finding, locate the site, author the edit, and commit it. A suggestion block collapses that to reading a concrete diff and applying it. The GitHub suggestion feature exists for exactly that: it makes "reviewers' feedback more actionable for the submitters" ([arXiv:2502.04835](https://arxiv.org/abs/2502.04835v1)). Resolution varies with the cost of acting, not persuasiveness ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997)). The same mechanism corroborates outside agent review: pull requests using human-authored suggestions merged at 76.2% against 65.7% without ([arXiv:2502.04835](https://arxiv.org/abs/2502.04835v1)).

## When this backfires

The mechanism is friction removal, so it removes friction from wrong changes just as efficiently.

- Comment validity is unmeasured. A patch attached to a false positive converts a comment the developer would have skipped into a one-click defect. Incorrect suggestions and intentional design decisions are the two most prevalent reasons comments go unresolved, and 63 of the 67 incorrect-suggestion cases were factually wrong or false positives ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)); a separate reception study finds rejection tracks validity rather than packaging ([arXiv:2607.03316](https://arxiv.org/abs/2607.03316v2)). Gate on [comment acceptance data](agentic-review-comment-acceptance.md) before optimizing attachment.
- The person applying the patch is not the person who would push back. Core developers (the top 20% by authored and reviewed pull requests) resolved 78.1% of Copilot's resolved comments, and design-grounds rejection concentrates in that group ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)). A one-click patch applied by a contributor with less repository context skips the scrutiny that data attributes to core reviewers.
- Merge latency matters more than resolution. Suggestion use significantly increased pull request resolution time and produced no decrease in code complexity ([arXiv:2502.04835](https://arxiv.org/abs/2502.04835)). More action is not faster delivery.
- You are treating resolution as usefulness. The authors flag resolution as "an imperfect proxy" and report the model's discrimination as low at AUC 0.58 ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997)). Suggestion attachment is the strongest lever inside a model that explains a small share of the outcome.
- Your stack is unlike the sample. Findings come from Python repositories with at least 1,000 stars, 1,000 pull requests, and 50 contributors; the authors name other languages, small projects, and proprietary settings as generalizability threats, and excluded Devin and Claude for insufficient data ([arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2)).

## Key Takeaways

- Suggestion attachment resolved comments at 75.5% versus 64.5% without and was the strongest predictor at odds ratio 1.617 against 1.022 for clarity; spend triage time writing the patch, not polishing the comment.
- Core developers resolved 78.1% of Copilot's resolved comments and are also where design-grounds rejection concentrates: route one-click patches through a reviewer with real repository context.
- Longer comments resolve less often (odds ratio 0.926), and the explanation flag is negatively associated at 0.593: rewriting prose is the wrong first knob.
- Attach a patch only where the finding is diff-verifiable and localized; post prose for design disagreements.
- The effect is observational on a model with AUC 0.58, measured against resolution rather than usefulness, so validity gating comes before attachment.

## Related

- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — the validity gate this pattern depends on: rejections track whether the comment was right, not how it was packaged
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the companion constraint: attach suggestions to fewer, higher-confidence comments rather than to everything
- [Batched Suggestion Application](batched-suggestion-application.md) — what to do once suggestions arrive in bulk, and the cluster discipline that stops bulk apply becoming a rubber stamp
- [Review-Then-Implement Loop](review-then-implement-loop.md) — the escalation path when a finding is real but too large to express as an inline patch
- [Learned Review Rules](learned-review-rules.md) — feed applied and dismissed suggestions back so the reviewer stops emitting the patches nobody takes

## Sources

- [arXiv:2607.21997](https://arxiv.org/abs/2607.21997v2) — Cynthia, Widyasari, Roy, Zhang, Lo (2026): "Go Home Copilot, You're Drunk": Understanding Developer Responses to Agent-Generated Code Review Comments — 54,791 comments collected across 342 Python repositories, 54,713 analyzed from three agents.
- [arXiv:2502.04835](https://arxiv.org/abs/2502.04835v1) — Bouraffa, Pham, Maalej (2025): How Do Developers Use Code Suggestions in Pull Request Reviews? — 8,672 suggestions across 2,852 pull requests in 46 projects.
- [arXiv:2607.03316](https://arxiv.org/abs/2607.03316) — Lin, Liang, Thongtanunam, Tantithamthavorn (2026): Is Agentic Code Review Helpful? Mining Developers' Feedback to CodeRabbit Reviews in the Wild.
