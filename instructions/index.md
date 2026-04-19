---
title: "Instructions: System Prompts, Rules, and Agent Configuration"
description: "Patterns for writing, structuring, and governing instruction files and system prompts that shape agent behavior across environments."
tags:
  - instructions
---

# Instructions

> Patterns for writing, structuring, and governing the instruction files and system prompts that shape agent behavior.

## Instruction Files

Every major AI coding tool ships a project-level instruction file. These pages cover the conventions, ecosystems, and design patterns for authoring them.

- [CLAUDE.md Convention](claude-md-convention.md) — CLAUDE.md is Claude Code's project-level instruction file, read at session start to understand project conventions, tooling, and behavioral rules
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md) — Every major AI coding tool invented a project-level instruction file independently; understanding how they relate helps teams avoid content drift and duplication
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md) — Four concrete patterns drawn from analysis of 2,500+ real repositories for writing effective AGENTS.md files
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md) — Keep AGENTS.md to ~100 lines as a pointer map; put structured knowledge in a versioned docs/ directory
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md) — Capture team-specific patterns, style rules, and tooling requirements in AGENTS.md files throughout the codebase
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — Auto-generated context files reduce task success rates; human-written files improve success only when they contain minimal, specific instructions
- [Natural-Language Customization Bootstrap](natural-language-customization-bootstrap.md) — Describe the customization in plain language; the agent drafts the instruction file, skill, subagent, or hook for you to review and commit

## Instruction Design

How you phrase, frame, and structure individual rules determines whether agents follow them or quietly ignore them.

- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md) — Positive directives outperform negative instructions in agent compliance, especially as instruction count grows
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — On SWE-bench, negative constraints are the only individually beneficial rule type; positive directives actively hurt — and rules work through context priming, not instruction specificity
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md) — Exclusions and constraints eliminate entire classes of mistakes more efficiently than equivalent positive guidance
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — Rules generalize; examples anchor — knowing when to use each determines whether agents interpret your intent or invent their own
- [Hints Over Code Samples in Agent Prompts](hints-over-code-samples.md) — Reference existing code by path instead of embedding samples in prompts — hints stay current, cost fewer tokens, and eliminate maintenance drift
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](critical-instruction-repetition.md) — Repeating a critical instruction at both the start and end of a prompt exploits primacy and recency bias for higher compliance
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — Instruction compliance degrades as rule count grows; adding more rules past a threshold produces omission errors, not better behavior
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — LLM code generation accuracy drops sharply as simultaneous constraint count increases; reduce constraint load through decomposition, schemas, and mechanical enforcement
- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — Restructuring how constraints are formatted in prompts does not improve model compliance; the compliance lever is constraint design, not encoding form
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md) — Effective prompts sit at the altitude that produces consistent behaviour across variation, neither too brittle nor too vague
- [Three Knowledge Tiers: Sourced, Unverified, Hallucinated](three-knowledge-tiers.md) — Classify agent knowledge into three tiers to preserve useful training knowledge while maintaining accuracy standards

## Architecture & Composition

Structuring instructions across scopes, layers, and files so the right context reaches the right agent at the right time.

- [Layered Instruction Scopes](layered-instruction-scopes.md) — Structure agent instructions in concentric layers — global defaults, project-level files, and directory overrides — so the most specific rule always wins
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md) — Layer CLAUDE.md files at multiple scopes so each agent session receives only the context relevant to its working location
- [@import Composition Pattern for Instruction Files](import-composition-pattern.md) — Claude Code supports `@path/to/file` imports in CLAUDE.md, enabling modular instruction authoring; other tools rely on hierarchical discovery instead
- [Prompt File Libraries](prompt-file-libraries.md) — Store reusable, parameterized prompt templates as version-controlled files that team members invoke on demand
- [Production System Prompt Architecture](production-system-prompt-architecture.md) — Structural patterns from a 102K-char production system prompt: XML-sectioned concern isolation, skills registries, and deferred tool loading

## System Prompts

Designing, replacing, and dynamically augmenting the system-level instructions that define an agent's identity and capabilities.

- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md) — Domain-specific system prompts with worked examples produce consistent, high-quality agent behavior in your specific context
- [System Prompt Replacement for Domain-Specific Agent Personas](system-prompt-replacement.md) — Replace the default coding-focused system prompt entirely to transform an agent into a domain specialist while preserving its tool ecosystem
- [Event-Driven System Reminders](event-driven-system-reminders.md) — Inject targeted guidance at specific points during agent execution to combat instruction fade-out without bloating the static system prompt

## Specifications & Standards

Leveraging existing artifacts — specs, schemas, standards files — as agent instructions rather than writing natural-language duplicates.

- [The Specification as Prompt](specification-as-prompt.md) — Use types, schemas, tests, and API definitions as agent instructions instead of natural language descriptions
- [Frozen Spec File](frozen-spec-file.md) — Write goals, non-goals, constraints, and completion criteria into an immutable file the agent reads but cannot modify, preventing drift across context compaction
- [Feature List Files](feature-list-files.md) — Maintain a structured JSON file defining every feature with status and acceptance criteria; agents work through it sequentially
- [Standards as Agent Instructions](standards-as-agent-instructions.md) — A standards file actionable for humans is, verbatim, an instruction file for agents — the same document does both jobs when written precisely
- [Convention Over Configuration for Agent Workflows](convention-over-configuration.md) — Reduce agent errors by encoding decisions into naming conventions, directory structure, and label schemes so agents follow patterns rather than invent them
- [WRAP Framework for Agent Instructions](wrap-framework-agent-instructions.md) — A four-step checklist for writing agent-ready task descriptions that maximize autonomous execution quality

## Governance & Maintenance

Reviewing, versioning, and repairing instruction files over time so they remain effective as projects evolve.

- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — Move critical behavioral rules out of prompts and into deterministic shell hooks that the model cannot override
- [Prompt Governance via PR](prompt-governance-via-pr.md) — Store agent instructions as plain markdown files in git and use pull requests to propose, review, and merge behaviour changes
- [Post-Compaction Re-read Protocol](post-compaction-reread-protocol.md) — Restore behavioural contracts after context compaction by triggering a targeted re-read of CLAUDE.md or AGENTS.md
- [Content Exclusion Gap in Agent Systems](content-exclusion-gap.md) — Security boundaries defined for one AI interaction mode may not apply across all modes; content exclusion rules for completions and chat can be silently ignored in agent mode
