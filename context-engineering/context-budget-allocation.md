---
title: "Context Budget Allocation: Spending Every Token Wisely"
term: "Context Budget Allocation"
description: "A 200K-token window can be 150K spent before work starts: context budget allocation means choosing what loads always and what loads only on demand."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - The 50% Rule
  - Context Budget
last_reviewed: 2026-06-13
maturity: adopted
---

# Context Budget Allocation: Spending Every Token Wisely

> Context is a finite budget: every token preloaded into the context window displaces a token available for reasoning, tool results, and implementation.

Learn it hands-on: [Every Token Has a Cost](https://learn.agentpatterns.ai/context-engineering/every-token-has-a-cost/), a guided lesson with quizzes.

!!! info "Also known as"
    The 50% Rule, Context Budget. For the failure mode when budgets are ignored, see [Context Window Management: The Dumb Zone](context-window-dumb-zone.md).

## The budget framing

Context budget allocation means deciding, before a task starts, which content goes into the always-on layer and which loads on demand. It treats the context window as a finite budget that must cover preloaded instructions, tool calls, reasoning, and file reads in one session.

A 200K token context window sounds large. Load AGENTS.md, five skill definitions, three reference files, and the system prompt, and the agent may start a task with 150K tokens already consumed. The remaining 50K must cover tool calls, intermediate reasoning, file reads, and implementation. That budget shrinks further as the conversation accumulates turns.

Claude Opus 4.6 and Sonnet 4.6 support a [1M token context window](https://docs.anthropic.com/en/docs/about-claude/models) natively, at flat pricing and with no beta header required. Older models (Sonnet 4.5 and Sonnet 4) still require the `context-1m-2025-08-07` beta header and face a pricing cliff above 200K tokens. Use 1M context when retaining full history matters. Prefer compaction when you can safely summarize prior context.

[Anthropic frames this](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) as an attention budget: the n² cost of token-pair relationships means a fully packed context is computationally thinner. Signal injected early competes with signal injected later.

## The two loading strategies

### Preload (always-on)

Content loaded at session start, present for every interaction:

- System prompt — role, core constraints, behavior
- Project instructions — conventions, architectural decisions, non-discoverable context
- Skill descriptions — lightweight identifiers, not full content

### On-demand (JIT)

Content loaded when actually needed, via tool calls:

- Full skill content — loaded on invocation, not at session start
- File reads — loaded when the task reaches those files
- Web fetches, search results — loaded at the point of need

[Anthropic describes this as JIT loading](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): maintain lightweight identifiers in the always-on layer; load actual data dynamically when needed.

### The trade-off

| | Preload | On-demand |
|-|---------|-----------|
| Latency | Zero | One tool call |
| Context cost | Paid on every task | Paid only when used |
| Best for | Always-needed context | Conditionally-needed context |

A hybrid works best: preload what every task needs, and load everything else on-demand.

## Sub-agents as context isolation

Sub-agents are a context budget tool. Each sub-agent runs in its own isolated context. A research sub-agent can read 50 files without that overhead appearing in the coordinator's context. [Anthropic describes](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) sub-agent architectures as one of three approaches (alongside compaction and structured note-taking) for managing context across long tasks.

## Measuring what you load

Skill descriptions in Claude Code's skill architecture [use a dynamic budget of 1% of the context window for all skill descriptions combined](https://code.claude.com/docs/en/skills), with a fallback cap of 8,000 characters. Full skill content loads only on invocation.

All skill descriptions share that budget, so adding more skills means each description must be leaner.

## Anti-patterns

Just-in-case preloading: loading reference material in case you might need it turns conditional cost into fixed overhead on every task.

Fat always-on instructions: instructions that include code samples, directory trees, and API signatures swell the always-on layer. Replace them with hints and pointers to [discoverable content](discoverable-vs-nondiscoverable-context.md).

Single-agent monoliths for research-heavy tasks: forcing one agent to hold all research and implementation context at once. Sub-agents isolate research cost.

## Example

A Claude Code skill configuration shows the split between preload and on-demand:

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

At session start, Claude Code loads only the two `description` strings (~30 tokens total). When you trigger `migrate-api`, the full YAML (including the three `steps` entries and the file paths) enters context for that task alone. A research sub-agent that reads `src/api/v1/` does so in its own isolated context window. Only its condensed summary appears in the coordinator's context. That leaves the coordinator's budget free for synthesis and implementation.

## FAQ

**Does a 1M-token context window remove the need for a budget?**

No. Claude Opus 4.6 and Sonnet 4.6 support a [1M token context window](https://docs.anthropic.com/en/docs/about-claude/models) natively at flat pricing, while older models still need the `context-1m-2025-08-07` beta header and face a pricing cliff above 200K tokens. Use the larger window when retaining full history matters, and prefer compaction whenever prior context can be safely summarized instead.

**How much room do skill descriptions get?**

Claude Code allocates [a dynamic budget of 1% of the context window](https://code.claude.com/docs/en/skills) for all skill descriptions combined, with a fallback cap of 8,000 characters; full skill content loads only on invocation. Because every description shares that single budget, each skill you add forces the existing descriptions to get leaner.

**What makes just-in-case preloading expensive?**

It converts a conditional cost into fixed overhead paid on every task, whether or not the material is used. The same applies to always-on instructions carrying code samples, directory trees, and API signatures: they swell the preloaded layer permanently. Replace them with hints and pointers to [discoverable content](discoverable-vs-nondiscoverable-context.md) the agent can fetch when it actually needs them.

## Key Takeaways

- A 200K-token window can be 150K committed before a task even starts. Check total preload against the window size before assuming spare room exists.
- On-demand content costs one tool call; preloaded content costs budget on every task whether or not you use it. Default to on-demand for anything conditional.
- Route research-heavy work to a sub-agent: only its condensed summary reaches the coordinator's context, not the files it read to produce it.
- Reserve meaningful headroom beyond preloaded content for tool calls, reasoning, and file reads: a fully packed window's [n² attention cost](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) makes late-session reasoning computationally thinner.

## Related

- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Context Window Anxiety: Countering Premature Task Closure](context-window-anxiety.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Long Context vs Retrieval: The Break-Even Decision](long-context-vs-retrieval-break-even.md)
- [Semantic Density Optimization for Agent Codebases](semantic-density-optimization.md)
