---
title: "GitHub Copilot: Building Custom Agents, Skills & Plugins"
description: "GitHub Copilot custom agents, skills, and plugins let teams codify workflows, teach Copilot specialized tasks, and share capabilities as installable packages."
tags:
  - agent-design
  - instructions
  - copilot
---

# GitHub Copilot: Custom Agents, Skills & Plugins

> Custom agents, skills, and plugins are GitHub Copilot's three extensibility layers — agents codify team workflows, skills teach Copilot specialized tasks via progressive disclosure, and plugins bundle everything into shareable packages.

## Custom Agents

Define [`CUSTOM-AGENT-NAME.md` files](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents) under `.github/agents/` to create specialized agents with their own tools, MCP servers, and instructions. Agents become available in the [coding agent on GitHub.com, coding agent in IDEs, and GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents).

## Agent Skills

[Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) are `SKILL.md` folders containing instructions, scripts, and resources. Copilot auto-loads them when relevant using progressive disclosure — it reads skill metadata first, then loads actual scripts and templates only when needed to avoid context window bloat.

Skills [surface as slash commands](https://code.visualstudio.com/docs/copilot/customization/agent-skills) in chat. Available across Copilot coding agent, CLI, and VS Code.

The [Agent Skills specification](https://agentskills.io) defines the open standard. The [microsoft/skills](https://github.com/microsoft/skills) repository provides Azure SDK-specific skills and plugin packages.

## Prompt Files

Stored in `.github/prompts/`, [prompt files](../../instructions/prompt-file-libraries.md) define specialized prompts invocable via `/` commands. They support YAML frontmatter to specify which model to use and are source-controlled for team sharing.

## Plugins

[Plugins](https://github.com/microsoft/skills) bundle MCP servers, agents, skills, and hooks into installable packages. Install from GitHub repos with `npx skills add owner/repo`. Plugins extend Copilot's capabilities — skills from plugins appear alongside local skills.

**Plugin marketplace management** (v1.113+): The command "Chat: Manage Plugin Marketplaces" lists configured marketplaces with options to browse, locate directories, and remove plugins. URL handler installation is available via `vscode://chat-plugin/install?source=<source>`.

## Custom Instructions

- **Repository instructions**: `copilot-instructions.md` in `.github/` applies to all requests in that repo
- **Path-specific instructions**: `NAME.instructions.md` in `.github/instructions/` applies only to matching file paths
- **AGENTS.md**: Auto-detected in workspace root; supports subfolder-level instructions

See [custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) in the GitHub docs.

## Example

The following shows a minimal custom agent definition file and a companion skill, demonstrating how the two layers work together. The agent lives at `.github/agents/release-engineer.md` and declares which tools and MCP servers it may use; the skill lives at `.github/skills/changelog/SKILL.md` and is auto-loaded by Copilot when the task is relevant.

**`.github/agents/release-engineer.md`**

```markdown
---
name: release-engineer
description: Automates release tasks — changelog generation, version bumping, and tag creation.
tools:
  - shell
  - file_edit
mcpServers:
  - url: https://mcp.example.com/github
    name: github
---

You are a release engineer agent. When asked to cut a release, you:
1. Run `git log --oneline <prev-tag>..HEAD` to collect commits.
2. Invoke the `/changelog` skill to produce the CHANGELOG entry.
3. Bump the version in `package.json` and commit with `chore(release): vX.Y.Z`.
4. Create and push a git tag.
```

**`.github/skills/changelog/SKILL.md`**

```markdown
---
name: changelog
description: Generates a CHANGELOG entry from conventional commits.
---

Given a list of commits, group them by type (feat, fix, chore) and output a
Markdown section ready for insertion into CHANGELOG.md.

Scripts: generate-changelog.sh
```

Copilot reads only the skill metadata until `/changelog` is invoked, keeping context budget low. The agent's `tools` list restricts it to `shell` and `file_edit`, preventing it from accessing resources outside the release workflow.

## Key Takeaways

- Custom agents (`CUSTOM-AGENT-NAME.md` at `.github/agents/`) codify team-specific workflows with dedicated tools and instructions
- Skills (`SKILL.md`) use [progressive disclosure](../../agent-design/progressive-disclosure-agents.md) to teach Copilot specialized tasks without bloating context
- Plugins bundle agents, skills, MCP servers, and hooks into installable packages
- Three instruction layers: repository-wide, path-specific, and workspace-level via AGENTS.md

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [AGENTS.md](../../standards/agents-md.md)
- [Agent Skills Standard](../../standards/agent-skills-standard.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Copilot Extensions](copilot-extensions.md)
- [Migrating Copilot Extensions to MCP](../../tool-engineering/copilot-extensions-to-mcp-migration.md)
- [Copilot MCP Integration](mcp-integration.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Copilot SDK](copilot-sdk.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Agent HQ](agent-hq.md)
- [Agent Mission Control](agent-mission-control.md)
