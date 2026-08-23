---
title: "Memory Transfer Learning: Cross-Domain Memory Reuse in Coding Agents"
term: "Memory Transfer Learning"
description: "How coding agents transfer learned memories across different task domains, why abstraction level determines transferability, and when cross-domain memory causes negative transfer."
tags:
  - agent-design
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - cross-domain memory transfer
  - memory transfer across domains
last_reviewed: 2026-05-27
maturity: emerging
---

# Memory Transfer Learning

> Cross-domain memory transfer improves coding agent performance when memories are stored at high abstraction levels — but low-abstraction memories cause negative transfer that actively degrades output.

## The single-domain constraint

Most agent memory systems retrieve only from the task domain where the memories were created. Yet coding tasks across domains share procedural meta-knowledge — iterative workflows, defensive validation, environment navigation — even when they share no algorithms.

Memory Transfer Learning (MTL) pools memories from heterogeneous sources and retrieves regardless of current domain ([Kim et al., 2026](https://arxiv.org/abs/2604.14004v1)). Across six benchmarks — competitive programming, repository engineering, CLI tasks, scientific replication, ML research — the cross-domain pool lifted average Pass@3 by 3.7% ([Kim et al., 2026, Table 1](https://arxiv.org/abs/2604.14004v1)).

## Abstraction level controls transferability

Four representations span a concrete-to-abstract spectrum ([Kim et al., 2026, §3.2](https://arxiv.org/abs/2604.14004)):

| Representation | Content | Gain | Transfer Risk |
|---------------|---------|------|---------------|
| Trajectory | Raw action-observation sequences | +1.1% | High — domain-specific patterns leak through |
| Workflow | LLM-filtered code snippets | +1.5% | Moderate — still carries implementation details |
| Summary | LLM-generated task summaries | +2.3% | Low |
| Insight | Title + description + generalizable principle | +3.7% | Lowest — domain-invariant by construction |

Embedding analysis confirms the mechanism: trajectory embeddings cluster tightly by source benchmark, while insight embeddings intermingle — domain-agnostic by construction ([Kim et al., 2026, Figures 4-5](https://arxiv.org/abs/2604.14004v1)). Within the insight format, task-agnostic insights beat task-specific ones by 1.1% ([Kim et al., 2026, Table 4](https://arxiv.org/abs/2604.14004v1)).

## What actually transfers: meta-knowledge, not code

In cases where zero-shot failed but MTL succeeded, 94.5% of gains came from procedural meta-knowledge, not algorithmic strategy ([Kim et al., 2026, Figure 3](https://arxiv.org/abs/2604.14004v1)):

| Category | Share | Example |
|----------|------|---------|
| Iterative workflow discipline | ~25% | Edit-test-repeat loops vs. one-shot solutions |
| Test-driven verification | ~20% | Reproduction scripts when tests are unavailable |
| Environmental adaptation | ~18% | Build tools, missing packages, OS constraints |
| API/interface compliance | ~15% | Preserving function signatures and class structures |
| Anti-pattern avoidance | ~8% | Guardrails like "avoid blind text patching" |
| Other procedural | ~8% | Interaction protocols, input validation, formatting |
| Algorithmic strategy | ~5.5% | Formulas, data structures, direct programming knowledge |

What transfers is how to work, not what to build. A competitive-programming memory — "create a self-contained test before submitting" — helped solve an unrelated Django ORM bug by transferring methodology, not Python ([Kim et al., 2026, Table 3](https://arxiv.org/abs/2604.14004v1)).

## Negative transfer

Low-abstraction memories cause three failure modes across domains ([Kim et al., 2026, §4.2, Appendix B](https://arxiv.org/abs/2604.14004)):

Domain-mismatched anchoring misleads the agent with memories that look similar but do not apply. A trajectory of R-language heredoc patterns, retrieved for a C++ project, triggered incompatible commands.

False validation confidence comes from verification memories that form self-confirming loops across domains. The agent leans on borrowed checks instead of criteria that fit the target.

Misapplied best-practice transfer warps a sound pattern into the wrong setting. A "pre-flight verification" rule became justification for smoke testing that violated the target's quality bar.

## Scaling and cross-model transfer

Performance rises with pool size and source-domain diversity ([Kim et al., 2026, Figure 6](https://arxiv.org/abs/2604.14004)).

Memories transfer across models. Those from GPT-5-mini, DeepSeek V3.2, and Qwen3-Coder transfer to one another. Self-generated memories win by only 0.5 to 1.5% ([Kim et al., 2026, Table 6](https://arxiv.org/abs/2604.14004v1)).

Simple embedding retrieval (text-embedding-3-small, top-3) beat both LLM reranking and adaptive rewriting ([Kim et al., 2026, Table 7](https://arxiv.org/abs/2604.14004)).

MTL used 431 memories — 13x fewer than [AgentKB's](https://arxiv.org/abs/2507.06229) 5,899 — while beating both AgentKB and [ReasoningBank](https://arxiv.org/abs/2509.25140) ([Kim et al., 2026, Table 2](https://arxiv.org/abs/2604.14004v1)).

## When this pattern applies

Use cross-domain transfer when:

- Tasks span diverse types sharing procedural foundations (builds, tests, debugging)
- Memory is stored at the insight level — principles stripped of file paths, variable names, implementation details
- The pool draws from multiple source domains
- The agent has multiple attempts per task (Pass@3 gain 3.7%, against 1.9% at Pass@1)

Skip it when:

- Tasks come from a single narrow domain where in-domain memory suffices
- Memory is stored as raw trajectories or workflows carrying implementation-specific patterns
- The transferable meta-knowledge can be encoded directly in system prompts

## Key Takeaways

- Abstraction level controls transferability — insight-level memories improve performance 3x more than raw trajectories across domains
- 94.5% of cross-domain gain is procedural meta-knowledge (workflows, validation, environment navigation), not task-specific code
- Low-abstraction memories cause negative transfer via domain-mismatched anchoring, false validation confidence, and misapplied patterns — strip implementation details before pooling
- Pools scale monotonically with size and diversity; cross-model transfer degrades by only 0.5-1.5%

## Related

- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — scope-based memory architecture; this page extends with cross-domain transfer specifics
- [Episodic Memory Retrieval](episodic-memory-retrieval.md) — episode-level recall within a domain; contrast with cross-domain episode transfer here
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — extracting lessons from logs; this page covers what abstraction level makes those lessons transferable
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md) — granularity within a domain; complementary to cross-domain abstraction
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — utility scoring for retrieval quality; orthogonal to cross-domain pooling
- [Dual-Trace Memory Encoding](dual-trace-memory-encoding.md) — fact-plus-scene encoding for temporal recall; different memory encoding strategy
