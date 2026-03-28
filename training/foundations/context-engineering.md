---
title: "Context Engineering: Designing for Reliable Agent Output"
description: "Context engineering is the discipline of designing what enters a model context window, how it is structured, and what is excluded to maximise reliability."
tags:
  - training
  - context-engineering
  - tool-agnostic
---
# Context Engineering

> The discipline of designing what enters a model's context window, how it is structured, and what is excluded — to maximise output quality and reliability.

Context windows have structural and economic properties that determine whether an agent produces reliable output or drifts into incoherence. Attention is not uniform — it follows a U-shaped curve. Tokens are not free — every preloaded token displaces one available for reasoning. Compression is not optional — long sessions demand it. This module covers these mechanics and the engineering strategies that exploit them, regardless of which tool you use.

---

## Context Engineering vs Prompt Engineering

Prompt engineering is writing a good instruction. Context engineering is designing the entire information environment the agent operates in — the system prompt, project instructions, tool outputs, conversation history, and file contents that collectively form the agent's world. [Anthropic frames this](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) as finding "the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."

The distinction matters because a well-crafted prompt in a poorly structured context produces inconsistent results. A mediocre prompt in a well-engineered context produces good results reliably. Context engineering subsumes prompt engineering, [skill design](../../context-engineering/context-engineering.md), agent architecture, and memory management.

For the full conceptual framework, see [Context Engineering: The Discipline of Designing Agent Context](../../context-engineering/context-engineering.md).

---

## How Transformer Attention Shapes Output

Two structural properties of transformer attention determine where to place information in a context window.

### Attention sinks

Initial tokens receive disproportionate attention regardless of their semantic content. This is a structural property of causal attention masking, not a quirk of any particular model. Whatever role, persona, or constraint appears at the very beginning of a system prompt receives stronger model attention than the same constraint placed later. Boilerplate metadata or generic preamble at the top of an instruction file wastes the highest-attention positions on low-value content. See [Attention Sinks: Why First Tokens Always Win](../../context-engineering/attention-sinks.md).

### The U-shaped attention curve

Model attention follows a U-shape: strongest at the start and end of the context, weakest in the middle. Content that must be reliably followed belongs at the edges. Content the agent refers to passively — schemas, examples, lookup information — can tolerate mid-context placement because the agent actively retrieves it rather than relying on passive recall.

The practical consequence: a long instruction file buries most of its rules in the zone where they are least likely to be followed. Each instruction added to the middle pushes existing instructions further from the high-attention edges. See [Lost in the Middle: The U-Shaped Attention Curve](../../context-engineering/lost-in-the-middle.md).

**Applying both properties together**: open instruction files with your most critical constraint. Close with a restated reminder of the same constraint. Reserve the middle for reference material.

---

## Context as a Finite Budget

A 200K token context window sounds large. Load a system prompt, project instructions, skill definitions, and reference files, and the agent may start a task with most of its budget already consumed. The remaining tokens must cover tool calls, intermediate reasoning, file reads, and implementation — and that budget shrinks further as the conversation accumulates turns.

[Anthropic describes](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) this as an attention budget: the quadratic cost of token-pair relationships means a fully packed context is computationally thinner. Every token preloaded into context displaces a token available for work.

### Preload vs on-demand loading

Two strategies manage this budget:

| | Preload (always-on) | On-demand (JIT) |
|-|---------------------|-----------------|
| **Latency** | Zero | One tool call |
| **Context cost** | Paid on every task | Paid only when used |
| **Best for** | Always-needed context (role, constraints) | Conditionally-needed context (skill content, file reads) |

[Anthropic describes JIT loading](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) as maintaining lightweight identifiers in the always-on layer and loading actual data dynamically when needed. Preload what every task needs; load everything else on-demand.

### Sub-agents as budget isolation

Each sub-agent runs in its own context window. A research sub-agent can read 50 files without that overhead appearing in the coordinator's context. [Anthropic identifies](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) sub-agent architectures as one of three complementary approaches — alongside compaction and structured note-taking — for managing context across long-horizon tasks.

For the full budget framework including anti-patterns, see [Context Budget Allocation: Every Token Has a Cost](../../context-engineering/context-budget-allocation.md).

---

## Compression Strategies

Long-running agents accumulate context that eventually fills the window. Without compression, the session fails or truncates arbitrarily. Two tiers apply in sequence.

