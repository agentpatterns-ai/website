---
title: "Anthropic's Effective Agents Framework: A Pattern Map"
term: "Anthropic's Effective Agents Framework"
description: "Anthropic's framework — augmented LLM, five workflow patterns, autonomous loop — maps cleanly to existing agent patterns when applied with explicit conditions."
tags:
  - agent-design
  - tool-agnostic
  - pattern
aliases:
  - Building Effective Agents
  - Anthropic Agent Patterns
last_reviewed: 2026-06-12
maturity: established
---

# Anthropic's Effective Agents Framework: A Pattern Map

> Anthropic's *Building Effective Agents* framework names three building blocks — augmented LLM, five workflow patterns, autonomous agent loop — each conditional on its own assumptions.

## Anthropic's three-layer taxonomy

Anthropic's December 2024 engineering post and the expanded 'Building Effective AI Agents' eBook define the most-cited taxonomy in agent-pattern literature ([Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents); [eBook landing](https://resources.anthropic.com/building-effective-ai-agents)). This page maps that taxonomy to site pages and the conditions under which each layer holds.

Anthropic names three layers:

- Augmented LLM — an LLM plus retrieval, tools, and memory
- Workflows — five patterns with predefined control flow, built on the augmented LLM
- Agents — the autonomous loop, where the LLM directs its own control flow

Anthropic's central advice is to start with simple prompts. Add agentic systems only when simpler solutions fall short.

## The augmented LLM

The base unit is an LLM extended with three capabilities ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)):

- Retrieval — the model writes its own search queries and reads the results
- Tools — the model picks and runs tools, then reads the output
- Memory — the model decides what to keep across turns

Anthropic recommends tailoring each capability behind a well-documented interface. It cites the Model Context Protocol as one way to connect them. See [Agent Memory Patterns](agent-memory-patterns.md), [Tool Engineering](../../tool-engineering/tool-engineering.md), and [Externalization in LLM Agents](externalization-in-llm-agents.md).

## The five workflow patterns

| Anthropic pattern | What it does | Site page |
|---|---|---|
| Prompt chaining | Decompose a task into sequential LLM calls with programmatic checkpoints between steps | [Prompt Chaining](../../context-engineering/prompt-chaining.md) |
| Routing | Classify input and dispatch to a specialized downstream prompt | [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) |
| Parallelization | Run independent LLM calls concurrently (sectioning) or repeat the same call for consensus (voting) | [Fan-Out Synthesis](../multi-agent/fan-out-synthesis.md) |
| Orchestrator-workers | A central LLM decomposes the task at runtime and dispatches dynamic subtasks to worker LLMs | [Orchestrator-Worker](../multi-agent/orchestrator-worker.md) |
| Evaluator-optimizer | A generator produces output; a separate evaluator critiques it; the loop continues until a quality threshold passes | [Evaluator-Optimizer](evaluator-optimizer.md) |

All five share one contract: control flow is predefined in code, not produced by the LLM. That is the dividing line between workflow and agent in Anthropic's taxonomy.

## The autonomous agent loop

An agent receives a task, plans on its own, takes tool actions, observes results, and either asks for human input or continues until a stopping condition fires. The LLM owns control flow ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)). Anthropic recommends agents for open-ended problems where you cannot predict the step count. See [Goal-Driven Autonomous Loop](../../loop-engineering/goal-driven-autonomous-loop.md), [Loop Strategy Spectrum](../../loop-engineering/loop-strategy-spectrum.md), and [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md).

## Workflows vs agents: the decision

Anthropic's decision criteria ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)):

| Dimension | Workflows | Agents |
|---|---|---|
| Best for | Fixed-step tasks | Open-ended tasks with unpredictable paths |
| Predictability | High — explicit code paths | Lower — LLM directs control flow |
| Cost / latency | Lower per invocation | Higher; compounding error rates per extra LLM call |
| Debuggability | Easier — failure localizes to a step | Harder — requires sandboxed testing and guardrails |

The site treats this as a spectrum, not a binary. See [Agentless vs Autonomous](agentless-vs-autonomous.md) for the case that simple two-phase workflows often beat autonomous agents, and [The Delegation Decision](delegation-decision.md) for matching task characteristics to delegation depth.

## What the eBook adds beyond the blog

