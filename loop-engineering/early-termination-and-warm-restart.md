---
title: "Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)"
term: "FailFast-RestartSmart"
description: "Stop a run that is likely to fail against a calibrated false-positive budget, then restart it with the killed attempt's diff mounted as an optional git overlay instead of discarded."
tags:
  - loop-engineering
  - cost-performance
  - technique
  - tool-agnostic
  - arxiv
aliases:
  - early failure prediction for agents
  - warm restart with diff overlay
  - calibrated early termination
last_reviewed: 2026-08-07
maturity: emerging
---

# Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)

> Stop a doomed agent run against a false-positive-rate budget, then restart it with the killed attempt's diff offered as an optional overlay.

Three conditions gate this technique. Your harness must show a measurable length gap between failing and succeeding runs, because that gap is the signal. You need past runs with known outcomes, because the design knob is a target false-positive rate and labels are what set it. And cost the two halves separately: early termination saves tokens, warm restart spends them.

## Step count is the free tier

Rank active runs by step count, kill the longest, and set the cut wherever your tolerated false-positive rate lands. Wang et al. include exactly this as a supervisor-free Duration control that "scores runs solely using step count, calibrated and thresholded across FPR budgets identically to learned monitors". At a 5% false-positive budget it saves 11.4% of execution tokens on Qwen3.6-27B, 10.9% on Qwen3.5-9B and 10.0% on Gemma4-31B ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)). Nothing to train or serve.

The threshold does not transfer. Failed runs are longer for every code agent measured, but by margins differing sixfold: SWE-agent's are 12.6% longer on SWE-Bench Lite and 18.5% on Verified, OpenHands' 31.0% and 82.5%, Prometheus 56.6% and 50.7% ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)). Calibrate on your own history.

## What a trained monitor buys

FailFast is a Qwen3-0.6B classifier in about 2GB of VRAM. It reads the observable prefix only, within 4,096 tokens: the issue text plus the last eight thought, action and observation steps, with the latest patch-producing step pinned. At the same 5% budget it saves 20.4%, 15.7% and 14.6% on those three policies and 16.0% on a closed-API Gemini 3 Flash, all from one monitor trained solely on Qwen3.6-27B trajectories ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

Read the recall column before deciding the training is worth it.

| False-positive budget | Recall | Precision | Runs stopped | Tokens saved |
|---|---|---|---|---|
| 5% | 30.5% | 76.1% | 13.4% | 20.4% |
| 10% | 45.5% | 69.7% | 21.8% | 28.0% |
| 25% | 68.3% | 58.8% | 38.8% | 49.0% |

Qwen3.6-27B on SWE-bench Verified ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

At a tight budget the monitor catches under a third of failures, and deeper savings come from interrupting more runs that would have passed. Choosing where to sit on that curve is the design work.

## Warm restart spends tokens to buy resolution

RestartSmart launches a fresh same-policy rollout carrying no prior prompt history, then hands over the killed run's edits as a mounted tool rather than as text: "we mount it as a removable, git-apply–backed tool the agent may inspect (diff), apply (on), or revert (off); the overlay starts off" ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

Resolution on Qwen3.6-27B rises from 66.6% to 69.8% at a 10% budget and to 71.8% at 25%, where a cold restart reaches only 67.2% and 66.8%. Net token spend against a plain single run rises 30.3% and 43.8% respectively ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)). Turn this half on to buy resolution rate, never to cut cost.

Which edits get handed over matters too. Extraction replays the aborted run's commands, restricts the captured diff to files that existed at baseline, takes the first edit at or after the abort signal, then cuts after five consecutive edit-free steps. Letting the edits settle is worth 5.2 resolution points against 2.2 for cutting at the abort signal ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

## Why it works

Failure is observable before the run ends. Failing runs re-explore and loop, so they run longer ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)). Step count is a real but weak proxy for it, which is why the trained monitor adds a dense fail-to-pass target: replay the commands, score intermediate patches with the official evaluator, and "how long has this been running" becomes "is this patch making failing tests pass" ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

The restart half splits what a failed run leaves behind into two parts of opposite value. Accumulated context anchors the next attempt: a model reproduces a near-identical program in 33-68% of retries once it sees its own failed code, against 2-14% under blind resampling ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)). The diff carries no such penalty and may be partly correct. A fresh rollout drops the context; an overlay that starts off keeps the diff out of the prompt.

