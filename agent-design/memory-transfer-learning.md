---
title: "Memory Transfer Learning: Cross-Domain Memory Reuse in Coding Agents"
description: "How coding agents transfer learned memories across different task domains, why abstraction level determines transferability, and when cross-domain memory causes negative transfer."
tags:
  - agent-design
  - memory
  - tool-agnostic
aliases:
  - cross-domain memory transfer
  - memory transfer across domains
---

# Memory Transfer Learning

> Cross-domain memory transfer improves coding agent performance when memories are stored at high abstraction levels — but low-abstraction memories cause negative transfer that actively degrades output.

## The Single-Domain Constraint

Most agent memory systems restrict memory to the task domain where it was created. An agent that solves Python web service bugs retrieves memories from prior Python web service sessions. This works when tasks repeat within a domain but misses a structural reality: coding tasks across different domains share procedural meta-knowledge — iterative workflows, defensive validation, environment navigation — even when they share no algorithms or code.

Memory Transfer Learning (MTL) removes the domain boundary by building a unified memory pool from heterogeneous task sources and retrieving from it regardless of the current task's domain ([Kim et al., 2026](https://arxiv.org/abs/2604.14004)). Across six benchmarks spanning competitive programming, repository-level engineering, CLI tasks, scientific replication, and ML research, a cross-domain memory pool improved average performance by 3.7% at Pass@3 ([Kim et al., 2026, Table 1](https://arxiv.org/abs/2604.14004)).

## Abstraction Level Controls Transferability

