---
title: "Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines"
term: "Parameter-Keyed Caching and Dependency-Aware Parallelism"
description: "Augment semantic cache keys with parsed parameters, disk-back the tool-discovery cache, and fan out dependency-independent plan steps — three orthogonal optimisations for parameter-rich, multi-MCP agent pipelines."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - temporal semantic caching
  - MCP workflow optimisation
  - parameter-aware cache key
  - dependency-aware step parallelism
last_reviewed: 2026-06-02
maturity: emerging
---

# Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines

> Three orthogonal caching and parallelism optimisations for parameter-rich plan-execute pipelines: partition the cache key on parsed parameters, disk-back tool discovery, and parallelise independent steps.

## When this pattern earns its complexity

These optimizations target a narrow workload profile. Apply each only when its condition holds. Otherwise the calibration overhead exceeds the latency win.

| Condition | Why it matters |
|---|---|
| Queries vary on temporal, asset, or sensor parameters | Plain semantic caching collapses parameter-distinguished queries into false hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| Plans coordinate across multiple MCP servers per query | Tool-discovery and selection dominate end-to-end latency in plan-execute pipelines ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| Generated plans contain genuinely independent steps | Dependency-aware parallelism degenerates to sequential-with-overhead when every step depends on the prior one |

The original evaluation is on AssetOpsBench — industrial asset operations with sensor data, work orders, and forecasting tools. Coding agents and chat assistants rarely meet the first condition.

## The three mechanisms

### 1. Parameter-augmented semantic cache key

Plain semantic caches hash the query embedding and serve any similar prior response. They fail on parameter-distinguished queries: "asset 7 failures yesterday" and "asset 7 failures last month" embed nearly identically — vocabulary dominates the vector while the temporal qualifier changes the answer.

Extract parameters before lookup and partition the cache key on them:

```
cache_key = embedding(query) + parsed(temporal) + parsed(asset_id) + parsed(sensor)
```

Lookup then matches similarity within a parameter bucket, never across buckets. The benchmark reports 30.6x median speedup on hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)), but the real win is eliminating a false-positive class plain caches cannot avoid at any threshold. This complements the dual-threshold mechanism in [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md): the dual threshold tunes precision-recall on the embedding axis; parameter keying partitions the lookup space.

### 2. Disk-backed tool-discovery cache

Each new session pays for `mcp/listTools` across every connected server plus planner-side relevance scoring. That output is deterministic on a given server set, so repeated discovery is pure overhead.

Persist it on disk, keyed by server-set hash and planner version; invalidate when either changes. Combined with mechanism 3, this cuts median end-to-end latency ~40% (1.67x) on AssetOpsBench ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)). The host-level alternative is Claude Code's `alwaysLoad`, which pins servers into the system-prompt prefix at zero per-session cost ([MCP alwaysLoad](../tool-engineering/mcp-eager-vs-jit-loading.md)). Disk-backing wins when the server set is too large for unconditional residence — tool selection degrades past 30-50 visible tools ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

### 3. Dependency-aware parallel step execution

LLM-generated plans often contain steps whose only inter-dependency is narrative ordering, not data flow. A planner that emits explicit input/output dataclasses per step lets a topological scheduler fan out independent leaves instead of running them serially. GAP trains the planner to emit the dependency graph directly for adaptive parallel-and-serial execution ([arxiv:2510.25320](https://arxiv.org/pdf/2510.25320)); M1-Parallel reports 2.2x speedup with preserved accuracy via early-termination parallel plans ([arxiv:2507.08944](https://arxiv.org/pdf/2507.08944)). This is distinct from [Agent Composition Patterns](agent-composition-patterns.md) fan-out: composition parallelizes across agents; this parallelizes steps within one plan.

## Why it works

Each mechanism removes provably redundant work. Parameter-keyed caching works because embeddings are dominated by surface vocabulary, not by the parameter values that determine answer validity, so partitioning the lookup eliminates a false-positive class no threshold can fix ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)). Disk-backed discovery works because `mcp/listTools` plus planner scoring is deterministic on the server set, making per-session re-computation waste. Dependency-aware parallelism works because explicit data-flow edges let a topological scheduler run independent leaves concurrently — GAP and M1-Parallel both report measured speedups from this transformation ([arxiv:2510.25320](https://arxiv.org/pdf/2510.25320), [arxiv:2507.08944](https://arxiv.org/pdf/2507.08944)).

## When this backfires

- Non-parameter-rich workloads. Code-review, doc-generation, and chat agents rarely vary queries on temporal or asset parameters. Extraction adds latency the hit rate never repays. A short-TTL plain cache is simpler ([PyImageSearch](https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/)).
- Discovery already amortized at the host. If the host pins servers via `alwaysLoad` or static config, per-session discovery cost is already zero ([MCP alwaysLoad](../tool-engineering/mcp-eager-vs-jit-loading.md)).
- Tightly sequential plans. "Read file, edit file, run tests" has hard data dependencies — the analyzer finds no parallelism and only adds latency.
- Weak parameter extractor. A mis-classifying extractor turns a 30x hit into a confidently wrong answer — worse than a miss, and a correctness regression vector without extractor evals.
- Small fleets. Three subsystems each carry calibration, observability, and failure modes. Below some QPS threshold the engineering cost outweighs the win.
- Heterogeneous workload mix. Fixed parameter schemas do not generalize. Category-aware approaches ([arxiv:2510.26835](https://arxiv.org/pdf/2510.26835)) may fit better.

## Trade-offs

| Optimization | Signal it's worth adding | Cheaper alternative |
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
