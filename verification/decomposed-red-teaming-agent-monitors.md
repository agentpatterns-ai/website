---
title: "Decomposed Red-Teaming for Agent Monitors"
term: "Decomposed Red-Teaming"
description: "Split attack construction into strategy, execution, and refinement stages so monitor evaluations expose the conceive-execute gap instead of measuring single-pass elicitation."
tags:
  - testing-verification
  - evals
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - decomposed red-teaming
  - semi-automated monitor red-teaming
last_reviewed: 2026-06-03
---

# Decomposed Red-Teaming for Agent Monitors

> Decomposed red-teaming splits attacks into strategy, execution, and refinement stages, dropping BashArena monitor catch rates from 94.9% to 60.3% and exposing the conceive-execute gap.

## Why Single-Pass Elicitation Under-Reports

One frontier model planning and executing an attack in one trajectory produces a narrow distribution. 81% of Opus 4.6-elicited attacks fall into 2 of 5 technical tiers, and 64% share identical structural templates ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)). The broader red-teaming literature reports the same shape: attacker LMs mode-collapse even with explicit diversity rewards, so single-pass elicitation under-samples the attack space ([Lee et al., 2024](https://arxiv.org/abs/2405.18540)). Splitting the task surfaces the long tail.

An Opus-4.5 monitor catches 94.9% of single-pass attacks but only 60.3% of full-pipeline attacks against the same 2,644-trajectory benchmark ([MonitoringBench](https://arxiv.org/abs/2605.09684)) — that gap is the under-reporting.

This is distinct from [controlled benchmark rewriting](controlled-benchmark-rewriting-safety-judgment.md) (rewriting existing trajectories) and [RL-trained automated red teamers](../security/rl-automated-red-teamers.md) (training one end-to-end attacker). Decomposition addresses a third gap: the conceive-execute trade-off within one prompt.

## The Conceive-Execute Gap

Attack construction has two demands that compete for one context budget:

- **Conceive** — generate novel attack ideas that escape mode-collapsed templates.
- **Execute** — produce a tool-call trajectory that completes the side task without surface cues the monitor detects.

A frontier LLM prompted to do both falls back on familiar templates and over-cues the execution with explicit malicious phrasing. Strategy generation by reconnaissance agents without execution pressure produces lower catch rates (73.5-82.7%) than single-pass baseline (94.9%) against Opus 4.5 ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)).

## The Three-Stage Pipeline

```mermaid
graph TD
    A[Side task<br/>specification] --> B[Strategy generation<br/>reconnaissance agent]
    B --> C[Execution<br/>strategy-fidelity validated]
    C --> D[Refinement<br/>rewrite suspicious elements]
    D --> E[Attack trajectory<br/>scored against monitors]
    F[Attack taxonomy<br/>T1-T5, S1-S4, E1-E4] -.coverage signal.-> B
    G[Development monitor<br/>feedback] -.grounded exploration.-> B
```

1. **Strategy generation** — a reconnaissance agent explores the environment without committing to execution. Three variants: human-in-the-loop, reconnaissance alone, and reconnaissance with monitor feedback. The taxonomy spans Technical Implementation (T1-T5), Structural Complexity (S1-S4), and Evasion Strategy (E1-E4: benign naming, overperformance, string obfuscation, persuasion) ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)).

2. **Execution** — a second model runs the strategy in BashArena. Strategy fidelity is validated at the trajectory level; executor drift discards the run.

3. **Refinement** — a four-stage post-processing pass identifies suspicious elements (lexical cues, anomalous tool sequences, explicit malicious framing) and rewrites the trajectory to preserve the side-task outcome while removing the surface signals.

Attacks refined against three development monitors (GPT-5 Nano, GPT-5, Claude Opus 4.5) generalise to ten held-out full-trajectory monitors and seven held-out stepwise monitors ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)).

## What the Drop Tells You

| Attack source | Opus 4.5 catch rate |
|---------------|---------------------|
| Baseline (single-pass Opus elicitation) | 94.9% |
| Reconnaissance-agent strategy, no refinement | 73.5-82.7% |
| Full pipeline (strategy + execution + refinement) | 60.3% |

The 34.6-point spread is the conceive-execute gap — same monitor, same threat model, same models, different elicitation methodology. Weaker monitors (GPT-5-tier and below) show steeper cliffs; the 60.3% Opus 4.5 figure is the upper bound of detection in this setting, not a floor ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)).

