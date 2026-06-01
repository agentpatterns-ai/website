---
title: "Prior Dominance Over Feedback in Agent Optimization Loops"
description: "LLMs in propose-evaluate-revise loops act as greedy optimizers anchored to pretrained priors; feedback amplifies the prior rather than replacing it."
tags:
  - agent-design
  - workflows
  - anti-pattern
  - tool-agnostic
aliases:
  - greedy optimizer prior
  - propose-evaluate-revise anti-pattern
  - prior over feedback
last_reviewed: 2026-05-27
---

# Prior Dominance Over Feedback

> LLMs in propose-evaluate-revise loops behave as greedy hill climbers anchored to their pretrained priors. When the prior is weak — uncommon problem sizes, low-resource languages, novel hardware idioms — additional feedback rounds cannot rescue the loop.

## The Pattern

In **propose-evaluate-revise loops** for LLM-driven optimization, kernel generation, hyperparameter search, and code performance, the model proposes a candidate, an evaluator (compiler, profiler, test, scorer) returns feedback, and the model revises. Practitioners treat more iterations as broader search. Empirically the loop is not search — it is a greedy hill climber that starts at, and remains near, the prior's mode.

## Why It Fails Where the Prior Is Weak

- **Acceptance rules barely matter; the prior carries the load.** Simulated annealing, parallel investigators, and second-model investigators provide no benefit over greedy hill climbing while requiring 2–3x more evaluations across four optimization tasks ([Yitao Li, "Greedy Is a Strong Default"](https://arxiv.org/abs/2603.27415)).
- **LLMs show three reliable failure modes under feedback:** greediness, frequency bias, and a knowing-doing gap. The model can describe what it should explore while sampling from the prior's mode; RL fine-tuning on self-generated chain-of-thought reduces but does not eliminate the bias ([Schmied et al., "LLMs are Greedy Agents"](https://arxiv.org/abs/2504.16078)).
- **Training on optimal exploration makes agents greedier.** LLMs supervised on UCB and Thompson Sampling demonstrations exceed their teacher on average reward by abandoning exploration earlier, at the cost of more catastrophic early failures ([Chen et al., "When Greedy Wins"](https://arxiv.org/abs/2509.24923)).
- **Feedback-loop returns decay roughly exponentially across iterations** until the loop plateaus ([Bhattacharjee et al.](https://arxiv.org/abs/2411.19043)). Compute past the plateau is waste.

## Why It Works

Each proposal samples from the LLM's pretrained conditional distribution. Feedback enters as prompt conditioning, which can shift probabilities only within the support the prior already assigns non-trivial mass. When the optimum lies where the prior assigns near-zero probability — uncommon kernel input sizes, low-resource programming languages (in The Stack, R appears in 0.04% of files, Racket in 0.004% per [Cassano et al.](https://arxiv.org/abs/2308.09895)), novel ISAs, bespoke DSLs — no conditioning produces samples from that region. The model cannot explore where it was never trained. This is the knowing-doing gap from bandit evaluations ([Schmied et al.](https://arxiv.org/abs/2504.16078)). Iterative refinement still adds roughly 20% over one-shot when the prior is strong ([Madaan et al., "Self-Refine"](https://arxiv.org/abs/2303.17651)) — feedback amplifies the prior, it does not replace it.

## When This Backfires

Additional loop iterations rarely find the optimum when any of these hold:

- **The prior on the problem family is weak.** Uncommon GPU shapes, low-resource programming languages, novel ISAs, bespoke DSLs.
- **The feedback channel is sparse or scalar-only.** Loss or score values without diagnostics reliably trigger greedy exploitation ([Schmied et al.](https://arxiv.org/abs/2504.16078)).
- **The compute budget is spent past the plateau** ([Bhattacharjee et al.](https://arxiv.org/abs/2411.19043)).
- **The optimum requires genuine exploration past the prior's mode** — rare optimization tricks or algorithmic structures the model would not propose unprompted.

## When Propose-Evaluate-Revise Still Works

The pattern is correct when the LLM has a substantial prior on the task family, the feedback encodes information the prior lacks (compiler errors, profiler timings, failing tests with stack traces — not bare scalars), and the horizon is short enough that the prior is still steering productively. ComPilot achieves 2.66x single-run and 3.54x best-of-5 speedups on PolyBench using zero-shot LLMs in a compiler-grounded loop ([Merouani et al.](https://arxiv.org/abs/2511.00592)). Treat the loop as a prior-amplifier, not a prior-replacement.

## Mitigations

- **Warm-start with diverse seeds** so the loop is not anchored to one mode.
- **Inject expert knowledge into the prompt** — known idioms, reference implementations, hardware specifications — to shift the prior into a useful region before the loop starts.
- **Use richer feedback than scalars** — compiler diagnostics, profiler traces, failing-test output.
- **Switch to MAB or evolutionary scaffolds** when the prior is weak, so exploration is enforced by the scaffold.
- **Detect the plateau** by tracking iteration-over-iteration improvement and stopping when marginal gain falls below a threshold.

## Key Takeaways

- LLMs in propose-evaluate-revise loops are greedy hill climbers from the prior's mode, not search procedures over the solution space.
- The acceptance rule and number of iterations matter less than the strength of the prior on the task family.
- When the prior is weak, feedback cannot rescue the loop.
- Feedback-loop returns decay roughly exponentially; iterations past the plateau extract no further signal.
- Treat propose-evaluate-revise as a prior-amplifier; when the prior is weak, switch to scaffolds that enforce exploration externally.

## Related

- [Boring Technology Bias](boring-technology-bias.md) — A parallel manifestation of the same prior: tool recommendations track training frequency rather than fitness.
- [Pattern Replication Risk](pattern-replication-risk.md) — Another instance of prior-dominated sampling: agents reproduce existing codebase patterns at scale.
- [Feedback as Capability Equalizer](../agent-design/feedback-capability-equalizer.md) — The positive case: when the prior is reasonable and feedback is informative, iterative feedback outweighs model scale.
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — Misapplying agent control structure where it adds cost without changing outcomes.
- [Loop Strategy Spectrum](../agent-design/loop-strategy-spectrum.md) — Loop structure is upstream of whether feedback can shift the agent off the prior's mode.
