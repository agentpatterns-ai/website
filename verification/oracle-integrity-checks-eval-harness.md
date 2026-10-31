---
title: "State-Integrity Checks for an Eval Oracle"
term: "Oracle-Integrity Checks"
description: "A grader that rebuilds its expectation inside the state it grades can return a correct verdict and leave that state holding the reference solution, and two assertions needing no model catch it."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - oracle integrity testing
  - grader state integrity checks
  - known-answer controls for graders
last_reviewed: 2026-10-25
maturity: emerging
---

# State-Integrity Checks for an Eval Oracle

> An eval oracle can return a correct verdict and leave the state it graded holding the reference solution.

Oracle-integrity checks are assertions about what your grading function does to the state it grades, run in continuous integration beside the tests on everything else. Chen's audit of one widely used agent benchmark reports a reward function that resets the environment database to build a ground-truth hash and never restores it. Over 4,320 archived episodes, "recorded labels report 4,194 database passes over 4,320 episodes, replay gives 2,883, and success falls from 94.3% to 65.5%" ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)). Chen found the defect during an earlier study and later tested eight checks against injected faults. Their detection claim is counterfactual: "The suite would therefore have caught the defect had it been pointed at the benchmark as it stood before the repair".

## When these checks apply

A second reader turns this state mutation into a wrong label; it is not a precondition for running the checks. The defective function returns a correct value, computed from a hash taken before the reset, and "the benchmark's own agent consumes that value without reading the environment again". What produces a wrong label is "a harness that scores the episode separately, after the session has ended: the second read finds the reference solution's state rather than the agent's" ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)). Chen assigns the result as an integration failure and makes no claim that the upstream runner inflates its own scores.

Chen recommends repeat scoring and terminal-state checks for any harness that grades an agent episode. A separate scoring process makes this particular defect consequential. The positive control additionally needs a reference terminal state that the harness can construct ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2), Discussion).

## The eight checks

Five invariants state properties that must hold whatever the task, and three known-answer controls check the direction of the verdict. The clauses are Chen's ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)).

| Check | Assertion |
|---|---|
| INV-1 | "a direct call must not change the graded state" |
| INV-2 | "two calls on the same environment must agree in verdict and leave the same state" |
| INV-3 | "the verdict must not depend on the order in which episodes are scored" |
| INV-4 | "if the oracle raises part-way through, the state must be restored and the exception must propagate" |
| INV-5 | "after a session-ending step the environment must still hold the state the agent left, and no actions beyond the terminating one may have been appended" |
| CTL-1 | "an episode that accomplishes nothing, and one that says the required outputs without performing the required writes, must not be graded as solved" |
| CTL-2 | "the reference solution must be graded as solved" |
| CTL-3 | "an accepted alternative spelling of a required output must be accepted" |

The families cannot stand in for each other: "an oracle that is state-clean but wrong is invisible to the invariants, and one that is state-dirty but accidentally right is invisible to the controls."

## Start with the two that cost nothing

"Two checks in our suite would have caught the benchmark's defect immediately and cost nothing to run" ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)). They are repeat scoring, which grades one finished episode twice and requires the same verdict, and terminal-state stability, which asserts after a session-ending step that the environment still holds what the agent left. "Neither requires a reference implementation, a model call, or a human." Chen puts both in the build: "We suggest that both belong in the continuous integration of any harness that grades an agent episode, next to the regression test that pins the fix."

A detection table would talk you out of both. Chen computes which checks are load-bearing against the fault battery: "Four of the eight checks are necessary for at least one class and four are not for any: INV-3 (9 unique detections across the battery), CTL-1 (15), INV-4 (6) and CTL-3 (5), against INV-1, INV-2, INV-5 and CTL-2 with zero." Repeat scoring is INV-2 and terminal-state stability is INV-5, so the two cheapest checks, and the two the paper says would have caught the defect that was really there, sit in the group an ablation by unique detections would delete. Use both cost and fault coverage when choosing checks; zero unique detections alone does not justify deleting a cheap check.

## Why it works

An untested oracle can hide faults: "an oracle is exercised by every test run and tested by none, so its own faults are silent" ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)). A grader that holds state adds a second way to fail. In this benchmark, it builds its expectation by executing the reference solution against the same store it is grading, so "the returned value can be correct" while the store holds something no other reader expects. Chen calls the underlying fault ordinary: "A function that mutates the state it is grading and returns without restoring it is the ordinary shape of a resource-handling bug". The contract that would have caught this is nowhere written down: "who reads the environment, and when, is not specified anywhere — so a second reader can be wrong through no fault of the oracle's own runner." A state signature taken before and after a call turns that implicit contract into an assertion.

