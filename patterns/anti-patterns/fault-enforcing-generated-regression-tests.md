---
title: "Accepting Generated Regression Tests That Pin Faulty Code"
term: "Fault-Enforcing Tests"
description: "A regression test generated from a new, unreviewed change can encode its bug as the expected value, pass today, and fail the developer who fixes the bug later."
tags:
  - testing-verification
  - workflows
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - fault-enforcing generated tests
  - bug-pinning regression tests
last_reviewed: 2026-10-09
maturity: emerging
---

# Accepting Generated Regression Tests That Pin Faulty Code

> An LLM-generated regression test for a new change takes its expected values from the code, so a bug becomes the expectation.

## The anti-pattern

This page applies to tests generated for new or changed code whose correctness nobody has established, such as an open pull request. It does not apply to deliberate characterization of long-stable behavior, covered under [When this backfires](#when-this-backfires).

A fault-enforcing test passes on the faulty code and fails on the corrected code. The paper that defines the term puts it this way: "When the code is defective, a generated test can thus encode the defect as expected behavior: the buggy implementation passes it, while a corrected version fails." ([Charoosaei, Richter & Papadakis, 2026](https://arxiv.org/abs/2610.11835v1))

A fault-revealing test does the opposite. It passes on the corrected code and fails on the faulty code. A team that accepts a generated regression suite because it is green collects the first kind far more often than the second.

## What the study measured

The study used 145 merged pull requests from SciPy (50), Qiskit (50), and pandas (45). It injected faults as mutants and generated tests with Claude Haiku 4.5, using a pull-request-aware, coverage-guided prompt. The shares below count mutant-test pairs for mutants that survived the developer suite and were killable ([paper](https://arxiv.org/abs/2610.11835v1)).

| Category | SciPy | Qiskit | pandas |
|----------|-------|--------|--------|
| Fault-revealing | 2.6% (90) | 2.4% (81) | 4.8% (455) |
| Fault-enforcing | 16.9% (587) | 8.4% (281) | 16.9% (1,614) |
| Weak (passes on both) | 64.6% | 69.5% | 41.4% |
| Invalid (fails on both) | 15.9% | 19.7% | 37.0% |

The per-project shares are imprecise. SciPy's 95% interval for the fault-enforcing share is 8.4 to 26.2%. The authors state that in every project the lower bound of the fault-enforcing interval lies above the upper bound of the fault-revealing one, with point ratios of 3.5 to 6.5 ([paper](https://arxiv.org/abs/2610.11835v1)).

Two further results matter to a reviewer:

- In 92 of the 145 pull requests (63%), at least one injected fault led to a fault-enforcing test. The authors call this a worst-case view and note that a subset of pull requests drives the aggregate rate ([paper](https://arxiv.org/abs/2610.11835v1)).
- Between 37% and 57% of fault-enforcing tests expect an exception (for example with `pytest.raises`), against 3% to 9% of fault-revealing tests. With all exception oracles filtered out, there are still 4.0, 4.3, and 2.6 times as many fault-enforcing tests as fault-revealing ones ([paper](https://arxiv.org/abs/2610.11835v1)).

## Why the wrong expectation stays

The test persists because nothing contradicts it. It fails only on the corrected code, so it stays green until someone fixes the bug. Across 2,480 propagated pairs, the generated test still accepted the fault at the end of history in 85.5% of SciPy pairs, 82.8% of Qiskit pairs, and 90.9% of pandas pairs. In SciPy and Qiskit, no fault-enforcing test ever started to detect its fault over up to 49 later pull requests ([paper](https://arxiv.org/abs/2610.11835v1)).

Developer tests rescued few of these faults. A developer test failed on the fault at some later pull request for 36.3% of SciPy pairs, 6.1% of Qiskit pairs, and 7.6% of pandas pairs. In the last two projects, over 90% of the faults that the generated tests accept are never caught by a developer test within the studied history ([paper](https://arxiv.org/abs/2610.11835v1)).

## Why it happens

The paper names two causes and does not separate them.

The first is the oracle problem. The model sees the implementation, so it writes assertions from what the code does. Earlier work found that LLM-based test generation approaches mainly capture the actual program behavior, which makes bug detection difficult ([Konstantinou, Degiovanni & Papadakis](https://arxiv.org/abs/2410.21136v2)). [Code-First Oracle Bias](code-first-test-oracle-bias.md) covers the single-shot version of this effect.

The second is the acceptance criterion. A generator keeps a test only if it passes on the code it sees. In the authors' words: "An accepted test needs to pass on C fault and hence can only be weak or fault-enforcing, while a test that would reveal the fault is discarded or revised." ([paper](https://arxiv.org/abs/2610.11835v1)) A "make the tests pass" loop therefore removes fault-revealing tests by construction. The authors call for evaluating generation approaches that do not require tests to pass, to separate this effect from the oracle problem ([paper](https://arxiv.org/abs/2610.11835v1)).

Neither cause is specific to LLMs. The authors write that any oracle derived from observed behavior, whether written by an LLM or produced by a search-based generator such as Pynguin or EvoSuite, tends to encode what it observes ([paper](https://arxiv.org/abs/2610.11835v1)).

## What to do in review

The authors give reviewers one instruction: "A passing generated test is not evidence of correctness. Its expected values come from the code, so reviewers should check them against the specification or the PR description and not against the output of the current code." ([paper](https://arxiv.org/abs/2610.11835v1))

Three review moves follow from that instruction and the data:

- Check each expected value against the specification or the pull request description, not against what the code returns.
- Read exception assertions on new code with extra care, since they make up 37% to 57% of fault-enforcing tests.
- When a generated test fails on its first run, consider that the code may be wrong before you let the agent edit the test.

The authors present deriving expectations from specifications and reporting a failing test as a possible code fault as suggestions. The paper's conclusion lists both as future work, and the study did not evaluate them ([paper](https://arxiv.org/abs/2610.11835v1)). To derive a specification when none is written, see [Deriving a Specification From Buggy Code Before Generating Tests](../../verification/derived-specification-test-generation.md).

## When this backfires

The finding has limits that decide whether the review cost is worth paying.

- The faults were mutants, not real defects. The authors write that "that the test would enforce a real defect is an interpretation, which holds to the extent that the mutant resembles one." ([paper](https://arxiv.org/abs/2610.11835v1))
- One small model generated the tests. The authors note that results might not generalize to stronger models, and they argue the effect is structural without testing that ([paper](https://arxiv.org/abs/2610.11835v1)).
- Characterization testing is deliberate. For legacy code with no specification, pinning observed behavior is the goal: the conservative path is to assume the old behavior is the required behavior, and such tests are change detectors ([Characterization test](https://en.wikipedia.org/wiki/Characterization_test)). Checking expected values against intent is not possible there.
- Most generated tests carry no fault signal either way. Between 41% and 70% of the generated tests were weak, meaning they cover the changed code but cannot tell the faulty version from the reference ([paper](https://arxiv.org/abs/2610.11835v1)). Reviewing the expected values of a weak test costs time for no gain.
- Developer tests rarely contradict the pinned fault, but the rate varies by project. A developer test failed on the fault at a later pull request for 36.3% of SciPy pairs, 6.1% of Qiskit pairs and 7.6% of pandas pairs ([paper](https://arxiv.org/abs/2610.11835v1)). The existing suites kill 58.6%, 54.0% and 16.0% of testable mutants, so suite strength alone does not predict the rate.
- Surfacing failing generated tests as bugs has a false-positive cost. Meta reported 41 candidate catches to engineers, and 8 were confirmed as true positives ([Just-in-Time Catching Test Generation at Meta](https://arxiv.org/abs/2601.22832v1)).

The accumulation experiment is also not a model of real fault accumulation. The authors call it a deliberately adverse stress test ([paper](https://arxiv.org/abs/2610.11835v1)).

## Example

**Before: green suite accepted as evidence:**

```text
Change: new helper clamp_index(i, n) in an open PR. Bug: it returns n for i >= n.
Agent:  "Generate regression tests for this PR. Keep only tests that pass."
Result: assert clamp_index(10, 5) == 5     # the bug, pinned as expected
        8/8 tests green; the PR merges
Later:  a developer fixes the bug to return n - 1; test_clamp_high fails
```

**After: expected values checked against the PR description:**

```text
PR description: "clamp_index returns the last valid index, n - 1, for i >= n."
Review step:    compare each expected value with that sentence.
Finding:        assert clamp_index(10, 5) == 5 contradicts it; treat the code as suspect.
```

The example is illustrative and does not come from the study.

## Key Takeaways

- In the study, generated tests pinned an injected fault 3.5 to 6.5 times as often as they revealed it, on mutants, one model, and three Python libraries.
- Persistence is the cost: 83% to 91% of pinned faults were still accepted at the end of the history, and no pinned fault was ever caught in SciPy or Qiskit.
- Keeping only tests that pass on the current code removes fault-revealing tests by construction, so the generator setting matters as much as the model.
- Checking expected values against the specification or pull request description is the authors' suggestion, and they have not measured it.
- The finding covers new, unreviewed changes. Long-stable legacy behavior is a case for characterization tests.

## Related

- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](code-first-test-oracle-bias.md) — the single-shot version of the same mechanism, measured as lost fault detection
- [Test Oracles That Read Their Expectation From the Code](state-anchored-test-oracles.md) — the run-time counterpart, where measurement and expectation move together
- [Specification-Grounded Test Writing](../../verification/specification-grounded-test-generation.md) — supply the specification so expected values do not come from the code
- [Deriving a Specification From Buggy Code Before Generating Tests](../../verification/derived-specification-test-generation.md) — what to do when no written specification exists
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — generated tests that run green with no oracle signal
