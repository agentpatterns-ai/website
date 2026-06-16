---
title: "Prior Dominance Over Feedback in Agent Optimization Loops"
term: "Prior Dominance Over Feedback"
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
last_reviewed: 2026-06-13
maturity: established
---

# Prior Dominance Over Feedback

> LLMs in propose-evaluate-revise loops are greedy hill climbers anchored to their pretrained priors. Where the prior is weak, more feedback cannot rescue the loop.

## The Pattern

In **propose-evaluate-revise loops** — kernel generation, hyperparameter search, code optimization — the model proposes a candidate, an evaluator (compiler, profiler, test, scorer) returns feedback, and the model revises. Practitioners treat more iterations as broader search. Empirically the loop is a greedy hill climber that starts at, and stays near, the prior's mode.

## Why It Fails Where the Prior Is Weak

- **The acceptance rule barely matters; the prior carries the load.** Simulated annealing, parallel investigators, and a second model give no benefit over greedy hill climbing while costing 2–3x more evaluations across four optimization tasks ([Yitao Li, "Greedy Is a Strong Default"](https://arxiv.org/abs/2603.27415)).
- **LLMs show three reliable failure modes under feedback:** greediness, frequency bias, and a knowing-doing gap — they can describe what to explore while still sampling the prior's mode. RL fine-tuning on self-generated chain-of-thought reduces but does not eliminate the bias ([Schmied et al., "LLMs are Greedy Agents"](https://arxiv.org/abs/2504.16078)).
- **Training on optimal exploration makes agents greedier.** Models supervised on UCB and Thompson Sampling demonstrations beat their teacher on average reward by abandoning exploration earlier, at the cost of catastrophic early failures ([Chen et al., "When Greedy Wins"](https://arxiv.org/abs/2509.24923)).
- **Returns decay roughly exponentially across iterations** until the loop plateaus; compute past the plateau is waste ([Bhattacharjee et al.](https://arxiv.org/abs/2411.19043)).

## Why It Works

Each proposal samples from the LLM's pretrained conditional distribution. Feedback enters as prompt conditioning, which shifts probabilities only within the support the prior already assigns non-trivial mass. When the optimum lies where the prior assigns near-zero probability — low-resource languages like R and Racket ([Cassano et al.](https://arxiv.org/abs/2308.09895)), novel ISAs, bespoke DSLs — no conditioning produces samples from that region. The model cannot explore where it was never trained. When the prior is strong, refinement still adds roughly 20% over one-shot ([Madaan et al., "Self-Refine"](https://arxiv.org/abs/2303.17651)): feedback amplifies the prior, it does not replace it.

## When This Backfires

Added iterations rarely find the optimum when any of these hold:

- **The prior on the problem family is weak** — uncommon GPU shapes, low-resource languages, novel ISAs, bespoke DSLs.
- **The feedback channel is scalar-only.** Bare loss or score values trigger greedy exploitation ([Schmied et al.](https://arxiv.org/abs/2504.16078)).
- **The compute budget runs past the plateau** ([Bhattacharjee et al.](https://arxiv.org/abs/2411.19043)).
- **The optimum needs exploration past the prior's mode** — tricks or structures the model would not propose unprompted.

## When Propose-Evaluate-Revise Still Works

The pattern is correct when the LLM has a substantial prior on the task family, the feedback encodes information the prior lacks (compiler errors, profiler timings, failing-test traces — not bare scalars), and the horizon is short enough that the prior still steers productively. ComPilot reaches 2.66x single-run and 3.54x best-of-5 speedups on PolyBench using zero-shot LLMs in a compiler-grounded loop ([Merouani et al.](https://arxiv.org/abs/2511.00592)).

## Mitigations

- **Warm-start with diverse seeds** so the loop is not anchored to one mode.
- **Inject expert knowledge** — idioms, reference implementations, hardware specs — to move the prior into a useful region before the loop starts.
- **Use [richer feedback than scalars](../agent-design/feedback-capability-equalizer.md)** — compiler diagnostics, profiler traces, failing-test output.
- **Switch to MAB or evolutionary scaffolds** when the prior is weak, so the scaffold enforces exploration.
- **Detect the plateau** and stop when marginal gain falls below a threshold.

## Key Takeaways

- LLMs in propose-evaluate-revise loops are greedy hill climbers from the prior's mode, not search procedures over the solution space.
- The acceptance rule and iteration count matter less than the strength of the prior; returns decay roughly exponentially and iterations past the plateau extract no further signal.
- Treat the loop as a prior-amplifier — when the prior is weak, switch to scaffolds that enforce exploration externally.

## Related

- [Boring Technology Bias](boring-technology-bias.md) — A parallel manifestation of the same prior: tool recommendations track training frequency rather than fitness.
- [Pattern Replication Risk](pattern-replication-risk.md) — Another instance of prior-dominated sampling: agents reproduce existing codebase patterns at scale.
- [Feedback as Capability Equalizer](../agent-design/feedback-capability-equalizer.md) — The positive case: when the prior is reasonable and feedback is informative, iterative feedback outweighs model scale.
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — Misapplying agent control structure where it adds cost without changing outcomes.
- [Loop Strategy Spectrum](../agent-design/loop-strategy-spectrum.md) — Loop structure is upstream of whether feedback can shift the agent off the prior's mode.
