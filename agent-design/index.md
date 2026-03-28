---
title: "Agent Design Patterns and Architectures for AI Agents"
description: "Architecture, delegation, memory, control, reliability, and harness patterns for building effective AI coding agents and assistants."
tags:
  - agent-design
---

# Agent Design

> Architecture, delegation, memory, control, reliability, and harness patterns for building effective agents.

## Core Design

Foundational architecture decisions — how to structure agents, delegate work, and separate concerns.

- [Agent-First Software Design](agent-first-software-design.md) — Architect systems where AI agents are the primary consumers, using machine-readable APIs and structured outputs instead of visual UIs
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md) — Reference architecture separating cognitive reasoning from execution, a topology taxonomy for multi-agent coordination, and an enterprise hardening checklist
- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md) — A closed loop where agents analyze their own traces and metrics to generate harness improvements that make all future agent work better
- [Agents vs Commands: Separation of Role and Workflow](agents-vs-commands.md) — Commands define what to do; agents define who does it — separating orchestration from expertise lets you change either without touching the other
- [Classical SE Patterns as Agent Design Analogues](classical-se-patterns-agent-analogues.md) — Classical GoF patterns and SOLID principles have direct structural analogues in agent systems, with the concern shift moving from reuse to control and safety
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md) — Separate the agent layer that decides what to do from the layer that acts — typed tool interfaces enforce the boundary and make each independently testable
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md) — Agent delegation has overhead; match task characteristics to agent strengths rather than delegating everything or nothing
- [Empowerment Over Automation](empowerment-over-automation.md) — AI tools should skip tedious work while preserving your autonomy over architectural decisions, domain logic, and creative choices
- [Execution-First Delegation](execution-first-delegation.md) — Instead of scripting steps, specify the outcome and the boundaries; the agent determines how
- [Inversion Analysis: Surface Capabilities Competitors Cannot Replicate](inversion-analysis.md) — Inversion asks what your architecture enables that others cannot replicate, producing novel integrations rather than feature parity
- [Open Agent School Pattern Mapping](open-agent-school-pattern-mapping.md) — Map the Open Agent School academic pattern taxonomy to practical coding-agent primitives like maxTurns, PreToolUse hooks, and CLAUDE.md memory
- [Persona-as-Code: Defining Agent Roles as Structured Documents](persona-as-code.md) — Encode each agent's domain, responsibilities, constraints, output artifacts, and scope exclusions as a Markdown file so roles are explicit, auditable, and composable
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) — Structure agent systems in three layers — skills (knowledge), agents (execution), and commands (orchestration) — so each layer changes independently
- [Task-Specific Agents vs Role-Based Agents](task-specific-vs-role-based-agents.md) — Build agents for specific tasks rather than generic roles — narrow scope produces more precise output and reduces context confusion
- [Three Reasoning Spaces: Plan, Bead, and Code](three-reasoning-spaces.md) — Treat plan space, bead space, and code space as explicit gates — transitioning between them deliberately prevents architecture drift during implementation

## Memory & State

How agents persist, retrieve, and synthesize information across turns and sessions.

- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — Persist knowledge across conversations using scoped memory systems so agents accumulate institutional knowledge rather than starting fresh every session
- [Beads: Structured Task Graphs as External Agent Memory](beads-task-graph-agent-memory.md) — Use the bd CLI to maintain a git-backed dependency graph of work items so agents resume sessions methodically rather than re-discovering project state
- [Episodic Memory Retrieval](episodic-memory-retrieval.md) — Retrieve relevant past interaction episodes — not isolated facts — so agents recall what was tried, what failed, and what worked when facing similar problems
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — Extract causal lessons from agent execution traces — what worked, what failed, which approaches were abandoned and why — so every run makes future runs more effective
- [Session Initialization Ritual: How Agents Orient Themselves](session-initialization-ritual.md) — A mandatory startup sequence that every agent session executes before touching code — verify state, orient to progress, confirm baseline health, then act
- [Subtask-Level Memory for Software Engineering Agents](subtask-level-memory.md) — Store and retrieve memory at individual reasoning stages, not whole sessions, to prevent misguided retrieval when tasks share surface similarity

## Control & Orchestration

Patterns for steering agent behavior, detecting convergence, and managing execution flow.

