---
title: "Classical SE Patterns as Agent Design Analogues"
description: "Strategy, Observer, Circuit Breaker, Composite, and Saga map to agent system design — with a concern shift from reuse to control and safety."
aliases:
  - "GoF patterns for agents"
  - "SOLID principles for agents"
  - "classical patterns agent analogues"
tags:
  - agent-design
  - pattern
  - tool-agnostic
  - human-factors
  - workflows
last_reviewed: 2026-06-12
maturity: emerging
---

# Classical SE Patterns as Agent Design Analogues

> Classical GoF patterns and SOLID principles have direct structural analogues in agent systems. The vocabulary transfers; the drivers shift from *reuse* to *control and safety*.

## The core qualification

Classical patterns are a starting point, not a blueprint. They solve code organization in deterministic systems. Agent patterns solve coordination where trust boundaries, context limits, and unpredictable outputs dominate.

## Pattern mapping

| Classical Pattern | Agent Analogue |
|---|---|
| Strategy | [Cost-aware routing](../token-engineering/cost-aware-agent-design.md); classifier dispatches to specialised handlers |
| Observer | `PreToolUse`/`PostToolUse` hooks; tracing middleware as independent subscribers |
| Circuit Breaker | `maxTurns`; [loop detection](../observability/loop-detection.md); backpressure on repeated failure |
| Composite | [Orchestrator-worker](../multi-agent/orchestrator-worker.md); sub-agents share the callable interface |
| Saga | Multi-step workflows where each tool call is a step with compensating actions on failure |
| Factory / Abstract Factory | [Dynamic tool](../anti-patterns/dynamic-tool-fetching-cache-break.md) instantiation; sub-agent spawning |
| Decorator | Context-injection middleware; summarisation wrapping outputs before passing downstream |
| Chain of Responsibility | Hook pipelines; permission escalation chains that approve, modify, or reject |
| Memento | Checkpointing; multi-session state resumption stored externally |
| Facade | `AGENTS.md` / `CLAUDE.md` as a stable interface hiding internal complexity |

## Behavioral patterns (strongest transfer)

- Observer — `PreToolUse` and `PostToolUse` hooks subscribe to tool-call events. Safety gates and telemetry are independent subscribers.
- Chain of Responsibility — Hook pipelines pass calls through sequential handlers. Each handler can approve, reject, or modify.
- Strategy — [Anthropic's routing workflow](https://www.anthropic.com/engineering/building-effective-agents) classifies input and dispatches to a specialized model. The per-class handlers are the interchangeable algorithms.

## Resilience patterns (strong transfer)

- Circuit Breaker — `maxTurns` and loop-detection middleware open the circuit on repeated failure.
- Saga — Each tool call is a saga step. On failure the agent runs compensating actions.

## Creational patterns (moderate transfer)

- Factory / Abstract Factory — Tool Search manufactures tool definitions on demand. Sub-agent spawning is a factory operation, and context isolation is the main constraint.
- Memento — A `progress.md` checkpoint is Memento: store and retrieve state without exposing internals.

## Structural patterns (weakest transfer)

- Composite — Hierarchical agent frameworks mirror Composite: the orchestrator treats a single sub-agent or a whole subtree identically. The [Anthropic multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) implements this with a lead agent coordinating specialized subagents in parallel.
- Facade — `CLAUDE.md` and `AGENTS.md` act as Facades: a stable interface hiding internal complexity.

## Why it works

Classical patterns capture stable structural relationships — how components connect and delegate — not implementation details. Those relationships (subscriber/publisher, context/strategy, component/composite) survive the shift from deterministic OOP to probabilistic LLM outputs. They survive because they are defined at the call-boundary level, not the computation level. An Observer hook (`PreToolUse`/`PostToolUse`) does not care whether the handler runs a database query or an LLM inference; it only requires that subscribers can be registered and notified. The concern shift — from reuse to control and safety — happens within each role, not at the structural connection between roles.

## When this backfires

Pattern vocabulary imports assumptions alongside structure. Apply each one with caution:

- Composite assumes a uniform interface: sub-agents return unstructured natural language by default. The uniform interface holds only if you enforce a strict output schema on every sub-agent, which hides real engineering overhead.
- [Circuit Breaker](exception-handling-recovery-patterns.md) assumes retriable failures: LLM failures are often prompt failures, so retrying the same call after a timeout fails again. The agent analogue needs a different retry strategy (reformulate, reduce scope), not just a wait.
- Factory conflates instantiation with configuration: spawning a sub-agent also requires context, tools, and a system prompt. That state has no analogue in classical Factory, which makes the metaphor leaky.

## Example

Strategy routing — A classifier subagent reads the task and returns one of `["code", "research", "write"]`. The harness dispatches to a specialized model per class. The router is the Strategy context; the per-class handlers are interchangeable algorithms. Adding a new handler requires no change to the router.

```yaml
# agent-routing.yml
routing:
  classifier: claude-3-5-haiku-20241022
  handlers:
    code: claude-3-5-haiku-20241022
    research: claude-3-7-sonnet-20250219
    write: claude-3-5-sonnet-20241022
```

Observer via hooks — A `PreToolUse` hook receives every tool call before execution. A telemetry handler and a safety-gate handler both subscribe. Neither knows the other exists, and the tool does not know either handler runs.

## SOLID reinterpreted

| Principle | Agent Reinterpretation |
|---|---|
| Single Responsibility | One agent, one domain — scope isolation prevents cross-contamination |
| Open/Closed | Add new skill files; do not modify the core harness instruction |
| Liskov Substitution | Sub-agents interchangeable for a role when outputs conform to the expected schema |
| Interface Segregation | Agents receive only the tools they need; broad tool access is a smell |
| Dependency Inversion | Agents depend on tool interfaces, not specific implementations |

## Key Takeaways

- Classical patterns transfer their structure (subscriber/publisher, context/strategy, component/composite) but not their drivers — agent systems optimise for control and safety, not reuse.
- Behavioral patterns (Observer, Chain of Responsibility, Strategy) transfer most cleanly; structural patterns (Composite, Facade) transfer weakest because the uniform interface depends on enforced output schemas.
- Treat the mapping as a starting vocabulary, not a blueprint: each metaphor imports assumptions (retriable failures, uniform interfaces, stateless instantiation) that LLM non-determinism can break.

## Related

- [Multi-Agent SE Design Patterns Taxonomy](../multi-agent/multi-agent-se-design-patterns.md) — the broader pattern catalogue this page maps into
- [Orchestrator-Worker](../multi-agent/orchestrator-worker.md) — Composite pattern realised
- [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md) — Chain of Responsibility and Observer in the agent loop
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — Saga and Circuit Breaker in failure recovery
- [Advanced Tool Use](../tool-engineering/advanced-tool-use.md) — Tool Search as Factory pattern
- [Harness Engineering](harness-engineering.md) — Factory and Facade patterns in harness design
- [AGENTS.md](../standards/agents-md.md) — Facade pattern in practice
- [Open Agent School Pattern Mapping](open-agent-school-pattern-mapping.md) — a parallel classical-to-agent mapping
</content>
</invoke>
