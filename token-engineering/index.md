---
title: "Token Engineering: Fewer, Cheaper Tokens Without Losing Quality"
description: "The cross-cutting discipline of getting the same result for fewer, cheaper tokens — the right model, the right token, the right cache, at the right time — without degrading output."
tags:
  - token-engineering
  - index
last_reviewed: 2026-06-29
---

# Token Engineering

> Token engineering gets the same result for fewer, cheaper tokens — routing to the right model and trimming each call, without degrading output.

Cost is now a first-order constraint on agentic coding, but the techniques that control it are scattered — model routing, effort budgets, prompt compression, caching discipline, token-efficient output, small-model offload, batch scheduling. Token engineering is the name for that cluster: the deliberate practice of spending fewer *expensive* tokens at the *wrong time*, while holding output quality fixed.

It cuts across the site. The canonical treatment of each technique still lives in its home discipline — [context engineering](../context-engineering/index.md), [agent design](../agent-design/index.md), [tool engineering](../tool-engineering/index.md), [observability](../observability/index.md). This section owns the pages whose primary subject *is* token cost, and crosswalks the rest under one frame so you can navigate "how do I cut token spend without losing quality?" as a single topic.

## What token engineering is — and isn't

- It is the optimisation goal: same task outcome, fewer/cheaper tokens. Every technique below carries an implicit "without degrading the end result" clause.
- It is not [context engineering](../context-engineering/context-engineering.md). Context engineering decides *what information enters the window* for quality and reliability; token engineering is the cost-and-efficiency lens *over* those decisions. They overlap (lean context is cheaper) but answer different questions.
- It is not generic cost-performance. The `cost-performance` tag spans latency, throughput, and infra; token engineering is specifically about the *token* as the unit of spend.
- The quality constraint is the whole point. Cutting tokens can backfire — see [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md), the guardrail every technique here must respect.

## The crosswalk

The frame is four "rights" — the right model, the right token, the right cache, at the right time — plus three supporting levers (effort scaling, small-model offload, measurement).

### Right model — routing

Send each task to the cheapest model and tier that still passes, escalating only on failure.

- [Routing Decision Framework](routing-decision-framework.md) — the selection map over the routing pages below: pick by dominant signal (complexity, blast radius, latency, cost)
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — the cornerstone: match model capability to task complexity, escalate on validation failure
- [Gateway Model Routing](../agent-design/gateway-model-routing.md) — one gateway knob drives both the inference target and the model picker
- [Auto Model Selection](../agent-design/auto-model-selection.md) — hand per-task model choice to the harness
- [Cross-Vendor Competitive Routing](../agent-design/cross-vendor-competitive-routing.md) — race competing vendors, gate on the winner
- [Model-Neutral Agent Architecture](../agent-design/model-neutral-agent-architecture.md) — keep the agent portable so routing stays a config decision
- [Multi-Shape BYOK Provider](../agent-design/multi-shape-byok-provider.md) — bring-your-own-key routing across provider shapes
- [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) — one delegation plan that jointly optimises decompose, worker, and budget
- [Self-Healing Tool Routing](../tool-engineering/self-healing-tool-routing.md) — route around failing tools before they burn retries

### Right token — lean context and output

Shrink what each call has to carry, on both the input and output sides.

- [Token-Efficient Tool Design](token-efficient-tool-design.md) — each tool call injects the minimum tokens for the next decision
- [Token-Efficient Code Generation](token-efficient-code-generation.md) — idiomatic structure beats "be concise" prompting
- [Tokenizer Swap Tax](tokenizer-swap-tax.md) — budgeting for migrations that change token counts under flat per-token pricing
- [Prompt Compression](../context-engineering/prompt-compression.md) — maximise signal per token in instructions
- [Semantic Density Optimization](../context-engineering/semantic-density-optimization.md) — raise task-relevant tokens per byte in the codebase
- [Context Budget Allocation](../context-engineering/context-budget-allocation.md) — treat context as a finite budget across sources

