---
title: "Bounded Agent Steps Inside a Deterministic Workflow"
term: "Bounded Agent Step"
description: "Embed a tool-using agent as one fenced workflow stage — pre-set goal, tool allowlist, turn cap, typed output — only where the boundary is a durable seam."
tags:
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - agent as a workflow step
  - embedded agent step
  - fenced agent stage
last_reviewed: 2026-08-02
maturity: emerging
---

# Bounded Agent Steps Inside a Deterministic Workflow

> A bounded agent step runs an agentic loop as one workflow stage, fenced by a pre-set goal, tool allowlist, turn cap, and typed output.

A bounded agent step keeps the agentic loop — a model that picks tools and iterates until it is satisfied — but strips it of the two powers that make a run unrepeatable: choosing what happens next, and deciding when the work is finished. The surrounding workflow owns both. Shuai Guo's [worked implementation](https://towardsdatascience.com/put-the-agent-inside-the-workflow/) shows the shape: one stage of an experimentation pipeline receives a typed `ExperimentSpec`, may call exactly one tool, runs at most ten turns, and must return a typed `AgentRecommendation` before the next stage will accept it.

This is a weaker move than handing control flow back to the program, which the [LLM-as-Code](llm-as-code-agentic-programming.md) and [deterministic orchestration](deterministic-orchestration-structured-modernization.md) pages cover. Those replace the agent with a plain model call. This one keeps the agent and builds the fence.

## The conditions that have to hold first

Build the fence only when both are true. Neither is about the model.

- The stage boundary is a durable domain seam — a transaction boundary, an audit point, a real interface between teams or systems. A boundary drawn because the model cannot yet be trusted to pick tools expires when that stops being true.
- The typed hand-off carries enough for the next stage to interpret it. If the next stage needs the reasoning and not just the answer, a narrow schema is a defect, not a contract.

## The four fences

| Fence | What the workflow supplies | What it buys |
|-------|---------------------------|--------------|
| Pre-set goal | The stage's objective, not the user's request | The agent cannot redefine the task mid-run |
| Tool allowlist | Only the tools this stage needs | Blast radius is the stage, not the system |
| Turn or iteration cap | A hard ceiling on loop iterations | A stuck agent fails fast instead of burning budget |
| Typed output | A schema validated at the boundary | Failure surfaces as a named validation error at a known stage |

Anthropic's guidance names the same primitives without the staging frame: use "stopping conditions (such as a maximum number of iterations) to maintain control," and run agents with "extensive testing in sandboxed environments, along with the appropriate guardrails" ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

## Why it works

The fence buys localization. Without a typed boundary, a bad agent decision surfaces as an incoherent result at the end of the run, and you work backwards to find where it went wrong. With one, it surfaces as a schema violation at a named stage — which is what makes retry-in-place and stage-level isolation possible at all. Every containment move here depends on that: you cannot retry a step you cannot identify.

Underneath sits the variance mechanism the [deterministic orchestration](deterministic-orchestration-structured-modernization.md) page derives in full — each fenced decision is one fewer stochastic branch compounding across the run. The measured effect is on the tail, not the mean. Holding models, prompts, tools, and source programs constant and varying only execution control on COBOL-to-Python modernization, Lwin and Kumar found comparable accuracy, improved worst-case robustness, and up to 3.5x lower token consumption ([arXiv:2605.09894v1](https://arxiv.org/abs/2605.09894v1)). Average accuracy did not move; the worst runs got better.

## When this backfires

Two failure modes are specific to this pattern, and both have first-hand accounts behind them.

The first is a fence built around a model limitation. Lance Martin built an orchestrator-worker research workflow in late 2024 that deliberately avoided tool calling because tool calling was unreliable then. Within months it was not: "the structure I imposed prevented me from leveraging these improvements. I did not use tool calling, so I could not take advantage of the growing MCP ecosystem" ([Learning the Bitter Lesson](https://rlancemartin.github.io/2025/07/30/bitter_lesson/)). He removed the structure and moved to an agent. Martin quotes Hyung Won Chung's rule: add structure for the compute available, then "remove them later, because these shortcuts will bottleneck further improvement."

The second is a typed output that starves the next stage. Walden Yan's first principle of context engineering is the direct opposite of a narrow schema: "Share context, and share full agent traces, not just individual messages" ([Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)). Because "most real-world tasks have many layers of nuance that all have the potential to be miscommunicated," a summary discards exactly that nuance — and the defect is invisible in testing, since every stage passes its own contract.

Three more conditions carry over unchanged from [LLM-as-Code](llm-as-code-agentic-programming.md) and [agentless vs autonomous](agentless-vs-autonomous.md): control flow that genuinely cannot be fixed in advance, one-off or fast-changing workflows where the contract code costs more than the variance it removes, and nesting so deep that every node is itself a fenced agent.

## Key Takeaways

- Fence the agent, do not replace it — the bounded step keeps tool use and iteration, and takes away only next-step choice and stop authority
- Justify every stage boundary by a durable domain seam; a boundary drawn around a current model weakness becomes the thing blocking your next upgrade ([Martin, 2025](https://rlancemartin.github.io/2025/07/30/bitter_lesson/))
- The measured win is variance and cost, not accuracy — comparable accuracy, better worst case, up to 3.5x fewer tokens ([Lwin & Kumar, 2026](https://arxiv.org/abs/2605.09894v1))
- A typed output that drops the trace can starve the next stage while every contract still passes ([Yan, 2025](https://cognition.com/blog/dont-build-multi-agents))
- Start with the stopping condition — Anthropic recommends a maximum-iterations cap as the baseline control for any agent ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents))

## Related

- [LLM-as-Code Agentic Programming for Agent Harnesses](llm-as-code-agentic-programming.md) — The stronger version of the same inversion, where the program replaces the agent loop with plain model calls
- [Deterministic Orchestration for Structured Modernization](deterministic-orchestration-structured-modernization.md) — The controlled study behind the variance and token mechanism, applied to legacy modernization
- [Stochastic-Deterministic Boundary as First-Class Contract](stochastic-deterministic-boundary.md) — The proposer, verifier, commit, reject contract that a typed stage boundary is one instance of
- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md) — The empirical case for constraining agents, and where constraint stops paying
- [Cognitive Reasoning vs Execution: A Two-Layer Agent](cognitive-reasoning-execution-separation.md) — The layer split that a fenced stage boundary enforces in practice
