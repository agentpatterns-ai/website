---
title: "Full Sandbox Snapshots Beat Retry Only for Untracked State"
term: "Snapshot Branching Boundary"
description: "Snapshot-and-branch recovery lost to plain retry 17/25 vs 6/25 at a matched token budget, and won only on a task gated by a database outside version control."
aliases:
  - snapshot search payoff condition
  - when full sandbox snapshots help
  - out-of-repository state test
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-12
maturity: emerging
---

# Full Sandbox Snapshots Beat Retry Only for Untracked State

> Under a matched token budget, snapshot branching lost to plain retry everywhere except one task gated by a database version control never tracked.

Snapshot branching restores a coding agent's whole sandbox from a mid-run checkpoint and starts a fresh agent there, instead of retrying from the original repository. It earns its cost on one condition: the progress worth keeping has to include state a diff cannot reconstruct. A preprint from Daytona and the University of Waterloo built Go-Explore-style search over full sandbox snapshots and measured both sides of that condition. Their finding: "higher and more efficient solve rates depend mainly on progress that sits outside the repository, such as databases, services, and other runtime state" ([Graviet and Shah, arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).

## The default is plain retry

At the same token budget, snapshot branching lost widely. Across five pre-registered Terminal-Bench 2.0 tasks, five seeds each, one million tokens per seed, "retry solves 17/25 tasks while snapshot-based search solves 6/25" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)). Retry spent that budget on three fresh attempts; snapshot search spent it on one root run plus up to two children restored from it.

One task shows why. On `extract-elf`, "children restored from a Git diff or from replayed commands succeeded on 4/4 seeds", while full-snapshot children frequently ran out of budget. The authors read that as a fact about the task: "most useful progress is already captured in the repository, so restoring the entire machine adds little" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).

The restores themselves worked. A follow-up experiment measured how often branching rescued a run that had already failed. On `extract-elf`, "snapshot branching successfully recovered 67% of failed roots, substantially higher than independent retry's overall success rate of 38% on that task". On `regex-log` the same rate was 13%. Useful midpoints existed; they were too rare to pay for themselves, and "those midpoints were not frequent enough for branching to win" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).

## Where the result inverts

The authors then built a task whose progress cannot come back from a patch. `staged-service-repair` needs a SQLite database the verifier reads, a shape they call common in production: "agents modify system state such as databases, caches, and services that version control systems never track". Three starting points, all with the same 200,000 remaining tokens ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)):

| Restored from | Seeds solved |
|---|---|
| Clean restart, no prior progress | 0/5 |
| Git diff applied, database absent | 0/5 |
| Full snapshot, code and database | 4/5 |

Token cost moved too: "Restoring the full machine state cuts the required inference nearly in half. Snapshot restorations solved the task with just 21k–41k tokens, while clean restarts and Git-diff starts consumed significantly more tokens and still failed" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).

So there is a test to run before building any of this. Ask whether a diff plus a replay of your setup commands reconstructs what the agent had achieved when it failed. If it does, this measurement says put the budget into a fresh attempt instead.

## Why it works

The restore step comes from Go-Explore, which blames failed exploration on two defects. Algorithms forget how to reach states they already visited, and they explore from a state without first returning to it. Go-Explore "addresses these two challenges directly through the simple principles of explicitly remembering promising states and first returning to such states before intentionally exploring" ([Ecoffet et al., arXiv:2004.12919v6](https://arxiv.org/abs/2004.12919v6)). A full sandbox snapshot makes that return exact for a coding agent: the restored machine is the earlier state, so nothing has to be re-derived.

That also explains the condition. For anything version control tracks, a diff already returns the agent to the earlier state, so the snapshot's extra fidelity costs budget and buys nothing. It buys the result only for state version control never recorded.

## Meeting the condition is not sufficient

Snapshots solve the easier of two problems: "Snapshotting solves the state-restoration problem, but it does not solve the state-selection problem. Effective environment-level search requires both" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)). Intelligent Go-Explore describes the original algorithm as needing hand-built heuristics to "determine which states to save and explore from" ([Lu et al., arXiv:2405.15143v4](https://arxiv.org/abs/2405.15143v4)). The one failure on the database task shows the cost: the snapshot restored correctly and the database was present, yet the agent marked the task complete without applying the remaining migration. "A new agent in a restored machine still has to notice what work remains" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).

## When this backfires

- The root run is not free. "Snapshot search instead spends part of its budget producing the root and divides the remainder among children" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)). A retry gets a whole attempt; a child gets a slice of one.
- Restoration is faithful to mistakes as well as progress, and the child edits around a bad decision rather than revisiting it: "Faithful restoration can therefore make an incorrect state unusually sticky" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).
- The child inherits the machine, not the parent's understanding of it. In one inspected trajectory "a child consumed roughly 190,000 tokens over 26 steps" against about 90,000 tokens over 11 steps for a successful fresh retry ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).
- Snapshotting every turn wastes most of the work. A separate checkpoint runtime reports that "over 75% of agent turns produce no recovery-relevant state, so most checkpoints are unnecessary", and calls full per-turn checkpointing "too expensive under dense co-location" ([Wu et al., arXiv:2604.28138v1](https://arxiv.org/abs/2604.28138v1)).
- A seed script or migration that rebuilds the database moves the progress back inside version control, removing the condition instead of paying for an archive. The paper concedes the general form of that argument to [Agentless](agentless-vs-autonomous.md): "More machinery is only worthwhile when it preserves something that matters" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)).
- The evidence is thin enough to test rather than adopt. One preprint, "Not peer reviewed and not published", one model tier (Claude Haiku 4.5), five tasks that "were selected for intermediate baseline difficulty rather than sampled randomly", and a benchmark the authors themselves call "largely file-centric" ([arXiv:2610.13841v1](https://arxiv.org/abs/2610.13841v1)). The task that produced the positive result was built by the authors for that purpose.

## Key Takeaways

- Run the diff test before building snapshot recovery. On the task where the authors compared the two restore methods head to head, a diff plus replayed setup commands went 4/4 and full snapshots lost.
- The positive case is narrow and large. On a task gated by a database outside version control, full snapshots went 4/5 where a patch went 0/5, at roughly half the inference.
- Meeting the condition buys restoration, not judgment. Choosing which checkpoint to return to is unsolved, and the paper's one snapshot failure was an agent not noticing the work left.
- Count the root run against your budget. Snapshot search funds the root and its children from the same tokens a retry would spend on complete attempts.
- Consider removing the condition instead of paying for it. Making the database or service rebuildable from version control is the cheaper answer when it is available.

## Related

- [Sandbox Forking: Branch Agent Runs From a Warm Snapshot](sandbox-forking.md) — the other use of a snapshot, amortizing setup across parallel runs rather than recovering mid-run progress.
- [Selective Checkpoint Restore Across Code and Conversation State](selective-checkpoint-restore.md) — which axis of state to roll back, once you have decided to checkpoint.
- [Task Shape Decides What a Heavier Agent Harness Buys](task-shape-harness-payoff.md) — the same conditional in another form, where task shape rather than model strength decides whether added machinery pays.
- [Delta Channels: Bounded Checkpoint Storage for Append-Only Agent State](delta-channels-checkpoint-storage.md) — the storage cost of keeping checkpoints once you are taking them.
- [Rollback-First Design](rollback-first-design.md) — why a reliable undo path can delay diagnosis of the bug that caused the failure.
