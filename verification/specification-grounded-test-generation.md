---
title: "Specification-Grounded Test Writing"
term: "Specification-Grounded Testing"
description: "Give an agent's test writer the specification as an explicit list of rules, one test per rule, so it catches the missing-validation and boundary bugs its own tests otherwise pass."
tags:
  - testing-verification
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - spec-grounded testing
  - specification grounding for tests
last_reviewed: 2026-07-10
maturity: emerging
---

# Specification-Grounded Test Writing

> Give a test writer the specification as explicit rules, not just a prose ticket, and it catches missing-validation bugs plain tests miss.

When an agent writes its own tests, a test only catches a bug if the writer knows what the code should do at each edge. Handing the writer the specification as a list of rules — one test per rule — supplies that intent directly. In a controlled study this lifted final correct-code rate from 62% to 100% across three Claude tiers, a +38 percentage-point gain over a strong baseline that was already told to probe invalid inputs and edge cases ([Haeri & Ghelichi, 2026](https://arxiv.org/abs/2607.06636)).

## When to use it

The gain is real but bounded. Reach for it when all three conditions hold:

- The bugs you worry about are specification-completeness defects: missing input validation, unhandled boundaries, unstated error conditions. On well-specified algorithmic problems the study found no natural bugs to catch, so grounding buys nothing there.
- You can state the correct edge behavior up front. The lever is supplying intent, so the rule list has to encode the right answer, not just restate the happy path.
- The test writer is capable enough to turn a rule into an input that triggers the bug and to predict the expected value. The study used a strong medium-tier model at near-perfect tester accuracy.

## How to apply it

Enumerate the specification into discrete rules and have the tester write one test per rule. For a `paginate` function the rules might be: pages are 1-indexed, `page` below 1 raises, `page_size` below 1 raises. Run the tests, then feed any failures back to the code model for a repair round.

The lever is grounding in intent, not the checklist format or the number of tests. The same specification given as a single prose paragraph caught 27 of 30 planted bugs; given as an enumerated checklist it caught 30 of 30, so the content does most of the work and enumeration adds a small margin ([Haeri & Ghelichi, 2026](https://arxiv.org/abs/2607.06636)). Adding tests without the spec does not substitute: a run of twice as many ungrounded tests reached 42% final correctness against 100% for the spec arm. The result replicated across vendors, with GPT-5.3-codex at +28 points and Gemini 3.5 Flash at +19 points (task-level sign test p = 0.002).

## Why it works

To write a test, the author has to know what the code should do at each edge, and when the ticket leaves an edge unstated an ungrounded tester has to guess. That guess fails in one of two ways: it never probes the edge, so the bug is missed, or it probes the edge but invents the wrong expected value, so correct code is rejected. The enumerated spec is an outside signal that states intended behavior one rule at a time, so the author stops guessing ([Haeri & Ghelichi, 2026](https://arxiv.org/abs/2607.06636)). Both failures share one root cause — missing access to intent — which is why the same signal raised bug detection from 18 of 30 to 30 of 30 and cut the false-alarm rate on correct code from 33% to 0% at once. More ungrounded tests cannot supply that missing intent, so a larger budget does not close the gap. This is the mirror image of the [code-first oracle bias](../anti-patterns/code-first-test-oracle-bias.md): withhold the implementation from the tester, but do supply the specification.

## When this backfires

- Algorithmic logic bugs. Where the defect is a wrong algorithm rather than a missing validation rule, grounding does not help — the study found zero natural bugs among 45 valid submissions on its logic tasks.
- Incomplete specification. Dropping validation rules degrades detection in proportion, falling from 30 of 30 to 6 of 30 when rules were omitted.
- Noisy specification. A rule that endorses the bug keeps detection high but drops tester precision to about 83%, so a wrong spec can certify a wrong implementation.
- Automatically derived specs. Models asked to write the spec restate the happy path and miss the unstated edge semantics, recovering only part of the benefit — the hard part is knowing the correct edge behavior, not formatting it.
- No agreed specification, or low-stakes code where false alarms are cheap. The study covers small single-function tasks only, not repository-level, stateful, or multi-step systems.

## Example

The only change is what the test-writing prompt is allowed to see.

**Before** — prose ticket, edge behavior left to the tester to guess:

```text
Ticket: "Implement paginate(items, page, page_size). Test invalid
         inputs and edge cases."
  -> tester probes page=0 but guesses it should return []
  -> code that silently returns [] on page=0 passes; the missing
     "raise on page < 1" rule is never enforced
```

**After** — specification supplied as enumerated rules, one test per rule:

```text
Rules: pages are 1-indexed; page < 1 raises ValueError;
       page_size < 1 raises ValueError.
  -> tester writes assert-raises tests for page=0 and page_size=0
  -> code that returns [] on page=0 fails test_page_below_one
```

The spec-grounded oracle enforces the rule the prose-grounded one guessed wrong.

## Key Takeaways

- Grounding an agent's test writer in the specification as enumerated rules lifted final correct-code rate from 62% to 100% across three Claude tiers, a +38-point gain over a baseline already told to probe edge cases.
- The lever is grounding in intent, not test count or checklist format: a prose spec caught 27 of 30 bugs and a checklist 30 of 30, while doubling ungrounded tests reached only 42% correctness.
- The same signal cuts both error types — it raised detection to 30 of 30 and dropped the false-alarm rate from 33% to 0% — because both come from the tester lacking access to intended behavior.
- The effect is bounded to specification-completeness defects with a correct, complete spec and a capable tester; it vanishes on algorithmic logic bugs and degrades with incomplete or noisy specs.

## Related

- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](../anti-patterns/code-first-test-oracle-bias.md) — the complementary rule: withhold the implementation from the tester, while this page supplies the specification to it
- [The Specification as Prompt](../instructions/specification-as-prompt.md) — using specs as instructions to the code writer; here the same spec grounds the test writer's oracle instead
- [Test-Driven Intent Clarification](test-driven-intent-clarification.md) — validating agent-written tests to surface specification ambiguity before writing code
- [Spec-Derived Execution as a Correctness Oracle](spec-derived-execution-correctness-judging.md) — grounding an LLM judge in a natural-language spec by executing spec-derived inputs
- [Per-Line Requirement Citations for Hallucination Detection](per-line-requirement-citations.md) — tying generated code back to specific requirement IDs so a mechanical check flags anything unsupported
