---
title: "Concurrent Agent Pull Requests and Merge-Conflict Cost"
description: "When multiple coding agents work one repo, co-active overlapping pull requests are the norm — budget for the merge-conflict cost and coordinate dispatch instead of assuming it away."
term: "Concurrent Agent Pull Requests"
tags:
  - workflows
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-07-07
maturity: emerging
---

# Concurrent Agent Pull Requests and Merge-Conflict Cost

> Fanning out multiple agents on one repo makes concurrent, overlapping pull requests the norm — plan for the merge-conflict cost before dispatching them in parallel.

## When the cost is real

The merge-conflict cost of parallel agents is not universal. It scales with three conditions:

- Agent volume: repos running 2+ agents at once. Below that, coordination machinery is overhead.
- File overlap: agents scoped to the same directories or modules collide; agents partitioned onto disjoint file ownership rarely do, even running concurrently.
- Vendor mix: 2+ agent products in the same repo. Cross-vendor pairs conflict at roughly 2x the rate of same-agent pairs (see the [measured conflict cost](#the-measured-conflict-cost) below).

If your setup meets none of these, run agents in parallel and resolve the occasional conflict at merge. If it meets one or more, the coordination ladder below pays for itself.

## Why concurrency is the default, not the exception

Concurrent agent pull requests are not an edge case you can dispatch your way around. A study of the AIDev-pop dataset — 33,596 agent-authored PRs across 2,807 repositories, December 2024 to July 2025 — measured how often agent PRs overlap in time ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)).

Under exact temporal overlap, 40.2% of repositories have co-active agent-authored PR pairs, and those co-active pairs account for 79.4% of all agent-submitted PRs ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). Widen the window to one week and 53.4% of repositories show co-activity, covering 95.0% of agent PRs ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). Once you run more than one agent, most of their work happens while another agent is also mid-change.

## The measured conflict cost

Co-activity produces textual merge conflicts at rates worth budgeting for:

| Pair type | Textual conflict rate | 95% CI |
|---|---|---|
| Intra-agent (same agent) | 19.8% | [16.8%, 23.2%] |
| Cross-agent (different vendors) | 41.7% | [33.1%, 50.9%] |

Cross-agent pairs conflict at roughly double the rate of same-agent pairs ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). The conflicts land where they hurt: 84.4% of conflicted files are source code and only 3.9% are manifest or lockfiles, so a human reviews the resolution rather than a tool auto-merging it ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). About 42% of conflicts are structural — modify/delete (26.8%) or add/add (15.1%) — not simple overlapping-line merges, and structural conflicts cost more to resolve than content conflicts (57.6%) ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)).

These are textual conflicts only, which the authors call conservative lower bounds — build and semantic conflicts were not measured, so the true friction is higher ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)).

## Why it works

Agents collide because they carry no shared-workspace awareness. Each one "operate[s] independently and in isolation, without knowledge that other agents of the same type are simultaneously accessing and altering the same files" — there is no lock or communication protocol preventing two agents from editing the same code region at once ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). Cross-vendor pairs conflict at double the rate because different products apply different formatting, structure, and conventions, which widens the edit overlap whenever they touch the same file ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)). Coordination works by restoring the awareness the agents lack — either by keeping their edit regions apart, or by making one agent's change land before the next one starts.

## The coordination ladder

Match the response to how many of the three conditions your repo meets. Each rung costs more than the one above it; stop at the first rung that removes your overlap.

1. Measure co-activity first. Count how often two agent PRs are open against the same repo at once. If it is rare, stop here — the cost does not justify coordination.
2. Partition by file ownership. Scope each agent to disjoint directories or modules so concurrent work produces no textual overlap. This preserves full parallelism and is the cheapest structural fix. [Sparse-checkout worktrees](../tools/claude/sparse-paths-monorepo-isolation.md) enforce the partition at the filesystem level.
3. Isolate and reserve. When agents must touch shared areas, run each on its own [worktree or branch](worktree-isolation.md) and add advisory reservations so agents avoid regions another agent has claimed, as in [single-branch git for agent swarms](single-branch-git-agent-swarms.md) and [labels as locks](labels-as-locks-pipeline.md).
4. Serialize the high-overlap cases. Reserve strict serialization — dispatch one agent, wait for merge, then dispatch the next — for the cases the cheaper rungs cannot separate: cross-vendor runs on the same files, or refactors that touch broad swaths of the codebase.

Serialization is the last rung, not the first, because it trades away the wall-clock throughput that made fan-out worth doing. It is the same delegation judgment covered in [the delegation decision](../agent-design/delegation-decision.md) — how much independent authority each agent should hold.

## When this backfires

Coordinating dispatch is itself a cost. It is the wrong default under these conditions:

- Low agent volume: a repo that rarely has two agents active at once gains nothing from coordination machinery and pays its overhead in full.
- Disjoint file ownership already in place: if agents are scoped to non-overlapping modules, temporal concurrency produces no overlap, and adding serialization only slows delivery.
- Fast merge cadence: short-lived branches and auto-merge shrink the overlap window, dropping co-activity without any coordination step.
- Single-vendor deployments: the high-cost 41.7% figure is cross-agent. A shop standardized on one agent sees the 19.8% rate, and cross-agent pairs are only about 0.5% of observed pairs today — partly an artifact of single-vendor data collection ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697)).

The failure mode is treating a ~20% same-agent conflict rate as a reason to serialize everything. Roughly four in five co-active same-agent pairs never conflict, and blanket serialization forfeits that parallel throughput to avoid a probabilistic, human-resolvable cost.

## Example

A team runs four Claude Code agents on one service repo. Before adding any coordination, they check co-activity: three of the four agents routinely have PRs open at the same time, and two are assigned overlapping modules. That meets the volume and file-overlap conditions, so they climb the ladder rather than serialize. They scope the two overlapping agents to disjoint directories with sparse-checkout worktrees (rung 2), leave the other two fully parallel, and add a branch reservation only for a shared `types/` directory both must edit (rung 3). No agent is serialized. Concurrency stays high; the textual-conflict surface drops to the single reserved directory.

## Key Takeaways

- Concurrent, overlapping agent PRs are the norm — 79.4% of agent PRs are co-active with another agent PR, so plan for it rather than assuming serial dispatch.
- Budget for the conflict cost: 19.8% of same-agent co-active pairs conflict textually, rising to 41.7% for cross-vendor pairs, mostly in source files a human must resolve.
- Climb a coordination ladder — measure, partition by file ownership, isolate and reserve, then serialize only the high-overlap or cross-vendor cases.
- Serialization is the last resort, not the default; blanket serialization forfeits the fan-out throughput that ~80% non-conflicting parallel pairs deliver.

## Related

- [Single-Branch Git for Agent Swarms](single-branch-git-agent-swarms.md) — advisory reservations and mechanical guards that keep parallel agents off each other's files
- [Parallel Agent Sessions Shift the Bottleneck](parallel-agent-sessions.md) — the workflow that produces the concurrency this page budgets for
- [Worktree Isolation](worktree-isolation.md) — the branch/worktree isolation that rung 3 builds on
- [Labels as Locks: Pipelined Backlog Processing](labels-as-locks-pipeline.md) — claim-label leasing to serialize only the contended work
- [Agent-Authored PR Integration](../code-review/agent-authored-pr-integration.md) — merge-success predictors on the same AIDev dataset, complementary to the conflict-cost view here
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md) — the human-attention cost of running the same parallel fleet
