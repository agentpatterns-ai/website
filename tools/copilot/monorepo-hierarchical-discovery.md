---
title: "Monorepo Skill and Agent Discovery: Hierarchical Configuration"
description: "GitHub Copilot CLI v1.0.12 discovers instructions, MCP servers, skills, and agents from the working directory up to the git root — enabling per-package configuration in monorepos."
tags:
  - copilot
  - agent-design
  - workflows
aliases:
  - monorepo agent discovery
  - hierarchical skill discovery
---

# Monorepo Skill and Agent Discovery: Hierarchical Configuration

> Copilot CLI v1.0.12 discovers custom instructions, MCP servers, skills, and agents at every directory level from the working directory up to the git root, enabling per-package configuration in monorepos.

## How Discovery Works

When you start a session in a working directory, Copilot CLI walks the directory tree from your current working directory up to the git root, collecting configuration at each level ([v1.0.12 release notes](https://github.com/github/copilot-cli/releases/tag/v1.0.12)). Lower directories take precedence over parent directories — package-level configuration overrides root-level defaults.

Four artifact types participate in discovery:

| Artifact | Purpose |
|---|---|
| Custom instructions | Behavioral rules and coding conventions |
| Skills (`SKILL.md`) | Slash commands with specialized prompts and scripts |
| Agents (`.github/agents/*.md`) | Specialized agents with their own tools and MCP servers |
| MCP servers (`.mcp.json`) | External tool connections |

A fifth scope applies to personal skills: `~/.agents/skills/` is loaded as a personal discovery directory, enabling developer-specific skills that are not checked into any repository [unverified whether this applies outside the VS Code extension].

## Monorepo Layout

In a monorepo with a frontend package and a backend service, each package can carry its own configuration:

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

When you run `copilot` from `frontend/`, the agent loads the root instructions plus `frontend/`-level instructions, the root MCP server plus the Figma/Storybook MCP servers, and the `/component` skill — but not the `/migration` skill or backend MCP servers. Working in `backend/` produces the inverse.

## Override Direction

Package-level configuration takes precedence over root-level configuration. When both levels define the same MCP server name [unverified — merge vs. override behavior is not specified in release notes], the package-level definition wins. Root-level config provides shared defaults; package-level config specializes for context.

This mirrors the precedence model in [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md), where more specific scopes override less specific ones. The difference here is that Copilot CLI handles the traversal automatically — no harness configuration required.

## Session Working Directory

The `/cd` command changes the working directory within an active session. When you `/cd` into a different package, Copilot re-evaluates which configuration applies to the new path [unverified whether re-discovery is immediate or requires `/clear`]. This allows a single session to work across packages with appropriate context at each location.

## When to Structure for Discovery

Discovery adds value when packages in your monorepo have genuinely different:

- **Tool contexts**: frontend work benefits from design-system MCP servers; backend work benefits from database or infrastructure MCP servers
- **Skill sets**: different slash commands are relevant per domain
- **Coding conventions**: language versions, testing frameworks, or style rules diverge by package

For monorepos with uniform conventions across all packages, root-level configuration is sufficient. Avoid duplicating identical configuration at multiple levels — that creates maintenance overhead without benefit.

## Relationship to Cross-Repo Distribution

Hierarchical discovery solves the per-package problem within a single repo. For sharing standards across multiple repositories, see [Architecting a Central Repo for Shared Agent Standards](../../workflows/central-repo-shared-agent-standards.md). The two approaches are complementary: distribute shared conventions from a central repo, then override with per-package configuration using hierarchical discovery.

## Key Takeaways

- Copilot CLI v1.0.12 discovers instructions, MCP servers, skills, and agents at every directory level from CWD to git root
- Lower directories take precedence; root-level config provides shared defaults
- `~/.agents/skills/` provides a personal discovery scope outside any repository
- Discovery is automatic — no harness configuration needed; package placement determines what the agent loads
- Use hierarchical discovery when packages need different MCP servers, skills, or conventions; use root-level config when conventions are uniform

## Unverified

- `~/.agents/skills/` as a personal discovery directory may apply only to the VS Code extension, not all Copilot surfaces
- Merge vs. override behavior when the same MCP server name appears at multiple levels
- Whether `/cd` triggers immediate re-discovery or requires `/clear` to reload configuration

## Related

- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [MCP Integration](mcp-integration.md)
- [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md)
- [Architecting a Central Repo for Shared Agent Standards](../../workflows/central-repo-shared-agent-standards.md)
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md)
