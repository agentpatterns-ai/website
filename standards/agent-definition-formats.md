---
title: "Agent Definition Formats: How Tools Define Agent Behavior"
description: "Agent definitions control system prompt, tool access, model selection, and permissions — the format varies by tool but the concerns are the same across all"
tags:
  - agent-design
  - tool-agnostic
aliases:
  - agent config format
  - agent manifest format
---

# Agent Definition Formats: How Tools Define Agent Behavior

> Agent definitions control system prompt, tool access, model selection, and permissions — the format varies by tool but the concerns are the same across all implementations.

## What an Agent Definition Controls

Every agent definition answers the same questions regardless of the tool:

- **Identity** — what is this agent, what is its role?
- **Instructions** — what are its operating constraints, quality bar, and procedures?
- **Tools** — which tools can it use, which are restricted?
- **Model** — which LLM and configuration runs this agent?
- **Permissions** — how does it interact with the human (ask, auto-approve, sandbox)?
- **Skills** — what domain knowledge does it load on demand?

The format differs; the concerns are stable.

## Claude Code Format

Claude Code agents live in `.claude/agents/` as markdown files with YAML frontmatter ([docs](https://code.claude.com/docs/en/sub-agents)):

```yaml
---
name: content-reviewer
description: Reviews drafted content pages for accuracy and standards compliance
model: claude-opus-4-5
tools:
  - Read
  - WebFetch
permissionMode: acceptEdits
skills:
  - writing-rules
  - accuracy-framework
---

You are a content reviewer for the project documentation site.
Review each page against the standards defined in your loaded skills.
...
```

The YAML frontmatter is machine-readable configuration. The markdown body is the system prompt. The model reads the body; the runtime reads the frontmatter.

Key frontmatter fields:

- `tools`: explicit allowlist restricts what tools the agent can invoke
- `permissionMode`: controls human-agent interaction (`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`)
- `skills`: skill names to load — the agent reads these on startup or on demand
- `hooks`: lifecycle event handlers scoped to this agent

## GitHub Copilot Format

GitHub Copilot uses `.github/agents/` directories with markdown agent files [unverified — Copilot agent format is evolving; verify against current docs.github.com]. The structure mirrors Claude Code: frontmatter for configuration, markdown body for instructions. The specific field names differ.

## Portable Patterns

Because agent definitions are markdown, the instructions (body) can be written portably. The frontmatter is tool-specific, but the system prompt can follow the same structure across tools:

1. **Role statement** — one sentence defining who the agent is
2. **Scope** — what tasks it handles, what it does not handle
3. **Quality bar** — standards it applies to its output
4. **Skill references** — what knowledge it loads on demand

This four-element structure works in any agent definition format. Encode it in markdown; adapt the frontmatter per tool.

## Anti-Pattern: Monolithic Definitions

Agent definitions that embed all domain knowledge inline — full checklists, all procedures, complete examples — combine identity with expertise in a way that is hard to update, duplicated across agents, and heavy on context. The portable pattern separates them: definition contains identity, skills contain expertise.

## Reading Agent Definitions

The runtime reads frontmatter for configuration. The model reads the body for instructions. This means:

- Frontmatter changes (tool restrictions, model selection) take effect on the next session
- Body changes (instructions, quality bar) take effect immediately — the model reads the new text
- Skills are read by the model, not the runtime — they extend the body, not the frontmatter

## Key Takeaways

- Agent definitions answer six questions: identity, instructions, tools, model, permissions, skills
- Claude Code: YAML frontmatter (config) + markdown body (system prompt) in `.claude/agents/`
- The markdown body can be written portably; frontmatter is tool-specific
- Frontmatter is parsed by the runtime; the body is read by the model — update accordingly
- Monolithic definitions that embed all knowledge in the body are harder to maintain than definition + skills

## Unverified Claims

- GitHub Copilot agent format uses `.github/agents/` directories with markdown agent files `[unverified — Copilot agent format is evolving; verify against current docs.github.com]`

## Related

- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
- [AGENTS.md: A README for AI Coding Agents](agents-md.md)
- [Tool Calling Schema Standards](tool-calling-schema-standards.md)
- [OpenAPI as the Source of Truth for Agent Tool Definitions](openapi-agent-tool-spec.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
