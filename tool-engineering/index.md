---
title: "Tool Engineering: Designing and Managing AI Agent Tooling"
description: "Design, expose, and manage the tools agents use — description quality, schema design, MCP servers, skills, hooks, and specialized patterns."
tags:
  - agent-design
  - tool-engineering
  - index
last_reviewed: 2026-05-27
---
# Tool Engineering

> Design, expose, and manage the tools that agents use to act on the world -- from description quality and schema design through MCP servers, skills, hooks, and specialized tool patterns.

## Fundamentals

Core principles for designing agent tools that are discoverable, unambiguous, and cost-effective.

- [Tool Engineering](tool-engineering.md) — Design agent tools like APIs -- with documentation, examples, edge-case handling, and mistake-proofing -- not as boilerplate wrappers around existing functions
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — Expose fewer, non-overlapping tools and provide goal-oriented instructions rather than step-by-step procedures
- [Tool Description Quality](tool-description-quality.md) — Tool descriptions -- not just implementations -- determine whether agents select the right tool; treat them as prompt engineering surfaces
- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md) — Write tool descriptions assuming the agent has never seen the system -- include implicit context, query syntax, domain terms, and resource relationships
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md) — Three API-level features for managing hundreds of tools without drowning in context or losing selection accuracy

## Tool Design

Structural patterns for tool interfaces, schemas, error handling, and output formatting.

- [Designing for Agent Consumers (Agent Experience)](designing-for-agent-consumers.md) — Treat the agent as a first-class consumer of your public SDK, CLI, API, and docs; the AX discipline that routes the surface-design tactics, distinct from harness engineering
- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — Tools are the agent's UI; the same principles that make human interfaces usable make agent tools effective
- [Function-Level Debugger Interfaces for Coding Agents](function-level-debugger-interfaces.md) — Re-expose interactive debuggers at the function frame instead of the source line so LLM agents pay one turn per call, not one turn per step
- [Semantic Tool Output](semantic-tool-output.md) — Return human-readable, contextually filtered output from agent tools to reduce hallucination and improve downstream call accuracy
- [Typed Schemas at Agent Boundaries](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md) — Formal schemas at every agent-to-agent interface establish explicit contracts that prevent state mismanagement and silent failures
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — Redesign tool interfaces so the wrong call cannot compile -- prevention over documentation
- [Consolidate Agent Tools](consolidate-agent-tools.md) — Prefer fewer, higher-level tools that match how agents reason about tasks over many narrow tools that mirror API endpoint boundaries
- [Toolset Agentization](toolset-agentization.md) — Group frequently co-used tools into specialized sub-agents so the top-level planner chooses among fewer, coarser actions at each routing step
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md) — Request structured errors from HTTP APIs using Accept headers to replace brittle HTML parsing with deterministic control flow
- [Headless-First Services: APIs for Agent Consumers](headless-first-services.md) — Expose the full product surface through API, MCP, and CLI so agents acting on behalf of users can complete any flow the GUI supports
- [Tool Necessity Probing](tool-necessity-probing.md) — Read tool-call decisions from the pre-generation hidden state with a linear probe — AUROC 0.89–0.96, 48% fewer tool calls at 1.7% accuracy loss
- [Chance-Corrected Shortlist Depth Sizing](chance-corrected-shortlist-depth-sizing.md) — Bits-over-Random measures whether retrieval at depth K beats random at depth K; the missing chance-corrected metric for sizing fixed or adaptive tool-retrieval shortlists

## MCP (Model Context Protocol)

Architecture and design guidance for MCP servers and clients -- the open protocol for agent-tool communication.

