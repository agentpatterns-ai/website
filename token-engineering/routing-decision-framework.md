---
title: "Routing Decision Framework: Which Routing Pattern Fits Which Signal"
term: "Routing Decision Framework"
description: "Pick the right routing pattern by the dominant signal — task complexity, blast radius, latency tolerance, or cost ceiling — without restating each routing page."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - model routing decision matrix
  - model tier selection map
  - routing pattern selection map
last_reviewed: 2026-06-29
maturity: adopted
---

# Routing Decision Framework

> Pick the routing pattern that fits your dominant signal — complexity, blast radius, latency, or cost — instead of stacking every routing page.

The [token engineering hub](index.md) lists eight routing pages under its "right model" axis but does not tell you which one to reach for first. This page is the selection map over those pages: each row names a routing pattern and the dominant signal that should pull you to it. It does not restate any of the linked pages — every cell is a pointer.

It follows the same model as the established [Pattern Selection Map](../patterns/selection-map.md): one matrix, every row a link, picked by the dominant trade-off. Use it the same way — once, to pick, not as a recommendation engine.

## The decision matrix

| Routing pattern | Dominant signal | Decision shape | Best when | Worst when |
|---|---|---|---|---|
| [Cost-Aware Agent Design](cost-aware-agent-design.md) | Task complexity | Per-task tier choice (Haiku / Sonnet / Opus) with escalation on validation failure | The workload has a wide complexity distribution and a cheap deterministic validator (linter, tests) gates escalation | Validation is expensive or absent — silent quality regressions go uncaught |
| [Gateway Model Routing](../patterns/agent-design/gateway-model-routing.md) | Infrastructure portability | One gateway endpoint serves inference *and* publishes the model catalog | You run a multi-tenant or BYOK fleet and want one config knob, not a per-harness model list | You have a single fixed model and adding a gateway is pure overhead |
| [Auto Model Selection](../patterns/agent-design/auto-model-selection.md) | Vendor capacity / plan policy | Hand per-request model choice to the harness's vendor-side broker | Executor-class work on a vendor that ships Auto modes and you trust the policy | Long sessions or eval-gated CI where you need a pinned model for reproducibility |
| [Cross-Vendor Competitive Routing](../patterns/agent-design/cross-vendor-competitive-routing.md) | Capability uncertainty | Run competing vendor agents on the same task in parallel; gate on the winner | You don't yet know which vendor's profile fits a task class and the team can review both outputs | Cost ceiling is tight — you pay every vendor and only ship one result |
| [Parsimonious Agent Routing](../patterns/multi-agent/parsimonious-agent-routing.md) | Decomposition + budget jointly | One learned planner emits a delegation plan: keep, single-route, or split-and-route, with per-branch budget | Multi-agent fan-out where decompose, worker, and budget are currently fixed at design time | Single-agent tasks — there is nothing to decompose |
| [Self-Healing Tool Routing](../tool-engineering/self-healing-tool-routing.md) | Tool reliability | Route around failing tools before retries burn the budget | Production agents with intermittent tool failures and a feedback signal | Stable tool surface where every call succeeds — pure overhead |
| [Model-Neutral Agent Architecture](../patterns/agent-design/model-neutral-agent-architecture.md) | Vendor portability | Keep the agent itself portable so routing stays a configuration decision | You expect to switch or add vendors and want routing to never touch agent code | A single-vendor fleet you have no plan to leave |
| [Multi-Shape BYOK Provider](../patterns/agent-design/multi-shape-byok-provider.md) | API-envelope capability preservation | Declare which API envelope (Chat Completions, Responses, Messages) each BYOK endpoint speaks, per endpoint | You run a BYOK fleet where down-translating to a single envelope silently drops vendor capability | A single-vendor, single-shape deployment — no envelope mismatch to preserve against |

## Inputs to the decision

