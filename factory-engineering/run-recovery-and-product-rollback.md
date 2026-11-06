---
title: "Factory Run Recovery and Compatible Product Rollback"
description: "Recover interrupted delivery runs by checking external effects, assigning recovery owners, and separating factory repair from compatible product rollback."
tags:
  - factory-engineering
  - tool-agnostic
  - workflows
maturity: emerging
last_reviewed: 2026-11-06
---

# Factory Run Recovery and Compatible Product Rollback

> Factory run recovery requires evidence of external effects before resumption and a separate compatibility decision before product rollback.

Run recovery is a decision about continuing interrupted delivery work when provider contracts and recorded effects establish a safe next action. Use this workflow when recovery crosses systems with different retry rules, data formats, or owners. Its operating sequence is editorial synthesis of [AWS retry guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [PostgreSQL rollback restrictions](https://www.postgresql.org/docs/18/pgupgrade.html#PGUPGRADE-NOTES), and [Microsoft compensation guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction).

## Separate the recovery decisions

Use these working definitions:

- Run resumption continues a recorded delivery task after checking completed and unresolved effects.
- Factory-configuration rollback restores a selected version of the delivery system's configuration.
- Product rollback restores an earlier compatible product version, with a separate decision about its data.

A configuration rollback does not establish that product data is repaired. Google SRE warns that rollback alone can leave data corruption unresolved. [Google SRE on-call guidance](https://sre.google/workbook/on-call/)

## Choose an action from confirmed effects

Start with the last confirmed stage, dispatched operations, and their recorded outcomes. The table proposes local owner assignments based on [retry contracts](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [compensation limits](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction), and [rollback compatibility](https://builder.aws.com/content/3F04j2yRAAMBuPSPs50xwXZqg01/ensuring-rollback-safety-during-deployments).

| Current stage | Effects and uncertainty | Decision | Accountable owner |
|---|---|---|---|
| Local preparation or verification | No external mutation dispatched; local progress known | Resume valid work, or restart disposable work after checking inputs | Run operator |
| Forge or tracker write | Missing response; outcome unknown | Inspect provider records; retry only within a valid provider contract; otherwise stop mutations and escalate | Integration owner through run operator |
| Publication completed | Remote artifact identity and state confirmed | Record the effect; continue from the next authorized stage | Run operator and release owner |
| Partial completion | Confirmed effects need repair | Apply service-specific repair or compensation; track its outcome | Affected system owner |
| Product deployed | Bad release confirmed; compatibility established | Roll back product; verify resulting service state | Product on-call or release owner |
| Product data changed | Old-version compatibility absent or unknown | Stop automatic rollback; choose supported restoration or forward repair | Data owner with incident lead |
| Shared factory defect | Other runs depend on faulty configuration or integration | Pause affected intake and dispatch; repair and validate before reopening | Factory operator or incident lead |

Use [evidence-guided recovery](../patterns/agent-design/evidence-guided-recovery-ambiguous-outcomes.md) for uncertain outcomes and [idempotent operations](../patterns/agent-design/idempotent-agent-operations.md) for provider-protected retries.

## Stop unknown effects and bound attempts

Stop mutations when available evidence and the provider contract cannot establish a safe action. Escalate to the integration owner through the run operator. An internal run ID supplies no provider deduplication guarantee. AWS's design depends on a caller-provided identifier within the destination API's contract. [AWS idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

Adopt a recovery handoff record with the run ID, operation identity, request details, timestamps, confirmed effects, unresolved outcomes, and responsible owner. Preserve useful logs without delaying urgent mitigation, as [Google SRE troubleshooting guidance](https://sre.google/sre-book/effective-troubleshooting/) recommends.

Set an attempt limit before resuming automated repair. Stripe returns a branch to its human operator after the second push and CI run. Choose a limit for your own workflow. [Stripe Minions, part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2)

## Contain a shared factory defect

Pause intake and dispatch for the affected integration or configuration. Repair it, validate recovery, then reopen that scope. This is an application of [circuit breaker isolation and restricted recovery probes](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker), not a vendor-defined factory protocol.

After the halt, inventory committed PRs, tracker changes, deployments, data writes, and notifications. Keep in-flight writes unresolved until their outcomes are known. Scheduling stops do not reverse these effects; each needs its own disposition. [AWS retry semantics](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) and [Google's rollback limits](https://sre.google/workbook/on-call/) support this distinction.

As a local policy, reassess recovery when configuration or release authority changes. Use [canary policy rollout](../workflows/canary-rollout-agent-policy.md) for staged configuration validation.

## Why it works

Provider-enforced request identity supports safe repetition within its contract. Compatibility checks constrain which product state can be restored. Compensation handles application-specific effects and can require human intervention. [AWS](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [PostgreSQL](https://www.postgresql.org/docs/18/pgupgrade.html#PGUPGRADE-NOTES), and [Microsoft](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) document these limits.

## When this backfires

A separate recovery controller adds little when disposable local work and provider-protected writes already cover the task. Prefer existing retry controls and human handoff in that case. [AWS retry guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) and [Microsoft's circuit breaker applicability guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) support that narrower choice.

Compensation can overwrite legitimate concurrent changes. It needs application-specific rules and progress tracking because compensation itself can fail. [Microsoft compensating transactions](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)

## Example

### GitHub timeout and PR inspection

GitHub documents a timeout response when API processing exceeds 10 seconds, while reserving the right to change that window. The response alone does not establish a write's outcome. [GitHub REST troubleshooting](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api#timeouts)

For an ambiguous PR creation request, inspect the recorded repository and head branch before another mutation. GitHub's list endpoint supports a `head` filter and `state=all`; the default state is `open`. An open-only search omits closed records. [GitHub pull request API](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests)

An empty listing supplies no documented guarantee that an earlier write cannot complete. If inspection and the provider contract leave the next action unsafe, stop and escalate. This applies the workflow's stop condition to documented API behavior; it is not a reported duplicate-PR incident.

### PostgreSQL data compatibility

PostgreSQL major releases can change the storage format. Minor releases retain storage compatibility within a major version. [PostgreSQL 18 upgrade documentation](https://www.postgresql.org/docs/18/upgrading.html)

After `pg_upgrade --link`, starting the new cluster changes shared files and makes the old cluster unsafe to use. PostgreSQL then requires restoring the old cluster from backup. [PostgreSQL 18 recovery instructions](https://www.postgresql.org/docs/18/pgupgrade.html#PGUPGRADE-NOTES)

Assign this decision to the database owner. Selecting the old executable or reverting factory configuration does not meet that documented restoration requirement.

## Key Takeaways

- Give unresolved effects an owner and a stop condition before automated repair resumes.
- Check product data compatibility separately from factory configuration recovery.
- Keep completed and in-flight effects in the recovery record after stopping affected intake.

Recovery operators establish state and carry out the approved action. The [release-authority contract](release-authority-boundaries.md) names who may authorize restart.

## Related

- [Release Authority Boundaries for Software Factories](release-authority-boundaries.md)
- [Reconstructable Factory Runs: Records and Replay Limits](reconstructable-factory-runs.md)
- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Factory Engineering](index.md) — delivery-system design and operation
- [Rollback-First Design](../patterns/agent-design/rollback-first-design.md) — plan action reversibility before execution
- [Fleet Irreversibility Budget](../patterns/agent-design/fleet-irreversibility-budget.md) — assess aggregate irreversible effects
