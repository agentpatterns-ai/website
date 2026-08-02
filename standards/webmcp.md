---
title: "WebMCP: Browser-Hosted Tool Contracts for In-Page AI Agents"
description: "WebMCP is a W3C Community Group draft that lets web pages register JavaScript tools with the browser through navigator.modelContext so in-tab AI agents call them by name instead of actuating the DOM."
tags:
  - agent-design
  - tool-agnostic
  - standards
  - mcp
aliases:
  - Web Model Context Protocol
  - navigator.modelContext
last_reviewed: 2026-06-03
maturity: emerging
---

# WebMCP: Browser-Hosted Tool Contracts for In-Page AI Agents

> WebMCP, a W3C draft, lets a page register JavaScript tools via `navigator.modelContext` so an in-tab agent calls them by name instead of actuating the DOM.

## When WebMCP is the right tool

WebMCP fits a narrow surface: an interactive in-tab single-page application where a logged-in user and an agent share UI state and the agent operates only while the tab is open. Reach for WebMCP when:

- The user keeps the tab in the foreground and watches the agent work
- The action depends on session state already loaded into the page (filters, cart, multi-step form progress)
- A server-side MCP server would duplicate logic that today lives only in the client
- The agent is the browser's own (Antigravity, Claude for Chrome, a built-in or extension-installed agent), not a headless CI runner

