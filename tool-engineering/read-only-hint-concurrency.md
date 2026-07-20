---
title: "Hint-Driven Concurrency for Read-Only MCP Tools"
term: "Hint-Driven Concurrency"
description: "MCP readOnlyHint became a concurrency dispatcher input in Codex CLI 0.134.0 — a wall-clock win that only holds when annotations are audited."
tags:
  - tool-engineering
  - cost-performance
  - tool-agnostic
  - mcp
aliases:
  - readOnlyHint parallel execution
  - parallel MCP tool dispatch
last_reviewed: 2026-06-03
maturity: established
---

# Hint-Driven Concurrency for Read-Only MCP Tools

> Hint-driven concurrency runs read-only MCP tools in parallel by reading the `readOnlyHint` annotation as a dispatch contract, not just a safety prompt.

Related lesson: [Tool-Call Cost and Latency Budgeting](https://learn.agentpatterns.ai/tool-engineering/cost-and-latency-budgeting/) — this concept features in a hands-on lesson with quizzes.

Hint-driven concurrency is a harness-side dispatch pattern that runs multiple MCP tool calls in one agent turn in parallel when each advertises `readOnlyHint: true`, while keeping annotated-mutating or unannotated tools strictly sequential. Codex CLI 0.134.0 shipped this in the open: read-only tools automatically qualify for parallel execution, and the server-level `supports_parallel_tool_calls` flag remains an additive override for tools that mutate ([Codex CLI changelog](https://developers.openai.com/codex/changelog), [openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). The annotation stopped being a passive safety badge the moment a major harness wired it into the dispatch path.

## The contract shift

The MCP spec defines `readOnlyHint` alongside `destructiveHint`, `idempotentHint`, and `openWorldHint`. Annotations are advisory — the spec is direct that "clients MUST consider tool annotations to be untrusted unless they come from trusted servers" ([MCP specification — tool annotations](https://spec.modelcontextprotocol.io/specification/server/tools/)). Until a harness uses the hint to make a scheduling decision, the trust caveat is cosmetic: the confirmation prompt may differ, but the tool's behavior is unchanged.

Once the harness reads `readOnlyHint` and lifts the sequential gate on that basis, the annotation governs execution semantics, not just the user prompt. A misannotated tool — one that declares `readOnlyHint: true` but mutates — produces concurrent racing writes the moment the agent issues two calls in the same turn. This is the most common misannotation class; hint-driven concurrency is what makes that misannotation load-bearing.

## Why it works

Read-only tools, by the annotation contract, do not mutate state shared across calls, so two concurrent invocations cannot interfere through tool effects — the only resource they share is the transport and the server's process budget. Wall-clock cost for N read calls drops from `sum(latency_i)` toward `max(latency_i)` plus dispatch overhead — the same overlap that drives 1.24x–1.44x speedups in [future-based asynchronous function calling](future-based-async-function-calling.md) and 90% research-time reductions in Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

The pattern is also cheap to wire. Explicit-dependency declaration — LLMCompiler's planned DAG ([arXiv:2312.04511](https://arxiv.org/abs/2312.04511)) or AsyncFC's symbolic futures ([arXiv:2605.15077](https://arxiv.org/abs/2605.15077)) — preserves ordering but adds a planner pass or a futures protocol. Hint-driven concurrency instead uses a static annotation lookup: the harness sees `readOnlyHint: true` in `tools/list` metadata and treats every such call as independently dispatchable. No planner, no DAG, no schema rewrite.

The spec-defined defaults make it safely opt-in. `readOnlyHint` defaults to `false`, so a server that omits annotations stays sequential. An author opts into concurrency by setting one boolean — and accepts the responsibility that comes with it.

## Preconditions

Read-only concurrency only holds when these are true.

- Annotation audit has run. The MCP spec treats annotations as untrusted unless from a trusted server ([MCP specification](https://spec.modelcontextprotocol.io/specification/server/tools/)). Audit tool idempotency against every connected server before flipping the harness flag — without it, one misannotated tool turns the win into a race.
- `idempotentHint` is set alongside `readOnlyHint`. A read-only call that fails transiently must be safe to retry. Pure reads are idempotent by definition; the annotation makes that explicit and gives the harness a safe recovery path.
- Per-server concurrency caps exist. The Codex PR mentions no fairness mechanism — every read-only tool against one server can be dispatched at once ([openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). Rate-limited backends need a harness-side cap or strict server-side throttling.
- The model handles interleaved tool results. Concurrent dispatch returns results out-of-order. Models that degrade on interleaved-ledger reasoning underperform the sequential baseline regardless of wall-clock gains ([Asynchronous Agent I/O and Speculative Tools](../patterns/agent-design/asynchronous-agent-io-and-speculative-tools.md)).

## When this backfires

The pattern inverts in five concrete cases.

- Misannotated mutating tools. A server declares `readOnlyHint: true` on a tool that writes — the common misannotation. Two concurrent calls race; the harness cannot detect it, and the agent reasons over an inconsistent result. The fix is upstream server-side correction, not harness recovery.
- Rate-limited or quota-bounded backends. A read tool against a per-second-capped external API (search, embeddings, LLM) hits 429s under concurrent dispatch that sequential would have avoided. Wall-clock gain is swapped for failure-recovery turns and API budget burn ([Arya AI: agentic system trade-offs](https://arya.ai/blog/navigating-trade-offs-in-agentic-systems)).
- Weakly consistent read replicas. List-then-get patterns across read replicas may return divergent results to concurrent reads; the agent reasons over a self-inconsistent view that sequential calls would have avoided.
- Single-server fan-out without per-server caps. Ten concurrent reads against a server sized for sequential traffic blow the process, thread, or connection budget. Without server-side throttling as a backstop, the harness gain becomes a server-side outage.
- In-page agents and embedded surfaces. [WebMCP](../standards/webmcp.md) explicitly chose sequential-only tool calls within a page ([WebMCP spec §5.1](https://webmachinelearning.github.io/webmcp/)); embedded surfaces accept the latency cost rather than reason about read-only races in the page event loop. This is a server-side-MCP optimization, not a universal pattern.

The Codex 0.134.0 default enables hint-driven concurrency for every connected MCP server, regardless of whether its author audited the annotations ([openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). For operators running many third-party servers, the safe posture is to leave per-server concurrency disabled until the upstream audit lands.

## Example

A coding agent loads three MCP servers in a session: a documentation search server, an internal knowledge-base server, and a customer-data API server. The agent emits three tool calls in one turn — one against each server, all read-only.

Before — sequential dispatch:

```
t=0ms    search_docs("readOnlyHint")        dispatched
t=850ms  search_docs returns
t=850ms  kb_lookup("MCP concurrency")       dispatched
t=1900ms kb_lookup returns
t=1900ms get_customer(id=42)                dispatched
t=2400ms get_customer returns
                                            total: 2400ms
```

After — hint-driven concurrency (all three tools annotated `readOnlyHint: true`):

```
t=0ms    search_docs("readOnlyHint")        dispatched
t=0ms    kb_lookup("MCP concurrency")       dispatched
t=0ms    get_customer(id=42)                dispatched
t=850ms  search_docs returns
t=1050ms kb_lookup returns
t=500ms  get_customer returns
                                            total: 1050ms (max of three)
```

The wall-clock cost drops from `sum` to `max`. If `get_customer` is annotated `readOnlyHint: true` but the implementation logs the access and updates a `last_seen` timestamp, the third server is mis-classified — concurrent calls race on the timestamp update. The harness has no way to detect this without an upstream audit, which is why tool-idempotency is a precondition, not a follow-up.

## Key Takeaways

- The MCP `readOnlyHint` is no longer just a safety hint — Codex CLI 0.134.0 wired it into the dispatch path, and that makes the annotation load-bearing for execution semantics.
- The hint defaults to `false`, so servers stay sequential until the author opts in — conservative by design.
- The MCP spec treats annotations as untrusted unless from a trusted server; hint-driven concurrency requires a per-server trust gate and an upstream tool-idempotency audit ([MCP specification](https://spec.modelcontextprotocol.io/specification/server/tools/)).
- The trade-off vs DAG-style explicit-dependency declaration is wiring cost vs ordering information: hint-driven concurrency is essentially free to wire but loses the ordering information the model already knew.
- Per-server concurrency caps and rate-limit-aware dispatch are the harness operator's responsibility — the Codex PR ships neither.

## Related

- [MCP Server Design](mcp-server-design.md)
- [Future-Based Asynchronous Function Calling](future-based-async-function-calling.md)
- [Asynchronous Agent I/O and Speculative Tools](../patterns/agent-design/asynchronous-agent-io-and-speculative-tools.md)
- [WebMCP: Browser-Hosted Tool Contracts](../standards/webmcp.md)
