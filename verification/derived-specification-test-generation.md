---
title: "Deriving a Specification From Buggy Code Before Generating Tests"
term: "Specification-Derived Test Generation"
description: "When no written specification exists and the code under test may be wrong, have the model write a behavioral docstring first and generate tests from that with the code removed."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - docstring-first test generation
  - specification derived from the code under test
last_reviewed: 2026-07-28
maturity: emerging
---

# Deriving a Specification From Buggy Code Before Generating Tests

> Buggy code steers a model into asserting the bug; replacing it with a model-written specification buys back part of the lost bug-detection power.

Show a model the implementation and ask for unit tests, and the tests encode whatever the implementation does — including its defects. Across 11 models on Defects4J 3.0 (318 focal methods, 233 defects, 17 Java projects), prompting with the buggy version instead of the fixed version raised misguided tests from 16.46 to 137.69 on average and cut effective bug-revealing tests from 304.08 to 104.15, close to a threefold loss ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)). A misguided test is one that passes on the buggy version and fails on the fixed one, so it is a false negative that certifies the defect.

## When to reach for it

This is a fallback with a measured ceiling, not a general upgrade to test generation. Three conditions have to hold:

- You have no trustworthy written specification. If you do, supply that instead — an enumerated human specification is the stronger lever, as [specification-grounded test writing](specification-grounded-test-generation.md) shows.
- The code under test may itself be wrong: a bug reproduction, an inherited module, a legacy method you are pinning down before changing.
- The unit is self-contained enough that a method-level description captures its behavior. The evidence base is method-level Java, not stateful or dependency-rich code.

Expect partial recovery. The base version of the technique moved misguided tests from 137.69 to 113.00 and effective tests from 104.15 to 186.77 — well short of the 16.46 and 304.08 the same models reached when given correct code ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)).

## How to apply it

Split generation into two prompts. First, ask the model to write a behavioral docstring for the method that states its functionality and intent without quoting the code. Second, generate tests from that docstring, with the implementation removed from the prompt. Removal is the load-bearing step: the authors report the code has to go entirely rather than be supplemented ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)).

An advanced docstring prompt asks the model to also flag logical mistakes that contradict the inferred intent and robustness omissions such as missing null checks or boundary handling. That variant added a further gain over the base prompt, larger on reasoning models (32.00 fewer misguided tests, 56.15 more effective ones) than on base models (18.17 fewer, 28.67 more) ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)).

Review the docstring before generating tests. It is the single point where the whole technique can fail silently.

## Why it works

Buggy code shifts the model's token-level preference toward tests that assert the buggy behavior, so the effect is internal to generation rather than downstream noise. The authors measured this with sequence scores, which reflect a model's probabilistic preference for a generated sequence: for DeepSeek-V3, misguided tests scored higher when conditioned on buggy code than on fixed code (−1.21 against −1.31), while effective tests scored higher when conditioned on fixed code (−1.23 against −1.30) ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)). Removing the implementation removes the conditioning signal that produces the skew, which is why supplementing the code with a specification does not work. The same study found the drop in misguided tests and the rise in effective tests correlate at r = 0.90 (p < 0.01), and that models with stronger code comprehension can be more susceptible to misguidance rather than less. This is the mitigation side of [code-first oracle bias](../patterns/anti-patterns/code-first-test-oracle-bias.md), applied to the case where the code was not the agent's own.

## When this backfires

- The derived specification inherits the bug. Manual inspection found 15% to 21% of generated docstrings preserved the original defect, and those runs produced significantly more misguided tests. The technique fails silently and its output is indistinguishable from a success ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)).
- Stateful or dependency-rich code. A method-level docstring omits class state and dependency information, which the authors name as a limit on their results. An industrial deployment report reaches the opposite conclusion for repository-scale Java, finding that compilation robustness depends on making project-level dependencies explicit rather than letting the model infer them ([Chen et al., 2026](https://arxiv.org/abs/2607.19682)).
- Regression and characterization testing. When the goal is pinning current behavior rather than checking it against intent, the implementation is the intended oracle and removing it defeats the exercise.
- Proprietary or domain-specific systems. Without domain knowledge the model can produce a hallucinated false intent instead of a specification ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)).
- False-alarm-sensitive pipelines. The advanced prompt lifted the false-positive share from roughly 16% to 18%, and on bug-free code the false-alarm rate rose from 37.45% to 39.04% ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883)). Coverage did not suffer there, so the cost is false alarms rather than reach.

## Example

The two prompt shapes below show the only thing that changes: what the test-generation prompt is allowed to see. The method stands in for any unit whose empty-input branch violates its stated contract, the defect class the study's advanced prompt is built to catch.

Before — implementation in the prompt, tests assert the defect:

```text
Prompt: "Write JUnit tests for this method."
        <paste of the implementation, whose empty-input branch
         returns null instead of the documented empty result>

  -> assertNull(subject.summarize(empty))
  -> green on the buggy version, red on the fixed version:
     a misguided test that certifies the defect
```

After — docstring first, implementation withheld:

```text
Prompt 1: "Write a formal docstring for this method describing its
           functionality and intent. Do not quote the code. Flag any
           logic that contradicts the inferred intent and any missing
           null or boundary handling."

  -> "Summarizes the input collection. Returns an empty result for
      an empty collection. Note: the implementation returns null in
      that branch, which contradicts the stated contract."

Prompt 2: "Write JUnit tests for the method described by this
           docstring." <docstring only, no code>

  -> assertEquals(EMPTY_RESULT, subject.summarize(empty))
  -> fails on the buggy version: an effective test
```

The second prompt never sees the null return, so it has nothing to copy. When the first prompt misses the contradiction, the docstring carries the bug forward and the suite certifies it again — the 15% to 21% case above.

## Key Takeaways

- Prompting a model with buggy code raised misguided tests from 16.46 to 137.69 and cut effective bug-revealing tests from 304.08 to 104.15 across 11 models on Defects4J 3.0.
- Sequence-score analysis shows the cause is internal: buggy code raises the model's own preference for tests that assert the buggy behavior, and stronger code comprehension can increase susceptibility.
- Replacing the implementation with a model-written docstring recovers part of the gap — 113.00 misguided and 186.77 effective tests — not all of it. The code must be removed, not supplemented.
- The docstring is the failure point: 15% to 21% preserved the original bug, so review it before generating tests.
- Reach for this only when no written specification exists. When one does, supply it directly; when the goal is regression testing or the code is dependency-rich, keep the implementation in context.

## Related

- [Specification-Grounded Test Writing](specification-grounded-test-generation.md) — the stronger move when a human-authored specification exists: enumerate it as rules and write one test per rule
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](../patterns/anti-patterns/code-first-test-oracle-bias.md) — the anti-pattern this mitigates, measured on code the agent itself just wrote
- [Reverse-Engineered Executable Specifications for Agentic Program Repair](../patterns/multi-agent/reverse-engineered-executable-specifications.md) — the same specification-inference-first split applied to patch generation rather than test generation
- [Assertion-Free Test Theater in Agent-Authored Patches](../patterns/anti-patterns/assertion-free-test-theater.md) — the adjacent failure where generated tests carry no oracle signal at all
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — keeps a pinned invariant suite outside the loop that refinement can drift against
