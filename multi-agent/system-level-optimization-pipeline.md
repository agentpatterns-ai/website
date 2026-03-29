---
title: "System-Level Optimization Pipeline: Multi-Agent Performance Engineering"
description: "A four-stage multi-agent pipeline — summarize, analyze, optimize, verify — that reasons about performance across component boundaries instead of optimizing functions in isolation."
tags:
  - multi-agent
  - agent-design
  - workflows
aliases:
  - Multi-Agent Performance Optimization
  - System-Wide Optimization Pipeline
---

# System-Level Optimization Pipeline

> A four-stage agent pipeline decomposes performance engineering into summarization, analysis, optimization, and verification — enabling AI agents to reason about bottlenecks that span component boundaries rather than optimizing functions in isolation.

!!! info "Also known as"
    Multi-Agent Performance Optimization, System-Wide Optimization Pipeline

## The Problem with Local Optimization

Most AI coding agents optimize at the function or file level. You point at a function, ask the agent to "make it faster," and it restructures the algorithm. This works for CPU-bound hot paths but misses the bottlenecks that matter most in distributed systems: connection pool exhaustion across services, lock contention on shared request paths, redundant object allocation in serialization layers.

These system-level performance problems emerge from **cross-component interactions** — how services call each other, share resources, and contend for locks. No single-file optimization pass can find them because the evidence is spread across multiple services and configuration layers.

## The Four-Stage Pipeline

The system-level optimization pipeline assigns each phase of performance engineering to a specialized agent role, following the [orchestrator-worker pattern](orchestrator-worker.md) with sequential handoff.

```mermaid
graph LR
    A[Summarization<br/>Agent] --> B[Analysis<br/>Agent]
    B --> C[Optimization<br/>Agent]
    C --> D[Verification<br/>Agent]

    A -.- A1[Component structure]
    A -.- A2[Behavior / call graphs]
    A -.- A3[Environment / config]
    B -.- B1[Ranked bottlenecks]
    C -.- C1[Code modifications]
    D -.- D1[Test + benchmark]
```

### Stage 1: Summarization

The summarization agent extracts architectural context that downstream agents need. It decomposes into three sub-tasks:

| Sub-Agent | Extracts |
|-----------|----------|
| **Component Summary** | Service boundaries, dependency maps, exported interfaces |
| **Behavior Summary** | Call graphs, control-flow complexity, database interactions, concurrency patterns |
| **Environment Summary** | Build config, runtime settings, deployment topology |

This is the stage that differentiates system-level from local optimization. Without architectural context, agents default to function-level reasoning. With it, they can trace performance signals across service boundaries.

### Stage 2: Analysis

The analysis agent receives the summarization output and identifies optimization opportunities. It ranks candidates by estimated impact and confidence, producing a prioritized list of bottlenecks with their cross-component root causes.

### Stage 3: Optimization

The optimization agent translates each identified bottleneck into concrete code changes. It operates under a non-breaking constraint: public APIs and service interfaces must remain stable. Changes target internal implementation only.

### Stage 4: Verification

The verification agent validates that optimizations are functionally correct (existing tests pass) and measures performance impact through benchmarking. Only verified improvements are retained.

## Early Evidence

[Peng et al. (2026)](https://arxiv.org/abs/2603.14703) evaluated this pipeline on TeaStore, a Java microservices benchmark with six interacting services:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Throughput (req/s) | 1,198 | 1,636 | **+36.6%** |
| Avg response time (ms) | 12.84 | 9.27 | **-27.8%** |
| p50 latency (ms) | 13.0 | 9.0 | **-30.8%** |
| p99 latency (ms) | 26.0 | 23.0 | **-11.5%** |

The three optimizations found were well-known performance patterns: HTTP client reuse via singleton, replacing synchronized methods with volatile flags, and sharing static ObjectMapper instances. The value was not in the novelty of the fixes but in the **automated discovery** across service boundaries.

!!! warning "Early-stage research"
    These results come from a single benchmark system. Comparative evaluations against existing tools (OpenCode, CodeX, SysLLMatic) are planned but not yet conducted. The framework assumes comprehensive existing test suites for correctness validation.

## Practical Takeaway: Context Shapes Optimization Scope

The key insight for developers using AI coding agents: **the context you provide determines the scope of optimization the agent can perform**.

- **File-level context** → agents find local algorithm improvements
- **Repository-level context** → agents find cross-file refactoring opportunities
- **System-level context** (architecture diagrams, dependency maps, call graphs, deployment config) → agents can reason about cross-service bottlenecks

If you want agents to find system-level performance issues, you need to provide system-level context. This means feeding agents:

1. **Dependency maps** — which services call which, and how
2. **Call graphs** — interprocedural flow across service boundaries
3. **Runtime configuration** — connection pools, thread counts, cache settings
4. **Deployment topology** — co-located vs. networked services, resource constraints

Without this, agents will default to the optimization scope their context window supports — which is usually a single file.

## Key Takeaways

- System-level performance bottlenecks emerge from cross-component interactions that no single-file agent pass can detect
- Decomposing optimization into four specialized stages (summarize, analyze, optimize, verify) lets each agent reason within a bounded scope while collectively covering the full system
- The context you feed an agent determines its optimization ceiling — provide architecture-level inputs to get architecture-level results
- Early results are promising (+36.6% throughput on one benchmark) but remain single-system and uncompared to existing tools

## Related

- [Specialized Agent Roles](../agent-design/specialized-agent-roles.md) — each pipeline stage has a distinct, non-overlapping responsibility
- [Orchestrator-Worker Pattern](orchestrator-worker.md) — sequential handoff with structured intermediate outputs
- [Agent Handoff Protocols](agent-handoff-protocols.md) — the summarization output serves as the contract between stages
- [Closed-Loop Role-Based Refinement](closed-loop-role-based-refinement.md) — the verification stage provides the feedback signal

## References

- [Peng et al. (2026). Beyond Local Code Optimization: Multi-Agent Reasoning for Software System Optimization. arXiv:2603.14703](https://arxiv.org/abs/2603.14703)
