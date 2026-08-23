---
title: "Blind Resampling Over Self-Repair in Small Code Models"
term: "Blind Resampling"
description: "Below about 7B parameters, discarding a failed program and resampling from the original prompt beats handing the failure back for repair — on accuracy and on tokens."
tags:
  - loop-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - blind resampling retry
  - resample instead of repair
last_reviewed: 2026-08-02
maturity: emerging
---

# Blind Resampling Over Self-Repair in Small Code Models

> Below 7B, discarding a failed program and resampling from the original prompt beats returning the failure to the model for repair.

Three conditions gate this technique: a model under roughly 7B parameters, a self-contained function as the unit of work, and a real test deciding pass or fail on every attempt. Inside that box, throwing the failed program away wins on accuracy and on tokens. Outside it, a conventional repair loop stays the better default.

The usual evaluation hides the effect. Self-repair returns a failed program to the model with its test output and asks for a correction. It is almost always measured against a single attempt with no retry. That comparison confounds the value of the feedback with the value of getting another draw at all ([Verma, 2026](https://arxiv.org/abs/2607.26117)). A matched-budget design separates the two. On MBPP+ with Qwen2.5-Coder at Q4_K_M quantization, four arms each get eight attempts: blind resampling from the original prompt, a content-free notice that the program was wrong, execution feedback, and feedback plus written self-reflection.

| Model | Resample | Placebo | Feedback | Reflect |
|-------|----------|---------|----------|---------|
| 1.5B | 0.749 | 0.688 | 0.688 | 0.688 |
| 3B | 0.778 | 0.709 | 0.735 | 0.743 |
| 7B | 0.820 | 0.802 | 0.810 | 0.828 |

pass@1 on MBPP+ at k=8 with Wilson intervals ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)).

Blind resampling leads the placebo arm by 6.1 points at 1.5B (p=0.006) and 6.9 points at 3B (p<0.001). Against the best repair arm at each scale the margin is 6.1 and 3.5 points. The result replicates on DeepSeek-Coder. At 7B the arms converge to a statistical tie, which the study treats as a transitional point rather than a ceiling ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)).

Cost points the same way. Output tokens at eight iterations run 63k, 76k and 49k for blind resampling, against 345k, 284k and 122k for reflection. That is 2.5 to 5.5 times more for no significant gain below 7B ([Verma, 2026](https://arxiv.org/abs/2607.26117)).

Two knobs follow. Keep the retry budget low: 46 to 53% of attainable gain lands by the second iteration, so k≈2 is a defensible start ([Bounded Repair-Loop Iterations](../verification/bounded-repair-loop-iterations.md) covers the general case). And price execution feedback as a costed resource, not a free default ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)).

## Why it works

Conditioning on a failed program collapses the model's exploration instead of informing it. With the previous attempt in context, the next sample re-treads it. Inter-attempt similarity rises by 0.30 to 0.38, and near-identical retries climb from 2–14% under blind resampling to 33–68% ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)). A retry only helps when attempts are diverse enough to reach a different solution branch, so reproducing the same program is a wasted draw.

