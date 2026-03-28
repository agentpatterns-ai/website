---
title: "Concept Map for AI Agent Development"
description: "All site content grouped by theme, cutting across sections. Find related concepts regardless of where they live in the navigation."
tags:
  - navigation
  - reference
---
# Concept Map

> All site content grouped by theme, cutting across sections. Find related concepts regardless of where they live in the navigation.

<div class="grid cards" markdown>

-   **Context Engineering**

    ---

    Budgets, compression, attention, and retrieval

    [Jump to section →](#context-engineering)

-   **Instructions & Prompts**

    ---

    Layering, scoping, polarity, and instruction files

    [Jump to section →](#instructions-prompts)

-   **Agent Architecture**

    ---

    Composition, delegation, coordination, and memory

    [Jump to section →](#agent-architecture)

-   **Tool Design**

    ---

    Descriptions, discovery, filtering, and engineering

    [Jump to section →](#tool-design)

-   **Security & Safety**

    ---

    Injection defense, sandboxing, and credentials

    [Jump to section →](#security-safety)

-   **Testing & Evaluation**

    ---

    Evals, metrics, code review, and verification

    [Jump to section →](#testing-evaluation)

-   **Hooks & Guardrails**

    ---

    Lifecycle events and deterministic enforcement

    [Jump to section →](#hooks-guardrails)

-   **Reliability & Recovery**

    ---

    Error handling, cost control, and loop detection

    [Jump to section →](#reliability-recovery)

-   **Standards & Protocols**

    ---

    AGENTS.md, MCP, A2A, and interop conventions

    [Jump to section →](#standards-protocols)

-   **Development Workflows**

    ---

    Planning, bootstrapping, CI/CD, and iteration

    [Jump to section →](#development-workflows)

-   **Human Factors**

    ---

    Cognitive load, attention management, and adoption

    [Jump to section →](#human-factors)

-   **Anti-Patterns**

    ---

    Common mistakes with context, prompts, and trust

    [Jump to section →](#anti-patterns)

-   **Emerging Concepts**

    ---

    Product-as-IDE, personalization, and early signals

    [Jump to section →](#emerging-concepts)

</div>

<div class="concept-map" markdown>

## Context Engineering

> Managing what enters the context window — budgets, compression, attention, and retrieval.

- [Attention Sinks: Why First Tokens Always Win](context-engineering/attention-sinks.md)
- [Context Budget Allocation: Every Token Has a Cost](context-engineering/context-budget-allocation.md)
- [Context Compression Strategies](context-engineering/context-compression-strategies.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering/context-engineering.md)
- [Context Priming](context-engineering/context-priming.md)
- [Context Window Management: The Dumb Zone](context-engineering/context-window-dumb-zone.md)
- [Discoverable vs Non-Discoverable Context](context-engineering/discoverable-vs-nondiscoverable-context.md)
- [Layered Context Architecture](context-engineering/layered-context-architecture.md)
- [Lost in the Middle: The U-Shaped Attention Curve](context-engineering/lost-in-the-middle.md)
- [Separation of Knowledge and Execution](agent-design/separation-of-knowledge-and-execution.md)
- [Three Knowledge Tiers: Sourced, Unverified, Hallucinated](instructions/three-knowledge-tiers.md)
- [Context Hub: On-Demand Versioned API Docs](context-engineering/context-hub.md)
- [Filter and Aggregate in the Execution Environment](context-engineering/filter-aggregate-execution-env.md)
- [Observation Masking: Filter Tool Outputs from Context](context-engineering/observation-masking.md)
- [Prompt Compression: Maximizing Signal Per Token](context-engineering/prompt-compression.md)
- [Retrieval-Augmented Agent Workflows](context-engineering/retrieval-augmented-agent-workflows.md)
- [Seeding Agent Context: Breadcrumbs in Code](context-engineering/seeding-agent-context.md)
- [Semantic Context Loading](context-engineering/semantic-context-loading.md)
- [Static Content First to Maximize Cache Hits](context-engineering/static-content-first-caching.md)

## Instructions & Prompts

> Writing effective instructions — layering, scoping, polarity, and instruction file conventions.

- [AGENTS.md as Table of Contents, Not Encyclopedia](instructions/agents-md-as-table-of-contents.md)
- [CLAUDE.md Convention](instructions/claude-md-convention.md)
- [Convention Over Configuration for Agent Workflows](instructions/convention-over-configuration.md)
- [Dynamic System Prompt Composition](context-engineering/dynamic-system-prompt-composition.md)
- [The Instruction Compliance Ceiling](instructions/instruction-compliance-ceiling.md)
- [Project Instruction File Ecosystem](instructions/instruction-file-ecosystem.md)
- [Layer Instructions by Specificity](instructions/layered-instruction-scopes.md)
- [Negative Space Instructions: What NOT to Do](instructions/negative-space-instructions.md)
- [Pre-Completion Checklists](verification/pre-completion-checklists.md)
- [Prompt Chaining](context-engineering/prompt-chaining.md)
- [Prompt Layering: How Instructions Stack and Override](context-engineering/prompt-layering.md)
- [Session Initialization Ritual](agent-design/session-initialization-ritual.md)
- [The Specification as Prompt](instructions/specification-as-prompt.md)
- [Standards as Agent Instructions](instructions/standards-as-agent-instructions.md)
- [Controlling Agent Output](agent-design/controlling-agent-output.md)
- [Critical Instruction Repetition](instructions/critical-instruction-repetition.md)
- [Domain-Specific System Prompts](instructions/domain-specific-system-prompts.md)
- [Example-Driven vs Rule-Driven Instructions](instructions/example-driven-vs-rule-driven-instructions.md)
- [Hierarchical CLAUDE.md](instructions/hierarchical-claude-md.md)
- [Example-Driven vs Rule-Driven Instructions](instructions/example-driven-vs-rule-driven-instructions.md)
- [Instruction Polarity: Positive Rules Over Negative](instructions/instruction-polarity.md)
- [Narrow Task Instructions to Reduce Injection](security/task-scope-security-boundary.md)
- [Agent Memory Patterns: Persistent, Scoped Corrections](agent-design/agent-memory-patterns.md)
- [System Prompt Altitude](instructions/system-prompt-altitude.md)
- [System Prompt Replacement for Domain-Specific Personas](instructions/system-prompt-replacement.md)

## Agent Architecture

> Composing, structuring, and coordinating agents — delegation, composition patterns, multi-agent coordination, and memory.

- [Adversarial Multi-Model Pipeline (VSDD)](multi-agent/adversarial-multi-model-pipeline.md)
- [Agent Backpressure: Automated Feedback for Self-Correction](agent-design/agent-backpressure.md)
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines](agent-design/agent-composition-patterns.md)
- [Agent-First Software Design](agent-design/agent-first-software-design.md)
- [Agent Harness: Initializer and Coding Agent](agent-design/agent-harness.md)
- [Agent Pushback Protocol](agent-design/agent-pushback-protocol.md)
- [Skill Library Evolution](tool-engineering/skill-library-evolution.md)
- [Agent Turn Model](agent-design/agent-turn-model.md)
- [Agents vs Commands](agent-design/agents-vs-commands.md)
- [Lay the Architectural Foundation by Hand](workflows/architectural-foundation-first.md)
- [Codebase Readiness for Agents](workflows/codebase-readiness.md)
- [Committee Review Pattern](code-review/committee-review-pattern.md)
- [The Delegation Decision](agent-design/delegation-decision.md)
- [Domain-Specific Agent Challenges](human/domain-specific-agent-challenges.md)
- [Evaluator-Optimizer Pattern](agent-design/evaluator-optimizer.md)
- [Fan-Out Synthesis Pattern](multi-agent/fan-out-synthesis.md)
- [File-Based Agent Coordination](multi-agent/file-based-agent-coordination.md)
- [Orchestrator-Worker Pattern](multi-agent/orchestrator-worker.md)
- [Progressive Disclosure for Agent Definitions](agent-design/progressive-disclosure-agents.md)
- [The Ralph Wiggum Loop](agent-design/ralph-wiggum-loop.md)
- [Specialized Agent Roles](agent-design/specialized-agent-roles.md)
- [Task-Specific Agents vs Role-Based Agents](agent-design/task-specific-vs-role-based-agents.md)
- [Worktree Isolation](workflows/worktree-isolation.md)
- [Agent Handoff Protocols](multi-agent/agent-handoff-protocols.md)
- [Agent Memory Patterns](agent-design/agent-memory-patterns.md)
- [Beads: Structured Task Graphs as External Agent Memory](agent-design/beads-task-graph-agent-memory.md)
- [Oracle-Based Task Decomposition](multi-agent/oracle-task-decomposition.md)
- [Skeleton Projects as Agent Scaffolding](workflows/skeleton-projects-as-scaffolding.md)
- [Sub-Agents for Fan-Out Research](multi-agent/sub-agents-fan-out.md)
- [Parallel Agent Sessions](workflows/parallel-agent-sessions.md)

## Tool Design

> Building, describing, and filtering tools — making tools agent-friendly.

- [Consolidate Agent Tools](tool-engineering/consolidate-agent-tools.md)
- [Feature List Files](instructions/feature-list-files.md)
- [Filesystem-Based Tool Discovery](tool-engineering/filesystem-tool-discovery.md)
- [Token-Efficient Tool Design](tool-engineering/token-efficient-tool-design.md)
- [Tool Minimalism and High-Level Prompting](tool-engineering/tool-minimalism.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](tool-engineering/advanced-tool-use.md)
- [Batch File Operations via Bash Scripts](tool-engineering/batch-file-operations.md)
- [CLI Scripts as Agent Tools](tool-engineering/cli-scripts-as-agent-tools.md)
- [Permutation Frameworks for Batch Code Generation](workflows/permutation-frameworks.md)
- [Semantic Tool Output](tool-engineering/semantic-tool-output.md)
- [Subagent Schema-Level Tool Filtering](multi-agent/subagent-schema-level-tool-filtering.md)
- [Tool Description Quality](tool-engineering/tool-description-quality.md)
- [Write Tool Descriptions Like Onboarding Docs](tool-engineering/tool-descriptions-as-onboarding.md)
- [Tool Engineering](tool-engineering/tool-engineering.md)

## Security & Safety

> Defending against prompt injection, data exfiltration, and credential exposure.

- [Blast Radius Containment: Least Privilege for AI Agents](security/blast-radius-containment.md)
- [Dual-Boundary Sandboxing](security/dual-boundary-sandboxing.md)
- [Prompt Injection: A First-Class Threat](security/prompt-injection-threat-model.md)
- [Scope Sandbox Rules to Harness-Owned Tools](security/sandbox-rules-harness-tools.md)
- [URL-Based Data Exfiltration Guard](security/url-exfiltration-guard.md)
- [Treat Task Scope as a Security Boundary](security/task-scope-security-boundary.md)
- [Defense-in-Depth Agent Safety](security/defense-in-depth-agent-safety.md)
- [Close the Attack-to-Fix Loop](security/close-attack-to-fix-loop.md)
- [PII Tokenization in Agent Context](security/pii-tokenization-in-agent-context.md)
- [Protecting Sensitive Files from Agent Context](security/protecting-sensitive-files.md)
- [RL-Trained Automated Red Teamers](security/rl-automated-red-teamers.md)
- [Scoped Credentials via Proxy](security/scoped-credentials-proxy.md)
- [Secrets Management for Agent Workflows](security/secrets-management-for-agents.md)
- [Public-Web Index to Gate URL Fetching](security/url-fetch-public-index-gate.md)

## Testing & Evaluation

> Measuring agent quality — evals, metrics, code review, and verification strategies.

- [Verification Ledger](verification/verification-ledger.md)
- [Diff-Based Review Over Output Review](code-review/diff-based-review.md)
- [Incremental Verification](verification/incremental-verification.md)
- [Agent-Assisted Code Review](code-review/agent-assisted-code-review.md)
- [Analyzing Agent Evaluation Transcripts](verification/agent-transcript-analysis.md)
- [Golden Query Pairs as Regression Tests](verification/golden-query-pairs-regression.md)
- [Grade Agent Outcomes, Not Execution Paths](verification/grade-agent-outcomes.md)
- [Test Harness Design for LLM Context Windows](verification/llm-context-test-harness.md)
- [pass@k and pass^k Metrics](verification/pass-at-k-metrics.md)
- [Red-Green-Refactor with Agents](verification/red-green-refactor-agents.md)
- [Risk-Based Task Sizing for Verification Depth](verification/risk-based-task-sizing.md)
- [Task List Divergence as Instruction Diagnostic](verification/task-list-divergence-diagnostic.md)
- [Test-Driven Agent Development](verification/tdd-agent-development.md)
- [Eval-Driven Development](workflows/eval-driven-development.md)
- [Evaluation-Driven Development for Agent Tools](workflows/eval-driven-tool-development.md)
- [LLM-as-Judge Evaluation](workflows/llm-as-judge-evaluation.md)
- [Simulation and Replay Testing](workflows/simulation-replay-testing.md)

## Hooks & Guardrails

> Deterministic enforcement — lifecycle hooks, permissions, and structured constraints.

- [Deterministic Guardrails Around Probabilistic Agents](verification/deterministic-guardrails.md)
- [Hooks for Enforcement vs Prompts for Guidance](verification/hooks-vs-prompts.md)
- [Structured Output Constraints](verification/structured-output-constraints.md)
- [Event-Driven System Reminders](instructions/event-driven-system-reminders.md)
- [Hook Catalog: Enforcing Agent Behavior with Hooks](tool-engineering/hook-catalog.md)
- [Hooks and Lifecycle Events](tool-engineering/hooks-lifecycle-events.md)
- [Permission-Gated Custom Commands](security/permission-gated-commands.md)
- [PostToolUse Auto-Formatting and Linting](workflows/posttooluse-auto-formatting.md)

## Reliability & Recovery

> Error handling, cost control, and recovery — circuit breakers, rollbacks, loop detection, and performance budgets.

- [Circuit Breakers for Agent Loops](observability/circuit-breakers.md)
- [Cost-Aware Agent Design](agent-design/cost-aware-agent-design.md)
- [Idempotent Agent Operations](agent-design/idempotent-agent-operations.md)
- [Rollback-First Design](agent-design/rollback-first-design.md)
- [Layered Accuracy Defense](verification/layered-accuracy-defense.md)
- [Risk-Based Shipping](verification/risk-based-shipping.md)
- [Context-Injected Error Recovery](context-engineering/context-injected-error-recovery.md)
- [Heuristic-Based Effort Scaling](agent-design/heuristic-effort-scaling.md)
- [Loop Detection](observability/loop-detection.md)
- [Reasoning Budget Allocation](agent-design/reasoning-budget-allocation.md)
- [Stateless Agent Loop with Prompt Caching](context-engineering/prompt-caching-architectural-discipline.md)
- [Steering Running Agents](agent-design/steering-running-agents.md)
- [The Think Tool](agent-design/think-tool.md)
- [Agent Debugging](observability/agent-debugging.md)
- [Escape Hatches: Unsticking Stuck Agents](workflows/escape-hatches.md)

## Standards & Protocols

> Open standards and conventions for agent interoperability — AGENTS.md, MCP, A2A, and more.

- [Agent-to-Agent (A2A) Protocol](standards/a2a-protocol.md)
- [Agent Cards: Capability Discovery](standards/agent-cards.md)
- [Agent Definition Formats](standards/agent-definition-formats.md)
- [Agent Skills: Cross-Tool Task Knowledge](standards/agent-skills-standard.md)
- [AGENTS.md: A README for AI Coding Agents](standards/agents-md.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](geo/llms-txt.md)
- [MCP: The Plumbing Behind Agent Tool Access](standards/mcp-protocol.md)
- [OpenAPI as Agent Tool Specification](standards/openapi-agent-tool-spec.md)
- [OpenTelemetry for Agent Observability](standards/opentelemetry-agent-observability.md)
- [Plugin and Extension Packaging](standards/plugin-packaging.md)
- [Tool Calling Schema Standards](standards/tool-calling-schema-standards.md)
- [Distributed AGENTS.md Conventions](instructions/agents-md-distributed-conventions.md)

## Development Workflows

> End-to-end processes — planning, bootstrapping, CI/CD integration, and team adoption.

- [Agent-Driven Greenfield Product Development](workflows/agent-driven-greenfield.md)
- [The AI Development Maturity Model](workflows/ai-development-maturity-model.md)
- [Content Pipeline: Idea to Published Page](workflows/content-pipeline.md)
- [Content & Skills Audit Workflow](workflows/content-skills-audit.md)
- [Continuous Agent Improvement](workflows/continuous-agent-improvement.md)
- [The Plan-First Loop: Design Before Code](workflows/plan-first-loop.md)
- [Repository Bootstrap Checklist](workflows/repository-bootstrap-checklist.md)
- [Team Onboarding for Agent Workflows](workflows/team-onboarding.md)
- [Vibe Coding: Outcome-Oriented Development](workflows/vibe-coding.md)
- [Browser Automation as a Research Tool](tool-engineering/browser-automation-for-research.md)
- [Headless Claude in CI](workflows/headless-claude-ci.md)

## Human Factors

> The human side — cognitive load, attention management, supervision, and team dynamics.

- [Human-in-the-Loop: Where and How to Supervise](workflows/human-in-the-loop.md)
- [Human-in-the-Loop Confirmation Gates](security/human-in-the-loop-confirmation-gates.md)
- [Developer as CPU Scheduler: Attention Management](human/attention-management-parallel-agents.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](human/cognitive-load-ai-fatigue.md)
- [Cross-Tool Translation](human/cross-tool-translation.md)
- [Initiatives and Community](human/initiatives-community.md)
- [Safe Command Allowlisting](human/safe-command-allowlisting.md)

## Anti-Patterns

> What to avoid — common mistakes and why they fail.

- [The Anthropomorphized Agent](anti-patterns/anthropomorphized-agent.md)
- [Cargo Cult Agent Setup](anti-patterns/cargo-cult-agent-setup.md)
- [The Copy-Paste Agent](anti-patterns/copy-paste-agent.md)
- [Distractor Interference](anti-patterns/distractor-interference.md)
- [Framework-First Agent Development](anti-patterns/framework-first.md)
- [The Infinite Context](anti-patterns/infinite-context.md)
- [The Mega-Prompt](instructions/instruction-compliance-ceiling.md)
- [Objective Drift](anti-patterns/objective-drift.md)
- [The Prompt Tinkerer](anti-patterns/prompt-tinkerer.md)
- [Indiscriminate Structured Reasoning](anti-patterns/reasoning-overuse.md)
- [The Kitchen Sink Session](anti-patterns/session-partitioning.md)
- [Single-Layer Prompt Injection Defence](anti-patterns/single-layer-injection-defence.md)
- [Trust Without Verify](anti-patterns/trust-without-verify.md)
- [Vibe Coding](workflows/vibe-coding.md)
- [The Yes-Man Agent](anti-patterns/yes-man-agent.md)

## Emerging Concepts

> Fringe ideas not yet standardized — early signals worth watching.

- [First-Party Agent Composition](emerging/first-party-agent-composition.md)
- [Hyper-Personalized Software](emerging/hyper-personalized-software.md)
- [Product-as-IDE](emerging/product-as-ide.md)

</div>
