---
title: "Advisory Prompts Distilled from Reasoning Traces"
term: "Advisory Prompt Distillation"
description: "Harvest the cases where thinking mode fixed an answer, distill them into standing procedural advice, and run with reasoning off at a measured per-model accuracy cost."
tags:
  - instructions
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - advisory prompt distillation
  - distilled reasoning advisory prompts
last_reviewed: 2026-08-04
maturity: emerging
---

# Advisory Prompts Distilled from Reasoning Traces

> Advisory prompts distilled from a model's own thinking traces cut output tokens sharply while conceding a model-specific amount of accuracy.

Advisory prompt distillation harvests the cases where a model's thinking mode fixed an answer its non-thinking mode got wrong, has a larger model diagnose the difference, and compresses the diagnosis into a few lines of standing procedural advice. That advice then rides in the prompt with reasoning switched off. Across 20 model-task pairs it lifted non-thinking accuracy by a mean of 3.1 pass-rate points while using 58.6% fewer output tokens than the thinking-mode baseline ([Faisal, Devanbu and Ahmed, 2026](https://arxiv.org/abs/2608.00437v1)).

## The condition that decides it

The technique does not recover reasoning-mode accuracy. How much accuracy it concedes is a property of the model you run, not of the method. The same paper, the same pipeline, two model families:

| Student models | Output tokens saved | Accuracy conceded against thinking baseline |
|---|---|---|
| Gemma-4-E2B-it, Gemma-4-E4B-it | 39% | 0.8 pass-rate points |
| Qwen3-4B, Qwen3-8B | 78% | 14.3 pass-rate points |

On the Gemma-4 students that is near-parity for a real saving. On the Qwen3 students it is a trade most teams would refuse ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)). Averaged over all 20 comparisons, thinking mode still wins 17 of them by 7.5 pass-rate points. Measure both numbers on the model you ship before treating a distilled prompt as a substitute for a [reasoning budget](../patterns/agent-design/reasoning-budget-allocation.md).

## How the distillation runs

Four stages ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)):

1. Run the student model over a distillation set in both modes and isolate the deltas: cases thinking fixed, and cases thinking broke.
2. A teacher model, GPT-5.4-mini in the published setup, diagnoses each delta case and emits a mechanism label, an explanation, an evidence span, and a confidence score.
3. A larger teacher, GPT-5.4, aggregates those diagnoses into improvement instructions and guard instructions, then composes three candidate prompts.
4. Score the candidates on a held-out validation split and keep the best, breaking ties on fewer regressions and shorter length.

Stage 4 is what stops a plausible-sounding rule from shipping.

## What survives selection

The selected advice describes process rather than domain knowledge. A keyword audit of the 100 selected prompts found that "49% ask the model to track state or transitions, 40% to work through concrete examples or dry runs, and 25% to check edge cases" ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)). None of it names a library or a repository, which separates this artifact from a tuned guidance file such as [probe-and-refine](probe-and-refine-guidance-tuning.md).

## Why it works

Reasoning mode's advantage on code-reasoning tasks is largely procedural rather than inferential, so a prompt can carry most of it. A thinking trace here spends its tokens tracking variable state, dry-running the code, and enumerating edge cases, which is exactly what the keyword audit above shows the teacher extracting. Stating that procedure as a standing instruction makes a non-thinking model run the steps without spending output tokens deriving that it should.

The gain pattern is the evidence. Distilled prompts lifted 19 of 20 non-thinking comparisons by a mean of 3.1 points, but only 14 of 20 thinking-mode comparisons by a mean of 1.3 ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)). New capability would help in both modes; advice that only helps where the procedure is absent is supplying procedure. The 7.5-point residual gap is the non-procedural half, and no prompt in this study recovered it.

## When this backfires

- The task is already near ceiling. Output prediction gained between 0.0 and 1.8 points because the baselines left no headroom ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)).
- The prompt is reused on an unvalidated model. Input prediction and output prediction transfers each averaged a 0.7-point loss across 60 source-target pairs, against gains of 2.7 to 4.4 points on the three task families where transfer worked ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)). Cross-model prompt reuse degrades often enough to have a name, "Model Drifting", reported as both common and severe ([Wang et al., 2025](https://arxiv.org/abs/2512.01420v1)).
- Transfer targets are picked by failure similarity. The authors "fail to observe a strong relationship between common-mode failure intensity and prompt-transfer effectiveness", and transferred prompts rescued 21.3% of shared source-target failures against 49.1% of target-only failures ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)).
- The advice is appended to a prompt that already carries standing rules. Generic rule additions do not improve monotonically; one measured case dropped retrieval citation compliance from 26 of 30 to 9 of 30 ([Commey, 2026](https://arxiv.org/abs/2601.22025v2)).
- Correctness matters more than throughput. The evaluation scores functional pass rate only, from a single sample per example at temperature 0.7, so the authors note some gain may reflect sampling variance ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)).

## Example

The advisory line below is published verbatim by the paper ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)); the surrounding task instruction is a one-line stand-in for the exception-prediction task it was distilled against.

**Before** — the bare task instruction with thinking mode off:

```text
Predict whether this Python function raises, and which exception.
```

**After** — the same instruction carrying the distilled advisory line:

```text
Predict whether this Python function raises, and which exception.

Check each operation for type compatibility before deciding whether
execution succeeds.
```

The added line names no library and carries no domain knowledge. It states a procedure, which is the same procedure the model runs internally with thinking mode on. On that task, distilled prompts lifted Qwen3-4B by up to 11.5 pass-rate points ([Faisal et al., 2026](https://arxiv.org/abs/2608.00437v1)).

## Key Takeaways

- Budget for a validation split on the model you actually ship. The accuracy you concede is a measurement, not a published constant.
- Re-run the distillation on every model swap, and re-check the task still has headroom before spending on it.
- Do not pick transfer targets by shared failure patterns; that predictor was measured and it failed.
- Reach for this only on the reasoning-off path. Stacking the advice on top of thinking mode moved 14 of 20 comparisons by a mean of 1.3 points.
- Size the expected win as a token-cost saving. Reasoning-mode accuracy stayed out of reach on every model family measured.

## Related

- [Codified Effort and Escalation Policy in the Instruction File](codified-effort-escalation-policy.md) — the surrounding decision: when the cheap, reasoning-off path is the default at all
- [Reasoning Budget Allocation: The Reasoning Sandwich](../patterns/agent-design/reasoning-budget-allocation.md) — the alternative lever when you can spend reasoning tokens and want them placed well
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — the repository-specific analogue, with the same model-specificity caveat
- [Indiscriminate Structured Reasoning](../patterns/anti-patterns/reasoning-overuse.md) — the failure mode on the other side, where reasoning is spent past the point it helps
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](prompt-rewrite-on-cross-generation-migration.md) — what to do with a tuned prompt stack when the model underneath changes
- [CoT Robustness in Code Generation](../verification/cot-robustness-code-generation.md) — prior evidence that chain-of-thought helps, hurts, or does nothing depending on model and task
