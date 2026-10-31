---
title: "Heuristic-Based Effort Scaling in Agent System Prompts"
term: "Heuristic-Based Effort Scaling"
description: "Encode resource allocation rules in prompts so agents spend proportional effort — few tool calls for simple lookups, many subagents for complex research."
tags:
  - instructions
  - agent-design
  - cost-performance
  - tool-agnostic
  - reliability
aliases:
  - effort scaling
  - effort-based resource allocation
last_reviewed: 2026-10-27
maturity: adopted
---

# Heuristic-Based Effort Scaling in Agent System Prompts

> Encode resource allocation rules in system prompts so agents spend proportional effort: few tool calls for simple lookups, many subagents for complex research.

Related lesson: [Orchestrator-Worker](https://learn.agentpatterns.ai/harness-engineering/orchestrator-worker/) — a hands-on lesson with quizzes covers this concept.

## The problem with rigid instructions

[Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) spawned up to 50 subagents for queries needing one until explicit complexity tiers were encoded.

## Complexity tiers

Define tiers in the system prompt with concrete resource ceilings:

| Tier | Example | Agents | Tool calls |
|------|---------|--------|------------|
| Simple fact-finding | "What does function X return?" | 1 | 3–10 |
| Direct comparison | "Compare approach A vs B" | 2–4 | 10–15 each |
| Complex research | "Audit the entire auth surface" | 10+ | Parallelized |

These numbers come from [Anthropic's documented experience](https://www.anthropic.com/engineering/multi-agent-research-system) building a production research system. Thresholds depend on your domain — the principle is that tiers exist and are explicit, not inferred.

## Breadth-first before narrowing

Specific query instructions push agents into narrow searches — the over-low [system-prompt altitude](../../instructions/system-prompt-altitude.md) failure mode. A breadth-first heuristic beats step-by-step specificity because the agent can adapt to what it discovers. Start with broad queries, inspect the results, then narrow the search. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) prompted this pattern after seeing the failure mode. A broad query returning 50 filterable results beats a specific query returning zero.

## Extended thinking as a planning phase

Before committing to a tool strategy, a lead agent can use extended thinking to assess complexity, select tool paths, set subagent count, and plan division of labor. [Anthropic's system](https://www.anthropic.com/engineering/multi-agent-research-system) uses this as a planning scratchpad before spawning subagents. Subagents use interleaved thinking after each tool result to decide whether to continue, pivot, or escalate.

The skills documentation says to include `ultrathink` anywhere in skill content to request deeper reasoning ([skills documentation](https://code.claude.com/docs/en/skills#advanced-patterns)). The automatic effort increase has a narrower scope: the interactive terminal. Release 2.1.311 raises that turn to `xhigh` on Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1 through Anthropic's API. Typed mid-turn, it raises the rest of that turn. The rainbow indicator appears only where the keyword can raise effort; quoted words and file paths do not qualify ([changelog 2.1.311](https://code.claude.com/docs/en/changelog#2-1-311)).

## Parallelization rules

Encode explicit parallelization constraints alongside tier limits. [Anthropic's research system](https://www.anthropic.com/engineering/multi-agent-research-system) found two independent dimensions:

1. Lead agent spawning 3–5 subagents simultaneously (not sequentially)
2. Each subagent executing 3+ tools in parallel

Combining both reduced complex query time by up to 90%. The system prompt should state which dimension applies at each tier; otherwise agents default to sequential execution.

## Agent self-diagnosis

Claude models can identify their own failure modes when prompted to. [Anthropic's system](https://www.anthropic.com/engineering/multi-agent-research-system) used a "tool-testing agent" that rewrote poor [MCP](../../standards/mcp-protocol.md) tool descriptions — a 40% reduction in completion time. Route diagnostic observations back into the prompt refinement loop and check [convergence](../../loop-engineering/convergence-detection.md).

## Iterative refinement protocol

[Anthropic's team](https://www.anthropic.com/engineering/multi-agent-research-system) started with about 20 queries representing real usage to assess early changes. The post uses a possible 30%-to-80% improvement to illustrate a large effect; it does not report that range as a measured result.

## Runtime effort adjustment in Claude Code

Claude Code's `/effort` command selects low, medium, high, xhigh, or max, subject to model support. `xhigh` sits between high and max. Run it between turns to escalate or reduce effort without re-prompting from scratch. The system prompt encodes default scaling heuristics; `/effort` lets the operator override them at runtime — see [model configuration documentation](https://code.claude.com/docs/en/model-config#adjust-effort-level).

## When this backfires

Heuristic effort scaling adds coordination overhead and multiplies token consumption. [Anthropic's research system](https://www.anthropic.com/engineering/multi-agent-research-system) documented multi-agent architectures using roughly 15× more tokens than single-agent chat. Three conditions make the trade-off unfavorable:

1. High inter-dependency tasks — if subtasks must share state or a later step depends on an earlier output, parallel subagents cause duplication and merge conflicts. Most coding tasks fall here: file-level changes conflict, and agents exploring the same module independently produce overlapping results.
2. Cost-sensitive or latency-sensitive workloads — spawning 10+ subagents is justified only when the answer's value scales with thoroughness. Routine lookups routed to Tier 3 by a miscalibrated classifier over-spend by an order of magnitude.
3. Synchronous execution constraints — the lead agent cannot steer subagents after spawning, and subagents cannot coordinate mid-run. If the search space shifts partway through, the system cannot adapt until the full batch completes.

## Example

A system prompt for a code research agent encodes three explicit tiers. The agent reads the query and applies the matching tier before spawning any subagents.

```
You are a code research agent. Before taking any action, classify the incoming query into one of three tiers:

TIER 1 — Simple fact-finding (e.g. "What does function X return?", "Which file defines Y?")
  - Use 1 agent (yourself), no subagents
  - Maximum 10 tool calls total
  - Start with a broad search, narrow once

TIER 2 — Direct comparison or impact analysis (e.g. "Compare approach A vs B", "What calls into module Z?")
  - Spawn 2–4 subagents in parallel, one per hypothesis
  - Maximum 15 tool calls per subagent
  - Each subagent reports a structured summary; you synthesise

TIER 3 — Complex research or cross-cutting audit (e.g. "Audit the auth surface for privilege escalation")
  - Spawn 10+ subagents, divided by subsystem or file cluster
  - Each subagent executes 3+ tool calls in parallel
  - Use extended thinking before spawning to plan division of labour

If the query fits no tier, default to Tier 2.
```

A query like "What does `validateSession` return?" triggers Tier 1: the agent runs a single `grep` or `read_file`, finds the return type, and answers. A query like "Audit all places that bypass authentication" triggers Tier 3: extended thinking produces a decomposition by subsystem, and 10+ subagents fan out in parallel across the codebase. Without explicit tiers, both queries would be handled with the same default strategy — either consistently over-investing (spawning subagents for fact lookups) or consistently under-investing (single-agent for the full auth audit).

## Key Takeaways

- Define explicit complexity tiers in system prompts with agent counts and tool-call budgets per tier.
- Breadth-first discovery heuristics outperform step-by-step specificity because they adapt to discovered context.
- Extended thinking gives lead agents a planning phase before committing to a tool strategy — see [reasoning budget allocation](reasoning-budget-allocation.md) for sizing it alongside tool-call budgets.
- Parallelization gains compound: parallel subagents and parallel tool calls within subagents are independent multipliers.
- Anthropic began early evaluation with about twenty representative queries to observe large changes; this does not establish a general regression-detection threshold ([research post](https://www.anthropic.com/research/multi-agent-research-system)).
- Claude Code's `/effort` command allows runtime effort adjustment between turns, complementing prompt-level heuristics.

## Related

- [System Prompt Altitude: Specific Without Being Brittle](../../instructions/system-prompt-altitude.md) — where to set instruction specificity so effort heuristics stay adaptable
- [Sub-Agents Fan-Out](../multi-agent/sub-agents-fan-out.md) — the parallel-subagent mechanism the higher tiers spend on
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — the cost discipline that effort scaling operationalizes
- [Reasoning Budget Allocation](reasoning-budget-allocation.md) — allocating thinking budget alongside tool-call budgets
- [Reasoning Effort Over Tool Scaffolding for First-Try Reliability](reasoning-effort-over-tool-scaffolding.md) — evidence that effort, not extra tools, moves first-try reliability
- [Code-Health-Gated LLM Tier Routing](auto-model-selection.md) — route by file-level code health as a pre-generation signal
- [Specialized Agent Roles](specialized-agent-roles.md) — assigning distinct roles to the subagents each tier spawns
- [Loop Strategy Spectrum: Accumulated, Compressed, and Fresh Context](../../loop-engineering/loop-strategy-spectrum.md) — context strategies that pair with effort tiers
