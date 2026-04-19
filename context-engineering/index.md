---
title: "Context Engineering: Shaping AI Agent Input and Attention"
description: "Techniques for controlling what enters an agent's context window, how it is structured, and what is excluded — for quality, reliability, and cost."
tags:
  - context-engineering
---

# Context Engineering

> The discipline of designing what information enters a model's context window, how it is structured, and what is excluded — to maximise the quality and reliability of agent output.

## Fundamentals

Core concepts that define context engineering as a practice and establish the structural patterns every other technique builds on.

- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md) — Context engineering is the practice of designing what information enters a model's context window, how it is structured, and what is excluded
- [Context Priming](context-priming.md) — Load relevant context before asking an agent to act; the order information enters the context window shapes the quality of everything that follows
- [Layered Context Architecture](layered-context-architecture.md) — Ground agents in multiple distinct context sources — schema, code, institutional knowledge, and persistent memory — rather than relying on any single signal
- [Context Budget Allocation](context-budget-allocation.md) — Context is a finite budget; every token preloaded into the context window displaces a token available for reasoning, tool results, and implementation
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — Only put non-discoverable information in agent instruction files; if the agent can find it in the codebase, let it find it
- [Instruction-Guided Code Completion](instruction-guided-code-completion.md) — Functional correctness and instruction adherence are independent capabilities; explicit implementation constraints and model selection close the gap

## Attention & Positioning

Models do not attend uniformly across the context window. These pages cover where attention concentrates, where it drops off, and how to structure content accordingly.

- [Attention Sinks](attention-sinks.md) — Transformer models disproportionately attend to initial tokens regardless of their semantic content; position determines attention weight, not importance
- [Lost in the Middle](lost-in-the-middle.md) — Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance
- [Context Window Dumb Zone](context-window-dumb-zone.md) — Output quality degrades as context fills, but the onset depends on task type; retrieval, reasoning, and code generation hit different thresholds
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — Auto-compaction fires at ~95% context fill, long after reasoning quality has degraded; manual compaction reframes context management as reasoning quality preservation
- [Observation Masking](observation-masking.md) — Strip intermediate tool results from conversation history once they have served their purpose to keep active context lean without losing the work product
- [Context Window Anxiety](context-window-anxiety.md) — Advanced models exhibit behavioral shortcuts as context limits approach; strategic buffers, counter-prompting, and token budget transparency counteract premature task closure
- [Turn-Level Context Decisions](turn-level-context-decisions.md) — Every completed turn is a branching point with five options: continue, rewind, clear, compact, or delegate to a subagent; choosing well is the core skill of context management

## Compression & Caching

Strategies for fitting more useful content into less space, and for making repeated prefixes cheaper through provider caching mechanisms.

- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md) — Surface which tool calls are inflating the context window so you can optimize specific culprits rather than prune blindly
- [Context Compression Strategies](context-compression-strategies.md) — Long-running agents accumulate context that eventually fills the window; tiered compression — offloading large payloads and summarising history — lets agents continue working without losing task continuity
- [Prompt Compression](prompt-compression.md) — Write instructions that convey the same guidance in fewer words; shorter, denser instructions improve agent compliance and reduce token cost
- [Prompt Cache Economics](prompt-cache-economics.md) — Prompt caching discounts range from 50% to 90% depending on the provider, but each has different activation rules, TTLs, and hidden costs
- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md) — Treat prompt caching as a structural constraint that shapes how you compose, extend, and compact agent context, not as an optimization you toggle on after the fact
- [Static Content First for Cache Hits](static-content-first-caching.md) — Place static content at the beginning of the prompt and variable content at the end to maximize prompt cache hits and keep inference costs linear
- [KV Cache Invalidation in Local Inference](kv-cache-invalidation-local-inference.md) — When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference
- [Token-Efficient Code Generation](token-efficient-code-generation.md) — Reduce token cost of AI-generated code through idiomatic syntax patterns and structural optimization rather than prompt-level efficiency instructions
- [Semantic Density Optimization](semantic-density-optimization.md) — Maximize task-relevant tokens in a codebase by eliminating zero-information ceremony while preserving naming, documentation, and commit context that agents cannot reconstruct without inference cost

## Assembly & Composition

How to build, layer, and route context to the right agent at the right time rather than dumping everything into a single prompt.

- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md) — Build system prompts from modular, priority-ordered sections rather than monolithic static text, enabling mode-specific variants and efficient API caching
- [Narrative Problem Reformulation for Code Generation](narrative-problem-reformulation.md) — Rewriting a fragmented coding problem as a coherent three-part narrative measurably shifts which algorithms a code LLM selects, with reported 18.7% zero-shot pass@10 gains concentrated on harder competitive-programming tasks
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md) — Optimise the orchestration layer that prepares each agent per phase; planners get summaries, workers get targeted file excerpts and validation commands
- [Prompt Chaining](prompt-chaining.md) — Decompose a complex task into a sequence of LLM calls where each step processes the output of the previous one, enabling verification and gate-checking at each stage
- [Prompt Layering](prompt-layering.md) — Agent instructions arrive from multiple sources simultaneously; understanding the precedence order and conflict resolution prevents unpredictable behavior
- [Filter and Aggregate in the Execution Environment](filter-aggregate-execution-env.md) — Run data processing logic inside the code execution sandbox before surfacing results to the model, so only the relevant subset of data enters context
- [Evolving Playbooks](evolving-playbooks.md) — Replace monolithic prompt rewrites with structured delta entries that accumulate, refine, and organize agent strategies without losing domain knowledge

## Loading & Retrieval

Techniques for getting the right context into an agent on demand, whether from code repositories, APIs, or structured knowledge bases.

- [Context Hub](context-hub.md) — Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data snapshots
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — Pull context into the agent at the moment it is needed rather than preloading it at session start
- [Repository Map Pattern](repository-map-pattern.md) — Parse source files with tree-sitter to extract structural symbols, rank them by graph importance, then binary-search fit the most relevant entries into the agent's available token budget
- [Semantic Context Loading](semantic-context-loading.md) — Query codebases through Language Server Protocol semantics — symbol lookup, reference finding, type navigation — rather than reading raw files
- [Seeding Agent Context](seeding-agent-context.md) — Strategically place files, comments, and markers that agents discover during exploration and use to shape their behaviour
- [Environment Specification as Context](environment-specification-as-context.md) — Feed dependency versions, lock files, and runtime constraints into agent context to prevent the 50–70% accuracy drop caused by environment-blind code generation
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — AI coding agents that retrieve cross-file context from dependency graphs, ASTs, and semantic embeddings generate more accurate code than those limited to local file context
- [Structured Domain Retrieval](structured-domain-retrieval.md) — Combine hierarchical knowledge graphs with coverage-driven case selection to retrieve domain-specific context that flat vector search misses
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — Use one shared domain schema across graph construction, query decomposition, and typed retrieval to improve multi-hop reasoning precision over private knowledge bases

## Error Handling & Drift Prevention

Keeping agents on track across long sessions by preserving failure signals and reinforcing goals.

- [Context-Injected Error Recovery](context-injected-error-recovery.md) — When a tool call fails, inject structured error context into the next inference call to prevent retry loops before they form
- [Error Preservation in Context](error-preservation-in-context.md) — Keep failed actions and error traces visible in the agent's context window; error history acts as negative examples that shift model behavior
- [Goal Recitation](goal-recitation.md) — Periodically rewrite objectives, to-do lists, and status summaries at the tail of context to exploit recency bias and prevent goal drift in long-running sessions
