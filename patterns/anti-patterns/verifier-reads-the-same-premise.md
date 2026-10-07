---
title: "When Your Agent's Verifier Reads the Same False Premise"
term: "Verification Trap"
description: "A verifier prompted from the same task description inherits its false premise, so 64-sample selection returns a wrong program over a correct one in the pool."
tags:
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - verification trap
  - premise-coupled verification
  - generator-verifier coupling
last_reviewed: 2026-10-06
maturity: emerging
status: current
---

# When Your Agent's Verifier Reads the Same False Premise

> A verifier prompted from the same task description inherits its false premise, so selection returns a wrong program over a correct one in the pool.

Two conditions have to hold. The task description asserts something untrue, and that same description reaches both the candidate generator and whatever writes the tests used to pick the winner. The pass rate then stops being an independent check, because the tests that would expose the shortcut are the ones the verifier no longer writes. The authors name this Verification Trap. A task counts as trapped when the "candidate pool contains at least one hidden-test-correct program, but the selector returns a hidden-test-wrong candidate" ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)).

## The anti-pattern

Sample many candidates, run generated tests over them, keep the best pass rate, and treat that rate as evidence the code is right. Sampling candidates and letting a verifier or selector pick the final output is standard practice. What couples the two halves is the prompt: "verifier inputs are constructed from the same prompt condition as the generator" ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)).

One misleading sentence in the description cost 13.81 points of selector-chosen correctness on HumanEval+ with Qwen2.5-Coder-32B (85.81 to 72.00 Selected@64). The objective, signature, and hidden tests were unchanged. Recoverable mis-selection on that cell more than doubled (4.73 to 12.00 Trap@64). Selection got worse in all eleven dataset-model cells, spanning HumanEval+, MBPP, LiveCodeBench, and five models including GPT-4o-mini ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)).

## Why it works

Premise-violating inputs are precisely the tests that catch a premise-consistent shortcut, and under a false premise the verifier writes fewer of them: "the counterexample rate decreases by 9.6 pp, 12.9 pp, and 18.9 pp for Qwen-7B, Qwen-14B, and Qwen-32B, respectively." A control inserting a true but irrelevant sentence stayed near baseline, so generic prompt noise is not the cause. The surviving tests leave wrong candidates in the same high-scoring region as right ones, and the selector follows that structure ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)).

One control isolates the channel. With the false-premise candidate pool held fixed, stripping the premise from the verifier prompt alone lowered Trap@64 across all three verifiers tested ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)). The defect sits in the evidence the selector reads.

## More tests do not fix it

Interventions that kept the original verifier as final judge moved selected correctness by under one point on the Qwen-7B and HumanEval+ cell. Extra verifier tests gained 0.97, width scaling lost 0.36, and regenerating candidates gained 0.67. Replacing what decides recovered 4.05 with a source-aware prior and 4.73 with a premise-agnostic robustness auditor ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)). Regeneration shows why quantity failed. It created correct programs that the original verifier then declined to select.

## When this backfires

A second evidence channel costs extra model calls and another scorer to calibrate. Three conditions limit what it buys.

1. The premise is true. The paper measured its mitigations only on false-premise tasks, so their benefit on true-premise tasks is unmeasured.
2. The pool holds no correct candidate. A trap needs a recoverable task by definition, and changing what selects cannot select a program that was never generated.
3. You expect the win to come from withholding the premise. An auditor handed the false-premise prompt still reached 80.41 against the clean auditor's 81.08. The authors conclude that "the mitigation gain is not explained solely by hiding the false premise from the auditor input" ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)). What pays is scoring candidate robustness instead of verifier-test agreement. Removing the premise adds a smaller amount on top.

The mitigation figures come from one dataset-model cell with an auditor the authors call simple. They also scope their claims to "the controlled false-premise settings evaluated in this work" rather than to any measured rate of false premises in the wild ([He et al., 2026](https://arxiv.org/abs/2610.05170v1)).

## Example

A schematic of the selection loop, with the premise sentence as the only difference between the two forms.

**Before — the verifier inherits the premise:**

```python
task = spec + "\nNote: the input list is always sorted ascending."
candidates = generate(task, n=64)
tests = write_tests(task)            # same text, same blind spot
best = max(candidates, key=lambda c: pass_rate(c, tests))
```

**After — a scorer that does not come from the verifier's tests:**

```python
candidates = generate(task, n=64)
tests = write_tests(spec)            # premise sentence withheld
audit = robustness_score(candidates) # candidate robustness, not test agreement
best = max(candidates, key=lambda c: (audit[c], pass_rate(c, tests)))
```

The Before form writes tests from the text under suspicion. The After form withholds the premise from test writing, scores candidates with an auditor, and uses the verifier only as a tiebreak.

## Key Takeaways

- The failure sits in selection: a correct program can sit in the pool while the selector returns a wrong one that the tests happen to agree with.
- Watch for the shared prompt. Stripping the premise from the verifier prompt alone lowered the trap rate with the candidate pool held fixed.
- Buying more of the same evidence moved correctness under one point; replacing what decides, with candidate-level robustness scores, moved it 4.73.
- Spend the extra channel only where premises are untrusted. The irrelevant-control condition left the verifier's counterexample rate near baseline, so generic prompt noise does not explain the drop.

## Related

- [The Test Homogenization Trap](test-homogenization-trap.md) — the same green-suite illusion attributed to shared model weights; that page treats a different test-writing model as a fix, which a shared prompt premise survives
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](code-first-test-oracle-bias.md) — the coupling that runs through the code rather than through the description
- [Independent Test Generation in Multi-Agent Code Systems](../multi-agent/independent-test-generation-multi-agent.md) — hiding the implementation from the test writer, and the independence it does not buy on its own
- [Test Oracles That Read Their Expectation From the Code](state-anchored-test-oracles.md) — oracle independence lost through state rather than through prompt text
- [Assumption Propagation](assumption-propagation.md) — the single-agent version, where one faulty premise compounds across turns
