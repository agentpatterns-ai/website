---
title: "Reading a Harness Comparison Run at One Fixed Model"
term: "Fixed-Model Harness Comparison"
description: "A fixed-model harness score equals the harness ceiling minus that checkpoint's mismatch. Report both terms and count the decisions each harness asks for."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - fixed-model harness comparison
  - frozen harness comparison
  - harness ceiling and mismatch
last_reviewed: 2026-11-01
maturity: emerging
---

# Reading a Harness Comparison Run at One Fixed Model

> A harness score at one fixed model is what the harness offers minus what that model loses, so the score cannot say which moved.

A harness score at a fixed model is a difference of two quantities. The ceiling is the best return the harness offers, and it does not depend on the model's weights. The mismatch is the return one checkpoint gives up by deciding worse than the best play open to it. Under KL-regularized control, deployed return equals ceiling minus mismatch exactly. The paper puts it this way: "The ceiling depends on the harness and the objective, and the mismatch depends on the harness and the checkpoint, including errors inherited from training" ([Mu et al., arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). A weight update moves only the mismatch. A harness change moves both. The paper states: "A frozen comparison of harnesses therefore mixes what each harness offers with how well the current checkpoint uses it."

## What this changes, and what it does not

- Report the two terms separately. The paper's reversals come from further post-training under the candidate harness. It used exact policy gradients on a 2B model in a compiled finite graph. Nine swaps met its entry conditions, and "After adaptation, the seven that raise the ceiling all beat the source pair, and the two that lower it gain nothing" ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). Without that post-training, a high-ceiling harness that your model handles badly keeps scoring badly.
- Estimating the ceiling needs a stronger model. Coding agents have no solvable optimum, so the study substitutes a teacher and states the cost: "The estimates put a teacher that need not be optimal in place of the optimum" ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). The ceiling estimate is then a lower bound. The mismatch estimate measures distance to the teacher. If you have no stronger model to act as teacher, you cannot estimate either term.

## The two terms separate harnesses that one score does not

A frozen Qwen3.5-9B ran the native configurations of five coding-agent harnesses. "With the model fixed, the harness moves Terminal-Bench Lite accuracy from 47.9% to 64.1%". The teacher-based estimate of ceiling minus mismatch reproduces that ordering across all five. Neither term does alone: "Either term alone misorders them" ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)).

| Harness | Decisions per trajectory | Ceiling estimate | Mismatch estimate | Difference | Accuracy (%) |
|---|---|---|---|---|---|
| Terminus-2 | 4.9 | 0.431 | 0.134 | 0.297 | 64.1 ± 5.1 |
| mini-SWE-agent | 8.6 | 0.631 | 0.335 | 0.296 | 59.8 ± 7.8 |
| DeepSeek Harness | 8.6 | 0.590 | 0.382 | 0.208 | 54.7 ± 3.9 |
| Pi coding-agent | 6.6 | 0.383 | 0.206 | 0.177 | 51.3 ± 2.6 |
| DeepAgents | 14.2 | 0.261 | 0.429 | −0.168 | 47.9 ± 3.9 |

The harness offering the most does not win here. mini-SWE-agent carries the highest ceiling estimate at 0.631 and lands second. Terminus-2 leads from a middle ceiling and the smallest mismatch.

Scope the figures before importing the ranking. "Terminal-Bench Lite contains 39 tasks, scored by the official verifier". Each harness got three runs, and the spread is the sample standard deviation across them. The per-state estimates come from three probe tasks ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)).

## Count the decisions the harness asks for

Mismatch is a per-decision loss summed along the model's own trajectory. The number of model calls is therefore a term in the total: "mismatch accumulates along the model's own trajectories, so it grows with the number of decisions a harness asks of the model" ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). One case separates volume from quality. "DeepAgents has a mismatch per decision close to that of Terminus-2, but the evaluated model makes nearly three times as many model calls under it and accumulates the largest mismatch". The counts are 14.2 decisions per trajectory against 4.9.

So ask how many model calls a candidate harness spends per task before asking how good each one is. The study counts summary, sub-agent and retry calls as decisions ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)), which is where a heavier harness adds them.

## Presentation moves the score without moving the right answer

The study isolates the mismatch term by changing only how the task is shown. The actions, dynamics, rewards and reference policy stayed fixed, so every optimal decision provably stayed put.

