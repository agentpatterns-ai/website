---
title: "GitHub Copilot MCP Integration for AI Agent Development"
description: "Connect Copilot to external tools and data sources via the Model Context Protocol. Configure MCP servers for agent mode, the coding agent, and the CLI."
tags:
  - agent-design
  - copilot
---

# GitHub Copilot MCP Integration

> Connect Copilot to external tools and data sources via the Model Context Protocol.

## Overview

GitHub Copilot supports [MCP servers](https://docs.github.com/en/copilot/tutorials/enhance-agent-mode-with-mcp) across agent mode, the [coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent), and the CLI. MCP provides a standardized way to connect agents to external tools, databases, APIs, and services.

## GitHub MCP Server

GitHub maintains an [official MCP server](https://docs.github.com/en/copilot/concepts/context/mcp) that provides access to GitHub's APIs directly from Copilot Chat. In VS Code, it is accessible remotely without local setup. You can enable or disable specific toolsets to control which GitHub API capabilities are exposed.

## Custom MCP Servers

Add custom MCP servers for any external tool or service. Configure them in VS Code settings or in the CLI configuration. The MCP Registry provides a curated list of available servers.

## Coding Agent + MCP

The coding agent can use [MCP tools](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent) from both local and remote servers. The GitHub MCP server and the Playwright MCP server are pre-configured by default. Tools only — resources and prompts are not supported, and remote servers that require OAuth for authentication are not currently supported.

## VS Code MCP Bridging (v1.113+)

As of [VS Code 1.113](https://code.visualstudio.com/updates/v1_113), MCP servers registered in VS Code are automatically bridged to Copilot CLI and Claude agent sessions running within the editor. This means servers configured in your workspace `.vscode/mcp.json` or user profile are available to CLI and Claude agents without separate configuration.

## CLI + MCP

Copilot CLI ships with the [GitHub MCP server built in](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) and supports adding custom MCP servers via the interactive `/mcp add` command or by editing `~/.copilot/mcp-config.json` directly. Companion commands include `/mcp show`, `/mcp edit`, `/mcp delete`, and `/mcp disable`/`/mcp enable`.

## Example

The following [`.vscode/mcp.json`](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) snippet configures two MCP servers: the remote GitHub MCP server with a restricted toolset, and a custom Postgres server for direct database queries.

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "X-MCP-Toolsets": "issues,pull_requests,code_search"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${env:DATABASE_URL}"
      }
    }
  }
}
```

The [`X-MCP-Toolsets` header](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) restricts which GitHub API capabilities are exposed — omitting `admin` and `repos` toolsets reduces the blast radius if the agent acts on an ambiguous instruction. (An equivalent path-segment form, `https://api.githubcopilot.com/mcp/x/issues`, supports a single toolset; use the header for multiple.) The Postgres server runs as a local stdio process, so no network port is exposed; the connection string is read from the environment rather than hardcoded.

## Key Takeaways

- MCP is the standard protocol connecting Copilot to external tools across all surfaces
- GitHub's official MCP server provides GitHub API access out of the box; the coding agent also enables Playwright by default
- Custom MCP servers extend Copilot to any external service
- The coding agent supports MCP tools only — not resources, prompts, or remote servers that require OAuth
- VS Code 1.113+ bridges registered MCP servers to CLI and Claude agent sessions automatically

## When This Backfires

- **Tool sprawl inflates context and cost.** Every registered MCP server exposes tool schemas into the agent's context window. Ten servers can add thousands of tokens per turn before the agent does anything useful, pushing common workflows toward larger models or context truncation.
- **Each custom server is a new supply-chain surface.** `npx`-launched or community-maintained MCP servers execute with the agent's permissions and see whatever prompts you route through them. A compromised server package can exfiltrate secrets from environment variables (like the `POSTGRES_CONNECTION_STRING` above) or inject instructions into tool output.
- **Remote MCP endpoints become availability dependencies.** Agent sessions that rely on a remote MCP server inherit its uptime, rate limits, and auth expiry. An expired token or flaky provider surfaces as opaque agent failures rather than clear infrastructure errors.
- **Built-in capabilities often suffice.** For tasks covered by Copilot's native file, terminal, and GitHub tools, adding an MCP server duplicates capability without adding value. Reach for MCP when the data or action genuinely lives outside the agent's default surface.

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Copilot Extensions](copilot-extensions.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Monorepo Skill and Agent Discovery](monorepo-hierarchical-discovery.md)
- [GitHub Copilot SDK](copilot-sdk.md)
- [MCP Protocol](../../standards/mcp-protocol.md)
