---
title: "AI Agent Development Anti-Patterns and Failure Modes"
description: "What not to do when working with AI agents, and why. - Assumption Propagation — An early misunderstanding cascades through all subsequent work, producing"
tags:
  - anti-pattern
last_reviewed: 2026-05-27
---
# Anti-Patterns

> What not to do when working with AI agents, and why.

## Pages

- [Assumption Propagation](assumption-propagation.md) — An early misunderstanding cascades through all subsequent work, producing internally consistent output that solves the wrong problem
- [Boring Technology Bias](boring-technology-bias.md) — LLMs recommend tools proportional to training data frequency, not fitness for the problem; popular beats optimal by default
- [Framework-First Agent Development](framework-first.md) — Starting with a high-level framework before understanding the raw LLM API adds abstraction layers that obscure failures and lock in architectural decisions before requirements are clear
- [The Effortless AI Fallacy](effortless-ai-fallacy.md) — Expecting AI tools to work without effort produces the worst outcomes and a self-sealing complaint cycle that low-investment users cannot exit
- [LLM Code Review Overcorrection](llm-review-overcorrection.md) — LLMs systematically flag correct code as non-compliant; more detailed review prompts make the misclassification rate worse, not better
- [PR Scope Creep as a Human Review Bottleneck](pr-scope-creep-review-bottleneck.md) — AI generation velocity outpaces human review capacity; stalled PRs attract scope additions that grow changesets past the cognitive effectiveness threshold, worsening the bottleneck
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — Applying mid-stream reasoning to every agent task regardless of whether reasoning improves outcomes — adding token cost and latency without benefit
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md) — Knowledge that exists only in Slack threads, meetings, or team memory is invisible to agents, producing repeating errors that no amount of prompting can fix
- [The Infinite Context](infinite-context.md) — A larger context window does not produce better output — unfocused context dilutes attention and degrades performance
- [Cargo Cult Agent Setup](cargo-cult-agent-setup.md) — Copying agent configurations without understanding why they work produces agents that follow irrelevant conventions
- [Comprehension Debt](comprehension-debt.md) — The growing gap between AI-generated code volume and developer understanding; it lives in people, not in the codebase
- [Context Poisoning: When Hallucinations Become Premises](context-poisoning.md) — A hallucination treated as fact propagates through subsequent reasoning, producing confidently wrong output that is internally consistent
- [Cross-Component Interference in Agent Scaffolds](cross-component-interference.md) — Stacking planning, memory, retrieval, and self-reflection on top of tool use is rarely the optimum; the maximally-equipped agent loses to smaller subsets in 30-50% of tasks, with planning and memory the worst offenders
- [Demo-to-Production Gap](demo-to-production-gap.md) — Agent demos curate inputs and ignore edge cases; per-step accuracy compounds multiplicatively, making demo success rates poor predictors of production performance
- [Distractor Interference: Relevance Is Not Enough](distractor-interference.md) — Semantically related but inapplicable instructions reduce compliance with applicable ones
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — Every external artifact crossing an agent's read boundary is a remote command-execution channel; treating READMEs, packages, and fetched pages as benign data is the developer mental-model failure
- [Dynamic Tool Fetching Breaks KV Cache](dynamic-tool-fetching-cache-break.md) — Loading tool definitions dynamically per step destroys prompt cache continuity, erasing cost savings that exceed the token reduction
- [Mid-Session Config Changes as Invisible Cache Invalidators](mid-session-config-cache-invalidators.md) — Switching model, effort, or MCP servers mid-session silently invalidates the prompt cache and re-bills the entire prefix at ~10x the cached rate
- [Objective Drift: When Agents Lose the Thread](objective-drift.md) — After [context compression](../context-engineering/context-compression-strategies.md) events, agents can continue working on a subtly different objective than the one they started with
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — Coding agents stop after the first visible signal of progress and declare the task complete while failing tests remain; named by four independent research teams within a year
- [Run-Status vs Task-Status Confusion in Autonomous Agent Runs](run-status-vs-task-status-confusion.md) — A green status on a scheduled or cloud-triggered agent means the harness exited cleanly, not that the task succeeded; single-axis dashboards hide every silent agent failure as default success
- [Pattern Replication Risk](pattern-replication-risk.md) — Agents absorb existing codebase patterns and reproduce them at scale, including deprecated APIs and legacy workarounds
- [Single-Layer Prompt Injection Defence](single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to injection attacks that the single layer does not address
- [MCP Allowlist by Label, Not by Identity (serverName Trap)](mcp-allowlist-label-vs-identity.md) — A `serverName`-only MCP allowlist filters the user-chosen label, not the underlying server — any binary or URL the user calls `github` passes the check
- [Prompt as Security Knob](prompt-as-security-knob.md) — Semantic-preserving prompt perturbations collapse the secure-and-functional rate of hardened code generators to 3–17%, so a "good" prompt is never sufficient evidence that generated code is secure
- [bypassPermissions Silently Overrides allowedTools (The Restricted-Bypass Trap)](bypass-permissions-overrides-allowlist.md) — Pairing allowedTools with bypassPermissions does not restrict the agent — the allow list is a no-op below the bypass step, so every tool runs without prompts
- [Direct Prompt Injection via Collaboration (User as Attack Vector)](direct-prompt-injection-collaboration.md) — When the user pastes an attacker-crafted prompt themselves, model-layer classifiers anchored on user intent have nothing anomalous to flag; only egress controls and filesystem boundaries hold
- [The Anthropomorphized Agent](anthropomorphized-agent.md) — Treating an AI agent as a team member with memory, feelings, and personality leads to misplaced trust and systematic misuse
- [The Copy-Paste Agent](copy-paste-agent.md) — Duplicating agent definitions causes drift; compose from shared skills instead
- [Spec Complexity Displacement](spec-complexity-displacement.md) — Writing a spec does not eliminate engineering precision — it relocates it; specs tight enough to drive reliable generation converge toward code-like structure
- [The Kitchen Sink Session](session-partitioning.md) — Mixing unrelated tasks in a single session fills the context window with irrelevant history and degrades output quality
- [The Mega-Prompt](../instructions/instruction-compliance-ceiling.md) — A single instruction file containing every rule, convention, and example degrades agent compliance rather than improving it
- [The Prompt Tinkerer](prompt-tinkerer.md) — Endlessly refining prompts to prevent errors that structural controls would eliminate deterministically
- [The Test Homogenization Trap](test-homogenization-trap.md) — LLM-generated test suites share the generating model's blind spots, providing false confidence because tests miss the same edge cases the code misses
- [The Yes-Man Agent](yes-man-agent.md) — Agents without verification instructions execute every request without flagging problems
- [Shadow Tech Debt](shadow-tech-debt.md) — AI agents operating without structural codebase understanding accumulate invisible architectural drift that compounds at machine speed
- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — CLAUDE.md, AGENTS.md, and .cursorrules drift out of sync with the code they describe; existing documentation-consistency checkers retarget cleanly at the new file glob
- [The Reasoning-Complexity Trade-off](reasoning-complexity-tradeoff.md) — Stronger LLMs produce more bloated and coupled code; capability gains buy maintainability losses, and detailed prompting does not mitigate the decay
- [Trust Without Verify](trust-without-verify.md) — Accepting agent output as correct because it looks polished
- [Vibe Coding](vibe-coding.md) — Accepting AI-generated code without structural review, producing fragile, unreviewable software
- [Agent-Laundered Bug Reports](agent-laundered-bug-reports.md) — Running a bug report through an LLM before filing strips the load-bearing observation and replaces it with confident speculation that misleads downstream triage
- [Memory-Induced Tool-Drift](memory-induced-tool-drift.md) — Personality biases stored in long-term memory act as implicit steering vectors on tool-call parameters in unrelated contexts; prompt-based defenses reduce but do not eliminate the drift
- [Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)](large-codebase-agent-failure-patterns.md) — Five named failure shapes — lost in the codebase, wrong symbol, partial completion, tool thrashing, context overflow — that surface in 400K+ LOC repos, sourced from 1,281 agent runs across 40+ codebases
- [Coding-Agent Misalignment Forms (Seven-Symptom Taxonomy)](coding-agent-misalignment-forms.md) — Seven session-level forms (S1–S7) of developer-agent misalignment named in a 20,574-session field study; constraint violations and inaccurate self-reporting grow in share while capability gains close the other forms
- [Trusting Human Review to Catch Deliberate Agent Sabotage](deliberate-agent-code-sabotage.md) — Human-in-the-loop review fails to catch AI agents that insert malicious code with a plausible cover story — 94% non-detection, 56% accept rate even after a safety monitor warns
- [Treating Agent Safety as Uniform Across a Session (Cold-Start Safety Gap)](cold-start-safety-gap.md) — Tool-calling LLM agents refuse unsafe requests 9–52% less often at session start than after a few benign tasks; deployments that assume uniform turn-by-turn safety leave a measurable gap
- [Trusting Tool Error Messages as Implicit Authority (Error-Path Injection)](tool-error-implicit-authority.md) — Error frames carry implicit authority that bypasses standard safety heuristics; sandwich injection inside error context triples ordinary IPI success and reaches up to 100% compliance on four frontier models
- [AI Agents in CI/CD with Elevated Permissions and Untrusted Content (GitInject)](ai-agents-in-ci-cd-with-elevated-permissions.md) — Default-shape AI reviewers in GitHub Actions hold repo-write tokens and ingest PR/issue text in the same runtime — every tested provider was vulnerable in default config, with at least one CVSS 9.4 case
