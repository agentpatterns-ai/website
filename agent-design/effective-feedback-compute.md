---
title: "Effective Feedback Compute (EFC) for Harness Comparison"
description: "Count only the feedback that is informative, valid, non-redundant, and retained — replacing raw tokens or tool calls as the scaling coordinate when comparing two agent harnesses."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - effective feedback compute
  - trace-level scaling coordinate
last_reviewed: 2026-05-30
---

# Effective Feedback Compute (EFC) for Harness Comparison

> Effective Feedback Compute credits only feedback that is informative, valid, non-redundant, and retained — a trace-level coordinate for comparing two agent harnesses.

## The Measurement Problem

Raw tokens, tool calls, operations, and wall time conflate useful work with retries and noise. On the same set of agent traces, raw tokens and tool calls explained R² = 0.33 and R² = 0.42 of success variance; an oracle Effective Feedback Compute coordinate reached R² = 0.94 and an estimated EFC reached R² = 0.99 ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)). The gap is the signature of the diagnosis: most of an agent's spend does not move the agent's posterior over the task.

EFC credits a feedback event only when it satisfies all four conditions below, then normalises the credited total by the task's feedback demand so two unlike tasks can be compared.

## The Four Conditions

A trace event counts toward EFC only if it is:

| Condition | What it means | What it filters out |
|---|---|---|
| **Informative** | Changes the agent's posterior over the task — adds signal not already implied by prior context | A re-read of the same file; a critique that restates an already-accepted fact |
| **Valid** | Survives a downstream check — the world supports it | A hallucinated tool result; a passing-looking assertion that the verifier rejects |
| **Non-redundant** | Not duplicated by an earlier credited event in the same trace | A second `ls` of the same directory; the same error message printed by two retries |
| **Retained** | Influences a subsequent decision — the agent's next action depends on it | Tool output the agent never reads back; reasoning the agent immediately overwrites |

The four-gate composition is the load-bearing part. Drop *informative* and the metric rewards noisy logs; drop *valid* and it rewards confident hallucinations; drop *non-redundant* and it rewards retry storms; drop *retained* and it rewards reasoning the agent never used ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).

## Why It Works

Agent success depends on the posterior over the task converging on the correct solution before the budget runs out. Raw spend measures *opportunity* for that posterior to update, not the update itself. Re-reading the same file, retries that emit identical errors, and critique rounds that restate accepted facts produce no posterior change and no expected success gain. EFC subtracts exactly those events.

Independent work on Iterative Agent Decoding reaches the same conclusion from a different angle: inserting feedback between decoding steps beats best-of-N sampling by up to 10 percentage points under matched compute, because best-of-N spends additional compute on samples whose posteriors are near-identical ([Chen et al., 2025](https://arxiv.org/abs/2504.01931)).

The empirical pay-off shows up in matched-budget interventions: starting from 27% baseline success, redirecting the same budget toward EFC-credited events lifted success to 90% ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)). The model did not change; the harness changed which events it produced.

## Where to Use It

Use EFC as the scaling coordinate when:

- **Comparing two candidate harnesses on the same multi-turn benchmark.** EFC controls for the harness's tendency to manufacture cheap-looking compute. A harness that hits the same success rate with lower EFC is the better harness.
- **Driving a [harness hill-climbing](harness-hill-climbing.md) loop.** Each candidate change should improve success-per-unit-EFC, not success-per-token. The latter rewards changes that suppress useful retries alongside useless ones.
- **Diagnosing why a harness plateaus.** A trace with high raw spend and low EFC tells you the bottleneck is feedback quality, not budget; raising the cap will not help.

