---
title: "Distractor Interference: Why Relevance Is Not Enough"
description: "Semantically related but inapplicable instructions reduce compliance with applicable ones — proximity creates interference, not safety."
tags:
  - context-engineering
---

# Distractor Interference: Relevance Is Not Enough

> Semantically related but inapplicable instructions actively reduce compliance with the instructions that are applicable — proximity in meaning creates interference, not safety.

## The Pattern

Include every instruction that might be relevant. Cover all cases. Make the instruction file comprehensive so nothing is missed.

## Why It Fails

Softmax attention is zero-sum: every token competes for the model's attention budget. Semantically similar tokens pull attention toward each other, so instructions *related to* the applicable instruction draw attention *away* from it [unverified — the mechanism as described involves well-established softmax attention properties, but the specific degradation of compliance from semantically similar distractors in instruction following has not been independently sourced here].

An instruction that is accurate in general and related to the current task domain, but not applicable to this specific task, is not a neutral presence in the context. It is a distractor that reduces compliance with the instruction that does apply.

## An Example

A prompt for a task that writes integration tests might include instructions about unit testing conventions, component testing patterns, and end-to-end test structure — all accurate, all related to the same domain, but only one of which applies.

The model attends to all three. The applicable instruction competes for the model's focus with two related-but-wrong instructions. Compliance on the applicable instruction is lower than if the other two were absent.

This effect scales. A comprehensive instruction file covering every testing pattern is not a safety net — it is an attention distribution problem where every inapplicable instruction dilutes the signal from the applicable one.

## Remediation

**Load task-scoped context** — Rather than loading all instructions for a domain, load only the instructions applicable to the current task. Skill-based architectures support this: skill content loads on invocation, so the agent receives only the instructions for the skills it is using.

**Prune before loading** — Remove instructions that are accurate but not applicable to the current task. The test is not "is this instruction correct?" but "does including this instruction improve the agent's output on this specific task?"

**Modular instruction files** — Organise instructions by task type rather than by domain. A file for "integration test writing" loads separately from "unit test writing". The agent loads the file for the task it is performing, not the comprehensive domain file.

**Test by removal** — If compliance seems lower than expected, remove instructions unrelated to the current task and observe whether compliance improves. Improvement indicates distractor interference.

## Key Takeaways

- Semantically related but inapplicable instructions reduce compliance with the instruction that applies.
- "Comprehensive" instruction files create attention competition, not safety.
- Load task-scoped instructions on demand; prune anything that does not apply to the current task.

## Related

- [The Infinite Context](infinite-context.md)
- [Context Poisoning](context-poisoning.md)
- [Token Preservation Backfire](token-preservation-backfire.md)
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md)
- [Objective Drift: When Agents Lose the Thread](objective-drift.md)
- [Cargo Cult Agent Setup](cargo-cult-agent-setup.md)
- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Treat Task Scope as a Security Boundary](../security/task-scope-security-boundary.md) — task-scoped instructions also reduce prompt injection attack surface
