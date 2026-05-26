---
title: "MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time"
description: "Decide which MCP servers earn unconditional context residence and which stay deferred behind tool search, using token cost, hit rate, and selection accuracy as signals."
aliases:
  - MCP eager vs deferred loading
  - alwaysLoad classification
  - MCP server load policy
tags:
  - tool-engineering
  - context-engineering
  - cost-performance
last_reviewed: 2026-05-27
---

# MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time

> Every MCP server is an eager-vs-JIT trade between always-paid context tax and on-demand discovery cost. Claude Code 2.1.121 made the choice a per-server flag; the decision rubric is reusable across any host that supports deferred tool loading.

## The Decision Surface

Claude Code 2.1.121 added an `alwaysLoad` option to MCP server config: when `true`, all tools from that server skip tool-search deferral and are always available ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The flag is the server-level inverse of the API's per-tool `defer_loading: true` parameter ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

Without `alwaysLoad`, a server's tools sit behind tool search — the model invokes a search step that returns 3-5 matching `tool_reference` blocks, which expand into full definitions inline. With `alwaysLoad: true`, every tool from that server is in the system-prompt prefix from the first turn.

The pattern generalises. Any host with deferred MCP discovery — current Claude Code, future MCP-aware Cursor or Copilot — faces the same per-server choice: which servers are core enough to deserve unconditional context residence, and which can be paid for only on demand?

## What Each Side Costs

**Eager loading** burns prefix tokens every turn whether the tool is used or not. A typical multi-server setup (GitHub, Slack, Sentry, Grafana, Splunk) consumes ~55K tokens in tool definitions before the conversation starts ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). It also dilutes selection accuracy: Anthropic reports tool selection degrades significantly past 30-50 visible tools ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

**JIT loading** pays a search round-trip on first reference — a `server_tool_use` call before the actual tool call — and depends on the model's ability to phrase a search query that retrieves the right tool. Tool descriptions that don't match natural-language tasks fail silently; the agent reports "no tool available" when one exists.

JIT loading does **not** break prompt cache. The docs are explicit: "Deferred tools are not included in the system-prompt prefix. When the model discovers a deferred tool through tool search, the tool definition is appended inline as a `tool_reference` block in the conversation. The prefix is untouched, so prompt caching is preserved" ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). This distinguishes deferred loading from manual per-step tool swapping, which does invalidate cache (see [Dynamic Tool Fetching Cache Break](../anti-patterns/dynamic-tool-fetching-cache-break.md)).

## Classification Rubric

Four signals decide each server:

| Signal | Eager (`alwaysLoad: true`) | JIT (default) |
|--------|---------------------------|---------------|
| **Hit rate** | Used in most sessions | Used in <20% of sessions |
| **Definition size** | Small relative to budget | Large enough to dominate |
| **Latency tolerance** | Cold-call round-trip is felt | Search step is acceptable |
| **Description quality** | Trustworthy under search | Keywords don't match task language |

The Anthropic docs operationalise the first two as a floor: tool search is worth enabling at 10+ tools or >10K tokens of total tool definitions ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Below that, eager-load every server. Above it, the per-server `alwaysLoad` decision matters.

The same docs give the explicit eager-load recommendation: "Keep your 3-5 most frequently used tools as non-deferred for optimal performance." `alwaysLoad` is the server-level mechanism for satisfying this guidance when those tools live behind an MCP server.

## Failure Modes

- **Silent context bloat** — eager-loading a rarely-used MCP server pays the full token cost every turn for ambient capability the agent never invokes. Detect with per-source context attribution (see [Context Usage Attribution](../observability/context-usage-attribution.md)).
- **Cold-start prompt churn** — JIT-loading the common-case server adds a search round-trip to the first turn that needs it, costing latency and a discovery prompt that crowds the first-turn budget.
- **Selection cliff** — eager-loading too many servers past the ~30-50 tool threshold degrades the agent's ability to pick correctly even when the right tool is visible.
- **Search-miss invisibility** — JIT-loading a server whose tool descriptions use jargon the model doesn't search for produces "tool not available" errors when the tool is right there. Audit description craft (see [Audit Tool Descriptions](../agent-readiness/audit-tool-descriptions.md)) before deferring.

## Example

A team runs five MCP servers in Claude Code: a project-specific search server (used every turn), a GitHub server (used in ~80% of sessions), a Linear server (used in ~15% of sessions for ticket lookup), and Sentry plus Grafana (used during incidents only).

```json
{
  "mcpServers": {
    "project-search": {
      "command": "mcp-server-search",
      "alwaysLoad": true
    },
    "github": {
      "command": "mcp-server-github",
      "alwaysLoad": true
    },
    "linear": {
      "command": "mcp-server-linear"
    },
    "sentry": {
      "command": "mcp-server-sentry"
    },
    "grafana": {
      "command": "mcp-server-grafana"
    }
  }
}
```

Project search and GitHub stay in the prefix every turn. Linear, Sentry, and Grafana load only when the model issues a tool search for "ticket", "error", or "metric" — paying the round-trip on the rare turns those capabilities are needed instead of the eager token tax on every turn.

## Key Takeaways

- `alwaysLoad: true` is the server-level switch that bypasses tool-search deferral for MCP servers in Claude Code 2.1.121
- Below 10 tools or 10K tokens of definitions, eager-load everything; above it, classify per server using hit rate, size, latency tolerance, and description quality
- Deferred loading preserves prompt cache because tool definitions append inline rather than mutate the prefix
- Eager-load the 3-5 most frequently used tools per the Anthropic guidance; defer the rest
- Audit descriptions before deferring — search-miss is the silent failure mode that turns JIT into "tool not available"

## Related

- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Production MCP Agent Stack](production-mcp-agent-stack.md)
- [Scoped MCP Server Discovery](scoped-mcp-server-discovery.md)
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md)
- [Dynamic Tool Fetching Cache Break](../anti-patterns/dynamic-tool-fetching-cache-break.md)
- [Context Usage Attribution](../observability/context-usage-attribution.md)
- [Audit Tool Output Token Cost](../agent-readiness/audit-tool-output-token-cost.md)
- [Audit Tool Descriptions](../agent-readiness/audit-tool-descriptions.md)
