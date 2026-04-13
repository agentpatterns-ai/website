---
title: "System Prompt Replacement for Domain-Specific Agent Personas"
description: "Replace an agent's default coding-focused system prompt with a domain-specific identity to eliminate engineering assumptions in non-technical workflows."
aliases:
  - System Prompt Replacement
  - Domain-Specific Personas
tags:
  - instructions
---
# System Prompt Replacement for Domain-Specific Agent Personas

> Replace the default coding-focused system prompt entirely to transform an agent into a domain specialist while preserving its tool ecosystem.

!!! note "Also known as"
    System Prompt Replacement, Domain-Specific Personas. For writing domain-specific prompts with worked examples (without replacing the default prompt), see [Domain-Specific System Prompts](domain-specific-system-prompts.md).

## Augmentation vs. Replacement

Most agent customization augments the default system prompt — adding project conventions, coding standards, or domain vocabulary on top of the existing software engineering persona. System prompt replacement removes the default persona entirely and substitutes a domain-specific identity.

The distinction matters because the default system prompt carries assumptions: that tasks are code-related, that output should include implementation details, that verification means running tests. For non-engineering domains — content strategy, research analysis, business operations — these assumptions create friction. The agent frames responses through a software lens even when the task has nothing to do with code.

[Claude Code's output styles feature](https://code.claude.com/docs/en/output-styles) implements this directly: custom output styles "exclude instructions for coding (such as verifying code with tests)" and replace the default personality with domain-specific behavioral instructions. The [Claude Agent SDK](../tools/claude/agent-sdk.md) offers the same capability programmatically — passing a custom string as `systemPrompt` replaces the default entirely.

## What Gets Replaced, What Stays

Replacement targets the agent's identity layer — its assumptions about domain, task types, communication style, and response formatting. The tool ecosystem remains intact.

**Replaced**: persona framing, domain assumptions, task prioritization, interaction patterns, response formatting, coding-specific verification instructions.

**Preserved**: file system operations, script execution, sub-agent delegation, [MCP integrations](../tools/copilot/mcp-integration.md), context management ([Source: Claude Code output styles docs](https://code.claude.com/docs/en/output-styles)).

This separation is possible because tools are registered independently of the system prompt. The system prompt shapes *how the agent reasons about tasks*; tools determine *what actions it can take*. A content strategist persona still reads files, executes scripts, and delegates to sub-agents — it just reasons about brand voice instead of code quality.

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

Note: custom `systemPrompt` strings in the SDK lose [default tool instructions and safety guardrails](https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts) unless you include them manually.

## When Replacement Outperforms Augmentation

Augmentation (via CLAUDE.md or `--append-system-prompt`) is sufficient when the agent's core software engineering persona is appropriate and you need domain context on top. Replacement is warranted when:

- **The task domain has no overlap with software engineering.** A legal analyst reviewing contracts gains nothing from code verification heuristics.
- **Default assumptions actively interfere.** The coding persona's bias toward structured output, test-driven verification, and implementation-first reasoning conflicts with the domain's norms.
- **Context budget matters.** The default system prompt consumes tokens. Replacing it with a shorter, domain-focused prompt frees context for the actual task.

The technique generalizes beyond Claude Code. Any agent platform with a configurable system prompt — OpenAI Assistants, custom LangChain agents, Cursor rules — supports the same principle: strip the generic persona, install a domain-specific one, keep the tools.

## Risks

- **Lost safety guardrails.** The default prompt includes security and safety instructions. Full replacement in the SDK requires manually re-adding these — the [Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts) confirm that custom `systemPrompt` strings lose both default tools and built-in safety, while output styles and `systemPrompt` with `append` preserve both. [Claude Code output styles](https://code.claude.com/docs/en/output-styles) replace coding-specific instructions while retaining the underlying tool ecosystem and safety guardrails.
- **Tool misuse without domain framing.** An agent with file system access but no coding heuristics may use tools in unexpected ways. Domain-specific tool guidance in the replacement prompt mitigates this.
- **Maintenance burden.** A custom system prompt does not benefit from upstream improvements to the default prompt. Each platform update requires reviewing and potentially updating replacement prompts.

## Key Takeaways

- System prompt replacement removes the default persona entirely; augmentation adds to it — choose based on domain overlap
- The tool ecosystem (file ops, scripts, sub-agents, MCP) survives replacement; only the identity and reasoning layer changes
- Claude Code output styles and the Agent SDK both support full replacement with different trade-offs (safety preservation vs. complete control)
- Replacement is warranted when default coding assumptions actively interfere with the target domain

## Related

- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md)
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md)
- [Controlling Agent Output: Concise Answers, Not Essays](../agent-design/controlling-agent-output.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