- [MCP Client/Server Architecture](mcp-client-server-architecture.md) — Architectural best practices covering transport selection, tool granularity, error handling, capability negotiation, and security
- [MCP Client Design](mcp-client-design.md) — Host-side logic for connecting to servers, negotiating capabilities, routing tool calls, caching descriptions, and degrading gracefully on failure
- [MCP Elicitation](mcp-elicitation.md) — How MCP servers collect structured user input mid-task, and how Elicitation and ElicitationResult hooks let you automate, validate, or block those requests
- [MCP LLM Sampling](mcp-llm-sampling.md) — How MCP servers request host LLM inference mid-execution via sampling/createMessage, creating hybrid tools that combine deterministic logic with embedded AI reasoning
- [MCP Server Design](mcp-server-design.md) — A server author's checklist for tool naming, schema design, error handling, resource exposure, and token efficiency
- [Production MCP Agent Stack](production-mcp-agent-stack.md) — Sequence six MCP decisions -- server location, tool grouping, schema delivery, result processing, auth, token storage -- into a coherent production deployment
- [MCP Tool Result Persistence via _meta Annotation](mcp-result-persistence-annotation.md) — Mark individual MCP tool outputs as durable through Claude Code's compaction pipeline with `_meta["anthropic/maxResultSizeChars"]`
- [Proprietary-to-Open-Standard Migration](copilot-extensions-to-mcp-migration.md) — When a proprietary extension system gets replaced by an open protocol, rebuild on the standard rather than port the old architecture
- [Scoped MCP Server Discovery: Most-Specific-Wins Resolution](scoped-mcp-server-discovery.md) — Resolve duplicate MCP server definitions across user, workspace, and project config files using a most-specific-wins precedence rule
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](mcp-eager-vs-jit-loading.md) — Decide which MCP servers earn unconditional context residence and which stay deferred behind tool search, using token cost, hit rate, and selection accuracy as signals
- [Documentation-Grounding MCP Servers for Vendor SDKs](documentation-grounding-mcp-servers.md) — Wire a vendor's docs-MCP endpoint to ground code generation in current API surfaces, only when SDK churn, token budget, and trifecta posture all permit it
- [Tool Cloning and Provenance Assessment](tool-cloning-provenance-assessment.md) — Raw repository counts overstate the diversity of MCP and Skills marketplaces because many entries are cloned, lightly modified, or template-derived — pair Jaccard and ssdeep before drawing ecosystem conclusions
- [Hint-Driven Concurrency for Read-Only MCP Tools](read-only-hint-concurrency.md) — The MCP `readOnlyHint` annotation became a concurrency dispatcher input once Codex CLI 0.134.0 shipped parallel execution for read-only tool calls — a wall-clock win that only holds when annotations are audited and trusted
- [Push-Event MCP Channels: Inverting the Pull-Tool Polarity](push-event-mcp-channels.md) — An MCP server that declares `claude/channel` flips the polarity from pull-on-demand to push-when-it-happens, gated by sender allowlist and an always-open session — useful when warm context is worth keeping
- [Auth-Isolation as the MCP-vs-CLI Selection Heuristic](mcp-auth-isolation-vs-cli-selection.md) — Reach for MCP when authenticated access needs its credentials kept out of the agent's context window; choose a CLI when there is no auth boundary to protect

## Skills

Packaging domain knowledge and reusable capabilities as agent skills with reliable invocation and lifecycle governance.

- [Skill as Knowledge Pattern](skill-as-knowledge.md) — Design skills as pure knowledge containers -- domain rules, heuristics, and reference material -- not executable behavior, so they remain portable across agents
- [CLI-First Skill Design](cli-first-skill-design.md) — Design agent skills as CLI tools so the same interface serves both humans debugging locally and agents automating through shell tool calls
- [Skill Authoring Patterns](skill-authoring-patterns.md) — Practical patterns for building, testing, and troubleshooting agent skills -- categories, description craft, implementation patterns, and debugging
- [Skill Authoring as Software Engineering: What Transfers](skill-authoring-software-engineering.md) — Which software-engineering principles survive contact with measurement when authoring skills, and the two questions that decide skill versus hook
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md) — All SKILL.md frontmatter fields: invocation control, subagent delegation, tool restriction, hooks, and argument handling
- [Listener-State Naming for User-Invoked Agent Skills](listener-state-skill-naming.md) — Name a user-invoked skill after the reader's failure state rather than the output shape, so the agent adds the missing premise instead of deleting words
- [Skill Context Isolation](skill-context-isolation.md) — Run a skill in an isolated subagent context so its auxiliary tokens never enter the main chat; the parent receives only the distilled result
- [Skill Library Evolution](skill-library-evolution.md) — How agent skill libraries grow, get pruned, and evolve through versioning, quality gates, and lifecycle governance
- [Skill Reuse as Vendored Forking](skill-reuse-as-vendored-forking.md) — Reusing a SKILL.md is a one-time near-verbatim copy that silently forks from its source; bind project specifics at adoption and track upstream only where the contract is coupled to a moving source
- [Skill Tool Runtime Enforcement](skill-tool-runtime-enforcement.md) — Use the Skill tool to load command prompts at invocation time rather than telling agents to read the file -- eliminates stale instructions and path drift
- [Google ADK Skills](adk-skills.md) — How Google ADK implements the Agent Skills standard via SkillToolset, inline `models.Skill`, and three auto-generated tools mapped to L1/L2/L3 progressive disclosure
- [Interpreter Skills](interpreter-skills.md) — Ship a SKILL.md plus an importable module so the model decides when the behavior fires while the runtime executes a reviewed, testable function — the named, versionable unit on top of an embedded code interpreter
- [Generated Procedure Drivers: Skills That Emit a Program](generated-procedure-drivers.md) — A skill whose output is an executable script that walks a person through a manual procedure, useful only where automation genuinely stops

## Hooks & Lifecycle

