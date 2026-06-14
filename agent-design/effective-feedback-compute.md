---
title: "Effective Feedback Compute (EFC) for Harness Comparison"
term: "Effective Feedback Compute (EFC)"
description: "Count only the feedback that is informative, valid, non-redundant, and retained — replacing raw tokens or tool calls as the scaling coordinate when comparing two agent harnesses."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - effective feedback compute
  - trace-level scaling coordinate
last_reviewed: 2026-06-12
maturity: established
---

# Effective Feedback Compute (EFC) for Harness Comparison

> Effective Feedback Compute credits only feedback that is informative, valid, non-redundant, and retained — a trace-level coordinate for comparing two agent harnesses.

## The Measurement Problem

Raw tokens, tool calls, and wall time conflate useful work with retries and noise. On the same agent traces, raw tokens and tool calls explained R² = 0.33 and R² = 0.42 of success variance, while oracle EFC reached R² = 0.94 and estimated EFC R² = 0.99 ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)) — most spend never moves the agent's posterior. EFC credits an event only if it meets the four conditions below, then normalises by task feedback demand so unlike tasks compare.

## The Four Conditions

A trace event counts toward EFC only if it is:

| Condition | What it means | What it filters out |
|---|---|---|
| **Informative** | Changes the posterior — signal not already implied by prior context | A re-read of the same file; a critique restating an accepted fact |
| **Valid** | Survives a downstream check | A hallucinated tool result; an assertion the verifier rejects |
| **Non-redundant** | Not duplicated by an earlier credited event | A second `ls` of the same directory; an error two retries both print |
| **Retained** | A later action depends on it | Output the agent never reads back; reasoning it overwrites |

The composition is load-bearing. Drop *informative* and the metric rewards noisy logs; drop *valid* and it rewards confident hallucinations; drop *non-redundant* and it rewards retry storms; drop *retained* and it rewards reasoning the agent never used ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).

## Why It Works

Success depends on the task posterior converging on the right solution before the budget runs out. Raw spend measures the *opportunity* for that posterior to update, not the update itself; re-reads, identical-error retries, and fact-restating critiques change no posterior and yield no success gain — and EFC subtracts exactly those events. Iterative Agent Decoding reaches the same conclusion from another angle: inserting feedback between decoding steps beats best-of-N by up to 10 percentage points under matched compute, because best-of-N spends it on near-identical posteriors ([Chen et al., 2025](https://arxiv.org/abs/2504.01931)).

In matched-budget interventions, redirecting the same budget toward EFC-credited events lifted success from a 27% baseline to 90% ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)) — the model did not change, only which events the harness produced.

## Where to Use It

Use EFC as the scaling coordinate when:

- **Comparing two candidate harnesses on the same benchmark.** EFC controls for a harness's tendency to manufacture cheap-looking compute; the harness that hits the same success rate at lower EFC is the better one.
- **Driving a [harness hill-climbing](harness-hill-climbing.md) loop.** Optimise success-per-unit-EFC, not success-per-token — the latter rewards changes that suppress useful retries alongside useless ones.
- **Diagnosing a plateau.** High raw spend with low EFC says the bottleneck is feedback quality, not budget; raising the cap will not help.

This fits the broader argument that harness changes drive late-stage gains more than model upgrades, and need a metric that tracks harness quality, not throughput ([Gu, 2026](https://arxiv.org/abs/2605.26112)).

## When This Backfires

EFC is a comparison and diagnostic coordinate, not a runtime spend controller; treat it as the latter and it fails predictably.

- **Verifier-free domains.** Without a feedback validator the *valid* gate degenerates to LLM-as-judge, inheriting judge variance and losing the monotonicity a stable optimisation target needs ([Setlur et al., 2025](https://arxiv.org/abs/2502.12118)).
- **Short-horizon single-turn tasks.** With no multi-step trace, EFC collapses to "did the final answer pass" — no signal beyond raw success rate.
- **Cost-bounded production enforcement.** Operators pay per token, not per EFC unit; a miscalibrated estimator can authorise unplanned spend, so keep deterministic raw-spend caps for cost.
- **Adversarial or injected feedback.** The *informative* gate weights the most surprising signals, so an attacker crafting surprising tool outputs (per the [lethal trifecta](../security/lethal-trifecta-threat-model.md)) scores *higher* and pulls the harness toward the attack. Pair EFC with feedback provenance.
- **Cross-task-family comparisons.** The task-demand normaliser is itself estimated; comparing one harness across task families inherits that error and the numbers stop being meaningful ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).
- **Long traces with context-ceiling degradation.** A window saturated with low-quality retained state degrades performance even as EFC climbs; EFC misses the [convergence-detection](convergence-detection.md) signal, so add a separate plateau check ([Li et al., 2026](https://arxiv.org/abs/2602.18998)).

## Building a Coarse EFC Counter

The paper's full estimator stack is research-grade, but a cheap coarse counter captures most of the diagnostic value:

- **Informative** — hash each tool input; reject events whose hash matches a credited earlier event.
- **Valid** — count only events whose downstream assertion or test passes in-trace.
- **Non-redundant** — deduplicate tool *outputs* by content hash; count one per re-issued call.
- **Retained** — require the output to reappear (literally or by summary) in a later agent message.

Wired this way it recovers the rank order of harness candidates without solving estimator calibration — reach for it inside a hill-climbing loop before building the full estimator.

## Key Takeaways

- Raw tokens and tool calls explain a third to under half of success variance; EFC explains nearly all of it ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).
- The four gates — informative, valid, non-redundant, retained — are load-bearing as a composition; each alone is insufficient.
- Use EFC for harness comparison, hill-climbing, and plateau diagnosis; keep raw-spend caps for cost enforcement.
- It inherits a verifier-quality bottleneck and a context-ceiling blind spot — pair it with feedback provenance and a separate convergence check.
- A coarse counter (input-hash, verifier-pass, output-dedup, retention) recovers harness rank order without the full estimator stack.

## Related

- [Harness Hill-Climbing](harness-hill-climbing.md) — the optimisation loop EFC is meant to score
- [Feedback as Capability Equalizer](feedback-capability-equalizer.md) — the broader claim that feedback quality outranks model scale
- [Dual-Budget Control for Search Agents](dual-budget-control-search-agents.md) — value-of-information budgeting; the runtime counterpart to EFC's offline measurement
- [Reasoning Budget Allocation](reasoning-budget-allocation.md) — concrete harness change whose payoff EFC can attribute
- [Convergence Detection](convergence-detection.md) — the plateau-stopping signal EFC does not capture
- [Isometric Harness Ablation](isometric-harness-ablation.md) — the fixed-model, one-subsystem-at-a-time way to attribute the EFC change a harness edit produced
