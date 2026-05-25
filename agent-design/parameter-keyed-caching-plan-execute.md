---
title: "Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines"
description: "Augment semantic cache keys with parsed parameters, disk-back the tool-discovery cache, and fan out dependency-independent plan steps — three orthogonal optimisations for parameter-rich, multi-MCP agent pipelines."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - temporal semantic caching
  - MCP workflow optimisation
  - parameter-aware cache key
  - dependency-aware step parallelism
---

# Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines

> For parameter-rich agent workloads that orchestrate multiple MCP servers, three orthogonal optimisations stack: augment the semantic cache key with parsed parameters, disk-back the tool-discovery step, and fan out plan steps that have no data dependency on prior steps.

## When This Pattern Earns Its Complexity

These optimisations target a narrow workload profile. Apply each only when its condition holds; otherwise the calibration overhead exceeds the latency win.

| Condition | Why it matters |
|---|---|
| Queries vary on temporal, asset, or sensor parameters | Plain semantic caching collapses parameter-distinguished queries into false hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| Plans coordinate across multiple MCP servers per query | Tool-discovery and selection dominate end-to-end latency in plan-execute pipelines ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| Generated plans contain genuinely independent steps | Dependency-aware parallelism degenerates to sequential-with-overhead when every step depends on the prior one |

The original evaluation is on AssetOpsBench — industrial asset operations with sensor data, work orders, and forecasting tools per query. Coding agents and generic chat assistants rarely meet the first condition.

## The Three Mechanisms

### 1. Parameter-Augmented Semantic Cache Key

Plain semantic caches hash the query embedding and serve any similar prior response. They fail on parameter-distinguished queries: "asset 7 failures *yesterday*" and "asset 7 failures *last month*" embed nearly identically — vocabulary dominates the vector; the temporal qualifier changes the correct answer.

Extract parameters before lookup and partition the cache key on them:

```
cache_key = embedding(query) + parsed(temporal) + parsed(asset_id) + parsed(sensor)
```

Lookup matches similarity *within* a parameter bucket, never across buckets. The temporal-cache benchmark reports 30.6x median speedup on hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)), but the real win is eliminating a false-positive class. Plain caches can reach 99% false-positive rates when poorly tuned; well-tuned production systems still report ~0.8% ([Maxim AI](https://www.getmaxim.ai/articles/semantic-caching-for-llms-how-to-cut-token-spend-with-ai-gateways/)). This complements the dual-threshold mechanism in [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md) — the dual threshold tunes precision-recall on the embedding axis; parameter keying partitions the lookup space.

### 2. Disk-Backed Tool-Discovery Cache

Each new session pays for `mcp/listTools` across every connected server plus a planner-side relevance scoring step. The output is deterministic on a given server set — repeated discovery is pure read overhead.

Persist the discovery output on disk, keyed by server-set hash and planner version; invalidate when either changes. Combined with mechanism 3, this reduces median end-to-end latency by ~40% (1.67x speedup) on AssetOpsBench ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)). The host-level alternative is Claude Code's `alwaysLoad`, which pins selected servers into the system-prompt prefix at zero per-session discovery cost ([MCP alwaysLoad](../tool-engineering/mcp-eager-vs-jit-loading.md)). Disk-backed discovery is the right move when the server set is too large for unconditional residence — Anthropic reports tool selection degrades past 30-50 visible tools ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)) — but discovery cost is still measurable.

### 3. Dependency-Aware Parallel Step Execution

LLM-generated plans frequently contain steps whose only inter-dependency is narrative ordering, not data flow. A planner that emits explicit input/output dataclasses per step lets a topological scheduler fan out independent leaves instead of running them serially.

The mechanism mirrors broader work on parallel function calling in agent planners. GAP trains the planner to emit the dependency graph directly, enabling adaptive parallel-and-serial tool execution ([arxiv:2510.25320](https://arxiv.org/pdf/2510.25320)); M1-Parallel reports 2.2x speedup with preserved accuracy via parallel-plan execution with early termination ([arxiv:2507.08944](https://arxiv.org/pdf/2507.08944)). This is distinct from [Agent Composition Patterns](agent-composition-patterns.md) fan-out — composition parallelises across *agents*; this parallelises *steps within one plan*.

## Why It Works

Parameter-keyed caching works because embeddings are dominated by surface vocabulary, not by parameter values that determine answer validity — partitioning the lookup on parameters eliminates a false-positive class plain semantic caching cannot avoid at any threshold ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)). Disk-backed discovery works because `mcp/listTools` plus planner scoring is deterministic on the server set; per-session re-computation is pure waste. Dependency-aware parallelism works because once the planner emits explicit data-flow edges, a topological scheduler executes independent leaves concurrently — GAP and M1-Parallel both report measured speedups from this transformation ([arxiv:2510.25320](https://arxiv.org/pdf/2510.25320), [arxiv:2507.08944](https://arxiv.org/pdf/2507.08944)).

## When This Backfires

- **Workloads without parameter-rich queries.** Code-review, doc-generation, and chat agents rarely vary queries only on temporal or asset parameters. Parameter extraction adds latency; the hit rate never compensates. A short-TTL plain cache is simpler ([PyImageSearch](https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/)).
- **Tool-discovery already amortised at the host.** If the host pins servers via `alwaysLoad` or static config, per-session discovery cost is zero ([MCP alwaysLoad](../tool-engineering/mcp-eager-vs-jit-loading.md)).
- **Tightly sequential plans.** "Read file, edit file, run tests" has hard data dependencies — the dependency analyser finds no parallelism and adds latency.
- **Weak parameter extractor.** A mis-classifying extractor turns a "30x speedup hit" into a confidently wrong answer — worse than a miss. Without extractor evals, the cache becomes a correctness regression vector.
- **Small fleets where engineering cost dominates.** Three new subsystems each carry calibration, observability, and failure modes. Below some QPS threshold, engineering cost outweighs the latency win.
- **Heterogeneous workload mix.** Fixed parameter schemas don't generalise; category-aware approaches ([arxiv:2510.26835](https://arxiv.org/pdf/2510.26835)) may be a better starting point.

## Trade-offs

| Optimisation | Signal it's worth adding | Cheaper alternative |
|---|---|---|
| Parameter-augmented cache key | Measurable false-positive rate on parameter-distinguished queries | Short TTL on plain semantic cache; category-aware thresholds |
| Disk-backed tool discovery | Large MCP server set with measurable per-session discovery latency | `alwaysLoad` (host pins selected servers) |
| Dependency-aware parallel steps | Planner already produces step DAGs with independent leaves | Sequential execution — predictable latency, no overhead |

## Key Takeaways

- Three orthogonal mechanisms — adopt each only when its specific condition is met, not as a bundled architecture
- The 30.6x cache-hit figure is benchmark-specific; the cache-hit *rate* on your workload dominates, not per-hit speedup
- Parameter extraction is a new correctness-critical component — it needs evals, not just latency monitoring
- Step-level parallelism is distinct from agent-level fan-out; it requires the planner to emit data-flow edges per step
- For coding agents and other non-parameter-rich workloads, prefer `alwaysLoad` plus a short-TTL plain semantic cache over the full architecture

## Related

- [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md) — embedding-similarity caching with dual thresholds; this page extends the lookup-axis question with parameter keying
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md) — the host-level alternative to disk-backed tool discovery
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md) — fan-out at the agent level, complementing the step-level parallelism described here
- [Plan Compliance in Agents](plan-compliance-in-agents.md) — dependency-aware parallel execution presupposes plans the agent actually executes
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md) — separating the layer that emits the dependency graph from the layer that schedules it
