---
title: "Selective Rewind Summarization: Compress Earlier Turns, Keep Recent Ones Intact"
term: "Selective Rewind Summarization"
description: "Pick a turn, compress everything before it, and leave the recent high-bandwidth context untouched — selective summarization beats blanket compaction when sessions have a clear last-verified milestone."
tags:
  - tool-agnostic
  - context-engineering
  - pattern
last_reviewed: 2026-06-13
maturity: adopted
---

# Selective Rewind Summarization: Compress Earlier Turns, Keep Recent Ones Intact

> A user-chosen cut point compresses earlier turns to a summary while the recent turns stay verbatim — a targeted alternative to whole-session compaction.

Selective rewind summarization splits the session at a chosen turn: everything before the cut becomes an AI-generated summary, while the selected message and everything after it stay verbatim. Claude Code exposes it as "Summarize up to here" and its mirror "Summarize from here" in the Rewind menu ([Checkpointing docs](https://code.claude.com/docs/en/checkpointing)), shipping in v2.1.139+ ([Week 20 digest](https://code.claude.com/docs/en/whats-new/2026-w20)). Blanket compaction summarizes the whole window when a threshold trips, often at the wrong moment. Selective summarization lets you pick where to cut — the part the harness cannot infer.

## Cut at the last verified milestone

The cut point is [the decision](manual-compaction-dumb-zone-mitigation.md), not the keystroke. The right cut is the last verified milestone — a passing test, an accepted PR, a confirmed observation — not the most recent natural break. Cutting at an unverified plan freezes speculation into the summary, and later turns inherit it as a fixed premise.

| Cut here | Result |
|----------|--------|
| Last passing test | Verified state captured; recent debugging stays verbatim |
| Last accepted patch | Confirmed work anchored; current iteration keeps detail |
| Mid-speculation | Speculation fixed as "what we did"; later turns build on it |

## Direction matters: up to vs from here

The two options look symmetric but invert the semantics. `Summarize up to here` compresses everything before the selected message — recent work survives. `Summarize from here` compresses it onward — early context survives. Pick by which side you want to discard:

| Session shape | Direction | Why |
|---------------|-----------|-----|
| Long exploration → focused execution | `Summarize up to here` | Compress the search; keep the build |
| Focused setup → wandering detour | `Summarize from here` | Keep the setup; compress the detour |
| Original instructions matter, recent turns are noise | `Summarize from here` | Initial prompt stays full-fidelity |

Getting the direction wrong is a dominant failure mode — see when this backfires, below.

## Why it works

Attention is computed over every token, so the per-token attention budget shrinks as the window fills ([Anthropic: Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Uniform compaction discards recent working context as forcefully as exploratory turns, yet recent turns hold the agent's current working model. Anthropic warns that "overly aggressive compaction can result in the loss of subtle but critical context whose importance only becomes apparent later" — compress the turns the agent is actively reasoning over and it has to rediscover what it just established.

Selective summarization exploits this asymmetry: heavy compression on old scaffolding, none on recent work — the same reason OPENDEV's adaptive context compaction "progressively reduces older observations" while leaving recent tool outputs intact ([Bui, arxiv 2603.05344](https://arxiv.org/abs/2603.05344)). The operation is non-destructive: both directions leave the original messages in the on-disk transcript, and `Restore conversation` recovers if the cut goes wrong ([Checkpointing docs](https://code.claude.com/docs/en/checkpointing)).

## When this backfires

Selective summarization fails the way blanket compaction does, plus a few ways unique to user-chosen cuts:

- Cut at unverified work: compressing up to a speculative plan freezes speculation as "what we did." Cut only at a milestone you can name as confirmed.
- Early context was load-bearing: turn-1 requirements, an architectural diagram, the error trace that anchored the debugging chain. Compressing these costs more than compressing recent chatter.
- Wrong direction chosen: the two options are mirror operations. Picking the inverse discards what you meant to keep, and the menu does not warn you.
- Repeated cycles compound error: each pass adds lossy compression. A thrice-compressed session stacks three layers on its early context, unrecoverable without `Restore conversation`.
- Forking would have been safer: when early context is irrecoverable-on-loss, `claude --continue --fork-session` preserves it in a parallel session at zero compression cost. Summarize when continuity matters most; fork when early-context fidelity does.
- Implementation bugs: regressions have shipped where the cut went wrong — bug [#42293](https://github.com/anthropics/claude-code/issues/42293) summarized the entire conversation, and [#47987](https://github.com/anthropics/claude-code/issues/47987) dropped pre-rewind messages. Verify the post-cut conversation before continuing high-stakes work.

The strongest counter is the Amp position: skip compaction, keep sessions short, branch when they grow ([Context Compaction Showdown](https://gist.github.com/badlogic/cd2ef65b0697c4dbe2d13fbecb0a0a5f)). That holds when sessions have natural breaks; selective summarization is for sessions that do not — long exploration resolving into focused execution, debugging chains locking onto a root cause.

## Example

A developer spends an hour exploring a bug across twelve source files, four test logs, and three speculative root-cause theories. They finally confirm the issue is a race condition in `PaymentService.process()` and write a passing regression test. Context is at ~70%.

The fix needs the test failure mode, the relevant module, and the recent reasoning — not the twelve exploratory reads or the three discarded theories.

In the Rewind menu, the developer selects the turn where the regression test passed and chooses **Summarize up to here**, with a focus directive:

```
Preserve: the race condition mechanism in PaymentService.process(),
the failing assertion in test_payment_flow.py, and the conclusion
that the fix requires a lock around the balance read.
```

After the cut, context drops to ~20%. The passing-test turn and everything after it stay verbatim; earlier exploration collapses to a summary anchored on the verified mechanism. The fix turn now has a clean, dense context to reason against.

If the developer had run `/compact` instead, the recent reasoning chain — including the passing test details — would have collapsed alongside the exploration, and the fix turn would have to rediscover what the regression test proved.

## Key Takeaways

- Selective summarization compresses one side of a chosen turn; uniform compaction compresses everything indiscriminately.
- The cut point is the decision — pick the last verified milestone, not the most recent natural break.
- `Summarize up to here` preserves recent work; `Summarize from here` preserves early context. Wrong direction discards what you meant to keep.
- Recent turns carry the agent's current working model — preserving them avoids the rediscovery cost that uniform compaction incurs.
- Original messages remain in the session transcript; the cut is non-destructive at the file layer. `Restore conversation` recovers if the cut was wrong.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the broader tiered-compression frame; selective summarization is the user-driven targeted slice.
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — when to compact at all; this page covers where to cut once you decide to.
- [Turn-Level Context Decisions](turn-level-context-decisions.md) — the five-option decision framework (continue, rewind, clear, compact, delegate) that this pattern lives inside.
- [Observation Masking](observation-masking.md) — a complementary primitive: strip intermediate tool results without touching the conversation shape.
- [Goal Recitation](goal-recitation.md) — what to preserve in the summary so the agent does not drift after the cut.
- [Agent-Initiated Rubric-Gated Self-Compaction](agent-initiated-self-compaction.md) — moves the cut decision from the user to the model, gated by a firing rubric instead of a chosen turn.
- [Addressable Recall Compaction](addressable-recall-compaction.md) — keeps the compressed side recoverable by ID instead of accepting the summary as the only record.
