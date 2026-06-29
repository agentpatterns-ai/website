---
title: "Production MCP Agent Stack: Sequencing Six Decisions into One Deployment"
term: "Production MCP Agent Stack"
description: "Six MCP design decisions — server location, tool grouping, schema delivery, result processing, auth, and token storage — constrain each other. Sequence matters more than the individual choices."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - tool-engineering
  - mcp
aliases:
  - production MCP reference architecture
  - end-to-end MCP deployment stack
last_reviewed: 2026-05-27
maturity: established
---

# Production MCP Agent Stack

> Moving an MCP agent from prototype to production means sequencing six orthogonal decisions that constrain each other. The patterns are well-documented; the sequence and the cross-pattern gotchas are where real deployments go wrong.

Learn it hands-on with the [Code Mode guided lesson and quizzes](https://learn.agentpatterns.ai/mcp-server-design/code-mode/).

Anthropic's [production MCP guidance](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp) (April 2026) frames MCP as "the critical layer" for cloud-resident agents. This page captures the order the guidance skips: which decision forecloses which, and which combinations silently break.

## The six-axis decision space

| Axis | Option A | Option B | Option C |
|------|----------|----------|----------|
| Server location | Local / stdio | Remote (HTTP/SSE) | — |
| Tool grouping | Flat 1:1 with API | Intent-grouped | Code-orchestrated (search + execute) |
| Schema delivery | Eager (all tools loaded) | Deferred via tool search (`defer_loading: true`) | — |
| Result processing | Raw-to-context | Programmatic tool calling (sandboxed) | — |
| OAuth client registration | Static / pre-registered | Dynamic Client Registration (DCR) | [Client ID Metadata Documents (CIMD)](../standards/oauth-client-id-metadata-documents.md) |
| Token storage | Per-session credentials | Vault with refresh | — |

Each axis has a defensible answer in isolation. The production question is which combinations compose cleanly.

## Decision sequencing

Resolve in this order. Each choice locks the option space for the next.

```mermaid
graph TD
    A[Server location] -->|Remote| B[OAuth required]
    A -->|Local| B2[Credential file or no auth]
    B --> C[CIMD vs DCR]
    C --> D[Token storage: vault or per-session]
    A --> E[Tool grouping]
    E -->|Flat or grouped| F[Schema delivery]
    E -->|Code-orchestrated| G[Sandbox availability]
    F -->|Tool search| H[Result processing]
    G --> H
    H -->|Programmatic| I[Sandbox + ZDR check]
```

1. Server location. Remote-first is the only configuration that reaches web, mobile, and cloud-hosted agents ([Anthropic, April 2026](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)). Remote forces OAuth. Local can use filesystem credentials.
2. OAuth flow. The [2025-11-25 MCP spec](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization#client-id-metadata-documents) adds CIMD as the recommended registration mechanism, with a faster first-time flow and fewer re-auth prompts than DCR. Note that CIMD provider support is still uneven (Keycloak experimental; WorkOS, Auth0, Authlete shipping through 2026). Practitioners report that real deployments often support both: CIMD for fast-moving distributed clients, DCR for vetted high-governance ones ([Scalekit, 2026](https://www.scalekit.com/blog/cimd-vs-dcr-how-to-choose-the-right-model-for-your-mcp-deployment)). Pick CIMD-first only when your IdP supports it.
3. Token storage. For multi-user cloud agents, [Claude Managed Agents vaults](https://platform.claude.com/docs/en/managed-agents/vaults#mcp-oauth-credential) register tokens once, inject them at session creation, and refresh automatically.
4. Tool grouping. Flat 1:1 API mirrors degrade at scale. [LongFuncEval (2025)](https://arxiv.org/abs/2505.10570) reports 7–85% selection-accuracy drops as catalogs grow. Intent-grouping ([toolset agentization](toolset-agentization.md)) shrinks the 1-of-N problem. Code-orchestration is the extreme form.
5. Schema delivery. [Tool search with `defer_loading: true`](advanced-tool-use.md) cuts tool-definition tokens by 85%+ but retrieves from whatever catalog you ship.
6. Result processing. [Programmatic tool calling](advanced-tool-use.md#programmatic-tool-calling-code-based-orchestration) cuts tokens ~37% on multi-step workflows but needs a sandbox and is not [Zero Data Retention](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#data-retention) eligible.

## Cross-pattern gotchas

The failure modes that matter in production only appear when patterns combine.

Dynamic fetching breaks the prompt cache, unless it is tool search. Rebuilding the tool list per step invalidates the cache prefix, because tool definitions sit atop the hierarchy (`tools` → `system` → `messages`). See the [dynamic tool fetching anti-pattern](../anti-patterns/dynamic-tool-fetching-cache-break.md). Tool search with `defer_loading: true` sidesteps this, because deferred tools are excluded from the cacheable prefix ([Anthropic advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).

Tool search and `input_examples` are mutually exclusive per catalog. Server-side tool search cannot surface tools that carry `input_examples` ([error handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool#error-handling)). Catalogs that rely on examples need standard calling or client-side search.

Retrieval quality binds at very large catalogs. Independent testing across 4,027 tools reports 56% (regex) and 64% (BM25) accuracy on straightforward queries, well below Anthropic's internal benchmarks ([Arcade.dev, December 2025](https://www.arcade.dev/blog/anthropic-tool-search-4000-tools-test/)). Plan custom client-side retrieval past a few thousand tools.

Programmatic calling is not ZDR-eligible and loses intermediate reasoning ([data retention](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#data-retention)). Only `stdout` returns.

Intent-grouping benefits from trajectory data. Regroup from real co-invocation traces once traffic lands ([toolset agentization](toolset-agentization.md)).

## Example: Cloudflare's two-tool MCP server

Cloudflare's [MCP server](https://github.com/cloudflare/mcp) is the reference extreme of intent-grouping plus code-orchestration. The API covers ~2,500 endpoints across Workers, DNS, Zero Trust, and the dashboard. A flat mirror would consume tens of thousands of tokens in definitions alone.

The design exposes two tools, `search` and `execute`, in roughly 1K tokens total ([Anthropic, April 2026](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)). Programmatic calling compounds the win. To "enable DNSSEC on all zones where it's disabled," the agent loops in a sandbox and returns only changed zones, instead of pulling thousands of records into context.

Every layer lines up: remote server → intent grouping at its extreme → deferred schemas unnecessary → programmatic calling for large result sets → OAuth plus vault on auth.

## When not to deploy the full stack

The stack earns its complexity at cloud-hosted multi-user scale. It is overkill in these cases:

- Under ~20 stable tools, single agent, single tenant. Intent-grouping and tool search add round-trips with no token benefit, so a direct API or CLI is simpler.
- Air-gapped or on-prem with no sandbox. Programmatic calling is inert without trusted code execution.
- Retrieval accuracy floor above ~80% on large catalogs. Server-side tool search drops below 65% at 4,000+ tools ([Arcade.dev](https://www.arcade.dev/blog/anthropic-tool-search-4000-tools-test/)), so plan custom retrieval or split the catalog.
- Catalogs that depend on `input_examples`. Tool search is mutually exclusive with examples, so pick one per catalog.

## Key Takeaways

- Six decisions — server location, tool grouping, schema delivery, result processing, OAuth, token storage — constrain each other; sequence matters more than any individual choice.
- Remote-first server forces OAuth, which forces the CIMD-vs-DCR decision, which shapes whether you need a vault.
- Tool search with `defer_loading: true` is the one form of dynamic tool loading that does not break the prompt cache; naive dynamic fetching does.
- Programmatic calling and `input_examples` + tool search are the two composition traps — verify sandbox availability and example-vs-search per catalog before committing.
- Cloudflare's two-tool server over ~2,500 endpoints is the reference case for how far intent-grouping and code-orchestration scale when every layer lines up.

## Related

- [MCP Server Design](mcp-server-design.md) — remote-first, primitive choice, schema design on the server side.
- [MCP Client Design](mcp-client-design.md) — host-side lifecycle, caching, and multi-server routing.
- [Toolset Agentization](toolset-agentization.md) — intent-grouping as a sub-agent pattern with trajectory-based adaptation.
- [Advanced Tool Use](advanced-tool-use.md) — tool search (`defer_loading`), programmatic calling, and input examples in depth.
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md) — the load-bearing gotcha that tool search sidesteps.
- [MCP Protocol](../standards/mcp-protocol.md) — the open standard these patterns build on.
