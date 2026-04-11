---
title: "Variance-Based RL Sample Selection"
description: "Profile training data by score variance before RL fine-tuning to identify the high-value subset where the model sometimes succeeds and sometimes fails."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - RL sample profiling
  - variance-based training selection
---

# Variance-Based RL Sample Selection

> Profile training samples by score variance before committing to RL fine-tuning — only the subset where the model sometimes succeeds and sometimes fails offers a real learning signal.

## Why Most Training Data Contributes Nothing

Reinforcement learning fine-tuning requires gradient signal. A sample produces no gradient when the model always gets it right (reward is constant at the maximum) or always gets it wrong (reward is constant at zero). In practice, this zero-variance majority is large. In a FinQA benchmark case study, approximately 85% of samples showed zero variance — meaning only 15% could contribute to learning. Running RL on the full dataset wastes roughly 6× the compute that the productive slice alone would require.

The three categories:

| Category | Score variance | Learning signal |
|---|---|---|
| Always correct | 0 | None — model already solved |
| Always wrong | 0 | None — task out-of-distribution or too hard |
| Variable | > 0 | Present — prime RL candidate |

"Always wrong" samples deserve the same exclusion as "always correct" ones. A model that consistently scores zero on a sample is not close to learning it — it signals a capability gap or a mismatched task, not a training opportunity.

## The Profiling Workflow

Run the baseline model on each training sample 3–5 times before any RL training. Compute four metrics per sample:

- **Mean score** — average reward across runs
- **Best score** — maximum reward achieved across runs
- **Standard deviation** — spread across runs
- **Variance** — square of standard deviation; threshold above zero to identify variable samples

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

## Improvement Ceiling Estimation

Before starting RL training, the gap between mean score and best-of-N score gives an upper bound on what RL can plausibly recover. In the FinQA case study, the baseline mean was 0.59 and the best-of-3 potential was 0.73 — a +24% relative ceiling. After 10 steps of RL fine-tuning on the high-variance subset, validation reward improved from 0.59 to 0.63 (+7%), with tool calls per rollout dropping from 6.9 to 4.2 (−39%). Actual gains land well below the ceiling; the ceiling is useful as a go/no-go filter before committing to a training run.

Additional validated results from the same methodology:

- Ambience Healthcare (ICD-10 medical coding): F1 0.52 → 0.57 (+9.6%), 18% latency reduction
- Cognition/Devon AI (file planning): 50% reduction in planning tool calls

[Source: [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/variance-based-rl-sample-selection.md)]

## Cost Trade-off

Profiling costs 3–5× a single inference pass per sample. This is paid once before training and is typically small relative to the GPU cost of a full RL training run on a dataset that is 85% unproductive. When the variable subset is 15% of the original dataset, the saving on training compute is approximately 6×.

The approach extends Prioritized Experience Replay ([Schaul et al., ICLR 2016](https://arxiv.org/abs/1511.05952)) from value-based RL to LLM fine-tuning — replacing TD-error as the priority signal with empirical score variance across repeated rollouts.

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

The team trains on 300 samples instead of 2,000 — a 6.7× compute reduction — and uses the ceiling estimate to set expectations before committing the GPU budget.

## Key Takeaways

- Run each training sample 3–5 times before RL training; discard always-correct and always-wrong samples
- In practice, ~85% of samples have zero variance and contribute no learning signal
- The gap between mean score and best-of-N score gives an improvement ceiling to evaluate before training
- Upfront profiling costs 3–5× inference; training cost savings typically exceed this by an order of magnitude
- Always-wrong samples indicate capability or task-distribution gaps — not training opportunities

## Unverified

- The FinQA benchmark case study and Ambience Healthcare / Cognition results are cited from the nibzard/awesome-agentic-patterns catalog; the underlying primary source (paper or blog post) is not directly linked in that catalog entry [unverified]

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md)
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