Reversing the order of the top-level JSON observation fields dropped task success from 85.0% to 19.2%. It also changed the most probable action at 52.0% of states ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). Six presentations ran against the same frozen checkpoint and the same 576 held-out tasks.

| Presentation | Task success (%) |
|---|---|
| Original | 85.0 |
| Reversed observation field order | 19.2 |
| Action menu rendered as a list | 86.0 |
| Three action-code reassignments | 57.1 to 68.2 |

The variants do not point one way. The paper keeps that spread in its own summary: "Reassigning the action codes has a moderate effect, and the list format has a small one." Measure presentation sensitivity on your harness. Do not import a direction or a size. [The Model Preference Fallacy](../fallacies/model-preference-fallacy.md) covers the wider format-sensitivity literature this sits inside.

## Why it works

Under KL-regularized control the optimal policy is a softmax over action scores. Its log odds between two actions recover the score difference its harness induces. A policy trained toward that optimum carries the harness's preferences while holding none of the harness's code. Post-training makes those preferences specific to the training harness: "Under every deployment harness, the checkpoint trained under that harness has the lowest error" ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). The regularized performance-gap identity applied to that induced problem gives return as ceiling minus mismatch. Mismatch is the occupancy-weighted divergence from the optimal policy, accumulated along the deployed policy's own path. The ceiling drops out of any weight update, because it is defined over the best policy the harness admits and not over yours. The confound belongs to that decomposition. That is why the reading applies to a comparison the paper never ran.

## When this backfires

- Near ties stay ties. Terminus-2 and mini-SWE-agent differ by 0.001 in the estimated difference, against a 4.3-point accuracy gap whose spreads are 5.1 and 7.8 points ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). The ordering held across all five, and a margin that size is still not a ranking.
- The probe can cost more than the benchmark. At each recorded state, the probe samples the target 128 times and the teacher 64 times. Harnesses average up to 14.2 decisions per trajectory ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)). Where three more benchmark runs are affordable, they are the cheaper instrument.
- The presentation result is one model on one benchmark. It is a single post-trained Qwen3.5-2B checkpoint on MiniWoB++, and harness sensitivity does not generalize across models. A 432-run study crossing six models with three harness conditions found "harness sensitivity appears non-monotone across the models evaluated, and depends critically on model type (chat vs. reasoning)", and limits its own claims because "each tier is represented by a single model in this study" ([Cho, arXiv:2605.26731v1](https://arxiv.org/abs/2605.26731v1)). Its 2B model was the stable one: Gemma4:e2B "matches strong-open-tier stability at 91.7% across all harnesses".
- A mismatch audit does not travel with the model. Mismatch is defined on a checkpoint, so swapping the backing model invalidates it while leaving the ceiling untouched. Run it again on the model you ship.

## Key Takeaways

- Report the ceiling beside the score, even as a rough teacher-based estimate. This separates a low ceiling from a checkpoint's difficulty using the harness.
- Count model calls per task as part of the comparison. Mismatch is per-decision and cumulative, so a harness can lose on volume at an equal per-decision rate.
- Treat a rejected high-ceiling harness as unresolved rather than refuted, and say so, because resolving it needs post-training you probably cannot run.
- Test your own presentation changes. Reordering observation fields took task success from 85.0% to 19.2% on one frozen 2B checkpoint. Rendering the action menu as a list did not lower success ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)).
- Scope imported rankings to 39 Terminal-Bench Lite tasks, three runs per harness, and three probe tasks. State that a teacher substitutes for an uncomputed optimum ([arXiv:2610.37255v2](https://arxiv.org/abs/2610.37255v2)).

## Related

- [Isometric Harness Ablation](../patterns/agent-design/isometric-harness-ablation.md) — pins the model and removes one subsystem at a time; this page names the two terms the resulting score drop is a difference of
- [Model Rankings Reverse Across Agent Harnesses](../patterns/agent-design/model-rankings-reverse-across-harnesses.md) — the same dependence read with the model as the variable instead of the harness
- [Belief Checks for Agent Harness Changes](harness-change-belief-check.md) — a component-level diff for a harness change that terminal success misses
- [Attempt-Budget Sweep for Harness Changes](attempt-budget-sweep-harness-gains.md) — the other axis along which a harness comparison reverses
- [Model-Set Parity: Reading Harness Efficiency Claims](../patterns/agent-design/model-set-parity-harness-claims.md) — the matching rule for reading somebody else's cross-harness figure
