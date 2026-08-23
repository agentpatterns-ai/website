---
title: "Variance-Based RL Sample Selection"
description: "Profile training data by score variance before RL fine-tuning to identify the high-value subset where the model sometimes succeeds and sometimes fails."
term: "Variance-Based RL Sample Selection"
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - RL sample profiling
  - variance-based training selection
last_reviewed: 2026-05-27
maturity: established
---

# Variance-Based RL Sample Selection

> Profile training samples by score variance before committing to RL fine-tuning — only the subset where the model sometimes succeeds and sometimes fails offers a real learning signal.

## Why most training data contributes nothing

Reinforcement learning fine-tuning needs a gradient signal. A sample produces no gradient when the model always gets it right (reward stays at the maximum) or always gets it wrong (reward stays at zero). This zero-variance majority is usually large. In a FinQA benchmark case study, about 85% of samples showed zero variance, so only 15% could contribute to learning. Running RL on the full dataset wastes roughly 6 times the compute that the productive slice alone needs.

The three categories:

| Category | Score variance | Learning signal |
|---|---|---|
| Always correct | 0 | None — model already solved |
| Always wrong | 0 | None — task out-of-distribution or too hard |
| Variable | > 0 | Present — prime RL candidate |

Exclude "always wrong" samples for the same reason you exclude "always correct" ones. A model that consistently scores zero on a sample is not close to learning it. That score signals a capability gap or a mismatched task, not a training opportunity.

## The profiling workflow

Run the baseline model on each training sample 3 to 5 times before any RL training. Compute four metrics per sample:

- Mean score: average reward across runs
- Best score: highest reward across runs
- Standard deviation: spread across runs
- Variance: the square of the standard deviation; a value above zero marks a variable sample

```python
from statistics import mean, stdev

def profile_sample(scores: list[float]) -> dict:
    """Compute variance metrics for a single training sample."""
    return {
        "mean": mean(scores),
        "best": max(scores),
        "std": stdev(scores) if len(scores) > 1 else 0.0,
        "variance": stdev(scores) ** 2 if len(scores) > 1 else 0.0,
    }

# Example: 5 runs on a single sample
scores = [0.0, 1.0, 0.0, 1.0, 0.0]
profile = profile_sample(scores)
# {"mean": 0.4, "best": 1.0, "std": 0.548, "variance": 0.3}
# Variable — include in RL training set
```

Filter to variable samples (variance > 0) before constructing the RL training dataset.

## Improvement ceiling estimation

The gap between mean score and best-of-N score gives an upper bound on what RL can plausibly recover, so measure it before you start training. In the FinQA case study, the baseline mean was 0.59 and the best-of-3 potential was 0.73, a +24% relative ceiling. After 10 steps of RL fine-tuning on the high-variance subset, validation reward rose from 0.59 to 0.63 (+7%), and tool calls per rollout dropped from 6.9 to 4.2 (−39%). Actual gains land well below the ceiling. The ceiling still helps as a go/no-go filter before you commit to a training run.

Additional validated results from the same methodology:

- Ambience Healthcare (ICD-10 medical coding): F1 0.52 → 0.57 (+9.6%), 18% latency reduction
- Cognition/Devon AI (file planning): 50% reduction in planning tool calls

[Source: OpenAI Build Hours — [Agent Reinforcement Fine-Tuning, November 2025](https://github.com/openai/build-hours/tree/main/20-agent-rft)]

## Cost trade-off

Profiling costs 3 to 5 times a single inference pass per sample. You pay it once before training. That cost is usually small next to the GPU cost of a full RL training run on a dataset that is 85% unproductive. When the variable subset is 15% of the original dataset, you save about 6 times the training compute.

The approach extends Prioritized Experience Replay ([Schaul et al., ICLR 2016](https://arxiv.org/abs/1511.05952)) from value-based RL to LLM fine-tuning — replacing TD-error as the priority signal with empirical score variance across repeated rollouts.

## When this backfires

Variance-based exclusion is not always the right call. It underperforms alternatives in three conditions:

- Always-wrong samples can still carry signal: [RL-ZVP (No Prompt Left Behind, ICLR 2026)](https://arxiv.org/abs/2509.21880) extracts learning from zero-variance prompts through entropy-guided advantage shaping, beating GRPO baselines that filter them out by up to 8.61 points on math benchmarks.
- Low rollout counts misclassify borderline samples: with 3 to 5 runs, samples near the learnability boundary often get tagged zero-variance by chance, the same boundary that curriculum approaches like [VCRL](https://arxiv.org/abs/2509.19803v1) target on purpose. Raise the rollout count or pair filtering with a difficulty schedule.
- Paired sampling beats variance heuristics: [Beyond Variance (Feb 2026)](https://arxiv.org/abs/2602.03452) shows that pairing a hard-but-solvable prompt with an easy-but-brittle one, without any variance filter, improves AIME 2025 Pass@8 from 16.8 to 22.2 over variance-selected GRPO.

The case study still holds when rollout cost dominates the GPU budget and the training stack cannot use zero-variance signal. Outside those conditions, treat variance filtering as one option, not the default.

## Example

A team fine-tuning a coding agent on 2,000 task samples runs each sample 3 times with the baseline model. Results:

```
Total samples:    2,000
Always correct:     800  (40%) — excluded
Always wrong:       900  (45%) — excluded
Variable:           300  (15%) — RL training set

Ceiling estimate: mean 0.61, best-of-3 0.74 → +21% relative headroom
Training cost:    300 samples × RL steps (vs. 2,000 without profiling)
```

The team trains on 300 samples instead of 2,000, a 6.7 times compute reduction, and uses the ceiling estimate to set expectations before committing the GPU budget.

## Key Takeaways

- Run each training sample 3–5 times before RL training; discard always-correct and always-wrong samples
- In practice, ~85% of samples have zero variance and contribute no learning signal
- The gap between mean score and best-of-N score gives an improvement ceiling to evaluate before training
- Upfront profiling costs 3–5× inference; training cost savings typically exceed this by an order of magnitude
- Always-wrong samples indicate capability or task-distribution gaps — not training opportunities

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md)
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
