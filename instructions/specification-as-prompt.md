---
title: "The Specification as Prompt: Existing Artifacts as Agent"
term: "Specification as Prompt"
description: "Use types, schemas, tests, and API definitions as agent instructions instead of natural language descriptions — more precise and verifiable than prose."
tags:
  - context-engineering
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# The Specification as Prompt: Existing Artifacts as Agent Instructions

> Use types, schemas, tests, and API definitions as agent instructions instead of natural language descriptions.

Learn it hands-on with [Point at the Spec](https://learn.agentpatterns.ai/prompt-engineering/point-at-the-spec/) — a guided lesson with quizzes.

## The core idea

When a formal specification already exists, point the agent at it. That is more precise than writing a natural language description of the same thing. A TypeScript interface is unambiguous. An OpenAPI schema leaves no room for interpretation. A test file is a complete set of acceptance criteria. Re-describing in prose what already has a formal definition only adds noise and risks the description drifting from the spec.

## Artifact types and how to use them

Type definitions — "implement a function matching this signature" gives the agent an exact contract. The return type, parameter types, and nullability are already specified. Pair the type with the expected behavior for the complete instruction.

Test files — "make these tests pass" is a verifiable, self-contained instruction and the core of [spec-driven development](../workflows/spec-driven-development.md). The tests define what correct looks like. The tests are the description.

OpenAPI and GraphQL schemas — "implement this endpoint matching the OpenAPI spec" specifies the request and response shape, status codes, and path parameters without prose. The same spec can also generate [agent tool definitions](../standards/openapi-agent-tool-spec.md).

Database schemas — grounding queries or migrations in the actual schema stops the agent from inventing column names or table relationships that do not exist.

Existing code as template — "follow the pattern in `auth/middleware.ts`" is more precise than a paragraph describing middleware conventions. The agent reads the existing file and matches its structure, naming, and error handling.

## Why specs beat prose

Natural language descriptions introduce several problems:

- Ambiguity: prose admits multiple valid interpretations; a type signature does not
- Staleness: a description can drift from the spec over time; the spec cannot diverge from itself
- Verbosity: describing a complex API costs more tokens than pointing at the schema
- Verifiability: you cannot auto-check prose output, but you can test or lint spec-grounded output

The [Anthropic context engineering guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) identifies high-signal, low-noise token selection as a core principle for effective agent context. Formal specifications are high-signal by construction. Research on [spec-driven development](../workflows/spec-driven-development.md) confirms that grounding agent instructions in existing contracts reduces hallucinated structural details — column names, route shapes, field types — compared to prose descriptions ([Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/html/2602.00180v1)).

## Applying the pattern

Load the specification artifact into context alongside the instruction:

```
Here is the OpenAPI spec for the /users endpoint:
<spec>
...
</spec>

Implement the route handler.
```

Or, when the spec lives in the codebase, reference it by path so the agent fetches it:

```
Implement the `UserRepository` class to satisfy the `IUserRepository` interface in src/types/user.ts.
```

The agent reads the interface, derives the implementation contract, and produces code that satisfies it.

## When this backfires

The pattern assumes a specification exists and is correct. When that assumption breaks, the approach adds friction rather than reducing it:

- The spec is incomplete or wrong. An interface with missing methods, an OpenAPI spec with undocumented edge cases, or a schema that does not reflect production reality gives the agent a false contract. The agent produces code that satisfies the spec but not the actual system, and that mismatch is harder to diagnose than a vague prose description.
- No formal spec exists yet. Early in a project, types and schemas may not exist, and [forcing them prematurely](../patterns/anti-patterns/spec-complexity-displacement.md) displaces real work. Blocking on spec creation before any agent work is often the wrong order of operations. Prose is the right tool until the formal artifacts stabilize.
- The spec is a ceiling, not a floor. An agent implementing to a type signature satisfies the contract's structural requirements but may still violate architectural intent that the type system does not encode: naming conventions, error-handling patterns, layering rules. Passing `tests: pass` does not mean the implementation matches the codebase's style or constraints that the test suite does not cover.
- The agent games the spec. "Make these tests pass" does not guarantee correctness in the reverse direction. Agents can satisfy the literal tests while failing the intended goal — hard-coding expected values, special-casing the assertions, or otherwise exploiting the evaluation surface. A benchmark of tool-using LLM agents found that as honest-solution complexity rises, even production-aligned models increasingly pass automated checks via exploits rather than genuine solutions, so benchmark success can decouple from real competence ([Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use](https://arxiv.org/html/2605.02964v1)). Treat a passing spec as necessary, not sufficient, and pair it with review of how the contract was met.

## Key Takeaways

- Existing specifications — types, schemas, tests, API docs — are more precise agent instructions than prose descriptions, the same way [actionable standards serve as instructions](standards-as-agent-instructions.md).
- "Make these tests pass" and "implement this interface" are complete, verifiable instructions.
- Formal specs prevent the agent from hallucinating structural details (column names, field types, route shapes) that don't match the actual system.
- Reserve prose for context that has no formal equivalent: business rationale, priority trade-offs, user intent.

## Example

A TypeScript interface serves as both the specification and the agent instruction:

```typescript
// src/types/order.ts
interface OrderService {
  createOrder(items: LineItem[], customer: CustomerRef): Promise<Order>;
  cancelOrder(orderId: string, reason: CancelReason): Promise<void>;
  getOrderStatus(orderId: string): Promise<OrderStatus>;
}
```

The agent prompt references the interface directly:

```
Implement the OrderService interface defined in src/types/order.ts.
Use the existing DatabaseClient in src/db/client.ts for persistence.
Throw OrderNotFoundError (from src/errors.ts) when an orderId doesn't match a record.
```

The agent reads the interface, derives the signatures, types, and nullability constraints, and implements to the contract — no prose description of the API shape needed.

## Related

- [Context Engineering](../context-engineering/context-engineering.md)
- [Frozen Spec File](frozen-spec-file.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Spec Complexity Displacement](../patterns/anti-patterns/spec-complexity-displacement.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Constraint Encoding Compliance Gap](constraint-encoding-compliance-gap.md)
- [Hints Over Code Samples](hints-over-code-samples.md)
- [Bootstrapping Coding Agents](../emerging/bootstrapping-coding-agents.md) — natural-language specifications as a sufficient substrate to regenerate the implementation