**Tier 1 — Offload large tool responses.** Replace large payloads (full files, API responses) with a filesystem reference and brief summary. The full content is written to disk; the agent re-reads it when needed. [LangChain's Deep Agents framework](https://blog.langchain.com/context-management-for-deepagents/) implements this as the first compression stage.

**Tier 2 — Summarise conversation history.** When context fills further, summarise prior turns. Effective summaries preserve the current objective, key artifacts, decisions and rationale, and next steps. [Anthropic's context engineering guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) identifies this as "compaction." The risk: summaries that capture only "what happened" without "what matters next" cause [objective drift](../../anti-patterns/objective-drift.md).

More graduated approaches exist. The [OPENDEV framework](https://arxiv.org/abs/2603.05344) implements five-stage Adaptive Context Compaction, triggered at specific budget thresholds from 70% to 99%, degrading gracefully rather than hitting a single compression cliff.

For implementation details and the full five-stage pipeline, see [Context Compression Strategies: Offloading and Summarisation](../../context-engineering/context-compression-strategies.md).

---

## Dynamic Context Assembly

Static system prompts break down as agent capabilities grow. Every conversation pays the token cost for every section, regardless of relevance.

### Modular prompt composition

Assemble system prompts at runtime from priority-ordered modular sections. Toggle sections by execution mode — a planning-mode prompt omits code quality rules; an execution-mode prompt omits strategic reasoning scaffolds. Inject provider-specific blocks conditionally to avoid cross-provider [prompt bloat](../../anti-patterns/prompt-tinkerer.md). The [OPENDEV paper](https://arxiv.org/abs/2603.05344) describes this as modular prompt composition with five functional tiers. See [Dynamic System Prompt Composition](../../context-engineering/dynamic-system-prompt-composition.md).

### Phase-specific context

Different workflow phases have structurally different context needs. A planner needs architecture summaries and constraints. A worker needs the approved plan, exact file excerpts, and validation commands. A reviewer needs the original spec, the diff, and acceptance criteria. Giving all agents the same context bundle is a common source of inconsistency.

The shift: from "what instructions should the agent follow?" to "what information does this agent need, and only this agent, at this step?" See [Phase-Specific Context Assembly](../../context-engineering/phase-specific-context-assembly.md).

---

## Prompt Caching as Architectural Discipline

Prompt caching reuses KV cache representations of previously computed tokens. Cached reads cost [10% of the base input price on Anthropic's API](https://platform.claude.com/docs/en/build-with-claude/prompt-caching); cache misses cost 100%. [Manus reports](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) that KV-cache hit rate is "the single most important metric for a production-stage AI agent."

The architectural constraint: a stable prefix followed by a growing tail. System prompt, tool definitions, and project instructions form the cacheable prefix. Conversation history occupies the dynamic suffix. Any change to the prefix — adding tools mid-session, switching models, injecting timestamps — invalidates the cache for everything after it.

Three patterns consistently bust the cache:

1. **Adding or removing tools mid-session.** Tool definitions sit in the prefix; changing them invalidates everything after.
2. **Switching models.** Model-specific instructions in the prefix change, breaking the byte-level match.
3. **Mutating the prefix to convey state.** Timestamps, config, or metadata in early sections bust the cache on every call.

For the full immutable prefix pattern and cache-safe compaction, see [Prompt Caching as Architectural Discipline](../../context-engineering/prompt-caching-architectural-discipline.md). For cost comparisons across Anthropic, OpenAI, and Gemini, see [Prompt Cache Economics](../../context-engineering/prompt-cache-economics.md). For ordering rules and common cache-busting bugs, see [Static Content First: Maximizing Prompt Cache Hits](../../context-engineering/static-content-first-caching.md).

---

## Seeding Agent Context

Agents explore codebases by reading files. What they find determines what they do. Seeding shifts context management from a per-session concern to a codebase hygiene concern.

Four techniques embed [discoverable context](../../context-engineering/discoverable-vs-nondiscoverable-context.md) where agents encounter it naturally:

1. **Directory-scoped instruction files** (AGENTS.md, CLAUDE.md) — scope conventions to where they apply. Subdirectory files override or extend project-level instructions.
2. **Inline decision comments** — explain *why* a decision was made, preventing agents from reverting intentional choices.
3. **Type annotations** — eliminate agent guesswork about return types, parameter shapes, and nullability.
4. **Example files** — agents pattern-match against existing code. A reference implementation communicates conventions more precisely than prose.

The rule of thumb: seed durable information in the codebase; prompt session-specific intent interactively. See [Seeding Agent Context: Breadcrumbs in Code](../../context-engineering/seeding-agent-context.md).

---

## Key Takeaways

- The context window is the agent's complete world. What is not in it does not exist for the agent. Optimise for signal density, not volume.
- Attention follows a U-shape: critical rules belong at the start and end of instruction files. The middle is for reference material, not rules.
- Context is a budget. Every preloaded token displaces a token available for reasoning and implementation. Preload only what every task needs; load everything else on-demand.
- Compression preserves task continuity in long sessions. Summaries must retain the objective, decisions, and next steps — not just action history.
- Assemble context dynamically per phase and per mode. A planner, a worker, and a reviewer need different context bundles, not the same monolithic prompt.
- Prompt caching is a structural constraint, not an afterthought. Stable prefix first, dynamic content last. Monitor cache hit rates — misses are silent.
- Seed durable conventions into the codebase where agents discover them naturally. Session-specific intent belongs in the prompt.

## Related

**Source pages**

- [Context Engineering: The Discipline of Designing Agent Context](../../context-engineering/context-engineering.md)
- [Attention Sinks: Why First Tokens Always Win](../../context-engineering/attention-sinks.md)
- [Lost in the Middle: The U-Shaped Attention Curve](../../context-engineering/lost-in-the-middle.md)
- [Context Budget Allocation: Every Token Has a Cost](../../context-engineering/context-budget-allocation.md)
- [Context Compression Strategies: Offloading and Summarisation](../../context-engineering/context-compression-strategies.md)
- [Dynamic System Prompt Composition](../../context-engineering/dynamic-system-prompt-composition.md)
- [Phase-Specific Context Assembly](../../context-engineering/phase-specific-context-assembly.md)
- [Seeding Agent Context: Breadcrumbs in Code](../../context-engineering/seeding-agent-context.md)
- [Prompt Caching as Architectural Discipline](../../context-engineering/prompt-caching-architectural-discipline.md)
- [Static Content First: Maximizing Prompt Cache Hits](../../context-engineering/static-content-first-caching.md)
- [Prompt Cache Economics: Comparing Costs by Provider](../../context-engineering/prompt-cache-economics.md)

**Training modules**

- [Prompt Engineering](prompt-engineering.md)
- [Harness Engineering](harness-engineering.md)
- [Tool Engineering](tool-engineering.md)
- [Eval Engineering](eval-engineering.md)
- [How the Four Disciplines Compound](prompt-context-harness-capstone.md)
- [GitHub Copilot: Context Engineering & Agent Workflows](../copilot/context-and-workflows.md)
