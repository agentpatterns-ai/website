---
title: "Probing Unstated Constraints in Generated Code (Intent Violation Rate)"
term: "Intent Violation Rate"
description: "A stated test suite can only check the constraints your prompt named, so measure how often passing code breaks the ones it did not and probe those directly."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - intent violation rate
  - IVR
  - unstated constraint testing
last_reviewed: 2026-08-11
maturity: emerging
---

# Probing Unstated Constraints in Generated Code (Intent Violation Rate)

> Code that passes every stated test still breaks unstated constraints in over half of problems, so probe the constraints you never wrote down.

A green test run tells you the code satisfies the specification you wrote, and nothing about the one you did not, because the suite came from the same prompt that omitted it. The DevIntent pilot benchmark puts a number on that residual: Claude Sonnet 4.6 passed 94.3% of stated tests while violating a hidden constraint in 54.5% of qualifying problems, and GPT-4.1 passed 92.7% with a 63.5% violation rate ([arXiv:2608.07614v1](https://arxiv.org/abs/2608.07614v1)).

## Conditions this holds under

- The evidence covers 49 single-function Python problems derived from HumanEval+, five samples each, one annotator writing every specification. The authors flag possible training contamination from the public dataset, name other languages and data-transformation tasks as untested, and call the metric a relative diagnostic rather than an absolute measure ([arXiv:2608.07614v1](https://arxiv.org/abs/2608.07614v1)). Nothing has been measured on multi-file, stateful, or repository-scale work, so read the rates as evidence the gap exists rather than as a rate for your codebase.
- The gap is specific to an omitted refinement. Where a requirement is instead vague or grammatically ambiguous, the ordinary suite already reacts: Orchid measures an average 7.22-point Pass@1 drop under ambiguity across 1,304 tasks, reaching 31.10 points for GPT-4 on syntactic ambiguity ([arXiv:2604.21505v1](https://arxiv.org/abs/2604.21505v1)). Those cases need no extra probe.
- You have to know the right answer. A probe encodes a constraint you are asserting, so an unfamiliar subsystem turns the exercise into guesswork.

## Running the probe

DevIntent builds each hidden test by taking a constraint the clarified prompt stated and deleting it from the prompt. In its HumanEval/34 example the gold prompt says "return only the unique values, sorted in ascending order" and the ambiguous version says only "return the unique elements in a list", so the stripped ordering requirement becomes the hidden test ([arXiv:2608.07614v1](https://arxiv.org/abs/2608.07614v1)). Run that construction backwards on your own task.

1. Write down the constraints you believe hold but did not put in the prompt. Ordering, mutation of inputs, error behavior on empty input, idempotency.
2. Keep the ones you would feel silly stating. Failure rates fall from 42.9% on the first stripped constraint to 15.4% on the third, which the authors read as the first being most central to the task ([arXiv:2608.07614v1](https://arxiv.org/abs/2608.07614v1)). Centrality is what makes a constraint feel too obvious to write.
3. Turn each into one assertion and run it against the code that already passed.
4. Feed the survivors back into the prompt rather than patching the output.

Do not reach for a second sample instead. Per-problem violation rates cluster at 0 or 1 for 95.7% of Claude's problems and 91.3% of GPT-4.1's, which the authors read as systematic rather than sampling noise ([arXiv:2608.07614v1](https://arxiv.org/abs/2608.07614v1)). Every draw misses the same constraint the same way, so best-of-N buys nothing.

## Why it works

Two artifacts derived from one source cannot cross-check each other. The stated suite was written from the stated prompt, so it exercises exactly the constraints that prompt named and is blind to the rest by construction. The model does not close the gap either, because it does not reliably notice the omission and so commits to one reading instead of asking. Orchid reports ambiguity localization "rarely exceed[s] 23%" with self-detection precision near 50% ([arXiv:2604.21505v1](https://arxiv.org/abs/2604.21505v1)), and QuestBench finds models "struggle to identify the right question even when they can solve the fully specified version" ([arXiv:2503.22674v2](https://arxiv.org/abs/2503.22674v2)). DevIntent offers no causal account of its own, so this mechanism is assembled from the independent ambiguity literature.

## When this backfires

- The constraint is not a requirement. On exploratory code, enumerating unstated constraints manufactures tests for behavior nothing depends on, and unlike every benchmark problem most real tasks have no gold prompt fixing a right answer.
- The gap is navigational rather than informational. When the missing constraint is discoverable by reading the codebase, an agent that explores first resolves it unaided and a probe duplicates that work ([arXiv:2502.13069](https://arxiv.org/abs/2502.13069)).
- Prompting is cheaper when you already know the constraint. Stating it up front beats catching it afterward, the case [test-driven intent clarification](test-driven-intent-clarification.md) and [specification-grounded test writing](specification-grounded-test-generation.md) already make. Probing is for the constraint you held without noticing.
- The construct is arguable. A model told "return the unique elements" that returns them unsorted satisfied the specification it was handed, so whether a hidden test measures a violation or a deleted requirement is a framing choice the numbers rest on.

## Example

A prompt asks for a function that merges two config dictionaries. The stated tests check that keys from both appear in the result, and the generated code passes all of them.

The probe list is three constraints nobody wrote down:

```python
def test_left_operand_not_mutated():
    a = {"x": 1}
    merge(a, {"y": 2})
    assert a == {"x": 1}           # fails: merge updated a in place

def test_right_wins_on_conflict():
    assert merge({"x": 1}, {"x": 2})["x"] == 2

def test_nested_dicts_merge_not_replace():
    assert merge({"db": {"host": "h"}}, {"db": {"port": 1}})["db"] == {
        "host": "h", "port": 1
    }                              # fails: the nested dict was replaced
```

Non-mutation and deep-merge are the two the stated suite cannot reach, because neither appeared in the prompt it was written from. When a probe like this fails, add the constraint to the prompt and regenerate rather than patching the output, since rerunning the same prompt produces the same in-place update every time.

## Key Takeaways

- Report intent violations separately from pass rate. One number describes the specification you wrote and the other describes the one you meant, and only the second predicts a production surprise.
- Rank your probe list by how obvious each constraint feels. Obviousness is why it went unwritten, and the earlier a constraint was dropped the more often it failed in the benchmark.
- Spend the probe budget on non-mutation, ordering, and empty-input behavior before happy-path coverage, since these are the classes a prompt-derived suite omits by construction.
- Treat a failed probe as a prompt defect, not a code defect. Patching the output leaves the omission in place for the next task that reuses the prompt.
- Stop sampling once a probe fails. Bimodal per-problem rates mean the second candidate carries the same misreading as the first.

## Related

- [Test-Driven Intent Clarification](test-driven-intent-clarification.md) — the prevention move: surface ambiguity through tests before code exists, where this page measures what survives it.
- [Specification-Grounded Test Writing](specification-grounded-test-generation.md) — supply the spec as enumerated rules to the test writer; probing is what to do about the rule you did not know you held.
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](../patterns/anti-patterns/code-first-test-oracle-bias.md) — a sibling shared-source failure, where the tests inherit the implementation rather than the prompt.
- [Assumption Propagation](../patterns/anti-patterns/assumption-propagation.md) — the behavior underneath the number: one committed reading that stays internally consistent until checked.
- [Verification Capacity as the Agent Quality Ceiling](verification-capacity-quality-ceiling.md) — budgets how much checking you can run; this page argues one specific check is worth the budget.
- [Unstated-Contract Bugs: Sort Tickets by Information Gap](unstated-contract-bug-triage.md) — the same blindness one step further out, where the constraint sits in user behavior rather than in a prompt you wrote.
