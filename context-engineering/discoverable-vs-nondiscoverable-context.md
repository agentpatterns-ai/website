---
title: "Discoverable vs Non-Discoverable Context for Agents"
term: "Discoverable vs Non-Discoverable Context"
description: "Agent instruction files should contain only non-discoverable context: architectural decisions, constraints, and domain knowledge not visible in code."
aliases:
  - non-discoverable context
tags:
  - context-engineering
  - tool-agnostic
  - instructions
last_reviewed: 2026-06-13
maturity: adopted
---

# Discoverable vs Non-Discoverable Context

> Only put non-discoverable information in agent instruction files — if the agent can find it in the codebase, let it find it.

Learn it hands-on: [Discoverable or Not](https://learn.agentpatterns.ai/context-engineering/discoverable-or-not/) — guided lesson with quizzes.

## The cost of instruction files

Agent instruction files (AGENTS.md, CLAUDE.md, [copilot-instructions.md](../tools/copilot/copilot-instructions-md-convention.md)) load into context on every interaction. Every line spends context budget before the agent starts work. So each line you add is a resource-allocation decision, not a documentation exercise.

The test for inclusion is simple. Can the agent find this itself with its own tools — file reads, grep, glob searches? If yes, the information does not belong in the instruction file.

## What is discoverable

Agents have read, search, and exploration tools. Everything those tools can reach is discoverable:

- File structure: directory trees, module organization, entry points
- API signatures: function names, parameters, return types, all present in the source
- Test patterns: how tests are structured and what test utilities they use, readable from test files
- Dependency versions: package.json, requirements.txt, and go.mod are readable files
- Code conventions: variable naming, imports, error handling, visible in any existing file
- Configuration: .eslintrc, tsconfig.json, and pyproject.toml are readable

Including any of these creates a maintenance problem. The instruction drifts from the real codebase as the project evolves, and the agent then follows a stale description rather than the code itself.

## What is non-discoverable

Some information you cannot infer from the codebase by reading files:

- Architectural decisions: why this approach was chosen over alternatives, not visible in code
- Constraints and gotchas: "never deploy directly to prod-db, use the migration pipeline", not encoded in files
- Domain knowledge: business rules, terminology, and context the codebase assumes but does not explain
- Non-obvious conventions: "the `*Service` suffix is reserved for classes that talk to external APIs", present in the pattern but stated nowhere
- Out-of-band context: dependencies, integrations, or constraints that live outside the repository

These are the only things that earn a place in agent instruction files. Anthropic's own Claude Code guide draws the same line: exclude "anything Claude can figure out by reading code," because "bloated CLAUDE.md files cause Claude to ignore your actual instructions" ([Anthropic, "Best Practices for Claude Code"](https://code.claude.com/docs/en/best-practices)). The [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md) pattern applies the same logic at the macro level: keep the file as a pointer map, not an encyclopedia.

## Applying the test

For each candidate entry in an instruction file, ask:

1. Can the agent discover this by reading the codebase?
2. If yes, remove it. Add a pointer if it helps ("see `src/repos/` for repository patterns").
3. If no, include it.

The pointer form works well for discoverable content that benefits from direction. "Use the repository pattern in `src/repos/`" tells the agent where to look without duplicating what it will find there.

## Why it works

Instruction files sit at the front of every context window before the agent reads a single file. Discoverable content placed there competes with task context for limited space. It also creates a second source of truth that drifts from the codebase over time. An agent given a stale directory tree may read paths that no longer exist or skip new modules. A controlled evaluation found that human-authored context files raise inference cost by over 20% when they include structural overviews, with no gain in task success. Agents given high-level structural context explore the codebase more broadly, not more precisely ([Gloaguen et al., "Evaluating AGENTS.md," 2026](https://arxiv.org/abs/2602.11988)).

## Anti-patterns

These 3 habits smuggle discoverable content into an instruction file:

- Directory trees: the agent can run a glob, and the tree in the file is stale within a sprint.
- Code samples that mirror real code: the agent can read the real file, and the sample [drifts the moment the code changes](../instructions/agents-md-as-table-of-contents.md).
- API signatures as documentation: the agent can read the source. Duplicating signatures creates two sources of truth, and one of them will be wrong.

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

The "after" version is shorter and will never go stale. The project structure, API signatures, and test runner are all readable directly from the codebase. The architectural decisions and operational constraints cannot be inferred from any file in the repository. These are the only entries that earn a place in the instruction file.

## When this backfires

The split breaks down in 3 cases:

- Agents without exploration tools: if the agent lacks file-read or search tools, the discoverable and non-discoverable split collapses. Structural information becomes non-discoverable to that agent, so check tool access before you apply this filter.
- Large monorepos: with hundreds of modules, a scoped pointer ("see `services/payments/`") crosses into discoverable territory but may be worth including to prevent broad traversal. The pointer form, a path rather than a full tree, limits token cost.
- High-churn codebases: context files go stale within a sprint during rapid restructuring. Lean toward non-discoverable content, and keep any structural pointers in a separate, frequently updated file rather than the main instruction file.

## Key Takeaways

- Run the discoverability test before adding a line: if the agent can find it in the codebase, cut it or leave a pointer instead.
- Without file-read or search tools, an agent cannot discover anything on its own, so check tool access before applying this split.
- In large monorepos, a scoped pointer such as `services/payments/` is worth keeping even though it is technically discoverable, since it prevents broad traversal.
- In high-churn codebases, keep structural pointers in a separate, frequently updated file, since embedded structure goes stale within a sprint.

## Related

- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](../instructions/agents-md-as-table-of-contents.md)
- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Getting Started: Setting Up Your Instruction File](../instructions/getting-started-instruction-files.md) -- bootstrap an instruction file with only non-discoverable content
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Layered Context Architecture](layered-context-architecture.md)
