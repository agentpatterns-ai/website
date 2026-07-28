---
title: "Context Engineering: Shaping AI Agent Input and Attention"
description: "Techniques for controlling what enters an agent's context window, how it is structured, and what is excluded — for quality, reliability, and cost."
tags:
  - context-engineering
  - index
last_reviewed: 2026-05-27
---

# Context Engineering

> The discipline of designing what information enters a model's context window, how it is structured, and what is excluded — to maximize the quality and reliability of agent output.

## Fundamentals

Core concepts that define context engineering as a practice and establish the structural patterns every other technique builds on.

- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md) — Context engineering is the practice of designing what information enters a model's context window, how it is structured, and what is excluded
- [Context Quality as a Leading Indicator of Agent Reliability](context-quality-audit.md) — Audit an agent's context across seven dimensions to predict where it will drift, hallucinate, misuse tools, or fall to injection before blaming the model
- [Context Priming](context-priming.md) — Load relevant context before asking an agent to act; the order information enters the context window shapes the quality of everything that follows
- [Layered Context Architecture](layered-context-architecture.md) — Ground agents in multiple distinct context sources — schema, code, institutional knowledge, and persistent memory — rather than relying on any single signal
- [Context Budget Allocation](context-budget-allocation.md) — Context is a finite budget; every token preloaded into the context window displaces a token available for reasoning, tool results, and implementation
- [Context Lifecycle Management](context-lifecycle-management.md) — Treat context as a managed lifecycle — decide, extract, store per type, consolidate, compact — rather than a passive store, to curb missing recalls and token cost that grows every turn
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — Only put non-discoverable information in agent instruction files; if the agent can find it in the codebase, let it find it
- [Instruction-Guided Code Completion](instruction-guided-code-completion.md) — Functional correctness and instruction adherence are independent capabilities; explicit implementation constraints and model selection close the gap
- [Re-Auditing Context Engineering Across Model Generations](generation-scoped-context-engineering.md) — Context-engineering best practices are model-generation-dependent; a capability jump lets you delete guardrails the new model no longer needs while keeping the security-critical ones

## Attention & Positioning

Models do not attend uniformly across the context window. These pages cover where attention concentrates, where it drops off, and how to structure content accordingly.

- [Attention Sinks](attention-sinks.md) — Transformer models disproportionately attend to initial tokens regardless of their semantic content; position determines attention weight, not importance
- [Lost in the Middle](lost-in-the-middle.md) — Model attention is strongest at the start and end of a context window; content in the middle receives significantly less focus regardless of its importance
- [Context Window Dumb Zone](context-window-dumb-zone.md) — Output quality degrades as context fills, but the onset depends on task type; retrieval, reasoning, and code generation hit different thresholds
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — Auto-compaction fires at ~95% context fill, long after reasoning quality has degraded; manual compaction reframes context management as reasoning quality preservation
- [Observation Masking](observation-masking.md) — Strip intermediate tool results from conversation history once they have served their purpose to keep active context lean without losing the work product
- [Context Window Anxiety](context-window-anxiety.md) — Advanced models exhibit behavioral shortcuts as context limits approach; strategic buffers, counter-prompting, and token budget transparency counteract premature task closure
- [Turn-Level Context Decisions](turn-level-context-decisions.md) — Every completed turn is a branching point with five options: continue, rewind, clear, compact, or delegate to a subagent; choosing well is the core skill of context management
- [Conversation Registers for AI Coding Sessions](conversation-registers.md) — Name which of four interaction modes you are in with an LLM — exploring, brainstorming, deciding, implementing — and start a fresh context when the register changes

## Compression & Caching

Strategies for fitting more useful content into less space, and for making repeated prefixes cheaper through provider caching mechanisms.

- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md) — Surface which tool calls are inflating the context window so you can optimize specific culprits rather than prune blindly
- [Reducing System-Prompt Token Bloat in Coding Agents](system-prompt-bloat-reduction.md) — Measure the shipped system prompt with `/context`, then switch off unused tools, skills, and features so the fixed prefix stops crowding out task context
- [Proprioceptive Context Dashboard](proprioceptive-context-dashboard.md) — Give a long-horizon agent a live view of its own context blocks — size, age, and usage — so it makes competent keep-or-archive decisions itself instead of a hidden layer compressing blindly
- [PEEK: Orientation Cache for Recurring-Context Agents](peek-orientation-cache.md) — A constant-sized prompt artifact that caches reusable orientation knowledge — what is in a recurring context, how it is organized, which entities matter — distinct from trajectory replay and playbook strategy memory
- [Context Compression Strategies](context-compression-strategies.md) — Long-running agents accumulate context that eventually fills the window; tiered compression — offloading large payloads and summarizing history — lets agents continue working without losing task continuity
- [Selective Rewind Summarization](selective-rewind-summarization.md) — A user-chosen cut point compresses earlier turns to a summary while the recent turns stay verbatim — a targeted alternative to whole-session compaction
- [Usage-Reinforced Memory Decay for Long-Running Agents](usage-reinforced-memory-decay.md) — Score retention with a forgetting curve whose stability compounds on every recall, so frequently-consulted facts outlive the idle stretches that silently evict them from a fixed recency window
- [Agent-Initiated Rubric-Gated Self-Compaction](agent-initiated-self-compaction.md) — Give the agent both a compaction tool and a firing rubric so it compacts on trajectory structure — sub-task resolved or converging — instead of a fixed token threshold
- [Version-Controlled Agent Context](version-controlled-agent-context.md) — Commit, branch, merge, and read agent memory as a durable file tree so the abstraction level is chosen at read time; the retrieval path carries the benefit, not the checkpoints
- [Elastic Context Orchestration](elastic-context-orchestration.md) — A per-turn vocabulary of context operations — Skip, Compress, Snippet, Rollback, Delete — that lets long-horizon search agents tier retention by current task relevance instead of accumulating raw trajectory
- [Prompt Compression](prompt-compression.md) — Write instructions that convey the same guidance in fewer words; shorter, denser instructions improve agent compliance and reduce token cost
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — Treat prompt caching as a structural constraint on prompt composition, with cross-provider economics and extended-TTL guidance folded in
- [Static Content First for Cache Hits](static-content-first-caching.md) — Place static content at the beginning of the prompt and variable content at the end to maximize prompt cache hits and keep inference costs linear
- [Prompt Cache Keepalive for Agent Pauses](prompt-cache-keepalive-agent-pauses.md) — Replay a cached prefix on a timer so it survives tool runs and approval waits, and the billing, pause-length, and interval conditions that decide whether it saves money or costs 4x more
- [Stateful Iteration State-Carry](stateful-iteration-state-carry.md) — Carry typed persistent state across long agent loops through a state-read tool instead of replaying the full transcript each turn; converts O(n²) total token cost to O(n) when loops are long and observations are large
- [Exclude Dynamic System Prompt Sections for Cross-Machine Cache Sharing](exclude-dynamic-system-prompt-sections.md) — Move per-machine context (cwd, OS, shell, memory paths) out of the Claude Code system prompt so identical fleet configurations share one prompt-cache entry across users and machines
- [KV Cache Invalidation in Local Inference](kv-cache-invalidation-local-inference.md) — When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference
- [Semantic Density Optimization](semantic-density-optimization.md) — Maximize task-relevant tokens in a codebase by eliminating zero-information ceremony while preserving naming, documentation, and commit context that agents cannot reconstruct without inference cost
- [Validating Token-Optimized Formats Inside Agentic Loops](validate-token-optimized-formats-in-agentic-loops.md) — Switching tool schemas from JSON to TOON or TRON saves up to 27% tokens but regresses accuracy by 9-14 percentage points in end-to-end agentic loops; input-side and output-side compression carry different risk
- [Source Code Minification for State-in-Context Agents](source-code-minification-trade-off.md) — Stripping comments, whitespace, and shortening identifiers cuts input tokens 42% but drops SWE-bench Verified resolution rate from 50% to 38% — apply only when measured savings beat the accuracy cost
- [Cross-Lingual Prompt Preprocessing (Local-LLM Token Arbitrage)](cross-lingual-prompt-preprocessing.md) — A local small model translates non-English prompts to English and rewrites them into compact task-oriented form before send; cuts input tokens 34–47% only when latency, accuracy, and fidelity costs do not erase the savings

## Assembly & Composition

How to build, layer, and route context to the right agent at the right time rather than dumping everything into a single prompt.

- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md) — Build system prompts from modular, priority-ordered sections rather than monolithic static text, enabling mode-specific variants and efficient API caching
- [Narrative Problem Reformulation for Code Generation](narrative-problem-reformulation.md) — Rewriting a fragmented coding problem as a coherent three-part narrative measurably shifts which algorithms a code LLM selects, with reported 18.7% zero-shot pass@10 gains concentrated on harder competitive-programming tasks
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md) — Optimize the orchestration layer that prepares each agent per phase; planners get summaries, workers get targeted file excerpts and validation commands
- [Prompt Chaining](prompt-chaining.md) — Decompose a complex task into a sequence of LLM calls where each step processes the output of the previous one, enabling verification and gate-checking at each stage
- [Prompt Layering](prompt-layering.md) — Agent instructions arrive from multiple sources simultaneously; understanding the precedence order and conflict resolution prevents unpredictable behavior
- [Filter and Aggregate in the Execution Environment](filter-aggregate-execution-env.md) — Run data processing logic inside the code execution sandbox before surfacing results to the model, so only the relevant subset of data enters context
- [Evolving Playbooks](evolving-playbooks.md) — Replace monolithic prompt rewrites with structured delta entries that accumulate, refine, and organize agent strategies without losing domain knowledge