The four signals that practitioner sources converge on ([Merge.dev — LLM Routing](https://www.merge.dev/blog/llm-routing); [MindStudio — Three-Tier LLM Routing](https://www.mindstudio.ai/blog/set-up-ai-model-router-llm-stack-c2610)):

- Task complexity — how hard the task is on average, and the variance across tasks. Wide variance pulls you toward [Cost-Aware Agent Design](cost-aware-agent-design.md); flat distributions don't need tier routing at all.
- Blast radius — what a wrong route costs. Read-only exploration tolerates a cheap-tier miss; writes against production do not. Blast-radius framing comes from the [Pattern Selection Map](../patterns/selection-map.md) axis legend.
- Latency tolerance — synchronous IDE work has a tight budget; deferrable bulk runs (overnight evals, refactors, doc refreshes) belong in [batch APIs at 50% discount](index.md#right-time--temporal-routing) rather than tier routing.
- Cost ceiling — the absolute spend cap. A team without a ceiling will not invest in routing; a team that has one needs the [per-plugin token-cost attribution](../observability/plugin-token-cost-attribution.md) before any router decision is trustworthy.

## Why It Works

The framework is cognitive offloading over the eight routing pages, not new mechanism. The cost mechanism each row exploits is already proven: [FrugalGPT](https://arxiv.org/abs/2305.05176) reports LLM cascade routing can match GPT-4 with up to 98% cost reduction, or improve accuracy by 4% at equivalent cost. The framework's contribution is matching each row to its dominant signal so the practitioner picks once instead of reading every routing page in sequence and stacking patterns blindly — the failure mode the [Pattern Selection Map](../patterns/selection-map.md) exists to defuse for patterns generally.

The selection logic itself has a quantitative grounding. [Triage (arxiv 2604.07494)](https://arxiv.org/abs/2604.07494) gives the explicit feasibility condition for tier routing: the light-tier pass rate on the routed tasks must exceed the inter-tier cost ratio. Below that threshold, rework costs more than the savings. That is the same threshold every row in the matrix implicitly assumes.

## When This Backfires

Four documented failure modes. Each one is the reason the matrix is a *picker*, not a recommendation engine.

- Workload below the feasibility threshold. If the light-tier pass rate on your tasks falls below the inter-tier cost ratio, every routing pattern in the matrix is a net loss — the cheap-tier failures generate rework that outweighs the savings ([Triage, arxiv 2604.07494](https://arxiv.org/abs/2604.07494)). Measure pass rates by tier on a representative sample before committing to a router.
- Unmeasured cost-driven routing. Routing to cheaper models without per-tier quality signals turns the cost dashboard green while customer-visible quality silently decays for months — the [Cost-Driven Model Routing Without Quality Monitoring](../patterns/anti-patterns/cost-routing-without-quality-monitoring.md) anti-pattern. The framework only works if the routing pattern you pick comes with the eval gate that proves the route was right.
- Static routers in agentic loops. Treating routing as a one-off classification is the [Agent-as-a-Router (arxiv 2606.22902)](https://arxiv.org/abs/2606.22902) information-deficit critique: the router cannot accumulate execution-grounded feedback, so the decision degrades as the workload drifts. Routing decisions in long-horizon agent loops need a Context-Action-Feedback loop, not a fixed table.
- Routing opacity as a debugging tax. Current routers present model assignments as opaque decisions ([Explainable Model Routing, arxiv 2604.03527](https://arxiv.org/abs/2604.03527)). When quality regresses, the team cannot distinguish "the router picked wrong" from "the cheap tier was always going to miss this." Production deployments need the routing decision plus the rationale recorded alongside the model output.

## Key Takeaways

- One matrix, one pick — the framework exists so you choose one routing pattern by its dominant signal, not so you stack all eight.
- The Triage feasibility condition (light-tier pass rate > inter-tier cost ratio) gates whether to route at all. If your workload fails it, no row in the matrix saves you money.
- Every routing pattern needs the eval gate that proves the route was right — the [unmeasured cost-routing anti-pattern](../patterns/anti-patterns/cost-routing-without-quality-monitoring.md) is the failure mode that hides a quality regression behind a green cost dashboard.
- The matrix is the start, not the end — static routers degrade in long-horizon loops; production routers close the Context-Action-Feedback loop ([Agent-as-a-Router, arxiv 2606.22902](https://arxiv.org/abs/2606.22902)).

## Related

- [Cost-Aware Agent Design](cost-aware-agent-design.md) — the complexity-routing row's canonical page
- [Gateway Model Routing](../patterns/agent-design/gateway-model-routing.md) — the infrastructure-portability row's canonical page
- [Auto Model Selection](../patterns/agent-design/auto-model-selection.md) — the vendor-capacity row's canonical page
- [Cross-Vendor Competitive Routing](../patterns/agent-design/cross-vendor-competitive-routing.md) — the capability-uncertainty row's canonical page
- [Parsimonious Agent Routing](../patterns/multi-agent/parsimonious-agent-routing.md) — the joint-decomposition-and-budget row's canonical page
- [Pattern Selection Map](../patterns/selection-map.md) — the model this page applies to routing specifically
- [Cost-Driven Model Routing Without Quality Monitoring](../patterns/anti-patterns/cost-routing-without-quality-monitoring.md) — the anti-pattern every row in this matrix assumes you have already defused
