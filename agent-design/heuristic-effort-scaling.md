---
title: "Heuristic-Based Effort Scaling in Agent System Prompts"
description: "Encode resource allocation rules in prompts so agents spend proportional effort — few tool calls for simple lookups, many subagents for complex research."
tags:
  - instructions
  - agent-design
  - cost-performance
aliases:
  - effort scaling
  - effort-based resource allocation
---

# Heuristic-Based Effort Scaling in Agent Prompts

> Encode resource allocation rules directly in system prompts so agents spend proportional effort on each query — few tool calls for simple lookups, many subagents for complex research.

## The Problem with Rigid Instructions

Fixed instructions like "always use three subagents" waste tokens on simple fact-finding and under-invest on complex tasks. "Be thorough" gives no actionable constraint. [Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) encountered this directly: early versions spawned up to 50 subagents for queries that needed one. Encoding explicit complexity tiers solved it.

## Complexity Tiers

Define tiers in the system prompt with concrete resource ceilings:

| Tier | Example | Agents | Tool calls |
|------|---------|--------|------------|
| Simple fact-finding | "What does function X return?" | 1 | 3–10 |
| Direct comparison | "Compare approach A vs B" | 2–4 | 10–15 each |
| Complex research | "Audit the entire auth surface" | 10+ | Parallelized |

These numbers come from [Anthropic's documented experience](https://www.anthropic.com/engineering/multi-agent-research-system) building a production research system. The exact thresholds depend on your domain — the critical principle is that tiers exist and are explicit, not inferred.

## Breadth-First Before Narrowing

Specific query instructions cause agents to issue overly narrow searches. A breadth-first heuristic outperforms step-by-step specificity because the agent can adapt to what it discovers. Encode it directly: "Start with short, broad queries. Evaluate what's available. Then progressively narrow focus." [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) explicitly prompted this pattern after observing the failure mode — a broad pattern returning 50 filterable results beats a specific pattern returning zero.

## Extended Thinking as a Planning Phase

Before committing to a tool strategy, a lead agent can use extended thinking to assess query complexity, select tool paths, determine subagent count, and plan division of labour. [Anthropic's system](https://www.anthropic.com/engineering/multi-agent-research-system) uses this as a planning scratchpad before spawning subagents. Subagents then use interleaved thinking after each tool result to evaluate quality and decide whether to continue, pivot, or escalate.

Include "ultrathink" in a Claude Code skill to enable extended thinking [unverified] — see [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

## Parallelization Rules

Encode explicit parallelization constraints alongside tier limits. [Anthropic's research system](https://www.anthropic.com/engineering/multi-agent-research-system) found two independent dimensions:

1. Lead agent spawning 3–5 subagents simultaneously (not sequentially)
2. Each subagent executing 3+ tools in parallel

Combining both reduced complex query time by up to 90%. The system prompt should state which dimension applies at each tier; otherwise agents default to sequential execution.

## Agent Self-Diagnosis

Claude models can identify their own failure modes when prompted to. [Anthropic's system](https://www.anthropic.com/engineering/multi-agent-research-system) used a "tool-testing agent" that analysed poor [MCP](../standards/mcp-protocol.md) tool descriptions and rewrote them — a 40% reduction in completion time. Route those diagnostic observations back into the prompt refinement loop.

## Iterative Refinement Protocol

[Anthropic's team](https://www.anthropic.com/engineering/multi-agent-research-system) found that ~20-query test sets are sufficient to detect regressions when refining effort-scaling prompts. Early iterations showed prompt tweaks moving success rates from 30% to 80%.

The refinement loop:

1. Run the current prompt against a fixed 20-query test set
2. Identify tiers where effort was misallocated (over or under)
3. Adjust tier thresholds or heuristic phrasing
4. Re-run and verify no regression on previously-passing queries

Avoid large test sets at the refinement stage — they slow the loop without proportional signal gain.

## Runtime Effort Adjustment in Claude Code

Claude Code's `/effort` command sets the reasoning effort level (low, medium, high). It can be adjusted while Claude is actively responding [unverified], allowing mid-task escalation rather than re-prompting. The system prompt encodes default scaling heuristics; `/effort` lets the operator override in real time.

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
- Extended thinking gives lead agents a planning phase before committing to a tool strategy.
- Parallelization gains compound: parallel subagents and parallel tool calls within subagents are independent multipliers.
- Small test sets (~20 queries) are sufficient for detecting regressions during prompt refinement.
- Claude Code's `/effort` command allows runtime effort adjustment, even during an active response [unverified], complementing prompt-level heuristics.

## Related

- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [Sub-Agents Fan-Out](../multi-agent/sub-agents-fan-out.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Reasoning Budget Allocation](reasoning-budget-allocation.md)
- [The Think Tool](think-tool.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Agentic AI Architecture Evolution](agentic-ai-architecture-evolution.md)
- [Agentic Flywheel](agentic-flywheel.md)
- [Classical SE Patterns and Agent Analogues](classical-se-patterns-agent-analogues.md)
- [Cognitive Reasoning and Execution Separation](cognitive-reasoning-execution-separation.md)
- [Loop Strategy Spectrum: Accumulated, Compressed, and Fresh Context](loop-strategy-spectrum.md)
- [Specialized Agent Roles](specialized-agent-roles.md)
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md)
