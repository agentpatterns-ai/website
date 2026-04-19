---
title: "The Specification as Prompt: Existing Artifacts as Agent"
description: "Use types, schemas, tests, and API definitions as agent instructions instead of natural language descriptions — more precise and verifiable than prose."
tags:
  - context-engineering
  - instructions
---

# The Specification as Prompt: Existing Artifacts as Agent Instructions

> Use types, schemas, tests, and API definitions as agent instructions instead of natural language descriptions.

## The Core Idea

When a formal specification already exists, pointing the agent at it is more precise than writing a natural language description of the same thing. A TypeScript interface is unambiguous. An OpenAPI schema leaves no room for interpretation. A test file is a complete set of acceptance criteria.

Writing a prose description of something that already has a formal definition introduces noise and the risk of divergence between the description and the specification.

## Artifact Types and How to Use Them

**Type definitions** — "Implement a function matching this signature" gives the agent an exact contract. The return type, parameter types, and nullability are already specified. Pairing the type with the expected behavior is the complete instruction.

**Test files** — "Make these tests pass" is a verifiable, self-contained instruction. The tests define what correct looks like. The agent cannot produce an implementation that satisfies your description but fails the tests — the tests are the description.

**OpenAPI and GraphQL schemas** — Schema-first API development produces definitions the agent can implement directly. "Implement this endpoint matching the OpenAPI spec" specifies the request/response shape, status codes, and path parameters without prose. OpenAPI specs can also serve as the source for [agent tool definitions](../standards/openapi-agent-tool-spec.md) — the same spec that documents the API generates the tool schema.

**Database schemas** — Grounding queries or migrations in the actual schema prevents the agent from making up column names or table relationships that don't exist.

**Existing code as template** — "Follow the pattern in `auth/middleware.ts`" is more precise than a paragraph describing middleware conventions. The agent can read the existing file and match its structure, naming, and error handling.

## Why Specs Beat Prose

Natural language descriptions introduce several problems:

- **Ambiguity**: prose admits multiple valid interpretations; a type signature does not
- **Staleness**: a description can diverge from the actual spec over time; the spec cannot diverge from itself
- **Verbosity**: writing a complete description of a complex API takes more tokens and more effort than pointing at the schema
- **Verifiability**: prose output cannot be automatically checked; spec-grounded output can be tested, validated, or linted

The [Anthropic context engineering guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) identifies high-signal, low-noise token selection as a core principle for effective agent context. Formal specifications are high-signal by construction. Research on [spec-driven development](https://arxiv.org/html/2602.00180v1) confirms that grounding agent instructions in existing contracts reduces hallucinated structural details — column names, route shapes, field types — compared to prose descriptions.

## Applying the Pattern

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

## When This Backfires

The pattern assumes a specification exists and is correct. When that assumption breaks, the approach adds friction rather than reducing it:

- **The spec is incomplete or wrong.** An interface with missing methods, an OpenAPI spec with undocumented edge cases, or a schema that doesn't reflect production reality gives the agent a false contract. The agent produces code that satisfies the spec but not the actual system — and the mismatch is harder to diagnose than a prose description that was vague.
- **No formal spec exists yet.** Early in a project, types and schemas may not exist. Blocking on spec creation before any agent work is often the wrong order of operations; prose is the right tool until the formal artifacts stabilize.
- **The spec is a ceiling, not a floor.** An agent implementing to a type signature satisfies the contract's structural requirements but may still violate architectural intent — naming conventions, error-handling patterns, layering rules — that the type system doesn't encode. Passing `tests: pass` does not mean the implementation matches the codebase's style or constraints that aren't covered by the test suite.

## Key Takeaways

- Existing specifications — types, schemas, tests, API docs — are more precise agent instructions than prose descriptions.
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

The agent reads the interface, derives the method signatures, parameter types, return types, and nullability constraints, then produces an implementation that satisfies the contract. No prose description of the API shape is needed — the type definition is the instruction.

## Related

- [Context Engineering](../context-engineering/context-engineering.md)
- [Frozen Spec File](frozen-spec-file.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Spec Complexity Displacement](../anti-patterns/spec-complexity-displacement.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Constraint Encoding Compliance Gap](constraint-encoding-compliance-gap.md)
- [Hints Over Code Samples](hints-over-code-samples.md)
- [Bootstrapping Coding Agents](../emerging/bootstrapping-coding-agents.md) — natural-language specifications as a sufficient substrate to regenerate the implementation
