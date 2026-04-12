---
title: "GoF Patterns and SOLID as Agent Design Vocabulary Bridge"
description: "Strategy, Observer, Circuit Breaker, Composite, and Saga map to agent system design — with a concern shift from reuse to control and safety."
aliases:
  - "GoF patterns for agents"
  - "SOLID principles for agents"
  - "classical patterns agent analogues"
tags:
  - agent-design
  - patterns
  - tool-agnostic
  - human-factors
  - workflows
---

# Classical SE Patterns as Agent Design Analogues

> Classical GoF patterns and SOLID principles have direct structural analogues in agent systems. The vocabulary transfers; the drivers shift from *reuse and maintainability* to *control, safety, and non-determinism*.

## The Core Qualification

Classical patterns are a **starting point**, not a blueprint. They solve code-organisation in deterministic systems; agent patterns solve coordination where trust boundaries, context limits, and unpredictable outputs dominate.

## Pattern Mapping

| Classical Pattern | Agent Analogue | Where It Appears |
|---|---|---|
| Strategy | [Cost-aware agent design](cost-aware-agent-design.md); tool selection | Routing classifies input and dispatches to specialised handlers — identical to Strategy's interchangeable algorithms |
| Observer | `PreToolUse`/`PostToolUse` hooks; tracing middleware | Hook pipelines and LangSmith-style middleware are structural Observer implementations |
| Circuit Breaker | `maxTurns`; [loop detection](../observability/loop-detection.md); backpressure | Budget-Constrained Execution Loop opens the circuit on repeated failure rather than retrying infinitely |
| Composite | [Orchestrator-worker](../multi-agent/orchestrator-worker.md); hierarchical decomposition | Hierarchical agent trees structurally mirror Composite — a root agent delegates to sub-agents that share the same callable interface |
| Saga | Multi-step agentic workflows with compensating actions | Each tool call is a saga step; the agent coordinates compensation when a step fails |
| Factory / Abstract Factory | [Dynamic tool](../anti-patterns/dynamic-tool-fetching-cache-break.md) instantiation; agent spawning | Tool Search Tool manufactures tool definitions on demand; sub-agent spawning is a factory operation |
| Decorator | Context injection middleware; summarisation wrapping | Middleware that adds context headers or wraps outputs before passing downstream |
| Chain of Responsibility | Hook pipelines; permission escalation chains | Sequential hook evaluation where each handler can accept, modify, or reject a tool call |
| Memento | Checkpointing; session recovery | Multi-session state resumption mirrors Memento — save state externally, restore on next session |
| Facade | `AGENTS.md` / `CLAUDE.md` as system interface | A single instruction file that hides internal complexity behind a stable interface |

## Behavioral Patterns (Strongest Transfer)

**Observer** — `PreToolUse`/`PostToolUse` hooks subscribe to tool-call events without coupling to the tool; safety gates and telemetry handlers are independent subscribers.

**Chain of Responsibility** — Hook pipelines pass tool calls through sequential handlers; each can approve, reject, or modify.

