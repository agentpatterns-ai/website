---
title: "The First Edit Predicts Whether an AI Completion Survives"
description: "In 53.6K in-IDE edits, developers who open by customizing an AI completion abandon it 23% of the time against 12% for those who change functionality first — a signal, not a rule to bin near-misses."
tags:
  - human-factors
  - workflows
  - tool-agnostic
  - arxiv
aliases:
  - AI completion abandonment signal
  - customize-first editing
  - developer edits of AI-generated code
last_reviewed: 2026-09-15
maturity: emerging
---

# The First Edit Predicts Whether an AI Completion Survives

> Developers who open by customizing an AI completion abandon it 23% of the time, against 12% for those who change its functionality first.

Renaming a completion's variables and adjusting its literals is the opening move most associated with discarding the whole thing later ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)). Fixing an error in it, or changing what it does, is not.

## What the evidence covers, and what it does not

This comes from DECODE, 53,614 before-after code pairs across 5,831 edit trajectories from 1,141 developers, collected by a VS Code extension that snapshots the working file whenever the developer pauses for one second ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)). Four conditions bound it:

- Inline completions, not agent diffs. The median completion is 97 characters, 9 lines ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)).
- Python, JavaScript and TypeScript only.
- Accepted completions only. The authors state DECODE "only includes edits to accepted AI-generated code", excluding "rejected completions, human-written code, and code obtained from outside the VS Code extension" ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)).
- No cost is measured on either branch. The study never times rewriting against repairing. Read what follows as a diagnostic signal, not as a recommendation to discard near-misses.

## The signal

Developers who first try to customize a completion, meaning they rename variables or change parameters and literals without altering behavior, go on to remove it 23% of the time. A first quality fix leads to removal 14% of the time, a first functionality change 12% ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)).

Removal edits also arrive earliest, at a mean of 23.6 minutes after acceptance, quality edits at 28.3, customizing at 49.3 and functionality changes at 59.2, with the ordering significant under a Kruskal-Wallis test (H=394.5, p<0.001) ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)). A second 23% appears in the same analysis measuring something else: that share of trajectories removes the completion on the very first edit, and 40% of those then change functionality, which the authors read as developers writing their own implementation instead ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)).

None of this is model-specific. Across the 20 models in the dataset the differences in editing behavior reach statistical significance but the effect sizes are small, at eta-squared 0.002 and 0.007 and Cramer's V 0.05 ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)).

That makes it a prompt, not a rule. When your first instinct is to rename and re-parameterize rather than fix or extend, make the keep-or-discard call then, not after the customizing work is done.

## Why it works

A median 63% of the original completion survives, but the distribution is bimodal: "for a majority of the time, AI-generated code is either accepted with few modifications or almost completely removed" ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)). There is not much of a middle to converge on, so the question is which mode you are in.

The edit types sort you into a mode because they diagnose different faults. A visibly broken completion gets a quality fix. One that needs different behavior gets a functionality change. Both are faults you can see. Customizing is what you reach for when the completion looks right and is off on intent, and that is the case the authors single out: "This suggests that AI completions that subtly do not align with a developer's intent or programming context are difficult for developers to adapt" ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)). The paper names the missing quantity as editability, how readily code adapts when it is not immediately usable, and says no good metric for it exists.

## When this backfires

- On agent output. A 9-line completion and a 40-file agent change are not the same decision, and nothing here was measured on the latter.
- When you accepted the completion because you did not know the API. Customizing is how you learn the call, and writing it yourself is not an option.
- When correctness is invisible to edit distance. Every retention metric in the study is Levenshtein-based ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)), so a semantically wrong completion needing a one-character fix scores as fully retained.
- As a ritual on every suggestion. A median 63% of completions survive and 56% of all edit snapshots are functionality changes ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2)), so keeping and editing is the common outcome. A keep-or-discard checkpoint on each one taxes the common case to catch a minority.
- As evidence that rewriting is faster. Developers who customize first abandon more often, and the study cannot say whether starting over would have finished sooner. They may have been customizing completions that were already marginal.

## Key Takeaways

- Customize-first is the highest-abandonment opening move at 23%, against 14% for quality fixes and 12% for functionality changes ([Liang et al., 2026](https://arxiv.org/abs/2607.25130v2))
- Retention is bimodal, so there is little middle ground to converge on and the useful question is which mode a completion is already in
- Removal decisions already cluster early, at a mean of 23.6 minutes against 59.2 for functionality edits, so the keep-or-discard call is one developers make up front whether or not they name it
- The behavior holds across 20 models with small effect sizes, so switching models is not the lever
- The study measures no cost on either branch and excludes rejected completions, so it bounds what the signal can be used for: deciding sooner, not deciding to rewrite

## Related

- [LLM Refactoring Adoption Patterns](llm-refactoring-adoption-patterns.md) — five patterns for modifying chat-initiated refactors, the channel that page scopes itself to and this one does not
- [Suggestion Gating](suggestion-gating.md) — the other side of the accept decision, where a classifier filters completions before they are shown
- [Blind Resampling Over Self-Repair in Small Code Models](../loop-engineering/blind-resampling-over-self-repair.md) — the model-side analogue on benchmark data, where discarding beats repairing below roughly 7B
- [Developer Control Strategies for AI Coding Agents](developer-control-strategies-ai-agents.md) — how experienced developers supervise and validate AI output more broadly
