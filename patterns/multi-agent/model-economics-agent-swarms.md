---
title: "The Model Economics of Agent Swarms: Cost and Width"
term: "Model Economics of Agent Swarms"
description: "How token cost, throughput, and the planner-worker model mix cap how wide a coding-agent swarm pays off — after task decomposability decides whether it helps at all."
tags:
  - multi-agent
  - tool-agnostic
  - cost-performance
aliases:
  - agent swarm economics
  - swarm cost and throughput
last_reviewed: 2026-07-21
maturity: emerging
---

# The Model Economics of Agent Swarms: Cost and Width

> A swarm's width is capped first by whether the task decomposes, then by the model mix that sets its cost — not by fan-out alone.

The model economics of an agent swarm decide how wide it pays to run and whether it pays at all: per-agent token cost, model throughput, and the planner-worker model mix set an economic ceiling on fan-out. But that ceiling only matters after a prior gate — task decomposability — has already decided whether more agents help. Treat swarm width as two sequential questions, not one topology choice.

## Gate one: decomposability decides if a swarm helps

Economics is the second question. The first is whether the task splits cleanly. A controlled Google Research study of 180 agent configurations found that multi-agent coordination improved a parallelizable task (financial reasoning) by 80.9% over a single agent, while every multi-agent variant degraded a strictly sequential planning task by 39 to 70% ([Google Research — Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/), [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)). No token budget or throughput rescues a task that does not decompose. Check decomposability before you price a swarm.

## Gate two: the model mix sets the ceiling

Once a task clears the first gate, cost is dominated by which model does which work — not by raw agent count. Building SQLite in Rust with a swarm, Cursor ran four model configurations that produced similar quality at costs that varied roughly eightfold: an Opus 4.8 planner paired with Composer 2.5 workers cost $1,339, versus $10,565 for GPT-5.5 as both planner and worker ([Cursor — Agent swarms and the new model economics](https://cursor.com/blog/agent-swarm-model-economics)). The worker fleet was the swing: cheap workers cost $411 against $9,373 for frontier workers at comparable quality ([Cursor](https://cursor.com/blog/agent-swarm-model-economics)).

Throughput then sets wall-clock convergence within that ceiling, but only where the task is valuable enough to pay for it. Anthropic reports multi-agent systems use about 15 times more tokens than a chat interaction, so "multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance" ([Anthropic — Building a multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Why it works

The cost asymmetry comes from where judgment is needed. In Cursor's run the planner "produced a small fraction of the tokens but roughly two-thirds of the cost," because "few moments in a large task genuinely require frontier intelligence, such as the original decomposition, the design decisions, and certain trade-offs. Once a frontier planner has collapsed the ambiguity into a detailed, explicit instruction, less expensive models simply have to follow it" ([Cursor](https://cursor.com/blog/agent-swarm-model-economics)). A planner never implements, so its context never fills with low-level detail, and a worker never plans, so it spends all its context on one narrow piece — which is why Cursor attributes the swarm's scalability to "context efficiency, more than from parallelism itself" ([Cursor](https://cursor.com/blog/agent-swarm-model-economics)). Swarm cost is therefore a model-mix decision: put frontier tokens only on the few high-judgment steps and buy width with cheap, high-throughput workers.

## When this backfires

- Sequential or tightly-coupled tasks: every multi-agent variant Google tested lost 39 to 70% on strict sequential reasoning, and cheaper or faster models do not recover it ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).
- Low-value tasks: at roughly 15 times the token cost of a chat, a swarm loses to a single agent whenever task value does not clear the bill ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).
- Tool-heavy agents: Google found a tool-coordination trade-off where the coordination tax grows disproportionately as agents gain more tools, eroding the per-agent economics ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).
- Communication-free swarms: independent agents that never check each other amplified errors 17.2x, against 4.4x for a centralized orchestrator, so cheap parallel workers without a validating stage generate rework that eats the savings ([Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).
- Ambiguous work handed to cheap workers: the cheap-worker economics hold only after a frontier planner collapses ambiguity. Without that, workers thrash — an early swarm run logged 68,000 commits and more than 70,000 conflicts in two hours ([Cursor](https://cursor.com/blog/agent-swarm-model-economics)).

Human review is a third ceiling that sits on top of both gates: parallel sessions concentrate review on one person, and that capacity, not agent count, becomes the throughput constraint ([Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)).

## Example

Cursor's four-configuration comparison shows the model mix moving cost while quality holds:

| Planner | Workers | Total cost | Quality |
|---------|---------|-----------|---------|
| GPT-5.5 | GPT-5.5 | $10,565 | comparable |
| Opus 4.8 | Composer 2.5 | $1,339 | comparable |

Same task, same swarm shape, similar quality — an eightfold cost gap driven entirely by which model plans and which model executes ([Cursor](https://cursor.com/blog/agent-swarm-model-economics)). The lever is the mix, not the fan-out width.

## Key Takeaways

- Ask decomposability first: on non-decomposable tasks, multi-agent variants lost 39 to 70%, and no budget recovers it.
- The planner-worker model mix, not agent count, dominates swarm cost — a frontier planner plus cheap workers held quality at roughly one-eighth the all-frontier cost.
- Throughput sets convergence speed only where task value clears the roughly 15x token premium of multi-agent work.
- Put frontier tokens on decomposition and design; buy width with cheap, high-throughput workers.
- Keep a validating orchestrator: communication-free swarms amplify errors 17.2x versus 4.4x centralized.

## Related

- [Swarm Migration Pattern](swarm-migration-pattern.md) — the mechanics of a 10–20 worker swarm; this page prices how wide that fan-out pays.
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md) — the topology gate that this cost lens sits beside, not replaces.
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — the per-task model-routing rule that generalizes the planner-worker mix.
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md) — human review as the separate throughput ceiling above swarm economics.
- [Cohesion-Aware Task Partitioning](cohesion-aware-task-partitioning.md) — how to test decomposability before fanning out.
