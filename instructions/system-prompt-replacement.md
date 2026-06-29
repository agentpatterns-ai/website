---
title: "System Prompt Replacement for Domain-Specific Agent Personas"
term: "System Prompt Replacement"
description: "Replace an agent's default coding-focused system prompt with a domain-specific identity to eliminate engineering assumptions in non-technical workflows."
aliases:
  - System Prompt Replacement
  - Domain-Specific Personas
tags:
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: adopted
---

# System Prompt Replacement for Domain-Specific Agent Personas

> Replace the default coding-focused system prompt entirely to transform an agent into a domain specialist while preserving its tool ecosystem.

!!! note "Also known as"
    System Prompt Replacement, Domain-Specific Personas. For writing domain-specific prompts with worked examples (without replacing the default prompt), see [Domain-Specific System Prompts](domain-specific-system-prompts.md).

## Augmentation versus replacement

Most agent customization augments the default system prompt — adding project conventions, coding standards, or domain vocabulary on top of the existing software engineering persona. System prompt replacement removes the default persona entirely and substitutes a domain-specific identity.

The distinction matters because the default system prompt carries assumptions that [domain-specific system prompts](domain-specific-system-prompts.md) target directly: that tasks are code-related, that output should include implementation details, that verification means running tests. For non-engineering domains — content strategy, research analysis, business operations — these assumptions create friction. The agent frames responses through a software lens even when the task has nothing to do with code.

[Claude Code's output styles feature](https://code.claude.com/docs/en/output-styles) implements this directly: custom output styles "exclude instructions for coding (such as verifying code with tests)" and replace the default personality with domain-specific behavioral instructions. The [Claude Agent SDK](../tools/claude/agent-sdk.md) offers the same capability programmatically — passing a custom string as `systemPrompt` replaces the default entirely.

## What gets replaced, what stays

Replacement targets the agent's identity layer — its assumptions about domain, task types, communication style, and response formatting. The tool set stays intact.

Replaced: persona framing, domain assumptions, task prioritization, interaction patterns, response formatting, coding-specific verification instructions.

Preserved: file system operations, script execution, sub-agent delegation, [MCP integrations](../tools/copilot/mcp-integration.md), context management ([Source: Claude Code output styles docs](https://code.claude.com/docs/en/output-styles)).

This separation works because tools are registered independently of the system prompt. The system prompt shapes how the agent reasons about tasks; the tools determine what actions it can take. A content strategist persona still reads files, runs scripts, and delegates to sub-agents — it just reasons about brand voice instead of code quality.

## Implementation

In Claude Code, create a markdown file in `~/.claude/output-styles/` (global) or `.claude/output-styles/` (project-level):

```markdown
---
name: Content Strategist
description: Brand-aware content creation and editing
---

You are a content strategist specializing in [brand/domain].

## Core Responsibilities
- Maintain brand voice consistency across all content
- Apply editorial standards: [specific standards]
- Structure content for the target audience

## Domain Vocabulary
- [Term]: [Definition in context]

## Output Format
- Provide content drafts in markdown
- Flag voice inconsistencies with inline annotations
- Include readability metrics when editing
```

Setting `keep-coding-instructions: false` (the default for custom styles) removes software engineering instructions from the system prompt. Set it to `true` only for styles that blend coding with another domain.

In the Agent SDK, pass the prompt directly:

```typescript
const messages = [];
for await (const message of query({
  prompt: "Review this quarterly report draft",
  options: {
    systemPrompt: "You are a business analyst specializing in..."
  }
})) {
  messages.push(message);
}
```

Note: custom `systemPrompt` strings in the SDK lose [default tool instructions and safety guardrails](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) unless you include them manually.

## When replacement outperforms augmentation

Augmentation (via CLAUDE.md or `--append-system-prompt`) is enough when the agent's core software engineering persona fits and you need domain context on top. Replacement is warranted when:

- the task domain has no overlap with software engineering: a legal analyst reviewing contracts gains nothing from code verification heuristics
- the default assumptions actively interfere, because the coding persona's bias toward structured output ([controlling agent output](controlling-agent-output.md)), test-driven verification, and implementation-first reasoning conflicts with the domain's norms
- the context budget matters, because the default system prompt consumes tokens and a shorter, domain-focused prompt frees context for the actual task

The technique generalizes beyond Claude Code. Any agent platform with a configurable system prompt — OpenAI Assistants, custom LangChain agents, Cursor rules — supports the same principle: strip the generic persona, install a domain-specific one, keep the tools.

## Risks

- Lost safety guardrails. The default prompt includes security and safety instructions. Full replacement in the SDK means you re-add these by hand — the [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) confirm that custom `systemPrompt` strings lose both default tools and built-in safety, while output styles and `systemPrompt` with `append` preserve both. [Claude Code output styles](https://code.claude.com/docs/en/output-styles) replace coding-specific instructions while keeping the underlying tool set and safety guardrails.
- Tool misuse without domain framing. An agent with file system access but no coding heuristics may use tools in unexpected ways. Domain-specific tool guidance in the replacement prompt reduces this.
- Maintenance burden. A custom system prompt does not gain from upstream improvements to the default prompt, and each model generation can shift its behavior — see [prompt rewrite on cross-generation migration](prompt-rewrite-on-cross-generation-migration.md). Each platform update means you review and may update the replacement prompts.

## Key Takeaways

- System prompt replacement removes the default persona entirely; augmentation adds to it — choose based on domain overlap
- The tool ecosystem (file ops, scripts, sub-agents, MCP) survives replacement; only the identity and reasoning layer changes
- Claude Code output styles and the Agent SDK both support full replacement with different trade-offs (safety preservation vs. complete control)
- Replacement is warranted when default coding assumptions actively interfere with the target domain

## Related

- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md)
- [Production System Prompt Architecture](production-system-prompt-architecture.md) — sibling on system-prompt design; layered production architecture rather than wholesale replacement
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md)
- [Controlling Agent Output: Concise Answers, Not Essays](controlling-agent-output.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
