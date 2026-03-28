---
title: "Building Dynamic System Prompts with Modular Sections"
description: "Build system prompts from modular, priority-ordered sections rather than monolithic static text — enabling mode-specific variants, provider-specific injection"
tags:
  - context-engineering
  - instructions
  - source:opendev-paper
aliases:
  - modular prompt assembly
  - composable system prompts
---

# Dynamic System Prompt Composition

> Build system prompts from modular, priority-ordered sections rather than monolithic static text — enabling mode-specific variants, provider-specific injection, and efficient API caching.

## Why Static Prompts Break Down

A single static system prompt works for simple agents. As capabilities grow, prompts accumulate sections for identity, code quality rules, safety constraints, interaction guidance, and context awareness. The result: every conversation pays the token cost for every section, regardless of relevance.

Dynamic composition addresses this by assembling the system prompt at runtime from modular sections, including only what applies to the current mode, provider, and session state ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)).

## Priority-Ordered Sections

Each section carries a numeric priority that determines assembly order ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)). The paper identifies five functional tiers — Core Identity, Tool Definitions, Safety & Rules, Provider-Specific Guidance, and Dynamic Context — without assigning specific numeric ranges. The following table illustrates one way to map those tiers to a numeric scheme:

| Priority Range | Functional Tier (illustrative) | Example Content |
|---------------|--------------------------------|-----------------|
| 10--30 | Core identity | Agent role, capabilities, boundaries |
| 40--50 | Tool definitions | Tool schemas, capability declarations |
| 55--65 | Safety & rules | Style rules, safety constraints |
| 70--80 | Provider-specific guidance | Provider-optimized instructions |
| 85--95 | Dynamic context | Session state, memory injection |

Only enabled sections are included in the final prompt. Sections can be toggled per conversation mode — planning mode omits code quality rules; execution mode omits planning heuristics ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)).

## Mode-Specific Variants

Different execution modes require different prompt emphasis. OPENDEV defines planning, thinking, and normal execution modes, each with a distinct prompt variant that includes only the constraints relevant to that mode ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)).

This prevents irrelevant instructions from consuming context and attention. A planning-mode prompt does not include code formatting rules; an execution-mode prompt does not include strategic reasoning scaffolds.

## Provider-Specific Sections

Conditional blocks inject provider-optimized instructions — Claude-specific, GPT-specific, or open-source model instructions — without bloating the prompt for other providers. The prompt assembly layer selects the appropriate blocks based on the active model ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)).

## Caching-Aware Structure

Prompt structure directly affects API cache efficiency. Separate cacheable sections (core prompt, tool schemas) from dynamic sections (session history, system reminders). OPENDEV's separation achieved significant cost reduction through effective cache hit rates ([Bui, 2025 §3.1](https://arxiv.org/abs/2603.05344)) [unverified — the specific ~40% figure is not stated in the cited section].

The design principle: place stable content first so the cacheable prefix remains constant across requests.

## Two-Tier Fallback

If custom section loading fails (corrupted config, missing files), prompt assembly falls back to default sections. The agent remains functional with baseline capabilities rather than failing entirely ([Bui, 2025 §2.3.1](https://arxiv.org/abs/2603.05344)).

## Example

The following Python snippet assembles a system prompt at runtime from priority-ordered section objects. Sections are filtered by the active mode and the current provider before being sorted and joined.

```python
from dataclasses import dataclass, field

@dataclass
class PromptSection:
    priority: int
    content: str
    modes: list[str] = field(default_factory=lambda: ["planning", "execution", "normal"])
    providers: list[str] = field(default_factory=lambda: ["anthropic", "openai"])

SECTIONS: list[PromptSection] = [
    PromptSection(
        priority=10,
        content="You are an autonomous software engineering agent. You reason step-by-step before acting.",
    ),
    PromptSection(
        priority=45,
        content="Format all responses as structured Markdown. Use headers for sections, fenced code blocks for code.",
    ),
    PromptSection(
        priority=60,
        content="Follow PEP 8. Write type annotations. Every public function must have a docstring.",
        modes=["execution"],
    ),
    PromptSection(
        priority=75,
        content="In planning mode, produce a numbered task list before writing any code.",
        modes=["planning"],
    ),
    PromptSection(
        priority=80,
        content="<claude_specific>Prefer tool use over free-form reasoning when a tool can answer the question directly.</claude_specific>",
        providers=["anthropic"],
    ),
    PromptSection(
        priority=90,
        content="Current session state: {session_state}",  # filled at runtime
    ),
]

def compose_prompt(mode: str, provider: str, session_state: str) -> str:
    active = [
        s for s in SECTIONS
        if mode in s.modes and provider in s.providers
    ]
    active.sort(key=lambda s: s.priority)
    return "\n\n".join(
        s.content.format(session_state=session_state) for s in active
    )

# Planning mode with Anthropic — omits the execution-only code quality section
system_prompt = compose_prompt(
    mode="planning",
    provider="anthropic",
    session_state="task: refactor auth module",
)
```

Sections at priority 10–45 are stable across requests and can be cached at the API level. The mode-specific sections at 60 and 75 are mutually exclusive, so only one is ever included. The provider-specific block at priority 80 is injected only for Anthropic and is absent for OpenAI calls — avoiding cross-provider [prompt bloat](../anti-patterns/prompt-tinkerer.md) without branching the calling code.

## Key Takeaways

- Assemble system prompts from priority-ordered modular sections, not monolithic text.
- Toggle sections by mode (planning vs execution) so irrelevant instructions do not consume context.
- Inject provider-specific blocks conditionally to avoid cross-provider [prompt bloat](../anti-patterns/prompt-tinkerer.md).
- Separate cacheable (stable) from dynamic (session-specific) sections for API cache efficiency.
- Fall back to default sections on load failure to maintain agent functionality.

## Unverified Claims

- OPENDEV's caching-aware prompt separation achieved significant cost reduction through effective cache hit rates [unverified — the specific ~40% figure is not stated in the cited section]

## Related

- [System Prompt Altitude](../instructions/system-prompt-altitude.md)
- [Prompt Layering: How Instructions Stack and Override](./prompt-layering.md)
- [Layered Instruction Scopes](../instructions/layered-instruction-scopes.md)
- [Context Budget Allocation: Every Token Has a Cost](./context-budget-allocation.md)
- [Prompt Caching as Architectural Discipline](./prompt-caching-architectural-discipline.md)
- [Structure Prompts with Static Content First to Maximize Cache Hits](./static-content-first-caching.md)
- [Phase-Specific Context Assembly for AI Agent Development](./phase-specific-context-assembly.md)
- [Prompt Cache Economics: Comparing Costs by Provider](./prompt-cache-economics.md)
- [Context Engineering](./context-engineering.md)
- [Layered Context Architecture](./layered-context-architecture.md)
