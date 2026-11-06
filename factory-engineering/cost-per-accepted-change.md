---
title: "Total Cost Accounting per Accepted Software Factory Change"
description: "Define accepted changes, track failed work and human repair, and separate API spend from full factory costs with a sourced partial-cost example."
term: cost per accepted change
tags:
  - factory-engineering
  - tool-agnostic
maturity: emerging
last_reviewed: 2026-11-06
---

# Total Cost Accounting per Accepted Software Factory Change

> Cost per accepted change divides scoped delivery costs by accepted outcomes when task class, acceptance rules, and accounting boundaries stay comparable.

Cost per accepted change is an outcome-based accounting proposal for a comparable class of software factory work. Use it when you can define acceptance and trace spending through failed attempts and human repair. The full-cost rules below are editorial synthesis. [Uber reports outcome costs alongside quality and volume](https://web.archive.org/web/20261016081304/https://www.uber.com/us/en/blog/efficient-software-factory/); that practice does not validate this full ledger or establish general savings.

## Define acceptance and the reporting boundary

Record merged, deployed, and production-observed events separately. Select one as the accounting acceptance event before counting outcomes. Pre-merge policy approval in the [dispatch contract](work-dispatch-and-change-integration.md) does not count as this event. For production-observed acceptance, specify the required checks and observation window. Set a policy for later defects: retain the original report and publish corrections with their dates.

Use these proposed reporting rules:

- Declare the task class, application, currency, and cutoff. Keep rejected, abandoned, and unresolved work visible.
- For a period ratio, divide costs incurred during the period by outcomes accepted during it. Disclose opening and closing unfinished work.
- For a fixed-intake cohort, select work items by intake date and follow their costs and outcomes through the cutoff. Label incomplete cohort results provisional.
- Count each accepted work item once. Report zero accepted outcomes as an undefined ratio, alongside spending and unresolved counts.

The period ratio includes work at different completion stages; reserve lifetime-cost claims for completed cohorts. These rules extend [DORA's guidance on comparable application-level measurement](https://web.archive.org/web/20261024202237/https://dora.dev/guides/dora-metrics/).

Pair accepted throughput with reverts, escaped defects, and rework over the declared window. Keep pre-merge revisions separate from [DORA deployment rework](https://web.archive.org/web/20261024202237/https://dora.dev/guides/dora-metrics/), which concerns unplanned deployments caused by production incidents.

## Reconcile costs once

For the proposed full-cost numerator, add billed delivery spend, monetized active human effort, and allocated factory overhead. Show each subtotal separately. State exclusions before calling the result total cost within that boundary.

| Cost record | Proposed treatment |
|---|---|
| Inference estimate | Retain for attribution; do not add it to an invoice that already covers it |
| Billed spend | Reconcile API, compute, and service charges to billing records |
| Human effort | Record active review, prompting, repair, and recovery time; disclose hours and labor rates |
| Factory overhead | Allocate maintenance and measurement costs using a stated basis; exclude costs already charged directly |

Assign a stable work ID to attempts, retries, child runs, and human repairs. Retain failed-attempt costs even when no change qualifies. Reconcile allocated costs plus the unallocated remainder to the source total. For inclusive parent totals, use either that total or its component costs once.

This distinction matters for [Warp's dashboard](https://github.com/warpdotdev/docs/blob/403d5d626153a8d4ee5dc37effddc86ce2f9d4aa/src/content/docs/factories/measure-and-improve.mdx). Its cost per PR is the median estimated cost of opened PRs. Run totals include child runs and split across PRs; external inference can be incomplete. That median cannot substitute for aggregate spending divided by accepted work. Warp's autonomy counts merged PRs with no human code push. A human opening the PR counts as a push. This does not establish zero human effort.

## Why it works

The accounting mechanism keeps failed work in the numerator while counting accepted outcomes in the denominator. [BurnLens uses repository spend, including rejected and abandoned work, per merged PR](https://github.com/sairintechnologycom/burnlens/blob/6a83d1e55f0244b1d16c3e011c0eaa35773e64de/frontend/src/app/cost-per-outcome/page.tsx). [Uber measures outcome costs with quality and volume](https://web.archive.org/web/20261016081304/https://www.uber.com/us/en/blog/efficient-software-factory/). Together, they support examining cost per outcome; neither establishes that this proposed accounting method causes savings or positive ROI.

## When this backfires

Detailed attribution adds work. For low-volume decisions, start with billed spend, stable outcome definitions, and existing quality measures. [DORA warns against excessive measurement investment and single-metric targets](https://web.archive.org/web/20261024202237/https://dora.dev/guides/dora-metrics/).

Avoid these comparisons:

- Concurrent agent duration as human labor. [METR describes concurrent-work and selection problems in task-time measurement](https://web.archive.org/web/20261031052227/https://metr.org/blog/2026-02-24-uplift-update/). Record active human time separately.
- Mixed task classes or changing PR sizes. [BurnLens notes varying PR size and work that lands without PRs](https://github.com/sairintechnologycom/burnlens/blob/6a83d1e55f0244b1d16c3e011c0eaa35773e64de/frontend/src/app/cost-per-outcome/page.tsx). Retain a stable work-item definition.
- Short observation windows as final economics. Under this proposal, unfinished work and later corrections require provisional results or dated revisions.

## Example

[BurnLens reports](https://github.com/sairintechnologycom/burnlens/blob/6a83d1e55f0244b1d16c3e011c0eaa35773e64de/frontend/src/data/cost-per-outcome.json) $710.85 in API spend and 104 merged PRs for its `burnlens` repository. The telemetry window runs from July 10 to August 15, 2026. Dividing $710.85 by 104 gives $6.84 per merged PR after rounding.

This is a real partial-cost calculation. BurnLens excludes human time and attributes spending to repositories, not individual PRs. Rejected and abandoned work remains in repository spend. The vendor-reported totals do not provide transaction-level reconciliation or a fixed-intake lifetime cohort.

No full itemized ledger is available in the inspected sources for failed attempts, human repair, and allocated overhead. Do not fill those gaps with invented amounts or treat the reported $6.84 as total delivery cost.

## Key Takeaways

- Publish the acceptance rule and cutoff with the ratio; mark incomplete cohort results provisional.
- Keep estimates, invoices, active human effort, and allocated overhead distinct so reconciliation counts each cost once.
- Treat the real API-spend example as partial evidence. The full accounting proposal remains unvalidated.

## Related

- [Test Factory Changes on Representative Work Before Promotion](controlled-factory-experiments.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Factory Engineering](index.md) — the delivery-system scope for this accounting proposal
- [Cost-Quality Pareto Measurement for Agent Configurations](../token-engineering/cost-quality-pareto-measurement.md) — compare execution configurations
- [The Four Terms That Decide What an Agent Task Costs](../token-engineering/four-term-agent-cost-model.md) — inference-cost components
- [Intervention Rate as a Diagnostic North Star, Not a Target](../human/intervention-rate-diagnostic-north-star.md) — interpret human corrections alongside task difficulty
- [Agent Loop Go/No-Go: When Looping Earns Its Cost](../loop-engineering/agent-loop-go-no-go-gate.md) — decide whether a bounded loop is justified
