---
title: "Discoverable vs Non-Discoverable Context for Agents"
description: "Agent instruction files should contain only non-discoverable context: architectural decisions, constraints, and domain knowledge not visible in code."
aliases:
  - non-discoverable context
tags:
  - context-engineering
  - tool-agnostic
---

# Discoverable vs Non-Discoverable Context

> Only put non-discoverable information in agent instruction files — if the agent can find it in the codebase, let it find it.

## The Cost of Instruction Files

Agent instruction files (AGENTS.md, CLAUDE.md, [copilot-instructions.md](../tools/copilot/copilot-instructions-md-convention.md)) are loaded into context on every interaction. Every line in those files consumes context budget before the agent starts any work. This makes the question of what to include a resource allocation decision, not a documentation exercise.

The test for inclusion is simple: can the agent discover this information itself using the tools available to it — file reads, grep, glob searches? If yes, the information does not belong in the instruction file.

## What Is Discoverable

Agents have read, search, and exploration tools. Everything reachable through those tools is discoverable:

- **File structure**: directory trees, module organization, entry points
- **API signatures**: function names, parameters, return types — present in the actual source
- **Test patterns**: how tests are structured, what test utilities are used — readable from test files
- **Dependency versions**: package.json, requirements.txt, go.mod are readable files
- **Code conventions**: variable naming, imports, error handling — visible in any existing file
- **Configuration**: .eslintrc, tsconfig.json, pyproject.toml are readable

Including any of these in an instruction file creates a maintenance problem: the instruction diverges from the real codebase as the project evolves. The agent follows a stale description of how things work rather than what is actually there.

## What Is Non-Discoverable

Some information cannot be inferred from the codebase through reading files:

- **Architectural decisions**: why this approach was chosen over alternatives — not visible in code
- **Constraints and gotchas**: "never deploy directly to prod-db, use the migration pipeline" — not encoded in files
- **Domain knowledge**: business rules, terminology, context the codebase assumes but doesn't explain
- **Non-obvious conventions**: "the `*Service` suffix is reserved for classes that talk to external APIs" — present in the pattern but not stated anywhere
- **Out-of-band context**: dependencies, integrations, or constraints that live outside the repository

These are the only things that earn a place in agent instruction files. The [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md) pattern applies the same logic at the macro level: keep the file as a pointer map, not an encyclopedia.

## Applying the Test

For each candidate entry in an instruction file, ask:

1. Can the agent discover this by reading the codebase?
2. If yes: remove it. Add a pointer if helpful ("see `src/repos/` for repository patterns").
3. If no: include it.

The pointer form is especially useful for discoverable content that benefits from direction. "Use the repository pattern in `src/repos/`" tells the agent where to look without duplicating what it will find there.

## Anti-Patterns

**Directory trees in instruction files**: The agent can run a glob. The tree in the file is stale within a sprint.

**Code samples that mirror real code**: The agent can read the real file. The sample drifts the moment the code changes.

**API signatures as documentation**: The agent can read the source. Duplicating signatures creates two sources of truth and one of them will be wrong.

## Example

The two CLAUDE.md snippets below show the same project described with discoverable content (before) versus non-discoverable content only (after).

```markdown
# Before — includes discoverable content (anti-pattern)

## Project Structure
- src/
  - api/         HTTP handlers
  - repos/       database repository layer
  - services/    business logic
  - utils/       shared helpers

## API Signatures
- `getUserById(id: string): Promise<User>`
- `createOrder(payload: OrderInput): Promise<Order>`

## Testing
Tests use Jest with `@testing-library/react`. Run with `npm test`.
```

```markdown
# After — non-discoverable content only

## Architectural Decisions
- The `*Service` suffix is reserved for classes that make outbound HTTP calls
  to third-party APIs. Internal business logic lives in plain classes without
  the suffix.
- We chose optimistic UI updates over server-confirmed writes to reduce
  perceived latency; the tradeoff is that rollback handling is mandatory in
  every mutation.

## Constraints
- Never write directly to the `orders` table. All order mutations must go
  through the `OrderService` to trigger the audit log side-effect.
- The `staging` environment shares the production read replica. Read-heavy
  queries against staging carry real production load.
```

The "after" version is shorter and will never go stale: the project structure, API signatures, and test runner are all readable directly from the codebase. The architectural decisions and operational constraints cannot be inferred from any file in the repository — these are the only entries that earn a place in the instruction file.

## Key Takeaways

- Instruction files load on every interaction — every line is a recurring cost.
- Discoverable information belongs in the codebase, not the instruction file.
- Non-discoverable information — decisions, constraints, domain context — earns a place in instruction files.
- Pointers ("see `src/repos/`") are preferable to copies of discoverable content.

## Related

- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md)
- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md) -- bootstrap an instruction file with only non-discoverable content
- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Context Priming: Pre-Loading Files for AI Agent Tasks](context-priming.md)
- [Retrieval-Augmented Agent Workflows: On-Demand Context](retrieval-augmented-agent-workflows.md)
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md)
- [Prompt Compression: Maximizing Signal Per Token](prompt-compression.md)
- [Prompt Layering: How Instructions Stack and Override](prompt-layering.md)
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Attention Sinks: Why First Tokens Always Win](attention-sinks.md)
