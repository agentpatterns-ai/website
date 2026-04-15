---
title: "Codebase Readiness for Agents: Agent-Friendly Code"
description: "Agents produce better output in codebases with strong types, comprehensive tests, and documented decisions — the same qualities that improve code for humans."
tags:
  - agent-design
aliases:
  - agent-friendly code
  - codebase readiness
---

# Codebase Readiness for Agents: What Makes Code Agent-Friendly

> Agents produce better output in codebases with strong types, comprehensive tests, consistent patterns, and documented decisions — the same qualities that improve code for humans.

## Agent-Hostile vs. Agent-Friendly

Agents don't work from requirements. They pattern-match against existing code. A codebase with weak types, no tests, inconsistent patterns, and undocumented decisions gives agents nothing to match against — so they invent.

The solution is not better prompts. It is better code.

## Readiness Dimensions

### Types

Strong type annotations tell agents what functions expect, what they return, and what invariants the code maintains. When types are absent or are `any`/`unknown`, agents fill in with guesses. Type errors from the compiler become [backpressure](../agent-design/agent-backpressure.md) — immediate, precise feedback the agent can act on.

### Tests

A comprehensive test suite gives agents a binary answer to "did I break anything?" Agents can run tests, read failure output, fix the issue, and run again without human intervention. A codebase without tests forces every agent output through human review.

### Consistent Patterns

Agents extrapolate patterns from what they observe. Inconsistent code produces inconsistent agent output. If three modules do the same thing three different ways, an agent writing a fourth will pick one arbitrarily — or invent a fourth way.

### Decision Comments

Intentional choices get reverted when agents don't know they were intentional. A comment explaining why an unusual approach was taken — "Using X instead of Y because Y doesn't handle Z" — survives context resets and prevents agents from "fixing" deliberate decisions.

### Directory Structure

Agents navigate by convention. A clear, predictable directory structure lets agents determine where new files belong without asking. Flat directories with mixed concerns force agents to guess.

### Project Instructions

[AGENTS.md and equivalent project instruction files](https://agents.md) provide [non-discoverable context](../context-engineering/discoverable-vs-nondiscoverable-context.md): decisions that can't be inferred from code alone. Architecture choices, external constraints, "don't do X because" rules. The AGENTS.md format is now an [open standard stewarded by the Linux Foundation's Agentic AI Foundation](https://www.infoq.com/news/2025/08/agents-md/), with wide adoption across coding-agent tools.

## Readiness Signals

| Signal | Agent-Friendly | Agent-Hostile |
|--------|---------------|---------------|
| Types | Strict, complete | `any`, untyped |
| Tests | High coverage, meaningful | None or low coverage |
| Patterns | Consistent across modules | Mixed, inconsistent |
| Comments | Decision points documented | None |
| Files | Small, single-responsibility | Large, mixed-concern |
| Project instructions | Present and current | Absent |

## Compounding Investment

Improving codebase readiness benefits agents and human developers identically — it's the same work. Adding types, writing tests, and documenting decisions are not agent-specific investments. They pay off regardless of whether an agent is involved.

## When Readiness Investment Backfires

Readiness work has real costs and does not always dominate. Consider deferring it when:

- **The code is throwaway.** Prototypes, spikes, and one-off scripts may never survive long enough to amortise the investment. Strict types and test scaffolding slow the exploration loop.
- **Patterns are premature.** Locking in conventions before the shape of the problem is understood produces rigid scaffolding that agents then faithfully extend in the wrong direction. Early code is often better left malleable.
- **The codebase is large enough that local readiness doesn't help.** Pattern-matching breaks down across enterprise codebases with hundreds of thousands of files regardless of how clean any single module is ([Qodo, 2025](https://www.qodo.ai/reports/state-of-ai-code-quality/)). Readiness is necessary but not sufficient at scale; retrieval, sub-agents, and architectural boundaries carry more weight than local hygiene.
- **Documentation drifts faster than it helps.** Large AGENTS.md files and verbose decision comments that go stale produce false confidence — agents trust out-of-date guidance and make it worse. If you cannot maintain the prose, terser is safer.

## Example

The two TypeScript snippets below show the same utility function before and after applying codebase readiness improvements. The agent-hostile version gives an agent nothing to pattern-match: no types, no test, no explanation of the deliberate behaviour.

```typescript
// Before: agent-hostile
// No types, no tests, no decision comment
export function paginate(items, page, size) {
  return items.slice((page - 1) * size, page * size);
}
```

```typescript
// After: agent-friendly
/**
 * Returns a single page of items from a zero-indexed array.
 *
 * NOTE: `page` is 1-based (first page = 1), not 0-based.
 * This matches the API contract defined in docs/conventions/pagination.md.
 * Do not change to 0-based without updating the API contract first.
 */
export function paginate<T>(items: T[], page: number, pageSize: number): T[] {
  if (page < 1) throw new RangeError(`page must be >= 1, got ${page}`);
  if (pageSize < 1) throw new RangeError(`pageSize must be >= 1, got ${pageSize}`);
  return items.slice((page - 1) * pageSize, page * pageSize);
}
```

```typescript
// paginate.test.ts
import { paginate } from "./paginate";

test("returns correct slice for page 1", () => {
  expect(paginate([1, 2, 3, 4, 5], 1, 2)).toEqual([1, 2]);
});

test("returns correct slice for page 2", () => {
  expect(paginate([1, 2, 3, 4, 5], 2, 2)).toEqual([3, 4]);
});

test("throws on zero page", () => {
  expect(() => paginate([], 0, 10)).toThrow(RangeError);
});
```

The decision comment explains the 1-based convention and where the contract lives. An agent extending or refactoring this function will preserve the behaviour rather than silently switching to 0-based indexing because "that's the usual convention".

## Key Takeaways

- Agent output quality correlates with codebase quality — weak types, no tests, and inconsistent patterns produce worse agent output.
- Decision comments prevent agents from reverting intentional choices.
- Consistent patterns give agents correct examples to extrapolate from.
- Improving codebase readiness for agents and improving it for humans are the same task.

## Related

- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Convention Over Configuration](../instructions/convention-over-configuration.md)
- [The Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md)
- [Getting Started: Setting Up Your Instruction File](getting-started-instruction-files.md)
- [Agent-Driven Greenfield Projects](agent-driven-greenfield.md)
- [Repository Bootstrap Checklist](repository-bootstrap-checklist.md)
- [Lay the Architectural Foundation First](architectural-foundation-first.md)
