---
title: "Context Priming: Pre-Loading Files for AI Agent Tasks"
description: "Context priming loads relevant files into an agent context window before a task, improving output quality by grounding the agent in your codebase."
tags:
  - context-engineering
  - instructions
aliases:
  - Providing Context to Agents
  - Seeding Agent Context
  - Breadcrumbs in Code
---

# Context Priming

> Load relevant context before asking an agent to act — the order information enters the context window shapes the quality of everything that follows.

!!! note "Also known as"
    Providing Context to Agents, Seeding Agent Context, Breadcrumbs in Code. Context priming is the general technique of loading context before a task. For embedding persistent contextual hints directly in the codebase for agents to discover, see [Seeding Agent Context](seeding-agent-context.md).

## How It Works

Agents don't retrieve project knowledge on their own. They work with what's in the context window at the time they generate a response. A cold prompt — "add authentication to the API" — forces the agent to guess at existing patterns, naming conventions, and architecture. Priming reverses this: you load the relevant context first, then ask.

An agent that has read your middleware layer, auth config, and user model before implementing authentication produces output that fits the codebase. Without that context, it produces generic code that defaults to common framework boilerplate rather than project-specific patterns.

## Priming Strategies

### Read Before Write

Have the agent read the files it will touch — and the files adjacent to them — before making any changes. For a new feature, that means existing similar features, the relevant module's entry point, and any shared utilities it will call.

### Progressive Context Loading

Start broad, then narrow:

1. Architecture overview (AGENTS.md, README, top-level structure)
2. Module or subsystem relevant to the task
3. Specific file(s) to modify

Dumping everything at once is less effective than building understanding incrementally. Language models attend more reliably to content at the start and end of a context window than to content buried in the middle — the [lost-in-the-middle effect](https://arxiv.org/abs/2307.03172). Loading architecture first, then specifics, keeps the most critical framing at the attention-favored start of context rather than interleaved with detail.

### Explore Before Implement

Use a read-only exploration phase before switching to implementation mode. Some tools support this explicitly — Claude Code's [plan mode](../workflows/plan-mode.md) separates reasoning from execution, letting the agent map out its approach before writing any code.

### Use Plan Mode

When your tool supports it, require a plan step before implementation. This forces the agent to surface its understanding of the codebase and the task. Review the plan, correct any misunderstandings, then approve execution. Catching a wrong assumption at plan time costs nothing; catching it after implementation costs a rewrite.

## Anti-Patterns

**Cold implementation**: Asking the agent to implement without reading existing code first. The agent defaults to generic patterns rather than project-specific ones.

**One-shot context dump**: Pasting all relevant files into a single prompt. This treats context as a bulk transfer rather than a structured loading sequence. Order within the dump still matters — information at the start and end of a context window receives more attention than information in the middle, a phenomenon documented in [lost-in-the-middle research](https://arxiv.org/abs/2307.03172).

## Example

The following Claude Code session demonstrates progressive context loading before implementing a new authentication endpoint. Context is built broad-to-narrow before any changes are made.

```bash
# Step 1 — architecture overview
cat AGENTS.md
cat README.md

# Step 2 — relevant module entry point and existing auth patterns
cat src/middleware/auth.ts
cat src/routes/auth/login.ts
cat src/routes/auth/logout.ts

# Step 3 — the specific files the new endpoint will touch
cat src/routes/auth/index.ts
cat src/models/user.ts
cat src/config/jwt.ts
```

After loading these files, the agent has the middleware signature, existing route conventions, the JWT config format, and the user model shape — all before writing a single line. The prompt that follows can be tightly focused:

```
Add a POST /auth/refresh endpoint. Follow the existing pattern in login.ts.
Use the refreshToken field on the User model. Return a new access token signed with jwtConfig.secret.
```

Contrast this with a cold prompt that provides none of the above context — the agent would fall back to generic Express boilerplate, require rework to match the actual middleware signature, and likely miss the `refreshToken` field entirely.

## Why It Works

Transformer models generate each token conditioned on all tokens currently in context — there is no separate "memory" step. When the agent generates code, it pattern-matches against the examples it can see right now. Loading your actual middleware signature, naming conventions, and config shape before the task puts those patterns directly in the distribution the model samples from, making project-specific outputs more probable and generic boilerplate less probable. This is the same mechanism that makes few-shot prompting effective: in-context examples shift output distribution without any weight update.

## When This Backfires

- **Context window saturation**: Pre-loading large files pushes task instructions and earlier reasoning toward the middle of the context window, where attention degrades. Long files should be trimmed or summarized before loading ([Context Compression Strategies](context-compression-strategies.md)).
- **Low-precision context**: Loading loosely related files adds noise that competes with the relevant signal. If the loaded content doesn't directly constrain the task output, it can steer the agent toward irrelevant patterns.
- **Short, self-contained tasks**: For tasks with no codebase dependency — writing a pure-function utility, converting a data format — priming adds latency and token cost without affecting output quality. Apply selectively.
- **Stale context**: If loaded files don't reflect the current state of the codebase (out-of-date after a refactor), the agent anchors on the wrong patterns. Verify that primed files are current before loading.

## Key Takeaways

- Agents work with what's in context — they don't automatically know your codebase
- Read relevant files first; implement second
- Build context progressively: broad architecture → specific files
- Use [plan mode](../workflows/plan-mode.md) to verify the agent's understanding before it acts
- Position critical context at the start of the prompt, not buried in the middle

## Related

- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
- [Context Compression Strategies: Offloading and Summarisation](context-compression-strategies.md)
- [Context Engineering: The Practice of Shaping Agent Context](context-engineering.md)
- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md)
- [Phase-Specific Context Assembly for AI Agent Development](phase-specific-context-assembly.md)
- [Layered Context Architecture for AI Agent Development](layered-context-architecture.md)
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md)
- [Repository Map Pattern: AST + PageRank for Dynamic Code](repository-map-pattern.md)
- [Retrieval-Augmented Agent Workflows: On-Demand Context](retrieval-augmented-agent-workflows.md)
- [Context Budget Allocation: Spending Every Token Wisely](context-budget-allocation.md)
- [Context Window Management: Understanding the Dumb Zone](context-window-dumb-zone.md)
- [Discoverable vs Non-Discoverable Context for Agents](discoverable-vs-nondiscoverable-context.md)
- [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md)
