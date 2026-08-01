---
title: "Context Priming: Pre-Loading Files for AI Agent Tasks"
term: "Context Priming"
description: "Context priming loads relevant files into an agent context window before a task, improving output quality by grounding the agent in your codebase."
tags:
  - context-engineering
  - instructions
  - tool-agnostic
aliases:
  - Providing Context to Agents
  - Seeding Agent Context
  - Breadcrumbs in Code
last_reviewed: 2026-06-13
maturity: emerging
---

# Context Priming: Pre-Loading Files for AI Agent Tasks

> Load relevant context before asking an agent to act — the order information enters the context window shapes the quality of everything that follows.

Learn it hands-on: [Prime the Pump](https://learn.agentpatterns.ai/context-engineering/prime-the-pump/) — guided lesson with quizzes.

!!! note "Also known as"
    Providing Context to Agents, Seeding Agent Context, Breadcrumbs in Code. Context priming is the general technique of loading context before a task. For embedding persistent contextual hints directly in the codebase for agents to discover, see [Seeding Agent Context](seeding-agent-context.md).

## How it works

Agents do not retrieve project knowledge on their own. They work with whatever is in the context window when they generate a response. A cold prompt — "add authentication to the API" — forces the agent to guess at existing patterns, naming conventions, and architecture. Priming reverses this: you [load the relevant context first](context-engineering.md), then ask.

An agent that has read your middleware layer, auth config, and user model before implementing authentication produces output that fits the codebase. Without that context, it produces generic code that defaults to common framework boilerplate rather than project-specific patterns.

## Priming strategies

### Read before write

Have the agent read the files it will touch — and the files adjacent to them — before making any changes. For a new feature, that means existing similar features, the relevant module's entry point, and any shared utilities it will call.

### Progressive context loading

Start broad, then narrow:

1. Architecture overview (AGENTS.md, README, top-level structure)
2. Module or subsystem relevant to the task
3. Specific file(s) to modify

Dumping everything at once is less effective than building understanding incrementally. Language models attend more reliably to content at the start and end of a context window than to content buried in the middle — the [lost-in-the-middle effect](https://arxiv.org/abs/2307.03172). Loading architecture first, then specifics, keeps the most critical framing at the attention-favored start of context rather than interleaved with detail.

### Explore before implement

Use a read-only exploration phase before switching to implementation mode. Some tools support this explicitly — Claude Code's [plan mode](../tools/claude/plan-mode.md) separates reasoning from execution, letting the agent map out its approach before writing any code.

### Use plan mode

When your tool supports it, require a [plan step](../tools/claude/plan-mode.md) before implementation. This forces the agent to surface its understanding of the codebase and the task. Review the plan, correct any misunderstandings, then approve execution. Catching a wrong assumption at plan time costs nothing; catching it after implementation costs a rewrite.

## Anti-patterns

Cold implementation: asking the agent to implement without reading existing code first. The agent defaults to generic patterns rather than project-specific ones.

One-shot context dump: pasting all relevant files into a single prompt. This treats context as a bulk transfer rather than a [structured loading sequence](phase-specific-context-assembly.md). Order within the dump still matters — information at the start and end of a context window receives more attention than information in the middle, a phenomenon documented in [lost-in-the-middle research](https://arxiv.org/abs/2307.03172).

## Example

The following Claude Code session shows progressive context loading before implementing a new authentication endpoint. It builds context broad-to-narrow before making any changes.

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

## Why it works

Transformer models generate each token conditioned on all tokens currently in context — there is no separate "memory" step. When the agent generates code, it pattern-matches against the examples it can see right now. Loading your actual middleware signature, naming conventions, and config shape before the task puts those patterns directly in the distribution the model samples from. That makes project-specific outputs more probable and generic boilerplate less probable. This is the same mechanism that makes [few-shot prompting effective](https://arxiv.org/abs/2005.14165): in-context examples shift output distribution without any weight update. [Repository-level prompt generation research](https://arxiv.org/abs/2206.12839) shows that conditioning code models on relevant repository files measurably improves output fit compared to single-file prompts.

## When this backfires

- Context window saturation: pre-loading large files pushes task instructions and earlier reasoning toward the middle of the context window, where attention degrades. Trim or summarize long files before loading them ([Context Compression Strategies](context-compression-strategies.md)).
- Low-precision context: loading loosely related files adds noise that competes with the relevant signal. If the loaded content does not directly constrain the task output, it can steer the agent toward irrelevant patterns.
- Short, self-contained tasks: for tasks with no codebase dependency — writing a pure-function utility, converting a data format — priming adds latency and [token cost](context-budget-allocation.md) without improving output quality. Apply it selectively.
- Stale context: if loaded files do not reflect the current state of the codebase (out-of-date after a refactor), the agent anchors on the wrong patterns. Verify that primed files are current before loading them.

## FAQ

**Why does loading files before the task change the output at all?**

Transformer models condition each generated token on everything currently in context — there is no separate memory step. Putting your actual middleware signature, naming conventions, and config shape in context makes project-specific outputs more probable and generic boilerplate less probable, the same mechanism that makes [few-shot prompting effective](https://arxiv.org/abs/2005.14165): in-context examples shift the output distribution without any weight update.

**When is priming not worth the tokens?**

On short, self-contained work with no codebase dependency, such as writing a pure-function utility or converting a data format. Priming there adds latency and token cost without improving output quality, so apply it selectively. Large files carry a saturation cost too: trim or summarize them before loading rather than pre-loading them whole.

**What happens if the primed files are out of date?**

The agent anchors on the wrong patterns, reproducing a structure the refactor already replaced, so verify that primed files reflect the current codebase before loading them. Loosely related files cause a milder version of the same problem: content that does not directly constrain the task output adds noise competing with the relevant signal.

## Key Takeaways

- Agents work with what's in context — they don't automatically know your codebase
- Read relevant files first; implement second
- Build context progressively: broad architecture → specific files
- Use [plan mode](../tools/claude/plan-mode.md) to verify the agent's understanding before it acts
- Position critical context at the start of the prompt, not buried in the middle

## Related

- [Context Engineering: The Practice of Shaping Agent Context](context-engineering.md)
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md)
- [Phase-Specific Context Assembly for AI Agent Development](phase-specific-context-assembly.md)
- [Layered Context Architecture for AI Agent Development](layered-context-architecture.md)
- [Retrieval-Augmented Agent Workflows: On-Demand Context](retrieval-augmented-agent-workflows.md)
- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