- [Controlling Agent Output: Concise Answers, Not Essays](controlling-agent-output.md) — Matching the agent's response format to what you actually need reduces noise and preserves context budget
- [Convergence Detection in Iterative Refinement](convergence-detection.md) — Monitor three observable signals across refinement passes to replace intuition-based stopping with a mechanical criterion
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — Two distinct LLM roles in a loop: a generator produces output and an evaluator critiques it, feeding structured feedback back until a quality threshold is met
- [Event-Driven Agent Routing](event-driven-agent-routing.md) — Route work between agents and human teams by reacting to status-change events rather than maintaining a central coordinator that owns the full workflow
- [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md) — Planning tells the agent what to do; monitoring tells you whether it actually did it and whether it wandered off
- [Loop Strategy Spectrum: Accumulated, Compressed, and Fresh Context](loop-strategy-spectrum.md) — Choose between accumulated-context loops, within-session compression, and fresh-context loops based on workload type, not habit
- [Progressive Disclosure for Agent Definitions](progressive-disclosure-agents.md) — Keep agent definitions minimal — identity and scope only — and load detailed task knowledge on demand through skills rather than front-loading everything
- [Specialized Agent Roles](specialized-agent-roles.md) — Assign distinct specializations to parallel agents so they complement rather than compete on the same problems
- [Steering Running Agents: Mid-Run Redirection and Follow-Ups](steering-running-agents.md) — Send a mid-execution message that redirects tool calls without discarding the context already built

## Reliability

Making agents robust — backpressure, idempotency, cost awareness, error recovery, and self-correction.

- [Agent Backpressure: Automated Feedback for Self-Correction](agent-backpressure.md) — Automated tooling — type systems, test suites, linters, CI pipelines — creates feedback loops that agents use to self-correct without human intervention
- [Agent Self-Review Loop](agent-self-review-loop.md) — Agents review their own output — running code review, security scanning, and quality checks — before submitting work for human review
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — Match model capability to task complexity: fast models for exploration, capable models for implementation, powerful models for architecture
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md) — Assign competing vendor agents to the same task, collect independent results, and let a human or automated gate select the winner
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — Agents fail; the question is whether they fail forward (recover and continue) or fail catastrophically (corrupt state, lose progress, repeat work)
- [Heuristic-Based Effort Scaling in Agent Prompts](heuristic-effort-scaling.md) — Encode resource allocation rules in system prompts so agents spend proportional effort — few tool calls for simple lookups, many subagents for complex research
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — Design agent operations so that running the same task twice produces the same end state — not duplicate artifacts, conflicting state, or compounded errors
- [The Ralph Wiggum Loop: Fresh-Context Iteration Pattern](ralph-wiggum-loop.md) — Iterate in bounded units with fresh context each cycle, persisting state to disk between iterations, so context never accumulates to the point of degradation
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — Allocate maximum reasoning compute to planning and verification phases, reduced compute to execution — rather than using a fixed level throughout
- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md) — Before choosing how an agent will perform an action, choose how you will undo it — if recovery costs more than one command, reconsider the approach
- [Wink: Classifying and Auto-Correcting Coding Agent Misbehaviors](wink-agent-misbehavior-correction.md) — An async trajectory-observer system that classifies misbehaviors into three categories and injects targeted course-corrections

## Harness & Tools

The runtime infrastructure that hosts and constrains agent execution.

- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md) — Multi-agent workflows follow four structural patterns — sequential chains, parallel fan-out, staged pipelines, and supervisor-coordinator — each suited to different task structures
- [Agent Harness: Initializer and Coding Agent](agent-harness.md) — Structure long-running agent work as two distinct phases — an initializer that prepares the environment, and a coding agent that picks up reliably from wherever any prior session left off
- [Agent Loop Middleware](agent-loop-middleware.md) — Treat the agent loop as a unit to wrap from the outside; middleware nodes guarantee critical steps happen regardless of agent behavior
- [Agent Pushback Protocol](agent-pushback-protocol.md) — Agents evaluate requests at both implementation and requirements level, surface concerns, and wait for explicit confirmation before executing
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md) — A single user-facing turn is an iterative sequence of model inference and tool execution steps, not a single round-trip inference call
- [Harness Engineering](harness-engineering.md) — The discipline of designing agent environments — layered architecture, mechanical enforcement, legibility — so agents reliably produce correct results
- [Temporary Compensatory Mechanisms](temporary-compensatory-mechanisms.md) — Design scaffolding that compensates for current model limitations as removable layers, not load-bearing architecture
- [The Think Tool](think-tool.md) — A mid-stream reasoning checkpoint that fires between tool calls, giving agents an explicit space to reflect on tool output before deciding the next action
