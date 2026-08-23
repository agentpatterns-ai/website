---
title: "Coding-Agent Working-Set Coverage (Coherence Debt)"
term: "Coherence Debt"
description: "Repository-scale coding agents fail when the coupled facts an upcoming edit needs are not resident in active context and not in parametric memory."
tags:
  - context-engineering
  - agent-design
  - pattern
  - arxiv
  - tool-agnostic
aliases:
  - coding agent working set
  - coupled fact graph coverage
  - agent context coverage debt
last_reviewed: 2026-08-18
maturity: emerging
---

# Coding-Agent Working-Set Coverage (Coherence Debt)

> Coherence debt is the coupled facts an upcoming edit needs that sit in neither active context nor parametric memory; the shortfall decides edit correctness.

An edit's correctness depends on availability. When Mohammadi et al. instrumented seven models across five harnesses, supplied facts stayed useful across the whole context (up to 128,000 characters in a tool-using harness, 200,000 in a closed-book run), while withheld facts produced linear damage across five withholding levels ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)). The measurable variable is coverage: what fraction of an edit's coupled facts is available at write time, from either channel.

## The two supply channels

Coverage is a union over two supply channels, both bounded. Effective context (`Rtᵢ`) is what the agent has resident now: prompt-supplied facts, files it has read, tool outputs, handoff notes. Context evicts as new reads arrive. Parametric memory (`K_M`) is what the model knows without reading, fixed per model and unreliable on any API it has not seen. Coherence debt for a given edit is the required coupled facts minus that union ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)). A fact absent from both channels does not make the agent stop; it makes the agent produce a confidently wrong edit.

The operations follow. Read the fact into effective context. Rely on parametric memory when you can verify the model knows the API. Design the harness so residency survives compaction and eviction between the read and the write.

## Distance stops mattering when coverage holds

The paper's Section 4.2 result overturns a common tuning instinct that a fact should sit near the edit it drives. Across the tested harnesses a supplied fact drove correct decisions regardless of position; withholding produced the failures ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)). This is compatible with earlier positional findings in retrieval-QA, where [Lost in the Middle](lost-in-the-middle.md) measured recall drops on static long prompts ([Liu et al., 2024, arXiv:2307.03172v3](https://arxiv.org/abs/2307.03172v3)). In a coding-agent trace the harness surfaces facts through re-reads, tool feedback, and compaction, so a fact remains present when the edit needs it. Position becomes a symptom of coverage design rather than an independent cause.

## The stale-file trap

Coverage is signed. Across ten trials per condition on 3,385 scored decisions, a current convention file drove 100% correct decisions; the same task with code alone drove 33%; a stale convention file demanding worse practice drove 0% ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)). A wrong fact is worse than a missing one, because the agent will produce an edit consistent with what it read. This is the mechanism behind the [Hacker News observation](https://news.ycombinator.com/item?id=47938417) that "a good AGENTS.md is a model upgrade, a bad one is worse than no docs at all". [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) covers what to place there; coherence debt covers what happens when the placed content lies.

## Why it works

An agent is a producer. Faced with a coupled fact it lacks, it will not usually pause and ask; it will emit an edit. The output is therefore plausibly consistent with what the agent read. Coverage decides whether "consistent with what it read" also means "correct". Read-monitoring, which logs what the agent looked at, cannot detect the shortfall: a page the agent never opened leaves no read trace, so the audit surface must be the produced edit, checked against the fact set the edit required ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)). The corollary is that identical task success can hide wide variation in how a harness reaches it. Across six configurations that all passed the same tests, cumulative input varied 12.8× and peak context 1.8× ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)).

## When this backfires

- Single-file edits and green-field code. Six of seven tested workloads were migration-shaped; the authors state the framework "should explain less" for single-file edits ([Mohammadi et al., 2026 v1](https://arxiv.org/abs/2608.16630v1)).
- Retrieval-QA on a static long prompt. Positional attention effects still dominate that task shape, which the coding-agent measurement did not cover ([Liu et al., 2024](https://arxiv.org/abs/2307.03172v3)).
- Portable residency dashboards. The paper's residency score does not transfer to real repositories (AUC ≈ 0.49 on SWE-bench, close to chance); the concept is workload-relative, not a general metric.
- Facts nobody wrote down. Coverage cannot supply what does not exist. On a rename that defeats parametric memory and has no written reference, every tested model failed identically.

## Key Takeaways

- Coverage of an edit's coupled facts, from context or parametric memory, is the variable that predicts whether the edit is correct.
- A supplied fact stayed usable across the full tested context length; withheld facts produced linear damage across five withholding levels.
- A stale convention file drove 0% correct decisions against 33% for code alone, because the agent's output stays consistent with what it read.
- Audit against what the agent produced, not what it looked at; missing facts surface as confident wrong edits, never as blank output.
- Identical test-pass outcomes can hide a 12.8× spread in tokens spent reconstructing the same facts, so a "successful" run is a weak signal for harness quality.

## Related

- [Lost in the Middle](lost-in-the-middle.md) — the positional recall finding this pattern reframes; both hold within their own task shapes.
- [Context Quality as a Leading Indicator of Agent Reliability](context-quality-audit.md) — the seven-dimension audit that operationalizes whether the coverage set is actually present.
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — the rule for which facts belong in a convention file, before the stale-file trap can bite.
- [Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)](../patterns/anti-patterns/large-codebase-agent-failure-patterns.md) — a symptom taxonomy for the same coverage failure, measured on a different bench.
- [Whole-Codebase Visibility as a Migration Prerequisite](../workflows/whole-codebase-visibility-migration-prerequisite.md) — the up-front scoping check that decides whether an agent-driven migration can reach the required coverage at all.
