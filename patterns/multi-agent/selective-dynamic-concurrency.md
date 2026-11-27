---
title: "Selective Dynamic Concurrency for Long-Horizon Coding Agents"
term: "Selective Dynamic Concurrency"
description: "Enable sub-agent concurrency per task: one study found 1.41x to 3.31x the tokens and mixed success, another small gains on random repository builds."
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

Dynamic concurrency lets an agent decide during a run whether to spawn parallel sub-agents. The policy pays off when the task has independently ownable components, when alternative attempts are cheap to compare, or when an independent sub-agent can validate the main agent's work. It costs tokens, time, and sometimes accuracy on bounded tasks. Treat it as a per-task opt-in, not a default setting. The conditions below come from one controlled study of three agents, so test them on your own tasks ([Li et al.](https://arxiv.org/abs/2610.10263v1)). A second study covers one task type, [building a whole repository](#building-a-whole-repository).

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

## Building a whole repository

[Lyu et al.](https://arxiv.org/abs/2611.33893v1) compared one Codex agent with a main agent allowed, but not told, to run up to 20 subagents at once. Tasks build a program or library against hidden tests, from a written specification (NL2Repo) or with an executable of the original to compare against (ProgramBench). Runs ended when the agent declared the task done, within 4 hours (Codex 0.147, `xhigh` reasoning).

On 30 random tasks per benchmark ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)):

- Subagents on the main agent's model added about 1 to 5 points of hidden tests passed, at 2.6 to 3.8 times the cost. GPT-5.6 Sol ran both benchmarks, and GPT-6 Sol and GPT-6.1 Sol ran ProgramBench.
- Those runs did not take longer, except with GPT-6 Sol. At equal cost, the single agent scored the same or higher.
- Cheaper GPT-5.6 Luna subagents, at their default reasoning level under a Sol main agent, ended below the single agent on both benchmarks, at a higher cost.
- Two runs of one setup on a task differed by about 7 points on average, more than the average gap (GPT-5.6 Sol, ProgramBench).
- On ProgramBench, the median gain was larger on hard tasks in all three models: 2.0 against 1.7 points on the rest with GPT-5.6 Sol, and 8.4 against 1.0 with GPT-6.1 Sol. NL2Repo showed no such pattern.

In a smaller replication with Opus 5.5 on Claude Code 2.1.283, one run each, subagents added 4.7 points at 3.1 times the cost on ten ProgramBench tasks. They did not raise the average on ten NL2Repo tasks ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

## Where the gain comes from

Lyu et al. report evidence for three mechanisms behind the hard-task gain: more checking, fresh context, and modular code. They tested the first two on a single agent and only observed the third ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

For checking, they gave a single agent this instruction ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)):

> "Before implementing, probe the reference executable across its whole public interface: list its commands, options and input formats, run each against the reference, and record the exact outputs and exit codes. Then implement, and check every recorded behaviour before you finish."

On 16 hard ProgramBench tasks with GPT-5.6 Sol, it raised the mean score by 6.7 points, against 8.8 for subagents. At list price it cost 50% more than the plain agent, and subagents cost 275% more. The medians are further apart, 1.3 points against 4.9, and the instructed agent has scores for only 15 tasks ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)). The result did not carry over everywhere ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)):

- With GPT-6 Sol and GPT-6.1 Sol, the instructed agent stayed close to the plain one, while subagents still added 6.0 and 2.8 points on average.
- Under DeepSeek's dsh harness, with GPT-5.6 Sol, it did not help on four hard tasks (one run each).
- NL2Repo has no reference program. There, GPT-5.6 Sol told to check every specification example scored below the plain agent on all four hard tasks tried.

