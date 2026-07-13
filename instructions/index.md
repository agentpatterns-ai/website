---
title: "Instructions: System Prompts, Rules, and Agent Configuration"
description: "Patterns for writing, structuring, and governing instruction files and system prompts that shape agent behavior across environments."
tags:
  - instructions
  - index
last_reviewed: 2026-05-27
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
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — Tune a repo-guidance file by probing the agent with synthetic bug-fix tasks and refining on the diagnosed failures; the artifact is model-specific, not transferable
- [Encoding Values in AGENTS.md: Why Prose Without Verification Fails](encoding-values-in-agents-md.md) — Corpus studies show ethics, fairness, and accessibility are largely absent from AGENTS.md; pair every value with a verification command or move it to a lower layer
- [Natural-Language Customization Bootstrap](natural-language-customization-bootstrap.md) — Describe the customization in plain language; the agent drafts the instruction file, skill, subagent, or hook for you to review and commit

## Instruction Design

How you phrase, frame, and structure individual rules determines whether agents follow them or quietly ignore them.

- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md) — Positive directives outperform negative instructions in agent compliance, especially as instruction count grows
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — On SWE-bench, negative constraints are the only individually beneficial rule type; positive directives actively hurt — and rules work through context priming, not instruction specificity
- [Security Knowledge Priming for Code Generation (SPARK)](security-knowledge-priming.md) — A brief task-relevant CWE cue in the prompt activates the model's latent security knowledge — supplementary to mechanical scanners, not a replacement
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md) — Exclusions and constraints eliminate entire classes of mistakes more efficiently than equivalent positive guidance
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — Rules generalize; examples anchor — knowing when to use each determines whether agents interpret your intent or invent their own
- [Encoding Product-Design Taste into Agent Context](encoding-product-design-taste.md) — Encode product-design decisions as observable rules and mode-routed skill files; pair with design tokens and lint, never instead of them
- [Iterative Binary Feedback for Pattern Adherence](iterative-binary-feedback-pattern-adherence.md) — Looping yes/no pattern judgments through capable models beats verbose critique for design-pattern adherence when the predicate space is small and the judge is deterministic
- [Hints Over Code Samples in Agent Prompts](hints-over-code-samples.md) — Reference existing code by path instead of embedding samples in prompts — hints stay current, cost fewer tokens, and eliminate maintenance drift
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](critical-instruction-repetition.md) — Repeating a critical instruction at both the start and end of a prompt exploits primacy and recency bias for higher compliance
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — Instruction compliance degrades as rule count grows; adding more rules past a threshold produces omission errors, not better behavior
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — LLM code generation accuracy drops sharply as simultaneous constraint count increases; reduce constraint load through decomposition, schemas, and mechanical enforcement
- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — Restructuring how constraints are formatted in prompts does not improve model compliance; the compliance lever is constraint design, not encoding form
- [Configuration File Structure Does Not Drive Compliance](configuration-file-structure-compliance-gap.md) — A factorial study of file size, instruction position, file architecture, and contradictions found none of the four variables produced detectable compliance contrasts within realistic file sizes
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md) — Effective prompts sit at the altitude that produces consistent behaviour across variation, neither too brittle nor too vague
- [Three Knowledge Tiers: Sourced, Unverified, Hallucinated](three-knowledge-tiers.md) — Classify agent knowledge into three tiers to preserve useful training knowledge while maintaining accuracy standards
- [Cost-Aware Skill Rewriting: Preserve Operational Anchors, Not Skill Tokens](cost-aware-skill-rewriting.md) — Rewriting a skill is an economic trade-off, not pure compression — stripping sparse operational anchors makes the agent explore and retry, raising total cost despite a shorter document
- [Codified Effort and Escalation Policy in the Instruction File](codified-effort-escalation-policy.md) — Write the default-cheap, escalate-on-evidence effort and model-routing rule into the instruction file so the cheap path is the default and survives context switches

## Architecture & Composition

Structuring instructions across scopes, layers, and files so the right context reaches the right agent at the right time.

- [Layered Instruction Scopes](layered-instruction-scopes.md) — Structure agent instructions in concentric layers — global defaults, project-level files, and directory overrides — so the most specific rule always wins
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md) — Layer CLAUDE.md files at multiple scopes so each agent session receives only the context relevant to its working location
- [claudeMdExcludes: Selective Ancestor Instruction-File Exclusion](claude-md-excludes.md) — Skip irrelevant ancestor CLAUDE.md files in a monorepo with a glob list, so the agent's context is not burned on conventions for packages you never touch
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
- [Agent-Ready Bug Reports for Software Repair Agents](agent-ready-bug-reports.md) — Rank bug report fields by measured effect on an AI repair agent's correct-fix rate; localization and suggested fixes beat human-style reproduction steps
- [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) — Independent specification layers absorb prompt noise that would otherwise degrade code-generation correctness; prose repetition and brittle terminology do not
- [Stage-Targeted Prompt Structure for Pull Request Outcomes](stage-targeted-prompt-structure-pr-outcomes.md) — Specificity, Context, and Verification each move a different stage of the LLM-assisted PR pipeline — diagnose which stage is failing, then raise that dimension
- [Ubiquitous Language for AI Plans](ubiquitous-language-for-ai-plans.md) — A maintained domain glossary plus ADRs anchors agent plans in existing code so plans, source, and prompt share one vocabulary

## Governance & Maintenance

Reviewing, versioning, and repairing instruction files over time so they remain effective as projects evolve.

- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — Move critical behavioral rules out of prompts and into deterministic shell hooks that the model cannot override
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — Tagging each rule with source, applies_to, and retire_when converts the rule-budget audit from a counting exercise into a pruning exercise so the instruction surface can actually shrink
- [Agent Context File Evolution: Treating ACFs as Configuration Code](agent-context-file-evolution.md) — ACFs are actively-maintained artifacts that drift with code and grow monotonically; the maintenance discipline is two loops — add-on-drift and compact-on-add — that keep the file under the compliance ceiling
- [Prompt Governance via PR](prompt-governance-via-pr.md) — Store agent instructions as plain markdown files in git and use pull requests to propose, review, and merge behaviour changes
- [Agent Config as a Managed Supply Chain](agent-config-as-managed-supply-chain.md) — Treat CLAUDE.md and AGENTS.md as a content-addressed, version-pinned, permission-declaring artifact; the benefit is provenance and rollback at multi-repo scale, not model compliance
- [Post-Compaction Re-read Protocol](post-compaction-reread-protocol.md) — Restore behavioural contracts after context compaction by triggering a targeted re-read of CLAUDE.md or AGENTS.md
- [Content Exclusion Gap in Agent Systems](content-exclusion-gap.md) — Security boundaries defined for one AI interaction mode may not apply across all modes; content exclusion rules for completions and chat can be silently ignored in agent mode
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](prompt-rewrite-on-cross-generation-migration.md) — Discard the inherited prompt stack on cross-generation hops, start from the smallest prompt that preserves the product contract, and re-tune reasoning effort, verbosity, tool descriptions, and output format against representative examples
- [HTML as Agent Output Format: When to Ask for HTML Instead of Markdown](html-as-output-format.md) — Markdown won by token efficiency on small context windows; on frontier models, asking for HTML unlocks interactive review artifacts and explainers — but only when the output will be opened in a browser, not piped into a Markdown-rendering surface
- [Mermaid as Agent Output Format: When to Ask for a Diagram Instead of Prose](mermaid-as-agent-output-format.md) — Asking the agent for a Mermaid block instead of a prose list scans faster for graph-shaped information — but only on surfaces that render Mermaid inline; the decision is a property of the consumer surface, not the model