This is consistent with the broader system-scaling argument: harness changes — context governance, trustworthy memory, dynamic skill routing — drive late-stage gains more than further model upgrades, and they need a metric that tracks harness quality, not raw throughput ([Gu, 2026](https://arxiv.org/abs/2605.26112)).

## When This Backfires

EFC is a comparison and diagnostic coordinate, not a runtime spend controller. Treat it as the latter and it fails in predictable ways.

- **Verifier-free domains.** The *valid* gate requires a feedback validator. In open-ended generation (creative writing, exploratory research) the gate degenerates to LLM-as-judge and inherits judge variance. The metric loses its monotonicity and stops being a stable optimisation target — the same problem identified for un-verified test-time scaling more broadly ([Setlur et al., 2025](https://arxiv.org/abs/2502.12118)).
- **Short-horizon single-turn tasks.** EFC collapses to "did the final answer pass" when there is no multi-step trace to score. Tracking it adds bookkeeping for zero signal beyond raw success rate.
- **Cost-bounded production enforcement.** Operators pay per token and per call, not per EFC unit. Replacing a deterministic spend cap with an EFC-budgeted controller injects estimator error into budget enforcement; a stale or miscalibrated EFC estimator can authorise spend that the operator did not plan for. Keep raw-spend caps for cost; use EFC for harness comparison.
- **Adversarial or injected feedback.** The *informative* gate weights signals that change the agent's posterior most. An attacker who crafts maximally surprising tool outputs (per the [lethal trifecta](../security/lethal-trifecta-threat-model.md)) scores *higher* on EFC and pulls the harness toward the attack. EFC must be paired with feedback provenance, never used alone.
- **Cross-task-family comparisons.** EFC normalises by task demand, which is itself estimated. Comparing two harnesses on the same task is sound; comparing one harness across different task families inherits demand-estimator error and the numbers are not directly meaningful ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).
- **Long sequential traces with context-ceiling degradation.** The *retained* gate counts feedback the agent kept — but a context window saturated with retained-but-low-quality state degrades performance even as EFC climbs. EFC does not capture the [convergence-detection](convergence-detection.md) signal; pair it with a separate plateau check ([Li et al., 2026 — Benchmark Test-Time Scaling of General LLM Agents](https://arxiv.org/abs/2602.18998)).

## Building a Coarse EFC Counter

Implementing the paper's full estimator stack is research-grade. A coarse counter that is cheap to wire produces most of the diagnostic value:

- **Informative** — hash each tool input and reject events whose input hash matches a credited event earlier in the trace.
- **Valid** — count only events whose downstream assertion or test passes within the same trace; discard events whose verifier rejected them.
- **Non-redundant** — deduplicate tool *outputs* by content hash; count one occurrence even when the agent re-issued the same call.
- **Retained** — require that the event's output text appears (literally or via summary reference) in a subsequent agent message.

A coarse counter wired this way recovers the rank order of harness candidates without solving the estimator-calibration problem. Use it inside a harness hill-climbing loop before investing in the paper's full estimator.

## Key Takeaways

- Raw tokens and tool calls explain a third to less than half of success variance across agent traces; EFC explains nearly all of it ([Zhang et al., 2026](https://arxiv.org/abs/2605.29682)).
- The four gates — informative, valid, non-redundant, retained — are load-bearing as a composition; each one alone is insufficient.
- Use EFC for harness comparison, harness hill-climbing, and plateau diagnosis. Keep raw-spend caps for cost enforcement.
- The metric inherits a verifier-quality bottleneck and a context-ceiling blind spot; pair it with feedback provenance and a separate convergence check.
- A coarse counter built from input-hash, verifier-pass, output-deduplication, and retention checks delivers most of the diagnostic value without the paper's full estimator stack.

## Related

- [Harness Hill-Climbing](harness-hill-climbing.md) — the optimisation loop EFC is meant to score
- [Feedback as Capability Equalizer](feedback-capability-equalizer.md) — the broader claim that feedback quality outranks model scale
- [Dual-Budget Control for Search Agents](dual-budget-control-search-agents.md) — value-of-information budgeting; the runtime counterpart to EFC's offline measurement
- [Reasoning Budget Allocation](reasoning-budget-allocation.md) — concrete harness change whose payoff EFC can attribute
- [Convergence Detection](convergence-detection.md) — the plateau-stopping signal EFC does not capture
