---
title: "Recursive Agent Harnesses (RAH)"
term: "Recursive Agent Harness"
description: "Treat the recursive unit of a coding agent as a full harness — filesystem tools, code execution, planning — that spawns subagent harnesses in parallel, not as a bare model call."
tags:
  - agent-design
  - tool-agnostic
  - pattern
  - arxiv
aliases:
  - harness recursion
  - RAH pattern
maturity: emerging
last_reviewed: 2026-06-12
---

# Recursive Agent Harnesses (RAH)

> A parent agent runs a script that spawns subagent harnesses in parallel, making the recursive unit a full harness rather than a model call.

## When to use it

A Recursive Agent Harness (RAH) is conditional, not a default. Use it only when all three hold ([Lumer et al., 2026](https://arxiv.org/abs/2606.13643); [Anthropic multi-agent retrospective](https://www.anthropic.com/engineering/built-multi-agent-research-system)):

1. The work splits into genuinely independent subtasks — no shared naming, types, or call sites that need reconciliation (see [Cohesion-Aware Task Partitioning](../multi-agent/cohesion-aware-task-partitioning.md) for the partition-cost formalism).
2. Each subtask has a cheap verification signal the parent can use to accept or reject the subagent's result, such as passing tests, lint, or a schema check.
3. The task value justifies a roughly 15x token multiplier over a single-agent run ([Anthropic, 2025](https://www.anthropic.com/engineering/built-multi-agent-research-system)).

If any of the three fails, prefer a single-threaded linear agent with a compression sub-LLM ([Cognition, 2025](https://cognition.ai/blog/dont-build-multi-agents)).

## What recurses

The pattern names what the recursive unit is. In Recursive Language Models (RLMs), it is a bare model call — the LLM examines a long prompt and calls itself programmatically on segments inside a Python REPL ([Zhang, Kraska, Khattab, 2025](https://arxiv.org/abs/2512.24601)). In a Recursive Agent Harness, it is a full harness: filesystem tools, code execution, planning, and its own context. The parent agent writes and runs a script that spawns subagent harnesses in parallel for fine-grained workloads, and falls back to structured function calls for minor subtasks ([Lumer et al., 2026](https://arxiv.org/abs/2606.13643)).

| | RLM | RAH |
|---|---|---|
| Recursive unit | Model call | Full agent harness |
| What the unit sees | Text segment | Filesystem, shell, tools |
| Where intermediate state lives | Outer model's variables | Subagent's context + filesystem |
| Failure mode | Long-context degradation | Conflicting parallel decisions |

## Production instance: Dynamic Workflows

[Claude Code Dynamic Workflows](../tools/claude/dynamic-workflows.md) ship a working instance ([Claude Code docs](https://code.claude.com/docs/en/workflows)): the parent agent writes a JavaScript orchestration script that a background runtime executes. It coordinates up to 1,000 subagents per run, with 16 in-flight, and holds results in script variables instead of the orchestrator's context. The parent generates code rather than control flow, each subagent inherits its own harness, and the concurrency cap bounds coordination overhead.

## Why it works

When the three preconditions hold, RAH wins for one reason: each subagent inherits a fresh context window plus its own tools. This moves work that would have crowded the parent's window into a per-subagent window and into executable actions a runtime can verify, instead of prompt tokens the parent must read ([Lumer et al., 2026](https://arxiv.org/abs/2606.13643)).

How well the mechanism works depends on how independent the subtasks really are. When subagents' work conflicts, the recursive structure cannot reconcile it. The parent only sees the returned artifacts and must choose between them without visibility into the reasoning that produced each one ([Cognition, 2025](https://cognition.ai/blog/dont-build-multi-agents)).

## When this backfires

RAH fails under specific, common conditions.

- Coupled coding work. Anthropic's multi-agent retrospective notes that "most coding tasks involve fewer truly parallelizable tasks than research" ([Anthropic, 2025](https://www.anthropic.com/engineering/built-multi-agent-research-system)). Parallel subagents working on shared naming, types, or call sites make implicit decisions that conflict on return, and the parent must reconcile them, eating the speedup ([Cognition, 2025](https://cognition.ai/blog/dont-build-multi-agents)). See [Cohesion-Aware Task Partitioning](../multi-agent/cohesion-aware-task-partitioning.md) for the partition-cost mechanism.
- Low-value tasks. Multi-agent runs use roughly 15 times the tokens of a single chat. A small refactor, doc edit, or simple bug fix cannot justify the multiplier, so the recursive structure pays the cost without earning it back. The [Agent-Headcount Vanity Metric](../anti-patterns/agent-headcount-vanity-metric.md) is the matching anti-pattern when the token cost is not paid back.
- No leaf-level verification signal. RAH assumes the parent can judge each subagent's output cheaply. Without an objective check per subtask, the parent rationalizes weak results rather than rejecting them. This is the recurring multi-agent failure cluster identified across 1,642 traces ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657); see also [Multi-Agent SE Design Patterns](../multi-agent/multi-agent-se-design-patterns.md)).
- Single-paper provenance. The RAH numbers — 71.75% to 81.36% on Oolong-Synthetic with a Codex baseline, 89.77% with Claude Sonnet 4.5 — come from one paper, one benchmark, 199 samples ([Lumer et al., 2026](https://arxiv.org/abs/2606.13643)). No independent replication yet.

Cognition argues that a single-threaded linear agent with a compression sub-LLM keeps the context-window benefit without the conflicting-decisions risk ([Cognition, 2025](https://cognition.ai/blog/dont-build-multi-agents)).

## Example

The Lumer et al. paper does not publish its parent-agent script. The closest production version is Claude Code's Dynamic Workflows runtime, where a parent agent writes a JavaScript script the runtime executes:

```text
Run a workflow to audit every API endpoint under src/routes/ for missing auth checks
```

The parent agent produces an orchestration script along these lines:

```javascript
// Sketch of a Dynamic Workflows parent script
const endpoints = await agent({
  agentType: "Explore",
  prompt: "List every route handler under src/routes/"
});

const findings = await parallel(endpoints.map(ep => ({
  agentType: "audit-page-worker",
  prompt: `Check ${ep} for missing auth middleware`,
})));

const verified = await agent({
  agentType: "skeptic",
  prompt: `Refute each finding: ${JSON.stringify(findings)}`,
});

return verified.filter(f => !f.refuted);
```

The `verified` step is what makes this RAH rather than ordinary fan-out — an adversarial check at each recursion node gives the parent a cheap signal for accepting or rejecting each subagent's result. Without it, the pattern collapses into the conflicting-decisions failure mode.

## Key Takeaways

- The recursive unit is a full harness (tools, execution, planning), not a model call — that's what distinguishes RAH from RLMs
- Use only when subtasks are genuinely independent, leaf verification is cheap, and task value justifies a ~15× token cost
- The parent generates and runs a script — intermediate results live in script variables, not the parent's context, which is why the pattern scales
- Evidence is one paper, one benchmark; Dynamic Workflows is the most credible production exemplar, but the empirical case is narrow

## Related

- [Claude Code Dynamic Workflows](../tools/claude/dynamic-workflows.md) — production runtime for the pattern, with the 1,000-agent cap and script-as-orchestrator model
- [Recursive Best-of-N Delegation](../multi-agent/recursive-best-of-n-delegation.md) — companion reliability pattern: K candidates per recursion node, judge-selected, to contain the conflicting-decisions risk
- [Cohesion-Aware Task Partitioning](../multi-agent/cohesion-aware-task-partitioning.md) — the partition-cost lens that decides whether subtasks are independent enough to recurse over
- [Agent Harness: Initializer and Coding Agent](agent-harness.md) — the harness this pattern makes the recursive unit of
- [Anthropic's Effective Agents Framework](anthropic-effective-agents-framework.md) — the workflow-vs-agent taxonomy RAH extends with a code-first orchestration script
- [Deep Agent Runtime](deep-agent-runtime.md) — the runtime layer that durably executes the script the parent writes
- [Orchestrator-Worker Pattern](../multi-agent/orchestrator-worker.md) — the structural pattern RAH specialises by making the worker a recursive harness
