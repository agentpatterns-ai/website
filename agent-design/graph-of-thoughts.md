---
title: "Graph of Thoughts: Directed Graph Reasoning for Multi-Path Problems"
term: "Graph of Thoughts"
description: "GoT models agent reasoning as a directed graph — enabling branch, aggregate, refine, and backtrack operations that CoT and ToT cannot express."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - Graph of Thoughts
  - GoT prompting
last_reviewed: 2026-06-12
maturity: adopted
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Graph of Thoughts: Directed Graph Reasoning for Multi-Path Problems

> Model reasoning as a directed graph to aggregate insights across independent paths — the operation that neither Chain-of-Thought nor Tree of Thoughts can express.

## The problem with linear and tree topologies

Chain-of-Thought (CoT) forces reasoning into a single linear sequence: each step depends only on the prior step. Tree of Thoughts (ToT) adds branching, so the model can explore multiple paths in parallel. But those paths never reconverge. Once two branches diverge, each runs in isolation to its own conclusion.

Some problems need synthesis across independent reasoning lines: multi-hop inference, strategic planning with interdependent sub-goals, or reconciling several converging analyses. Neither topology can express these, which motivates the richer graph-based scaffolds in [Petri Net of Thoughts](petri-net-of-thoughts.md).

[Besta et al. (2023)](https://arxiv.org/abs/2308.09687) introduced Graph of Thoughts (GoT) to close this gap. GoT models reasoning as a directed graph where thoughts are vertices and dependencies are edges. Any vertex can have multiple predecessors, so diverged paths can reconverge before the model draws a conclusion.

## Four core operations

GoT defines four operations on the reasoning graph:

| Operation | Description | Available in CoT? | Available in ToT? |
|-----------|-------------|:-----------------:|:-----------------:|
| Branch | Generate multiple thoughts from one state | No | Yes |
| Aggregate | Merge insights from multiple paths into one thought | No | No |
| Refine | Improve a thought using context from neighboring nodes | Partial | Partial |
| Backtrack | Revisit an earlier node using later context | No | No |

Aggregate is the operation that sets GoT apart. It lets reasoning paths converge:

```mermaid
graph TD
    A[Problem] --> B[Analysis: approach 1]
    A --> C[Analysis: approach 2]
    A --> D[Analysis: approach 3]
    B --> E[Aggregate: synthesize findings]
    C --> E
    D --> E
    E --> F[Refined conclusion]
    F -->|needs revision| B
```

CoT and ToT can only represent linear or tree-shaped structures. Neither can express the converging edges from B, C, and D into E.

## Performance and cost

On sorting tasks, GoT showed a [62% quality improvement over ToT while reducing costs by more than 31%](https://arxiv.org/abs/2308.09687). The gains come from aggregation: merging intermediate results avoids redundant exploration across independent tree searches.

GoT costs 5–20x more than linear CoT ([nibzard catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/graph-of-thoughts.md)). That overhead is only worth it when the problem genuinely needs path convergence.

[Besta et al. (IEEE TPAMI 2025)](https://arxiv.org/abs/2401.14295) formalized the reasoning-topology taxonomy. It positions CoT, ToT, and GoT as a progression in expressiveness, with GoT as the general case and the others as special instances.

## When GoT is justified

GoT adds value when the problem has interdependent reasoning paths, where insights from one analysis must inform another before a conclusion is sound:

- Multi-hop reasoning: the answer requires chaining findings across multiple independent sub-queries
- Strategic planning: sub-goals have mutual dependencies, so you must reconcile independent analyses before committing to a plan
- Revision under new context: an earlier reasoning step needs refinement after a later step reveals new information, and Backtrack makes this explicit rather than ad hoc
- Solution synthesis: the correct answer is the merge of insights from several paths, not the output of any single one

GoT is not justified for:

- Problems solvable by a single reasoning chain — use CoT
- Exploration tasks where paths do not need to reconverge — use ToT or [Plan Mode](../tools/claude/plan-mode.md)
- Resource-constrained settings — the 5–20x cost premium and implementation complexity limit production use ([nibzard catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/graph-of-thoughts.md))
- Advanced reasoning models (Claude extended thinking, o1) that internalize multi-step synthesis — external GoT scaffolding adds latency without a demonstrated benefit over the model's built-in chain computation

## Implementation considerations

Production GoT requires infrastructure that tree-based prompting does not:

- Graph state management: tracking which nodes are complete, pending, or ready for aggregation
- Scoring per node: evaluation criteria at each vertex, not just at leaves
- Pathfinding: a traversal strategy for deciding which aggregated nodes to expand next
- Redundancy detection: pruning to prevent duplicate reasoning paths accumulating

The [nibzard catalog entry](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/graph-of-thoughts.md) lists the sophisticated scoring and path-finding algorithms GoT requires as a core trade-off — the implementation overhead that keeps it out of most production agent systems.

## Key Takeaways

- GoT adds Aggregate and Backtrack — operations unavailable in CoT or ToT that enable path convergence and explicit revision
- Aggregate is the core differentiator: it merges insights from independent reasoning paths before drawing a conclusion
- GoT is 5–20x costlier than linear CoT — reserve it for problems that genuinely require multi-path synthesis
- Production use requires graph state management, per-node scoring, and redundancy detection — significant barriers to adoption
- For problems with known, fixed decision sequences, [Petri Net of Thoughts](petri-net-of-thoughts.md) provides formal structure with lower overhead

## Related

- [Petri Net of Thoughts: Formal Process Models as Prompting Scaffolds](petri-net-of-thoughts.md) — Formal graph-based reasoning with Petri net structure and state-aware prompts
- [Three Reasoning Spaces: Plan, Bead, and Code](three-reasoning-spaces.md) — Explicit phase gates that separate planning topology from execution
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — Allocate reasoning compute by phase rather than uniformly
- [Agent Composition Patterns](agent-composition-patterns.md) — Multi-agent structural patterns including chains, fan-out, pipelines, and supervisors
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — Two-role loop where generator and evaluator iterate to a quality threshold
- [Self-Discover Reasoning: LLM-Composed Reasoning Structures](self-discover-reasoning.md) — Model selects and composes reasoning modules per task, an alternative to fixed CoT or GoT topologies