### Right cache — caching discipline

Structure prompts so the cacheable prefix stays stable and hits.

- [Prompt Caching: Architectural Discipline for Agents](../context-engineering/prompt-caching-architectural-discipline.md) — design for cache hits and cross-provider cache economics
- [Static Content First to Maximize Cache Hits](../context-engineering/static-content-first-caching.md) — order stable content first so the prefix caches
- [Exclude Dynamic System Prompt Sections](../context-engineering/exclude-dynamic-system-prompt-sections.md) — move per-machine context out so fleets share one cache entry
- [KV Cache Invalidation in Local Inference](../context-engineering/kv-cache-invalidation-local-inference.md) — attribution headers that silently break the KV cache

### Right time — temporal routing

Route non-urgent work into cheaper capacity windows. Batch APIs are the concrete cost primitive: Anthropic's Message Batches and OpenAI's Batch API both run jobs asynchronously at a 50% discount, completing within 24 hours — typically under an hour for Anthropic ([Anthropic — Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing); [OpenAI — Batch API](https://developers.openai.com/api/docs/guides/batch)). Work that can wait — overnight evals, doc refreshes, bulk refactors, research passes — belongs in those windows.

- [Temporal Token Routing: Batch and Flex Tiers for Non-Urgent Work](temporal-token-routing.md) — the right-time decision: which workload class belongs in batch, flex, or the synchronous tier
- [Idle-Time Speculative Planning](../agent-design/idle-time-speculative-planning.md) — use idle compute to pre-plan likely next steps
- [Background TODO Agent](../agent-design/background-todo-agent.md) — defer non-urgent work to a background agent
- [Programmatic Cloud Agent Dispatch](../workflows/programmatic-cloud-agent-dispatch.md) — schedule deferred agent runs into cheaper capacity

This axis is the freshest and least covered today — see the spin-off issues for deeper pages on eval-gated scheduling.

### Effort and budget scaling

Spend reasoning compute in proportion to task difficulty, not uniformly.

- [Reasoning Budget Allocation](../agent-design/reasoning-budget-allocation.md) — the reasoning sandwich: heavy planning and verification, light execution
- [Heuristic-Based Effort Scaling](../agent-design/heuristic-effort-scaling.md) — encode effort rules in the system prompt
- [Per-Call Budget Hints on Tool Invocations](../agent-design/per-call-budget-hints-tool-calls.md) — raise the cap on one dense, infrequent call
- [Per-Tool Extended Reasoning Opt-In](../agent-design/per-tool-extended-reasoning-opt-in.md) — tool-call-scoped reasoning budgets

### Small-model offload

Push verbose intermediate work to a cheaper model and return a compact result.

- [Specialized Small Language Models as Agent Sub-Tools](../agent-design/specialized-slm-as-agent-tool.md) — an SLM absorbs raw bytes; the orchestrator never sees them
- [Compositional Skill Routing](../context-engineering/compositional-skill-routing.md) — route across a large skill library without loading it all

### Measurement and visibility

You cannot reduce what you do not measure — instrument spend before cutting it.

- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the instrument-attribute-fix-verify loop
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — plot each configuration on the (cost, quality) frontier so quality-trading downgrades are visible
- [Code Cleanliness as an Agent Cost Lever](code-cleanliness-agent-cost-lever.md) — cleaner code cut token use 7-8% with no pass-rate change
- [Per-Plugin Token-Cost Attribution](../observability/plugin-token-cost-attribution.md) — attribute spend down to the plugin
- [BYOK Model Token Visibility](../observability/byok-model-token-visibility.md) — in-IDE token and context telemetry for BYOK routes

## Related

- [Concept Map](../concepts.md) — all site content grouped by theme
- [Context Engineering](../context-engineering/index.md) — the canonical home for lean-context techniques
- [Agent Design](../agent-design/index.md) — routing, effort, and offload patterns live here
- [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md) — the quality guardrail this section must respect
