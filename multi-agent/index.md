---
title: "Multi-Agent Systems: Coordination and Orchestration"
description: "Patterns for designing, coordinating, and operating systems where multiple agents collaborate — topology, fan-out, and deployment."
tags:
  - agent-design
  - multi-agent
---
# Multi-Agent Systems

> Patterns for designing, coordinating, and operating systems where multiple agents collaborate — from topology selection through fan-out parallelism to production deployment.

## Topology & Architecture

Choosing the right structure for agent collaboration determines failure modes, latency, and coordination overhead.

- [Multi-Agent Topology Taxonomy: Centralised, Decentralised, and Hybrid](multi-agent-topology-taxonomy.md) — Choosing the wrong coordination topology for a task type is a primary source of production agent failures; each topology carries distinct failure modes
- [Multi-Agent SE Design Patterns: A Taxonomy Across 94 Papers](multi-agent-se-design-patterns.md) — A systematic study of 94 LLM-based multi-agent SE papers identifies 16 design patterns, with Role-Based Cooperation as the dominant pattern
- [Orchestrator-Worker Pattern](orchestrator-worker.md) — A lead agent decomposes a complex task and assigns independent subtasks to specialized workers running in parallel
- [Oracle-Based Task Decomposition](oracle-task-decomposition.md) — Introduce a reference oracle to generate per-unit expected outputs, converting one monolithic task into hundreds of independently verifiable subtasks

## Fan-Out & Parallelism

Strategies for splitting work across parallel agents — and controlling the blast radius of concurrent execution.

- [Fan-Out Synthesis Pattern](fan-out-synthesis.md) — Spawn N independent agents to solve the same problem in parallel, then use a synthesis agent to merge the strongest elements from each attempt
- [Sub-Agents for Fan-Out Research and Context Isolation](sub-agents-fan-out.md) — Spawn sub-agents to parallelize independent work in isolated context windows; the main thread receives only distilled results
- [Bounded Batch Dispatch](bounded-batch-dispatch.md) — Process large agent workloads without hitting API rate limits by dispatching work in sequential batches of fixed size
- [Staggered Agent Launch](staggered-agent-launch.md) — Launch parallel agents 30 seconds apart to break the thundering-herd dynamic so each agent claims work before the next reads the queue
- [LLM Map-Reduce Pattern](llm-map-reduce.md) — Split a large input into context-window-sized chunks, process each chunk independently, then combine chunk-level results into a coherent output

## Coordination

How agents hand off work, share state, and refine each other's output without a centralized controller.

- [Agent Handoff Protocols: Passing Work Between Agents](agent-handoff-protocols.md) — Define explicit contracts between pipeline stages to prevent information loss at handoff points
- [File-Based Agent Coordination](file-based-agent-coordination.md) — Coordinate parallel agents using lightweight file locks in a shared repository; git merge mechanics enforce task exclusivity without a central orchestrator
- [Observation-Driven Coordination: CRDT-Based Parallel Agent Code Generation](crdt-observation-driven-coordination.md) — CRDT-based shared state enables lock-free concurrent code generation with zero structural merge conflicts
- [Closed-Loop Role-Based Refinement](closed-loop-role-based-refinement.md) — Decompose the self-improving agent loop into discrete, specialized roles with persistent knowledge layers, staged validation, and gated persistence

## Multi-Model

Patterns that leverage multiple distinct models — using diversity of reasoning to strengthen outputs.

- [Adversarial Multi-Model Development Pipeline (VSDD)](adversarial-multi-model-pipeline.md) — A six-phase pipeline where a fresh-context adversary attacks builder output until convergence, combining spec-driven development, TDD, and formal verification
- [Multi-Model Plan Synthesis](multi-model-plan-synthesis.md) — Get independent plans from multiple frontier models, then synthesize a hybrid architecture from the strongest ideas of each before writing code
- [Voting / Ensemble Pattern](voting-ensemble-pattern.md) — Run the same task N times in parallel, then aggregate results through voting to trade compute for confidence

## Operational

Deploying, observing, and optimizing multi-agent systems in production.

- [Rainbow Deployments for Agents](rainbow-deployments-agents.md) — Shift traffic between agent versions gradually so new versions prove themselves alongside old ones before full cutover
- [Emergent Behavior Sensitivity](emergent-behavior-sensitivity.md) — Small changes to a lead agent's prompt unpredictably alter subagent behavior; multi-agent prompts must be frameworks for collaboration, not rigid instructions
- [Semantic Caching for Multi-Agent Code Systems](semantic-caching-multi-agent.md) — Semantic caching with LLM-based equivalence detection achieves 67% cache hit rates and reduces token consumption by 40-60%
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — Restrict subagent capabilities by filtering their tool schemas, making unauthorized tool use structurally impossible
