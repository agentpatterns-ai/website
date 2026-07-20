---
title: "GitHub Copilot Custom Agents and Skills Extensibility Guide"
description: "GitHub Copilot custom agents, skills, and plugins let teams codify workflows, teach Copilot specialized tasks, and share capabilities as installable packages."
tags:
  - agent-design
  - instructions
  - copilot
  - skills
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
---

# GitHub Copilot Custom Agents and Skills Extensibility Guide

> Custom agents, skills, and plugins are GitHub Copilot's three extensibility layers — agents codify team workflows, skills teach Copilot specialized tasks via progressive disclosure, and plugins bundle everything into shareable packages.

## Custom agents

Define [`CUSTOM-AGENT-NAME.md` files](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents) under `.github/agents/` to create specialized agents with their own tools, [MCP servers](mcp-integration.md), and instructions. Agents then become available in the [coding agent on GitHub.com, coding agent in IDEs, and GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents).

## Agent skills

[Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills) are `SKILL.md` folders that hold instructions, scripts, and resources. Copilot auto-loads them when relevant through progressive disclosure: it reads the skill metadata first, then loads the scripts and templates only when needed, so the context window stays small.

Skills [surface as slash commands](https://code.visualstudio.com/docs/copilot/customization/agent-skills) in chat. They work across the Copilot coding agent, CLI, and VS Code.

The [Agent Skills specification](https://agentskills.io) defines the open standard. The [microsoft/skills](https://github.com/microsoft/skills) repository provides Azure SDK-specific skills and plugin packages.

## Prompt files

[Prompt files](../../instructions/prompt-file-libraries.md) live in `.github/prompts/` and define specialized prompts you invoke with `/` commands. They use YAML frontmatter to set which model to use, and you keep them in source control to share across the team.

## Plugins

[Plugins](https://github.com/microsoft/skills) bundle MCP servers, agents, skills, and hooks into installable packages. Install from GitHub repos with `npx skills add owner/repo`. Skills from a plugin appear alongside local skills.

Plugin marketplace management arrived in [VS Code 1.113+](https://code.visualstudio.com/updates/v1_113). The `Chat: Manage Plugin Marketplaces` command lists configured marketplaces, with options to browse them, locate their directories, and remove plugins. URL handler installation uses the format `vscode://chat-plugin/install?source=<source>`.

## Custom instructions

- Repository instructions: `copilot-instructions.md` in `.github/` applies to every request in that repo
- Path-specific instructions: `NAME.instructions.md` in `.github/instructions/` applies only to matching file paths
- AGENTS.md: auto-detected in the workspace root, and supports subfolder-level instructions

See [custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) in the GitHub docs.

## Limitations

The official docs flag three sharp edges in these layers:

- Skills silently fail to load when the `name` field contains invalid characters. Slashes, colons, dots, or hand-added namespace prefixes like `myorg/skillname` drop the skill without an error ([VS Code: Use Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)). The parent directory name must also match the `name` field exactly, or the skill does not load.
- Activation depends on description quality. Copilot reads the skill description to decide whether to load it, so a vague description makes Copilot miss relevant invocations ([VS Code: Use Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)).
- Long instruction and skill context degrades adherence. Skills stack on top of base instructions, and practitioners report that once the combined instruction context gets long, the agent follows it less reliably ([Your Agent Instructions Are Probably Making Things Worse](https://www.wordman.dev/blog/agent-instructions)). Keep each skill narrow and prune instruction files often.

## Example

This example pairs a minimal custom agent with a companion skill to show how the two layers work together. The agent lives at `.github/agents/release-engineer.md` and declares which tools and MCP servers it may use. The skill lives at `.github/skills/changelog/SKILL.md`, and Copilot auto-loads it when the task is relevant.

`.github/agents/release-engineer.md`

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

`.github/skills/changelog/SKILL.md`

```markdown
---
name: changelog
description: Generates a CHANGELOG entry from conventional commits.
---

Given a list of commits, group them by type (feat, fix, chore) and output a
Markdown section ready for insertion into CHANGELOG.md.

Scripts: generate-changelog.sh
```

Copilot reads only the skill metadata until you invoke `/changelog`, which keeps the context budget low. The agent's `tools` list restricts it to `shell` and `file_edit`, so it cannot reach resources outside the release workflow.

## Key Takeaways

- Custom agents (`CUSTOM-AGENT-NAME.md` at `.github/agents/`) codify team-specific workflows with dedicated tools and instructions
- Skills (`SKILL.md`) use [progressive disclosure](../../patterns/agent-design/progressive-disclosure-agents.md) to teach Copilot specialized tasks without bloating context
- Plugins bundle agents, skills, MCP servers, and hooks into installable packages
- Three instruction layers: repository-wide, path-specific, and workspace-level via AGENTS.md

## Related

- [Agent Mission Control](agent-mission-control.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [AGENTS.md](../../standards/agents-md.md)
- [Agent Skills Standard](../../standards/agent-skills-standard.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Copilot Extensions](copilot-extensions.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Managing Agent Skills from the GitHub CLI](gh-skill-cli-management.md)
