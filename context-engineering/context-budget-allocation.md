---
title: "Context Budget Allocation: Spending Every Token Wisely"
description: "Context is a finite budget — every token preloaded into the context window displaces a token available for reasoning, tool results, and implementation."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - The 50% Rule
  - Context Budget
---

# Context Budget Allocation: Every Token Has a Cost

> Context is a finite budget — every token preloaded into the context window displaces a token available for reasoning, tool results, and implementation.

!!! info "Also known as"
    **The 50% Rule**, **Context Budget**. For the failure mode when budgets are ignored, see [Context Window Management: The Dumb Zone](context-window-dumb-zone.md).

## The Budget Framing

Context budget allocation is the practice of deciding, before a task starts, which content goes into the always-on layer and which loads on demand — treating the context window as a finite budget that must cover preloaded instructions, tool calls, reasoning, and file reads within a single session.

A 200K token context window sounds large. Load AGENTS.md, five skill definitions, three reference files, and the system prompt, and the agent may start a task with 150K tokens already consumed. The remaining 50K must cover tool calls, intermediate reasoning, file reads, and implementation — and shrinks further as the conversation accumulates turns.

Claude Opus 4.6 and Sonnet 4.6 support a [1M token context window](https://docs.anthropic.com/en/docs/about-claude/models) natively — no beta header required, at flat pricing. Older models (Sonnet 4.5 and Sonnet 4) still require the `context-1m-2025-08-07` beta header and face a pricing cliff above 200K tokens. Use 1M context when retaining full history matters; prefer compaction when prior context can be safely summarized.

[Anthropic frames this](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) as an attention budget: the n² cost of token-pair relationships means a fully packed context is computationally thinner. Signal injected early competes with signal injected later.

## The Two Loading Strategies

### Preload (Always-On)

Content loaded at session start, present for every interaction:

- System prompt — role, core constraints, behavior
- Project instructions — conventions, architectural decisions, non-discoverable context
- Skill descriptions — lightweight identifiers, not full content

Cost: paid on every task. Benefit: zero latency.

### On-Demand (JIT)

Content loaded when actually needed, via tool calls:

- Full skill content — loaded on invocation, not at session start
- File reads — loaded when the task reaches those files
- Web fetches, search results — loaded at the point of need

[Anthropic describes this as JIT loading](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): maintain lightweight identifiers in the always-on layer; load actual data dynamically when needed.

Cost: one tool call. Benefit: budget preserved until needed.

### The Trade-off

| | Preload | On-demand |
|-|---------|-----------|
| Latency | Zero | One tool call |
| Context cost | Paid on every task | Paid only when used |
| Best for | Always-needed context | Conditionally-needed context |

Hybrid: preload what every task needs; load everything else on-demand.

## Sub-Agents as Context Isolation

Sub-agents are a budget tool, not just an architecture pattern. Each sub-agent runs in its own isolated context — a research sub-agent can read 50 files without that overhead appearing in the coordinator's context. [Anthropic describes](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) sub-agent architectures as one of three complementary approaches — alongside compaction and structured note-taking — for managing context across long-horizon tasks.

## Measuring What You Load

Skill descriptions in Claude Code's skill architecture [use a dynamic budget of 1% of the context window for all skill descriptions combined](https://code.claude.com/docs/en/skills), with a fallback cap of 8,000 characters. Full skill content loads only on invocation.

All skill descriptions share that budget, so adding more skills means each description must be leaner.

## Anti-Patterns

**Just-in-case preloading**: Loading reference material "in case it's needed" converts conditional cost into fixed overhead on every task.

**Fat always-on instructions**: Instructions that include code samples, directory trees, and API signatures bloat the always-on layer. Replace with hints and pointers to discoverable content.

**Single-agent monoliths for research-heavy tasks**: Forcing one agent to hold all research and implementation context simultaneously. Sub-agents isolate research cost.

## Example

A Claude Code skill configuration demonstrating the preload vs. on-demand split:

```yaml
# .claude/skills/migrate-api.yaml  — full content, loaded on invocation only
name: migrate-api
description: "Migrate REST endpoints to the v2 API contract"  # ← this line lives in always-on context (~15 tokens)
steps:
  - read: [src/api/v1/, src/api/v2/schema.json, tests/api/]
  - run: "npm run lint -- --fix"
  - run: "npm test -- --testPathPattern=api"
```

```yaml
# .claude/skills/summarise-pr.yaml
name: summarise-pr
description: "Summarise a pull request for the changelog"
steps:
  - run: "gh pr view $PR_NUMBER --json title,body,files"
```

At session start, Claude Code loads only the two `description` strings (~30 tokens total). When `migrate-api` is triggered, the full YAML — including the three `steps` entries and the file paths — enters context for that task alone. A research sub-agent that reads `src/api/v1/` does so in its own isolated context window; only its condensed summary appears in the coordinator's context, leaving the coordinator's budget available for synthesis and implementation.

## Key Takeaways

- Context is a budget: every preloaded token displaces a token available for work.
- Preload only what every task needs; load everything else on-demand.
- Sub-agents isolate context cost — research in one context, synthesis in another.
- Reserve meaningful headroom beyond preloaded content for tool calls, reasoning, and file reads — the [n² attention cost](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) of a fully packed window makes late-session reasoning computationally thinner.

## Related

- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Context Window Anxiety: Countering Premature Task Closure](context-window-anxiety.md)
- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md)
- [Semantic Density Optimization for Agent Codebases](semantic-density-optimization.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Manual Compaction and Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md)
- [Prompt Compression: Maximizing Signal Per Token](prompt-compression.md)
- [Prompt Cache Economics Across Providers](prompt-cache-economics.md)
- [Semantic Context Loading](semantic-context-loading.md)
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [Attention Sinks: Why First Tokens Always Win](attention-sinks.md)
- [Context Priming](context-priming.md)
- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md)
- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md)
- [Repository Map Pattern](repository-map-pattern.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Seeding Agent Context](seeding-agent-context.md)
- [Static Content First for Cache Hits](static-content-first-caching.md)
