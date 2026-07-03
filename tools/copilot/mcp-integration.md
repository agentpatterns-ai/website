---
title: "GitHub Copilot MCP Integration for AI Agent Development"
description: "Connect Copilot to external tools and data sources via the Model Context Protocol. Configure MCP servers for agent mode, the coding agent, and the CLI."
tags:
  - agent-design
  - copilot
  - mcp
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
---

# GitHub Copilot MCP Integration

> Connect Copilot to external tools and data sources via the Model Context Protocol.

## Overview

GitHub Copilot supports [MCP servers](https://docs.github.com/en/copilot/tutorials/enhance-agent-mode-with-mcp) across agent mode, the [coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent), and the CLI. MCP is a standard way to connect agents to external tools, databases, APIs, and services.

## GitHub MCP server

GitHub maintains an [official MCP server](https://docs.github.com/en/copilot/concepts/context/mcp) that gives Copilot Chat direct access to GitHub's APIs. In VS Code, you reach it remotely, with no local setup. You can enable or disable specific toolsets to control which GitHub API capabilities the agent sees.

## Custom MCP servers

Add custom MCP servers for any external tool or service. Configure them in VS Code settings or in the CLI configuration. The MCP Registry lists the servers available.

## Coding agent and MCP

The coding agent can use [MCP tools](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent) from local and remote servers. It supports tools only, not resources or prompts.

## VS Code MCP bridging (v1.113+)

[VS Code 1.113](https://code.visualstudio.com/updates/v1_113) automatically bridges MCP servers registered in VS Code to Copilot CLI and Claude agent sessions running in the editor. Tools you configure in `settings.json` are then available to CLI and Claude agents, with no separate configuration.

## CLI and MCP

Copilot CLI ships with the [GitHub MCP server built in](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers). You can add custom MCP servers through the interactive `/mcp add` command or the `~/.copilot/mcp-config.json` file.

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

`enabledToolsets` on the GitHub server restricts which GitHub API capabilities the agent sees. Omitting the `admin` and `repos` toolsets limits the damage if the agent acts on an ambiguous instruction. The Postgres server runs as a local stdio process, so it exposes no network port, and it reads the connection string from the environment rather than hardcoding it.

## Key Takeaways

- MCP is the standard protocol connecting Copilot to external tools across all surfaces
- GitHub's official MCP server provides GitHub API access out of the box
- Custom MCP servers extend Copilot to any external service
- The coding agent supports MCP tools (not resources or prompts)
- VS Code 1.113+ bridges registered MCP servers to CLI and Claude agent sessions automatically

## When this backfires

- Tool sprawl inflates context and cost. Every registered MCP server exposes tool schemas into the agent's context window. Ten servers can add thousands of tokens per turn before the agent does anything useful, pushing common workflows toward larger models or context truncation.
- Each custom server is a new supply-chain surface. MCP servers launched with `npx` or maintained by the community run with the agent's permissions and see whatever prompts you route through them. A compromised server package can exfiltrate secrets from environment variables (like the `POSTGRES_CONNECTION_STRING` above) or inject instructions into tool output.
- Remote MCP endpoints become availability dependencies. Agent sessions that rely on a remote MCP server inherit its uptime, rate limits, and auth expiry. An expired token or flaky provider surfaces as opaque agent failures rather than clear infrastructure errors.
- Built-in capabilities often suffice. For tasks covered by Copilot's native file, terminal, and GitHub tools, adding an MCP server duplicates capability without adding value. Use MCP when the data or action genuinely lives outside the agent's default surface.

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Copilot Extensions](copilot-extensions.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Monorepo Skill and Agent Discovery](monorepo-hierarchical-discovery.md)
- [GitHub Copilot SDK](copilot-sdk.md)
- [MCP Protocol](../../standards/mcp-protocol.md)
