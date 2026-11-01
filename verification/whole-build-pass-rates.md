---
title: "Whole-Build Pass Rates in Long-Horizon Agent Benchmarks"
term: "Whole-Build Pass Rate"
description: "A whole-build score counts only runs where every check passes. Read it next to the per-check rate: on ViBench 2.0 the top models pass over 90% of checks and 49% to 65% of builds."
tags:
  - testing-verification
  - evals
  - benchmarks
  - tool-agnostic
aliases:
  - whole-build pass rate
  - build-level pass at 1
  - conjunctive benchmark scoring
last_reviewed: 2026-10-30
maturity: emerging
---

# Whole-Build Pass Rates in Long-Horizon Agent Benchmarks

> A whole-build score counts only the runs where every check passes, so it sits far below the per-check rate measured on the same runs.

Report both numbers, and read the gap between them only once models clear the floor where the strict score moves at all. A benchmark scoring a multi-hour build has no single passing test to point at, so it has to choose what counts as success. Replit's ViBench 2.0 publishes two metrics side by side. The first is "Pass@1: the share of builds in which every test plan passes". The second is "Plan pass rate: the share of test plans where all steps pass, averaged by product" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)). The distance between them on one set of runs is the part you can act on.

## What the two scores measure

ViBench 2.0 starts the agent on an empty project. The agent builds a product one feature at a time, modeled on products like Uber, GitHub, or Google Docs. The suite holds "seventeen products, 241 feature requests, and 544 test plans". The agent "builds a first version of the given product from a short spec, then adds up to eighteen features on top of its existing code". A grading agent then runs each test plan in a real browser, clicking and typing through it ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)).

At the top of the table the two metrics separate by at least 25 points, and by more than 40 for Opus 5.5. GPT-6.1 Sol leads on build-level pass@1 at 65%, GPT-6 Astra scores 60%, and Opus 5.5 scores 49%. "All three pass more than 90% of their test plans, so most of their failed builds miss by only a few plans" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)). Read the strict number alone and the weakest leader fails half its builds. Read the per-check number alone and each leader gets almost everything right.

## Why it works

A whole-build score is a conjunction, so the weakest check governs it. The gap is informative rather than arithmetic because the failures are not spread evenly. Each new feature has to fit a schema and routes the agent committed to earlier, before it knew what was coming. The design "forces it to choose the schema and routes before knowing what's next, so later features can be harder than earlier ones". Replit names the consequence: "New features have to fit code the agent wrote earlier, and that is where builds often break". It also quantifies the clustering: "Nearly three-quarters of those models' failed builds fail only on these intersections" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)).

On ViBench, a wide gap is a statement about where the work is. Few checks fail, and they fail at feature boundaries, so the engineering problem is integration rather than capability. An agent failing checks uniformly would drag its per-check rate down with it.

The threshold sensitivity shows up independently of Replit. Long-Horizon-Terminal-Bench reports threshold-sensitive scores. Its strongest model moves from "10.9% at a perfect-reward threshold of 1.0" to "15.2% pass@1 at a partial-reward threshold of 0.95" ([Li et al., 2026](https://arxiv.org/abs/2607.08964v3)).

## When this backfires

- The models sit below the floor. When almost no build passes, the strict score pins at zero and orders nothing. ViBench's own generational run shows pass@1 "from 0% for GPT-5.4 to 31% for GPT-6 Sol and 53% for GPT-6.1 Sol", while plan pass rate over the same models "climbs from 42% to 95%" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)). At the bottom of that range the per-check rate carries the signal on its own.
- The work is short-horizon. A bounded fix carries one or a few checks, so conjunction over them returns roughly the per-check rate. The gap is a long-horizon instrument and reports nothing on a single edit.
- Your harness differs. The source states the confound itself: "All models run in one agent harness built on OpenHands, so a model tuned for a different setup may score lower here" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)).
- You want to reproduce it locally. Eight of the seventeen products are public in Harbor format and the remaining nine are held out. Public-product scores also run lower, putting the same model at 53% there against 65% overall ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)).
- The grader is also a contestant. Opus 5.5 grades every build and is scored among them. Replit reports a planted-bug check, a cross-model re-grade where "99.2% were confirmed correct", and "no sign that Opus favors builds from Claude models" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)). That bounds the concern without removing it.

A stronger position argues against the strict metric entirely. Long-Horizon-Terminal-Bench holds that final-outcome grading of long tasks "overlooks intermediate progress and partial solutions, yielding sparse reward signals and an incomplete picture of agent capability", and decomposes each task into graded subtasks instead ([Li et al., 2026](https://arxiv.org/abs/2607.08964v3)). For tracking your own progress month over month rather than ranking vendors, that design gives you a gradient the conjunctive score does not.

## Example

ViBench publishes one of the plans the leaders miss. A design tool's undo feature request specifies that "Each person has their own undo history, so undo only takes back your own changes, never a collaborator's." The test plan has Alice and Bob alternate edits on one rectangle. Alice moves it, Bob renames it, Alice recolors it, and Bob changes its opacity. Alice then presses undo, and the plan verifies that her fill change reverted while Bob's rename and opacity change survived. GPT-6.1 Sol, GPT-6 Astra and Opus 5.5 "fail this plan in eight of their twelve builds" ([Kirani et al., 2026](https://frontier.replit.com/vibench-2-long-horizon-software-benchmark/)).

That is one test plan sitting exactly where two features meet, and it is invisible in a plan pass rate above 90%. One failed plan lowers that product's plan pass rate by one plan. It fails the build outright under the whole-build metric. That asymmetry is what the two scores exist to expose.

## Key Takeaways

- Publish the whole-build rate and the per-check rate together; either alone supports a different decision about the same runs.
- Treat the distance between them as the diagnostic. On ViBench, the leaders' failures concentrate at feature boundaries. A narrower gap at the same build rate would need a different explanation.
- Check that the strict metric is above its floor before you rank on it. ViBench's GPT-5.4 scores 0% pass@1 at the same end of the range where plan pass rate still reads 42%.
- Record the harness with the score. ViBench's figures are conditional on one OpenHands-based harness, by its authors' own statement.

## Related

- [pass@k and pass^k: Capability and Consistency Metrics](pass-at-k-metrics.md) — the orthogonal axis: capability against consistency across repeated attempts, rather than granularity within one run
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — its held-out test gap is another long-horizon score gap, read for reward hacking instead of integration failure
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — how many runs a reported gap needs before it means anything
- [Valid Completion Rate as a Second Scoring Axis](valid-completion-rate-second-axis.md) — a second axis that separates clean termination from task correctness
- [Dual Executable Specifications for Long-Horizon Features](dual-executable-specifications.md) — a build-side response to the same feature-intersection failures this score surfaces
