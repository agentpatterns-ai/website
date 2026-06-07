---
title: "Quality Score Rubric and Simplification Log for Agent Harnesses"
description: "Pair an A/B/C/D quality rubric with a simplification log to make agent harness health measurable and harness shrinkage visible as model capability rises."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - harness-engineering
aliases:
  - harness quality score
  - harness simplification log
last_reviewed: 2026-06-02
---

# Quality Score Rubric and Simplification Log

> Pair an A/B/C/D quality rubric with a simplification log to make agent harness health measurable per module and harness shrinkage visible over time.

The pattern is two artefacts: a `QUALITY_SCORE.md` that grades each module, and a simplification log that records every harness primitive retired as model capability grew enough to remove it. The rubric makes harness *health* legible; the log makes harness *shrinkage* legible. The canonical [template lives in the walkinglabs repo](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/repo-template/docs/QUALITY_SCORE.md); treating the harness as a first-class engineering surface draws on research into terminal coding agents ([Bui, 2026](https://arxiv.org/abs/2603.05344)).

## The Four Tiers

The grading scale, verbatim from the source template:

- **A** — verified, legible, stable, boundaries enforced.
- **B** — working with minor gaps.
- **C** — partially working, notable confusion or instability.
- **D** — broken, unsafe, or structurally unclear.

The discipline depends on *using* the lower grades. "Is the test suite OK?" hides ambiguity behind a yes-or-no answer; a `C` grade forces the reviewer to name the instability.

## What Each Artefact Captures

The template grades two axes plus a benchmark table:

| Artefact | What it records |
|---|---|
| **Product Domains table** | Per domain: Grade / Verification / Agent Legibility / Test Stability / Key Gaps / Last Updated |
| **Architectural Layers table** | Per layer (Types, Services, Runtime, UI): Grade / Boundary Enforcement / Agent Legibility / Key Gaps / Last Updated |
| **Benchmark Snapshots table** | Per harness variant: Date / Variant label / Completion Rate / Retries / Defects Before Review / Notes |
| **Simplification Log table** | Per removal: Date / Component Removed / Outcome (degraded or unchanged) / Decision (restore or keep removed) |

The benchmark snapshots are an outcome record, not a path record — completion rate is the kind of [outcome grade](../verification/grade-agent-outcomes.md) that survives the agent finding an unexpected path to the goal.

## How the Log Defends Against Bloat

Harness scaffolding is depreciating capital — its value falls as model capability rises ([Harness Impermanence](harness-impermanence.md)). Without a record of what was retired, every removal looks like a risky deletion of working code. The simplification log inverts the default: additions are easy, removals require recorded outcomes to reverse.

This pairs with the classification in [Temporary Compensatory Mechanisms](temporary-compensatory-mechanisms.md): the log tracks compensatory removals, not structural ones. Sandboxes and permission gates are never retired by a model upgrade and should not appear in the log.

## How the Rubric Feeds the Tuning Loop

[Harness hill-climbing](harness-hill-climbing.md) is an eval-driven local search over harness configuration. The benchmark snapshots table is the persistent record of that loop's output: when a tuning regression appears later, the team has the last known-good configuration with its date, variant label, and completion rate. Without the snapshot, every iteration climbs from an unknown baseline.

## Update Cadence

End-of-session updates ride a moment when state is already top-of-mind. A `Stop`-event hook can emit a grade *hint* from `lint --check` exit codes, test pass rate, or defect counts; a human or supervisor agent ratifies it into the rubric. The [pre-completion checklist](../verification/pre-completion-checklists.md) pattern is the same wiring point. The hook should propose, not write — automated grade rewrites turn the rubric into a moving average of recent build state, which loses the "uncomfortable truth" the rubric is meant to surface.

## When This Backfires

The rubric and log are paperwork. They pay back only under specific conditions:

- **Solo or two-person projects.** Without a second reviewer the rubric captures one person's biases uncorrected and decays into ritual.
- **Pinned-model deployments.** The simplification log is a no-op when no model upgrade will arrive to obsolete the scaffolding ([Harness Impermanence](harness-impermanence.md)).
- **Single-module repos.** The two tables collapse to one row each — a README sentence carries the same information at lower cost.
- **Mature, stable harnesses.** When grades have not moved in months, the rubric becomes a file no one reads. The signal is in the deltas.
- **Staleness risk.** A `QUALITY_SCORE.md` that has not been updated in three sessions is worse than no rubric — it implies a system is healthy that may not be. The rubric is only useful when the update cadence is enforced (Stop hook, PR template, or recurring review).

If these conditions apply, the same signals can be surfaced from existing telemetry: completion rate from the eval dashboard, defects from the issue tracker, simplifications from commits tagged `chore(harness): remove`. The rubric file pays back when its forced legibility beats reconstructing the picture from scattered sources.

## Example

A team running a coding agent on Terminal Bench maintains `QUALITY_SCORE.md` at the repo root. After a tuning session that removed the retry-with-reminder middleware, the simplification-log entry reads:

```markdown
## Simplification Log

| Date       | Component Removed                  | Outcome    | Decision        |
|------------|-----------------------------------|------------|-----------------|
| 2026-04-12 | retry-with-instruction-reminder   | unchanged  | keep removed    |
| 2026-03-30 | json-repair-middleware            | unchanged  | keep removed    |
| 2026-02-18 | sub-task summarization-loop       | degraded   | restored        |
```

The benchmark snapshot for the same week records the completion-rate delta from removing the middleware:

```markdown
## Benchmark Snapshots

| Date       | Harness Variant              | Completion Rate | Retries | Defects Before Review | Notes                          |
|------------|-----------------------------|-----------------|---------|-----------------------|--------------------------------|
| 2026-04-12 | post-retry-removal          | 66.5%           | 1.2     | 3                     | Reminder middleware retired    |
| 2026-04-05 | baseline (with reminder)    | 66.1%           | 1.4     | 3                     | Last known-good before removal |
```

Six weeks later a regression to 61% appears on a different change. The team has a date-stamped configuration to roll back to and a record of what was retired in between.

## Key Takeaways

- The pattern is two artefacts: a per-module A/B/C/D rubric and a simplification log of retired primitives, maintained together.
- Use the lower grades — `C` and `D` are the signal; an all-`A` rubric is either accurate or unread.
- The simplification log creates a one-way ratchet that defends against harness bloat as model capability rises ([Harness Impermanence](harness-impermanence.md)).
- Benchmark snapshots give [harness hill-climbing](harness-hill-climbing.md) a persistent baseline; tuning regressions become diagnosable.
- The rubric is paperwork — it pays back on multi-person teams with moving harnesses and decays into ritual on solo projects, pinned-model deployments, or stable harnesses.
- Automate the grade *hint*, not the grade. Stop-event signals propose; humans or supervisor agents ratify.

## Related

- [Harness Impermanence](harness-impermanence.md) — the authoring discipline that produces scaffolding cheap enough to retire; the simplification log makes the retirement legible.
- [Harness Hill-Climbing](harness-hill-climbing.md) — the eval-driven tuning loop whose results feed the benchmark snapshots.
- [Temporary Compensatory Mechanisms](temporary-compensatory-mechanisms.md) — the classification that determines what belongs in the simplification log.
- [Grade Agent Outcomes, Not Execution Paths](../verification/grade-agent-outcomes.md) — why the benchmark column is an outcome score, not a path score.
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md) — the Stop-event wiring point for the automated grade hint.
- [Agentic Flywheel](agentic-flywheel.md) — agents proposing harness changes; the rubric is one place those proposals land.