The mechanism also predicts the direction of the error, which is what makes a correction credible. Of the 4,320 episodes, 1,244 pass only under the archived label, with "no episode moves in the other direction, which is what a defect that reads the reference solution's state should produce." The damage is no constant you could subtract afterwards: per-agent the correction removes "from 24.0 to 33.6 pp, and every one of those intervals excludes zero". It changes which systems form the leading group and resolves no single winner either way, since the archived top two were separated by 0.28 pp and the corrected top two by 1.20 pp, on intervals that both contain zero.

## When this backfires

- No reference terminal state your harness can build. The suite did not transfer to a second, independently implemented framework, because "the framework materialises a reference episode only inside its own run loop" ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)). "The reference terminal state that the positive control needs cannot be reconstructed by an external harness from that framework's recorded API-call log, so no sensitivity or specificity could be estimated on its held-out task set and we report none." The fixture the framework did expose could not stand in: three of its 21 held-out tasks looked usable and were false positives produced by the defect the control exists to detect.
- A grade-once runner can consume the correct return value and never observe the mutated state. The integrity checks still apply: terminal-state stability fails without downstream code, and repeat scoring supplies its own second call ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2), Discussion).
- A not-applicable result is a blind spot rather than a pass. An oracle swallowing its own exception made INV-4 record the probed path as not applicable on all three targets, and Chen names the mechanism as general: "a check whose precondition is destroyed by the defect it is meant to detect will record that defect as inapplicable."
- The detection figures do not forecast your defects. The full suite detects 54 of 57 separable variant-target combinations, and the paper says why that number travels badly: "Every variant is author-constructed, so these figures are a conditional property of this battery, not a detection rate for unknown defects."
- The defect may sit below the oracle, where a state-clean grader still returns a wrong verdict. Bellibatlu and colleagues audited 34 mutating tools across four benchmarks and found "a clinical benchmark whose tool tells the agent each write executed under a documented no-write design its interface does not disclose; its grader takes that message as evidence, so its action success rate records whether a request carried the expected payload, not whether any record changed" ([arXiv:2609.37315v1](https://arxiv.org/abs/2609.37315v1)). Catching that needs contract conformance checking on the tools.
- Cheaper instruments ask less of your framework. A design-time checklist found other grading defects: "SWE-bench-Verified uses insufficient test cases"; the same paper reports that a trivial agent returning empty responses passes some intentionally impossible τ-bench tasks ([arXiv:2507.02825v5](https://arxiv.org/abs/2507.02825v5)). Gao and Zhou add "an outcome-evidence reporting layer to existing benchmarks, without changing their tasks, agents, or evaluators", which runs off stored artifacts and needs no reference state ([arXiv:2605.10448v1](https://arxiv.org/abs/2605.10448v1)).

## Example

Chen's benchmark grader hashes the agent's state, resets the database, and replays the reference solution to build the expected hash. It returns the comparison without restoring the agent's state. The original runner consumes a correct return value, while a later scorer reads the reference solution's writes.

A terminal-state assertion catches the mutation immediately after the session-ending step. Calling the scorer again also exposes the changed environment. Neither check needs the later scoring process that produced the wrong archived labels ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2), Discussion).

The following Python sketch makes the two contracts explicit. Supply a fixture paused immediately before its terminal action; `snapshot` must copy all graded state, not return a mutable alias. `score` returns a stable verdict, excluding timing fields.

```python
from copy import deepcopy

before = deepcopy(snapshot(env))
env.step(terminal_action)
assert snapshot(env) == before  # terminal action is declared state-neutral

first = score(env, episode)
assert snapshot(env) == before
second = score(env, episode)
assert second == first
assert snapshot(env) == before
```

For a terminal action that legitimately changes state, compare against the independently specified expected terminal state instead. This is an illustrative adapter contract, not code copied from Chen's implementation.

## Key Takeaways

- Keep the fault-injection battery separate from estimates of real-world defect detection. Chen's 54-of-57 result measures author-constructed faults.
- Report a missing check precondition as an evidence gap. An exception-swallowing defect can destroy the precondition that would expose it.
- Replay needs recorded tool calls that an external harness can execute against a resettable store. Chen used replay because the provider exposed no deterministic seed ([arXiv:2610.16067v2](https://arxiv.org/abs/2610.16067v2)).

## Related

- [LLM-Driven Benchmark Auditing](llm-benchmark-auditing.md) — the artifact-level counterpart, which reads specs, fixtures, and grading scripts with a frontier model
- [Test Oracles That Read Their Expectation From the Code](../patterns/anti-patterns/state-anchored-test-oracles.md) — the neighboring defect class, where the expectation itself is contaminated rather than the state the grading leaves behind
- [Protecting the Test Oracle From the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) — the same artifact guarded against a different adversary, the agent that would rewrite it
- [Per-Attempt Sandboxes for Agents That Change the Filesystem](per-attempt-eval-sandboxes.md) — the environment-level control that isolates attempts; grader state-integrity checks still apply within each attempt
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — the model-graded half of the same question, where the instrument's noise floor rather than its state hygiene is what moves the verdict
