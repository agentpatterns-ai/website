---
title: "Building on Inherited Test Failures in Agent Task Chains"
term: "Building on Inherited Test Failures"
description: "An agent that starts a task from a repo whose earlier tests already fail reuses the defect instead of repairing it, and resolves 5.6 points fewer later tasks on average."
tags:
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - inherited failures
  - building on a red suite
  - agent-history penalty
last_reviewed: 2026-10-15
maturity: emerging
---

# Building on Inherited Test Failures in Agent Task Chains

> An agent that starts a task from code with failing earlier tests builds on the defect, and the new task fails on the same mismatch.

Building on inherited test failures is the practice of letting an agent start a new task while tests from its earlier tasks fail, then asking it to build on that code. Pan et al. measured the cost on 100 three-event episodes from 50 Python repos. Each later event ran twice with the same task, agent, and tests, once from the developers' preceding patches and once from the agent's own preceding changes ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)).

## Conditions that set the size of the effect

The numbers below come from a harness where the agent cannot see the earlier tests. The paper does not test a repo where the agent can run its suite, so the numbers may not carry over to one.

- Hidden earlier tests. The authors write that "in our harness these tests are hidden, so an agent cannot see that it broke earlier behavior, whereas an agent that runs them can repair a failure at the event that caused it, while the repair is still local."
- Three events, Python, one agent continuing its own work. The study excludes "agents that build on another agent's work or on mixed human–agent histories."
- Tested behavior only. The authors write that "inherited test failures and their absence refer only to tested behavior."

## What the study measured

Building on its own history lowered later-task resolution by 5.6 percentage points (95% CI −7.2 to −4.1) in all ten system–model combinations. At the first event, where both settings start from identical code, the two differed by only +1.8 points ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)).

When all earlier tests must also pass, the gap grows to 14.0 points. That figure is an upper bound, because the agent could not run those tests. Two-thirds of Agent-History starting repos already fail earlier tests, and only 1.9% of events built on them end with all accumulated tests passing ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)).

The cost sits in the cohort that starts red. For the 1,349 events that start with failing earlier tests, the gap on resolving the event with all earlier tests passing is −21.9 points (95% CI −24.5 to −19.3). The gap on the new task is −7.6 points (95% CI −9.7 to −5.6).

Once inherited code passes all earlier tests, the agent does as well as from developer history. The paper reports +2.7 points on resolving the event with all earlier tests passing (95% CI −0.5 to +6.1). On task resolution in the same cohort, the gap is −1.1 points (95% CI −3.8 to +1.6) ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)). Both intervals include zero.

## Why it works

The cost follows failing behavior that nobody repairs. The paper finds that structural properties of the earlier change do not predict it. With the earlier tests hidden, the agent cannot see that a prior change broke something, so the next task starts from defective code. In the paper's unidiff case, the agent "reads the line-splitting logic it wrote and reuses it in the constructor, so the inherited failure stays unrepaired and the new task fails on the same mismatch." The authors add that "Inherited failures are almost never repaired, and they also hinder the new task" ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)).

Static properties of the agent's code did not explain which changes hurt. In the exploratory analysis of 53 facilitation and 36 hindrance events, "none of the structural properties in RQ3 predicts when an earlier change hinders the next task, whereas whether earlier tests still pass does."

## Not all inherited failures are broken code

Part of the cost is unfinished work. In 28% of inherited failures, "the agent produced no valid change for that event." In 38%, earlier tests fail only on assertions, so the code runs but behaves incorrectly. In 26%, the failures involve missing names, missing attributes, or mismatched signatures, and 9% cannot be classified ([Pan et al., 2026](https://arxiv.org/abs/2610.14768v1)).

Setting the 28% aside does not remove the penalty. Among assertion-only failures, "The cost to the new task remains" (ΔTR −4.4, 95% CI −7.7 to −1.0).

## Safeguards the paper names

The paper's practical advice is about the test pipeline:

- Run the accumulated suite after every change. "The practical safeguard is to keep the tests of earlier tasks in the pipeline and run them after every agent change, not only the tests the agent was asked to satisfy."
- Treat the current tests as necessary, not sufficient. In the crontab case, "a change that fixed only the tested call sites passed two consecutive events and still broke code added later."
- Repair before building. "an agent that inherits a failure should repair it rather than build on it"
- Test agents from their own history. "Benchmarks that start every task from developers' code overstate how well agents sustain maintenance, so evaluations should also run agents from their own history."

A completion gate that requires earlier tests to pass applies the fix from [Premature Completion](premature-completion.md) across tasks instead of inside one session.

## A conflicting result

[SlopCodeBench](https://arxiv.org/abs/2603.24755v2) points the other way on code quality over longer chains. It reports that "Quality degrades across checkpoints, with structural erosion rising in 77% of trajectories and verbosity in 75.5%," and that "agents pass checkpoints while producing code that erodes and bloats with each turn" ([Orlanski et al., 2026](https://arxiv.org/abs/2603.24755v2)).

The two papers differ in horizon and in what they measure. SWE-Maintain uses three events and paired task outcomes. Its authors say their conclusion on code debt "rests on paired maintenance outcomes, not on static maintainability metrics, whose validity as proxies is debated," and that "longer sequences may compound the cost further." SlopCodeBench measures static erosion over longer trajectories. This page does not decide between them. The SWE-Maintain result covers tested behavior over two follow-on tasks and does not show that code debt is absent.

## When this backfires

Running earlier tests after every change fails or costs more than it saves when:

- Coverage is thin. A green run covers only tested behavior, so untested inherited breakage passes unseen.
- The suite is already red. Without a baseline of accepted failures, "do not build on failing tests" cannot separate a new inherited failure from a known one.
- The suite is slow and changes are frequent. Teams that sample tests to save CI time reopen the gap.
- The history is mixed. The study does not cover an agent that inherits another agent's or a human's partial work.
- The chain is long. Dropping structural review on the strength of one three-event study ignores the SlopCodeBench result.

## Example

**Before — agent continues from a red suite:**

```text
task 1: agent patch applied, target tests pass, earlier suite not run
task 2: starts on task 1 code, 6 earlier tests fail (unseen)
        agent reuses the task 1 helper, new task fails the same assertion
```

**After — earlier tests gate each step:**

```text
task 1: agent patch applied, full accumulated suite run, 6 failures reported
        agent repairs the failures before the task counts as done
task 2: starts from a green suite
```

The example is illustrative and not drawn from the paper. It shows where the gate sits.

## Key Takeaways

- In a harness that hides earlier tests, building on the agent's own history cut later-task resolution by 5.6 points, and by 14.0 points when earlier tests must also pass. Treat 14.0 as an upper bound.
- When inherited code passed earlier tests, the gap was +2.7 on resolving the event with all earlier tests passing and −1.1 on task resolution, with intervals that include zero.
- About 28% of inherited failures are earlier tasks where the agent produced no valid change.
- Keep earlier tests in the pipeline, run them after every agent change, and repair a red start before building.
- SlopCodeBench reports erosion over longer chains. The two results conflict and this page does not resolve them.

## Related

- [Premature Completion](premature-completion.md)
- [Shadow Tech Debt](shadow-tech-debt.md)
- [The Agent-on-Agent Maintenance Penalty](agent-on-agent-maintenance-penalty.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
- [Codeslop Trajectory Minimization](codeslop-trajectory-minimization.md)
