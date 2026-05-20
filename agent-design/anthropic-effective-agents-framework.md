---
title: "Anthropic's Effective Agents Framework: A Pattern Map"
description: "Anthropic's framework — augmented LLM, five workflow patterns, autonomous loop — maps cleanly to existing agent patterns when applied with explicit conditions."
tags:
  - agent-design
  - tool-agnostic
  - pattern
aliases:
  - Building Effective Agents
  - Anthropic Agent Patterns
---

# Anthropic's Effective Agents Framework: A Pattern Map

> Anthropic's *Building Effective Agents* framework names three building blocks — augmented LLM, five workflow patterns, and the autonomous agent loop — that decompose "build an agent" into a structured selection problem. The framework is foundational but conditional: each pattern works only when its specific assumptions hold.

## Overview

Anthropic's December 2024 engineering post and the expanded *Building Effective AI Agents: Architecture Patterns and Implementation Frameworks* eBook define a taxonomy that is the most-cited primary source in agent-pattern literature ([Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents); [eBook landing](https://resources.anthropic.com/building-effective-ai-agents)). This page maps that taxonomy to existing site pages and names the conditions under which each layer holds.

Anthropic distinguishes three layers:

- **Augmented LLM** — an LLM plus retrieval, tools, and memory
- **Workflows** — five patterns with predefined control flow built on the augmented LLM
- **Agents** — the autonomous loop, where the LLM directs its own control flow

The central advice: start with simple prompts and add agentic systems only when simpler solutions fall short ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)).

## The Augmented LLM

The base unit is an LLM extended with three capabilities ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)):

- **Retrieval** — the model generates its own search queries and consumes the results
- **Tools** — the model selects and invokes tools, then consumes the output
- **Memory** — the model decides what to retain across turns

Anthropic recommends tailoring each capability behind a well-documented interface and cites the Model Context Protocol as one integration substrate. See [Agent Memory Patterns](agent-memory-patterns.md), [Tool Engineering](../tool-engineering/tool-engineering.md), and [Externalization in LLM Agents](externalization-in-llm-agents.md).

## The Five Workflow Patterns

| Anthropic pattern | What it does | Site page |
|---|---|---|
| **Prompt chaining** | Decompose a task into sequential LLM calls with programmatic checkpoints between steps | [Prompt Chaining](../context-engineering/prompt-chaining.md) |
| **Routing** | Classify input and dispatch to a specialized downstream prompt | [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) |
| **Parallelization** | Run independent LLM calls concurrently (sectioning) or repeat the same call for consensus (voting) | [Fan-Out Synthesis](../multi-agent/fan-out-synthesis.md) |
| **Orchestrator-workers** | A central LLM decomposes the task at runtime and dispatches dynamic subtasks to worker LLMs | [Orchestrator-Worker](../multi-agent/orchestrator-worker.md) |
| **Evaluator-optimizer** | A generator produces output; a separate evaluator critiques it; the loop continues until a quality threshold passes | [Evaluator-Optimizer](evaluator-optimizer.md) |

All five share a contract: control flow is predefined in code, not produced by the LLM. That is the dividing line between workflow and agent in Anthropic's taxonomy.

## The Autonomous Agent Loop

Agents receive a task, plan independently, take tool actions, observe results, and either request human input or continue until a stopping condition fires — the LLM owns control flow ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)). Anthropic positions agents as the right choice for open-ended problems where the step count cannot be predicted. See [Goal-Driven Autonomous Loop](goal-driven-autonomous-loop.md), [Loop Strategy Spectrum](loop-strategy-spectrum.md), and [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md).

## Workflows vs Agents: The Decision

Anthropic's decision criteria ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)):

| Dimension | Workflows | Agents |
|---|---|---|
| Best for | Fixed-step tasks | Open-ended tasks with unpredictable paths |
| Predictability | High — explicit code paths | Lower — LLM directs control flow |
| Cost / latency | Lower per invocation | Higher; compounding error rates per extra LLM call |
| Debuggability | Easier — failure localizes to a step | Harder — requires sandboxed testing and guardrails |

The site treats this as a spectrum, not a binary: see [Agentless vs Autonomous](agentless-vs-autonomous.md) for the case that simple two-phase workflows often outperform autonomous agents, and [The Delegation Decision](delegation-decision.md) for matching task characteristics to delegation depth.

