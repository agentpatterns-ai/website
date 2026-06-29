---
title: "The Delegation Decision: When to Use an Agent vs Do It Yourself"
term: "Delegation Decision"
description: "Agent delegation has overhead. Match task characteristics to agent strengths rather than delegating everything or nothing, and factor the review tax into every delegation decision."
tags:
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: emerging
---

# The Delegation Decision: When to Use an Agent vs Do It Yourself

> Agent delegation has overhead; match task characteristics to agent strengths rather than delegating everything or nothing.

## The overhead reality

Delegating to an agent costs time: writing the prompt, waiting for output, reviewing the result, fixing mistakes. For some tasks this overhead is small next to the value delivered. For others, it exceeds the task itself. To model that trade-off, see [cost-aware agent design](../token-engineering/cost-aware-agent-design.md).

The delegation decision is not "can an agent do this?" but "does using an agent improve the outcome, accounting for the full cycle time?"

## The describe-it test

If describing what you want takes longer than doing it, do it yourself. A one-line variable rename takes ten seconds to execute and thirty seconds to prompt and verify. A codebase-wide API migration takes hours manually and minutes with an agent.

Anthropic's [Claude Code best practices](https://code.claude.com/docs/en/best-practices) applies the same test for planning overhead: "If you could describe the diff in one sentence, skip the plan." The same threshold applies to delegation itself.

## When to delegate

Delegate tasks with these characteristics:

- Repetitive — the same operation applied across many instances
- Large scope — reading or changing many files
- Broad knowledge required — depends on patterns across the codebase, not deep knowledge of one subsystem
- Well-specified — you can describe the desired outcome precisely
- Verifiable — you can check the result against a clear criterion (tests pass, lint clean, format matches)

## When to do it yourself

Keep tasks that have these characteristics:

- Small and fast — quicker to execute than to describe
- Novel architecture — needs judgment calls an agent will not make correctly without heavy guidance
- Ambiguous requirements — you do not yet know what you want; you are working it out by doing
- Taste-dependent — the test for "good" is in your head, not in any specification
- Deep domain nuance — the correct answer depends on knowledge the agent does not have and cannot get efficiently

## The review tax

Every agent output needs review, whether by a human or an [agent self-review loop](../code-review/agent-self-review-loop.md). Review is not optional — it is the cost of delegation. Factor the review time into your decision: a task that takes five minutes by hand may take two minutes with an agent but four minutes to review, for a net loss.

The review tax falls as:

- Task specifications become more precise
- Agent outputs become more predictable
- Review becomes automated (tests, linting, CI)

## Progressive delegation

If you are unsure where to draw the line, start conservatively. Use agents for review and research before you use them for implementation. As trust builds with specific task types — informed by [task-feasibility awareness](task-feasibility-awareness.md) — expand delegation in those categories. This builds calibrated confidence rather than swinging between over-delegation and under-delegation.

## When this backfires

[Skill atrophy](../human/skill-atrophy.md). Developers who delegate codebase changes without reading the diffs lose familiarity with the code. The agent does the work; the developer loses the context, and accumulates [comprehension debt](../anti-patterns/comprehension-debt.md). Reserve enough hands-on work to keep your mental model current.

Specification overhead underestimated. The describe-it test assumes you can state the task. When requirements are only partly formed, specification costs more than the estimate. The agent then produces output that needs rework because the spec was wrong, not the execution. [Interactive clarification for underspecified tasks](interactive-clarification-underspecified-tasks.md) recovers some of that cost up front.

"Verifiable" in practice is harder than in theory. A task seems verifiable ("tests pass") but the test suite does not cover the relevant behavior. Agent output can satisfy the stated criterion while adding an unlisted failure mode that the [premature-completion](../anti-patterns/premature-completion.md) anti-pattern describes. The review tax is non-zero even for test-covered tasks.

Automation bias. The tendency to trust agent output without enough scrutiny grows after repeated successful delegations. This creates a trust gap: the agent's actual error rate does not change, but the review depth drops ([Cognitive Load Framework for Human–AI Symbiosis, Springer 2026](https://link.springer.com/article/10.1007/s10462-026-11510-z)).

## Anti-patterns

Delegate everything because agents are available. Some tasks genuinely do not benefit from delegation. Forcing them through an agent adds overhead without improving output quality — the [effortless-AI fallacy](../anti-patterns/effortless-ai-fallacy.md) in practice.

Never delegate because of one bad experience. A failed delegation in one task category does not invalidate delegation in others. Diagnose the specific failure — poor specification, wrong tool, ambiguous criteria — rather than generalizing.

## Example

The following two tasks illustrate the delegation decision in practice using Claude Code.

Delegate — codebase-wide API migration (repetitive, large scope, verifiable):

```bash
# The task touches 40+ files; describing it takes 30 seconds, doing it manually takes hours.
claude "Migrate all fetch() calls in src/ to use the internal apiClient.get/post wrappers.
The wrapper lives in src/lib/apiClient.ts. After migrating, run: npm test -- --testPathPattern=api"
```

The result is verifiable (tests pass or fail), the scope is too large for manual execution, and the operation is repetitive — all three delegation criteria are met.

Do it yourself — a one-line rename (quicker to execute than to describe):

```bash
# Renaming a single local variable takes 5 seconds in the editor.
# Writing a prompt, waiting, and reviewing the diff takes ~60 seconds.
# Do it yourself.
```

Applying the describe-it test: the rename prompt would require explaining which file, which function, which variable, what to rename it to, and why — easily 40+ words. The edit itself is two keystrokes in an IDE. The test says: do it yourself.

## Key Takeaways

- Delegation has overhead; the break-even point depends on task size, repeatability, and review cost.
- The describe-it test: if describing the task takes longer than executing it, do it yourself.
- Agent strengths are breadth, volume, and consistency — not novelty, ambiguity, or taste; lean on them via [execution-first delegation](execution-first-delegation.md).
- The review tax is fixed per delegation; automation (tests, CI) reduces it over time.

## Related

- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Execution-First Delegation](execution-first-delegation.md)
- [The Yes-Man Agent](../anti-patterns/yes-man-agent.md)
- [Agent Backpressure](agent-backpressure.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Agents vs Commands](agents-vs-commands.md)
