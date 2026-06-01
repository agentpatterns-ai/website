---
title: "Selective Rewind Summarization: Compress Earlier Turns, Keep Recent Ones Intact"
description: "Pick a turn, compress everything before it, and leave the recent high-bandwidth context untouched — selective summarization beats blanket compaction when sessions have a clear last-verified milestone."
tags:
  - tool-agnostic
  - context-engineering
  - pattern
last_reviewed: 2026-05-30
---

# Selective Rewind Summarization: Compress Earlier Turns, Keep Recent Ones Intact

> A user-chosen cut point compresses earlier turns to a summary while the recent turns stay verbatim — a targeted alternative to whole-session compaction.

Selective rewind summarization splits the session at a specific turn: the portion before the cut becomes an AI-generated summary, while the selected message and everything after it stay in full detail. Claude Code exposes it as "Summarize up to here" in the Rewind menu, paired with its mirror "Summarize from here" ([Checkpointing docs](https://code.claude.com/docs/en/checkpointing)), both shipping in v2.1.139+ ([Week 20 digest, May 11–15 2026](https://code.claude.com/docs/en/whats-new/2026-w20)).

The pattern matters because blanket compaction summarises the whole window when a threshold trips, often at the wrong moment. Selective summarization lets the practitioner pick *where* to cut — the part the harness cannot infer.

## Cut at the Last Verified Milestone

The cut point is the decision, not the keystroke. The right cut is the last *verified* milestone — a passing test, an accepted PR, a confirmed observation — not just the most recent natural break. Cutting at an unverified plan freezes speculation into the summary, and subsequent turns inherit the unchecked assumption as a fixed premise.

| Cut here | Result |
|----------|--------|
| Last passing test | Verified state captured; recent debugging stays verbatim |
| Last accepted patch | Confirmed work anchored; current iteration keeps full detail |
| Last reviewed plan | Approved approach captured; execution context stays intact |
| Mid-speculation | Speculation fixed as "what we did"; subsequent turns build on unchecked premise |
| Arbitrary "long enough" point | Early context may have been load-bearing; recent exploration may be discardable |

## Direction Matters: Up To vs From Here

The two options look symmetric in the menu but invert the semantics. `Summarize up to here` compresses everything *before* the selected message — recent work survives. `Summarize from here` compresses the selected message *onward* — early context survives ([Checkpointing docs](https://code.claude.com/docs/en/checkpointing)).

Pick by which side is the side you want to discard:

| Session shape | Direction | Why |
|---------------|-----------|-----|
| Long exploration → focused execution | `Summarize up to here` at the execution start | Compress the search; preserve the build |
| Focused setup → wandering side discussion | `Summarize from here` at the side-quest start | Preserve the setup; compress the detour |
| Original instructions matter, recent turns are noise | `Summarize from here` | Initial prompt stays full-fidelity |
| Setup is verbose scaffolding, recent turns are the live problem | `Summarize up to here` | Recent debugging keeps every error string |

Getting the direction wrong is one of the dominant failure modes — see *When This Backfires*.

## Why It Works

Transformer attention is computed over every token in the window, so the model's effective per-token attention budget shrinks as the window fills ([Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Uniform compaction discards exploratory turns and the recent high-bandwidth working context with equal force, but recent turns are where the agent's current working model lives. Aggressive summarization of recent context is "particularly damaging because… the most recent context (containing just-accumulated insights) is heavily compressed, forcing the agent to rediscover context in subsequent turns" ([Parallel Context Compaction, arxiv 2605.23296](https://arxiv.org/abs/2605.23296)).

Selective summarization exploits this asymmetry deliberately: heavy compression on old scaffolding, none on recent work. The same shape appears in production agents — Bui (2026) §2.3.6 keeps "recent tool outputs at full fidelity" in OPENDEV's Adaptive Context Compaction precisely because newer signal is denser per token ([Building AI Coding Agents for the Terminal, arxiv 2603.05344](https://arxiv.org/abs/2603.05344)). What Claude Code adds is moving the cut from a fixed window into the user's hands — the practitioner usually knows where the verified milestone is, and the harness does not.

## Original Messages Stay Recoverable

Both directions leave the original messages in the session transcript on disk; the model just stops seeing them in-context ([Checkpointing docs](https://code.claude.com/docs/en/checkpointing)). This makes the operation non-destructive at the file layer — if the cut goes wrong, `Restore conversation` can recover. The compression is in working memory, not in the durable record.

## When This Backfires

Selective summarization fails the same way blanket compaction does, plus a few new ways unique to user-chosen cuts:

- **Cut at unverified work**: Compressing up to a speculative plan freezes speculation as "what we did." Always cut at a milestone you can name as confirmed.
- **Early context was the load-bearing context**: Requirements pasted at turn 1, an architectural diagram, the original error trace that anchored the debugging chain. Compressing this away costs more than compressing recent exploratory chatter.
- **Wrong direction chosen**: `Summarize up to here` and `Summarize from here` are mirror operations; picking the inverse discards what you meant to keep. The menu does not warn you.
- **Repeated cycles compound error**: Each summarisation adds error. A session compressed three times has three layers of lossy compression on its early context — in-context detail is unrecoverable without a manual `Restore conversation` ([Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) warns that "overly aggressive compaction can result in the loss of subtle but critical context whose importance only becomes apparent later").
- **Forking would have been safer**: When the early context is genuinely irrecoverable-on-loss, `claude --continue --fork-session` preserves it in a parallel session at zero compression cost. Selective summarization is the right primitive when continuity matters more than perfect early-context fidelity; forking is the right primitive when it does not.
- **Implementation bugs**: Real regressions have shipped where the cut went wrong. Bug [#42293](https://github.com/anthropics/claude-code/issues/42293) summarised the *entire* conversation instead of one side; bug [#47987](https://github.com/anthropics/claude-code/issues/47987) dropped pre-rewind messages entirely on certain versions. Verify the post-cut conversation contains what you expect before continuing high-stakes work.

The strongest counter to the pattern is the Amp position: skip compaction entirely, keep sessions short, branch when they grow ([Context Compaction Showdown](https://gist.github.com/badlogic/cd2ef65b0697c4dbe2d13fbecb0a0a5f)). That argument holds when sessions have natural breaking points; selective summarization is for sessions where they do not — long exploration that resolves into focused execution, debugging chains that finally lock onto a root cause.

## Example

A developer spends an hour exploring a bug across twelve source files, four test logs, and three speculative root-cause theories. They finally confirm the issue is a race condition in `PaymentService.process()` and write a passing regression test. Context is at ~70%.

The next task is the fix itself, which needs the test failure mode, the relevant module, and the recent reasoning — but not the twelve exploratory file reads or the three discarded theories.

In the Rewind menu, the developer selects the turn where the regression test passed and chooses **Summarize up to here**, with a focus directive:

```
Preserve: the race condition mechanism in PaymentService.process(),
the failing assertion in test_payment_flow.py, and the conclusion
that the fix requires a lock around the balance read.
```

After the cut, context drops to ~20%. The selected turn (the passing test) and everything after it remain verbatim. Earlier exploration collapses to a summary anchored on the verified mechanism. The fix turn that follows has a clean, dense context to reason against.

If the developer had run `/compact` instead, the recent reasoning chain — including the passing test details — would have collapsed alongside the exploration, and the fix turn would have to rediscover what the regression test proved.

## Key Takeaways

- Selective summarization compresses one side of a chosen turn; uniform compaction compresses everything indiscriminately.
- The cut point is the decision — pick the last *verified* milestone, not the most recent natural break.
- `Summarize up to here` preserves recent work; `Summarize from here` preserves early context. Wrong direction discards what you meant to keep.
- Recent turns carry the agent's current working model — preserving them avoids the rediscovery cost that uniform compaction incurs.
- Original messages remain in the session transcript; the cut is non-destructive at the file layer. `Restore conversation` recovers if the cut was wrong.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the broader tiered-compression frame; selective summarization is the user-driven targeted slice.
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — when to compact at all; this page covers where to cut once you decide to.
- [Turn-Level Context Decisions](turn-level-context-decisions.md) — the five-option decision framework (continue, rewind, clear, compact, delegate) that this pattern lives inside.
- [Observation Masking](observation-masking.md) — a complementary primitive: strip intermediate tool results without touching the conversation shape.
- [Goal Recitation](goal-recitation.md) — what to preserve in the summary so the agent does not drift after the cut.
