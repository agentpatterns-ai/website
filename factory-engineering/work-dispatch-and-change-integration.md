---
title: "Work Dispatch and Change Integration in Agent Pipelines"
description: "Separate task eligibility from merge eligibility when execution and integration have different completion rules. Keep dependencies and ownership explicit."
tags:
  - tool-agnostic
  - factory-engineering
last_reviewed: 2026-11-06
maturity: emerging
---

# Work Dispatch and Change Integration

> Separate work dispatch from change integration when starting a task and landing its output require different eligibility rules.

Work dispatch assigns eligible tasks to execution capacity. Change integration decides which candidate changes can enter the target branch together. This distinction is an editorial synthesis of [Symphony's dispatch specification](https://raw.githubusercontent.com/openai/symphony/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md) and [GitHub's merge queue behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue). The sources describe separate systems, with no reported combined deployment. Use the distinction when work completion and merge completion have different conditions.

## Define each queue's decision

Here, task queue means the logical set of pending work. It does not imply that Symphony requires a message broker. The comparison uses each source's own objects and rules:

| Boundary | Object | Eligibility | Completion event |
|---|---|---|---|
| Work dispatch, in Symphony | Normalized tracker issue | Required identity and labels, active nonterminal state, adapter eligibility, no running or claimed entry, available global and per-state capacity | Worker execution ends; successful execution can hand off for review without completing the issue |
| Change integration, in GitHub | Queued PR and its temporary merge group | Branch-protection requirements, enqueueing by a user with write access, then required checks against the latest target branch and queued predecessors | Changes reach the target branch |

[Symphony Draft v1, sections 1, 7, and 8](https://raw.githubusercontent.com/openai/symphony/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md) defines the dispatch contract. [GitHub's merge queue documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) defines integration behavior. An available execution slot supplies no evidence that the output meets those merge requirements.

## Record the handoff states

Define these states locally. The names below are editorial definitions:

- A completed run records an execution outcome. It can succeed without producing a PR.
- A candidate change is an output artifact, if the run produces one.
- Here, a policy-approved PR has cleared your repository's defined acceptance policy. Policy approval alone does not establish queue admission or merge completion. The [cost metric](cost-per-accepted-change.md) selects a later counting event, such as merge or deployment; approval alone does not enter that denominator.
- An integrated change has landed on the target branch.

This vocabulary preserves Symphony's separation of run success from issue completion and GitHub's separate queue admission and merge events. [Symphony specification](https://raw.githubusercontent.com/openai/symphony/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md), [GitHub merge queue documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).

The sources do not report a shared dependency protocol.

## Why it works

Separate decisions attach evidence to the object under judgment. Symphony checks whether an issue can run; GitHub checks a proposed combination before merging. Keeping those decisions explicit prevents execution success from substituting for integration evidence. This is a design inference from [Symphony](https://raw.githubusercontent.com/openai/symphony/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md) and [GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue), not a measured productivity gain. GitHub's guarantee covers configured required checks; omitted semantic interactions remain outside that evidence.

## When this backfires

A dedicated integrator can become a bottleneck. Cursor removed that role after it created more bottlenecks than it solved; workers handled conflicts themselves. The account also reports unresolved coordination problems. It supports optional ownership arrangements, without establishing permission to bypass repository checks. [Wilson Lin, Cursor, January 14, 2026](https://cursor.com/blog/scaling-agents).

For low-volume work, consider a sequential execute, review, check, and merge process. Keep the decisions explicit without adding separate queue services. The cited sources establish no minimum worker count or mandatory service split. The synthesis remains emerging. A draft specification and separate implementation accounts support its components; independent replication of the combined practice remains absent from this evidence.

## Example

Cursor's Solid-to-React migration passed CI and early checks while careful review remained outstanding. That report illustrates why passing checks and completing acceptance deserve separate records. It does not establish that the migration used Symphony or GitHub's merge queue. [Cursor's experimental account](https://cursor.com/blog/scaling-agents).

## Scope boundaries

Use [evidence-bundled agent PRs](../verification/evidence-bundled-agent-prs.md) for review evidence and [verification capacity saturation](../verification/verification-capacity-saturation.md) for review capacity. Scheduler mechanics belong in the [Symphony specification guide](../standards/symphony-orchestration-spec.md). Execution concurrency belongs in [lane-based queueing](../patterns/agent-design/lane-based-execution-queueing.md) and [bounded batch dispatch](../patterns/multi-agent/bounded-batch-dispatch.md).

This pattern leaves queue setup, retry protocols, and release permission outside its scope. Use the [Factory Engineering index](index.md) for the broader delivery process.

## Key Takeaways

- Name the event that releases dependent work. If a task needs a prerequisite on the target branch, use integration as that event. This is a design deduction.
- Assign an owner for integration decisions and conflict resolution; a dedicated agent is optional.

## Related

- [Factory Engineering Across Software Delivery Systems](factory-engineering.md)
- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md) — organize the work that produces a candidate PR
- [Single-Branch Git Agent Swarms](../workflows/single-branch-git-agent-swarms.md) — choose a branch topology
- [Merge-Rate Infrastructure Readiness](../workflows/merge-rate-infrastructure-readiness.md) — examine infrastructure capacity
- [Ecosystem-Level Integration Friction Governance](../code-review/ecosystem-level-integration-friction-governance.md) — define repository governance
