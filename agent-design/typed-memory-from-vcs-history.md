---
title: "Typed Memory from VCS History: When It Pays Off"
description: "Distil git history into Facts, Skills, and Patterns — pays off only under tight retrieval budgets and high commit hygiene; otherwise it returns BM25 parity."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - typed memory layer for repositories
  - commit-history knowledge distillation
last_reviewed: 2026-05-27
---

# Typed Memory from VCS History

> Mine git commits, pull-request discussions, and issue threads into a typed memory layer (Facts, Skills, Patterns) that a coding agent consults before acting. The pattern only pays off under tight retrieval budgets and high commit hygiene — under typical conditions it converges with a BM25 baseline.

Typed memory from VCS history is a memory layer that extracts structured prior knowledge from commit messages, PR discussions, and issue threads using deterministic extractors, then exposes the result to a coding agent through a budget-constrained retriever.

## When This Pattern Applies

The reference implementation, CommitDistill, reports a 0.750 hit-rate over BM25 (0.333) and `git log` grep (0.083) at a **256-character query budget** but **no statistically detectable lift on headline LLM-as-judge metrics** in head-to-head evaluation ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)). Apply only when all four conditions hold:

- **High-quality commit hygiene** — conventional commits, structured PR descriptions, linked issues. 90% of 5,000 randomly sampled GitHub commits are assessed low quality; 14% of commits across 23,000 OSS projects are empty and only 10% contain normal descriptive English ([Tian et al. 2022](https://arxiv.org/pdf/2202.02974)). Low-quality input yields a low-signal index.
- **Tight retrieval budget** — the typing advantage shrinks as per-query character budget grows; unconstrained retrieval converges with BM25 ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)).
- **Slow-evolving codebase** — extracted Facts and Patterns reflect commit-time state. Repos refactoring quarterly encode conventions the codebase no longer follows.
- **Repository scale** — small repos let the agent read raw `git log` directly; indexing only amortises once linear scans exceed the budget.

If any condition fails, prefer commit-time capture going forward (see *Trade-offs*) or rely on `git log` read ad-hoc.

## How It Works

The CommitDistill design has three components ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)):

- **Deterministic extractor** — regex over commit messages, PR descriptions, and issue threads. No embeddings, no external service. Reported throughput: 10,000 commits in under 4 seconds on a laptop.
- **Typed knowledge units** — three categories that act as a coarse-grained category filter at retrieval time:
    - **Facts** — discrete information units (e.g. a specific configuration value, an API constraint)
    - **Skills** — procedural knowledge (e.g. how a migration is run, the steps to regenerate a fixture)
    - **Patterns** — recurring approaches or conventions (e.g. how this repo names files, how errors are handled)
- **Budget-constrained TF-IDF retriever with calibrated silence threshold (theta = 2.5)** — declines to answer out-of-distribution queries rather than returning irrelevant top-k matches. The silence threshold is what makes the typed structure load-bearing under tight budgets.

```mermaid
graph LR
    A[git history<br>commits + PRs + issues] -->|deterministic regex| B[Typed units<br>Facts / Skills / Patterns]
    B --> C[TF-IDF index]
    C -->|budget-constrained query| D[Retriever]
    D -->|theta &gt; 2.5| E[Return units]
    D -->|theta &le; 2.5| F[Decline / silence]
    E --> G[Agent context]
```

The independent finding that supports the broader approach: [Wang et al. 2025](https://arxiv.org/abs/2510.01003) shows augmenting a code-localisation agent with historical commits, linked issues, and module-functionality summaries improves repository-level bug-fix localisation. Their gain comes from the combined signal — commits alone are insufficient.

## Why It Works

The typed structure acts as a category filter under tight budgets because TF-IDF's lexical noise dominates when the query carries few tokens. Splitting the corpus into three disjoint pools lets the retriever route to the right pool before scoring, so a 256-character query lands in a narrower space than full lexical search over raw commits ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)). The calibrated silence threshold (theta = 2.5) is the second load-bearing element — it returns nothing when no unit clears the threshold, preventing the agent from acting on weakly relevant noise. Without abstention, top-k over noisy commits surfaces false positives that degrade output ([abstention-aware retrieval](abstention-aware-memory-retrieval.md) shows the effect generalises).

## When This Backfires

- **Confident retrieval of stale Facts** — on fast-evolving codebases, extracted Patterns conflict with current conventions; the index becomes a confident source of wrong answers. Outdated information in RAG knowledge bases substantially reduces response accuracy and can mislead models even when current information is available ([Ouyang et al. 2025](https://arxiv.org/abs/2503.04800)).
- **Decision Shadow already lost** — each commit captures the diff but not the reasoning, constraints, or rejected alternatives. No extractor can recover what was never recorded. The orthogonal fix is to instrument commit-time capture going forward — for example, the Lore protocol restructures commit messages with git trailers carrying constraints, rejected alternatives, and agent directives ([Stetsenko 2026](https://arxiv.org/abs/2603.15566)).
- **Treated as a default upgrade** — CommitDistill itself reports indistinguishable performance from BM25 in head-to-head LLM-as-judge evaluation ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)). The pattern is a budget-conditional optimisation, not a default.

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Typed memory from VCS history (CommitDistill-style) | Cheap to build (10K commits < 4s, no embeddings); typing structure dominates under tight budgets; calibrated silence prevents noisy retrieval | No headline lift over BM25 in LLM-as-judge eval; degrades on low-quality commit history; stale on fast-moving repos |
| Raw `git log` read into context | Zero infrastructure; always current | Linear cost in history size; agent burns context budget on irrelevant commits |
| Instrument commit-time capture (e.g. [Lore](https://arxiv.org/abs/2603.15566)) | Preserves Decision Shadow at the source; structured trailers carry constraints and alternatives | Requires team discipline going forward; historical commits remain unstructured |
| Combined signal (commits + linked issues + module summaries) | Reported improvement on repository-level localisation ([Wang et al. 2025](https://arxiv.org/abs/2510.01003)) | More moving parts; harder to attribute gains to a single component |

## Key Takeaways

- Treat this as a budget-conditional optimisation, not a default — CommitDistill reports no headline lift over BM25 in LLM-as-judge evaluation ([Chukkapalli et al. 2026](https://arxiv.org/abs/2605.18284)).
- The reported advantage holds at a 256-character budget; larger budgets converge with the lexical baseline.
- Regex extraction, Facts/Skills/Patterns typing, and the silence threshold (theta = 2.5) work as a unit — remove abstention and the layer becomes a confident noise source.
- Commit-history quality is the binding constraint. With 90% of random GitHub commits low quality ([Tian et al. 2022](https://arxiv.org/pdf/2202.02974)), the index reflects the source.
- For repos lacking commit hygiene, instrument capture going forward (e.g. [Lore](https://arxiv.org/abs/2603.15566)) rather than mining historical noise.

## Related

- [Tiered Memory Architecture](tiered-memory-architecture.md) — Episodic-to-semantic promotion as a different shape of structured memory; both are conditional on long operation windows
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — Extract causal lessons from agent execution traces; complementary memory source that does not depend on commit hygiene
- [Abstention-Aware Memory Retrieval](abstention-aware-memory-retrieval.md) — The calibrated-silence mechanism CommitDistill uses; abstention is what makes typed memory load-bearing under tight budgets
- [Episodic Memory Retrieval](episodic-memory-retrieval.md) — Episode-level retrieval as an alternative memory shape — closer to raw observation streams, less structured than typed units
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — Scope-and-temporal memory taxonomy that typed memory from VCS history slots into as a cross-session source
