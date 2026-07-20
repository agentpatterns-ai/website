---
title: "Density-Normalized Quality Metrics Mask AI-Driven Code Growth"
term: "Density-Normalized Quality Metric"
description: "A density-normalized quality drop after AI adoption can be a code-growth artifact — a moving denominator turns the ratio into the wrong signal."
tags:
  - anti-pattern
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - smell density denominator artifact
  - lines-of-code normalized quality metric
  - architectural smell density misreading
last_reviewed: 2026-06-14
maturity: emerging
---

# Density-Normalized Quality Metrics Mask AI-Driven Code Growth

> A density-normalized quality metric falls when AI adoption inflates the denominator faster than smells grow — the ratio reports code growth, not improvement.

Density-normalized quality metrics — architectural smells per KLOC, warnings per file, complexity per method — appear to fall after a team adopts AI coding assistants. Platform teams cite the drop as evidence the tools improve code. A 151-repo causal study of Java codebases found the apparent improvement is arithmetic: smell counts stay flat (+1.1%, p = 0.82) while lines of code grow +12.8% (p = 0.003), mechanically producing the headline −6.7% density figure (p = 0.004) without a single architectural defect being removed ([Larsen & Moghaddam, 2026, *arxiv:2606.13298*](https://arxiv.org/abs/2606.13298)).

## The pattern

The metric ships as a single ratio — `smell_count / loc`, `warnings / files`, `complexity / methods` — and teams present the period-over-period delta as the quality signal. Adoption decks pair the falling ratio with the AI rollout date and infer causation. Reports rarely show the numerator and denominator alongside the ratio, so readers cannot tell which one moved.

## Why it fails

A causal estimator can hold everything else constant and the ratio still misleads, because the denominator is part of the treatment. The Larsen & Moghaddam study used a staggered difference-in-differences design with the Borusyak imputation estimator across 1,811 monthly Arcan snapshots of 74 agentic-AI-adopting Java repos against 77 propensity-matched controls; pre-trends were flat (Wald p = 0.90) and wild cluster bootstrap, Lee bounds, and stale-observation checks all held ([Larsen & Moghaddam, 2026](https://arxiv.org/abs/2606.13298)). The clean design still cannot rescue the ratio. The authors warn directly: "density-normalized outcomes can mislead when treatment affects system size."

An independent MSR '26 DiD study of Cursor adoption finds the symmetric shape from the opposite side: a "statistically significant, large, but transient" velocity gain paired with a "substantial and persistent" rise in static-analysis warnings and complexity ([Wang et al., 2025, *arxiv:2511.04427*](https://arxiv.org/abs/2511.04427)). Both papers triangulate to: AI grows the codebase faster than it grows architectural debt, and reports that frame that as a quality win are reading the denominator.

## Why it works

The ratio survives because it is the standard cross-repo comparator. Without normalization, you cannot compare a 10k-LOC repo and a 100k-LOC repo at all, and pre-AI tooling correctly treated density as a quality measure when the denominator drifted slowly. AI adoption broke that assumption: when treatment inflates the denominator faster than the numerator, the ratio crosses from quality signal to artifact, and no internal property of the ratio flags the transition.

## Substitute metrics

Report the decomposition, not the ratio:

- Raw numerator and denominator alongside any density figure. Smell count and LOC, warning count and file count, complexity and method count — published together so the reader sees which one moved. The Larsen & Moghaddam recommendation is "raw counts and explicit decomposition" ([Larsen & Moghaddam, 2026](https://arxiv.org/abs/2606.13298)).
- Period-over-period delta on the numerator alone. A flat or rising raw smell count is the quality signal; a falling density with a flat numerator is the artifact warning.
- Industry baselines for the denominator. GitClear's 2025 longitudinal analysis of 211M changed lines found AI-era refactor share fell from 25% to under 10% while copy-paste share rose from 8.3% to 12.3% — denominator-inflating patterns documented at scale ([GitClear, 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)). A density drop in a repo following the industry trend is presumptively artifact until decomposed.

## When this backfires

- Net-deletion AI usage. Teams using AI for refactoring sweeps, dead-code removal, or migration consolidation may see LOC flat or shrinking; density changes there track real architectural movement and decomposition adds noise without value.
- High-baseline-smell repos. A codebase entering AI adoption with already-saturated absolute smell counts can show genuine density falls as new LOC accretes against a fixed numerator — the decomposition shows the same story but does not falsify the ratio.
- Tech stacks without mature smell detection. Arcan covers Java; for Go, Rust, or modern TypeScript-first stacks where architectural-smell tooling is weak, the numerator becomes noisy enough that neither density nor count is reliable. Decomposition does not rescue an untrustworthy numerator.

## Example

Before — reporting a single ratio:

```text
Q2 architecture review: AI adoption update
- Architectural smell density: -6.7% YoY (1.43 → 1.33 smells/KLOC)
- Statistically significant (p = 0.004)
- Conclusion: agentic AI adoption is improving architectural quality
```

The ratio fell, the p-value clears, and the conclusion follows — except the numerator and denominator are absent, so the reader cannot tell that the smell count was flat and LOC grew 13%.

After — reporting the decomposition:

```text
Q2 architecture review: AI adoption update
- Total architectural smells: +1.1% YoY (n.s., p = 0.82)
- Lines of code: +12.8% YoY (p = 0.003)
- Derived smell density: -6.7% (denominator-driven; do not read as quality signal)
- Conclusion: smell count did not change; codebase grew. AI adoption is not
  improving architectural quality at the repo level over this window.
```

Same data, the conclusion inverts. The decomposition exposes that the density delta is downstream of LOC growth, not architectural cleanup.

## Key Takeaways

- A causal study of 151 Java repos shows agentic AI adoption leaves smell counts flat (+1.1%) while LOC grows +12.8% — the apparent −6.7% density "improvement" is denominator inflation, not architectural cleanup
- Density-normalized metrics break as quality signals when treatment inflates the denominator faster than the numerator; the canonical pre-AI assumption that the denominator drifts slowly no longer holds
- Always report the raw numerator and denominator alongside any quality density, and flag a density drop with a flat numerator as presumptively artifact until decomposed
- The denominator artifact runs in both directions — single-ratio velocity, productivity, and quality dashboards built on `X / LOC` need the same decomposition discipline

## Related

- [Agent Headcount as a Vanity Metric](agent-headcount-vanity-metric.md) — adjacent measurement failure where the easy-to-count number gets cited as outcome evidence
- [Shadow Tech Debt](shadow-tech-debt.md) — the architectural drift that flat smell counts can still understate when AI bypasses structural understanding
- [LLM Code Review Overcorrection](llm-review-overcorrection.md) — companion misreading where the review signal is the artifact, not the code
- [The Reasoning-Complexity Trade-off](reasoning-complexity-tradeoff.md) — stronger models produce more bloated and coupled code; corroborates the LOC-inflation half of this anti-pattern
- [Vibe Coding](vibe-coding.md) — the consumption shape that drives the LOC-inflation denominator behind density artifacts
