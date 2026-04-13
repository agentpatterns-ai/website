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

LLMs show significantly degraded performance when irrelevant but contextually plausible content is present alongside applicable instructions — [Shi et al. (2023)](https://arxiv.org/abs/2302.00093) demonstrate that model reasoning accuracy drops dramatically when irrelevant but domain-coherent context is added to the prompt. The same principle applies to instruction sets: instructions *related to* the applicable instruction compete for the model's attention, drawing it *away* from the one that matters.

An instruction that is accurate in general and related to the current task domain, but not applicable to this specific task, is not a neutral presence in the context. It is a distractor that reduces compliance with the instruction that does apply.

## An Example

A prompt for a task that writes integration tests might include instructions about unit testing conventions, component testing patterns, and end-to-end test structure — all accurate, all related to the same domain, but only one of which applies.

The model attends to all three. The applicable instruction competes for the model's focus with two related-but-wrong instructions. Compliance on the applicable instruction is lower than if the other two were absent.

This effect scales. A comprehensive instruction file is not a safety net — every inapplicable instruction dilutes the signal from the applicable one, with performance degrading as irrelevant context grows ([Ponnusamy et al., 2025](https://arxiv.org/abs/2601.11564)).

## Remediation

**Load task-scoped context** — Load only instructions applicable to the current task. Skill-based architectures support this: skill content loads on invocation, so the agent receives only what it is using.

**Prune before loading** — Remove instructions accurate-but-inapplicable to this task. The test is not "is this correct?" but "does including this improve output on this specific task?"

**Modular instruction files** — Organise by task type, not domain. A file for "integration test writing" loads separately from "unit test writing".

**Test by removal** — If compliance seems low, remove unrelated instructions and observe whether it improves. Improvement indicates distractor interference.

## When This Backfires

Over-pruning creates its own failure mode. Narrowing context too aggressively risks:

- **Under-informing the model** — edge cases that live in adjacent instructions get stripped, producing technically-compliant-but-wrong output on the margins.
- **Brittle task detection** — if task classification is wrong, the model loads the wrong instruction set entirely; a broad fallback provides a partial safety net.
- **Cross-domain tasks** — a task spanning two instruction domains genuinely needs both files; pruning one causes real compliance failures, not interference.
- **Maintenance overhead** — each task type needs its own instruction file; the pattern works best for well-defined, bounded tasks and offers less benefit for open-ended work where the applicable instruction set is uncertain at load time.

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
