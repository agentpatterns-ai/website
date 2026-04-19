---
title: "PASS@(k,T): Evaluate RL for Agents Along Sampling and Interaction Depth"
description: "A single pass@k number misreads RL's effect on tool-use agents. PASS@(k,T) varies sampling budget k and interaction depth T jointly, separating capability expansion from efficiency improvement."
tags:
  - testing-verification
  - evals
  - agent-design
---

# PASS@(k,T): Evaluate RL for Agents Along Sampling and Interaction Depth

> A single pass@k number misreads what RL does to a tool-use agent. Vary sampling budget *k* and interaction depth *T* together to tell capability expansion apart from efficiency gains.

## Why One-Dimensional pass@k Misleads for Agents

For static reasoning — math, code, visual reasoning — base and RL pass@k curves converge at large *k*: RL raises pass@1 but does not expand what the model can ever solve [Source: [Yue et al., *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?*](https://arxiv.org/abs/2504.13837)]. That result has been read as a general ceiling on RL post-training.

Agentic tool use breaks the assumption. Agents interleave reasoning with tool calls over *T* rounds. Compositional strategies — plan, retrieve, re-plan on retrieved content, retrieve again — depend on *T*, not on resampling. A metric that only varies *k* conflates "cannot do this at any k" with "cannot do this at this T."

## The Two-Dimensional Metric

PASS@(k,T) jointly varies sampling budget *k* and interaction depth *T* [Source: [Zhai et al., *Does RL Expand the Capability Boundary of LLM Agents? A PASS@(k,T) Analysis*](https://arxiv.org/abs/2604.14877)]. For each (k, T) cell: sample *k* trajectories with at most *T* interaction rounds each, count success as ≥1 trajectory correct.

```mermaid
graph TD
    A[Pick task suite] --> B[Define interaction budgets T]
    B --> C[Define sampling budgets k]
    C --> D[For each k,T: run k rollouts capped at T rounds]
    D --> E[Pass@k,T = any rollout correct]
    E --> F[Plot surface over k x T]
```

The output is a surface, not a number. Reading the shape separates distinct effects:

| Pattern | Interpretation |
|---|---|
| RL curve pulls above base at all T, gap closes at large k | Efficiency gain — RL samples winning trajectories more densely |
| RL curve pulls above base and gap **widens** at large k | Capability expansion — base model cannot reach the strategy at any k under this T |
| Gap appears only above some T threshold | Compositional gain — the strategy requires interaction depth the base model cannot use |
| Curves converge at all (k, T) | No RL effect on this task class |

## What the Paper Finds

On compositional, sequential information-gathering tasks the RL agent's pass-curve pulls above the base model and **the gap widens at large k rather than converging** — the opposite of the static-reasoning result [Source: [Zhai et al.](https://arxiv.org/abs/2604.14877)]. The effect is task-specific: on simpler tasks RL converges with the base model as prior work predicts.

Under matched training data, supervised fine-tuning regresses the boundary on the same compositional tasks, isolating self-directed exploration as the causal factor — not supervision quality [Source: [Zhai et al.](https://arxiv.org/abs/2604.14877)]. Mechanism analysis shows RL reweights the base strategy distribution toward strategies whose downstream reasoning more reliably produces a correct answer, concentrated on how the agent integrates retrieved information [Source: [Zhai et al.](https://arxiv.org/abs/2604.14877)].

Optimistic and pessimistic readings of RL for LLMs are both correct, on different task types.

## When PASS@(k,T) Changes a Decision

Use the 2D surface when deciding whether to invest in RL post-training for an agentic workload. A team that only measures pass@1 sees an RL lift and concludes RL is working; a team that measures pass@k at fixed *T* may see convergence and conclude RL is purely efficiency. Only the joint surface reveals whether the RL agent is reaching strategies the base model cannot reach under the same interaction budget.

Single-turn benchmarks — HumanEval, MBPP, math word problems — do not require this metric. PASS@(k,T) collapses to pass@k when *T*=1.

## Limits and Measurement Traps

- **T must span the compositional budget.** If the harness caps *T* below what a compositional plan requires, both base and RL agents fail and the metric reports no expansion. Size *T* from observed successful-trajectory lengths before fixing the grid.
- **Early-training checkpoints understate the effect.** RL can narrow capability during an exploitation phase before an exploration phase recovers it [Source: [Yao et al., *The Debate on RLVR Reasoning Capability Boundary: Shrinkage, Expansion, or Both?*](https://arxiv.org/abs/2510.04028)].
- **pass@k at large k is exponentially forgiving** — any non-zero-capability agent eventually hits the right answer. Interpret widening gaps at large *k* as capability expansion only when the base model's pass-curve has plateaued [Source: [Brooker, *Pass@k is Mostly Bunk*](https://brooker.co.za/blog/2026/01/21/pass-k.html)].
- **Reward-hackable environments inflate the surface.** If the outcome check can be satisfied by surface patterns, RL exploits the reward; the widening gap reflects hacking, not reasoning. Audit with [trajectory-opaque evaluation](trajectory-opaque-evaluation-gap.md) before trusting outcome-only scores.
- **Small suites give wide confidence intervals.** The 2D grid multiplies sample requirements; report intervals rather than point estimates per cell [Source: [Hariri et al., *Don't Pass@k: A Bayesian Framework for LLM Evaluation*](https://arxiv.org/abs/2510.04265)].

## Example

A team evaluates whether tool-use RL on a retrieval-augmented agent is worth shipping. They compare the base model against an RL-fine-tuned variant on 50 compositional research tasks. The numbers below are illustrative shapes the metric can produce, not values reported in any specific paper.

```
pass@(k, T) surface — compositional information-gathering suite

Base model:
          k=1     k=4     k=16    k=64
T=2      0.12    0.21    0.28    0.31
T=8      0.24    0.41    0.52    0.58
T=32     0.31    0.48    0.60    0.63    <- plateaus at large k

RL variant:
          k=1     k=4     k=16    k=64
T=2      0.18    0.28    0.34    0.37
T=8      0.41    0.58    0.71    0.78
T=32     0.52    0.71    0.83    0.89    <- gap widens at large k
```

Reading the surface:

- At **T=2** the gap is small and closes at large *k* — efficiency only; base model reaches similar ceiling with more samples
- At **T=8 and T=32** the gap **widens** at large *k* — RL reaches strategies the base model does not find under matched interaction budget
- The **compositional expansion is real** for this workload; RL post-training is worth shipping

If the team had only measured pass@1 (+0.21 at T=32), they would call RL "better." If they had only measured pass@64 at T=2 (+0.06), they would call RL "barely different." Neither reading is correct.

## Key Takeaways

- Single pass@k numbers mislead for multi-turn tool-use agents — interaction depth *T* is a first-class dimension
- Widening gap at large *k* indicates capability expansion; closing gap indicates efficiency gain only
- The expansion result is specific to compositional tasks — simpler tasks converge as prior work predicts
- Matched-data SFT regresses the same boundary — self-directed exploration is the mechanism, not supervision
- Size *T* from observed successful-trajectory lengths; too-small *T* hides the effect

## Related

- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — single-turn pass@k versus pass^k
- [Variance-Based RL Sample Selection](variance-based-rl-sample-selection.md) — upstream: which samples give RL a gradient signal
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — outcome-based grading that PASS@(k,T) builds on
- [Trajectory-Opaque Evaluation Gap](trajectory-opaque-evaluation-gap.md) — why outcome-only metrics need trajectory audits
- [Behavioral Testing for Non-Deterministic AI Agents](behavioral-testing-agents.md) — multi-trial evaluation design