Fresh context and modular code were studied in long runs on three hard tasks with GPT-5.6 Sol and GPT-6.1 Sol. Agents were told to continue past each stop until a time budget ran out (Codex 0.154, `high` reasoning). The multi-agent setup was also told to use subagents aggressively, one module each. It was ahead at equal time and overtook the single agent late at equal cost, unless an edit broke coupled code. With GPT-5.6 Sol, it led clearly on one task (84.0 against 75.2 at $260), barely on another, and trailed on the third ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

Claude Code with Opus 5.5, given no such parallelism instruction, differed. A 4-hour multi-agent run ended above an 8-hour single-agent run on both tasks tried (one run each), at about twice the cost. In six shorter pairs, though, a single agent given twice the time caught up on average ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

For fresh context, the authors took a single agent's code after 8 to 12 hours, when its score was rising slowly. They compared resuming that session, with automatic compaction, against a chain of new sessions that each started empty and ran 3 hours. With GPT-5.6 Sol and GPT-6.1 Sol, the chain led over the first hour in all six comparisons, by only 0.3 to 0.7 points with GPT-5.6 Sol. It ended clearly higher in one, and the other five ended close. A new multi-agent session from the same code gained sooner than the chain, but not more at equal cost. Only Codex was tested ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

For modular code, the evidence is observational. Multi-agent code had more files and shorter functions. At equal cost, the multi-agent setup ended clearly ahead with both models on one task only, where the single agent kept nearly all its code in one file. That comparison has one run per setup, and another one-file case, with GPT-5.6 Sol, ended about even. Multi-agent runs also broke code more often and more severely: 2 of 30 long runs ended with a program that did not build, against none of 38 single-agent runs. The authors advise re-checking after integration with new inputs, not stored ones ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

## Limits of the evidence

- Li et al.'s sequential baseline in Claude Code disabled the Workflow, Task, and Agent tools. The study does not separate dynamic workflows from plain sub-agent delegation, so it gives no reason to drop the latter.
- Each Li et al. cell has one run. LoopsBench has 28 tasks, so Claude Code's 14.3 point gain there equals 4 tasks.
- Li et al. scope their findings "to the tested agents and benchmarks" ([Li et al.](https://arxiv.org/abs/2610.10263v1)).
- Most Lyu et al. comparisons rest on one to three runs per setup, on closed models and whole-program tasks. The probe instruction needs a reference program, "which most projects lack" ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).
- Results on task difficulty are not settled. Lyu et al. note that concurrent work by Samway et al., with its own agent team, found the largest gains on easy tasks ([Lyu et al.](https://arxiv.org/abs/2611.33893v1)).

## Key Takeaways

- Enable concurrency per task. In Li et al., default-on cost 1.41x to 3.31x the tokens and slowed runs in 14 of 15 agent-benchmark cells.
- Before fan-out, check for independent owners, cheap comparison of alternatives, or an independent validator.
- Isolate each sub-agent's writes, tie join deadlines to the task budget, and name one owner per deliverable.
- Skip it for bounded fixes: Claude Code lost 24 points on SWE-bench Verified.
- Long-horizon work is no guarantee: Claude Code lost 16 points on RepoZero.
- Repeat runs before you credit subagents. On Lyu et al.'s random ProgramBench tasks with GPT-5.6 Sol, rerun noise exceeded the average gain.
- If you have a reference program, test the probe instruction before paying for subagents. It raised GPT-5.6 Sol's mean score on Codex, but did little under dsh or with later GPT Sol models.
- When a long single session slows, try a new one. In Lyu et al.'s Codex runs, it started faster but rarely finished clearly higher.

## Related

- [Delegation Threshold Calibration for Orchestrator Agents](../agent-design/delegation-threshold-calibration.md)
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](../agent-design/delegation-decision.md)
- [Sub-Agents Fan-Out](sub-agents-fan-out.md)
- [Model Economics of Agent Swarms](model-economics-agent-swarms.md)
- [Pre-Write Change Intent Admission](pre-write-change-intent-admission.md)
- [Cohesion-Aware Task Partitioning](cohesion-aware-task-partitioning.md)
- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md)
