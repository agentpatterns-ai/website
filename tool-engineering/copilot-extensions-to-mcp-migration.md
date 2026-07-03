---
title: "Proprietary-to-Open-Standard Tool Migration (Copilot Extensions to MCP)"
term: "Proprietary-to-Open-Standard Tool Migration"
description: "How to migrate from deprecated Copilot Extensions to MCP servers, and the broader pattern of proprietary extension systems converging on open protocols."
tags:
  - agent-design
  - workflows
  - copilot
  - tool-engineering
  - mcp
aliases:
  - Copilot Extensions to MCP Migration
last_reviewed: 2026-05-27
maturity: established
---

# Proprietary-to-Open-Standard Tool Migration (Copilot Extensions to MCP)

> When a proprietary extension system gets replaced by an open protocol, the right response is to rebuild on the standard — not port the old architecture. The Copilot Extensions deprecation exemplifies this pattern.

GitHub [deprecated Copilot Extensions (GitHub Apps) on September 24, 2025](https://github.blog/changelog/2025-09-24-deprecate-github-copilot-extensions-github-apps/). It blocked new extension creation immediately and disabled all functionality on November 10, 2025. GitHub replaced the system with [MCP servers](../standards/mcp-protocol.md).

## What changed architecturally

| Dimension | Copilot Extensions (deprecated) | MCP Servers |
|-----------|----------------------------------|-------------|
| Standard | Proprietary (GitHub Apps) | Open (MCP / JSON-RPC 2.0) |
| Invocation | `@mention` in Copilot Chat | Tool-calling by agent mode, autonomous use by coding agent |
| Hosting | Remote server required | Local (stdio) or remote (Streamable HTTP) |
| Tool reach | Copilot only | Copilot, Claude Code, Cursor, VS Code, ChatGPT, any MCP client |
| Distribution | GitHub Marketplace or private org | Any registry, or none — direct config |
| AI abstraction | Skillsets: Copilot handles all LLM logic | None — server exposes tools, client decides when to call them |
| Enterprise governance | GitHub App permissions | [Registry allow lists and access policies](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-mcp-usage/configure-mcp-server-access), project `.mcp.json` |

## What you gain

Cross-tool portability. Build the [MCP server](../standards/mcp-protocol.md) once and it works with every MCP-compatible agent: Copilot, Claude Code, Cursor, and others.

No mandatory hosting for local tools. Copilot Extensions always ran remotely. With MCP, stdio transport runs the server as a local process and needs no infrastructure. Remote tools still need hosting.

Autonomous invocation. Copilot's agent mode and coding agent call MCP tools without a user `@mention`. The agent discovers available tools at startup through [`tools/list`](https://raw.githubusercontent.com/modelcontextprotocol/specification/main/schema/2024-11-05/schema.ts) and calls them as it works.

Open registry. The [GitHub MCP Registry](https://github.blog/ai-and-ml/generative-ai/how-to-find-install-and-manage-mcp-servers-with-the-github-mcp-registry/) (github.com/mcp) offers [one-click VS Code installation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers), namespace conventions, and enterprise allow lists. The same registry serves all MCP clients.

## What you lose

Skillset abstraction. [Skillsets](../tools/copilot/copilot-extensions.md) handled all AI logic: routing, prompt crafting, and response generation, with no LLM code required. MCP servers expose raw tools, and orchestration becomes the host agent's job.

Marketplace distribution. No single marketplace equivalent exists yet. You distribute MCP servers yourself or list them in a registry.

## The broader pattern

The Copilot Extensions deprecation shows a recurring pattern: proprietary extension systems converge on open protocols once a protocol reaches wide adoption.

The sequence is predictable:

1. A vendor ships a proprietary plugin system to capture early value.
2. Competing vendors ship incompatible systems, so you maintain many integrations.
3. An open protocol emerges with broad vendor support.
4. Early-mover vendors deprecate their proprietary system and adopt the standard.
5. If you built on the open protocol, you get cross-tool reach for free.

```mermaid
graph TD
    A[Proprietary extension system] -->|protocol reaches critical mass| B[Open standard adopted]
    B -->|same server binary| C[Build once]
    C -->|deploy to| D[Copilot]
    C -->|deploy to| E[Claude Code]
    C -->|deploy to| F[Cursor]
    C -->|deploy to| G[Any MCP client]
```

MCP follows the same path as USB-C (connector standards), LSP (language server protocol for editors), and OAuth (auth delegation). Once enough agents support MCP, the economics flip: maintaining Copilot-only tooling costs more than maintaining one MCP server.

## Migration approach

For existing Copilot Extensions:

1. Identify each tool or skill endpoint in the extension.
2. Implement each one as an MCP `tool` with the same input and output schema.
3. Choose a transport: stdio for local tools, Streamable HTTP for remote ones.
4. Configure each client: `claude mcp add` for Claude Code, `.vscode/mcp.json` for Copilot, and native MCP settings for Cursor.
5. Remove the `@mention` documentation, since agents call MCP tools on their own.

For new integrations:

Build MCP servers from the start. Do not build Copilot Extensions, since the system is deprecated and no longer works.

## Example

A Copilot Extension that queries a deployment status API moves to an MCP server that exposes the same capability as a tool.

Before, with a Copilot Extension skillset definition in a GitHub App manifest:

```yaml
# github-app/skillset.yml (no longer functional)
skills:
  - name: get-deploy-status
    description: Returns the current deployment status for a service
    parameters:
      service_name:
        type: string
        required: true
```

The extension ran on a remote server, handled Copilot's callback protocol, and you invoked it with `@deploy-bot get-deploy-status payments`.

After, the MCP server (Python, stdio transport):

```python
# deploy_status_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("deploy-status")

@mcp.tool()
def get_deploy_status(service_name: str) -> str:
    """Returns the current deployment status for a service."""
    # Same logic as the old extension endpoint
    status = query_deploy_api(service_name)
    return f"{service_name}: {status.state} (deployed {status.timestamp})"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Client configuration:

```json
// .vscode/mcp.json (Copilot)
{
  "servers": {
    "deploy-status": {
      "command": "python",
      "args": ["deploy_status_server.py"]
    }
  }
}
```

```bash
# Claude Code
claude mcp add deploy-status -- python deploy_status_server.py
```

The same server binary works across Copilot, Claude Code, and Cursor with no code changes. Only the client config differs.

## Key Takeaways

- Copilot Extensions are fully deprecated as of November 10, 2025 — build MCP servers instead
- MCP's core value is cross-tool portability: one server, every MCP-compatible agent
- Skillsets had no equivalent in MCP — tool orchestration is the host agent's responsibility
- When an open standard reaches critical adoption mass, proprietary extension systems deprecate; build on the standard early

## Related

- [MCP Protocol](../standards/mcp-protocol.md)
- [Copilot MCP Integration](../tools/copilot/mcp-integration.md)
- [Copilot Extensions (deprecated)](../tools/copilot/copilot-extensions.md)
- [MCP Client Design](mcp-client-design.md)
- [MCP Client/Server Architecture](mcp-client-server-architecture.md)
- [MCP Server Design](mcp-server-design.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Plugin and Extension Packaging](../standards/plugin-packaging.md)
