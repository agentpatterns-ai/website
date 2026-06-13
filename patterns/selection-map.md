---
title: "Pattern Selection Map: Trade-off Matrix for This Site's Patterns"
term: "Pattern Selection Map"
description: "Compare 14 patterns from this site across six axes — token cost, latency, frontier-model dependency, blast radius, verification cost, and task class — so you can pick the cheapest pattern that solves your problem."
tags:
  - agent-design
  - cost-performance
  - workflows
  - tool-agnostic
  - long-form
aliases:
  - pattern trade-off matrix
  - pattern decision matrix
last_reviewed: 2026-06-13
---

# Pattern Selection Map

> This selection map compares patterns by what they cost, where they break, and what they assume — so you pick the cheapest one that works.

Adopting agent patterns without comparing their costs produces two documented failure modes: stacking sophisticated patterns ([cargo-cult agent setup](../anti-patterns/cargo-cult-agent-setup.md)) and stacking frontier-model roles until economics collapse ([compound engineering's 80/20 inversion](../workflows/compound-engineering.md)). The matrix below surfaces the trade-offs from each pattern's canonical page so you can compare without re-reading every one.

It is scoped to this site's 14 patterns that share a common set of axes. Patterns where these axes are not the dominant trade-off live on their own pages.

## The Matrix

| Pattern | Token cost | Latency overhead | Frontier-model dependency | Blast radius | Verification cost | Task class |
|---------|------------|------------------|---------------------------|--------------|-------------------|------------|
| [Harness Engineering](../agent-design/harness-engineering.md) | low | none | none | contained writes | linter-able | open-ended |
| [Agent Self-Review Loop](../agent-design/agent-self-review-loop.md) | high | +N turns | one role | contained writes | eval-able | iterative |
| [Cognitive Reasoning vs Execution](../agent-design/cognitive-reasoning-execution-separation.md) | medium | +1 turn | one role | contained writes | linter-able | iterative |
| [Episodic Memory Retrieval](../agent-design/episodic-memory-retrieval.md) | low | +1 turn | none | read-only | eval-able | iterative |
| [Agent Circuit Breaker](../agent-design/agent-circuit-breaker.md) | low | none | none | read-only | linter-able | iterative |
| [Agent Backpressure](../agent-design/agent-backpressure.md) | low | none | none | contained writes | linter-able | iterative |
| [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) | medium | +N turns | one role | contained writes | human-only | open-ended |
| [Declarative Multi-Agent Topology](../multi-agent/declarative-multi-agent-topology.md) | medium | +N turns | one role | contained writes | linter-able | open-ended |
| [Economic Value Signaling](../multi-agent/economic-value-signaling.md) | medium | +N turns | none | production effects | human-only | open-ended |
| [Review-Then-Implement Loop](../code-review/review-then-implement-loop.md) | high | +N turns | one role | contained writes | eval-able | iterative |
| [Agentic Code Review Architecture](../code-review/agentic-code-review-architecture.md) | high | +N turns | one role | read-only | eval-able | iterative |
| [Incremental Verification](../verification/incremental-verification.md) | low | +1 turn | none | contained writes | linter-able | iterative |
| [Escape Hatches](../workflows/escape-hatches.md) | low | none | none | read-only | human-only | open-ended |
| [Compound Engineering](../workflows/compound-engineering.md) | very high | unbounded | all roles | production effects | human-only | open-ended |

## Axis Legend

**Token cost** — relative to a baseline single-shot prompt:

- `low` — fixed or one-time setup; per-task addition negligible
- `medium` — roughly 1.5×–2× baseline
- `high` — roughly 2×–5× baseline (multiple review or critic passes)
- `very high` — 5×+ baseline, or stacks frontier-model roles across phases

**Latency overhead** — wall-clock impact on time-to-result:

- `none` — runs in parallel or as setup
- `+1 turn` — one added model round-trip
- `+N turns` — a bounded loop (typically 2–5 iterations or fan-out turns)
- `unbounded` — loops until convergence or human intervention

**Frontier-model dependency** — how many roles need a top-tier model:

- `none` — works with mid-tier or open-weight models
- `one role` — one role (reasoning, reviewer, or planner) needs a frontier model; the rest run cheaper
- `all roles` — every role needs a frontier model; the most expensive shape

**Blast radius** — the maximum reach of a failure or unintended action:

- `read-only` — only observes or gates; no external writes
- `contained writes` — writes scoped to branches, ephemeral state, or pre-approved paths
- `production effects` — writes reach production or shared ledgers without an automatic gate

**Verification cost** — how correctness is checked:

- `linter-able` — a deterministic script or type check confirms wiring
- `eval-able` — needs an LLM-graded or metric-based eval; deterministic checks fall short
- `human-only` — requires human judgement (taste, architecture, market dynamics)

**Task class** — the kind of work the pattern fits:

- `one-shot` — single-prompt, single-result tasks
- `iterative` — bounded loops with a clear convergence criterion
- `open-ended` — long-running work with no fixed convergence point

## Why It Works

The matrix compresses information already sourced on each pattern's canonical page. Experienced engineers think in trade-off axes when choosing architectural patterns but lack a centralised comparison surface — cognitive offloading of the cross-page comparison step is the mechanism. The axes are the dimensions where stacking patterns blindly produces the documented failure modes: token economics, latency, frontier-model cost, and blast radius. These map onto the production-engineering work the [80% problem in agentic coding](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) identifies as the failure surface — the retry logic, rate limiting, and blast-radius controls that agentic coding skips on the way to a fast first draft.

## When This Backfires

The matrix is a comparison aid, not a recommendation engine. Three failure modes to watch:

- **Pattern shopping** — scanning the table and assembling several patterns at once produces the exact stack-everything failure mode the page exists to defuse. The TL;DR and the closing rule are deliberate counterweights.
- **Stale rows** — pattern pages evolve over time. If a pattern page changes its cost or blast-radius characterisation, the matrix row diverges silently until the next periodic audit catches it. The `last_reviewed` frontmatter dates the synthesis.
- **Axis flattening** — a single ordinal value per axis hides distributions. A pattern marked `medium` token cost in steady state may spike to `high` during cold start or on certain task shapes. The canonical page carries the nuance; the matrix row does not.

## Key Takeaways

- Compare across patterns on costs you already care about — token spend, latency, blast radius — before composing them.
- `low`-cost patterns ([harness engineering](../agent-design/harness-engineering.md), [agent backpressure](../agent-design/agent-backpressure.md), [incremental verification](../verification/incremental-verification.md)) are the unsexy foundation; sophisticated patterns assume these are already in place.
- `very high` cost patterns ([compound engineering](../workflows/compound-engineering.md)) deliver on long horizons but collapse economics on short tasks — match cost class to task class.
- `production effects` blast radius ([economic value signaling](../multi-agent/economic-value-signaling.md), [compound engineering](../workflows/compound-engineering.md)) requires human-only verification — these are not patterns to stack speculatively.
- If two patterns score similarly across all axes, pick the one your team can debug at 3am.

## Related

- [Patterns](index.md) — the parent index this map sits under
- [Cargo Cult Agent Setup](../anti-patterns/cargo-cult-agent-setup.md) — copying patterns without understanding the trade-offs is the failure mode this map exists to defuse
- [AI Development Maturity Model](../workflows/ai-development-maturity-model.md) — adoption phases for AI coding tools; complements the per-pattern trade-off view with a developmental view
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md) — the broader treatment of cost as a first-class design constraint
- [Compound Engineering](../workflows/compound-engineering.md) — the highest-cost pattern on the matrix; the planning/review investment that makes it economic
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — coordination-pattern comparison (Sequential / Concurrent / Group chat / Handoff / Magentic) for the topologies above; orthogonal axes to this map's six