The expanded eBook covers material the December 2024 post does not ([eBook landing](https://resources.anthropic.com/building-effective-ai-agents)):

- Case studies — Coinbase runs Claude as a customer-support agentic system with financial-compliance guardrails ([Coinbase engineering blog](https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase)); Thomson Reuters rebuilds CoCounsel Legal on the Claude Agent SDK ([press release](https://www.prnewswire.com/news-releases/thomson-reuters-and-anthropic-expand-partnership-to-connect-claude-with-cocounsel-legal-302769890.html))
- Context management — expanded in [Anthropic's context-engineering post](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Skills — modular instructions for cross-task agent capability, defined in the [agentskills.io standard](https://agentskills.io)

## Why it works

The framework's value is taxonomic, not algorithmic. It names five patterns with distinct cost, predictability, and debuggability profiles. That turns "build an agent" into a discrete choice: which control-flow shape — sequence, branch, parallel, dispatch, refine — fits this problem? Those shapes are [classical CS primitives](classical-se-patterns-agent-analogues.md), and the contribution is matching shape to task before you write code.

Every extra LLM call adds latency, cost, and a compounding error rate. Workflows beat agents whenever a task's structure is stable enough to encode in code, because they pay the inference cost only at decision points the developer chose ([Anthropic blog](https://www.anthropic.com/engineering/building-effective-agents)).

## When this backfires

The patterns assume the task is well-specified and the output is verifiable. In production, those assumptions fail in several settings ([Towards AI: Beyond Anthropic's Playbook](https://pub.towardsai.net/agent-workflow-patterns-beyond-anthropics-playbook-1bd76a48d63d)):

- High-frequency, low-complexity tasks — deterministic code beats both workflows and agents on cost and latency ([aimultiple: Building AI Agents](https://aimultiple.com/building-ai-agents))
- No clear evaluation criterion — evaluator-optimizer becomes circular when the evaluator cannot reliably tell good output from bad
- High-stakes one-shot decisions — the framework's autonomous-loop guidance under-specifies adversarial verification and external grounding
- Retrieval-bottlenecked tasks — when RAG correctness dominates outcome quality, workflow-pattern choice is a second-order concern
- Teams with existing frameworks — for teams without infra, LangGraph or CrewAI encode these patterns at lower upfront cost than re-implementation
- Definitional drift — independent reviewers note that the post's definitions of "agentic", "workflows", and "agents" are not internally consistent ([thoughtsfromthedatafront analysis](https://www.thoughtsfromthedatafront.com/p/anthropics-blueprint-for-building))
- Parallel sub-agents sharing implicit context — when parallelization or orchestrator-workers is pushed into autonomous multi-agent territory, Cognition argues the pattern turns fragile: concurrent agents that lack each other's implicit design decisions make conflicting choices that do not compose ([Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)). Their follow-up narrows the safe envelope to topologies where multiple agents contribute intelligence but writes stay single-threaded ([Cognition: Multi-Agents — What's Actually Working](https://cognition.ai/blog/multi-agents-working)), the opposite of the dynamic-dispatch framing the original post leaves open

The site's [Anti-Patterns](../anti-patterns/index.md) section catalogs specific failure modes for several of these workflow shapes.

## FAQ

**What are the five workflow patterns, and what does each decompose?**

Prompt chaining splits a task into sequential LLM calls with programmatic checkpoints between steps. Routing classifies input and dispatches to a specialized downstream prompt. Parallelization runs independent calls concurrently or repeats one call for consensus. Orchestrator-workers decomposes the task at runtime and dispatches dynamic subtasks. Evaluator-optimizer pairs a generator with a separate critic that loops until a quality threshold passes.

**What does the eBook add beyond the December 2024 post?**

Three things. Case studies: Coinbase running Claude as a customer-support agentic system with financial-compliance guardrails, and Thomson Reuters rebuilding CoCounsel Legal on the Claude Agent SDK. Expanded context management, developed further in Anthropic's context-engineering post. And Skills — modular instructions for cross-task agent capability, defined in the agentskills.io standard.

**Where do these patterns stop applying?**

They assume a well-specified task and verifiable output. Deterministic code beats both workflows and agents on high-frequency, low-complexity work. Evaluator-optimizer turns circular with no reliable evaluation criterion. Retrieval-bottlenecked tasks make pattern choice second-order. And teams without existing infrastructure often adopt LangGraph or CrewAI more cheaply than re-implementing the patterns themselves.

**What do critics say about the multi-agent guidance?**

Cognition argues that pushing parallelization or orchestrator-workers into autonomous multi-agent territory makes the pattern fragile: concurrent agents that lack each other's implicit design decisions make conflicting choices that do not compose. Their follow-up narrows the safe envelope to topologies where multiple agents contribute intelligence but writes stay single-threaded. Independent reviewers separately note the post's definitions are not internally consistent.

## Key Takeaways

- The augmented LLM (retrieval + tools + memory) is the substrate; the five workflow patterns and the autonomous loop are built on it
- Workflows have predefined control flow in code; agents put the LLM in charge of control flow — that boundary determines cost, predictability, and debuggability
- Start with the simplest viable approach. The marginal-cost threshold for adding a pattern is one extra LLM call's latency and error rate
- The framework's patterns are taxonomic, not algorithmic — they name shape choices a developer must still match to task structure
- Apply the framework with conditions: each pattern fails predictably in specific settings that the original post does not enumerate

## Related

- [Agent Composition Patterns](agent-composition-patterns.md) — the same workflow shapes treated as composition primitives
- [Prompt Chaining](../../context-engineering/prompt-chaining.md) — Anthropic's first workflow pattern in detail
- [Evaluator-Optimizer](evaluator-optimizer.md) — Anthropic's fifth workflow pattern in detail
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — taxonomy that subsumes orchestrator-workers and parallelization
- [Agentless vs Autonomous](agentless-vs-autonomous.md) — when simple workflows beat autonomous agents
- [Loop Strategy Spectrum](../../loop-engineering/loop-strategy-spectrum.md) — control-flow choices for the autonomous agent loop
- [Agentic Pattern Vocabulary Crosswalk](../pattern-vocabulary-crosswalk.md) — site-wide vocabulary crosswalk that uses this page as the Anthropic-column anchor
