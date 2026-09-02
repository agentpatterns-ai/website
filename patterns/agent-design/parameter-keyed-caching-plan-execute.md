---
title: "Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines"
term: "Parameter-Keyed Caching and Dependency-Aware Parallelism"
description: "Augment semantic cache keys with parsed parameters, disk-back the tool-discovery cache, and fan out dependency-independent plan steps — three orthogonal optimizations for parameter-rich, multi-MCP agent pipelines."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
  - long-form
aliases:
  - temporal semantic caching
  - MCP workflow optimisation
  - parameter-aware cache key
  - dependency-aware step parallelism
last_reviewed: 2026-08-30
maturity: emerging
---

# Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines

> Three orthogonal caching and parallelism optimizations for parameter-rich plan-execute pipelines: partition the cache key on parsed parameters, disk-back tool discovery, and parallelize independent steps.

## When this pattern earns its complexity

Parameter-keyed caching, disk-backed tool discovery, and dependency-aware parallelism target a narrow workload profile. Apply each only when its condition holds. Otherwise the calibration overhead exceeds the latency win.

| Condition | Why it matters |
|---|---|
| Queries vary on temporal, asset, or sensor parameters | Plain semantic caching collapses parameter-distinguished queries into false hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| Plans coordinate across multiple MCP servers per query | Discovery cost scales with server count and repeats every session regardless of the query; caching removes this fixed overhead, even though execution — not discovery — dominates end-to-end latency ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1), Table 1: execution is 60.8% of baseline latency vs. ~22% for discovery plus planning) |
| Generated plans contain genuinely independent steps | Dependency-aware parallelism degenerates to sequential-with-overhead when every step depends on the prior one |

The original evaluation is on AssetOpsBench — industrial asset operations with sensor data, work orders, and forecasting tools. Coding agents and chat assistants rarely meet the first condition.

## The three mechanisms

### 1. Parameter-augmented semantic cache key

Plain semantic caches hash the query embedding and serve any similar prior response. They fail on parameter-distinguished queries: "asset 7 failures yesterday" and "asset 7 failures last month" embed nearly identically — vocabulary dominates the vector while the temporal qualifier changes the answer.

Extract parameters before lookup and partition the cache key on them:

```
cache_key = embedding(query) + parsed(temporal) + parsed(asset_id) + parsed(sensor)
```

Lookup then matches similarity within a parameter bucket, never across buckets. The benchmark reports 30.6x median speedup on hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1)), but the real win is eliminating a false-positive class plain caches cannot avoid at any threshold. This complements the dual-threshold mechanism in [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md): the dual threshold tunes precision-recall on the embedding axis; parameter keying partitions the lookup space.

### 2. Disk-backed tool-discovery cache

Each new session pays for `mcp/listTools` across every connected server. That output is deterministic on a given server set, so repeated discovery is pure overhead.

Persist it on disk, keyed by an MD5 hash of server file paths and the mtimes of server source and dependency files; invalidate automatically on a code or dependency change, plus a 24-hour TTL as a backstop ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1), Appendix A). Combined with mechanism 3, this cuts median end-to-end latency ~40% (1.67x) on AssetOpsBench ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1)). The host-level alternative is Claude Code's `alwaysLoad`, which pins servers into the system-prompt prefix at zero per-session cost ([MCP alwaysLoad](../../tool-engineering/mcp-eager-vs-jit-loading.md)). Disk-backing wins when the server set is too large for unconditional residence — tool selection degrades past 30-50 visible tools ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

### 3. Dependency-aware parallel step execution

