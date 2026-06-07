---
title: "Scoped MCP Server Discovery: Most-Specific-Wins Resolution"
description: "Resolve MCP servers across user, workspace, and project config files using a most-specific-wins precedence rule to avoid duplicate tools and shadowed routing."
aliases:
  - layered MCP configuration
  - MCP scope precedence
tags:
  - tool-engineering
  - tool-agnostic
  - mcp
last_reviewed: 2026-06-03
---

# Scoped MCP Server Discovery: Most-Specific-Wins Resolution

> Across user, workspace, and project MCP configs, the most-specific scope defining a server name wins, and duplicate definitions are suppressed before the agent sees them.

## The Three Scopes

MCP server definitions can live at three places. Each scope answers a different question — "what do I always want available?" "what does this team agree on?" "what stays personal to this checkout?"

| Scope | Claude Code | VS Code | Use for |
|-------|-------------|---------|---------|
| **User** | `~/.claude.json` | `mcp.json` in the user profile folder | Personal utilities used across every project |
| **Workspace** | `.mcp.json` at the project root | `.vscode/mcp.json`, plus workspace-level `.mcp.json` since 1.118 | Team-shared servers checked into version control |
| **Local** | `~/.claude.json`, scoped to the project path | (not exposed) | Personal experiments and credentials you do not want in VCS |

VS Code 1.118 (April 29 2026) added workspace-level `.mcp.json` "aligning with other tools such as the Copilot CLI" ([VS Code 1.118 release notes](https://code.visualstudio.com/updates/v1_118)); the file paths for Claude Code and VS Code workspace/user scopes come from the [Claude Code MCP docs](https://code.claude.com/docs/en/mcp) and [VS Code MCP servers docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers). Cursor follows the same shape with `.cursor/mcp.json` (project) and `~/.cursor/mcp.json` (global) ([Cursor MCP docs](https://cursor.com/docs/context/mcp)).

## Most-Specific-Wins

When the same server name appears at multiple scopes, the host picks one. Claude Code documents the precedence explicitly: "When the same server is defined in more than one place, Claude Code connects to it once, using the definition from the highest-precedence source: 1. Local scope 2. Project scope 3. User scope 4. Plugin-provided servers 5. claude.ai connectors" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)). The three file-based scopes match by name; plugins and connectors match by endpoint.

VS Code 1.118 applies the same rule: "By default, only the most-specific MCP server will be enabled, and enabling a server will disable other servers by the same name" ([VS Code 1.118 release notes](https://code.visualstudio.com/updates/v1_118)).

## Why Dedup Matters

MCP defines no collision resolution at the protocol level — the host decides. Loading two servers under the same name forces either namespace prefixing (extra tokens in every tool description) or arbitrary selection (action-at-a-distance routing). Most-specific-wins resolves the collision deterministically before the tool list reaches the model. This matters because tool-search accuracy degrades as the visible toolset grows ([Anthropic: advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).

## Operational Discipline

Three habits keep layered configs debuggable:

- **Inspect the effective config**, not the source files. In Claude Code, `/mcp` lists what is loaded after dedup; in VS Code, search `@mcp @installed` in the extensions view ([VS Code 1.118 release notes](https://code.visualstudio.com/updates/v1_118)).
- **Approve project-scope servers explicitly.** Claude Code prompts before activating servers from a project `.mcp.json`; reset choices with `claude mcp reset-project-choices` ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)).
- **Rename when intent differs.** If a developer's `github` server points at a private fork and the team's `github` server points at the public registry, the dedup rule silently disables one. Rename one of them — layering is for overrides, not for parallel intents.

## When This Backfires

Most-specific-wins is the right default, but the same silent determinism that prevents duplicates can hide problems. Treat these as failure conditions, not edge cases:

- **Different intents collide under one name.** When a developer's `github` server points at a private fork and the team's `github` points at the public registry, the dedup rule disables one with no error — the agent silently routes to whichever scope won. Shadowing is for overrides of the *same* intent; parallel intents need distinct names.
- **The winning scope is invisible at the call site.** Because resolution happens before the tool list reaches the model, a tool that misbehaves gives no hint that a different-scope definition shadowed the one you were reading. Debugging starts from the wrong file unless you inspect the effective config first.
- **Local scope outlives its usefulness.** A local-scope override added for a one-off experiment persists in `~/.claude.json` and keeps shadowing the team default indefinitely. Nothing prompts you to retire it, so a stale personal entry can mask an updated project server for weeks.

In each case the alternative — explicit per-scope naming, or surfacing every loaded server without dedup — trades token cost and a longer tool list for transparency. Prefer most-specific-wins when scopes genuinely override the same server, and reach for distinct names the moment two definitions mean different things.

## Example

A team ships a Postgres MCP server in their repo's `.mcp.json` (project scope). A developer wants a local variant pointing at a staging database without breaking the team default:

**Project `.mcp.json`** — checked into version control:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "args": ["--url", "${env:DATABASE_URL}"]
    }
  }
}
```

**Local override** — added with `claude mcp add postgres --scope local`:

```bash
claude mcp add postgres --scope local -- mcp-server-postgres --url postgresql://localhost:5432/staging
```

Claude Code stores the local entry under the developer's home `.claude.json` and prefers it for this project. The team default still loads in everyone else's checkouts. Running `/mcp` in the developer's session shows one `postgres` server — the local one — confirming the project-scope entry was correctly shadowed.

## Key Takeaways

- Three canonical scopes (user, workspace/project, local) carry distinct intents — personal utilities, team agreement, private overrides
- Most-specific-wins is the dedup rule: the closest scope defining a name disables matches at outer scopes
- Inspect the effective config (`/mcp`, `@mcp @installed`), not the source files, when debugging shadowed entries
- Rename rather than rely on shadowing when servers at different scopes have different intents

## Related

- [MCP Client Design: Building Robust Host-Side Logic](mcp-client-design.md)
- [MCP Server Design: A Server Author's Checklist](mcp-server-design.md)
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](mcp-eager-vs-jit-loading.md)
- [Monorepo Hierarchical Discovery](../tools/copilot/monorepo-hierarchical-discovery.md)
- [Extension Points: Discovery Surfaces in Claude Code](../tools/claude/extension-points.md)
