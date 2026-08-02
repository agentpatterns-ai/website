---
title: "Ask the Docs: AI Search Over Agent Patterns"
description: "Ask questions of the Agent Patterns corpus in natural language — AI-powered search over every page, with cited source links, served by Cloudflare AI Search."
tags:
  - tool-agnostic
noindex: true
---

# Ask the Docs

> Natural-language search over the full Agent Patterns corpus — ask a question, get an answer grounded in the site's pages, with links to the sources it drew from.

<!-- Cloudflare AI Search UI snippet (#9917). Version-pinned deliberately —
     the component is early (v0.x); bump the asset path on purpose, not by
     floating on latest. -->
<script type="module" src="https://024a397e-1bb1-47a1-a5c6-ba5914b1d289.search.ai.cloudflare.com/assets/v0.0.25/search-snippet.es.js"></script>

<search-bar-snippet
  api-url="https://024a397e-1bb1-47a1-a5c6-ba5914b1d289.search.ai.cloudflare.com/"
  placeholder="Ask a question — e.g. “when should research and execution run in separate sessions?”"
  max-results="20"
  max-render-results="10"
  show-url="true"
  show-date="true"
  theme="auto">
</search-bar-snippet>

Answers are generated from the pages of this site and nothing else; every result links to the page it came from. For exact-phrase or keyword lookup, the header search (the `/` shortcut) remains the faster tool.

## For AI agents

Agents can query the same index directly over MCP (streamable HTTP, no authentication, read-only):

```
https://024a397e-1bb1-47a1-a5c6-ba5914b1d289.search.ai.cloudflare.com/mcp
```

The endpoint is advertised in this site's [MCP server card](/.well-known/mcp/server-card.json), alongside the other machine-readable surfaces: [llms.txt](/llms.txt), per-page markdown twins (`<page-url>index.md`), and the [agent-skills index](/.well-known/agent-skills/index.json).

## Related

- [What is GEO](geo/what-is-geo.md) — why this site is structured for AI retrieval
- [How AI Engines Cite](geo/how-ai-engines-cite.md) — what makes a page citable
- [This site's agent access policy](/auth.md) — no authentication, all agent surfaces public ([robots.txt](/robots.txt) carries the machine-readable form)
- [AI Crawler Policy](geo/ai-crawler-policy.md) — guidance on setting a robots.txt/WAF policy for AI crawlers on your own site
