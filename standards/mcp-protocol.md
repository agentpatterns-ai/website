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
maturity: established
---

# MCP: The Open Protocol Connecting Agents to External Tools

> The Model Context Protocol is an open standard for connecting AI agents to external tools and data sources — agents speak MCP, tools implement MCP servers, and they interoperate regardless of which AI tool is running.

Learn it hands-on with the [Capstone — Ship a Server Agents Can Drive](https://learn.agentpatterns.ai/mcp-server-design/capstone/) guided lesson and quizzes.

## What MCP does

Before MCP, every AI coding tool needed its own integration format — Claude Code plugins, VS Code Copilot extensions, Cursor integrations — so you had to rebuild a database connector for each host.

The [Model Context Protocol](https://modelcontextprotocol.io) standardizes the interface. An agent host (Claude Code, GitHub Copilot, Cursor) speaks MCP on one side. An MCP server (a database connector, API wrapper, or local script) speaks MCP on the other. As with TCP/IP, a standard protocol decouples the agent from the tooling.

## What MCP servers expose

An MCP server exposes three types of capabilities:

| Capability | Description | Example |
|-----------|-------------|---------|
| Tools | Functions the agent can call | `search_database`, `create_issue`, `run_tests` |
| Resources | Data sources the agent can read | File contents, API responses, database records |
| Prompts | Reusable prompt templates | Structured queries the server provides |

The agent discovers capabilities at startup. Tool descriptions in the server manifest tell the agent how and when to call each tool.

## Transport modes

MCP supports two transport modes ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)):

- stdio (local): the server runs as a subprocess on the same machine and communicates over stdin and stdout. Fast and enough for most developer tooling.
- Streamable HTTP (remote): the server runs remotely and accepts HTTP connections with optional streaming, so teams can share tooling. The older HTTP+SSE transport is deprecated.

## Cross-tool portability

The same MCP server works with any MCP-compliant host. A Playwright [browser automation](../tool-engineering/browser-automation-for-research.md) server built for Claude Code also works in GitHub Copilot once Copilot supports MCP, so an organization builds its internal tools server once. [GitHub Copilot's third-party agent documentation](https://docs.github.com/en/copilot/concepts/agents/about-third-party-agents) covers how Copilot works with agents such as Claude and Codex.

## Separation of concerns

MCP splits the work cleanly. The agent handles reasoning, planning, and language. The server handles tool execution. The agent does not need to know how a database query runs — it calls the tool and receives the result. You can then audit the reasoning (which tools did the agent call, and in what order) separately from the implementation.

## Community servers

[Hundreds of community servers](https://github.com/modelcontextprotocol/servers) span databases (PostgreSQL, SQLite), cloud providers (AWS, GCP), communication tools (Slack, GitHub), browsers (Playwright), and developer tooling. [github/awesome-copilot](https://github.com/github/awesome-copilot) catalogs Copilot-targeted servers, and [modelcontextprotocol.io](https://modelcontextprotocol.io) indexes the wider set.

## Example

This `.claude/settings.json` snippet configures two MCP servers — one local (stdio) and one remote (Streamable HTTP) — to show both transport modes.

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

The `playwright` server runs as a subprocess on the developer's machine, and the agent communicates over stdin and stdout. The `internal-api` server runs remotely and the team shares it. Every developer's Claude Code session connects to the same hosted tool server, so no one installs a local copy.

Because both servers implement MCP, the agent treats them as interchangeable. Moving from Claude Code to another MCP-compliant host (for example, GitHub Copilot) needs no changes to either server.

## When this backfires

MCP adds a protocol layer that is not always worth it:

- Single-tool integrations: when an agent only ever calls one API, a native SDK call is simpler than standing up an MCP server. The abstraction buys nothing if you do not need portability.
- Version skew: host and server must agree on the same MCP protocol version. When Anthropic or a tool vendor ships a breaking spec change, servers built against the old spec stop working until someone updates them — a maintenance burden that native integrations avoid.
- Subprocess overhead for stdio: each session spawns MCP servers as subprocesses, a measurable startup cost in latency-sensitive or resource-constrained environments.
- Organizational overhead: remote servers need hosting, auth, and availability SLAs. Teams without existing infrastructure for hosted services may find the operational cost outweighs the portability benefit.
- Context and token bloat: MCP injects tool schemas into the model's context at startup. The GitHub MCP server alone has been measured at roughly 55,000 tokens across its 93 tool definitions ([The New Stack](https://thenewstack.io/how-to-reduce-mcp-token-bloat/)), and stacking several servers can consume a third or more of a 200k window before any user input. Mitigations such as tool search and hierarchical routing ([MCP SEP-1576](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576)) are still being standardized. Until then, treat per-server token cost as a budget item.
- Supply-chain attack surface: the stdio execution model leaves input sanitization to each server author. [Ox Security disclosed a systemic RCE-class flaw](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) in the official MCP SDKs in April 2026, affecting 150M+ downloads and 7,000+ exposed servers, and [Anthropic confirmed the behavior is by design](https://www.securityweek.com/by-design-flaw-in-mcp-could-enable-widespread-ai-supply-chain-attacks/). Treat third-party MCP servers as third-party shell scripts: select, pin, and sandbox them. See [Blast Radius Containment](../security/blast-radius-containment.md).

Use MCP when building reusable tool servers shared across hosts or developers. For one-off integrations, evaluate whether the indirection adds value.

## FAQ

**Do I need an MCP server for every integration?**

No. When an agent only ever calls one API, a native SDK call is simpler than standing up an MCP server, and the abstraction buys nothing if you do not need portability. Use MCP when you are building reusable tool servers shared across hosts or developers; for one-off integrations, evaluate first whether the extra protocol layer adds value.

**How much context does an MCP server consume?**

More than most teams budget for. MCP injects tool schemas into the model's context at startup: the GitHub MCP server alone has been measured at roughly 55,000 tokens across its 93 tool definitions ([The New Stack](https://thenewstack.io/how-to-reduce-mcp-token-bloat/)), and stacking several servers can consume a third or more of a 200k window before any user input arrives.

**How much should I trust a third-party MCP server?**

Treat it like a third-party shell script: select, pin, and sandbox it. The stdio execution model leaves input sanitization to each server author, and [Ox Security disclosed an RCE-class flaw](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) in the official MCP SDKs affecting 150M+ downloads and 7,000+ exposed servers, which [Anthropic confirmed is by design](https://www.securityweek.com/by-design-flaw-in-mcp-could-enable-widespread-ai-supply-chain-attacks/).

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
- [Governance Layer for Agent Interoperability Protocols](protocol-governance-layer.md)
- [Tool Calling Schema Standards for AI Agent Development](tool-calling-schema-standards.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
