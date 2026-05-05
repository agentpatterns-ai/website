---
title: "AI Agent Development Anti-Patterns and Failure Modes"
description: "What not to do when working with AI agents, and why. - Assumption Propagation — An early misunderstanding cascades through all subsequent work, producing"
tags:
  - anti-patterns
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
- [Demo-to-Production Gap](demo-to-production-gap.md) — Agent demos curate inputs and ignore edge cases; per-step accuracy compounds multiplicatively, making demo success rates poor predictors of production performance
- [Distractor Interference: Relevance Is Not Enough](distractor-interference.md) — Semantically related but inapplicable instructions reduce compliance with applicable ones
- [Dynamic Tool Fetching Breaks KV Cache](dynamic-tool-fetching-cache-break.md) — Loading tool definitions dynamically per step destroys prompt cache continuity, erasing cost savings that exceed the token reduction
- [Objective Drift: When Agents Lose the Thread](objective-drift.md) — After [context compression](../context-engineering/context-compression-strategies.md) events, agents can continue working on a subtly different objective than the one they started with
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — Coding agents stop after the first visible signal of progress and declare the task complete while failing tests remain; named by four independent research teams within a year
- [Pattern Replication Risk](pattern-replication-risk.md) — Agents absorb existing codebase patterns and reproduce them at scale, including deprecated APIs and legacy workarounds
- [Single-Layer Prompt Injection Defence](single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to injection attacks that the single layer does not address
- [The Anthropomorphized Agent](anthropomorphized-agent.md) — Treating an AI agent as a team member with memory, feelings, and personality leads to misplaced trust and systematic misuse
- [The Copy-Paste Agent](copy-paste-agent.md) — Duplicating agent definitions causes drift; compose from shared skills instead
- [Spec Complexity Displacement](spec-complexity-displacement.md) — Writing a spec does not eliminate engineering precision — it relocates it; specs tight enough to drive reliable generation converge toward code-like structure
- [The Kitchen Sink Session](session-partitioning.md) — Mixing unrelated tasks in a single session fills the context window with irrelevant history and degrades output quality
- [The Mega-Prompt](../instructions/instruction-compliance-ceiling.md) — A single instruction file containing every rule, convention, and example degrades agent compliance rather than improving it
- [The Prompt Tinkerer](prompt-tinkerer.md) — Endlessly refining prompts to prevent errors that structural controls would eliminate deterministically
- [The Test Homogenization Trap](test-homogenization-trap.md) — LLM-generated test suites share the generating model's blind spots, providing false confidence because tests miss the same edge cases the code misses
- [The Yes-Man Agent](yes-man-agent.md) — Agents without verification instructions execute every request without flagging problems
- [Shadow Tech Debt](shadow-tech-debt.md) — AI agents operating without structural codebase understanding accumulate invisible architectural drift that compounds at machine speed
- [The Reasoning-Complexity Trade-off](reasoning-complexity-tradeoff.md) — Stronger LLMs produce more bloated and coupled code; capability gains buy maintainability losses, and detailed prompting does not mitigate the decay
- [Trust Without Verify](trust-without-verify.md) — Accepting agent output as correct because it looks polished
- [Vibe Coding](../workflows/vibe-coding.md) — Accepting AI-generated code without structural review, producing fragile, unreviewable software
