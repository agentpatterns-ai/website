---
title: "Generating Tests From Agent-Written Code (Code-First Oracle Bias)"
term: "Code-First Oracle Bias"
description: "Generating a test suite from the code an agent just wrote makes the tests inherit the code's faults, so they pass the buggy implementation instead of catching it — generate tests from the specification independently."
tags:
  - testing-verification
  - workflows
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - code-first test generation bias
  - coding before testing error propagation
last_reviewed: 2026-07-07
maturity: emerging
---

# Generating Tests From Agent-Written Code (Code-First Oracle Bias)

> Tests generated from the code an agent just wrote inherit that code's faults, so they pass instead of catching them.

## The anti-pattern

You ask an agent to implement a function, then ask the same agent to write tests for that implementation. The suite runs green and you treat that as proof the code is correct. It is not. Once the model sees the implementation before writing the tests, the tests encode the same wrong assumptions the code does, so a faulty implementation and its tests agree and the bug stays hidden.

An empirical study across five models (GPT-5-mini, GPT-4.1-mini, DeepSeek-V4, Claude Haiku, Llama 3.3) and three benchmarks (HumanEval+, MBPP, BigCodeBench) measured the cost: tests generated from the task description alone detected 25% of injected faults, but tests generated after the model saw the faulty code detected only 14% — an ~11.7% absolute drop, significant at p < 0.05 ([Konstantinou, Tambon & Papadakis, 2026](https://arxiv.org/abs/2607.05139)). Chain-of-Thought and Chain-of-Verification prompting did not recover the loss.

## Symptoms

- Tests written immediately after the implementation that pass on the first run with no iteration.
- Assertions that restate what the code does rather than what the specification requires.
- A green suite alongside a bug the specification would have caught.

## Why it works

Language models generate autoregressively, so once faulty code exists it becomes part of the context that shapes every later token, including the tests. The model reuses the same assumptions and reasoning trajectory for both artifacts — the authors call this error propagation: faults in the code are systematically replicated in the tests rather than randomly distributed ([Konstantinou, Tambon & Papadakis, 2026](https://arxiv.org/abs/2607.05139)). A test written to match a buggy implementation asserts the buggy behavior, so it passes. This is the temporal-ordering sibling of the [Test Homogenization Trap](test-homogenization-trap.md): homogenization comes from a shared model's blind spots, this comes from the code entering the test-generation context.

## Mitigations

- Generate tests from the specification, not the implementation: give the model the task description and expected behavior and withhold the code the agent produced ([Konstantinou, Tambon & Papadakis, 2026](https://arxiv.org/abs/2607.05139)).
- Order tests first, as in [TDD for agent development](../../verification/tdd-agent-development.md), which keeps the code out of the oracle's context by construction.
- Break the shared context: use a different model, session, or an adversarial test generator, or add human-authored edge cases as the independent layer.

## When this backfires

Withholding the implementation is not always right. Feeding code as context is a legitimate, separate use in three cases:

- Regression or characterization testing, where the goal is to pin current behavior rather than verify it against a specification — the code is the intended oracle.
- Coverage and compilability goals, where exposing the source raises pass rates and cuts hallucinated symbols. Industry tools such as [Meta's TestGen-LLM](https://arxiv.org/abs/2402.09171) feed the implementation for this — a different axis from fault-detection independence.
- Trusted, human-reviewed code used as context, where a separate oracle still gates correctness and the derived tests are not the sole proof.

The anti-pattern is specifically the single-model case where the green suite is treated as proof the code is correct.

## Example

**Before — tests generated from the agent's own implementation:**

```text
Prompt 1: "Implement parse_duration(s) returning seconds."
  -> agent returns code with an off-by-one on the minutes branch

Prompt 2: "Now write pytest tests for the function above."
  -> tests assert parse_duration("2m") == 119   # matches the bug
  -> suite is 6/6 green; the off-by-one ships
```

**After — tests generated from the specification, code withheld:**

```text
Prompt: "Write pytest tests for parse_duration(s): '2m' is 120 seconds,
         '1h30m' is 5400 seconds, '0s' is 0."
  -> tests assert parse_duration("2m") == 120   # matches the spec
  -> the off-by-one implementation fails test_minutes
```

The only change is what the test-generation prompt is allowed to see. The spec-grounded oracle catches the fault the code-grounded one certified.

## Key Takeaways

- Generating tests from an agent's own code drops fault detection from 25% to 14% across five models and three benchmarks, because faults propagate from code into the tests that should catch them.
- The green suite is not independent evidence: a test derived from a buggy implementation asserts the buggy behavior and passes.
- Generate tests from the specification, order them first, or use a separate model — keep the implementation out of the oracle's context.
- Feeding code as context is fine for regression tests, coverage goals, or trusted code with a separate oracle; the trap is treating a single-model, code-first green suite as proof of correctness.

## Related

- [The Test Homogenization Trap](test-homogenization-trap.md) — LLM-generated tests share the generating model's blind spots; the shared-blind-spot sibling of this temporal-ordering trap
- [TDD for Agent Development](../../verification/tdd-agent-development.md) — write tests first so the agent implements against human-defined expectations
- [Re-Run the Original Test Suite After Every Refinement Turn](../../verification/test-suite-after-refinement-turn.md) — the pinned original suite is the invariant multi-turn refinement is not optimizing against
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — agent-written tests that run green while carrying no real oracle signal
- [Happy Path Bias](happy-path-bias.md) — agents skip error handling and edge cases systematically, in code and in tests
- [Specification-Grounded Test Writing](../../verification/specification-grounded-test-generation.md) — the complementary move: withhold the implementation, then supply the specification as enumerated rules so the tester knows the intended edge behavior
