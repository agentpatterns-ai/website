---
title: "Factory Engineering: Building and Improving Software Delivery Systems"
description: "Design, operate, measure, and improve software factories. Explore work intake, agent pipelines, verification, recovery, and team ownership."
tags:
  - factory-engineering
  - tool-agnostic
  - index
last_reviewed: 2026-11-06
---

# Factory Engineering

> Factory engineering covers the design, operation, and improvement of the systems that produce software with coding agents.

This section connects work intake, agent execution, verification, release, and production feedback. Use it to find guidance for the whole delivery process. Existing pages keep their public URLs.

Suggested reading order: start with the [category definition](factory-engineering.md), then [stage boundaries](../workflows/issue-to-pr-delegation-pipeline.md) and [factory configuration](factory-as-code.md). Next read acceptance, authority, and recovery. Finish with measurement and a bounded rollout.

## Foundations and architecture

Start with the production model, then examine how work enters and passes through the system.

- [Factory Engineering](factory-engineering.md) — category definition and competing practitioner meanings
- [Factory as Code](factory-as-code.md) — version the factory definition separately from product and run records
- [Work Dispatch and Change Integration](work-dispatch-and-change-integration.md) — separate eligibility to execute from permission to integrate
- [The Software Factory Model](../workflows/software-factory-model.md) — production models, verification limits, and human review choices
- [Factory Over Assistant](../workflows/factory-over-assistant.md) — parallel agent work and asynchronous review
- [Backlog Triage](../workflows/backlog-triage-skill.md) — verify request claims and preserve unresolved readiness decisions
- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md) — connect analysis, implementation, and review

## Verification and operations

Use these pages to examine evidence, authority, and recovery across the delivery process.

- [Acceptance Scenario Lifecycle](acceptance-scenario-lifecycle.md) — author, calibrate, and maintain acceptance evidence
- [Release Authority Boundaries](release-authority-boundaries.md) — assign merge, deployment, waiver, and restart decisions
- [Reconstructable Factory Runs](reconstructable-factory-runs.md) — retain run identity and evidence with explicit replay limits
- [Run Recovery and Product Rollback](run-recovery-and-product-rollback.md) — establish effects before retry, compensation, or rollback
- [Evidence-Bundled Agent PRs](../verification/evidence-bundled-agent-prs.md) — package evidence for a review decision
- [Protect the Oracle from the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) — control changes to tests and acceptance criteria
- [Judgment Relocation](../human/judgment-relocation.md) — assign responsibility for product and verification decisions
- [Evidence-Guided Recovery](../patterns/agent-design/evidence-guided-recovery-ambiguous-outcomes.md) — establish external effects before retrying an operation

## Measurement and improvement

Use outcome evidence to decide which part of the factory needs work.

- [Cost per Accepted Change](cost-per-accepted-change.md) — define the counting event, cohort, and included costs
- [Controlled Factory Experiments](controlled-factory-experiments.md) — compare candidate configurations before promotion
- [Verification Capacity Saturation](../verification/verification-capacity-saturation.md) — examine the capacity to check generated changes
- [Intervention Rate as a Diagnostic](../human/intervention-rate-diagnostic-north-star.md) — separate correction, approval, repair, and recovery measures
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — connect repeated failures to changes in agent configuration

## Adoption and ownership

- [Bounded Factory Rollout](bounded-factory-rollout.md) — name output owners, capacity limits, and expansion decisions

The output owner decides whether work is useful. The scenario owner maintains acceptance evidence. The [release-authority contract](release-authority-boundaries.md) assigns advancement and restart decisions. The recovery operator carries out the authorized action. One person may hold several roles; record each responsibility explicitly.

## Related

- [Harness Engineering](../patterns/agent-design/harness-engineering.md) — execution environments and controls around agents
- [Tool Engineering](../tool-engineering/index.md) — interfaces through which agents act
- [Context Engineering](../context-engineering/index.md) — information supplied to agents
- [Loop Engineering](../loop-engineering/index.md) — iteration, convergence, and stopping conditions
