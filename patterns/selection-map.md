---
title: "Pattern Selection Map: Trade-off Matrix for This Site's Patterns"
description: "Compare 14 patterns from this site across six axes — token cost, latency, frontier-model dependency, blast radius, verification cost, and task class — so you can pick the cheapest pattern that solves your problem."
tags:
  - agent-design
  - cost-performance
  - workflows
aliases:
  - pattern trade-off matrix
  - pattern decision matrix
last_reviewed: 2026-05-26
---

# Pattern Selection Map

> Compare patterns by what they cost, where they break, and what they assume — then pick the cheapest one that solves your problem, not the most sophisticated.

Adopting agent patterns without comparing their costs leads to two failure modes documented on this site: stacking sophisticated patterns ([cargo-cult agent setup](../anti-patterns/cargo-cult-agent-setup.md)) and stacking frontier-model roles until economics collapse ([compound engineering's 80/20 inversion](../workflows/compound-engineering.md)). The matrix below surfaces the trade-offs already documented on each pattern's canonical page so you can compare across them without re-reading every one.

The matrix is scoped to this site's 14 patterns that map onto a common set of axes. Patterns not on the matrix exist for cases where these axes are not the dominant trade-off — they live on their own pages.

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

**Token cost** — relative to a baseline single-shot prompt against the same task:

- `low` — fixed overhead or one-time setup; per-task addition is negligible
- `medium` — roughly 1.5× to 2× baseline
- `high` — roughly 2× to 5× baseline (multiple review or critic passes per task)
- `very high` — 5×+ baseline or stacks frontier-model roles across plan/work/assess phases

**Latency overhead** — wall-clock impact on time-to-result:

- `none` — runs in parallel or as setup; no per-task added latency
- `+1 turn` — adds one model round-trip
- `+N turns` — adds a bounded loop (typically 2–5 iterations or fan-out turns)
- `unbounded` — loops until convergence or human intervention

**Frontier-model dependency** — how many roles require a top-tier model to function:

- `none` — works with mid-tier or open-weight models
- `one role` — one role (reasoning, reviewer, or planner) benefits materially from a frontier model; the rest can run on cheaper models
- `all roles` — every role (planner, executor, critic, reviewer, summariser, memory) benefits from a frontier model; the most expensive shape

**Blast radius** — the maximum reach of a failure or unintended action:

- `read-only` — the pattern only observes or gates; no writes outside its own state
- `contained writes` — writes are scoped to feature branches, ephemeral state, or pre-approved paths
- `production effects` — writes reach production systems, shared ledgers, or persistent infrastructure without an automatic gate

**Verification cost** — how the pattern's correctness is checked:

- `linter-able` — a deterministic script or type check confirms the pattern is wired correctly
- `eval-able` — needs an LLM-graded or metric-based eval to confirm quality; deterministic checks are insufficient
- `human-only` — outcomes require human judgement to validate (taste, architecture review, market dynamics)

**Task class** — the kind of work the pattern fits:

- `one-shot` — single-prompt, single-result tasks
- `iterative` — bounded loops with a clear convergence criterion
- `open-ended` — long-running work without a fixed convergence point (greenfield, ongoing maintenance, multi-agent operations)

## Why It Works

The matrix compresses information that is already present and sourced on each pattern's canonical page. Experienced engineers already think in trade-off axes when choosing architectural patterns — they just lack a centralised comparison surface. Cognitive offloading of the cross-page comparison step is the mechanism. The axes were chosen because they are the dimensions where stacking patterns blindly produces the documented failure modes: token economics, latency budgets, frontier-model cost, and blast radius are the four levers that the [80% problem in agentic coding](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) traces production failures back to.

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
