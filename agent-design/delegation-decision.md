---
title: "The Delegation Decision: When to Use an Agent vs Do It"
description: "Agent delegation has overhead; match task characteristics to agent strengths rather than delegating everything or nothing. Delegating to an agent costs time"
tags:
  - agent-design
---

# The Delegation Decision: When to Use an Agent vs Do It Yourself

> Agent delegation has overhead; match task characteristics to agent strengths rather than delegating everything or nothing.

## The Overhead Reality

Delegating to an agent costs time: writing the prompt, waiting for output, reviewing the result, fixing mistakes. For some tasks this overhead is negligible relative to the value delivered. For others, it exceeds the task itself.

The delegation decision is not "can an agent do this?" but "does using an agent improve the outcome, accounting for the full cycle time?"

## The Describe-It Test

If describing what you want takes longer than doing it, do it yourself. A one-line variable rename takes ten seconds to execute and thirty seconds to prompt and verify. A codebase-wide API migration takes hours manually and minutes with an agent.

## When to Delegate

Delegate tasks with these characteristics:

- **Repetitive** — same operation applied across many instances
- **Large scope** — requires reading or modifying many files
- **Broad knowledge required** — depends on understanding patterns across the codebase, not deep knowledge of one subsystem
- **Well-specified** — the desired outcome can be described precisely
- **Verifiable** — the result can be checked against a clear criterion (tests pass, lint clean, format matches)

## When to Do It Yourself

Keep tasks that have these characteristics:

- **Small and fast** — faster to execute than to describe
- **Novel architecture** — requires judgment calls an agent won't make correctly without extensive guidance
- **Ambiguous requirements** — you don't yet know what you want; you're figuring it out by doing
- **Taste-dependent** — the criterion for "good" is in your head, not in any specification
- **Deep domain nuance** — the correct answer depends on knowledge the agent doesn't have and can't be given efficiently

## The Review Tax

Every agent output requires review. This is not optional — it's the cost of delegation. Factor the review time into your decision: a task that takes five minutes manually may take two minutes with an agent but four minutes to review, for a net loss.

The review tax decreases as:

- Task specifications become more precise
- Agent outputs become more predictable
- Review becomes automated (tests, linting, CI)

## Progressive Delegation

If you're unsure where to draw the line, start conservatively. Use agents for review and research before using them for implementation. As trust builds with specific task types, expand delegation in those categories. This builds calibrated confidence rather than oscillating between over-delegation and under-delegation.

## Anti-Patterns

**Delegate everything because agents are available.** Some tasks genuinely don't benefit from delegation. Forcing them through an agent adds overhead without improving output quality.

**Never delegate because of one bad experience.** A failed delegation in one task category doesn't invalidate delegation in others. Diagnose the specific failure — poor specification, wrong tool, ambiguous criteria — rather than generalizing.

## Example

The following two tasks illustrate the delegation decision in practice using Claude Code.

**Delegate** — codebase-wide API migration (repetitive, large scope, verifiable):

```bash
# The task touches 40+ files; describing it takes 30 seconds, doing it manually takes hours.
claude "Migrate all fetch() calls in src/ to use the internal apiClient.get/post wrappers.
The wrapper lives in src/lib/apiClient.ts. After migrating, run: npm test -- --testPathPattern=api"
```

The result is verifiable (tests pass or fail), the scope is too large for manual execution, and the operation is repetitive — all three delegation criteria are met.

**Do it yourself** — a one-line rename (faster to execute than to describe):

```bash
# Renaming a single local variable takes 5 seconds in the editor.
# Writing a prompt, waiting, and reviewing the diff takes ~60 seconds.
# Do it yourself.
```

Applying the describe-it test: the rename prompt would require explaining which file, which function, which variable, what to rename it to, and why — easily 40+ words. The edit itself is two keystrokes in an IDE. The test says: do it yourself.

## Key Takeaways

- Delegation has overhead; the break-even point depends on task size, repeatability, and review cost.
- The describe-it test: if describing the task takes longer than executing it, do it yourself.
- Agent strengths are breadth, volume, and consistency — not novelty, ambiguity, or taste.
- The review tax is fixed per delegation; automation (tests, CI) reduces it over time.

## Related

- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Execution-First Delegation](execution-first-delegation.md)
- [The Yes-Man Agent](../anti-patterns/yes-man-agent.md)
- [Agent Backpressure](agent-backpressure.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Agents vs Commands](agents-vs-commands.md)