Deterministic interception points that enforce policy, automate side effects, and audit agent behavior without relying on model compliance.

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md) — Hooks run deterministic code at defined points in an agent's execution -- before and after tool calls, at session boundaries -- enabling enforcement and audit
- [Conditional Hook Execution](conditional-hook-execution.md) — Use the `if` field on hook handlers to filter by tool name and arguments, eliminating subprocess spawns for non-matching calls
- [Hook Catalog](hook-catalog.md) — A reference catalog of high-value hooks grouped by purpose: CLI enforcement, destructive operation guardrails, sandboxing, and workflow automation
- [On-Demand Skill Hooks](on-demand-skill-hooks.md) — Register PreToolUse hooks through a skill invocation to arm strict guardrails for a single session without imposing friction on every workflow
- [PostToolUse BSD/GNU Detection](posttooluse-bsd-gnu-detection.md) — Catch BSD/GNU CLI incompatibilities at runtime with a PostToolUse hook, feed fixes back via additionalContext, and persist knowledge to CLAUDE.md
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md) — The StopFailure hook fires when a Claude Code turn ends due to an API error, giving harnesses a deterministic signal to log failures, alert operators, and feed external recovery workflows
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md) — Claude Code's PreCompact hook can now block compaction outright, deferring context compression until the agent reaches a safer checkpoint
- [PostToolUse continueOnBlock: Refusal With a Load-Bearing Reason](posttooluse-continue-on-block.md) — Feed a hook's rejection reason back to the agent as a continuation signal instead of stopping the turn, turning routable policy violations into guided corrections
- [Terminal Tool Output Compression](terminal-output-compression.md) — Harness-side post-processing collapses predictable shell-output noise (lockfile diffs, `ls -l`, `npm install` progress, unchanged diff hunks) before the model sees it, with a banner that lets the agent opt out per call
- [MessageDisplay Hook: Transforming Assistant Text at the Display Boundary](messagedisplay-hook-assistant-text-transform.md) — A Claude Code 2.1.152 hook event fires on every outbound assistant message and lets a hook rewrite or hide the text before the user sees it — the display-side analogue of PostToolUse output replacement
- [PostToolBatch Hook: Once-Per-Decision-Cycle Injection at the Batch Boundary](posttoolbatch-hook-batch-boundary.md) — `PostToolBatch` fires exactly once per parallel tool batch, before the next model call — the cardinality-matched injection point for conventions and validations that would otherwise duplicate N times across `PostToolUse`

## Specialized Tools

Purpose-built tool patterns for file operations, web research, CLI integration, and editor-level assistance.

- [Batch File Operations via Bash Scripts](batch-file-operations.md) — Consolidate multiple file writes into a single bash script execution to reduce per-call overhead, token consumption, and sequential latency
- [Browser Automation for Research](browser-automation-for-research.md) — When an agent's HTTP client is blocked by CDN bot detection, switch to browser automation tools like Playwright to fetch content
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md) — Write thin wrapper scripts that pre-filter system output so agents receive a decision-ready summary rather than raw command output
- [Cross-Repo Agent Search](cross-repo-agent-search.md) — Expose a GitHub-API-backed text-search tool to reach code outside the workspace, and compose it with local indexed search under remote-index trade-offs
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md) — Structure MCP tools as files in a directory tree and let the agent load only the definitions it needs, reducing token overhead by up to 98%
- [Indexed Regex Search for Agent Tools](indexed-regex-search-agent-tools.md) — Back an agent's regex search with a trigram or suffix-array index so query latency stays bounded on large repositories, at the cost of freshness machinery
- [Next Edit Suggestions](../tools/copilot/next-edit-suggestions.md) — A proactive editing paradigm where the AI predicts both where and what to edit next, between reactive autocomplete and autonomous agent mode
- [Override Interactive Commands](override-interactive-commands.md) — Suppress interactive prompts with a one-line instruction override so the same command definition serves both human-in-the-loop and automated execution
- [Self-Healing Tool Routing](self-healing-tool-routing.md) — Route agent tool calls through a cost-weighted graph; recompute paths on failure and escalate to the LLM only when no feasible path exists
- [Terminal Tools for Agents: send_to_terminal and Background Interaction](send-to-terminal-background-interaction.md) — Use VS Code's send_to_terminal tool and backgroundNotifications setting to give agents bidirectional control over background terminal processes
- [Unix CLI as Native Tool Interface](unix-cli-native-tool-interface.md) — A single run(command) tool backed by Unix CLI can replace large function catalogs, leveraging pretraining on shell usage and built-in discovery primitives
- [Restricting a Coding Agent to a Single execute_code Tool](restrict-coding-agent-to-execute-code.md) — When narrowing an agent to one execute_code tool is cheaper than bash or native edit, and when edit-heavy modification work makes it costlier — a regime-by-agent decision
- [Web Search Agent Loop](web-search-agent-loop.md) — Instead of firing a single query, wrap retrieval in a cycle of search, evaluate, refine, and synthesize -- giving the agent autonomy to decide when evidence is sufficient
- [Lexical-First Retrieval for Agentic Search](lexical-first-retrieval-for-agentic-search.md) — A tuned BM25 index paired with a frontier LLM and deep retrieval can match or beat dense retrieval on deep-research benchmarks -- when the agent loop is strong enough to filter the ranking noise
