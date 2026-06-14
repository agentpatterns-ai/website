---
title: "Coding-Agent Reversibility: Platform Choice as a Two-Way Door"
description: "Coding agents make platform and language choices reversible — but only when behavioural tests, stable contracts, and shallow platform-API surface hold."
tags:
  - human-factors
  - workflows
  - tool-agnostic
aliases:
  - reversible platform decisions
  - platform lock-in calculus
  - agent-driven migration economics
last_reviewed: 2026-06-13
maturity: established
---

# Coding-Agent Reversibility: Platform Choice as a Two-Way Door

> Coding agents make a platform choice reversible only in proportion to how well executable tests capture behaviour — not by any property of the agent.

Coding-agent reversibility is the decision-economics shift in which a platform or language choice — once a multi-year, one-way commitment — becomes a multi-day agent run *if* the codebase meets specific conditions. Mitchell Hashimoto framed it as: "Programming languages used to be LOCK IN, and they're increasingly not so" ([Simon Willison, 2026-05-14](https://simonwillison.net/2026/May/14/mitchell-hashimoto/)). The conditions decide whether that holds or is a trap that ships the wrong stack.

## When Reversibility Holds

Treat a platform decision as reversible only when all hold:

| Condition | Why it matters |
|-----------|----------------|
| **High-coverage behavioural tests** | Agents converge against tests; missing coverage means semantic drift goes invisible. FreshBrew gates migrations on test pass *and* coverage within 5 pp ([arxiv 2510.04852](https://arxiv.org/abs/2510.04852)). |
| **Stable external contracts** | Public APIs, data formats, and wire protocols anchor the translation. Internal refactors lack this anchor. |
| **Shallow platform-API surface** | The fewer HealthKit, ARKit, CoreML, or kernel-level calls, the more of the codebase is portable logic vs. platform glue. |
| **Functional requirements dominate** | Agents preserve logic, not latency distributions, memory profiles, or security postures. |

If any is missing, the cost saving is the small half of the bill.

## Why It Works (When It Does)

The agent's translate → compile → test → correct loop converges quickly when the suite is dense enough to anchor every behavioural decision, and slowly (or wrongly) when it is not ([FreshBrew §3](https://arxiv.org/abs/2510.04852)). The test suite is the portability substrate; the agent amortises it into a one-time port cost ([Simon Willison, 2026-05-14](https://simonwillison.net/2026/May/14/not-so-locked-in/)).

The empirical anchor is Bun PR [#30412](https://github.com/oven-sh/bun/pull/30412): 1,009,257 lines of Rust replacing Zig in six days at a 99.8% pass rate, produced by Claude agents in a four-phase translate, error-correct, and verify loop ([byteiota analysis](https://byteiota.com/bun-rust-rewrite-merged-the-13000-unsafe-block-problem/)). The pre-existing dense suite was the precondition.

## When This Backfires

Five situations break the framing:

- **Anaemic test coverage.** FreshBrew — same-language JDK 8 → JDK 17 upgrades with mandatory ≥50% baseline coverage — caps the top model (Gemini 2.5 Flash) at **52.3% project success** across 228 real Java projects ([arxiv 2510.04852](https://arxiv.org/abs/2510.04852)). Cross-language ports against weaker suites do worse.
- **Tests pass, production doesn't.** A logistics company migrating Java to Node.js passed every functional test then failed under realistic load — the agent translated logic without preserving performance ([eleks: Code Migration with AI](https://eleks.com/expert-opinion/code-migration-with-ai/)).
- **The headline language change is cosmetic.** Bun's Rust port shipped with **13,000+ `unsafe` blocks** vs. 73 in `uv`, a comparable-size project ([byteiota](https://byteiota.com/bun-rust-rewrite-merged-the-13000-unsafe-block-problem/)). The 99.8% pass validates behaviour at the public API, not that the unsafe blocks uphold memory invariants — a migration that nominally bought "memory safety" delivered something softer.
- **Deep platform API integration.** React Native ports of native apps still hit framework limits on heavy GPU work, AR, real-time video, and design-system fidelity — "feature parity becomes a budgeting problem instead of a technical one" ([leanware, 2026](https://www.leanware.co/insights/react-native-vs-native-development)). The agent ports your code, not platform capabilities.
- **Ecosystem network effects are the real lock-in.** Proprietary file formats, package registries, design-system libraries, and certification regimes (SOC2, HIPAA, PCI) survive a rewrite. The Bun port was partly *forced* by the Zig project's April 2026 ban on LLM-authored contributions ([byteiota](https://byteiota.com/bun-rust-rewrite-merged-the-13000-unsafe-block-problem/)) — less voluntary than the framing implies.

The opposing posture — committing irreversibly — is documented in [Burn the Boats](../workflows/burn-the-boats.md). The two are not contradictions; reversibility is a property of the decision you've structured for it.

## What to Invest In Instead

The prerequisites the agent can't manufacture are what a healthy codebase already wants:

- **Behavioural tests over unit tests** — property-based and end-to-end coverage against the contract surface.
- **Contract isolation** — push platform-API calls behind a thin adapter so the retranslation surface stays small.
- **Performance baselines as artefacts** — latency and memory profiles captured as benchmarks the post-migration build must match.

Reversibility is a side effect of these investments, not their goal.

## Decision Checklist

Score each before treating a choice as reversible:

1. Does the test suite cover behaviour, not just lines?
2. Are external contracts stable and documented?
3. Is the platform-API surface < 20% of the codebase?
4. Are non-functional requirements captured as benchmarks?
5. Is the lock-in in source code, or in data formats, certifications, and ecosystem?

A "no" on 1 or 2 means the migration is human-led with agent help, not agent-led.

## Key Takeaways

- Coding-agent reversibility is real but conditional; the binding constraint is behavioural test coverage, not agent capability.
- The Bun Zig→Rust port (6 days, 1M lines, 99.8% tests passing, 13K unsafe blocks) shows both the speed dividend and the quality fine print.
- FreshBrew caps best-in-class agents at 52.3% success on same-language JDK upgrades — cross-language ports against weaker tests do worse.
- Performance, security posture, platform-API behaviour, and ecosystem lock-in survive an agent migration; only behaviourally-tested logic ports cleanly.
- Invest in behavioural tests, contract isolation, and performance baselines if you want to keep the reversibility option open.

## Related

- [Burn the Boats — Commitment-Forcing Deprecation](../workflows/burn-the-boats.md) — the opposing posture: structured irreversibility as a forcing function.
- [LLM Agent Bug Fix Taxonomy](../verification/agent-bug-fix-taxonomy.md) — empirical bug patterns in agent-edited code; relevant when validating post-migration behaviour.
- [Portable Agent Definitions](../standards/portable-agent-definitions.md) — adjacent reversibility shift for agent configuration, not application code.
- [Progressive Autonomy with Model Evolution](progressive-autonomy-model-evolution.md) — how trust in agent output scales with demonstrated reliability, which gates how confidently you can run large migrations.
- [Documentation-Guided Legacy Migration](../workflows/documentation-guided-legacy-migration.md) — the workflow side of agent-driven migration, focused on capturing behaviour before translation.
