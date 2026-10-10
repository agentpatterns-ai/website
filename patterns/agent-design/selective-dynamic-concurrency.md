---
title: "Selective Dynamic Concurrency for Long-Horizon Coding Agents"
term: "Selective Dynamic Concurrency"
description: "Enable runtime sub-agent concurrency per task, not by default: a controlled study of three coding agents shows token cost up 1.41x to 3.31x and mixed success."
tags:
  - agent-design
  - tool-agnostic
  - multi-agent
aliases:
  - dynamic concurrency policy
  - selective sub-agent concurrency
  - concurrency opt-in for coding agents
last_reviewed: 2026-10-09
maturity: emerging
---

# Selective Dynamic Concurrency for Long-Horizon Coding Agents

> Let a coding agent spawn parallel sub-agents only when the task splits into components it can own, compare, or check independently.

Dynamic concurrency lets an agent decide during a run whether to spawn parallel sub-agents. The policy pays off when the task has independently ownable components, when alternative attempts are cheap to compare, or when an independent sub-agent can validate the main agent's work. It costs tokens, time, and sometimes accuracy on bounded tasks. Treat it as a per-task opt-in, not a default setting. The evidence comes from one controlled study of three agents, so test the conditions below on your own tasks ([Li et al.](https://arxiv.org/abs/2610.10263v1)).

## When to turn it on

The study examined 131 paired trajectories where concurrency won. It found three ways the main agent turned parallel output into progress: "sub-agents can complete complementary work, explore alternative solutions, or independently validate and correct the main agent's implementation" ([Li et al.](https://arxiv.org/abs/2610.10263v1)).

| Condition | What to check before fan-out |
|-----------|------------------------------|
| Complementary components | Each component has one named owner and a shared interface contract |
| Alternative attempts | You can compare the results cheaply, for example by running one test suite against each |
| Independent validation | The validator reads the main agent's output and does not share its assumptions |

The authors say concurrency "should be enabled selectively rather than by default" and is "more promising for difficult, long-horizon tasks" ([Li et al.](https://arxiv.org/abs/2610.10263v1)). Long-horizon alone does not predict a gain. On RepoZero, a long-horizon benchmark, Claude Code fell from 42.7% to 26.7% task pass under concurrency. The authors report only an association between larger expected implementation size and a larger gain, across four benchmarks.

## What it costs

The study ran 2,124 runs of Codex, Claude Code, and Kimi Code with concurrency on and off. Task success moved between an 11.9 point drop and a 2.3 point gain, while mean token use reached 1.41 to 3.31 times the sequential level ([Li et al.](https://arxiv.org/abs/2610.10263v1)).

- Tokens per solved task rose for all three agents. Codex went from 7.69 million to 24.12 million.
- Mean runtime rose for all three agents, and in 14 of 15 agent-benchmark combinations.
- Of 366 cases solved in both modes, concurrency finished at least 20% faster in only 46 (12.6%).
- On SWE-bench Verified, a bounded benchmark, Claude Code dropped from 83.0 to 59.0 task pass and took 27.8 minutes instead of 17.5.

## Failure modes and guards

The authors coded 804 failure instances across 650 concurrent trajectories into 28 patterns. Shared state and merge problems were the largest group, at 33.2% of instances ([Li et al.](https://arxiv.org/abs/2610.10263v1)). Each pattern suggests a guard you can set before fan-out.

| Failure pattern | Share of instances | Guard |
|-----------------|--------------------|-------|
| Concurrent writes to one workspace | 26.5%; 62.9% of Codex's | Give each sub-agent its own worktree or output directory |
| Fan-out budget exhaustion | 19.2% | Cap the sub-agent count against the task budget |
| Load imbalance | 20.6%; 39.8% of Claude Code's | Split work into similar-size parts before spawning |
| Early sub-agent termination | 15.9% | Derive the join deadline from the task budget |
| Deliverable overwrite | 14.9% | Name one owner per deliverable |

The guards are my reading of each pattern. The paper does not test them.

## Example

The paper records a join-timing failure. In it, "the main agent assumes a two-hour sub-agent timeout despite a 40-minute task budget. The task deadline therefore arrives before the planned join, terminating sub-agents with required work unfinished." A join deadline computed from the remaining task budget removes this case ([Li et al.](https://arxiv.org/abs/2610.10263v1)).

## Why it works

Concurrency pays when the main agent converts parallel output into progress on the critical path. Coordination has a fixed cost that bounded tasks cannot repay. Anthropic states the same limit: "most coding tasks involve fewer truly parallelizable tasks than research" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Cognition narrows working setups to those where "writes stay single-threaded and the additional agents contribute intelligence rather than actions" ([Cognition](https://cognition.com/blog/multi-agents-working)). A separate study of agent scaling found that all multi-agent variants degraded planning tasks by 39% to 70%, while decentralized coordination helped parallel web exploration by 9.2%, so task structure decides the result. Those tasks are not coding tasks, so the numbers show the mechanism and not a coding forecast ([agent-scaling study](https://arxiv.org/abs/2512.08296v3)).

## When this backfires

- Bounded single-issue fixes. Claude Code lost 24 points on SWE-bench Verified, and the pooled declines for Claude Code and Kimi Code are significant ([Li et al.](https://arxiv.org/abs/2610.10263v1)).
- Tasks dominated by one critical-path component. The other sub-agents wait, and the paper lists Pseudo-Concurrency and Critical-Path Starvation among its patterns.
- Tight fixed budgets. Budget-driven patterns make up about a third of failure instances. The paper tests no looser budget, so part of the measured loss may come from the time cap and not from concurrency.
- Parallel-by-nature work can justify default-on concurrency. Anthropic's lead-and-sub-agent system beat a single agent by 90.2% on its internal breadth-first research eval ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

The opposing view has merit: the study used July 2026 scaffolds, and many failure patterns look fixable in the harness.

## Limits of the evidence

- The sequential baseline in Claude Code disabled the Workflow, Task, and Agent tools. The study does not separate dynamic workflows from plain sub-agent delegation, so it gives no reason to drop the latter.
- Each cell has one run. LoopsBench has 28 tasks, so Claude Code's 14.3 point gain there equals 4 tasks.
- The authors scope their findings "to the tested agents and benchmarks" ([Li et al.](https://arxiv.org/abs/2610.10263v1)).

## Key Takeaways

- Enable concurrency per task. Default-on cost 1.41x to 3.31x the tokens and slowed runs in 14 of 15 agent-benchmark cells.
- Before fan-out, check for independent owners, cheap comparison of alternatives, or an independent validator.
- Isolate each sub-agent's writes, tie join deadlines to the task budget, and name one owner per deliverable.
- Skip it for bounded fixes: Claude Code lost 24 points on SWE-bench Verified.
- Long-horizon work is no guarantee: Claude Code lost 16 points on RepoZero.

## Related

- [Delegation Threshold Calibration for Orchestrator Agents](delegation-threshold-calibration.md)
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md)
- [Sub-Agents Fan-Out](../multi-agent/sub-agents-fan-out.md)
- [Model Economics of Agent Swarms](../multi-agent/model-economics-agent-swarms.md)
- [Pre-Write Change Intent Admission](../multi-agent/pre-write-change-intent-admission.md)
