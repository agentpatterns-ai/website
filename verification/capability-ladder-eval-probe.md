---
title: "Capability-Ladder Probe: Calibrate an Eval Before You Trust Its Score"
term: "Capability-Ladder Probe"
description: "On a task family where longer reasoning helps, a stronger model at higher effort should score higher. A flat reading there puts the fault in the eval rather than the system, and a baseline with no headroom cannot reliably attribute your next change."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - capability ladder probe
  - eval monotonicity check
  - ordered-stimulus eval calibration
last_reviewed: 2026-10-01
maturity: emerging
---

# Capability-Ladder Probe: Calibrate an Eval Before You Trust Its Score

> Where longer reasoning helps a task, a stronger model at higher effort should score higher; an eval missing that ordering is itself the fault.

Before you trust an eval score, run it again on a weaker model and at a lower effort setting. You already know which way those two scores should move, so the ordering they produce is a reading you can check. The source that names this test puts the diagnosis beside the property: "More capable models and higher effort levels typically should perform better on an evaluation. If they don't, ambiguous tasks or a miscalibrated grader often are hobbling performance" ([Martin, claude.dev, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).

## When the probe is worth running

Run it before the first round of [harness hill-climbing](../patterns/agent-design/harness-hill-climbing.md), under three conditions.

- A model set you can rank by capability without using this eval, plus an effort control applied the same way every run. Effort "may not be applied consistently" across a configuration ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).
- A task family where longer reasoning is expected to help. Counting with distractors and regression with spurious features are documented exceptions ([arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).
- Budget for a run multiplied by every rung, spent before one change of yours has been tested.

## What the ladder reads

| Reading | What it says |
|---|---|
| Scores rise with capability and with effort | The eval resolves the axis you are about to change. Go ahead. |
| The top rung sits well below a perfect score | A change has room to show above the baseline. |
| Flat, where the family says it should rise | Stop. The fault is in the task set or the grader. |

Headroom is about attribution rather than difficulty. The strongest model at the highest effort "should be well below 100% on the evaluation, otherwise you can't reliably judge how changes impact performance" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). The `claude-api` skill's build-eval command draws its line at roughly 95%, above which a hillclimb "should aim to explore cost or latency rather than quality" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).

Per task, replication separates a hard case from a broken one. The tell is that "a task fails every evaluation run, regardless of the number of replicates", and a good task meets two conditions: "two domain experts would reach the same verdict and everything the grader checks is stated in the task" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).

## Where a flat ladder comes from

### Adversarial sampling

"Model capability is jagged. If you pick cases because today's model fails them, you are sampling the valleys of one model's capability surface" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). The eval can end up "measuring that model's failure fingerprint rather than what is intrinsically hard or valuable for your application to do". That is the expensive kind of broken eval, because it runs, returns a plausible number, and moves for nothing.

The fix is a sentence you have to be able to write. "Pick hard cases because a human judged them hard: a useful test is to be able to say why a task is hard before you include it" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). A study of 60 benchmarks lands in the same place from outside, finding that "resilience to saturation is impacted by expert-curation, not by public test data" ([arXiv:2602.16763v4](https://arxiv.org/abs/2602.16763v4)). Production traffic is not the safe substitute it looks like, because "users sometimes try what they expect to work, so a task distribution drawn strictly from user traffic may skew easy" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).

### A grader that disagrees with itself

Replay the grader on one output and compare the two verdicts, which the `claude-api` skill's build-eval command does during its baseline runs ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). A stable grader can still check the wrong thing, which the ladder surfaces as a task that never moves. [Measuring the judge as an instrument](judge-instrument-stability-check.md) covers the stability half.

### An environment that answers for the model

Watch for cases where "leftover state from an earlier trial (a file, a git history) can hand the agent the answer" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). Such a case scores the same at every rung, so it reads as flat. [Answer-Reachable Eval Environments](../patterns/anti-patterns/answer-reachable-eval-environments.md) prices the two ways to scrub it.

## Why it works

You cannot check an instrument against the quantity it reports, because that quantity is the thing you do not know. The two ladders supply orderings from outside the eval, so their direction is not in dispute and the reading has something to be wrong against. A reading that fails to reproduce an undisputed ordering puts the fault in the instrument. That is why the source routes a flat ladder to the task set or the grader instead of to the system ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).

The ceiling check is the same property at the other end. Saturation is the loss of separating power, "making it difficult to differentiate models and diminishing their long-term value" ([arXiv:2602.16763v4](https://arxiv.org/abs/2602.16763v4)), and a near-ceiling baseline inflicts that loss on every comparison run after it.

## When this backfires

- Task families where longer reasoning hurts. Gema and colleagues "construct evaluation tasks where extending the reasoning length of Large Reasoning Models (LRMs) deteriorates performance", spanning "simple counting tasks with distractors, regression tasks with spurious features, deduction tasks with constraint tracking, and advanced AI risks" ([arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)). A falling effort axis there is the result, and calling it a grader bug sends you to repair a working instrument.
- One model, so one axis. A checkpoint pinned for compliance or self-hosting leaves only the effort ladder, whose control may not be applied consistently ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).
- A regression gate you expect to pass at 100%, where the ceiling is the design. Change the objective instead. The source's answer to a saturated eval is to pursue cost reduction "while keeping performance at parity" ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)).
- A borrowed capability ranking. Nearly half of the 60 benchmarks studied showed saturation, with rates increasing with age ([arXiv:2602.16763v4](https://arxiv.org/abs/2602.16763v4)), so a leaderboard ranking may be a claim rather than a known ordering.

## Example

The `claude-api` skill's own eval shows what skipping the probe costs ([Martin, 2026](https://claude.dev/blog/automating-eval-design-and-hillclimbing/)). The baseline scored 66%. Filling in eight missing feature sections reached 74%, and correcting errors in the C# and Java type tables reached 77%.

Then the score stalled for two rounds. The next step made no edit and only sorted the remaining failures by root cause. That analysis found the skill content was present but the model wrote older API shapes, so a table steering it from remembered forms to current ones reached 80%. It also found what a ladder reads first. "Tasks that never improved in performance despite addressing obvious content gaps are tells that the example or grader is flawed. One task asked for code that catches one error type, while its grader wanted a chain of at least three." Repairing those, with more skill edits, took the run to about 88% by round 24.

The grader repair came in the third phase of work. The defect sat in the task set through the first two phases, and it scored every edit made there.

## Key Takeaways

- Run both ladders before the first change, not after the score stalls.
- Write down the ordering you expect and where the ranking came from. A ranking lifted from a saturated benchmark is not an ordering you know.
- A task that fails every replicate is broken, not hard. The replicate count is what tells them apart.
- At a baseline near 95%, switch the objective to cost or latency instead of repairing the eval.
- A falling effort curve can be the honest result. Check the task family against the inverse-scaling list before calling it a defect.

## Related

- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — the run-to-run variance half, and the floor-and-ceiling band a cell has to sit inside
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — how small a change the eval can resolve, once the ladder says it resolves anything
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — replaying a judge to measure its own noise, the cheapest of the flat-ladder diagnoses
- [Answer-Reachable Eval Environments](../patterns/anti-patterns/answer-reachable-eval-environments.md) — leftover container state solving the task before the model does
- [Harness Hill-Climbing](../patterns/agent-design/harness-hill-climbing.md) — the iteration loop this probe gates
