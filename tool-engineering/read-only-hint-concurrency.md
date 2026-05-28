---
title: "Hint-Driven Concurrency for Read-Only MCP Tools"
description: "MCP readOnlyHint became a concurrency dispatcher input in Codex CLI 0.134.0 — a wall-clock win that only holds when annotations are audited."
tags:
  - tool-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - readOnlyHint parallel execution
  - parallel MCP tool dispatch
last_reviewed: 2026-05-27
---

# Hint-Driven Concurrency for Read-Only MCP Tools

> Hint-driven concurrency runs read-only MCP tools in parallel by reading the `readOnlyHint` annotation as a dispatch contract, not just a safety prompt.

Hint-driven concurrency is a harness-side dispatch pattern that runs multiple MCP tool calls in the same agent turn in parallel when each tool advertises `readOnlyHint: true`, while leaving annotated-mutating or unannotated tools strictly sequential. Codex CLI 0.134.0 shipped this in the open: read-only tools "automatically qualify for parallel execution," and the server-level `supports_parallel_tool_calls` flag remains an additive override for tools that mutate ([Codex CLI changelog](https://developers.openai.com/codex/changelog), [openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). The annotation stopped being a passive safety badge the moment a major harness wired it into the dispatch path.

## The Contract Shift

The MCP spec defines `readOnlyHint` alongside `destructiveHint`, `idempotentHint`, and `openWorldHint`. Annotations are *advisory* — the spec is direct that "clients MUST consider tool annotations to be untrusted unless they come from trusted servers" ([MCP specification — tool annotations](https://spec.modelcontextprotocol.io/specification/server/tools/)). Until a harness uses the hint to make a scheduling decision, the trust caveat is cosmetic: the agent might display a different confirmation prompt, but the tool's behavior is unchanged.

Once the harness reads `readOnlyHint` and lifts the sequential gate on that basis, the contract changes. The annotation now governs *execution semantics*, not just UX. A misannotated tool — one that declares `readOnlyHint: true` but mutates — produces concurrent racing writes the moment the agent issues two calls in the same turn. The audit-tool-idempotency runbook already enumerates this as the most common misannotation class ([Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md)); hint-driven concurrency is what makes that misannotation load-bearing.

## Why It Works

Two reasons the mechanism pays off on read-heavy turns.

Read-only tools, by the annotation contract, do not mutate state shared across calls. Two concurrent invocations cannot interfere through tool effects; the only resource they share is the underlying transport and the server's process budget. Wall-clock cost for N read calls drops from `sum(latency_i)` toward `max(latency_i)` plus dispatch overhead — the same overlap mechanism that drives 1.24x–1.44x speedups in [future-based asynchronous function calling](future-based-async-function-calling.md) and 90% research-time reductions in Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

The pattern is also cheap to wire compared with alternatives. Explicit-dependency declaration — LLMCompiler's planned DAG ([arXiv:2312.04511](https://arxiv.org/abs/2312.04511)) or AsyncFC's symbolic futures ([arXiv:2605.15077](https://arxiv.org/abs/2605.15077)) — preserves ordering information but adds a planner pass or a futures protocol. Hint-driven concurrency uses a static annotation lookup. The harness sees `readOnlyHint: true` in `tools/list` metadata and treats every such call as independently dispatchable. No planner, no DAG, no rewrite of the model's tool-calling schema.

The spec-defined defaults make it safely opt-in. `readOnlyHint` defaults to `false`; an MCP server that omits annotations stays on the sequential path ([Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md)). A server author opts into concurrency by setting one boolean, and they accept the responsibility that comes with it.

## Preconditions

Read-only concurrency only holds when these are true.

- **Annotation audit has run.** The MCP spec treats annotations as untrusted unless from a trusted server ([MCP specification](https://spec.modelcontextprotocol.io/specification/server/tools/)). Run the [tool-idempotency audit](../agent-readiness/audit-tool-idempotency.md) against every connected server before flipping the harness flag. Without the audit, a single misannotated tool turns the concurrency win into a race.
- **`idempotentHint` is set alongside `readOnlyHint`.** A read-only call that fails transiently must be safe to retry. Pure reads are idempotent by definition; the annotation makes that explicit and gives the harness a safe recovery path ([Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md)).
- **Per-server concurrency caps exist.** The Codex PR summary mentions no fairness mechanism — every read-only tool against the same server can be dispatched simultaneously ([openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). Rate-limited backends need a per-server cap on the harness side or strict server-side throttling.
- **The model handles interleaved tool results.** Concurrent dispatch returns results out-of-order. Models that degrade on interleaved-ledger reasoning underperform the sequential baseline regardless of wall-clock gains ([Asynchronous Agent I/O and Speculative Tools](../agent-design/asynchronous-agent-io-and-speculative-tools.md)).

## When This Backfires

The pattern inverts in five concrete cases.

- **Misannotated mutating tools.** A server declares `readOnlyHint: true` on a tool that writes (the common misannotation in [Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md) Step 3). Two concurrent calls race; the harness has no signal to detect it, and the agent reasons over an inconsistent result. The fix is upstream — server-side correction — not harness-side recovery.
- **Rate-limited or quota-bounded backends.** A read tool against a per-second-capped external API (search, embeddings, LLM) hits 429s under concurrent dispatch when sequential would have stayed under the limit. Wall-clock gain is swapped for failure-recovery turns and API budget burn ([Arya AI: agentic system trade-offs](https://arya.ai/blog/navigating-trade-offs-in-agentic-systems)).
- **Weakly consistent read replicas.** List-then-get patterns across read replicas may return divergent results to concurrent reads; the agent reasons over a self-inconsistent view that sequential calls would have avoided.
- **Single-server fan-out without per-server caps.** Ten concurrent reads against an MCP server sized for sequential traffic blow the process, thread, or connection budget. Server-side throttling is the only remaining backstop; lacking it, the harness gain becomes a server-side outage.
- **In-page agents and embedded surfaces.** [WebMCP](../standards/webmcp.md) explicitly chose sequential-only tool calls within a page ([WebMCP spec §5.1](https://webmachinelearning.github.io/webmcp/)); embedded surfaces accept the latency cost rather than reason about read-only races in the page event loop. Hint-driven concurrency is a server-side-MCP optimisation, not a universal pattern.

The Codex 0.134.0 default enables hint-driven concurrency for every MCP server the user connects, regardless of whether the server author audited their annotations ([openai/codex PR #23750](https://github.com/openai/codex/pull/23750)). For operators running many third-party servers, the safe posture is to leave per-server concurrency disabled until the upstream audit lands.

## Example

A coding agent loads three MCP servers in a session: a documentation search server, an internal knowledge-base server, and a customer-data API server. The agent emits three tool calls in one turn — one against each server, all read-only.

**Before — sequential dispatch:**

```
t=0ms    search_docs("readOnlyHint")        dispatched
t=850ms  search_docs returns
t=850ms  kb_lookup("MCP concurrency")       dispatched
t=1900ms kb_lookup returns
t=1900ms get_customer(id=42)                dispatched
t=2400ms get_customer returns
                                            total: 2400ms
```

**After — hint-driven concurrency (all three tools annotated `readOnlyHint: true`):**

```
t=0ms    search_docs("readOnlyHint")        dispatched
t=0ms    kb_lookup("MCP concurrency")       dispatched
t=0ms    get_customer(id=42)                dispatched
t=850ms  search_docs returns
t=1050ms kb_lookup returns
t=500ms  get_customer returns
                                            total: 1050ms (max of three)
```

The wall-clock cost drops from `sum` to `max`. If `get_customer` is annotated `readOnlyHint: true` but the implementation logs the access and updates a `last_seen` timestamp, the third server is mis-classified — concurrent calls race on the timestamp update. The harness has no way to detect this without an upstream audit, which is why [tool-idempotency](../agent-readiness/audit-tool-idempotency.md) is a precondition, not a follow-up.

## Key Takeaways

- The MCP `readOnlyHint` is no longer just a safety hint — Codex CLI 0.134.0 wired it into the dispatch path, and that makes the annotation load-bearing for execution semantics.
- The hint defaults to `false`, so servers stay sequential until the author opts in — conservative by design ([Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md)).
- The MCP spec treats annotations as untrusted unless from a trusted server; hint-driven concurrency requires a per-server trust gate and an upstream tool-idempotency audit ([MCP specification](https://spec.modelcontextprotocol.io/specification/server/tools/)).
- The trade-off vs DAG-style explicit-dependency declaration is wiring cost vs ordering information: hint-driven concurrency is essentially free to wire but loses the ordering information the model already knew.
- Per-server concurrency caps and rate-limit-aware dispatch are the harness operator's responsibility — the Codex PR ships neither.

## Related

- [MCP Server Design](mcp-server-design.md)
- [Audit Tool Idempotency](../agent-readiness/audit-tool-idempotency.md)
- [Future-Based Asynchronous Function Calling](future-based-async-function-calling.md)
- [Asynchronous Agent I/O and Speculative Tools](../agent-design/asynchronous-agent-io-and-speculative-tools.md)
- [WebMCP: Browser-Hosted Tool Contracts](../standards/webmcp.md)
