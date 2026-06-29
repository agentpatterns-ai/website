---
title: "Deferred Standards Enforcement via Review Agents"
description: "Move post-hoc-checkable standards out of CLAUDE.md into a reviewer agent that runs at PR time — saving implementation context for code understanding, spending it at review where compliance checking is the entire job."
tags:
  - code-review
  - instructions
  - context-engineering
  - tool-agnostic
aliases:
  - "CLAUDE.md standards split"
  - "review-time standards enforcement"
last_reviewed: 2026-06-13
maturity: adopted
---

# Deferred Standards Enforcement via Review Agents

> Move post-hoc-checkable standards out of CLAUDE.md into a reviewer agent that runs at PR time — preserving implementation context budget for the task at hand.

## The problem with standards in CLAUDE.md

CLAUDE.md loads into every Claude Code session. Every line it contains costs tokens on every task, whether or not those tokens matter to the work in that session ([Claude Code memory docs](https://code.claude.com/docs/en/memory)). Anthropic frames this as an attention budget: in a fully packed context, preloaded content competes with task instructions, tool results, and code for the model's attention ([Anthropic: Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); see also [Context Engineering](../context-engineering/context-engineering.md)).

Standards documents can be large. Style guides, compliance checklists, naming conventions, and API requirements all add up. Load all of them into every implementation session and the agent writing code carries the same context as the agent that should be reviewing it — a phase mismatch.

## The split

Not all standards need to be present during code generation. Standards fall into two types:

Generation-shaping standards affect the structure of the code being written. The agent must know these during generation — they belong with the other [standards loaded as agent instructions](../instructions/standards-as-agent-instructions.md) — or it makes architectural decisions that need rework, not revision.

Examples: "Every new API endpoint requires an integration test", "Use repository pattern for all database access", "API keys must come from environment variables, never hardcoded"

Post-hoc-checkable standards can be verified after the code is written, without the agent having known them during generation.

Examples: Style conventions, comment formatting, import ordering, file naming, line length limits, log format requirements

Post-hoc-checkable standards belong in a reviewer agent. Generation-shaping standards belong in CLAUDE.md.

## Implementation: CLAUDE.md and REVIEW.md

Anthropic's [Claude Code Review](../tools/claude/code-review.md) product formalizes this split directly. The [Code Review documentation](https://code.claude.com/docs/en/code-review) defines two files:

- `CLAUDE.md`: shared project instructions for all Claude Code tasks, including implementation sessions
- `REVIEW.md`: review-only guidance, read only during code reviews — "for rules that are strictly about what to flag or skip during review and would clutter your general `CLAUDE.md`"

The review agent reads `REVIEW.md` at PR time. The implementation agent never sees it. Each phase gets the context its task needs.

For teams running custom review agents rather than Claude Code Review, the same split applies: keep `REVIEW.md` (or an equivalent reviewer agent instruction file) separate from `CLAUDE.md`, and load it only when the review agent runs.

## Example

`REVIEW.md` holds review-only rules, never loaded during implementation:

```markdown
# Code Review Guidelines

## Always flag
- New public functions missing type annotations
- Log calls using f-string interpolation (use structured logging)
- Error messages that include internal stack traces or paths

## Skip
- Formatting in generated files under `src/gen/`
- Import ordering in migration files
```

`CLAUDE.md` holds implementation context, stripped of reviewable-only rules:

```markdown
# Project Instructions

## Architecture
- Use repository pattern for all database access (see src/db/repositories/)
- Every new API endpoint requires a corresponding integration test in tests/api/

## Commands
- Build: `make build`
- Test: `make test`
- Lint: `make lint`
```

The implementation agent carries only what shapes code decisions. The review agent loads the full compliance checklist at PR time, in a fresh context where standards are the primary payload.

## When the split backfires

Generation-shaping rules deferred by mistake. Moving architectural rules to review time means the implementation agent makes structural decisions without knowing the constraints. The PR fails review and the agent must rework rather than revise — one iteration becomes two.

High-cost review cycles. If each PR review cycle is expensive (slow CI, large codebase, costly review agents), the rework cost from deferred discovery outweighs the savings on generation context — a pressure [tiered code review](tiered-code-review.md) exists to manage. The economics only favor deferral when review catches style violations, not when it triggers re-implementation.

No PR gate. The pattern needs a review step. In direct-commit workflows or single-agent loops that skip PRs, there is no enforcement point — deferred standards simply go unenforced.

## Key Takeaways

- CLAUDE.md is always-on context: every line costs tokens on every task, not just the ones where it matters
- Standards split into two types: generation-shaping (stay in CLAUDE.md) and post-hoc-checkable (move to REVIEW.md or reviewer agent)
- Claude Code Review formalizes this split: `REVIEW.md` is read exclusively by the review agent at PR time ([docs](https://code.claude.com/docs/en/code-review))
- The mechanism is phase-specific context allocation: each phase receives only the context its task requires
- The split backfires when architectural rules are mistakenly deferred — rework costs exceed the token savings

## Related

- [Agent-Assisted Code Review](agent-assisted-code-review.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [Context Budget Allocation](../context-engineering/context-budget-allocation.md)
- [Standards as Agent Instructions](../instructions/standards-as-agent-instructions.md)
- [Rigor Relocation](../human/rigor-relocation.md)
- [Learned Review Rules](learned-review-rules.md)
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Tiered Code Review](tiered-code-review.md)