LLM-generated plans often contain steps whose only inter-dependency is narrative ordering, not data flow. A planner that emits explicit input/output dataclasses per step lets a topological scheduler fan out independent leaves instead of running them serially. GAP trains the planner to emit the dependency graph directly for adaptive parallel-and-serial execution ([arxiv:2510.25320](https://arxiv.org/abs/2510.25320v1)). This is distinct from [Agent Composition Patterns](agent-composition-patterns.md) fan-out: composition parallelizes across agents; this parallelizes steps within one plan.

The distinction is one the literature draws too, and against this pattern. M1-Parallel takes the other side: it runs redundant teams concurrently and stops at the first to finish, reporting "up to 2.2x speedup while preserving accuracy", and rules out the approach on this page outright — "parallelization within a single plan is impractical for multi-agent systems that dynamically devise plans and take actions at execution time" ([arxiv:2507.08944v1](https://arxiv.org/abs/2507.08944v1)). Its objection is to *dynamically* devised plans. This pattern applies where the planner emits the dependency graph up front, which is the condition M1-Parallel's argument excludes.

## Why it works

Each mechanism removes provably redundant work. Parameter-keyed caching works because embeddings are dominated by surface vocabulary, not by the parameter values that determine answer validity, so partitioning the lookup eliminates a false-positive class no threshold can fix ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)). Disk-backed discovery works because `mcp/listTools` output is deterministic on a given server set, making per-session re-computation waste. Dependency-aware parallelism works because explicit data-flow edges let a topological scheduler run independent leaves concurrently. GAP is the measured evidence for that transformation: it "explicitly models inter-task dependencies through graph-based planning to enable adaptive parallel and serial tool execution" ([arxiv:2510.25320v1](https://arxiv.org/abs/2510.25320v1)). One paper, not two — M1-Parallel's speedup comes from concurrent redundant teams, not from this.

## When this backfires

- Non-parameter-rich workloads. Code-review, doc-generation, and chat agents rarely vary queries on temporal or asset parameters. Extraction adds latency the hit rate never repays. A short-TTL plain cache is simpler ([PyImageSearch](https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/)).
- Discovery already amortized at the host. If the host pins servers via `alwaysLoad` or static config, per-session discovery cost is already zero ([MCP alwaysLoad](../../tool-engineering/mcp-eager-vs-jit-loading.md)).
- Tightly sequential plans. "Read file, edit file, run tests" has hard data dependencies — the analyzer finds no parallelism and only adds latency.
- Weak parameter extractor. A mis-classifying extractor turns a 30x hit into a confidently wrong answer — worse than a miss, and a correctness regression vector without extractor evals.
- Small fleets. Three subsystems each carry calibration, observability, and failure modes. Below some QPS threshold the engineering cost outweighs the win.
- Heterogeneous workload mix. Fixed parameter schemas do not generalize. Category-aware approaches ([arxiv:2510.26835](https://arxiv.org/abs/2510.26835)) may fit better.

## Trade-offs

| Optimization | Signal it's worth adding | Cheaper alternative |
|---|---|---|
| Parameter-augmented cache key | Measurable false-positive rate on parameter-distinguished queries | Short TTL on plain semantic cache; category-aware thresholds |
| Disk-backed tool discovery | Large MCP server set with measurable per-session discovery latency | `alwaysLoad` (host pins selected servers) |
| Dependency-aware parallel steps | Planner already produces step DAGs with independent leaves | Sequential execution — predictable latency, no overhead |

## Example

Two queries hit the same asset-operations agent: "asset 7 failures yesterday" and "asset 7 failures last month". Their embeddings sit close together — only one word differs — so a plain semantic cache treats the second as a hit on the first and returns yesterday's failure count for a query about last month.

Parameter extraction runs before the lookup and splits the two queries into separate buckets:

```
query_1 = "asset 7 failures yesterday"
parsed_1 = { asset_id: "7", temporal: "yesterday" }
cache_key_1 = embedding(query_1) + parsed_1

query_2 = "asset 7 failures last month"
parsed_2 = { asset_id: "7", temporal: "last month" }
cache_key_2 = embedding(query_2) + parsed_2
```

`parsed_1.temporal` and `parsed_2.temporal` differ, so `cache_key_1 != cache_key_2`. The second query misses the cache and re-runs the plan instead of returning the first query's answer for the wrong month. A weak extractor undoes this guarantee: if it mis-parses "last month" or drops the asset ID, the query lands in the wrong bucket and returns another period's cached answer with full confidence — a wrong hit, not a miss.

For dependency-aware parallelism, take a four-step plan: fetch sensor readings, fetch work-order history, compute a failure-rate forecast from the readings, and generate a summary from the forecast and the work orders. The two fetch steps read from different sources and do not depend on each other; the forecast step depends only on the readings; the summary step depends on both the forecast and the work orders:

```
fetch_readings    ---> compute_forecast ---\
fetch_work_orders ------------------------> generate_summary
```

A topological scheduler reads this graph and runs `fetch_readings` and `fetch_work_orders` concurrently, instead of running all four steps in planner-emitted order.

## Key Takeaways

- Three orthogonal mechanisms — adopt each only when its specific condition is met, not as a bundled architecture
- The 30.6x cache-hit figure is benchmark-specific; the cache-hit *rate* on your workload dominates, not per-hit speedup
- Parameter extraction is a new correctness-critical component — it needs evals, not just latency monitoring
- Step-level parallelism is distinct from agent-level fan-out; it requires the planner to emit data-flow edges per step
- For coding agents and other non-parameter-rich workloads, prefer `alwaysLoad` plus a short-TTL plain semantic cache over the full architecture

## Related

- [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md) — embedding-similarity caching with dual thresholds; this page extends the lookup-axis question with parameter keying
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../../tool-engineering/mcp-eager-vs-jit-loading.md) — the host-level alternative to disk-backed tool discovery
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md) — fan-out at the agent level, complementing the step-level parallelism described here
- [Plan Compliance in Agents](plan-compliance-in-agents.md) — dependency-aware parallel execution presupposes plans the agent actually executes
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md) — separating the layer that emits the dependency graph from the layer that schedules it
