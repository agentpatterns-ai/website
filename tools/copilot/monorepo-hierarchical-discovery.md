---
title: "Monorepo Skill and Agent Discovery: Hierarchical Configuration"
description: "GitHub Copilot CLI v1.0.11 discovers instructions, MCP servers, skills, and agents from the working directory up to the git root — enabling per-package configuration in monorepos."
tags:
  - copilot
  - agent-design
  - workflows
aliases:
  - monorepo agent discovery
  - hierarchical skill discovery
---

# Monorepo Skill and Agent Discovery: Hierarchical Configuration

> Copilot CLI v1.0.11 discovers custom instructions, MCP servers, skills, and agents at every directory level from the working directory up to the git root, enabling per-package configuration in monorepos.

## How Discovery Works

When you start a session in a working directory, Copilot CLI walks the directory tree from your current working directory up to the git root, collecting configuration at each level ([v1.0.11 release notes](https://github.com/github/copilot-cli/releases/tag/v1.0.11)). Lower directories take precedence over parent directories — package-level configuration overrides root-level defaults.

Four artifact types participate in discovery:

| Artifact | Purpose |
|---|---|
| Custom instructions | Behavioral rules and coding conventions |
| Skills (`SKILL.md`) | Slash commands with specialized prompts and scripts |
| Agents (`.github/agents/*.md`) | Specialized agents with their own tools and MCP servers (root-only — see note below) |
| MCP servers (`.mcp.json`) | External tool connections |

A fifth scope applies to personal skills: the Copilot CLI also loads skills from `~/.copilot/skills/`, `~/.claude/skills/`, and `~/.agents/skills/` in the user's home directory, enabling developer-specific skills that are not checked into any repository ([GitHub Docs: Creating agent skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills)).

Agents are the current exception. As of April 2026, only the git root's `.github/agents/` is scanned; agents defined in a subdirectory are invisible to `/agent` ([copilot-cli issue #1859](https://github.com/github/copilot-cli/issues/1859), open). Instructions, skills, and MCP servers traverse the full hierarchy; keep agent definitions at the repo root until this gap closes.

## Monorepo Layout

In a monorepo with a frontend package and a backend service, each can carry its own configuration:

```
my-monorepo/
├── .github/
│   └── copilot-instructions.md     # shared repo-wide instructions
├── .mcp.json                        # shared MCP servers (e.g., GitHub)
├── frontend/
│   ├── .github/
│   │   └── copilot-instructions.md # frontend-specific conventions
│   ├── .mcp.json                   # Figma, Storybook MCP servers
│   └── .github/skills/
│       └── component/SKILL.md      # /component skill for React work
└── backend/
    ├── .github/
    │   └── copilot-instructions.md # backend-specific conventions
    ├── .mcp.json                   # database, observability MCP servers
    └── .github/skills/
        └── migration/SKILL.md      # /migration skill for DB work
```

Running `copilot` from `frontend/` loads the root and `frontend/` instructions, both MCP server sets, and `/component` — but not `/migration` or the backend MCP servers. Working in `backend/` produces the inverse.

## Override Direction

Package-level configuration takes precedence over root-level. MCP servers use last-wins: when both levels define the same server name, the package-level definition overrides the root-level one ([GitHub Docs: Adding MCP servers for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)).

This mirrors the precedence model in [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md), where more specific scopes override less specific ones. The difference: Copilot CLI handles the traversal automatically — no harness configuration required.

## Session Working Directory

The `/cd` (or `/cwd`) command changes the working directory within an active session ([GitHub Copilot CLI slash commands](https://github.blog/ai-and-ml/github-copilot/a-cheat-sheet-to-slash-commands-in-github-copilot-cli/)), letting a single session move across packages instead of starting a new process per location. If reloaded configuration does not appear to take effect after `/cd`, run `/clear` to reset session state.

## When to Structure for Discovery

Discovery adds value when packages in your monorepo have genuinely different:

- **Tool contexts**: frontend work benefits from design-system MCP servers; backend work benefits from database or infrastructure MCP servers
- **Skill sets**: different slash commands are relevant per domain
- **Coding conventions**: language versions, testing frameworks, or style rules diverge by package

For monorepos with uniform conventions, root-level configuration is sufficient. Avoid duplicating identical config at multiple levels — maintenance overhead without benefit.

## When This Backfires

Hierarchical configuration is worse than root-only configuration when:

- **Packages drift silently.** Per-package instructions let each subtree encode its own conventions. Without a review cadence that diffs package-level config against root defaults, drift accumulates and a developer moving between packages gets conflicting guidance.
- **Debugging becomes path-sensitive.** When agent behavior depends on the current working directory, reproducing a reported issue requires knowing exactly where the session was started. "It worked from the repo root but not from `packages/api/`" is a failure mode that root-only config does not produce.
- **Precedence confusion.** Last-wins override across four artifact types (instructions, skills, agents, MCP servers) multiplied by multiple directory levels makes it non-obvious which configuration is active. A small monorepo can expose this without real benefit.
- **Onboarding cost.** New contributors must learn both the hierarchical discovery model and the per-package layout. If packages share most of their agent surface, centralizing at the root reduces the number of places to look.

If your packages mostly share conventions, prefer root-level config and introduce per-package overrides only for directories with genuinely different tool contexts.

## Relationship to Cross-Repo Distribution

Hierarchical discovery solves the per-package problem within a single repo. For sharing standards across multiple repositories, see [Architecting a Central Repo for Shared Agent Standards](../../workflows/central-repo-shared-agent-standards.md). The two approaches are complementary: distribute shared conventions from a central repo, then override with per-package configuration using hierarchical discovery.

## Key Takeaways

- Copilot CLI v1.0.11 discovers instructions, MCP servers, skills, and agents at every directory level from CWD to git root
- Lower directories take precedence; root-level config provides shared defaults
- `~/.agents/skills/` provides a personal discovery scope outside any repository
- Discovery is automatic — no harness configuration needed; package placement determines what the agent loads
- Use hierarchical discovery when packages need different MCP servers, skills, or conventions; use root-level config when conventions are uniform

## Related

- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [MCP Integration](mcp-integration.md)
- [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md)
- [Architecting a Central Repo for Shared Agent Standards](../../workflows/central-repo-shared-agent-standards.md)
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md)