## Loading & Retrieval

Techniques for getting the right context into an agent on demand, whether from code repositories, APIs, or structured knowledge bases.

- [Context Hub](context-hub.md) — Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data snapshots
- [Codebase-Derived Pattern Libraries as Agent Context](codebase-pattern-library-context.md) — Mine your own repositories for proven implementations and serve them to an agent as intent-searchable context instead of generic public examples
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — Pull context into the agent at the moment it is needed rather than preloading it at session start
- [Live Browser as Agent Context Channel](live-browser-context-channel.md) — Subscribe an agent to the developer's running browser tabs as live context — lower friction than copy-paste, but the developer's logged-in session enters the indirect-injection blast radius
- [App-Window Snapshot as Agent Context](app-window-snapshot-context.md) — Bind one hotkey to send the active app window — rendered screenshot plus accessibility-tree text — as a single context unit; the richer payload changes which cross-app handoffs are plausible to delegate
- [Repository Map Pattern](repository-map-pattern.md) — Parse source files with tree-sitter to extract structural symbols, rank them by graph importance, then binary-search fit the most relevant entries into the agent's available token budget
- [Deterministic Anchoring](deterministic-anchoring.md) — Inject call-graph, inheritance, and config-dependency facts as plain-text comments so code-agent navigation converges run-to-run; the win is reproducibility, not capability
- [Semantic Context Loading](semantic-context-loading.md) — Query codebases through Language Server Protocol semantics — symbol lookup, reference finding, type navigation — rather than reading raw files
- [Seeding Agent Context](seeding-agent-context.md) — Strategically place files, comments, and markers that agents discover during exploration and use to shape their behavior
- [Grounding Agents in Code the Model Has Never Seen](grounding-zero-prior-code.md) — When the model has no training signal for a proprietary SDK or custom framework, it generates against the closest public API in training; provisioning must displace that prior, not just supplement it
- [Environment Specification as Context](environment-specification-as-context.md) — Feed dependency versions, lock files, and runtime constraints into agent context to prevent the 50–70% accuracy drop caused by environment-blind code generation
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — AI coding agents that retrieve cross-file context from dependency graphs, ASTs, and semantic embeddings generate more accurate code than those limited to local file context
- [Agent-Tuned Code Search](agent-tuned-code-search.md) — A search tool that runs its own loop and returns file paths plus line ranges cuts search latency sharply, but the token win against local grep is modest and bounded by index freshness
- [AOCI: Symbolic-Semantic Repository Indexing](aoci-symbolic-semantic-indexing.md) — A persistent, query-independent blueprint pairing architectural coordinates with semantic content — read whole before any task, distinct from on-demand retrieval and token-fitted repo maps
- [Structured Domain Retrieval](structured-domain-retrieval.md) — Combine hierarchical knowledge graphs with coverage-driven case selection to retrieve domain-specific context that flat vector search misses
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — Use one shared domain schema across graph construction, query decomposition, and typed retrieval to improve multi-hop reasoning precision over private knowledge bases
- [Chunking Strategy for RAG-Based Code Completion](chunking-strategy-rag-code-completion.md) — Function-based chunking is dominated by every other strategy on line-level code completion; Sliding Window and cAST sit on the Pareto frontier, and doubling cross-file context length matters more than chunking choice
- [Component-Wise RAG Prioritization](rag-component-prioritization-software-engineering.md) — A 21+ model component-wise empirical study finds retriever choice dominates generator choice for SE-task RAG, and BM25 is robust across code generation, summarization, and repair — under specific conditions
- [LLM-Driven Logical Retrieval](llm-driven-logical-retrieval.md) — When the agent LLM is frontier-capable, letting it emit AND/OR/NOT Boolean queries against an inverted index matches an agentic hybrid baseline at 41× lower indexing cost — under specific lexical-overlap conditions
- [Compositional Skill Routing](compositional-skill-routing.md) — Decompose a query into atomic sub-tasks, retrieve one skill per sub-task, then compose the plan — earns its cost only above hundreds of skills, where decomposition quality caps the system
- [Skill Loadout Curation for Coding Agents](skill-loadout-curation.md) — Curate the skills and MCP servers an agent loads before a session; above roughly 30 skills the gain comes from removing colliding descriptions, not from saving tokens

## Error Handling & Drift Prevention

Keeping agents on track across long sessions by preserving failure signals and reinforcing goals.

- [Context-Injected Error Recovery](context-injected-error-recovery.md) — When a tool call fails, inject structured error context into the next inference call to prevent retry loops before they form
- [Error Preservation in Context](error-preservation-in-context.md) — Keep failed actions and error traces visible in the agent's context window; error history acts as negative examples that shift model behavior
- [Goal Recitation](goal-recitation.md) — Periodically rewrite objectives, to-do lists, and status summaries at the tail of context to exploit recency bias and prevent goal drift in long-running sessions
