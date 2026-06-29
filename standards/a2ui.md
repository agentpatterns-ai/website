---
title: "A2UI: Framework-Agnostic Generative UI Standard for Agents"
description: "A2UI is an open standard for agents to emit declarative UI blueprints that a host application renders with its own native components and design system."
tags:
  - agent-design
  - tool-agnostic
  - standards
aliases:
  - agent-to-UI protocol
  - generative UI standard
last_reviewed: 2026-06-13
maturity: adopted
---

# A2UI: Framework-Agnostic Generative UI Standard

> A2UI is an open standard for agents to emit declarative UI blueprints that a host renders with its own native components.

## What A2UI is

[A2UI](https://a2ui.org/) is an Apache 2.0 spec from Google for describing UI as structured data. An agent emits JSON that references components from a catalog the host advertises, and the host renders them with its native widgets. [Google released v0.8 in December 2025](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/) and [shipped v0.9 on April 17, 2026](https://developers.googleblog.com/a2ui-v0-9-generative-ui/) with renderers for Flutter, Lit, Angular, and React plus a Python Agent SDK.

A2UI sits alongside the other agent-facing open standards: [llms.txt](llms-txt.md), [AGENTS.md](agents-md.md), [Agent Skills](agent-skills-standard.md), [MCP](mcp-protocol.md), and [A2A](a2a-protocol.md). It covers the agent-to-UI handoff.

## How A2UI works

A2UI moves the trust boundary from UI to data. The agent emits a JSON blueprint — "a flat list of components with ID references" — against a client-declared "Trusted Catalog" ([Google Developers Blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/)). It never emits HTML, JS, or component code.

```mermaid
graph LR
    A[Agent] -->|JSON blueprint| B[Transport]
    B -->|A2A / MCP / AG-UI / WS / REST| C[Host App]
    C -->|catalog lookup| D[Native Widgets]
    D --> E[Rendered UI]
```

The host keeps control over styling and security. The blueprint references only pre-approved components and cannot embed code. This mirrors MCP's tool model: structured schema in and out, and execution belongs to the host.

The alternatives have known problems. Sandboxed HTML/JS in an iframe "is heavy, can be visually disjointed (it rarely matches your app's native styling), and introduces complexity around security boundaries" ([Google Developers Blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/)) — the model that [MCP Apps](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/) uses. Direct DOM manipulation works locally but breaks remotely.

## What v0.9 shipped

The [v0.9 release](https://developers.googleblog.com/a2ui-v0-9-generative-ui/) consolidates the spec and adds production features:

- Python Agent SDK — `pip install a2ui-agent-sdk` — wraps schema management, catalog loading, and incremental JSON healing for streaming.
- Shared `web-core` library across the React, Lit, and Angular renderers.
- Client-defined functions — host-side validation and callbacks the agent can reference.
- Client-to-server data syncing for collaborative editing between user and agent.
- Multiple transports — A2UI runs over [A2A](a2a-protocol.md), [AG-UI](https://ag-ui.com/), [MCP](mcp-protocol.md), WebSockets, or REST.
- "Standard" components renamed to "Basic" — a concession that frontend teams plug in their own design systems.

The [google/A2UI](https://github.com/google/A2UI) repo is the source of truth for spec, catalogs, renderers, and samples.

## Adoption signals

Early integrations cluster around Google's surfaces and the AG-UI / CopilotKit ecosystem:

| Integration | Status | Source |
|-------------|--------|--------|
| Flutter GenUI SDK | Uses A2UI "under the covers" for remote agents | [Google Developers Blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/) |
| AG-UI / CopilotKit | Day-zero via `npx copilotkit@latest create my-app --framework a2ui` | [Google Developers Blog](https://developers.googleblog.com/a2ui-v0-9-generative-ui/) |
| Gemini Enterprise, Opal | Internal Google adopters | [Google Developers Blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/) |
| Oracle Agent Spec | Agent Spec + AG-UI + A2UI stack | [Oracle blog](https://blogs.oracle.com/ai-and-datascience/announcing-agent-spec-for-a2ui-copilotkit-ag-ui) |
| Vercel `json-renderer` | Experimental A2UI renderer | [Google Developers Blog](https://developers.googleblog.com/a2ui-v0-9-generative-ui/) |
| AG2 `A2UIAgent` | Native integration from the AutoGen team | [Google Developers Blog](https://developers.googleblog.com/a2ui-v0-9-generative-ui/) |

Cross-vendor backing is narrower than MCP's: A2UI is wider on frameworks and narrower on model providers.

## A2UI versus MCP Apps

The two approaches solve the same problem with opposite trust models ([The New Stack](https://thenewstack.io/agent-ui-standards-multiply-mcp-apps-and-googles-a2ui/); [A2UI docs](https://a2ui.org/introduction/agent-ui-ecosystem/)):

| Dimension | A2UI | MCP Apps |
|-----------|------|----------|
| Payload | Declarative JSON blueprint | HTML resource at a `ui://` URI |
| Rendering | Host's own native components | Sandboxed iframe |
| Design-system fidelity | Inherits host styling | Generic unless iframe is themed |
| Expressivity ceiling | Catalog intersection | Anything valid HTML/JS |
| Security model | Data, not code | Sandbox isolation |
| Cross-vendor backing | Google + AG-UI / CopilotKit | Anthropic, OpenAI (via MCP) |

Neither has won. [An upcoming bridge lets MCP servers return A2UI blueprints alongside HTML resources](https://www.copilotkit.ai/blog/the-state-of-agentic-ui-comparing-ag-ui-mcp-ui-and-a2ui-protocols), which suggests coexistence rather than head-to-head competition.

## When this backfires

A2UI is the wrong choice in four situations:

- Catalog-poor hosts: portability is bounded by host catalog ∩ agent references. The v0.9 "Standard" → "Basic" rename concedes there is no cross-host common set ([Google Developers Blog](https://developers.googleblog.com/a2ui-v0-9-generative-ui/)).
- Single-app, single-framework deployments: the wire format earns its overhead across trust boundaries. For one React app with one design system, [direct tool calls](tool-calling-schema-standards.md) are cheaper.
- Rapidly iterating UI: the catalog is a static contract. Products that change UI weekly spend more time syncing the catalog and agent prompt than they save.
- Consolidation risk: A2UI is pre-1.0, Google-led, and competes with MCP Apps, AG-UI native rendering, and OpenAI ChatKit. Picking it now bets on the spec surviving.

## Example

A reservation agent emits the following A2UI blueprint in place of a text back-and-forth ([adapted from Google's intro blog](https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/)):

```json
{
  "version": "0.9",
  "components": [
    {"id": "form", "type": "Card", "children": ["header", "date", "time", "submit"]},
    {"id": "header", "type": "Text", "props": {"text": "Book a table"}},
    {"id": "date", "type": "DatePicker", "props": {"label": "Date"}},
    {"id": "time", "type": "Select", "props": {
      "label": "Time",
      "options": ["5:00", "5:30", "6:00", "8:30", "9:00", "9:30", "10:00"]
    }},
    {"id": "submit", "type": "Button", "props": {"label": "Reserve", "action": "submit"}}
  ]
}
```

The host receives the blueprint over A2A, AG-UI, or MCP transport. It looks each `type` up in its catalog — `Card`, `Text`, `DatePicker`, `Select`, `Button` — and renders the form with its own styled components. The agent did not produce HTML, and the host did not trust opaque code. The same blueprint, sent to a Flutter client, renders as native Flutter widgets.

## Key Takeaways

- A2UI is the wire format for agent-to-UI handoff: structured JSON blueprints referencing a host-declared component catalog.
- The mechanism moves the trust boundary from UI to data — the host renders only components it pre-approved.
- v0.9 ships Python Agent SDK, first-party renderers for Flutter / Lit / Angular / React, and transports over A2A, AG-UI, MCP, REST, and WebSockets.
- The portability ceiling is the catalog intersection, not the spec — hosts with sparse design systems gain little.
- MCP Apps occupies adjacent territory with an iframe-based trust model; neither standard has won as of v0.9.
- The overhead earns out in multi-agent meshes and catalog-rich hosts; it does not earn out in single-framework single-team apps.

## Related

- [Agent-to-Agent (A2A) Protocol](a2a-protocol.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [AGENTS.md: A README for AI Coding Agents](agents-md.md)
- [llms.txt: Making Your Project Discoverable to AI Agents](llms-txt.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [Interactive Canvases: Agent-Generated Visual Artifacts as Outputs](../emerging/interactive-canvas-outputs.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