**Strategy** — [Anthropic's routing workflow](https://www.anthropic.com/engineering/building-effective-agents) classifies input and dispatches to a specialised model or prompt; the classifier is the Strategy context, the per-class handlers are the interchangeable algorithms.

## Resilience Patterns (Strong Transfer)

**Circuit Breaker** — `maxTurns` and loop-detection middleware open the circuit on repeated failure.

**Saga** — Each tool call is a saga step; on failure the agent runs compensating actions.

## Creational Patterns (Moderate Transfer)

**Factory / Abstract Factory** — Tool Search manufactures tool definitions on demand; sub-agent spawning is a factory operation — **context isolation** is the key constraint.

**Memento** — A `progress.md` checkpoint is Memento: store and retrieve state without exposing internals.

## Structural Patterns (Weakest Transfer)

**Composite** — Hierarchical agent frameworks structurally mirror Composite: a root agent delegates to sub-agents that expose the same callable interface, so the orchestrator treats a single agent or a whole subtree identically. The [Anthropic multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) implements this with an orchestrator-worker structure where a lead agent coordinates specialised subagents running in parallel.

**Facade** — `CLAUDE.md` and `AGENTS.md` act as Facades: a stable interface hiding internal complexity.

## Why It Works

Classical patterns capture stable structural relationships — how components connect and delegate — not implementation details. Those relationships (subscriber/publisher, context/strategy, component/composite) survive the shift from deterministic OOP to probabilistic LLM outputs because they are defined at the call-boundary level, not the computation level. An Observer hook doesn't care whether the subscribed handler executes a database query or an LLM inference; it only requires that subscribers can be registered and notified. The concern shift — from reuse and maintainability to control, safety, and non-determinism — happens *within* each pattern's role, not at the structural connection between roles.

## When This Backfires

Pattern vocabulary imports assumptions alongside structure. Apply these with caution in three situations:

- **Composite assumes a uniform interface**: classical Composite works because every node exposes the same method signature. Sub-agents return unstructured natural language by default; the uniform interface only holds if you enforce a strict output schema on every sub-agent, which adds engineering overhead that the pattern's simplicity hides.
- **Circuit Breaker assumes retriable failures**: the pattern opens on repeated failure and resets after a timeout. LLM failures are often prompt failures — retrying the same call after a timeout will fail again. The agent analogue needs a *different retry strategy* (reformulate the prompt, reduce scope), not just a wait.
- **Factory conflates instantiation with configuration**: in OOP, a factory creates an object with a fixed interface. Spawning a sub-agent requires also providing context, tools, and a system prompt — the "factory" must manage configuration state that has no analogue in classical Factory, making the metaphor leaky for teams who take it literally.

## Example

**Strategy routing** — A classifier subagent reads the task and returns one of `["code", "research", "write"]`. The harness dispatches to a specialised model per class. The router is the Strategy context; the per-class handlers are interchangeable algorithms. Adding a new handler requires no change to the router.

```yaml
# agent-routing.yml
routing:
  classifier: claude-3-5-haiku-20241022
  handlers:
    code: claude-3-5-haiku-20241022
    research: claude-3-7-sonnet-20250219
    write: claude-3-5-sonnet-20241022
```

**Observer via hooks** — A `PreToolUse` hook receives every tool call before execution. A telemetry handler and a safety-gate handler both subscribe; neither knows the other exists, and the tool does not know either handler runs.

## SOLID Reinterpreted

| Principle | Agent Reinterpretation |
|---|---|
| Single Responsibility | One agent, one domain — scope isolation prevents cross-contamination |
| Open/Closed | Add new skill files; do not modify the core harness instruction |
| Liskov Substitution | Sub-agents interchangeable for a role when outputs conform to the expected schema |
| Interface Segregation | Agents receive only the tools they need; broad tool access is a smell |
| Dependency Inversion | Agents depend on tool interfaces, not specific implementations |

## Related

- [AGENTS.md](../standards/agents-md.md) — Facade pattern in practice
- [CLAUDE.md Convention](../instructions/claude-md-convention.md) — Facade with four scopes
- [Hierarchical CLAUDE.md](../instructions/hierarchical-claude-md.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md) -- set up the Facade instruction file from scratch
- [Agent Backpressure](agent-backpressure.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Open Agent School Pattern Mapping](open-agent-school-pattern-mapping.md)
- [Multi-Agent SE Design Patterns Taxonomy](../multi-agent/multi-agent-se-design-patterns.md)
- [Rollback-First Design](rollback-first-design.md)
- [Agent Harness](agent-harness.md)
- [Advanced Tool Use](../tool-engineering/advanced-tool-use.md) — Tool Search as Factory pattern
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md)
- [WINK Agent Misbehavior Correction](wink-agent-misbehavior-correction.md)
- [Event-Driven Agent Routing](event-driven-agent-routing.md)
- [Idempotent Agent Operations](idempotent-agent-operations.md)
- [Agentic AI Architecture Evolution](agentic-ai-architecture-evolution.md)
- [Cognitive Reasoning and Execution Separation](cognitive-reasoning-execution-separation.md)
- [Execution-First Delegation](execution-first-delegation.md)
- [Agent Loop Middleware](agent-loop-middleware.md) — Chain of Responsibility and Observer in the agent loop
- [Harness Engineering](harness-engineering.md) — Factory and Facade patterns in harness design
- [Agent Turn Model](agent-turn-model.md)
- [Agentic Flywheel](agentic-flywheel.md)
- [Heuristic Effort Scaling](heuristic-effort-scaling.md)
- [Persona as Code](persona-as-code.md)
- [Temporary Compensatory Mechanisms](temporary-compensatory-mechanisms.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md) — SOLID layering applied
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — Saga and Circuit Breaker in failure recovery
- [Evaluator-Optimizer](evaluator-optimizer.md) — behavioral generator/evaluator loop
