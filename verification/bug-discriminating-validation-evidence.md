---
title: "Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)"
term: "Bug-Discriminating Validation Evidence"
description: "Replay a repair agent's own passing test against the unfixed code. If it passes there too, the green run carried no information about the reported bug."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - buggy-state replay for agent tests
  - evidence-inadequate closure
  - bug-contrast feedback
last_reviewed: 2026-08-03
maturity: emerging
---

# Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)

> A passing test is evidence about a bug only if that same test also fails on the unfixed code.

When a repair agent runs a test and sees green, it treats the result as evidence that the reported defect is fixed. Replaying that same test against the original buggy code settles whether the treatment was warranted. Across 3,730 validation events in 643 rollouts over 110 tasks, 46.0% of positive comparable events were regression-only or misleading, carrying no information that discriminated the bug ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).

## When this applies

The measurement is cheap and general. The intervention built on top of it is narrower, so adopt the two separately.

- You can replay a validation command deterministically. The method applies post hoc to any repair trajectory that preserves the required code states and execution environment ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)), meaning pinned containers and a reproducible test invocation.
- Your agent runs an unconstrained tool-use loop. Under a plan-execute-verify scaffold the baseline rate of evidence-inadequate closure was already 8.3%, against 18.9% for the unconstrained loop, and no intervention component reached detectability (interaction estimate 5.00 points, p=0.52) ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).
- Your suite is stable enough to replay. A replay that disagrees with the captured outcome is classified as flaky and drops out of the comparable set ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).
- You are targeting evidence quality, not resolution rate. See [when this backfires](#when-this-backfires) before adopting on the strength of the headline number.

## What the replay measures

BSG-VA captures each validation command at the working-tree state that produced it, extracts a test-only patch holding just the test files, scripts, and fixtures the agent touched, then replays that patch on three states: the original buggy code (B), the captured candidate (S), and the developer gold fix (G) ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). The B and G outcomes assign each passing event a role:

| B replay | G replay | Role | What the pass proves |
|---|---|---|---|
| Fails | Passes | Gold-aligned bug-discriminating | The test targets the defect and generalizes past this candidate |
| Fails | Fails | Candidate-specific | The test separates bug from candidate, but not from the real fix |
| Passes | Passes | Regression-only | No new failures introduced, nothing about the bug |
| Passes | Fails | Misleading | The test contradicts the developer's fix |

Only 27.0% of positive comparable events were gold-aligned bug-discriminating; 30.6% were regression-only ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). At rollout level, 23.8% of baseline runs ended in evidence-inadequate closure, submitting a patch whose entire positive evidence base never discriminated the bug ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).

## Why it works

A test that passes on the unmodified buggy code was never sensitive to the defect, so its passing cannot raise your confidence that the defect is gone. That is a logical fact about the test, which is why replaying on state B is a decision procedure rather than a second opinion. The behavioral half is weaker. Feeding the B-replay outcome back to the agent cut evidence-inadequate closure by 7.8 points against an attention-matched reminder (p=0.0029) and raised bug-discriminating evidence by 7.4 points (p=0.011), but roughly one-third of that came from the reminder alone ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). The authors call this a mixed account and conclude that "the cheaper intervention has the broader reach" ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). The model can assess its own evidence; mostly it does not until something asks.

Independent work supports the prevalence half. SWT-Bench names "adding passing tests that do not reproduce the given issue" as a common error in even the best-performing method, with the top agent reaching a 19.2% fail-to-pass rate while producing 10.1% pass-to-pass tests ([Mündler et al., 2025](https://arxiv.org/abs/2406.12952v3)). This is the same discriminator [mutation testing applies to a synthetic fault](mutation-testing-quality-gate.md), aimed at the real one.

## When this backfires

- The intervention buys no extra repairs. Official resolution moved +0.5 points, and both primary estimates fell below the prespecified 10-point smallest effect size of interest, leaving practical magnitude uncertain ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).
- Test-writing behavior may not drive outcomes at all. Across six models on SWE-bench Verified, resolved and unresolved tasks showed similar test-writing frequencies, agent-written tests acted mainly as observational print channels rather than assertions, and prompt-induced changes in test volume did not significantly change final outcomes ([Chen et al., 2026](https://arxiv.org/abs/2602.07900v2)).
- The replay content generalizes poorly. On gpt-5.6-terra the generic reminder alone produced -7.5 points, while the B-replay content added +2.50 points with a 95% confidence interval of [-16.08, 21.08], reported as descriptive only ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)).
- Live repair has no gold fix. Roles are assigned against the developer gold fix as reference standard, which introduces noise where that fix is incomplete or several valid fixes exist ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). Outside a benchmark only the B half transfers.
- Evidence quality is not correctness. 29.6% of plausible SWE-bench patches induce different behavior than the ground-truth patch ([Aleithan et al., 2025](https://arxiv.org/abs/2503.15223v2)), a gap a bug-discriminating test does not close.

## Example

Bug-contrast feedback added a median of 11.0 seconds of B-replay per rollout, 3.3% of wall time, and the token difference against the reminder arm was not distinguishable from zero ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)). The shape in a CI or harness step:

```bash
# 1. Isolate the agent's test-only changes from its production edits.
git diff HEAD -- 'tests/**' 'conftest.py' > test-only.patch

# 2. Replay the agent's own validation command on the unfixed code.
git stash --include-untracked
git apply test-only.patch
pytest "$AGENT_TEST_TARGET" -q; B_STATUS=$?
git checkout -- . && git stash pop

# 3. A test that passed on B carries no bug-discriminating evidence.
[ "$B_STATUS" -eq 0 ] && echo "WARN: test passes on buggy code; not evidence of a fix"
```

Step 1 is the load-bearing part. Replaying the whole working tree would carry the production fix along with the test and always report a pass.

## Key Takeaways

- Put the buggy-state replay inside the agent's validation step rather than in review. The B outcome is only obtainable while the trajectory is still replayable, and it is what turns a green run into evidence.
- Measure evidence-inadequate closure as a rollout-level rate. A baseline of 23.8% ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)) tells you how much of your agent's confidence is unfounded.
- Adopt the measurement widely and the feedback loop narrowly. Its effect held only for one model under an unconstrained loop, and fell below the authors' own practical-significance bar.
- Try the generic reminder first. It reproduced across both models tested and delivered about a third of the benefit at no replay cost.
- Expect no change in repair success. This technique corrects what the agent believes it has proved, not how often it is right.

## Related

- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — replays the project suite to catch regressions; this page replays the agent's own new test to check it discriminates the bug.
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — asks whether a suite would catch a synthetic fault; the buggy-state replay asks about the real one.
- [State-Bound Evidence and Typed Revision Contracts for Repair Loops](state-bound-repair-evidence.md) — binds a test result to the code state that produced it, the freshness half of the same evidence discipline.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders cheap evidence ahead of expensive runs, which is where a B replay belongs.
- [Precise Debugging: Measure Edit Precision, Not Just Test Pass Rate](precise-debugging-benchmark.md) — the adjacent failure where tests pass because the agent regenerated unrelated code.
