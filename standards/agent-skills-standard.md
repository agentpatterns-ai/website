---
title: "Agent Skills: A Cross-Tool Task Knowledge Standard"
description: "The Agent Skills open standard packages task-specific knowledge into portable SKILL.md folders for cross-tool discovery and reuse on demand."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - SKILL.md standard
  - agent skills spec
---

# Agent Skills: Cross-Tool Task Knowledge Standard

> The Agent Skills open standard packages task-specific knowledge into portable SKILL.md folders that AI coding tools can discover and load on demand.

## What the Standard Defines

The [Agent Skills standard](https://agentskills.io) specifies a format for distributing task knowledge across AI coding tools. A skill is a directory containing a `SKILL.md` entrypoint with YAML frontmatter and markdown instructions, optionally accompanied by supporting files: scripts, templates, examples, or schemas.

The standard is tool-agnostic. Claude Code and GitHub Copilot (VS Code, CLI, and cloud agent) both implement it ([VS Code Agent Skills docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Claude Code skills docs](https://code.claude.com/docs/en/skills)). Other tools including Cursor and Gemini CLI have adopted the standard per the agentskills.io registry, but cross-tool portability is only confirmed for tools that have published implementation documentation.

## Skill Structure

```
skills/
  writing-rules/
    SKILL.md          # entrypoint with frontmatter + instructions
    templates/        # supporting files
    examples/
```

`SKILL.md` frontmatter specifies metadata the tool uses to match skills to tasks:

```yaml
---
name: writing-rules
description: Style, tone, and structure standards for content pages
version: 1.0.0
---
```

The markdown body contains the actual instructions the agent reads.

## Discovery and Loading

Skills are discovered from three locations, in order of precedence:

1. **Project skills** — `.claude/skills/` or `.github/skills/` — committed to the repo, shared with all contributors
2. **User skills** — `~/.claude/skills/` — local to the developer, available across all projects
3. **Plugin skills** — distributed as part of an installable plugin bundle

Agents load skills on demand: when a task matches a skill's scope, the agent reads `SKILL.md` and any referenced supporting files. This is the progressive disclosure pattern applied to knowledge distribution — see [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md).

## Portability Value

Without a standard, skill knowledge is embedded in tool-specific formats. A checklist written for Claude Code's agent format doesn't transfer to GitHub Copilot without manual adaptation. With the standard, the same `SKILL.md` works wherever the standard is implemented.

This matters for teams using multiple tools and for open-source skill distribution. The [github/awesome-copilot](https://github.com/github/awesome-copilot) repository demonstrates community-scale skill sharing.

## Relationship to Agent Definitions and Commands

Skills carry domain knowledge. Agent definitions carry identity and skill references. Commands carry orchestration logic. The three layers are distinct:

- A `writing-rules` skill knows what good content looks like
- A `content-writer` agent knows it should use writing-rules for drafting tasks
- A `draft-content` command knows to invoke content-writer after research is complete

Skills are the reusable knowledge layer; agents and commands are not.

## In Practice

A documentation project might maintain skills covering [content pipeline](../workflows/content-pipeline.md) management, writing standards, accuracy frameworks, and site navigation. Each agent definition references the skills it needs; each skill is self-contained. A typical project keeps 5--15 skills, each focused on one domain concern.

Claude Code implementation: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills).

## Example

A documentation team maintains a `writing-rules` skill in `.github/skills/writing-rules/`:

```
.github/skills/
  writing-rules/
    SKILL.md
    templates/
      page-template.md
```

`SKILL.md` content:

```yaml
---
name: writing-rules
description: Style, tone, and structure standards for documentation pages
version: 1.2.0
---
```

```markdown
# Writing Rules

## Audience
Write for practitioners who deploy and configure agents. Skip introductory definitions; assume working knowledge.

## Structure
Every page opens with a `>` blockquote that defines the concept, not describes the page.

## Tone
Active voice. Present tense. No filler phrases ("it's worth noting", "in this guide").
```

When a contributor runs `/draft-content`, the agent definition for `content-writer` references `writing-rules`. The tool discovers `.github/skills/writing-rules/SKILL.md`, loads it into context, and the agent applies the style rules without the contributor needing to specify them. The same skill file works unchanged in Claude Code, GitHub Copilot, and Cursor.

## Why the Standard Works

Portability comes from two design decisions. First, the `SKILL.md` entrypoint is a fixed path that any tool can locate without configuration — tools scan `.claude/skills/`, `.github/skills/`, and user-level equivalents because the standard specifies those paths. Second, YAML frontmatter makes skill metadata machine-readable: a tool can match a skill to a task by comparing the `description` field against the current context without loading the full instruction body. The progressive disclosure effect follows directly — only the metadata pays the context cost until the skill activates. ([Source: Claude Code skills docs](https://code.claude.com/docs/en/skills))

## When This Backfires

The standard adds value only when skills need to cross tool or team boundaries. Four conditions make it the wrong choice:

- **Single-tool, single-developer projects** — if one person uses one tool, the portability guarantee is unused overhead. A plain markdown file in `CLAUDE.md` or a tool-specific command has less structure with no loss.
- **Rapidly changing instructions** — skill files are versioned assets. When guidance evolves daily, the structure and tooling overhead of maintaining SKILL.md directories slows iteration relative to ad-hoc prompting.
- **Tool mismatch on frontmatter extensions** — tools extend the standard with non-portable frontmatter fields (Claude Code adds `disable-model-invocation`, `context: fork`; VS Code adds its own fields). Skills that rely on these extensions lose portability silently — the file loads, but tool-specific behavior is silently ignored.
- **Untrusted skill sources** — the same portability that enables cross-tool reuse also enables prompt-injection payloads to run wherever the standard is implemented. Snyk's [ToxicSkills audit of 3,984 published skills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) found 534 (13.4%) contained critical-severity issues — 76 confirmed malicious payloads including credential theft and data exfiltration, with 91% of malicious skills combining native code patterns and prompt injection. Skills from community registries should be treated like any other third-party code dependency — reviewed, pinned, and sandboxed — not trusted by default because they loaded cleanly.

## Key Takeaways

- Skills are directories with a `SKILL.md` entrypoint: frontmatter metadata + markdown instructions
- The Agent Skills standard enables the same skill to work across multiple AI coding tools; confirmed implementors include Claude Code and GitHub Copilot
- Discovery order: project → user → plugin
- Skills carry domain knowledge; agent definitions reference them; commands orchestrate agents
- Community distribution: skills as git repos, installable by URL or plugin bundle

## Related

- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
- [Cross-Tool Translation: Learning from Multiple AI Assistants](../human/cross-tool-translation.md)
- [AGENTS.md: Project-Level README for AI Coding Agents](agents-md.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
- [Agent-to-Agent (A2A) Protocol for AI Agent Development](a2a-protocol.md)
