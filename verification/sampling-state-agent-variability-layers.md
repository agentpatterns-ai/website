---
title: "Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)"
term: "Variability Layer Decomposition"
description: "Separate run-to-run agent variability into token-sampling, infrastructure, and orchestration-state layers — a single trajectory cannot tell you which one to fix."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - "agent variability decomposition"
  - "sampling vs orchestration state variance"
  - "intrinsic and orchestration variance"
last_reviewed: 2026-06-12
maturity: adopted
---

# Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)

> Run-to-run agent variability has at least three distinct layers — separate them before picking a mitigation, because lowering temperature does not fix an orchestration-state cascade.

This pattern pays off only when three conditions hold: the agent runs a real multi-step orchestration loop (not a single model call), you control enough of the stack to act on the attribution, and the mitigation cost is justified by the decision. Single-shot or hosted-API-only workloads should skip to [pass@k and pass^k metrics](pass-at-k-metrics.md) and accept the aggregate spread.

When they hold, decomposition is the framework Hydari & Iqbal (2026) propose for validating non-deterministic coding agents: trace the variability to the layer where the mitigation lives, instead of tuning whichever knob is most visible [Source: [Hydari & Iqbal, *The Token Not Taken*](https://arxiv.org/abs/2606.08998)].

## The three layers

| Layer | What varies | What fixes it |
|---|---|---|
| Intrinsic (token sampling) | Per-step stochastic selection over the next-token distribution at temperature > 0 | Lower temperature, fix the seed (where supported), greedy decode |
| Extrinsic (infrastructure) | Floating-point reduction order across hardware, kernels, and server batch size — drifts even at temperature 0 | Batch-invariant kernels, pinned hardware, fixed-batch inference |
| Orchestration state | Across-step accumulation of tool outputs, errors, and context that conditions every subsequent step | Tighter system prompt, deterministic tools, narrower state surface, retries with reset |

Practitioners reach for the intrinsic layer first because temperature is the most visible knob. The extrinsic layer is invisible from the API surface: [Thinking Machines (2025)](https://simonwillison.net/2025/Sep/11/defeating-nondeterminism/) showed that even at temperature 0 hosted endpoints drift because the forward pass is not batch-invariant — server batch size changes the floating-point reduction order in normalization, matmul, and attention. The orchestration-state layer compounds: each step's intrinsic noise becomes the next step's deterministic input.

## Why it works

A single trajectory cannot distinguish the layers because each step's intrinsic noise becomes the next step's deterministic state. The paper's mechanism: sampling introduces stochasticity at each token, and when agents iterate it compounds across steps because the state encodes every prior decision [Source: [Hydari & Iqbal](https://arxiv.org/abs/2606.08998)]. Holding one layer constant while varying the others gives the attribution:

- Isolate intrinsic: fix the prompt and tool sequence, then vary the seed (or run many times at fixed temperature). Remaining variance is sampling-driven.
- Isolate extrinsic: fix the prompt, run at temperature 0, and vary the server-side batch size (or compare inference backends). Remaining variance is infrastructure-driven.
- Isolate orchestration state: fix the prompt and use greedy decoding, then perturb the tool outputs or context order between runs. Remaining variance is state-driven.

The independent agentic-eval study found single-run pass@1 standard deviations exceeding 1.5 percentage points even at temperature 0, "because trajectories diverge early, often within the first few percent of tokens, and these small differences cascade into different solution strategies" [Source: [arXiv:2602.07150](https://arxiv.org/abs/2602.07150v3)]. That cascade is the orchestration-state layer; the early divergence is the intrinsic layer that seeds it.

## When this backfires

The decomposition adds cost — at least one extra controlled run per layer isolated, plus the infrastructure to vary one layer at a time. It does not pay off in several conditions:

- Hosted-API consumers with no infrastructure control: Anthropic, OpenAI, and Google do not expose batch size, stable seeds, or kernel variants to API clients in 2026. Intrinsic and extrinsic attribution is operationally indistinguishable, so the only mitigation is multi-run characterization regardless of layer.
- Single-step or short-horizon agents: when the agent emits one model call with no tool-loop iteration, the orchestration-state layer is empty. There is no across-step state for [Markov-chain reliability](markov-chain-agent-reliability.md) to model, so attribution adds effort without changing what you can do about the variance.
- Latency-critical or single-shot tasks: CI gating, code completions, and one-shot migration scripts cannot pay the multi-run cost. Fall back to aggregate [pass@k and pass^k metrics](pass-at-k-metrics.md), tighten guardrails so any single run is acceptable, and do not decompose its variance.
- External non-determinism dominant: when tool outputs are themselves stochastic (web search, third-party APIs, timing-dependent state), the dominant variance is outside all three layers. The framework then misattributes external noise to whichever layer happens to be isolated when the external source is quiet.
- Model-version drift underneath: silent endpoint updates and A/B routing introduce a fourth layer (model identity) that the paper does not address. If you suspect drift, compare a frozen baseline against the live endpoint with [behavioral testing](behavioral-testing-agents.md) before attributing variance to any named layer.

The dominant misattribution is treating a batch-invariance drift as a temperature problem and lowering temperature until the variance is too small to notice — leaving the bug in place and burning capability headroom. The second is treating an orchestration-state cascade as flaky-test variance and re-running for a green build, which never converges because the state surface keeps growing.

## Key Takeaways

- Run-to-run agent variability is not one signal — it is at least three layers (token sampling, infrastructure, orchestration state) that require different mitigations.
- A single trajectory cannot distinguish the layers; isolate one at a time by holding the others fixed.
- Temperature 0 does not give you reproducibility on hosted endpoints because the forward pass is not batch-invariant — variability at T=0 is an extrinsic signal, not a sampling one.
- Decomposition pays off only with a multi-step orchestration loop, enough stack control to act, and mitigation cost justified by the decision. Otherwise, use aggregate metrics and accept the spread.
- The two costly misattributions are lowering temperature to mask a batch-invariance bug and re-running tests to mask an orchestration-state cascade.

## Related

- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md)
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md)
- [Markov-Chain Reliability for LLM Agents](markov-chain-agent-reliability.md)
- [Behavioral Testing for Non-Deterministic AI Agents](behavioral-testing-agents.md)
- [Dominator-Graph Trajectory Invariants](dominator-graph-trajectory-invariants.md)
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md)
- [Specification-Path Testing: Same Contract, Different History](specification-path-testing.md) — specification path as a further variability source, held constant in this taxonomy
- [Multi-Run, Shuffled-Order Evaluation for Self-Improving Agents](multi-run-shuffled-order-evaluation.md) — task order as an orchestration-state variable when the agent writes memory between tasks
