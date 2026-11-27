---
title: "Parameter-Keyed Caching and Dependency-Aware Parallelism for Plan-Execute Pipelines"
term: "Parameter-Keyed Caching and Dependency-Aware Parallelism"
description: "Three plan-execute optimizations: a parameter cache key that the source paper proposes but does not test, for parameter-varying queries, a disk-backed tool-discovery cache for pipelines that rediscover MCP servers on every query, and parallel execution of independent steps."
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

> Three separate plan-execute optimizations: a proposed parameter-keyed cache for parameter-varying queries, disk-backed tool discovery for pipelines that rediscover MCP servers on every query, and parallel execution of independent steps.

## When this pattern earns its complexity

Parameter-keyed caching, disk-backed tool discovery, and dependency-aware parallelism target a narrow workload profile. Apply each only when its condition holds. These conditions, and the backfire cases and alternatives below, are this page's judgment. The paper does not test them as adoption rules.

| Condition | Why it matters |
|---|---|
| Queries vary on temporal, asset, or sensor parameters | Plain semantic caching collapses parameter-distinguished queries into false hits ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630)) |
| The pipeline rediscovers tools from several MCP servers on every query | The AssetOpsBench baseline discovers tools from four servers on every query. Caching cut that phase from 2.096 s to 0.007 s, but execution, not discovery, dominates end-to-end latency ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1), §3.3 and Table 1, an 18-query parallelism stress test: execution is 60.9% of baseline latency vs. ~22% for discovery plus planning) |
| Generated plans contain genuinely independent steps | Dependency-aware parallelism degenerates to sequential-with-overhead when every step depends on the prior one |

The paper's measurements are on AssetOpsBench, which covers industrial asset operations with sensor data, work orders, and forecasting tools. The measurements cover a temporal semantic cache, a tool-discovery cache, and parallel steps with a persistent server pool. They do not cover the parameter key in mechanism 1. Coding agents and chat assistants rarely meet the first condition.

## The three mechanisms

### 1. Parameter-augmented semantic cache key

Plain semantic caches match a new query to stored ones by embedding similarity. They can fail on parameter-distinguished queries. "Asset 7 failures yesterday" and "asset 7 failures last month" can embed close together, because shared vocabulary dominates the vector while the temporal qualifier changes the answer.

