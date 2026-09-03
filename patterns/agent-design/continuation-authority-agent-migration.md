---
title: "Continuation Authority in Agent Migration"
term: "Continuation Authority"
description: "The right to act as a migrated agent is held by the deployment boundary, not by the checkpoint, so copying an agent's memory produces a replica rather than a successor."
tags:
  - agent-design
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - continuation authority
  - agent migration authority fence
  - single authoritative agent execution
last_reviewed: 2026-09-02
maturity: emerging
---

# Continuation Authority in Agent Migration

> Continuation authority is the right to act as a migrated agent, and copying that agent's memory does not transfer it.

Swapping an agent's model, harness, or host moves two things that need to move separately. State copies freely. The right to produce external effects on the agent's behalf should not, because a backup and an attacker can both copy state. Zhao and Zhao separate the two: memory is "evidence of history, not exclusive proof of continuation", because "a backup, fork, or attacker can copy it" ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)). Authority lives in the deployment boundary and is granted once per migration.

## When this applies

All three conditions below have to hold before the machinery earns its cost.

The agent has to outlive the swap. If the work unit is one task and the repository already holds the state, restarting is cheaper than migrating.

It also has to produce external effects: sending mail, filing issues, moving money, writing to shared storage. An agent that only reads and proposes cannot corrupt anything by running twice.

Last, the old execution has to still reach those effects. A process that is definitely dead needs no fence. The invariant exists for the case where the old one is unreachable rather than confirmed stopped.

## The invariant and the protocol

The governing rule is stated as invariant I4: "Within the governed deployment boundary, at most one cooperating execution can hold continuation authority and produce authoritative external effects for the migrated instance" ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)). Five companion invariants cover identity lineage, memory ancestry, body revision, visible capability deltas, and keeping runtime labels as metadata rather than identity.

Six phases carry the swap:

| Phase | What it does |
|---|---|
| Quiesce and fence | Halts new intake and increments the authority epoch so outdated executions reject tasks |
| Checkpoint | Records identity version, body revision, memory snapshots, workflow state, pending work, provider cursors |
| Validate | Verifies schemas, hashes, declared lineage, and target capability before touching the destination |
| Bind | Resolves target providers and credentials through the body's versioned contracts |
| Rehydrate | Installs private state atomically and creates fresh harness and interaction sessions |
| Verify and resume | Runs continuity checks, acquires a new authority epoch, reconciles ambiguous effects |

## Why it works

Duplicate external effects come from two executions each believing it is the live one. The protocol removes that belief by making authority a monotonic epoch instead of a property of state. Quiesce increments the epoch so stale executions reject work, and resume acquires a new epoch only after verification passes ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)). Because the epoch is held by the boundary and never embedded in the checkpoint, a copied checkpoint "may be a useful replica or descendant, but it must not silently inherit unique authority". The paper names that first phase "quiesce and fence". The epoch behaves like a fencing token in distributed locking, a monotonic number the resource checks, applied here to an agent's right to act rather than to a write.

## When this backfires

- Session-scoped agents. The control plane has nothing to control when the repository is already the source of truth.
- Read-only agents. Two concurrent proposers are a duplicate-work problem, not a correctness one.
- Teams reading the fence as a security control. It is cooperative. The paper states it cannot stop "a detached or malicious copy retaining unrevoked credentials from producing effects outside that boundary" ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)).
- Old, memory-heavy agents. Preserving lineage preserves accumulated defects. Al-Tawaha and colleagues find "memory-induced violation rates show a robust upward trend with exposure length", driven primarily by accumulated content rather than encounter order ([arXiv:2605.17830v1](https://arxiv.org/abs/2605.17830v1)). A clean rebuild resets that; a faithful migration does not.
- Anyone expecting the successor to behave the same. Mechanical continuity is the whole claim. The reference system passes 833 core tests and 92 provider and library tests. That evidence supports "architectural substitutability, failure handling, and individual-axis feasibility, but not equal task performance, behavioral fidelity, latency, cost, or controlled combined migration" ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)).

The evidence base is one young open-source lineage with no controlled all-axis migration matrix, so treat the invariants as a design checklist rather than a validated result.

## Example

A support agent runs on model version N, writes to a ticketing API, and is being moved to version N+1 on a new host.

Copy-and-start, which looks like a migration and is not:

```text
1. snapshot memory + workflow state from host A
2. restore onto host B, start agent on model N+1
3. host A is "probably" drained
-> both executions hold live ticketing credentials
-> a retried in-flight task posts the same customer reply twice
```

Fenced migration:

```text
1. quiesce host A: stop intake, bump authority epoch 7 -> 8
   (host A's writes now carry epoch 7 and are rejected)
2. checkpoint identity version, body revision, memory, pending work
3. validate hashes and lineage against host B's capability set
4. bind host B to the ticketing provider through the body contract
5. rehydrate state atomically, open a fresh session on model N+1
6. verify, claim epoch 8, reconcile the in-flight task's uncertain effect
```

The structural difference is step 1. The epoch bump happens before any state moves, so there is no window in which two executions both hold a valid claim ([arXiv:2609.00546v1](https://arxiv.org/abs/2609.00546v1)). Step 6 still needs the ticketing write to be [idempotent](idempotent-agent-operations.md), because the fence bounds who may act and not whether an accepted effect landed once.

## Key Takeaways

- Authority is a property of the deployment boundary, not of the checkpoint; design it as a monotonic epoch the destination acquires and the source loses
- Bump the epoch before the state moves, so a partially drained source cannot double-write during the copy
- The fence is cooperative and bounded by the governed deployment, so revoking credentials remains a separate job
- Preserving memory lineage preserves its accumulated defects, which pulls against a clean rebuild on an old agent
- The published evidence covers mechanical substitutability on one system, so do not promise stakeholders that the migrated agent behaves the same

## Related

- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the checkpointing and resumability layer this protocol sits on
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — splits state layers inside one deployment, where this page governs the swap between deployments
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — what makes step 6's reconciliation of ambiguous effects survivable
- [Portable Agent Definitions: Full-Stack Identity as Code](../../standards/portable-agent-definitions.md) — packaging the identity half as a version-controlled artifact
- [The Handoff Tax: What a Receiving Model Should Inherit](../../context-engineering/handoff-tax-model-switch-context.md) — the behavioral cost a mechanically clean model swap still pays
