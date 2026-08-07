---
title: "Plugin and Extension Packaging: Distributing Agent Capabilities"
description: "Package agents, skills, MCP servers, and hooks into installable bundles — plugins solve the distribution problem for agent capabilities."
tags:
  - agent-design
  - tool-agnostic
  - standards
last_reviewed: 2026-06-13
maturity: adopted
---

# Plugin and Extension Packaging: Distributing Agent Capabilities

> Package agents, skills, MCP servers, and hooks into installable bundles — plugins solve the distribution problem for agent capabilities beyond the single project.

## The distribution problem

Useful agent configurations — research agents, writing skills, internal-API MCP servers, convention-enforcing hooks — otherwise live in one repo, and you have to copy them by hand to every consumer. Plugin packaging bundles them into a versioned, installable unit.

## Why git-based plugins

Plugin packaging reduces distribution to a single git reference. The alternatives all trade something away:

- Git submodules require consumers to initialize and update nested repos, and they do not bundle different component types behind one install command.
- Package registries (npm, PyPI) demand accounts, publish workflows, and language-specific runtimes — too much for config files and shell scripts.
- Shared config repos with custom sync scripts reinvent version pinning, partial updates, and rollback, and they do it worse than git tags — the same versioned-artifact problem that [portable agent definitions](portable-agent-definitions.md) solve with git primitives.

A git repo plus a manifest gives one source of truth per tag, atomic install from one reference, and tooling every developer already has. Updating is `git pull`; pinning is a tag; auditing is `git log`.

## What a plugin contains

A plugin bundles any combination of:

- Agents — agent definition files (`.claude/agents/`)
- Skills — task knowledge files (`.claude/skills/` or `.github/skills/`)
- MCP servers — tool server definitions
- Hooks — lifecycle event handlers
- Commands — workflow definitions

Claude Code plugins are git repositories with a manifest ([Claude Code plugins documentation](https://code.claude.com/docs/en/plugins)). Installing by URL adds the plugin's agents, skills, MCP servers, and hooks. Current docs list 10 root-level plugin directories and files in total, including newer additions such as LSP servers (`.lsp.json`) and background monitors (`monitors/`) alongside the five component types above.

## Distribution levels

| Level | Scope | Mechanism |
|-------|-------|-----------|
| Project | One repo | Committed files in `.claude/` or `.github/` |
| User | One developer, all projects | `~/.claude/` or user-level plugin install |
| Organization | All team members | Managed settings push plugins to all users |
| Community | Public distribution | Git URL, plugin marketplace |

Organization-managed distribution matters for enterprise: a security team can push compliance-enforcing hooks to every installation without per-developer install steps.

## The marketplace model

The [github/awesome-copilot repository](https://github.com/github/awesome-copilot) shows community-scale distribution: curated agents, skills, and instructions that teams install by URL. The [Agent Skills standard](agent-skills-standard.md) lets you distribute skills across tools — a skill written to the standard works in Claude Code, GitHub Copilot, and Cursor ([VS Code Agent Skills docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code skills docs](https://code.claude.com/docs/en/skills)).

An agent can discover plugins from a site's [llms.txt file](../geo/llms-txt.md) and recommend them.

## Security model

Plugins run code on your machine. MCP servers execute as processes; hooks execute shell scripts; agents may have broad tool access. Trust considerations:

- Install only from trusted authors or audited community sources
- Inspect MCP server code and hooks before running them
- Apply least privilege — tool restrictions in frontmatter limit blast radius
- Have your security review vet organization-managed plugins

Recent disclosures sharpen the threat model: PromptArmor demonstrated [marketplace-plugin injection attacks](https://www.promptarmor.com/resources/hijacking-claude-code-via-injected-marketplace-plugins) that hijack Claude Code sessions, and the third-party registry PromptArmor targeted rescans GitHub for new marketplaces every hour, so a malicious listing can become installable within about 60 minutes of being pushed. SentinelOne separately documented [marketplace skills that redirect dependency installs to attacker-controlled sources](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/). Treat community plugins as third-party tooling — pin versions and prefer private or organization-managed marketplaces for anything with access to secrets.

## Versioning and lifecycle

Because plugins are git repositories, versioning uses git primitives: tags for releases, branches for development. Installing at a tag pins the version; updating pulls the new tag. For organization-managed plugins, the org controls the version deployed to all members, so teams cannot ship a breaking update by accident.

## When this backfires

Plugin packaging adds overhead that may not be justified in every context:

- Air-gapped environments: organizations that restrict outbound network access block marketplace installs, so committed `.claude/` files are the only viable path.
- Small, stable teams: for one or two people on a single project, plugin overhead (manifest, versioning, marketplace registration) outweighs the benefit over a committed `.claude/` directory.
- Fragile cross-tool support: cross-tool portability depends on each tool implementing the standard the same way, and a skill that works in Claude Code may need adjustments elsewhere.
- Version-management burden: pinning by tag prevents unintended updates, but it forces teams to track and apply version bumps rather than inheriting improvements automatically.

## Anti-pattern: copy-paste distribution

Copying agent definition files between repos by hand creates version fragmentation: each repo carries a slightly different version, updates do not propagate, and no central source of truth exists. Plugin packaging — even a shared git repo — removes this problem.

## Example

This minimal Claude Code plugin layout packages a research agent, a Playwright MCP server, and a pre-tool hook into a single installable unit.

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

- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [Agent Plugins: Portable Packaging With Client-Defined Trust](agent-plugins-standard.md) — the vendor-neutral layout for the skills and MCP half of a bundle
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
- [Cross-IDE Plugin Discovery](cross-ide-plugin-discovery.md) — discovery model for plugins across IDEs
- [Pre-Install Plugin Transparency](pre-install-plugin-transparency.md) — capability inventory before install
- [Plugin Dependency Declaration](plugin-dependency-declaration.md) — manifest-level plugin dependency hints
- [Pre-Install Context-Cost Projection](marketplace-cost-projection.md) — marketplace cost forecasting before install
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [AGENTS.md: Project-Level README for AI Coding Agents](agents-md.md)