The parameter key is a proposal, not a measured result. The paper lists it as future work and does not build or test it ([arxiv:2605.20630, §6](https://arxiv.org/abs/2605.20630v1)). It proposes extracting "structured parameters (entity, sensor, time window, action verb)" and caching under a key of the form "(canonical_intent, param_combo)". A parameter-exact match returns the cached answer, and "semantic matching only fires when parameter sets overlap".

The sketch below is this page's own, stricter variant:

```
cache_key = embedding(query) + parsed(temporal) + parsed(asset_id) + parsed(sensor)
```

In this variant, lookup matches similarity within a parameter bucket, never across buckets. Resolve relative times to concrete windows before keying. The paper warns that caching phrases like "yesterday" "under their literal text would produce stale hits" ([§3.2](https://arxiv.org/abs/2605.20630v1)). The proposed key would complement the dual-threshold mechanism in [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md): the dual threshold tunes precision-recall on the embedding axis, and parameter keying would partition the lookup space.

What the paper did measure is a temporal semantic cache: a temporal classifier, embedding retrieval, and a reranker-based judge. Run alone, without the MCP optimizations, on a stratified sample of 50 queries, it had a 36.0% hit rate, a 30.6x median speedup on hits, 2.23 s median added latency on misses, and precision 0.667 ([Appendix B](https://arxiv.org/abs/2605.20630v1)). The paper also reports cross-parameter false positives from its cache, one with a judge score of 0.97. The authors conclude that "pure semantic similarity is not a sound proxy for answer validity in parameter-rich industrial queries, and no choice of similarity threshold can fully resolve this" ([§5](https://arxiv.org/abs/2605.20630v1)). They expect the parameter key to "eliminate the false-positive class" ([§6](https://arxiv.org/abs/2605.20630v1)).

### 2. Disk-backed tool-discovery cache

The AssetOpsBench baseline runs MCP tool discovery on every query: it spawns each of the four servers and calls `list_tools()`, which takes 2 to 3 seconds per query in the authors' setup. The paper treats tool signatures as "semi-static metadata" and persists the catalog to a local JSON file ([§3.3](https://arxiv.org/abs/2605.20630v1)).

Key that file by an MD5 hash of server file paths and the mtimes of server source and dependency files; invalidate automatically on a code or dependency change, plus a 24-hour TTL as a backstop ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1), Appendix A). The paper measured this cache together with parallel step execution and a persistent server pool. The three cut median end-to-end latency by about 40% (1.67x) on 18 IoT queries ([§4.2](https://arxiv.org/abs/2605.20630v1)). The queries come from a subset retained for having at least two parallelizable branches, "a parallelism stress test (not a representative slice of the full corpus)" ([§4.1](https://arxiv.org/abs/2605.20630v1)). Claude Code has a host-level equivalent for remote HTTP and SSE servers: its discovery cache loads a tool list saved in a previous session instead of connecting at startup. The cache is off by default unless a rollout has enabled it, and `MCP_DISCOVERY_CACHE=1` turns it on ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#server-status-detail)). `alwaysLoad` does a different job. It exempts a server's tools from tool-search deferral. It also makes startup wait up to 5 seconds for that server's tools, unless the server is a remote one with a valid cached entry, which supplies its tools without connecting ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#exempt-a-server-from-deferral)).

### 3. Dependency-aware parallel step execution

LLM-generated plans often contain steps whose only inter-dependency is narrative ordering, not data flow. A planner that emits explicit input/output dataclasses per step lets a topological scheduler fan out independent leaves instead of running them serially. GAP trains the planner to emit the dependency graph directly for adaptive parallel-and-serial execution ([arxiv:2510.25320](https://arxiv.org/abs/2510.25320v1)). This is distinct from [Agent Composition Patterns](../multi-agent/agent-composition-patterns.md) fan-out: composition parallelizes across agents; this parallelizes steps within one plan.

The distinction is one the literature draws too, and against this pattern. M1-Parallel takes the other side: it runs redundant teams concurrently and stops at the first to finish, reporting "up to 2.2x speedup while preserving accuracy", and rules out the approach on this page outright — "parallelization within a single plan is impractical for multi-agent systems that dynamically devise plans and take actions at execution time" ([arxiv:2507.08944v1](https://arxiv.org/abs/2507.08944v1)). Its objection is to *dynamically* devised plans. This pattern applies where the planner emits the dependency graph up front, which is the condition M1-Parallel's argument excludes.

## Why it works

Parameter keying is expected to work because embeddings are dominated by shared wording, not by the parameter values that determine answer validity. The paper predicts that partitioning on parameters would eliminate the resulting false positives, but does not test the prediction ([arxiv:2605.20630](https://arxiv.org/abs/2605.20630v1), §5 and §6). Disk-backed discovery works because tool signatures can be treated as "semi-static metadata", so discovering them again on every query repeats work ([§3.3](https://arxiv.org/abs/2605.20630v1)). Dependency-aware parallelism works because explicit data-flow edges let a topological scheduler run independent leaves concurrently. GAP is the measured evidence for that transformation: it "explicitly models inter-task dependencies through graph-based planning to enable adaptive parallel and serial tool execution" ([arxiv:2510.25320v1](https://arxiv.org/abs/2510.25320v1)). One paper, not two — M1-Parallel's speedup comes from concurrent redundant teams, not from this.

## When this backfires

- Non-parameter-rich workloads. Code-review, doc-generation, and chat agents rarely vary queries on temporal or asset parameters. Extraction adds latency the hit rate may never repay. A short-TTL plain cache is simpler ([PyImageSearch](https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/)).
- Discovery already amortized at the host. If the host already caches or reuses tool discovery, a disk cache adds little.
- Tightly sequential plans. "Read file, edit file, run tests" has hard data dependencies — the analyzer finds no parallelism and only adds latency.
- Weak parameter extractor. A mis-classifying extractor can turn a cache hit into a confidently wrong answer — worse than a miss, and a correctness regression vector without extractor evals.
- Small fleets. Three subsystems each carry calibration, observability, and failure modes. Below some QPS threshold the engineering cost outweighs the win.
- Heterogeneous workload mix. Fixed parameter schemas do not generalize. Category-aware approaches ([arxiv:2510.26835](https://arxiv.org/abs/2510.26835)) may fit better.

## Trade-offs

| Optimization | Signal it's worth adding | Cheaper alternative |
|---|---|---|
| Parameter-augmented cache key (proposed, not tested in the paper) | Measurable false-positive rate on parameter-distinguished queries | Short TTL on plain semantic cache; category-aware thresholds |
| Disk-backed tool discovery | Large MCP server set with measurable discovery latency | The host's own discovery cache, such as Claude Code's `MCP_DISCOVERY_CACHE=1` for remote servers |
| Dependency-aware parallel steps | Planner already produces step DAGs with independent leaves | Sequential execution — predictable latency, no overhead |

## Example

Two queries hit the same asset-operations agent: "asset 7 failures yesterday" and "asset 7 failures last month". Their embeddings can sit close together, since only the time phrase differs, so a plain semantic cache can treat the second as a hit on the first and return yesterday's failure count for a query about last month.

In this page's stricter sketch, which the paper does not build or test, parameter extraction runs before the lookup and splits the two queries into separate buckets:

```
query_1 = "asset 7 failures yesterday"
parsed_1 = { asset_id: "7", temporal: resolve("yesterday", now) }
cache_key_1 = embedding(query_1) + parsed_1

query_2 = "asset 7 failures last month"
parsed_2 = { asset_id: "7", temporal: resolve("last month", now) }
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

- Three separate mechanisms — adopt each only when its specific condition is met, not as a bundled architecture
- The paper proposes the parameter key as future work and never measures it. The 30.6x median speedup on hits belongs to its temporal semantic cache, run alone at precision 0.667
- On your workload, the cache-hit *rate* matters more than per-hit speedup
- Parameter extraction is a new correctness-critical component — it needs evals, not just latency monitoring
- Step-level parallelism is distinct from agent-level fan-out; it requires the planner to emit data-flow edges per step
- For coding agents and other non-parameter-rich workloads, prefer a short-TTL plain semantic cache and the host's own discovery cache over the full architecture

## Related

- [Semantic Caching for Multi-Agent Code Systems](../multi-agent/semantic-caching-multi-agent.md) — embedding-similarity caching with dual thresholds; this page extends the lookup-axis question with a proposed parameter key
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../../tool-engineering/mcp-eager-vs-jit-loading.md) — decides whether a server's tools load upfront or wait behind tool search; it does not cache discovery
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](../multi-agent/agent-composition-patterns.md) — fan-out at the agent level, complementing the step-level parallelism described here
- [Plan Compliance in Agents](plan-compliance-in-agents.md) — dependency-aware parallel execution presupposes plans the agent actually executes
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md) — separating the layer that emits the dependency graph from the layer that schedules it
