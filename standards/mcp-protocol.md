---
title: "MCP: The Open Protocol Connecting Agents to External Tools"
description: "The Model Context Protocol standardizes how AI agents connect to external tools and data sources, enabling any MCP-compliant host to use any MCP server."
tags:
  - agent-design
  - tool-agnostic
  - standards
  - mcp
aliases:
  - MCP
  - Model Context Protocol
last_reviewed: 2026-05-27
---

# MCP: The Open Protocol Connecting Agents to External Tools

> The Model Context Protocol is an open standard for connecting AI agents to external tools and data sources — agents speak MCP, tools implement MCP servers, and they interoperate regardless of which AI tool is running.

## What MCP Does

Before MCP, every AI coding tool required its own integration format — Claude Code plugins, VS Code Copilot extensions, Cursor integrations — so a database connector had to be rebuilt for each host.

The [Model Context Protocol](https://modelcontextprotocol.io) standardizes the interface. An agent host (Claude Code, GitHub Copilot, Cursor) speaks MCP on one side; an MCP server (a database connector, API wrapper, or local script) speaks MCP on the other. By analogy to TCP/IP, a standard protocol decouples the agent from the tooling.

## What MCP Servers Expose

An MCP server exposes three types of capabilities:

| Capability | Description | Example |
|-----------|-------------|---------|
| **Tools** | Functions the agent can call | `search_database`, `create_issue`, `run_tests` |
| **Resources** | Data sources the agent can read | File contents, API responses, database records |
| **Prompts** | Reusable prompt templates | Structured queries the server provides |

The agent discovers capabilities at startup; tool descriptions in the server manifest inform the agent how and when to call each tool.

## Transport Modes

MCP supports two transport modes ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)):

**stdio (local)** — the server runs as a subprocess on the same machine, communicating via stdin/stdout. Fast and sufficient for most developer tooling.

**Streamable HTTP (remote)** — the server runs remotely and accepts HTTP connections with optional streaming, enabling shared tooling across teams. The older HTTP+SSE transport is deprecated.

## Cross-Tool Portability

The same MCP server works with any MCP-compliant host. A Playwright [browser automation](../tool-engineering/browser-automation-for-research.md) server built for Claude Code also works in GitHub Copilot once Copilot supports MCP — an organization building an internal tools server builds it once. [GitHub Copilot's third-party agent documentation](https://docs.github.com/en/copilot/concepts/agents/about-third-party-agents) covers Copilot interop with agents such as Claude and Codex.

## Separation of Concerns

MCP enforces a clean split: the agent handles reasoning, planning, and language; the server handles tool execution. The agent does not need to know how a database query runs — it calls the tool and receives the result. Reasoning becomes auditable (what tools did the agent call, in what order?) separately from implementation.

## Ecosystem

[Hundreds of community servers](https://github.com/modelcontextprotocol/servers) span databases (PostgreSQL, SQLite), cloud providers (AWS, GCP), communication tools (Slack, GitHub), browsers (Playwright), and developer tooling. [github/awesome-copilot](https://github.com/github/awesome-copilot) catalogs Copilot-targeted servers; the broader ecosystem is indexed at [modelcontextprotocol.io](https://modelcontextprotocol.io).

## Example

The following `.claude/settings.json` snippet configures two MCP servers — one local (stdio) and one remote (Streamable HTTP) — demonstrating the two transport modes in practice.

```json
{
  "mcpServers": {
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com/tools"
    }
  }
}
```

The `playwright` server runs as a subprocess on the developer's machine — the agent communicates via stdin/stdout. The `internal-api` server runs remotely and is shared across the team; every developer's Claude Code session connects to the same hosted tool server without each installing a local copy.

Because both servers implement MCP, they are interchangeable from the agent's perspective. Switching from Claude Code to another MCP-compliant host (e.g., GitHub Copilot) requires no changes to either server.

## When This Backfires

MCP adds a protocol layer that is not always justified:

- **Single-tool integrations**: When an agent only ever calls one specific API, a native SDK call is simpler than standing up an MCP server. The abstraction buys nothing if portability is not a requirement.
- **Version skew**: Host and server must agree on the same MCP protocol version. When Anthropic or a tool vendor ships a breaking spec change, servers built against the old spec stop working until updated — a maintenance burden that native integrations avoid.
- **Subprocess overhead for stdio**: Each session spawns MCP servers as subprocesses — measurable startup cost in latency-sensitive or resource-constrained environments.
- **Organizational overhead**: Remote servers require hosting, auth, and availability SLAs. Teams without existing infra for hosted services may find operational cost exceeds the portability benefit.
- **Context and token bloat**: Tool schemas are injected into the model's context at startup. The GitHub MCP server alone has been measured at roughly 55,000 tokens across its 93 tool definitions ([The New Stack](https://thenewstack.io/how-to-reduce-mcp-token-bloat/)), and stacking multiple servers can consume a third or more of a 200k window before any user input. Mitigations like tool search and hierarchical routing ([MCP SEP-1576](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576)) are still being standardized; until then, treat per-server token cost as a budget item.
- **Supply-chain attack surface**: The stdio execution model leaves input sanitization to each server author. [Ox Security disclosed a systemic RCE-class flaw](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) in the official MCP SDKs in April 2026 affecting 150M+ downloads and 7,000+ exposed servers; [Anthropic confirmed the behaviour is by design](https://www.securityweek.com/by-design-flaw-in-mcp-could-enable-widespread-ai-supply-chain-attacks/). Treat third-party MCP servers as third-party shell scripts: select, pin, and sandbox accordingly. See [Blast Radius Containment](../security/blast-radius-containment.md).

Use MCP when building reusable tool servers shared across hosts or developers. For one-off integrations, evaluate whether the indirection adds value.

## Key Takeaways

- MCP decouples agent reasoning from tool execution — write a tool server once, use it with any MCP-compliant host
- MCP servers expose tools (callable), resources (readable), and prompts (templates)
- Two transports: stdio for local tooling, Streamable HTTP for remote and shared servers (HTTP+SSE is deprecated)
- Agent discovers available tools from the server manifest at startup
- Growing ecosystem of community servers for common infrastructure and developer tools

## Related

- [Agent-to-Agent (A2A) Protocol for AI Agent Development](a2a-protocol.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [Tool Calling Schema Standards for AI Agent Development](tool-calling-schema-standards.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
