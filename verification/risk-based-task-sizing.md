---
title: "Risk-Based Task Sizing for Agent Verification Depth"
description: "Scale verification effort to match task risk — trivial changes get quick checks, high-risk changes get multi-model adversarial review and human approval gates"
aliases:
  - Risk-Based Verification
  - Verification Depth Scaling
tags:
  - testing-verification
  - agent-design
---

# Risk-Based Task Sizing for Agent Verification Depth

> Scale verification effort to match task risk — trivial changes get quick checks, high-risk changes get multi-model adversarial review and human approval gates.

## The Problem

Most agent workflows apply uniform verification: every change runs the same checks regardless of whether it touches a comment or an auth module. Low-risk changes waste cycles; high-risk changes pass with insufficient scrutiny because the bar was set for average tasks.

## File Risk Classification

The [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) classifies files into three risk tiers based on what they control:

| Tier | Scope | Examples |
|------|-------|---------|
| Low | Additive, no behavioral change | New tests, documentation, config comments |
| Medium | Existing behavior modified | Business logic, function signatures, database queries, UI state |
| High | Security or data integrity surface | Auth, crypto, payments, data deletion, schema migrations, public API |

The classification is static per file — determined by what the file controls, not by what the current change does to it. A one-line change to an authentication module is still high-risk because the [blast radius](../security/blast-radius-containment.md) of a mistake in that file is large.

## Task Sizing

Task size combines scope and file risk:

| Size | Verification | Review |
|------|-------------|--------|
| Small | IDE diagnostics + syntax check only | None |
| Medium | Full verification cascade + structured ledger | 1 reviewer |
| Large | Full cascade + operational readiness checks | 3 cross-model reviewers + human gate |

The [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) applies a critical escalation rule: high-risk files auto-escalate to Large regardless of task scope. A typo fix in a payments module triggers the full verification pipeline because the file's risk tier overrides the task's apparent simplicity.

The default heuristic is "if unsure, treat as Medium" — this errs toward more verification rather than less.

## Verification Cascade

Verification is tiered with fallback layers:

1. **IDE diagnostics** — always run on changed files and their importers
2. **Syntax/parse check** — the file must parse without errors
3. **Build/compile** — run if build tooling exists
4. **Type checker** — run on changed files
5. **Linter** — run on changed files only
6. **Test suite** — full suite or relevant subset
7. **Import/load test** — verify the module loads without crashing (fallback when tiers 3-6 produce no runtime signal)
8. **Smoke execution** — a throwaway script exercising the changed code path (fallback when no other runtime verification exists)

The [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) requires that if tiers 1-6 yield only static checks with no runtime verification, at least one tier 7-8 check must run. Empty runtime verification is never acceptable.

## Structured Verification Ledger

Every verification step is recorded as structured data — an INSERT, not prose. The evidence bundle presented to the developer is a SELECT query, not a self-reported summary. This prevents hallucinated verification: if the INSERT did not happen, the check did not happen. See [Verification Ledger](verification-ledger.md) for the full pattern.

The ledger captures baseline state before changes and post-change state, enabling regression detection by comparing the two phases programmatically.

## When This Backfires

Risk-tier systems inherit the weaknesses of [risk-based testing](https://en.wikipedia.org/wiki/Risk-based_testing): assignment is subjective, classifications drift, and focus on high-risk paths can leave low-risk areas under-tested. Specific conditions where this pattern underperforms uniform verification:

- **Tier drift after refactors.** Static per-file tiers assume file purpose is stable. A tests helper that accretes production code over six months may still be tagged Low. Teams routinely stop updating risk matrices once maintenance cost exceeds perceived benefit ([TestRail, "Pros and Cons of Risk-Based Testing"](https://www.testrail.com/blog/risk-based-testing/)).
- **Subjective classification.** Two engineers can reasonably disagree whether a billing calculator is "business logic" (Medium) or "data integrity surface" (High). Without a rubric enforced in review, tier assignments become inconsistent and create a false sense of rigor ([Technology.org, "Benefits and disadvantages of risk-based testing"](https://www.technology.org/2024/05/22/benefits-and-disadvantages-of-risk-based-testing/)).
- **High-risk-file fatigue.** Auto-escalating every touch of an auth file to Large review discourages defensible small improvements — typo fixes, comment updates, dead-code removal. Teams route around the policy by avoiding the file.
- **Low-tier blind spots.** Concentrating verification on High-tier files under-weights defects from interactions between Low-tier modules. A documentation change that silently invalidates a runbook can cause an incident the tiered cascade never catches.

If the risk map is not reviewed regularly, or the team lacks a shared rubric for the tier boundaries, uniform verification may be more honest than a stale tier map masquerading as risk awareness.

## Key Takeaways

- Classify files by what they control (data integrity, security surface), not by change size
- High-risk files auto-escalate verification regardless of apparent task simplicity
- Default to Medium when uncertain — over-verification is cheaper than missed defects
- Tier verification with fallbacks so every change gets at least one runtime signal
- Record verification as structured data, not prose — queryable evidence over self-reported claims

## Example

A coding agent receives a task: "Add a `--dry-run` flag to the deploy CLI command." The agent identifies the changed files and classifies each:

| File | Risk Tier | Reason |
|------|-----------|--------|
| `cli/deploy.py` | High | Controls production deployment — data integrity surface |
| `cli/flags.py` | Medium | Modifies existing CLI argument parsing |
| `tests/test_deploy.py` | Low | Additive test — no behavioral change |

The highest file risk is High, so the task auto-escalates to Large regardless of the change's apparent simplicity. The agent runs the full verification cascade:

```
✓ Tier 1 — IDE diagnostics: 0 errors in deploy.py, flags.py, test_deploy.py
✓ Tier 2 — Syntax check: all files parse
✓ Tier 3 — Build: `pip install -e .` succeeds
✓ Tier 4 — Type checker: `mypy cli/ tests/` passes
✓ Tier 5 — Linter: `ruff check cli/ tests/` clean
✓ Tier 6 — Tests: `pytest tests/test_deploy.py` — 14 passed, 0 failed
```

Tiers 3-6 produced runtime signal, so tiers 7-8 are skipped. The agent records each result as a structured ledger entry and routes the change to three cross-model reviewers plus a human approval gate — the full Large-task pipeline.

If the same task only touched `tests/test_deploy.py` (Low tier), it would stay Small: IDE diagnostics, syntax check, no review required.

## Related

- [Incremental Verification: Check at Each Step](incremental-verification.md)
- [Heuristic-Based Effort Scaling](../agent-design/heuristic-effort-scaling.md)
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md)
- [Committee Review Pattern](../code-review/committee-review-pattern.md)
- [Delegation Decision](../agent-design/delegation-decision.md)
- [Risk-Based Shipping](risk-based-shipping.md)
- [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md)
