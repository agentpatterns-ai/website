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

Useful agent configurations — a research agent, a set of writing skills, an MCP server for an internal API, hooks that enforce team conventions — otherwise live in one repo and require manual copying to every project that needs them. Plugin packaging bundles them into a versioned, installable unit.

## Why Git-Based Plugins

Plugin packaging works by collapsing the distribution surface to a single git reference. Alternatives trade off on different axes:

- **Git submodules** require consumers to initialize and update nested repos and do not bundle heterogeneous components behind one install verb.
- **Package registries** (npm, PyPI) demand accounts, publish workflows, and language-specific runtimes — overkill for config files and shell scripts.
- **Shared config repos** with custom sync scripts reinvent version pinning, partial updates, and rollback poorly compared to git tags.

A git repository plus a manifest gives one source of truth per tag, atomic install from one reference, and tooling every developer already has. Updating a plugin is a git pull; pinning is a tag; auditing is a git log.

## What a Plugin Contains

A plugin bundles any combination of:

- **Agents** — agent definition files (`.claude/agents/`)
- **Skills** — task knowledge files (`.claude/skills/` or `.github/skills/`)
- **MCP servers** — tool server definitions
- **Hooks** — lifecycle event handlers
- **Commands** — workflow definitions

Claude Code plugins ([docs](https://code.claude.com/docs/en/plugins)) are git repositories with a manifest; installing by URL adds the plugin's agents, skills, MCP servers, and hooks.

## Distribution Levels

| Level | Scope | Mechanism |
|-------|-------|-----------|
| Project | One repo | Committed files in `.claude/` or `.github/` |
| User | One developer, all projects | `~/.claude/` or user-level plugin install |
| Organization | All team members | Managed settings push plugins to all users |
| Community | Public distribution | Git URL, plugin marketplace |

Organization-managed distribution matters for enterprise: a security team can push compliance-enforcing hooks to every installation without per-developer install steps.

## The Marketplace Model

The [github/awesome-copilot](https://github.com/github/awesome-copilot) repository demonstrates community-scale distribution: curated agents, skills, and instructions that teams install by URL. The [Agent Skills standard](agent-skills-standard.md) enables skills to be distributed across tools — a skill written to the standard works in Claude Code, GitHub Copilot, and Cursor ([VS Code Agent Skills docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code skills docs](https://code.claude.com/docs/en/skills)).

Plugin discovery via [llms.txt](../geo/llms-txt.md) enables machine-readable indexing: an agent can discover plugins from a site's `llms.txt` and recommend them.

## Security Model

Plugins run code on your machine. MCP servers execute as processes; hooks execute shell scripts; agents may have broad tool access. Trust considerations:

- Install only from trusted authors or audited community sources
- Inspect MCP server code and hooks before running them
- Apply least-privilege — tool restrictions in frontmatter limit blast radius
- Organization-managed plugins are vetted by your security review

Recent disclosures sharpen the threat model: PromptArmor demonstrated [marketplace-plugin injection attacks](https://www.promptarmor.com/resources/hijacking-claude-code-via-injected-marketplace-plugins) that hijack Claude Code sessions, and SentinelOne documented [marketplace skills that redirect dependency installs to attacker-controlled sources](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/). Treat community plugins as third-party tooling — pin versions and prefer private or organization-managed marketplaces for anything with access to secrets.

## Versioning and Lifecycle

Because plugins are git repositories, versioning uses git primitives: tags for releases, branches for development. Installing at a tag pins the version; updating pulls the new tag. For organization-managed plugins, the org controls the version deployed to all members — teams cannot inadvertently ship a breaking update.

## When This Backfires

Plugin packaging adds overhead that may not be justified in every context:

- **Air-gapped environments**: Organizations that restrict outbound network access block marketplace installs; committed `.claude/` files are the only viable path.
- **Small, stable teams**: For one or two people on a single project, plugin overhead (manifest, versioning, marketplace registration) outweighs the benefit over a committed `.claude/` directory.
- **Ecosystem fragility**: Cross-tool portability depends on each tool implementing the standard consistently; a skill that works in Claude Code may need adjustments elsewhere.
- **Version management burden**: Pinning by tag prevents unintended updates but forces teams to explicitly track and apply version bumps rather than inheriting improvements automatically.

## Anti-Pattern: Copy-Paste Distribution

Manually copying agent definition files between repos creates version fragmentation: each repo carries a slightly different version, updates do not propagate, and no central source of truth exists. Plugin packaging — even a shared git repo — eliminates this problem.

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

- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Agent Definition Formats](agent-definition-formats.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [AGENTS.md: Project-Level README for AI Coding Agents](agents-md.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
- [A2A Protocol: Agent-to-Agent Communication Standard](a2a-protocol.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
