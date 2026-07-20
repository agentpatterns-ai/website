---
title: "MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time"
term: "MCP alwaysLoad"
description: "Decide which MCP servers earn unconditional context residence and which stay deferred behind tool search, using token cost, hit rate, and selection accuracy as signals."
aliases:
  - MCP eager vs deferred loading
  - alwaysLoad classification
  - MCP server load policy
tags:
  - tool-engineering
  - context-engineering
  - cost-performance
  - tool-agnostic
  - mcp
last_reviewed: 2026-06-18
maturity: adopted
---

# MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time

> Classify each MCP server as eager (`alwaysLoad`) or just-in-time by weighing always-paid context tax against on-demand discovery cost.

Related lesson: [Tool-Call Cost and Latency Budgeting](https://learn.agentpatterns.ai/tool-engineering/cost-and-latency-budgeting/) covers this concept in a hands-on lesson with quizzes.

## The decision surface

Claude Code 2.1.121 added an `alwaysLoad` option to MCP server config: when `true`, all tools from that server skip tool-search deferral and are always available ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The flag is the server-level inverse of the API's per-tool `defer_loading: true` parameter ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

Without `alwaysLoad`, a server's tools sit behind tool search. The model runs a search step that returns 3 to 5 matching `tool_reference` blocks, which expand into full definitions inline. With `alwaysLoad: true`, every tool from that server sits in the system-prompt prefix from the first turn.

The pattern generalizes. Any host with deferred MCP discovery — current Claude Code, future MCP-aware Cursor or Copilot — faces the same per-server choice. Which servers are core enough to deserve unconditional context residence, and which can be paid for only on demand? Other harnesses push the deferral axis further than per-server. OpenAI Codex added per-thread MCP executor activation with plugin discovery, so executors activate per conversation thread rather than globally ([OpenAI Codex changelog](https://developers.openai.com/codex/changelog)). This narrows the load decision to a per-conversation scope.

## What each side costs

Eager loading burns prefix tokens every turn whether the tool is used or not. A typical multi-server setup (GitHub, Slack, Sentry, Grafana, Splunk) consumes about 55K tokens in tool definitions before the conversation starts ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). It also dilutes selection accuracy. Anthropic reports that tool selection degrades significantly past 30 to 50 visible tools ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

JIT loading pays a search round-trip on first reference — a `server_tool_use` call before the actual tool call. It also depends on the model's ability to phrase a search query that retrieves the right tool. Tool descriptions that do not match natural-language tasks fail silently, and the agent reports "no tool available" when one exists.

JIT loading does not break prompt cache at the API design level. The docs are explicit: "Deferred tools are not included in the system-prompt prefix. When the model discovers a deferred tool through tool search, the tool definition is appended inline as a `tool_reference` block in the conversation. The prefix is untouched, so prompt caching is preserved" ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). This sets deferred loading apart from manual per-step tool swapping, which does invalidate cache (see [Dynamic Tool Fetching Cache Break](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md)).

The caveat is harness-level, not API-level. A deferred tool definition and `cache_control` are mutually exclusive on the same tool. The API rejects setting both — "Tools with defer_loading cannot use prompt caching" — and a Claude Code build that applied both flags unconditionally surfaced this as a hard error once 3 or more MCP servers were configured ([claude-code#30920](https://github.com/anthropics/claude-code/issues/30920)). The prefix-level cache benefit still holds, but do not assume an individual deferred tool block is itself cacheable, and check that your host does not double-set the flags.

## Classification rubric

Four signals decide each server:

| Signal | Eager (`alwaysLoad: true`) | JIT (default) |
|--------|---------------------------|---------------|
| Hit rate | Used in most sessions | Used in <20% of sessions |
| Definition size | Small relative to budget | Large enough to dominate |
| Latency tolerance | Cold-call round-trip is felt | Search step is acceptable |
| Description quality | Trustworthy under search | Keywords do not match task language |

The Anthropic docs turn the first two into a floor: tool search is worth enabling at 10 or more tools, or more than 10K tokens of total tool definitions ([Tool search tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Below that, eager-load every server. Above it, the per-server `alwaysLoad` decision matters.

The same docs give the explicit eager-load recommendation: "Keep your 3-5 most frequently used tools as non-deferred for optimal performance." `alwaysLoad` is the server-level mechanism for satisfying this guidance when those tools live behind an MCP server.

## Failure modes

- Silent context bloat: eager-loading a rarely-used MCP server pays the full token cost every turn for ambient capability the agent never invokes. Detect it with per-source context attribution (see [Context Usage Attribution](../observability/context-usage-attribution.md)).
- Cold-start prompt churn: JIT-loading the common-case server adds a search round-trip to the first turn that needs it. This costs latency and a discovery prompt that crowds the first-turn budget.
- Selection cliff: eager-loading too many servers past the 30-to-50 tool threshold degrades the agent's ability to pick correctly even when the right tool is visible.
- Search-miss invisibility: JIT-loading a server whose tool descriptions use jargon the model does not search for produces "tool not available" errors when the tool is right there. Check the descriptions before you defer.

## Example

A team runs five MCP servers in Claude Code: a project-specific search server (used every turn), a GitHub server (used in about 80% of sessions), a Linear server (used in about 15% of sessions for ticket lookup), and Sentry plus Grafana (used during incidents only).

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
- [Dynamic Tool Fetching Cache Break](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md)
- [Context Usage Attribution](../observability/context-usage-attribution.md)