Stepwise monitors expose a separate problem: per-action FPR calibrated at 1% compounds to 6.7-17.4% trajectory-level FPR ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)). Independent work on weak-to-strong monitoring sees the same pattern — TPR is hard to hold at low FPR, and monitor scaffolding matters more than the model itself ([Bhatt et al., 2025](https://arxiv.org/abs/2508.19461)). Reporting only per-action FPR understates production noise.

## When This Applies

Run decomposed red-teaming when:

- A monitor LLM is the load-bearing safety layer — the catch rate is what regression testing protects
- The threat model includes adversaries with frontier-model access
- The monitor was last evaluated with single-pass elicitation and scored at or above 90% — the gap is largest there

Skip when:

- The agent has no monitor LLM and relies on [deterministic guardrails](deterministic-guardrails.md), confirmation gates, or permission scoping
- The deployment is structurally narrow (single tool, fixed input schema) and the attack surface is closed at the harness level
- Single-pass elicitation already exposes failures the team has not closed — fix those first

## Failure Modes

- **BashArena-specific transfer** — the drop is measured against bash tool-use monitors. Replicate in the target environment before quoting externally.
- **Refinement budget** — each run consumes reconnaissance, execution, and refinement calls. Scope which attack tiers get the full pipeline.
- **Monitor-feedback grounding leaks** — strategy generation using the monitor being scored leaks signal. Use a held-out monitor for final scoring.
- **Persuasion is the long tail** — frontier monitors mis-calibrate when the trajectory contains plausible justification ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)). Lexical-cue refinement misses this category; run explicit persuasion-evasion variants.

## Example

A team evaluating a Claude Opus 4.5 monitor for a tool-using coding agent runs the same 2,644-trajectory benchmark under two methodologies:

```text
                                Catch rate    Notes
Single-pass elicitation         94.9%         baseline used in most reports
Decomposed pipeline             60.3%         strategy + execute + refine
```

Source: results from the MonitoringBench main table ([Jotautaitė et al., 2026](https://arxiv.org/abs/2605.09684)).

The baseline number alone would let the team ship the monitor with confidence. The pipeline number forces a different decision: either accept that one in three frontier-model attacks passes the monitor, or stack a deterministic guardrail beneath it so the load-bearing detection is not the monitor LLM alone.

## Key Takeaways

- Single-pass elicitation under-reports monitor failure because frontier models hit a conceive-execute trade-off within one prompt — 81% of Opus 4.6-elicited attacks cluster into 2 of 5 technical tiers.
- Decomposing red-teaming into strategy, execution, and refinement drops Opus 4.5 monitor catch rates from 94.9% to 60.3% against the same threat model.
- Attacks refined against three development monitors generalise to ten held-out monitors and seven held-out stepwise monitors — the pipeline is not overfit to a specific defender.
- Stepwise monitors calibrated at 1% per-action FPR exhibit 6.7-17.4% trajectory-level FPR; report both or the noise floor is mis-stated.
- Treat the decomposed-pipeline catch rate as the regression number for any monitor that is the load-bearing safety layer; pair with [deterministic guardrails](deterministic-guardrails.md) when the residual is above the team's risk tolerance.

## Related

- [Controlled Benchmark Rewriting for Agent Safety Judgment](controlled-benchmark-rewriting-safety-judgment.md) — Rewrite existing trajectories to test judgment robustness; complementary to constructing new attacks
- [RL-Trained Automated Red Teamers](../security/rl-automated-red-teamers.md) — Train a single end-to-end attacker via RL; alternative to decomposed construction
- [Close the Attack-to-Fix Loop](../security/close-attack-to-fix-loop.md) — Feed discovered attacks straight into adversarial fine-tuning of the defender
- [Learned Prefix Monitors for Agent Traces](learned-prefix-monitors-agent-traces.md) — Online failure-warning scorers and the alert-calibration problem the FPR finding maps onto
- [Eval Awareness](eval-awareness.md) — Why monitors and judges shift behaviour on eval-shaped prompts
- [Trajectory-Opaque Evaluation Gap](trajectory-opaque-evaluation-gap.md) — Outcome-only grading misses safety violations that trajectory auditing catches
