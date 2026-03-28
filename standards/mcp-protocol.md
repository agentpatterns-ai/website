---
title: "MCP: The Open Protocol Connecting Agents to External Tools"
description: "The Model Context Protocol standardizes how AI agents connect to external tools and data sources, enabling any MCP-compliant host to use any MCP server."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - MCP
  - Model Context Protocol
---

# MCP: The Open Protocol Connecting Agents to External Tools

> The Model Context Protocol is an open standard for connecting AI agents to external tools and data sources — agents speak MCP, tools implement MCP servers, and they interoperate regardless of which AI tool is running.

## What MCP Does

Before MCP, each AI coding tool implemented tool integrations independently [unverified]. Claude Code had its own plugin format, VS Code Copilot had extensions, Cursor had integrations. An MCP server for a database had to be rebuilt separately for each tool.

The [Model Context Protocol](https://modelcontextprotocol.io) standardizes the interface. An agent host (Claude Code, GitHub Copilot, Cursor) speaks MCP on one side. An MCP server (a database connector, an API wrapper, a local script) speaks MCP on the other. The two communicate over a standard protocol — which host is running does not matter.

This is the TCP/IP analogy: a standard protocol decouples the agent from the tooling.

## What MCP Servers Expose

An MCP server exposes three types of capabilities:

| Capability | Description | Example |
|-----------|-------------|---------|
| **Tools** | Functions the agent can call | `search_database`, `create_issue`, `run_tests` |
| **Resources** | Data sources the agent can read | File contents, API responses, database records |
| **Prompts** | Reusable prompt templates | Structured queries the server provides |

The agent discovers available capabilities from the server at startup. Tool descriptions in the server's manifest inform the agent how and when to call each tool.

## Transport Modes

MCP supports two transport modes ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)):

**stdio (local)** — the MCP server runs as a subprocess on the same machine. The agent communicates via stdin/stdout. Fast, simple, and sufficient for most developer tooling.

**Streamable HTTP (remote)** — the MCP server runs remotely and accepts HTTP connections with optional streaming. The older HTTP+SSE transport is deprecated. Enables shared tooling across teams and cloud-hosted tool servers.

## Cross-Tool Portability

The same MCP server works with any MCP-compliant agent host. A Playwright [browser automation](../tool-engineering/browser-automation-for-research.md) server built for Claude Code sessions also works in GitHub Copilot when Copilot supports MCP. An organization building an internal tools MCP server builds it once.

[GitHub Copilot's third-party agent documentation](https://docs.github.com/en/copilot/concepts/agents/about-third-party-agents) covers how Copilot works with third-party coding agents such as Claude and Codex.

## Separation of Concerns

MCP enforces a clean separation: the agent handles reasoning, planning, and language; the MCP server handles tool execution. The agent does not need to know how the database query executes — it calls the tool and receives the result.

This makes agent reasoning auditable (what tools did the agent call, in what order?) separately from tool implementation (how does the database connector work?).

## Ecosystem

The MCP ecosystem has grown rapidly since the protocol's release [unverified]. Community MCP servers exist for databases (PostgreSQL, SQLite), cloud providers (AWS, GCP), communication tools (Slack, GitHub), browsers (Playwright), and developer tooling. [github/awesome-copilot](https://github.com/github/awesome-copilot) catalogs community servers for Copilot; the broader MCP ecosystem is indexed at [modelcontextprotocol.io](https://modelcontextprotocol.io).

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

## Key Takeaways

- MCP decouples agent reasoning from tool execution — write a tool server once, use it with any MCP-compliant host
- MCP servers expose tools (callable), resources (readable), and prompts (templates)
- Two transports: stdio for local tooling, Streamable HTTP for remote and shared servers (HTTP+SSE is deprecated)
- Agent discovers available tools from the server manifest at startup
- Growing ecosystem of community servers for common infrastructure and developer tools

## Related

- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [Agent-to-Agent (A2A) Protocol for AI Agent Development](a2a-protocol.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [OpenTelemetry for Agent Observability](opentelemetry-agent-observability.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [Tool Calling Schema Standards for AI Agent Development](tool-calling-schema-standards.md)