The placebo arm shows this is exposure, not bad information. A content-free notice that the program was incorrect costs as much accuracy as genuine execution feedback. The feedback-minus-placebo gap is statistically null at all three scales. Severity tracks how bad the anchor is: the penalty is predicted by baseline model quality alone at r=+0.96 across six configurations ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)). A weaker model commits to a worse first attempt and pays more for staying near it. An independent preregistered study agrees from the training side: an error-content adapter ties its intervention-free baseline 8–8 (p=1.0), so fine-tuning does not rescue error conditioning at this scale ([Iscan, 2026](https://arxiv.org/abs/2607.12962v1)).

## When this backfires

- The model is at or above roughly 7B. The gap already closes at 7B, and the anchoring penalty shrinks as baseline quality rises ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)). At frontier scale the matched-budget picture is mixed, not inverted. GPT-4 beats its no-repair baseline by up to 8% on APPS at an equivalent budget, while GPT-3.5's gains are limited: up to 3% on HumanEval as it nears the ceiling, and marginal on APPS only at the largest sample counts. Once repair cost is priced in, those gains are "often modest, vary significantly between subsets of the data, and are sometimes not present at all" ([Olausson et al., 2024](https://arxiv.org/abs/2306.09896)). Do not carry the sub-7B result over to Claude Code, Copilot, or Cursor on a frontier model.
- The task is larger than a self-contained function. The finding is bounded to function-level synthesis on MBPP+ and HumanEval+ ([Verma, 2026](https://arxiv.org/abs/2607.26117)); discarding a mostly-correct multi-file patch costs more than the anchoring it avoids.
- The original prompt cannot reproduce the attempt. When an attempt depended on accumulated repo context or prior tool calls, there is nothing to resample from.
- No real oracle sits in the loop. Every arm relies on differential testing to accept or reject each candidate ([Verma, 2026](https://arxiv.org/abs/2607.26117)). Without a test that can reject a program, resample-and-select is picking at random.
- The feedback is richer than a failing-test transcript. The null covers test output and verbal reflection, not interactive dynamic analysis such as debugger-driven state inspection ([Wang et al., 2025](https://arxiv.org/abs/2510.18327)).

Counter-evidence above 8B deserves weight. Iterative self-repair lifts pass rates by 4.9 to 17.1 points on HumanEval and 16.0 to 30.0 points on MBPP Sanitized across seven models up to Gemini 2.5 Pro. That is against a single-shot baseline ([Arimbur, 2026](https://arxiv.org/abs/2604.10508)).

## Example

The placebo-controlled shape generalizes beyond this one result. To test whether any retry mechanism earns its context, run it against a content-free stand-in at the same attempt budget, not against no retry at all.

**Before** — the standard comparison, which cannot separate the two effects:

```text
Arm A: one attempt, no retry
Arm B: attempt, then repair with test output   # k = 8
```

**After** — the matched-budget decomposition:

```text
Arm A: resample from original prompt           # k = 8, no exposure
Arm B: failed program + "this was incorrect"   # k = 8, exposure, no content
Arm C: failed program + test output            # k = 8, exposure + content
```

A gap between A and B is the cost of exposure. A gap between B and C is the value of the feedback content. In the small-model study the first gap is large and the second is null ([Verma, 2026](https://arxiv.org/abs/2607.26117)).

## Key Takeaways

- Below 7B, blind resampling beats every self-conditioning retry arm at a matched budget — pass@1 at k=8 of 0.749 against 0.688 at 1.5B, and 0.778 against 0.709 to 0.743 at 3B on MBPP+ ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)).
- The cost comes from seeing the failed program, not from bad feedback: a content-free failure notice loses as much accuracy as real execution feedback.
- Anchoring is the mechanism — near-identical retries rise from 2–14% to 33–68% once the model sees its own code, so retries stop exploring.
- Blind resampling is also the cheapest arm at every scale, with reflection costing 2.5 to 5.5 times more tokens for no gain below 7B.
- The result is bounded to sub-7B models on self-contained functions with a real test oracle. It does not transfer to frontier-model coding agents, where the matched-budget evidence is mixed ([Olausson et al., 2024](https://arxiv.org/abs/2306.09896)).

## Related

- [Bounded Repair-Loop Iterations](../verification/bounded-repair-loop-iterations.md) — budgets how many repair rounds run; this page asks whether the round should carry the failed attempt at all.
- [Loop Strategy Spectrum: Accumulated vs Fresh Context](loop-strategy-spectrum.md) — the general axis this result moves, applied to whole agent loops rather than a single retry.
- [The Ralph Wiggum Loop: Fresh-Context Iteration Pattern](ralph-wiggum-loop.md) — the same clean-slate-per-iteration idea at task scale.
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](loop-budgeting.md) — where the k≈2 cap and the token comparison fit into a wider budget.
- [Local Model Viability Factors for Coding](../patterns/agent-design/local-model-viability-for-coding.md) — the deployment context in which sub-7B quantized models are the ones doing the retrying.
- [Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)](early-termination-and-warm-restart.md) — the repo-scale counterpart, where a restart keeps the failed attempt's diff behind an optional tool rather than in the prompt.