## What the eBook Adds Beyond the Blog

The expanded eBook covers material the December 2024 post does not ([eBook landing](https://resources.anthropic.com/building-effective-ai-agents)):

- **Case studies** — Coinbase deploys Claude as a customer-support agentic system with financial-compliance guardrails ([Coinbase engineering blog](https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase)); Thomson Reuters rebuilds CoCounsel Legal on the Claude Agent SDK ([press release](https://www.prnewswire.com/news-releases/thomson-reuters-and-anthropic-expand-partnership-to-connect-claude-with-cocounsel-legal-302769890.html)); Intercom is cited as a customer-support deployment
- **Context management** — expanded in [Anthropic's context-engineering post](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **Skills** — modular instructions for cross-task agent capability, defined in the [agentskills.io standard](https://agentskills.io)

## Why It Works

The framework's value is taxonomic, not algorithmic. By naming five patterns with distinct cost-predictability-debuggability profiles, it converts an under-specified "build an agent" task into a discrete selection: which control-flow shape — sequence, branch, parallel, dispatch, refine — matches this problem? Those shapes are classical CS primitives in agent dress, and the contribution is in matching shape to task before writing code.

The accompanying mechanism for "start simple": every additional LLM call adds latency, cost, and a compounding error rate. The marginal-value threshold for adding a pattern is the marginal-cost threshold of one extra inference. Workflows beat agents whenever a task's structure is stable enough to encode in code, because they pay the inference cost only at decision points the developer chose ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)).

## When This Backfires

The patterns assume the task is well-specified, the output is verifiable, and the framework is applied once rather than continuously evolved. Production experience shows those assumptions fail in several settings ([Towards AI: Beyond Anthropic's Playbook](https://pub.towardsai.net/agent-workflow-patterns-beyond-anthropics-playbook-1bd76a48d63d)):

- **High-frequency, low-complexity tasks** — deterministic code beats both workflows and agents on cost and latency; the "start simple" advice under-specifies how simple ([aimultiple: Building AI Agents](https://aimultiple.com/building-ai-agents))
- **No clear evaluation criterion** — evaluator-optimizer becomes circular when the evaluator cannot reliably distinguish good output from bad; the loop silently degrades into iterative noise
- **High-stakes one-shot decisions** — one agent's answer is not safe for financial, legal, or medical decisions; the framework's autonomous-loop guidance under-specifies adversarial verification and external grounding requirements
- **Retrieval-bottlenecked tasks** — when RAG correctness dominates outcome quality, workflow-pattern selection is a second-order concern
- **Teams with existing frameworks** — the post's caution against frameworks oversells DIY; for teams without infra, LangGraph, CrewAI, or similar encode these patterns at lower upfront cost than re-implementation
- **Definitional drift** — independent reviewers note the post's definitions of "agentic", "workflows", and "agents" are not internally consistent, making the framework harder to apply at the boundary ([thoughtsfromthedatafront analysis](https://www.thoughtsfromthedatafront.com/p/anthropics-blueprint-for-building))

The site's [Anti-Patterns](../anti-patterns/index.md) section catalogues specific failure modes for several of these workflow shapes.

## Key Takeaways

- The augmented LLM (retrieval + tools + memory) is the substrate; the five workflow patterns and the autonomous loop are built on it
- Workflows have predefined control flow in code; agents put the LLM in charge of control flow — that boundary determines cost, predictability, and debuggability
- Start with the simplest viable approach. The marginal-cost threshold for adding a pattern is one extra LLM call's latency and error rate
- The framework's patterns are taxonomic, not algorithmic — they name shape choices a developer must still match to task structure
- Apply the framework with conditions: each pattern fails predictably in specific settings that the original post does not enumerate

## Related

- [Agent Composition Patterns](agent-composition-patterns.md) — the same workflow shapes treated as composition primitives
- [Prompt Chaining](../context-engineering/prompt-chaining.md) — Anthropic's first workflow pattern in detail
- [Evaluator-Optimizer](evaluator-optimizer.md) — Anthropic's fifth workflow pattern in detail
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — taxonomy that subsumes orchestrator-workers and parallelization
- [Agentless vs Autonomous](agentless-vs-autonomous.md) — when simple workflows beat autonomous agents
- [Loop Strategy Spectrum](loop-strategy-spectrum.md) — control-flow choices for the autonomous agent loop
