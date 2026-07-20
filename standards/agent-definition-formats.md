---
title: "Agent Definition Formats: How Tools Define Agent Behavior"
description: "Agent definitions control system prompt, tool access, model selection, and permissions — the format varies by tool but the concerns are the same across tools."
tags:
  - agent-design
  - tool-agnostic
  - standards
aliases:
  - agent config format
  - agent manifest format
last_reviewed: 2026-06-13
maturity: established
---

# Agent Definition Formats: How Tools Define Agent Behavior

> Agent definitions control system prompt, tool access, model selection, and permissions — the format varies by tool but the concerns are the same across tools.

## What an agent definition controls

Every agent definition answers the same questions, whatever the tool:

- Identity: what is this agent, and what is its role?
- Instructions: what are its operating constraints, quality bar, and procedures?
- Tools: which tools can it use, and which are restricted?
- Model: which LLM and configuration (`model:`) runs this agent?
- Permissions: how does it interact with the human (ask, auto-approve, sandbox)?
- Skills: what domain knowledge does it load on demand?

The format differs; the concerns stay the same.

## Claude Code format

Claude Code agents live in `.claude/agents/` as markdown files with YAML frontmatter ([Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents)):

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

The main frontmatter fields:

- `tools`: an explicit allowlist restricts which tools the agent can invoke
- `permissionMode`: controls how the agent works with the human (`default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`)
- `skills`: skill names to load — the agent reads these on startup or on demand
- `hooks`: lifecycle event handlers scoped to this agent

## GitHub Copilot format

VS Code Copilot custom agents use markdown files with YAML frontmatter and the `.agent.md` extension. You store them in `.github/agents` at the workspace level, or `~/.copilot/agents` for user profiles ([VS Code custom chat modes docs](https://code.visualstudio.com/docs/copilot/customization/custom-chat-modes)). Supported frontmatter fields include `description`, `tools` (a tool or tool-set allowlist), and `model` (a single name or a prioritized list), alongside `name`, `argument-hint`, `agents`, `user-invocable`, and `handoffs`. The body is the system prompt — the same split Claude Code uses ([Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents)).

## Portable patterns

Because agent definitions are markdown, you can write the instructions (the body) so they port across tools. The frontmatter is tool-specific, but the system prompt can follow the same structure everywhere:

1. Role statement: one sentence that defines who the agent is.
2. Scope: what tasks it handles, and what it does not handle.
3. Quality bar: the standards it applies to its output.
4. Skill references: the knowledge it loads on demand.

This four-part structure works in any agent definition format. Encode it in markdown, then adapt the frontmatter per tool.

## Anti-pattern: monolithic definitions

Some agent definitions embed all domain knowledge inline — full checklists, every procedure, complete examples. This mixes identity with expertise. The result is hard to update, duplicated across agents, and heavy on context. The portable pattern keeps them apart: the definition holds identity, and the skills hold expertise.

## Reading agent definitions

The runtime reads the frontmatter for configuration. The model reads the body for instructions. So:

- Frontmatter changes (tool restrictions, model selection) take effect on the next session.
- Body changes (instructions, quality bar) take effect right away, because the model reads the new text.
- The model reads skills, not the runtime — they extend the body, not the frontmatter.

## When this backfires

Structured agent definition files add overhead that is not always worth it. Inline prompts or command files are the better choice in three cases.

First, single-use tasks. If the agent runs once and is never reused, a definition file is indirection with no payoff.

Second, solo projects. A `.claude/agents/` directory structure costs file management that pays off only when several agents or team members reuse the definitions.

Third, fast-changing instructions. When the agent's operating constraints change on every run (dynamic config, per-invocation tool restrictions), frontmatter configuration is less flexible than building the prompt in code.

The definition-plus-skills split also carries a coherence risk. The body and the loaded skill content can drift apart, so the agent's identity ends up contradicting its expertise.

## Key Takeaways

- Agent definitions answer six questions: identity, instructions, tools, model, permissions, skills
- Claude Code: YAML frontmatter (config) + markdown body (system prompt) in `.claude/agents/`
- The markdown body can be written portably; frontmatter is tool-specific
- Frontmatter is parsed by the runtime; the body is read by the model — update accordingly
- Monolithic definitions that embed all knowledge in the body are harder to maintain than definition + skills

## Related

- [Progressive Disclosure for Agent Definitions](../patterns/agent-design/progressive-disclosure-agents.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [Agent-to-Agent (A2A) Protocol for AI Agent Development](a2a-protocol.md)
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md)
- [AGENTS.md: A README for AI Coding Agents](agents-md.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
