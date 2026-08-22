---
title: "Coordination Channel Policy for Multi-Agent Coding"
term: "Coordination Channel Policy"
description: "Task shape decides whether a coding-agent team should coordinate through a shared file or peer messages; the same mandate that cuts 42% of output tokens on specification work adds 10% on pipeline work."
aliases:
  - agent coordination channel policy
  - shared-file versus peer-messaging policy
tags:
  - multi-agent
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-19
maturity: emerging
---

# Coordination Channel Policy for Multi-Agent Coding

> For teams of four or more coding agents, task shape decides the coordination channel: a shared file, or peer messages.

Mandating a shared file for eight coding agents cuts output tokens by about 42% when the work is built around one specification, and raises them by about 10% when it is a pipeline ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)). Same rule, opposite sign. Classify the task before setting the policy.

## When this decision applies

Conditions matter more than the headline:

- Four agents or more. At two agents the mean sustained degree is 0.90 on both task shapes, so there is no repeated messaging to collapse. Every measured effect appears at four and eight agents ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).
- Cost is the binding constraint. The file-policy experiment measures output tokens. It reports nothing about whether the team's code passed more tests.
- Peer messaging already exists. Without it, files are the only channel and there is no policy to set.

## The fan-out test

Count the readers of each fact the team produces. Many consumers per fact means mandate the file; one consumer means leave the policy permissive.

Specification-sharing work has high fan-out: every agent needs the same interface decisions. It builds a dense mesh: mean sustained degree of 5.47 against a possible 7 at eight agents, with a clustering coefficient of 0.81. Pipeline work stays sparse at 2.99 degree and 0.38 clustering ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).

## Why it works

A message reaches one recipient. A file is written once and read by any number of agents, so the saving scales with how many agents need the same fact. On specification work, peer messaging repeats the spec once per pair, and the file collapses that repetition into a single write. On pipeline work each step's output already has exactly one consumer downstream, and the code file carrying it exists anyway, so a second written channel adds turns without removing repetition ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)). Anthropic reports the same causal story from production, describing persistent artifacts as a way to avoid "token overhead from copying large outputs through conversation history" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## The messaging curve is an introduction phase

Direct messaging grows close to quadratically between two and eight agents; on the pipeline task the exponent is 1.92. Most of that is one round of introductions. On specification work, 90% of the distinct sender-to-recipient pairs a run will ever use appear within the first 20% of run time at every team size, in one of the two collection sessions. Sustained peer traffic barely grows after that. On the sixteen-step chain, mean messages per run are 21.4, 47.0 and 46.8 at four, eight and sixteen agents, and the slope between eight and sixteen is 0.00 (95% CI [−0.34, 0.34]). Teams change channel instead of talking more: across that step named-peer messages drop to 12.2 per run from 34.6, while broadcasts climb to 34.0 from 12.3 ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).

## Naming a coordinator buys nothing

Filtering each run's message graph to the channels carrying a disproportionate share of traffic leaves 0 of 1,170 channels at eight agents on specification work, and 2 of 1,077 on pipeline work. In a sealed replication the flat and coordinator teams are level on success (p=0.75 under the mandatory file policy, p=0.53 under the permissive one) ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)). A role named in a prompt does not become a hub in the traffic. That is a claim about labels rather than orchestration: a lead agent holding dispatch control and synthesizing results is a different mechanism ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)), covered in [Orchestrator-Worker](orchestrator-worker.md).

## When this backfires

- Correctness binds instead of cost. On a long-horizon planning task a shared notebook cut hallucinated-detail errors by 18%, and an orchestrator cut errors by up to a further 13.5% within focused sub-areas ([arXiv:2508.12981v1](https://arxiv.org/abs/2508.12981v1)). Where hallucinated detail fails your runs, mandate the artifact whatever the shape.
- The job mixes shapes. Work with both a shared spec and a sequential handoff pays the pipeline penalty on one half while collecting the specification saving on the other. The two shapes were measured only in isolation.
- Several agents write the same file. The mechanism assumes write-once-read-many, and concurrent writers turn the channel into a contention point. That is the problem [Worktree Isolation](../../workflows/worktree-isolation.md) and [File-Based Agent Coordination](file-based-agent-coordination.md) address.
- Your stack differs. All 1,902 graded runs use Claude Code 2.1.x with the model pinned to `claude-sonnet-4-6`, on two synthetic Python tasks graded by fixed test suites ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).
- The team is small. Below four agents the effect was not measured, and the mechanism predicts no gain.

## Example

Two eight-agent teams, each writing one Python module.

The first splits a single function's specification four ways: signature, validation, discount, sort order. Every agent needs the others' interface decisions, so fan-out is high. Mandating a shared file here cut output tokens by 36% to 49% across collection sessions ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).

The second runs a four-step pipeline: parse, validate, aggregate, format. Each step's output feeds exactly one downstream step, and the code file already carries it. The same mandate raised output tokens by about 10% ([arXiv:2608.16801v1](https://arxiv.org/abs/2608.16801v1)).

## Key Takeaways

- Classify work by fan-out before setting a channel policy. Many readers per fact favors a mandated shared file; one reader per fact does not.
- The two outcomes are asymmetric: roughly 36% to 49% fewer output tokens when the call is right on specification work, against 10% to 17% more when it is wrong on pipeline work.
- Treat the result as a cost lever only. Nothing in it says a shared file makes the team's code more correct.
- Quadratic-looking message growth is a one-time introduction round, and total messaging plateaus by sixteen agents as teams switch to broadcast.
- Calling one agent the coordinator in its prompt produces no traffic hub and no measured success gain. Give it dispatch control if you want it to lead.

## Related

- [Cohesion-Aware Task Partitioning for Multi-Agent Coding](cohesion-aware-task-partitioning.md) — the upstream decision about whether to fan out at all
- [The Model Economics of Agent Swarms](model-economics-agent-swarms.md) — how swarm width is priced once decomposability clears
- [File-Based Agent Coordination](file-based-agent-coordination.md) — files as an exclusivity mechanism rather than a communication channel
- [Persistent Shared Search Sub-Agent for Output-Token Reuse](persistent-search-subagent.md) — the same write-once-read-many saving applied to repository lookups
- [Multi-Agent Topology Taxonomy: Centralized, Decentralized, and Hybrid](multi-agent-topology-taxonomy.md) — the coarser topology choice this policy sits inside
