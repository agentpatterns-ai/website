---
title: "Plugin and Extension Packaging: Agent Capabilities"
description: "Package agents, skills, MCP servers, and hooks into installable bundles — plugins solve the distribution problem for agent capabilities."
tags:
  - agent-design
  - tool-agnostic
---

# Plugin and Extension Packaging: Distributing Agent Capabilities

> Package agents, skills, MCP servers, and hooks into installable bundles — plugins solve the distribution problem for agent capabilities beyond the single project.

## The Distribution Problem

You build useful agent configurations: a custom research agent, a set of writing skills, an MCP server for an internal API, hooks that enforce team conventions. Without packaging, these live in one repo and require manual copying to every other project that needs them.

Plugin packaging solves the distribution problem: bundle capabilities into a versioned, installable unit that travels to wherever it is needed.

## What a Plugin Contains

A plugin bundles any combination of:

- **Agents** — agent definition files (`.claude/agents/`)
- **Skills** — task knowledge files (`.claude/skills/` or `.github/skills/`)
- **MCP servers** — tool server definitions
- **Hooks** — lifecycle event handlers
- **Commands** — workflow definitions

Claude Code plugins ([docs](https://code.claude.com/docs/en/plugins)) are git repositories with a manifest. Installing a plugin by URL adds its agents, skills, MCP servers, and hooks to the installation.

## Distribution Levels

| Level | Scope | Mechanism |
|-------|-------|-----------|
| Project | One repo | Committed files in `.claude/` or `.github/` |
| User | One developer, all projects | `~/.claude/` or user-level plugin install |
| Organization | All team members | Managed settings push plugins to all users |
| Community | Public distribution | Git URL, plugin marketplace |

Organization-managed distribution is significant for enterprise use: a security team can push hooks that enforce compliance rules to every Claude Code installation, without requiring you to install them manually.

## The Marketplace Model

The [github/awesome-copilot](https://github.com/github/awesome-copilot) repository demonstrates community-scale distribution: curated agents, skills, and instructions that teams install by URL. The [Agent Skills standard](https://agentskills.io) enables skills to be distributed across tools — a skill written to the standard installs in Claude Code, GitHub Copilot, and Cursor.

Plugin discovery via [llms.txt](../geo/llms-txt.md) enables machine-readable indexing: an agent can discover available plugins from a site's `llms.txt` and recommend relevant ones for a project's needs.

## Security Model

Plugins run code on your machine. MCP servers execute as processes; hooks execute shell scripts; agents may have broad tool access if the plugin grants it. Trust model considerations:

- Source matters: install plugins from trusted authors or audited community sources
- Review before installing: inspect MCP server code and hooks before running them
- Scope restrictions: the plugin's agents should follow least-privilege — tool restrictions in frontmatter limit blast radius
- Organization-managed plugins are vetted by your organization's security review

The convenience of community plugins comes with the same risks as installing any third-party tooling.

## Versioning and Lifecycle

Plugins are git repositories, so versioning uses git primitives: tags for releases, branches for development versions. Installing a plugin at a specific tag pins the version. Updating means pulling the new tag.

For organization-managed plugins, the org controls the version deployed to all members — teams cannot inadvertently update to a breaking version without the org's review.

## Anti-Pattern: Copy-Paste Distribution

Copying agent definition files between repos manually creates version fragmentation: each repo has a slightly different version, updates to one do not propagate, and there is no central source of truth. Plugin packaging — even at the simple level of a shared git repo — eliminates this class of problem.

## Example

The following shows a minimal Claude Code plugin repository layout that packages a research agent, a Playwright MCP server, and a pre-tool hook into a single installable unit.

```
my-research-plugin/
├── manifest.json
├── .claude/
│   ├── agents/
│   │   └── researcher.md          # Agent definition with frontmatter
│   └── hooks/
│       └── pre-tool-validate.sh   # Hook that blocks dangerous commands
└── mcp-servers/
    └── playwright.json            # MCP server definition
```

The `manifest.json` declares the plugin's contents:

```json
{
  "name": "my-research-plugin",
  "version": "1.2.0",
  "description": "Research agent with browser access and safety hooks",
  "agents": [".claude/agents/researcher.md"],
  "hooks": [".claude/hooks/pre-tool-validate.sh"],
  "mcpServers": ["mcp-servers/playwright.json"]
}
```

Installing the plugin by URL adds all three components to the target project:

```bash
claude plugin install https://github.com/example-org/my-research-plugin@v1.2.0
```

Pinning to a tag (`@v1.2.0`) means the project stays on a known-good version until explicitly updated. An organization can push this plugin to all members via managed settings, so the safety hook is enforced team-wide without per-developer installs.

## Key Takeaways

- Plugins bundle agents, skills, MCP servers, and hooks into installable versioned units
- Distribution levels: project (committed), user (local), org (managed), community (marketplace)
- Organization-managed distribution pushes plugins to all members without manual install
- Plugins run code on your machine — apply the same trust evaluation as any third-party tooling
- Versioning is git-native: pin by tag, update by pulling new version

## Related

- [Agent Definition Formats](agent-definition-formats.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [AGENTS.md: Project-Level README for AI Coding Agents](agents-md.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
- [A2A Protocol: Agent-to-Agent Communication Standard](a2a-protocol.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
