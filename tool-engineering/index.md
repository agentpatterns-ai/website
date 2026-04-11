---
title: "Tool Engineering: Designing and Managing AI Agent Tooling"
description: "Design, expose, and manage the tools agents use — description quality, schema design, MCP servers, skills, hooks, and specialized patterns."
tags:
  - agent-design
  - tool-engineering
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
- [Token-Efficient Tool Design](token-efficient-tool-design.md) — Design tools so that each call injects the minimum tokens needed for the next agent decision

## Tool Design

Structural patterns for tool interfaces, schemas, error handling, and output formatting.

- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — Tools are the agent's UI; the same principles that make human interfaces usable make agent tools effective
- [Semantic Tool Output](semantic-tool-output.md) — Return human-readable, contextually filtered output from agent tools to reduce hallucination and improve downstream call accuracy
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md) — Formal schemas at every agent-to-agent interface establish explicit contracts that prevent state mismanagement and silent failures
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — Redesign tool interfaces so the wrong call cannot compile -- prevention over documentation
- [Consolidate Agent Tools](consolidate-agent-tools.md) — Prefer fewer, higher-level tools that match how agents reason about tasks over many narrow tools that mirror API endpoint boundaries
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md) — Request structured errors from HTTP APIs using Accept headers to replace brittle HTML parsing with deterministic control flow

## MCP (Model Context Protocol)

Architecture and design guidance for MCP servers and clients -- the open protocol for agent-tool communication.

- [MCP Client/Server Architecture](mcp-client-server-architecture.md) — Architectural best practices covering transport selection, tool granularity, error handling, capability negotiation, and security
- [MCP Client Design](mcp-client-design.md) — Host-side logic for connecting to servers, negotiating capabilities, routing tool calls, caching descriptions, and degrading gracefully on failure
- [MCP Elicitation](mcp-elicitation.md) — How MCP servers collect structured user input mid-task, and how Elicitation and ElicitationResult hooks let you automate, validate, or block those requests
- [MCP LLM Sampling](mcp-llm-sampling.md) — How MCP servers request host LLM inference mid-execution via sampling/createMessage, creating hybrid tools that combine deterministic logic with embedded AI reasoning
- [MCP Server Design](mcp-server-design.md) — A server author's checklist for tool naming, schema design, error handling, resource exposure, and token efficiency
- [Proprietary-to-Open-Standard Migration](copilot-extensions-to-mcp-migration.md) — When a proprietary extension system gets replaced by an open protocol, rebuild on the standard rather than port the old architecture

## Skills

Packaging domain knowledge and reusable capabilities as agent skills with reliable invocation and lifecycle governance.

- [Skill as Knowledge Pattern](skill-as-knowledge.md) — Design skills as pure knowledge containers -- domain rules, heuristics, and reference material -- not executable behavior, so they remain portable across agents
- [CLI-First Skill Design](cli-first-skill-design.md) — Design agent skills as CLI tools so the same interface serves both humans debugging locally and agents automating through shell tool calls
- [Skill Authoring Patterns](skill-authoring-patterns.md) — Practical patterns for building, testing, and troubleshooting agent skills -- categories, description craft, implementation patterns, and debugging
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md) — All SKILL.md frontmatter fields: invocation control, subagent delegation, tool restriction, hooks, and argument handling
- [Skill Library Evolution](skill-library-evolution.md) — How agent skill libraries grow, get pruned, and evolve through versioning, quality gates, and lifecycle governance
- [Skill Tool Runtime Enforcement](skill-tool-runtime-enforcement.md) — Use the Skill tool to load command prompts at invocation time rather than telling agents to read the file -- eliminates stale instructions and path drift

## Hooks & Lifecycle

Deterministic interception points that enforce policy, automate side effects, and audit agent behavior without relying on model compliance.

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md) — Hooks run deterministic code at defined points in an agent's execution -- before and after tool calls, at session boundaries -- enabling enforcement and audit
- [Conditional Hook Execution](conditional-hook-execution.md) — Use the `if` field on hook handlers to filter by tool name and arguments, eliminating subprocess spawns for non-matching calls
- [Hook Catalog](hook-catalog.md) — A reference catalog of high-value hooks grouped by purpose: CLI enforcement, destructive operation guardrails, sandboxing, and workflow automation
- [On-Demand Skill Hooks](on-demand-skill-hooks.md) — Register PreToolUse hooks through a skill invocation to arm strict guardrails for a single session without imposing friction on every workflow
- [PostToolUse BSD/GNU Detection](posttooluse-bsd-gnu-detection.md) — Catch BSD/GNU CLI incompatibilities at runtime with a PostToolUse hook, feed fixes back via additionalContext, and persist knowledge to CLAUDE.md
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md) — The StopFailure hook fires when a Claude Code turn ends due to an API error, giving harnesses a deterministic signal to log failures, alert operators, and feed external recovery workflows

## Specialized Tools

Purpose-built tool patterns for file operations, web research, CLI integration, and editor-level assistance.

- [Batch File Operations via Bash Scripts](batch-file-operations.md) — Consolidate multiple file writes into a single bash script execution to reduce per-call overhead, token consumption, and sequential latency
- [Browser Automation for Research](browser-automation-for-research.md) — When an agent's HTTP client is blocked by CDN bot detection, switch to browser automation tools like Playwright to fetch content
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md) — Write thin wrapper scripts that pre-filter system output so agents receive a decision-ready summary rather than raw command output
- [Filesystem-Based Tool Discovery](filesystem-tool-discovery.md) — Structure MCP tools as files in a directory tree and let the agent load only the definitions it needs, reducing token overhead by up to 98%
- [Next Edit Suggestions](next-edit-suggestions.md) — A proactive editing paradigm where the AI predicts both where and what to edit next, between reactive autocomplete and autonomous agent mode
- [Override Interactive Commands](override-interactive-commands.md) — Suppress interactive prompts with a one-line instruction override so the same command definition serves both human-in-the-loop and automated execution
- [Self-Healing Tool Routing](self-healing-tool-routing.md) — Route agent tool calls through a cost-weighted graph; recompute paths on failure and escalate to the LLM only when no feasible path exists
- [Terminal Tools for Agents: send_to_terminal and Background Interaction](send-to-terminal-background-interaction.md) — Use VS Code's send_to_terminal tool and backgroundNotifications setting to give agents bidirectional control over background terminal processes
- [Unix CLI as Native Tool Interface](unix-cli-native-tool-interface.md) — A single run(command) tool backed by Unix CLI can replace large function catalogs, leveraging pretraining on shell usage and built-in discovery primitives
- [Web Search Agent Loop](web-search-agent-loop.md) — Instead of firing a single query, wrap retrieval in a cycle of search, evaluate, refine, and synthesize -- giving the agent autonomy to decide when evidence is sufficient
