---
title: "Line-Anchored Feedback: Deliver Change Requests as Inline Comments"
term: "Line-Anchored Feedback"
description: "Delivering code-change requests as line-anchored inline comments instead of one holistic prompt cuts edit tokens on large files and can raise correctness — under specific conditions."
aliases:
  - inline-comment feedback
  - anchored change requests
tags:
  - token-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-07-16
maturity: emerging
---

# Line-Anchored Feedback: Deliver Change Requests as Inline Comments

> Delivering change requests as line-anchored inline comments, not one holistic prompt, cuts edit tokens on large files — where the model emits valid edit blocks.

The format you use to request a code change is itself a cost lever. Delivering the same set of edits as structured, line-anchored inline comments rather than one holistic prompt cut generated tokens 22% on Claude Opus and 58% on Claude Sonnet in a paired experiment, and raised correctness for models that had headroom to improve ([Line-Anchored Feedback, arxiv 2607.12713](https://arxiv.org/abs/2607.12713v1)). The model and the task are held fixed — only the feedback format changes.

## When it pays off

The win is real but conditional. Reach for line-anchored feedback when all three hold:

- The file is large. On files of 100 lines or more, Sonnet saved 75-80% of tokens per size tier and Opus 24-38%; the median across all seven tested models on 100-500 line files was roughly 60% ([arxiv 2607.12713](https://arxiv.org/abs/2607.12713v1)). On small files both formats saturate and the benefit disappears.
- The model can emit valid edit blocks. Line anchoring rides on a targeted-edit output contract (SEARCH/REPLACE-style blocks). A model that cannot produce them reliably pays a penalty instead: two of the seven models generated significantly more tokens under anchoring ([arxiv 2607.12713](https://arxiv.org/abs/2607.12713)).
- You know which axis has headroom. The gain lands wherever the model has room: frontier models near the correctness ceiling become cheaper, weaker models become more correct.

## How to apply it

Deliver each requested change as an inline comment anchored to the specific line, quoting the source text it refers to, and export the whole set as structured markdown — the shape a code reviewer leaves on a pull request. In the study this was FileMark, a VSCodium extension that exports inline comments on any file; both arms drew from an identical change set, so the content was constant and only the anchoring differed ([arxiv 2607.12713](https://arxiv.org/abs/2607.12713)). Any harness that lets you attach comments to line ranges and hand the model that structured export gets the same effect.

## Why it works

Line anchors shrink the model's search space. On a large file, finding which lines to change is genuinely hard, so a model handed only a holistic prompt hedges by regenerating large spans, often the whole file, to be safe. Telling it exactly where to edit licenses a small, targeted edit instead, which is where the token saving comes from ([arxiv 2607.12713](https://arxiv.org/abs/2607.12713v1)). The same localization removes silent "runs but produces the wrong result" failures in weaker models by pointing them at the right region: for one model that failure rate dropped from 7.3% to zero. So the benefit follows whichever dimension has slack.

## When this backfires

- Small files. Locating the change is trivial and both formats already saturate, so anchoring adds structure the model does not need without a token or correctness payoff.
- Models weak at the edit-block contract. Line anchoring is strictly worse when the model cannot emit valid blocks — the study saw regressions of +6% and +30.9% tokens on two local models, and three local models essentially never produced valid blocks on the largest files ([arxiv 2607.12713](https://arxiv.org/abs/2607.12713v1)). The contract is a capability gate, not free.
- Correctness-critical work on a near-ceiling model. Terse anchored edits can apply cleanly yet fail validation: Claude Sonnet traded 4.5 points of correctness for its 75-80% token saving. When accuracy outranks cost, the holistic delivery can be the right call.
- Real, evolved codebases. The evidence is synthetic, single-shot base-R tasks; diff-match accuracy on real evolved code sits nearer 70-80% ([Morph — diff format](https://www.morphllm.com/edit-formats/diff-format-explained)), and a fixed localized format is not always optimal — adaptive selection between targeted edits and whole-file rewrites can beat either fixed choice ([arxiv 2604.27296](https://arxiv.org/html/2604.27296)).

## Example

The same request, delivered two ways. A holistic prompt (control) hands the model the whole task at once:

```
Fix the bugs in utils.R: the running total starts at 1 instead of 0,
the filter keeps inactive users, and the date parser assumes US format.
```

Line-anchored comments (treatment) carry the same three changes, each tied to the line it touches:

```
L12  total <- 1    — should start at 0
L27  keep(users)   — drops the is_active check; keep only active users
L44  as.Date(x)    — assumes US MDY, but the input is ISO YYYY-MM-DD
```

The content is identical; only the second tells the model where each edit lands, so it patches those lines instead of scanning the file to locate them — the localization the token saving comes from.

## Key Takeaways

- Feedback format is a token lever independent of the model: line-anchored comments cut edits 22-58% on frontier models.
- The win concentrates on files of 100+ lines; small files show no benefit.
- The gain follows headroom — capable models get cheaper, weaker ones get more correct.
- It rides on a valid edit-block contract; models that cannot emit one get more expensive, and terse edits can trade away correctness.

## Related

- [Token-Efficient Code Generation: Structural Beats Prompting](token-efficient-code-generation.md) — the sibling output-token lever, on the code the model writes rather than the feedback you give
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — route by complexity and headroom, the same "spend where it pays" logic
- [Cost-Quality Pareto Measurement](cost-quality-pareto-measurement.md) — plot the cost-versus-correctness trade-off so a Sonnet-style accuracy loss is visible
- [Token Preservation Backfire](../patterns/anti-patterns/token-preservation-backfire.md) — the guardrail: cutting tokens can degrade output, so measure the correctness side
- [Harness-Controlled Token Economics](harness-token-economics.md) — how the surrounding harness, not just the model, sets token volume
