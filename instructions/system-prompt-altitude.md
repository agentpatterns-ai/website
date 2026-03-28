---
title: "System Prompt Altitude: Specific Without Being Brittle"
description: "Effective system prompts describe how to reason, not what to decide — sitting at the altitude that produces consistent behaviour across variation."
aliases:
  - prompt altitude
  - instruction specificity level
tags:
  - context-engineering
  - instructions
---

# System Prompt Altitude: Specific Without Being Brittle

> System prompts fail in two directions — too brittle on edge cases or too vague to constrain behaviour. Effective prompts sit at the altitude that produces consistent behaviour across variation.

## The Two Failure Modes

**Too brittle**: The system prompt enumerates cases. "If the user asks about X, do Y. If they ask about Z, do W." This works for the anticipated cases and fails on everything else. Each edge case requires a prompt update. The agent has no principle to reason from — only a lookup table.

**Too vague**: "Be helpful, accurate, and concise." This gives the agent no real constraint. Any output can satisfy it. The agent defaults to its pre-training distribution rather than task-specific behaviour.

[Anthropic's context engineering guide](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) identifies prompt altitude as a core design decision: effective system prompts function as strong heuristics that generalize, not lookup tables that enumerate cases [unverified — paraphrased concept; exact wording not found in cited source].

## The Right Altitude

A well-calibrated system prompt tells the agent *how to reason*, not *what to decide* for each case. This produces behaviour that generalises to unanticipated inputs.

Compare:

| Too brittle | Right altitude |
|-------------|---------------|
| "If the file is over 500 lines, read the first 100 and last 100 lines" | "For large files, identify structural landmarks before reading in full — start with what the file declares, not what it implements" |
| "Never edit files in /src/auth/" | "Treat authentication code as high-risk; any edit requires understanding the downstream session and token impact before proceeding" |
| "Always add a test for every function" | "Changes to business logic require test coverage; changes to types, formatting, or comments do not" |

The right-altitude versions generalise. The too-brittle versions break on edge cases the author didn't anticipate.

## Organising System Prompts

[Anthropic recommends](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) organising system prompts into distinct sections, each operating at an appropriate level of specificity:

| Section | Purpose | Altitude |
|---------|---------|---------|
| Background | Role, project context, agent's scope | High — principles and context |
| Instructions | How to behave and what to prioritise | Medium — heuristics |
| Tool guidance | When and how to use specific tools | Low — precise constraints |
| Output format | Structure, length, format of responses | Precise — exact requirements |

Background sections can be general. Tool guidance should be precise. Mixing altitudes within a section produces inconsistency.

## Testing Altitude

The practical test for altitude calibration: introduce an edge case the prompt didn't anticipate, then observe behaviour. A well-altitude prompt degrades gracefully — the agent applies the nearest applicable heuristic. A too-brittle prompt breaks or falls through to vague default behaviour. A too-vague prompt was never constrained to begin with.

If adding one new instruction requires adding three others to handle its edge cases, the original instruction was too brittle. Raise the altitude — describe the principle, not the case.

## Key Takeaways

- Brittle prompts enumerate cases; they break on inputs the author didn't anticipate.
- Vague prompts give no real constraint; the agent defaults to its pre-training distribution.
- The right altitude describes how to reason, not what to decide — strong heuristics that generalise.
- Organise system prompts by section; each section operates at an appropriate altitude (background high, tool guidance precise).

## Example

A code-review agent needs guidance on handling test files. Here is the same instruction at three altitudes:

**Too brittle** — enumerates cases:

```
If the file ends in _test.go, only check for assertion coverage.
If the file ends in .test.ts, only check for mock usage.
If the file ends in _spec.rb, only check for describe/context structure.
```

This breaks for any test framework the author did not anticipate (Pytest, Vitest, Playwright).

**Too vague** — no real constraint:

```
Review test files carefully.
```

The agent has no principle to apply. It defaults to reviewing test files the same way it reviews production code.

**Right altitude** — a heuristic that generalises:

```
Test files: focus on whether the test verifies observable behaviour rather than
implementation details. Flag tests that would break on a safe refactor (e.g.,
asserting on internal state, mocking every dependency, or testing private
methods). Do not flag stylistic choices that vary by framework.
```

This version works across Go, TypeScript, Ruby, Python, and any future test framework because it describes the reasoning principle, not the per-language checklist.

## Unverified Claims

- Anthropic's context engineering guide identifies prompt altitude as a core design decision: effective system prompts function as strong heuristics that generalize, not lookup tables [unverified — paraphrased concept; exact wording not found in cited source]

## Related

- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Seeding Agent Context: Breadcrumbs in Code](../context-engineering/seeding-agent-context.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [WRAP Framework for Agent Instructions](wrap-framework-agent-instructions.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Domain-Specific System Prompts with Concrete Examples](domain-specific-system-prompts.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Layer Agent Instructions by Specificity: Global, Project](layered-instruction-scopes.md)
- [The Instruction Compliance Ceiling: How Rule Count Limits AI](instruction-compliance-ceiling.md)
- [Production System Prompt Architecture](production-system-prompt-architecture.md)
- [System Prompt Replacement](system-prompt-replacement.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
