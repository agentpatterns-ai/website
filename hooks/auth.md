# Agent Access — agentpatterns.ai

**No authentication is required.** Every agent-facing surface on this site is public, anonymous,
and read-only. There is no registration step, no API key, and no token endpoint. The OAuth
discovery documents (`/.well-known/openid-configuration`, `/.well-known/oauth-authorization-server`,
`/.well-known/oauth-protected-resource`) are **deliberately absent**: this site has no protected
APIs, and publishing authorization-server metadata for infrastructure that does not exist would
only send your token flow to a 404. If you are an agent looking for how to authenticate — you
already have full access.

## What you can use, without credentials

| Surface | Where |
|---|---|
| MCP search endpoint (streamable HTTP, tools capability) | `https://024a397e-1bb1-47a1-a5c6-ba5914b1d289.search.ai.cloudflare.com/mcp` |
| Search API (POST, OpenAI-style `messages` body) | `https://024a397e-1bb1-47a1-a5c6-ba5914b1d289.search.ai.cloudflare.com/search` |
| Markdown content negotiation | any page URL with `Accept: text/markdown` (or fetch `<page-url>index.md` directly) |
| Corpus indexes | [/llms.txt](/llms.txt) · [/llms-full.txt](/llms-full.txt) |
| API catalog (RFC 9727) | [/.well-known/api-catalog](/.well-known/api-catalog) |
| MCP server card | [/.well-known/mcp/server-card.json](/.well-known/mcp/server-card.json) |
| Agent skills index | [/.well-known/agent-skills/index.json](/.well-known/agent-skills/index.json) |
| DNS discovery | SVCB records at `_index._agents` / `_mcp._agents` (DNSSEC-signed) |

## Terms

Content is licensed **CC BY 4.0** — reuse requires attribution to
[agentpatterns.ai](https://agentpatterns.ai/). Crawling, AI grounding, and AI training are all
welcome; the machine-readable form of that policy is the `Content-Signal` line in
[/robots.txt](/robots.txt). Rate limiting is Cloudflare-default — be a polite client.