Reach for [server-side MCP](mcp-protocol.md) instead when the agent runs headlessly, fans tool calls out in parallel, operates without an open tab, or already has an authoritative API. Google frames the two as complementary: server-side MCP answers from anywhere, WebMCP only while you are on the site ([Chrome for Developers: When to use WebMCP and MCP](https://developer.chrome.com/blog/webmcp-mcp-usage)).

## What WebMCP defines

The [WebMCP specification](https://webmachinelearning.github.io/webmcp/) is a Draft Community Group Report (20 May 2026) of the W3C Web Machine Learning Community Group, with editors from Microsoft and Google. It is not on the W3C Standards Track.

The spec adds one entry point — `navigator.modelContext` — and one tool descriptor shape: a JavaScript function with a `name`, a natural-language `description`, a JSON Schema `inputSchema`, and an `execute` callback. Tools carry annotations including `readOnlyHint` and `untrustedContentHint`. The latter signals output that may contain content from outside the application's trust boundary, propagating the MCP trust model into the page. Two registration shapes coexist ([Chrome for Developers: WebMCP](https://developer.chrome.com/docs/ai/webmcp)): an imperative API (`navigator.modelContext.registerTool({...})`) and a declarative API (HTML form-element annotations the browser synthesizes into a JSON Schema). An `exposedOrigins` list and a `tools` permissions-policy feature scope which embedded origins can invoke a page's tools.

## Why it works

Without WebMCP, a browser agent reaches the page's actions through DOM actuation — serializing rendered HTML, picking a target element by visual or accessibility cues, and simulating clicks and keystrokes ([Chrome for Developers: WebMCP](https://developer.chrome.com/docs/ai/webmcp)). Every step is open to interpretation.

WebMCP replaces actuation with a typed function call against a contract the page declares. The agent stops serializing HTML, and the "which element is the Add to Cart button" inference disappears because the page exposes an `addToCart` tool with an explicit JSON Schema. Chrome frames the gain as "increased speed, reliability, and precision" ([Chrome for Developers: WebMCP early preview](https://developer.chrome.com/blog/webmcp-epp)). Pilot numbers cited in secondhand coverage — a 67.6% token reduction and 97.9% task success — remain to be reproduced in independent benchmarks ([Manveer Chawla: The WebMCP False Economy](https://dev.to/manveer_chawla_64a7283d5a/the-webmcp-false-economy-why-we-dont-need-another-layer-of-abstraction-566e)).

## When this backfires

WebMCP carries real adoption and security costs. The cases below mark where reaching for it makes the system worse:

- Headless or background agents — WebMCP tools run on the page event loop and need an open tab; tool calls within a page are sequential, not parallel ([WebMCP spec §5.1](https://webmachinelearning.github.io/webmcp/)). CI runners and server-side cron jobs want [server-side MCP](mcp-protocol.md) instead.
- Long-tail sites with no UI investment budget — Twenty years of voluntary metadata (microformats, schema.org, OpenGraph) show that long-tail sites do not adopt optional protocols without distribution incentives ([Manveer Chawla: The WebMCP False Economy](https://dev.to/manveer_chawla_64a7283d5a/the-webmcp-false-economy-why-we-dont-need-another-layer-of-abstraction-566e)). For a restaurant menu, the browser synthesizing existing ARIA roles and form labels is more realistic than a `registerTool` call that never ships.
- Teams that already maintain a server-side API or MCP server — A WebMCP descriptor written against the in-page UI becomes a second tool contract that drifts from the server API; the same critique calls it "a second-class annotation that describes the product rather than owning it" ([Manveer Chawla: The WebMCP False Economy](https://dev.to/manveer_chawla_64a7283d5a/the-webmcp-false-economy-why-we-dont-need-another-layer-of-abstraction-566e)).
- Multi-tab browser agents with private data in adjacent tabs — An agent holding a logged-in session in tab A and visiting an attacker-controlled WebMCP page in tab B receives tool descriptors and outputs from an untrusted origin. The `untrustedContentHint` annotation acknowledges the threat but does not solve it, and Section 6 'Security and privacy considerations' of the May 2026 draft is still empty ([WebMCP spec §6](https://webmachinelearning.github.io/webmcp/)). Treat WebMCP as one more untrusted-content surface alongside the [lethal-trifecta threat model](../security/lethal-trifecta-threat-model.md).

## Current adoption status

WebMCP is available in Chrome 149 through the early preview program ([Chrome for Developers: WebMCP early preview](https://developer.chrome.com/blog/webmcp-epp), 2026-02-10). Brandon Walderman of Microsoft is lead editor alongside Khushal Sagar and Dominic Farolino of Google. The spec remains a Community Group Draft, not a W3C Recommendation.

The implementation existing does not mean agents use it. As of May 2026 no mainstream agent (Claude, ChatGPT's agent, Gemini, or Perplexity) calls `navigator.modelContext` tools directly; all still rely on DOM scraping or computer use, and with no agent demand sites have little reason to author descriptors ([freeCodeCamp: A Developer's Guide to WebMCP — Shipping a 0% Adoption Standard](https://www.freecodecamp.org/news/a-developers-guide-to-webmcp/)). Until a shipping agent consumes these tools, WebMCP is a capability to track, not one to build against. Follow changes at [webmachinelearning.github.io/webmcp](https://webmachinelearning.github.io/webmcp/).

## Example

A page registers a single tool that the browser's agent can call when the user asks to filter a search result. The page owns the state — the agent does not need to know how the filter UI is implemented:

```javascript
navigator.modelContext.registerTool({
  name: "applyPriceFilter",
  description: "Filter the visible search results to listings under the given maximum price in USD.",
  inputSchema: {
    type: "object",
    properties: {
      maxPriceUsd: {
        type: "number",
        minimum: 0,
        description: "Maximum price in USD; results above this are hidden."
      }
    },
    required: ["maxPriceUsd"]
  },
  annotations: { readOnlyHint: true },
  execute: ({ maxPriceUsd }) => {
    applyFilter({ price: { lte: maxPriceUsd } });
    return { filteredCount: getVisibleListings().length };
  }
});
```

The agent calls `applyPriceFilter({maxPriceUsd: 50})` by name and receives a structured result; it never has to find the price slider in the DOM. `readOnlyHint: true` lets the browser agent surface the call as a low-risk action ([WebMCP spec §4.2.1](https://webmachinelearning.github.io/webmcp/)).

## Key Takeaways

- WebMCP is a W3C Community Group draft, not a Standards Track recommendation — treat it as an experimental Chrome early-preview capability rather than a broadly supported standard.
- The right place for WebMCP is in-tab interactive flows where the agent and user share UI state; server-side MCP remains the right answer for headless, parallel, or multi-platform agents.
- Tool descriptors carry an `untrustedContentHint` annotation, but the spec's Security and Privacy section is still empty — the indirect-prompt-injection threat model is not yet normative.
- Two API shapes (Imperative `registerTool`, Declarative HTML annotations) coexist; the declarative form is the lighter on-ramp for standard form submissions.
- Adoption follows the same long-tail dynamics as past voluntary metadata standards; sites with no UI investment budget will not author WebMCP descriptors, so browser-side synthesis from existing accessibility metadata remains complementary.

## Related

- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
- [A2A Protocol](a2a-protocol.md)