## When this backfires

- Your harness has a tight length distribution. The duration control has nothing to separate on, and a borrowed step cap is uncalibrated when the gap spans 12.6% to 82.5% across frameworks ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)).
- No labeled trajectory history. A false-positive budget cannot be expressed, let alone hit, without past runs whose outcomes are known.
- Cost is the binding constraint and you enable the restart. The combined system spends 30.3% to 43.8% more than a plain run ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)), undoing the reason you stopped early.
- A developer is waiting on the run. At a 25% budget the alarm fires on 38.8% of runs at 58.8% precision, so roughly two in five interruptions are wrong ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)). That is a batch-fleet trade.
- The killed run's work was in new files. Overlay extraction excludes newly created files ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)), so the restart degrades to cold.
- The monitor is an LLM judge. Per-round judging dominates the cost it is meant to save: a judge-free semantic stopper cut operational tokens 38% at parity quality on HotpotQA while the quality-gated variant was counter-productive ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)). Keep the monitor cheap relative to the policy it watches: FailFast's is 0.6B against 27B ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).
- The authors' own bound: "Our evaluation is limited to SWE-bench Verified with mini-swe-agent, so the findings may not generalize to other software engineering tasks or agent frameworks" ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).

Two findings argue against the design rather than the goal. Hidden-state linear probes predict failure from the first interaction round, "substantially earlier than agent-monitoring methods based only on observable behavior", and adding behavioral features to them "provides no further gain" ([Ruan et al., 2026](https://arxiv.org/abs/2607.06503v2)). The observable-prefix-only design that lets one monitor transfer to a closed API is the same choice that caps its ceiling. Shrivastava separately reports an oracle round-selector beating every practical stopping policy by 0.115 Information Score, "reframing the problem from 'when to stop' (easy) to 'which round is best' (open)" ([Shrivastava, 2026](https://arxiv.org/abs/2606.27009v1)).

## Example

The overlay interface is the transferable engineering detail. A restarted run sees four commands and no prompt text describing its predecessor's edits:

```text
overlay status   # is the prior diff applied?  (starts off)
overlay diff     # inspect the killed attempt's edits
overlay on       # git-apply the diff into the working tree
overlay off      # revert it
```

The restart prompt says only that an earlier attempt was stopped because it looked unlikely to finish, and that its edits "may be a correct fix, an incomplete fix, or a wrong direction — do NOT assume they are right" ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)). None of those edits enter context unless the agent runs `overlay diff`. Splicing the same diff into the restart prompt would deliver the artifact and the anchoring cost together.

## Key Takeaways

- Calibrate the threshold on your own trajectory history. The failed-versus-successful length gap ranges from 12.6% to 82.5% across code agents ([Majgaonkar et al., 2025](https://arxiv.org/abs/2511.00197v1)), so a published step cap transfers nothing.
- Start with step count alone: about 10-11% token savings at a 5% false-positive budget, with no model to train or serve ([Wang et al., 2026](https://arxiv.org/abs/2608.03222v1)).
- A 0.6B observable-prefix monitor roughly doubles that to 14.6-20.4%, and one trained on a single policy transfers to three others including a closed API.
- Pick the false-positive budget before picking a detector. At 5% the monitor catches 30.5% of failures; at 25% it catches 68.3% but stops 38.8% of all runs at 58.8% precision.
- Cost the halves separately: early termination saves tokens, warm restart spends 30.3-43.8% more to buy 3.2-5.2 resolution points.
- Mount the prior diff as a git-backed tool that starts off, never as prompt text, and wait five edit-free steps before extracting it.

## Related

- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](loop-budgeting.md) — the static caps this replaces with a predicted stop; read it first for choosing the budget primitive at all
- [Blind Resampling Over Self-Repair in Small Code Models](blind-resampling-over-self-repair.md) — the anchoring cost the overlay design exists to avoid, and the opposite answer at function scale
- [Stuck-Loop Recovery: Detecting and Escaping Non-Converging Agent Loops](stuck-loop-recovery.md) — the in-place recovery ladder to climb before reaching for a kill-and-restart
- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — stopping a healthy loop on diminishing returns, the mirror of predicting a doomed one
- [Within-Task Model Cascade: Designing the Escalation Gate](within-task-model-cascade.md) — the same false-accept-rate arithmetic applied to a cheap-model gate
