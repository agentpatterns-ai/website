---
title: "Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)"
term: "Half-Life Truncation"
description: "Mechanically shortening older tool results as the window fills raises coding-agent fix rates under a tight context window, and converges with the untouched transcript on two of three benchmarks once the window is wide."
aliases:
  - half-life truncation
  - age-tiered tool result truncation
  - pressure-gated tool result truncation
tags:
  - context-engineering
  - agent-design
  - arxiv
  - tool-agnostic
last_reviewed: 2026-08-29
maturity: emerging
status: current
---

# Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)

> Shortening older tool results lifts coding-agent fix rates under a tight context window; widen the window and two of three benchmarks converged.

Adopt this only if your agent runs are ending because the transcript filled the window. That precondition is the whole finding. A harness A/B at a fixed model raised mean per-task fail-to-pass fraction on SWE-bench Verified "from 28% to 49% and complete solutions from 43 to 72" under a 20,480-token window across 169 tasks ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)). The same frozen treatment, run at 262,144 tokens, produced a Verified difference of -0.3 percentage points with a 95% confidence interval of [-4.5, +3.9].

## Confirm the window is the bottleneck

Count how many runs end with a full context rather than a finished task. The paper's diagnostic is the reading boundary, the point at which half the trajectories stop while still reading: "on every benchmark, treatment moved this boundary to more than twice the control location" ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)). If your runs already reach an answer and stop there, moving that boundary buys nothing, and [context-window diagnostic tooling](context-window-diagnostic-tooling.md) will tell you which tool calls are filling the window.

## The policy

The treatment is mechanical, with no model call in the loop. Three parameters, all as reported in [Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1):

| Parameter | Setting in the study |
|---|---|
| Activation point | Shortening starts once the estimated full prompt reaches half the configured window |
| Protected results | "The newest four tool results remain full" |
| Age tiers | Older results keep their beginning and end inside a printed cap; the cap halves as age doubles |

The in-memory result stays complete, so only the printed prompt shrinks. In the three tight-window arms this removed 45.2%, 55.7% and 64.4% of characters, first activating at a median turn of 9 to 13. A second component reads the execution record rather than the transcript: when a command repeats with an identical error, the harness injects a message naming the repetition. On the 20,480-token Verified cohort the detector fired 45 times across 31 sessions, and the conditioned action applied 56 times ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)).

The other two tight-window arms move the same way. SWE-bench Pro went from 15% to 33% mean per-task fail-to-pass fraction at a 49,152-token window, FeatureBench from 11% to 20% at 47,104 tokens, both p<0.0001 on the direction sign test. It transferred without tuning: "the same frozen treatment also raises both endpoints on the same cohort for three additional models with different designs" ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)).

## Why it works

Truncation does not make the model reason better. It stops the run from ending. The paper's causal claim is that "long coding tasks accumulate full files, search results, command output, and repeated tests, so that history competes with the new evidence needed for the next decision" ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)). Freeing space buys more turns before forced termination, which is what the doubled reading boundary measures. That also predicts the wide-window null: with no run dying on length, there is no termination to postpone.

One thing does survive the wide window. At 262,144 tokens the treatment served 7.2% fewer prompt tokens per turn on Verified, a geometric mean ratio of 0.928 with a 95% CI of [0.878, 0.979], at 1.4% more turns ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)). Decide that on serving cost, not on score.

## When this backfires

- A window already wide relative to the transcript. Verified complete solutions came out at 102 versus 101, and Pro was similarly close; FeatureBench kept a gain, 23.9% to 30.7%, but only on one of two tests — "The primary task-paired sign test gives p=0.00022, while the repository-level direction sign test gives p=0.0963" — and that row "pairs an earlier treatment with a later corrected control", making it a historical comparison rather than an exact replication ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)). The null is not universal, but two of three benchmarks showed nothing.
- A late step that needs an old tool result verbatim. The policy keeps the head and tail and drops the middle, so a long file read consulted at the end comes back with a hole the run cannot recover.
- Compression causing the repetition the stall detector patches. Recurrent context compression "can weaken the influence of recent interactions, increasing blocked actions, repeated exploration, and instability across runs" ([Min et al., arXiv:2608.06503v1](https://arxiv.org/abs/2608.06503v1)). The study ships truncation and the detector together and never runs truncation alone, so their contributions are confounded.
- Bulk material that could live on disk instead. Coding agents that put long material in the file system and read it with their own tools beat published state of the art by 17.3% on average ([Cao et al., arXiv:2603.20432v1](https://arxiv.org/abs/2603.20432v1)). A pointer costs little to keep, so there is nothing to truncate.
- An evidence base narrower than the recommendation. Four open-weight models, the primary one quantized to four bits, on repository-level tasks scored by tests, one greedy trajectory per task per arm. Run-to-run variance went unmeasured and hosted frontier models untested. Effects vary by pairing: across 5,194 trajectories, Harness-Bench found "substantial variation in completion, process quality, efficiency, and failure behavior across model-harness pairings" ([Yao et al., arXiv:2605.27922v1](https://arxiv.org/abs/2605.27922v1)).

This sits awkwardly beside the usual advice to compact rather than truncate, covered in [reasoning retention and compaction](reasoning-retention-and-compaction.md). That advice targets harnesses that delete whole old messages. Half-life truncation deletes no message and no recent result; it shortens the middle of stale tool output while keeping the four newest results intact.

## Example

The two prompt shapes the study compared, at the same point in the same run ([Lewis, arXiv:2608.26218v1](https://arxiv.org/abs/2608.26218v1)):

**Before** — control, full conversation in time order:

```text
turn 24:  [system] + [tool result 1 .. 23, each printed in full] + [latest result]
          estimated prompt exceeds the 20,480-token window
          -> run terminates while still reading
```

**After** — treatment, half-life truncation active:

```text
turn 24:  [system]
          + [results 1 .. 19: head and tail only, cap halving as age doubles]
          + [results 20 .. 23: printed in full]
          + [latest result]
          45-65% of characters removed from the printed prompt
          -> run continues; in-memory results stay complete
```

The model, the tools, and the task are identical across the two shapes. Only what the harness prints into the prompt differs.

## Key Takeaways

- Measure the reading boundary before adopting anything: if runs are not dying on window length, this policy has no measured benefit.
- Three knobs carry the policy: activate at half the window, keep the newest four tool results whole, halve the character cap as result age doubles.
- Run the two components separately if you adopt them. The study never isolated truncation from the stall detector, so you cannot tell from it which one you need.
- Treat the 7.2% wide-window token saving as a serving-cost decision, priced against the engineering time the policy costs to build and debug.
- Record the window size alongside any agent score you report. Two numbers 21 points apart came from the same weights on the same 169 tasks.

## Related

- [Observation Masking](observation-masking.md) — strips a tool result entirely once used, where half-life truncation shortens it by age
- [Reasoning Retention and Compaction as Harness Settings](reasoning-retention-and-compaction.md) — the compaction-over-truncation position this study complicates
- [Per-Type Retention Policy for Agent Compaction](per-type-retention-under-compaction.md) — retention fidelity set by content type rather than by age
- [Addressable Recall Compaction](addressable-recall-compaction.md) — keeping the full observation addressable so a truncated view stays recoverable
- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md) — finding which tool calls fill the window before choosing a policy
