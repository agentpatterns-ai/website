---
title: "Runtime Workflow Selection Across Models (Project HydraFusion)"
term: "Runtime Workflow Selection"
description: "Pick the orchestration shape per request (single call, cascade, or cross-family critique) instead of pinning one model. The published payoff is cost at parity, not better answers."
tags:
  - multi-agent
  - agent-design
  - cost-performance
  - copilot
aliases:
  - runtime orchestration shape selection
  - per-request workflow routing
  - compound model workflow selection
last_reviewed: 2026-09-05
maturity: emerging
---

# Runtime Workflow Selection Across Models (Project HydraFusion)

> Runtime workflow selection picks the orchestration shape for each request: one model, a cheap-first cascade, or a cross-family critique loop.

Runtime workflow selection moves a hand-made decision into the harness: draft with one model, ask a second to review, escalate the hard cases. A selection layer makes that choice per request. On the only published evidence the payoff is cost, at roughly equal quality. GitHub's Project HydraFusion has been a research preview in Copilot CLI since 4 September 2026. Against a Claude Opus 5 baseline it cut estimated workflow cost by 36% to 67% across three agentic coding benchmarks. It improved quality on one of the three ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)).

## The three shapes

HydraFusion chooses one of three execution patterns for each request ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)):

- Single: one selected model solves the task directly.
- Cascade: an efficient model drafts a solution, and a quality gate decides whether to accept it or escalate to a stronger model.
- Critique: one model drafts a result, an independent read-only critic from a different model family reviews it, and the drafting model revises once.

Each shape already has a name in practice. The selection layer is the new part. The harness reads capability signals for reasoning, code generation, debugging, and tool use, then picks the least complex shape expected to clear the quality bar. GitHub fitted that policy with beam search against a frozen baseline rather than hand-tuned thresholds. Review steps run in tool-less contexts, so a critic cannot touch the repository. Billing is unchanged: each model is priced at its standard rate, so the saving comes from calling the expensive model less often ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)).

## What the published numbers support

| Benchmark | Cost vs Opus 5 | Quality vs Opus 5 |
|---|---|---|
| TerminalBench 2.1 | 67% lower | +4.9 points |
| DeepSWE | 36% lower | -1.5 points |
| CheckpointBench | 65% lower | -0.1 points |

Read the quality column first. Two of the three benchmarks came in below the pinned frontier model. GitHub's own summary is the accurate one: HydraFusion "matched or exceeded the evaluated Opus 5 baseline while reducing estimated workflow cost." The post then discounts its single quality win, noting that TerminalBench 2.1's "relative saturation makes broader validation important" ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)).

Two scope limits travel with those figures. The runs are controlled offline evaluations tied to fixed benchmark revisions, workflow configurations, model pool, and pricing assumptions. Every model ran at the same medium reasoning level. The claim to carry forward is parity at 36% to 67% lower cost; a quality gain is not yet established.

## Why it works

The cost mechanism is cascade economics. Most requests are solvable by the cheaper model, so the expensive one is invoked only on the residual that fails the acceptance gate, and spend tracks the escalation rate rather than the request count. FrugalGPT formalized this and matched the best individual LLM of its day at up to 98% lower cost ([arxiv 2305.05176v1](https://arxiv.org/abs/2305.05176v1)). The wider design space is mapped in [Dynamic Model Routing and Cascading for Efficient LLM Inference (arxiv 2603.04445v3)](https://arxiv.org/abs/2603.04445v3).

The quality mechanism rests on independence, not on extra calls. A model reviewing its own output has no external signal, and intrinsic self-correction degrades reasoning: LLMs "struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction" ([arxiv 2310.01798v2](https://arxiv.org/abs/2310.01798v2)). Drawing the critic from a different model family, in a context with no tools and no repository access, is what supplies that missing signal.

## When this backfires

- Quality is the binding constraint. On DeepSWE, which covers repository-level work, the trade was 1.5 points of verified task quality for 36% off the bill. Where one missed fix costs more than a month of inference, that trade is backwards.
- The loop is interactive. Cascade and critique add serial model calls, and the preview holds intermediate drafts back until a final result is ready. GitHub calls the resulting wait "a real trade-off for developers" ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)).
- Sessions are multi-turn. The preview is scoped to first-turn, single-prompt coding tasks, and strong multi-turn performance is named as future work ([GitHub Blog, 2026-09-04](https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)).
- The critic cannot outrank the drafter. Cross-model exchange is not free improvement. Debate "can lead to a decrease in accuracy over time", with models shifting "from correct to incorrect answers in response to peer reasoning, favoring agreement over challenging flawed reasoning" ([arxiv 2509.05396v2](https://arxiv.org/abs/2509.05396v2)). The drafter performs the revise step, which is exactly where that failure lands.
- You cannot measure quality per request. The cost dashboard turns green on day one. Without a quality signal per shape, a routing regression stays invisible for months, which is the failure documented in [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md).

## Key Takeaways

- Adopt shape selection to spend less at the same quality. Adopting it to raise quality is not supported by the published evidence.
- Log which shape ran and grade quality per shape. Aggregate cost tells you nothing about whether the gate is accepting bad drafts.
- Keep a pinned frontier model available for work where a 1.5-point quality drop costs more than the inference it saves.
- The critic must come from a different model family and hold no tools. A same-family or self-review step removes the mechanism the pattern depends on.

## Related

- [Within-Task Model Cascade: Designing the Escalation Gate](../../loop-engineering/within-task-model-cascade.md) — how to build the acceptance gate the cascade shape depends on.
- [Adversarial Multi-Model Development Pipeline (VSDD)](adversarial-multi-model-pipeline.md) — the critique shape run to convergence instead of for a single revision.
- [Auto Model Selection](../agent-design/auto-model-selection.md) — the earlier Copilot layer that picks a model per request rather than a workflow.
- [Routing Break-Even: When a Cheaper Model Actually Pays](../agent-design/routing-break-even.md) — the arithmetic deciding whether the gate's own cost is affordable.
- [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md) — what happens when the cost win is measured and the quality cost is not.
