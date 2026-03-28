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

The coding agent can use [MCP tools](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent) from both local and remote servers. Currently supports tools only — not resources or prompts.

## VS Code MCP Bridging (v1.113+)

As of [VS Code 1.113](https://code.visualstudio.com/updates/v1_113), MCP servers registered in VS Code are automatically bridged to Copilot CLI and Claude agent sessions running within the editor. This means tools configured in your `settings.json` are available to CLI and Claude agents without separate configuration.

## CLI + MCP

Copilot CLI ships with the GitHub MCP server built in [unverified — not confirmed in public CLI docs] and supports adding custom MCP servers for extended capabilities.

## Example

The following VS Code `settings.json` snippet configures two MCP servers for Copilot agent mode: the built-in GitHub MCP server with a restricted toolset, and a custom Postgres server for direct database queries.

```json
{
  "github.copilot.chat.mcp.servers": [
    {
      "name": "github",
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "enabledToolsets": ["issues", "pull_requests", "code_search"]
    },
    {
      "name": "postgres",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${env:DATABASE_URL}"
      }
    }
  ]
}
```

`enabledToolsets` on the GitHub server restricts which GitHub API capabilities are exposed — omitting `admin` and `repos` toolsets reduces the blast radius if the agent acts on an ambiguous instruction. The Postgres server runs as a local stdio process, so no network port is exposed; the connection string is read from the environment rather than hardcoded.

## Key Takeaways

- MCP is the standard protocol connecting Copilot to external tools across all surfaces
- GitHub's official MCP server provides GitHub API access out of the box
- Custom MCP servers extend Copilot to any external service
- The coding agent supports MCP tools (not resources or prompts)
- VS Code 1.113+ bridges registered MCP servers to CLI and Claude agent sessions automatically

## Unverified Claims

- Copilot CLI ships with the GitHub MCP server built in [unverified — not confirmed in public CLI docs]

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Copilot Extensions](copilot-extensions.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [MCP Protocol](../../standards/mcp-protocol.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
