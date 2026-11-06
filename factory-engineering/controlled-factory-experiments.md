---
title: "Test Factory Changes on Representative Work Before Promotion"
term: "Controlled Factory Experiments"
description: "Compare factory configurations on representative tasks, preserve missing outcomes, and use bounded production evidence to decide promotion or rollback."
tags:
  - factory-engineering
  - tool-agnostic
  - evals
last_reviewed: 2026-11-06
maturity: emerging
---

# Test Factory Changes on Representative Work Before Promotion

> Factory experiments support promotion decisions when representative tasks, complete outcome records, and production checks bound what replay results can establish.

A controlled factory experiment compares a candidate configuration with a recorded baseline before wider use. Replay supports conclusions about the tested tasks. Production claims need representative exposure and a suitable comparison design. [Warp's benchmarks](https://docs.warp.dev/factories/benchmarks/) document replay and follow-up; [Google's canary guidance](https://sre.google/workbook/canarying-releases/) explains exposure and attribution limits.

## Record the decision before running trials

The record below is a proposed synthesis, not a vendor schema. It combines [Warp's versioned configuration practice](https://www.warp.dev/blog/7-ways-to-build-a-software-factory) with [Google's rollout controls](https://sre.google/workbook/canarying-releases/).

| Record | Specify before comparison |
|---|---|
| Hypothesis and owner | Expected change, decision owner, and evidence needed to decide |
| Task cohort | Selection rule, task types, difficulty groups, exclusions, and separate regression cases |
| Versions | Baseline and candidate configuration, repository starting state, environment, and evaluator versions |
| Trial plan | Repetitions per task and configuration; quality criteria, cost boundary, and acceptable variance |
| Production plan | Allocation rule, exposure limit, observation window, rollback trigger, and rollback target |
| Outcome ledger | Every assigned trial, terminal status, available scores, missing evidence, and evidence links |
| Decision | Promote, retain baseline, rollback, or inconclusive, with reason and owner |

Proposed quality gate: reject promotion when the candidate fails the declared quality criterion, even if its measured cost falls. Set criteria first. Uber's [joint quality-and-cost comparisons](https://www.uber.com/us/en/blog/efficient-software-factory/) motivate this rule; the source does not document this exact gate.

## Replay comparable work and retain missing outcomes

Run baseline and candidate against the same tasks and starting states. Repeat trials. Inspect their spread. Warp preserves run inputs and supports repetitions. [Anthropic recommends clean trial environments](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), including isolation from earlier trials' files and git history.

Reserve separate regression cases that you do not use to tune the candidate. This holdout rule is a proposed safeguard, not a reported Warp or Uber protocol.

Keep assigned trials separate from scored results. Warp can score available evidence from a blocked trial while retaining its blocked status. Failed or canceled benchmarks show only results that finished scoring before the run stopped. List missing scores separately. Record their causes. Never count them as successful work. [Warp benchmark result semantics](https://docs.warp.dev/factories/benchmarks/) define these limits.

Use [cost-quality Pareto measurement](../token-engineering/cost-quality-pareto-measurement.md) for configuration comparisons and [isometric harness ablation](../patterns/agent-design/isometric-harness-ablation.md) for component attribution. Keep those methods separate from the promotion decision.

## Compare production outcomes within a bounded rollout

This rollout protocol adapts [Google's canary guidance](https://sre.google/workbook/canarying-releases/) to factory configurations. Limit candidate exposure, retain a contemporaneous baseline where feasible, and observe the declared window before deciding. Record the allocation rule, task mix, and any other configuration changes that occur during the same observation window. Restore the recorded baseline when a rollback trigger fires.

Distinguish the claims you can make:

- Offline comparison describes performance on the fixed replay cases.
- Before/after observation describes an association. Google warns that timing changes can confound attribution.
- A causal production claim needs a design that addresses allocation, selection, missing outcomes, and interference. [METR's experiment update](https://metr.org/blog/2026-02-24-uplift-update/) shows why task randomization alone does not resolve selection and noncompletion.

Record 3 time measures separately: elapsed delivery time, agent runtime, and human effort. This accounting rule is synthesis prompted by [METR's concurrent-agent timing problems](https://metr.org/blog/2026-02-24-uplift-update/). Log active human work intervals and overlapping tasks. Allocate each human interval once, or mark it shared and unallocated. Do not sum agent durations as human labor. Leave unknown time visible.

Define included charges. [Warp cautions](https://docs.warp.dev/factories/benchmarks/) that reported costs can omit external charges and that trial duration differs from billable active time.

## Why it works

Preserved inputs make a comparison inspectable; clean starting environments reduce contamination from previous trials. These mechanisms support repeatable replay evidence. [Warp](https://docs.warp.dev/factories/benchmarks/) documents the first; [Anthropic](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) describes the second. Bounded exposure limits the work affected while production evidence accumulates, as [Google's canary analysis](https://sre.google/workbook/canarying-releases/) explains.

## When this backfires

Low-volume workflows can lack enough comparable work for a useful live comparison. Anthropic reserves [live A/B testing for sufficient traffic](https://www.anthropic.com/research/demystifying-evals-for-ai-agents). For such workflows, consider a small regression check and reversible release; report the decision's uncertainty.

Selective task submission or unequal completion can distort completed-task averages. [METR reports both problems](https://metr.org/blog/2026-02-24-uplift-update/). Show allocation and missing outcomes alongside results.

Shared infrastructure can contaminate comparisons; [Google documents shared-cache and overlapping-canary risks](https://sre.google/workbook/canarying-releases/). For factory experiments, also investigate shared reviewer queues as a possible interference path. That reviewer check is a proposed application of the isolation concern.

## Example

Uber built uReview's benchmark from real PRs with known bugs, grouped by difficulty. It measured precision, recall, F1, cost per review, latency, timeouts, and noise. Uber reports that a model switch improved F1 while reducing cost per PR. [Uber's account](https://www.uber.com/us/en/blog/efficient-software-factory/) documents a joint quality-and-cost selection, without establishing a randomized production effect or universal saving.

The proposed reject-on-quality-failure rule above is separate from this historical result. Uber's account does not supply a cheaper candidate rejection for this example.

## Key Takeaways

- Attach the outcome ledger to the decision so reviewers can inspect omissions before accepting a completed-task average.
- Record an inconclusive result when the planned production comparison lacks representative exposure.
- Keep shared, unallocated human time visible in the decision record rather than forcing a productivity estimate.

Use the [cost ledger](cost-per-accepted-change.md) for human-time allocation and included spending. Keep those accounting rules fixed across candidates.

## Related

- [Bounded Factory Rollout with Named Owners and Limits](bounded-factory-rollout.md)
- [Reconstructable Factory Runs: Records and Replay Limits](reconstructable-factory-runs.md)
- [Total Cost Accounting per Accepted Software Factory Change](cost-per-accepted-change.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Factory Engineering](index.md) — the wider delivery process
- [Cost-Quality Pareto Measurement](../token-engineering/cost-quality-pareto-measurement.md) — compare cost and quality across configurations
- [Isometric Harness Ablation](../patterns/agent-design/isometric-harness-ablation.md) — examine component contributions
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — select changes from repeated failures