The central finding: not all memory formats transfer equally. Four representations span a concrete-to-abstract spectrum ([Kim et al., 2026, §3.2](https://arxiv.org/abs/2604.14004)):

| Representation | Content | Avg. Improvement | Transfer Risk |
|---------------|---------|-----------------|---------------|
| **Trajectory** | Raw action-observation sequences with failed steps | +1.1% | High — domain-specific patterns leak through |
| **Workflow** | Extracted code snippets filtered by an LLM | +1.5% | Moderate — still carries implementation details |
| **Summary** | LLM-generated task/experience summaries | +2.3% | Low |
| **Insight** | Title + description + generalizable principle | +3.7% | Lowest — domain-invariant by construction |

Embedding space analysis confirms the pattern: trajectory embeddings cluster tightly by source benchmark (high Davies-Bouldin Index, low Local Inverse Simpson's Index), while insight embeddings intermingle across benchmarks — they are structurally domain-agnostic ([Kim et al., 2026, Figures 4-5](https://arxiv.org/abs/2604.14004)).

Even within the same format, abstraction matters. When insight memories were split by task-inferability (whether the source task could be guessed from the memory), task-agnostic insights outperformed task-specific ones by 1.1% on average ([Kim et al., 2026, Table 4](https://arxiv.org/abs/2604.14004)).

## What Actually Transfers: Meta-Knowledge, Not Code

An LLM-based analysis of cases where zero-shot failed but MTL succeeded found that 94.5% of gains came from procedural meta-knowledge, not algorithmic strategies ([Kim et al., 2026, Figure 3](https://arxiv.org/abs/2604.14004)):

| Category | Share of Gains | Example |
|----------|---------------|---------|
| Iterative workflow discipline | ~25% | Edit-test-repeat loops instead of one-shot solutions |
| Test-driven verification | ~20% | Creating reproduction scripts when official tests unavailable |
| Environmental adaptation | ~18% | Navigating build tools, missing packages, OS constraints |
| API/interface compliance | ~15% | Preserving function signatures and class structures |
| Anti-pattern avoidance | ~8% | Guardrails like "avoid blind text patching" |
| Other procedural | ~8% | Interaction protocols, input validation, formatting |
| **Algorithmic strategy** | **~5.5%** | Direct programming knowledge, formulas, data structures |

The implication: the transferable substrate of coding agent memory is *how to work*, not *what to build*. A memory from a competitive programming session that says "create a quick self-contained test to validate fixes before submitting" helped an agent solve an unrelated Django ORM bug — not by transferring Python knowledge, but by transferring a validation methodology ([Kim et al., 2026, Table 3](https://arxiv.org/abs/2604.14004)).

## Negative Transfer

Low-abstraction memories cause three failure modes when transferred across domains ([Kim et al., 2026, §4.2, Appendix B](https://arxiv.org/abs/2604.14004)):

**Domain-mismatched anchoring.** Structurally irrelevant but superficially similar memories create misleading assumptions. In one case, a trajectory memory containing R-language heredoc patterns was retrieved for a C++ project, causing the agent to execute incompatible commands.

**False validation confidence.** Verification memories from one domain create self-confirming loops in another. The agent relies on superficial checks borrowed from the source domain instead of applying formal criteria appropriate to the target task.

**Misapplied best-practice transfer.** Successful patterns transferred indiscriminately override task-specific requirements. A "pre-flight verification" pattern (checking datasets and checkpoints exist) was distorted into justification for low-quality smoke testing that violated the target task's quality requirements.

## Scaling and Cross-Model Transfer

**Memory pool size.** Performance increases monotonically with pool size and source domain diversity. Broader diversity enhances meta-knowledge coverage; larger pools increase the probability of retrieving applicable procedural guidance ([Kim et al., 2026, Figure 6](https://arxiv.org/abs/2604.14004)).

**Cross-model transfer.** Memories generated by one model (GPT-5-mini, DeepSeek V3.2, Qwen3-Coder) transfer to others with positive results, though self-generated memories outperform cross-model transfers by 0.5-1.5% ([Kim et al., 2026, Table 6](https://arxiv.org/abs/2604.14004)). This validates that meta-knowledge is largely model-agnostic.

**Retrieval method.** Simple embedding-based retrieval (text-embedding-3-small, top-3) outperformed both LLM reranking and adaptive memory rewriting. The authors attribute this to the difficulty of anticipating retrieval needs in dynamic multi-step agent settings ([Kim et al., 2026, Table 7](https://arxiv.org/abs/2604.14004)).

**Efficiency.** MTL used 431 memories — 13 times fewer than AgentKB's 5,899 — while outperforming both AgentKB and ReasoningBank baselines ([Kim et al., 2026, Table 2](https://arxiv.org/abs/2604.14004)).

## When This Pattern Applies

Cross-domain memory transfer is most valuable when:

- The agent operates across diverse task types that share procedural foundations (builds, tests, deployments, debugging)
- Memory is stored at the insight level — generalizable principles stripped of domain-specific file paths, variable names, and implementation details
- The memory pool draws from multiple source domains, increasing meta-knowledge coverage
- The agent has multiple attempts per task (Pass@3 improvement is 3.7% vs. 1.9% at Pass@1)

It adds cost without proportional value when:

- All tasks come from a single narrow domain where in-domain memory is sufficient
- Memory is stored as raw trajectories or workflows that carry implementation-specific patterns
- The team has limited engineering budget — the meta-knowledge that transfers best (iterative workflows, test-driven verification) can often be encoded directly in system prompts

## Key Takeaways

- Abstraction level is the primary control variable for memory transferability — insight-level memories improve performance 3x more than raw trajectories when used across domains
- 94.5% of successful cross-domain transfer comes from procedural meta-knowledge (workflows, validation, environment navigation), not task-specific code
- Low-abstraction memories cause negative transfer through domain-mismatched anchoring, false validation confidence, and misapplied patterns — strip implementation details before pooling memories
- Cross-domain memory pools scale monotonically with size and diversity, and transfer between models with modest degradation (0.5-1.5%)

## Related

- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — scope-based memory architecture; this page extends with cross-domain transfer specifics
- [Episodic Memory Retrieval](episodic-memory-retrieval.md) — episode-level recall within a domain; contrast with cross-domain episode transfer here
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — extracting lessons from logs; this page covers what abstraction level makes those lessons transferable
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md) — granularity within a domain; complementary to cross-domain abstraction
- [Memory Reinforcement Learning (MemRL)](memory-reinforcement-learning.md) — utility scoring for retrieval quality; orthogonal to cross-domain pooling
- [Dual-Trace Memory Encoding](dual-trace-memory-encoding.md) — fact-plus-scene encoding for temporal recall; different memory encoding strategy
