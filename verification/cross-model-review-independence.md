---
title: "When a Second Model Helps in LLM Review"
term: "Cross-Model Review"
description: "Route code review to the generating model in a fresh session and prose review to a second vendor, and pair them only when you are already paying for two review calls."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - cross-model review
  - model independence
  - XMR
last_reviewed: 2026-10-05
maturity: emerging
---

# When a Second Model Helps in LLM Review

> A second model finds different, not uniformly better, defects. One same-model and one top-tier cross-model review matched 56.7% of planted errors; two same-model, 42.7%.

Cross-model review uses a reviewer from a different model family than the one that produced the artifact. Treat it as a routing decision. The experiment behind these numbers ran 900 review sessions over 30 artifacts carrying 150 planted errors, across 10 conditions and three reviewer models from two developers ([Song, 2026, arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). No cross-model condition separated from same-model fresh-session review (CCR) on F1.

## The routing rule

Send code to the generating model in a fresh session. Send prose to a second vendor.

On code artifacts the same-model fresh-session reviewer scored F1 40.7% against 37.2% for the top-tier cross-model reviewer. On documents the ranking inverts and widens: 42.1% for that cross-model reviewer against 24.5%. On documents, the reversal covers every condition, not only the table's four: "all six cross-model conditions (F1 30.1-42.1%) score above all four same-model conditions (17.4-24.5%)" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).

## What a second call buys

Pair the two only when the budget already covers two review calls. One same-model plus one top-tier cross-model review matched 85 of 150 planted errors (56.7%). Two same-model reviews matched 64 of 150 (42.7%). The 14.0pp gain carries a 95% confidence interval of 6.7 to 22.0 and a Holm-adjusted p of .006 ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).

Those figures are "set-level recalls over run 1", not per-session means. The mixed pair also failed to beat two reviews by the top-tier cross-model reviewer. On the 29 artifacts without a failed session it matched 82 of 145 against 76 of 145. That 4.1pp gain has an interval spanning zero (adjusted p=.184). The consequence: the mixed pairing is "not significantly more than two reviews by the top-tier cross-model reviewer, so model difference and reviewer capability are not separated" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).

Three-model union recall reached 58.0% against the two-model union's 56.7%: "In this setting, a third reviewer adds little" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).

## Why it works

Swapping the model changes which errors get found. Swapping the session does not. Sessions of the same model shared 52% to 62% of their findings, while cross-model pairs shared 37% to 46%. Fresh-session review of the generating model overlapped its own same-session review at 59.9%, inside that within-model band. The author draws the line plainly: "we see no clear sign that changing the context alone changes which errors the model finds, whereas changing the model is accompanied by lower overlap" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). Overlap between the two headline reviewers was a Jaccard of 41.2%. Training-data divergence is one of three candidate explanations the author offers, and this design does not establish any of them.

## When this backfires

- A cheap model fills the second slot. The lightweight cross-model reviewer scored F1 24.0% unrestricted and 27.0% with requirements withheld. Both sit under the same-model fresh-session baseline of 28.6%. Per the author, "model independence with a lightweight reviewer shows no clear advantage over baseline self-review" at 27.1% ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).
- You treat a different vendor as statistical independence. Across more than 350 models, "larger and more accurate models have highly correlated errors, even with distinct architectures and providers" ([Kim et al., 2025, arXiv:2506.07962v1](https://arxiv.org/abs/2506.07962v1)). On one leaderboard dataset in that study, "models agree 60% of the time when both models err". The review study concedes the point about its own data: "the observed unions in fact fall below both pooled and within-artifact independence reference values" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).
- Your stack is newer than the reviewer's training data. Of 1,995 cross-model false positives, 187 (9.4%) were classified as model bias. Of those 187, 136 (72.7%) "involved flagging generator-specific features or tools as non-existent" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). The classification was keyword-based and unvalidated.
- The union becomes the safety net. The author's ethics note holds the line: "even our union approach matches only 56.7% of the planted errors under our automated matcher" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)).

## What the evidence will not carry

One single-author preprint, not peer reviewed, built on three earlier preprints by the same author. Each capability tier is represented by one model, so reviewer capability and model identity stay confounded throughout. The union comparison is retrospective, and "the headline pairing is among the higher of the reused run combinations". Every artifact and ground-truth label is in Korean. Because the matcher scores keywords against Korean text, "it may under-credit English-language reviews" ([arXiv:2610.01471v1](https://arxiv.org/abs/2610.01471v1)). That bias runs against the same-model arm, since 20 of 30 same-model fresh-session reviews in run 1 came back in English. Treat the routing rule as a default to test on your own artifacts.

## Key Takeaways

- Route by artifact type: generating model in a fresh session for code, second vendor for prose.
- Pair them only at a two-call budget, for roughly 14 extra percentage points of planted-error coverage.
- A weak second model scored at or below plain self-review, with no clear advantage over it.
- Vendor diversity is not error independence; correlation rises with model accuracy.
- Stop at two reviewers. The third added 1.3 percentage points.

## Related

- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — what the same reasoning does when the second opinion is a panel of judges
- [Distillation-Induced Similarity Metrics for Tool-Use Agents](distillation-induced-similarity-metrics.md) — measuring shared behavior between two models before treating them as independent
- [Choosing the Judge Model That Grades Your Agent Evals](judge-model-bake-off.md) — picking the second model once you know you want one
- [Committee Review Pattern](../code-review/committee-review-pattern.md) — the multi-reviewer structure this result caps at two models
