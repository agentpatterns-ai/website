---
title: "Acknowledged-Debt Ledger with Next-Trigger Conditions"
description: "Replace ambient TODO comments with a single versioned ledger where every deferred item carries an observable Next Trigger — the event that forces re-evaluation."
tags:
  - instructions
  - workflows
  - tool-agnostic
aliases:
  - tech debt tracker
  - deferred work ledger
  - next-trigger debt log
last_reviewed: 2026-06-02
maturity: adopted
---

# Acknowledged-Debt Ledger with Next-Trigger Conditions

> Replace ambient TODO comments with one versioned ledger where every deferred item carries an observable Next Trigger — the event that forces re-evaluation.

## The Problem

Agents produce TODOs and never act on them. Scattered `TODO` and `FIXME` comments accumulate across files, never indexed, invisible until someone reads the line. Fowler's [technical-debt quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html) distinguishes deliberate debt (logged, justified) from inadvertent — without externalisation, every agent-emitted TODO defaults to inadvertent.

The Acknowledged-Debt Ledger is the deliberate alternative: a single versioned file with one row per deferred item, read at session start, indexed by an observable **Next Trigger**.

## The Six-Column Template

Walkinglabs' harness-engineering template ships this as `docs/exec-plans/tech-debt-tracker.md` with six columns ([source](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/repo-template/docs/exec-plans/tech-debt-tracker.md)):

| Date | Area | Debt | Why Deferred | Risk | Next Trigger |
|------|------|------|--------------|------|--------------|
| 2026-04-12 | `auth` | Verification uses sync SMTP — blocks request thread | Shipping OAuth was the quarter's commit | p95 spikes during signup bursts | `signups/day > 5,000` OR p95 `/auth/register` > 800ms |
| 2026-04-29 | `billing` | Stripe webhook retries in-process | Pre-Series-A scale; queue would be overbuilt | Lost events on deploy | First event-loss incident OR webhook volume > 200/min |

The template's framing — "debt that is real, acknowledged, and intentionally deferred" — is load-bearing. Items without a defensible "Why Deferred" do not belong; rewrite as backlog tickets or fix them.

## The Next-Trigger Discipline

The Next-Trigger column separates the ledger from a passive list. Each trigger must be an observable event that a person, a scheduled scan, or an [entropy-reduction agent](../workflows/entropy-reduction-agents.md) can evaluate mechanically.

| Acceptable | Unacceptable |
|----|----|
| Metric threshold (`p95 > 800ms`, `error_rate > 1%`) | "When we have time" |
| Feature shipping (`when SSO ships`, `when v2 API is GA`) | "Later" |
| Error or volume count (`first webhook drop`, `> 200/min`) | "If it becomes a problem" |
| A date (`2026-09-01`, `next major release`) | "Eventually" |

The acceptable forms are checkable against dashboards, changelogs, log counts, or the calendar. The unacceptable forms defer the trigger definition to the next reader, who will defer again — the ledger collapses back to ambient TODO noise. Enforce the discipline at review time or the pattern is not present.

## Why It Works

Two mechanisms compose:

1. **Single-file determinism.** A ledger in version control at a known path is a deterministic read at session start. "If it is not in version control, it does not exist for agents" ([Lavaee](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/)). Scattered TODOs require the agent to discover them by editing the right file at the right moment; the ledger does not.
2. **Mechanical trigger evaluation.** Each Next Trigger is checkable without prose interpretation. A scheduled scan reads the ledger, evaluates each trigger against current metrics or release state, and lifts fired items into PRs — composing directly with [Entropy Reduction Agents](../workflows/entropy-reduction-agents.md), which already use a `tech-debt-tracker.md` that agents read and update.

The pattern mirrors the [Frozen Spec File](frozen-spec-file.md) — versioned, agent-readable, single-source — applied to deferred work rather than intent.

## Anti-Pattern Boundary

A pile of `TODO:` and `FIXME:` comments scattered through source files is not an Acknowledged-Debt Ledger. The codebase has no central index, no trigger conditions, no expectation that the next agent will act on them. If an agent emits a TODO during work, the next agent should lift it into the ledger (with a Next Trigger) or remove it. A tracker without that lifting discipline is just a second pile.

## When This Backfires

The ledger adds overhead that only pays off under specific conditions. Skip it or treat it as optional when:

- **Greenfield or short-lived projects** — little accumulated debt; the project will be rewritten before triggers fire.
- **No scheduled scan or read-at-session-start discipline** — a ledger nobody reads is worse than scattered TODOs, which at least sit next to the code that needs to change.
- **Solo projects** — the [implicit-knowledge problem](../anti-patterns/implicit-knowledge-problem.md) does not apply when there is no one to externalise to.
- **Bloated entries** — the ETH Zurich AGENTS.md study found overly detailed agent-readable files reduce task success by ~3% and raise cost by >20% ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988), cited in [Shadow Tech Debt](../anti-patterns/shadow-tech-debt.md)). Keep each row short.
- **Concurrent agent writes** — parallel append/resolve without serialisation produces merge conflicts and silently dropped entries.

## Example

A row gets lifted from an ambient TODO into the ledger when its deferral becomes a decision.

**Before — ambient TODO in `src/auth/register.py`:**

```python
# TODO: this SMTP call is sync, fix later
send_verification_email(user.email, token)
```

The comment sits in one file. No index, no trigger, no expected reader.

**After — promoted to `docs/exec-plans/tech-debt-tracker.md`:**

```markdown
| 2026-04-12 | auth | Verification uses sync SMTP — blocks request thread under load | Shipping OAuth was the quarter's commit | p95 latency spikes during signup bursts | signups/day > 5,000 OR p95 /auth/register > 800ms |
```

The code comment can stay or be removed, but the ledger row is now the source of truth. A nightly entropy-reduction scan reads the ledger, checks the trigger against current metrics, and opens a PR when the trigger fires.

## Key Takeaways

- Use the six columns from the template: Date / Area / Debt / Why Deferred / Risk / Next Trigger
- Next Trigger must be observable — a metric threshold, a feature shipping, an error count, or a date
- One canonical location (e.g. `docs/exec-plans/tech-debt-tracker.md`) so the agent reads it deterministically at session start
- Scattered TODO comments are not a ledger — they have no index and no triggers
- The pattern composes with [Entropy Reduction Agents](../workflows/entropy-reduction-agents.md) — scheduled scans evaluate Next Triggers mechanically

## Related

- [Frozen Spec File](frozen-spec-file.md) — sibling pattern: versioned, agent-readable, single-source — applied to intent rather than deferred work
- [Entropy Reduction Agents](../workflows/entropy-reduction-agents.md) — scheduled scans that evaluate Next Triggers and open PRs when they fire
- [The Implicit Knowledge Problem](../anti-patterns/implicit-knowledge-problem.md) — version-controlled decision artifacts beat tribal knowledge
- [Shadow Tech Debt](../anti-patterns/shadow-tech-debt.md) — the failure mode the ledger mitigates
- [Background Todo Agent](../agent-design/background-todo-agent.md) — within-session plan maintenance; the ledger is the cross-session companion
- [Feature List Files](feature-list-files.md) — structured tracking for in-flight features alongside deferred debt
