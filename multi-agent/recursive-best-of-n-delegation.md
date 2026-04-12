---
title: "Recursive Best-of-N Delegation"
description: "Run K parallel candidate workers at each recursion node and select the best result via a judge before the parent consumes it — preventing error compounding in recursive agent trees."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - recursive best-of-N
  - parallel candidate selection
---

# Recursive Best-of-N Delegation

> Run K parallel candidate workers at each recursion node and select the best result via a judge before the parent consumes it — preventing error compounding in recursive agent trees.

## The Problem

In recursive delegation, each subtask's output becomes input for the parent agent. A weak result at any node doesn't stay local — it poisons every decision above it in the tree. Single-path recursion compounds errors upward with no mechanism for recovery short of a full retry.

## Structure

At each recursion node, instead of sending one candidate result to the parent:

1. **Fan-out** — spawn K candidate workers (typically 2–5) in independent sandboxes for the same subtask
2. **Score** — a judge combines automated signals (tests, lint, exit codes) with LLM-as-judge rubric evaluation
3. **Select** — the top-scoring candidate becomes the canonical result for the parent
4. **Escalate** — if no candidate clears the confidence threshold, increase K or spawn investigator sub-agents
5. **Aggregate** — selected results propagate upward and the parent continues its own recursion

```mermaid
graph TD
    O[Orchestrator] --> N1[Node A]
    O --> N2[Node B]
    N1 --> C1[Candidate 1]
    N1 --> C2[Candidate 2]
    N1 --> C3[Candidate 3]
    C1 & C2 & C3 --> J1[Judge]
    J1 -->|Best result| O
    N2 --> D1[Candidate 1]
    N2 --> D2[Candidate 2]
    N2 --> D3[Candidate 3]
    D1 & D2 & D3 --> J2[Judge]
    J2 -->|Best result| O
```

This is distinct from the [voting/ensemble pattern](voting-ensemble-pattern.md) (flat parallel evaluation of the same task) and from [fan-out synthesis](fan-out-synthesis.md) (merging complementary strengths). Here, selection happens at each internal node of a decomposition tree, not at a single top-level aggregation point.

## Judge Design

Judge quality determines the pattern's reliability. A judge that rationalizes poor outputs is worse than no judge.

| Signal type | Examples | Role |
|-------------|----------|------|
| Objective checks | Test pass rate, lint warnings, exit codes, diff size | Hard gate — failing outputs are eliminated before LLM scoring |
| LLM-as-judge rubric | Correctness, adherence to repo conventions, completeness | Discriminates between candidates that pass objective checks |

Run objective checks first. Eliminate candidates that fail before LLM scoring to avoid wasting evaluation budget and to prevent the judge from rationalizing broken outputs as acceptable.

## Dynamic K Allocation

Applying K uniformly across all nodes wastes compute. A node processing a well-understood, deterministic subtask doesn't benefit from K=5; a node handling ambiguous API behavior or repo-specific convention mapping does.

Heuristics for raising K at a node:

- Prior failures at this subtask type in the same run
- High output variance across early candidates
- Subtask touches security-sensitive code, schema migrations, or high-blast-radius paths
- Cheap verification available (tight test coverage exists for this module)

Lower K (or K=1) is appropriate when subtask outputs are deterministic and machine-verifiable with high confidence.

## When to Apply

**Best fit:**

- Shardable subtasks where outputs are cheaply scorable — tight unit tests, type checking, lint
- High-cost failure modes — migrations, security changes, large refactors where a wrong answer is expensive to undo
- Tasks with repo-specific ambiguity — API conventions, naming patterns that a single agent might misread

**Poor fit:**

- Tasks without a cheap verification signal — if you cannot score candidates objectively, judge quality degrades
- Low-blast-radius leaf nodes where the cost of K candidates exceeds the cost of a retry
- Real-time pipelines where latency is the primary constraint

## Cost Trade-Off

Each node with K=3 costs roughly 3× the per-node compute of single-path recursion, plus judge overhead. The cost is justified when:

- Failures in the subtask are expensive to catch and fix downstream
- The verification signal is cheap relative to the subtask cost

Targeted K allocation — concentrating extra candidates only on uncertain or high-stakes nodes — recovers most of the reliability benefit at a fraction of the uniform-K cost.

## Key Takeaways

- K parallel candidates at each recursion node prevent weak results from compounding upward through the tree
- Judge design is critical: pair automated objective checks with LLM scoring; objective checks eliminate failing candidates before LLM evaluation runs
- Apply dynamic K — higher at uncertain or high-stakes nodes, lower at deterministic leaf nodes — to contain cost
- Escalation path matters: when no candidate clears the confidence threshold, increase K or spawn investigator sub-agents rather than accepting a weak result
- Best suited for subtasks with cheap, objective verification signals and high-cost failure modes

## Related

- [Voting / Ensemble Pattern](voting-ensemble-pattern.md)
- [Fan-Out Synthesis Pattern](fan-out-synthesis.md)
- [Orchestrator-Worker Pattern](orchestrator-worker.md)
- [Sub-Agents Fan-Out](sub-agents-fan-out.md)
- [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Bounded Batch Dispatch](bounded-batch-dispatch.md)
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md)
- [LLM-as-Judge Evaluation](../workflows/llm-as-judge-evaluation.md) — scoring candidate outputs with rubric-based LLM judges at scale
