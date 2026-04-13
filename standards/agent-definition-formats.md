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
- `permissionMode`: controls human-agent interaction (`default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`)
- `skills`: skill names to load — the agent reads these on startup or on demand
- `hooks`: lifecycle event handlers scoped to this agent

## GitHub Copilot Format

GitHub Copilot agent definitions use a similar frontmatter-plus-body structure to Claude Code, with tool-specific field names. Consult the current [GitHub Copilot Extensions documentation](https://docs.github.com/en/copilot) for the canonical directory location and supported frontmatter fields, as the format continues to evolve.

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

## When This Backfires

Structured agent definition files add overhead that isn't always justified. Three conditions where inline prompts or command files are the better choice: (1) **single-use tasks** — if the agent runs once and is never reused, a definition file is indirection without benefit; (2) **solo projects** — maintaining a `.claude/agents/` directory structure imposes file management cost that pays off only when multiple agents or multiple team members reuse the definitions; (3) **rapidly evolving instructions** — when the agent's operating constraints change on every run (dynamic config, per-invocation tool restrictions), frontmatter-based configuration is less flexible than programmatic construction. The definition-plus-skills split also creates a coherence risk: the body and the loaded skill content can drift independently, producing an agent whose identity contradicts its expertise.

## Key Takeaways

- Agent definitions answer six questions: identity, instructions, tools, model, permissions, skills
- Claude Code: YAML frontmatter (config) + markdown body (system prompt) in `.claude/agents/`
- The markdown body can be written portably; frontmatter is tool-specific
- Frontmatter is parsed by the runtime; the body is read by the model — update accordingly
- Monolithic definitions that embed all knowledge in the body are harder to maintain than definition + skills

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
