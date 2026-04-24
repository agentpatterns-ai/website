---
title: "Plan Files as Resumable Artifacts"
description: "Committed plan files externalise agent state across sessions — a qualified pattern that pays for multi-session, recurring, or cross-functional work and backfires without a supersession discipline."
tags:
  - context-engineering
  - workflows
  - human-factors
  - tool-agnostic
---

# Plan Files as Resumable Artifacts

> A plan committed to the repo is a resumable, version-controlled artifact — a pattern that holds for multi-session work, recurring workflows, and cross-functional review, and backfires without a supersession discipline.

## What a Persisted Plan File Is

A *persisted* plan lives in the repo at a stable path, tracked in git — mutable companion to the [frozen spec](../../instructions/frozen-spec-file.md): the spec fixes goals and done-when, the plan tracks approach and progress. Claude Code's in-session plan mode defaults `plansDirectory` to `~/.claude/plans` — outside the repo ([Claude Code settings](https://code.claude.com/docs/en/settings)). Checking the plan in turns session memory into a team-visible hand-off.

## When It Pays

The pattern is **qualified**. Treat these as prerequisites:

- **Multi-session work.** The plan externalises state the context window cannot retain ([Anthropic harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).
- **Recurring workflows with template value.** Stulberg reports that reusing plan files lets the next run "start at 80% done" ([Aakash x Stulberg](https://www.news.aakashg.com/p/claude-code-team-os)).
- **Cross-functional review.** When a PM, designer, or domain expert must approve the approach, the plan PR is the review surface ([transcript](https://www.aakashg.com/hannah-stulberg-podcast/)).

Outside these conditions, a disposable in-session plan is cheaper.

## Three Canonical Shapes

No single convention has won. Three are in active use:

- **Ralph single-root.** One `IMPLEMENTATION_PLAN.md` at the repo root; one task per iteration, one commit per update. The author "throws it out often" — durability is not the goal ([Huntley](https://ghuntley.com/ralph/); [how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum)).
- **Codex `.agent/PLANS.md`.** Referenced from `AGENTS.md`, with the invariant that "it should always be possible to restart from only the ExecPlan." The plan is "fully self-contained" — progress, decision log, surprises, outcomes ([Codex cookbook](https://developers.openai.com/cookbook/articles/codex_exec_plans)).
- **Manus tripartite.** Split across `task_plan.md`, `findings.md`, `progress.md`. Rewriting the todo list "recites objectives into the end of the context" — the plan doubles as attention bias ([Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus); [planning-with-files](https://github.com/OthmanAdi/planning-with-files)).

Pick by team size: Ralph for solo iteration, Codex for long-horizon runs, Manus for phase/findings separation.

## Resumption Mechanic

The next session reads the plan as context — it does not reconstruct reasoning. Anthropic frames resumption as "engineers working in shifts, where each new engineer arrives with no memory of what happened on the previous shift": read git log and progress files, then pick the highest-priority unfinished feature ([Anthropic harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)). In Claude Code, accepting a plan auto-names the session from its content, tying `claude --resume <name>` to the artifact ([common workflows](https://code.claude.com/docs/en/common-workflows)). Filesystem plays disk; context window plays RAM ([planning-with-files](https://github.com/OthmanAdi/planning-with-files)).

## The Supersession Discipline

Persistence without invalidation is actively harmful. Claude Code issue [#13740](https://github.com/anthropics/claude-code/issues/13740) reports plan mode "repeatedly displaying stale plans" instead of fresh analysis; Cursor generates [dozens of `.plan.md` snapshots per plan](https://forum.cursor.com/t/plan-mode-creates-many-plan-md-snapshots-in-home-user-cursor-plans-for-a-single-plan-2-2-36-linux/146772). Make supersession first-class:

- Archive completed plans under a dated path; do not leave them active.
- Use `supersedes:` / `superseded-by:` frontmatter for a machine-readable chain.
- Add a CI staleness check that fails when a plan references missing code paths.
- Treat drift as a pager event — Prassanna's "chain-of-thought that was correct at turn ten becomes actively misleading at turn sixty" applies to persisted plans ([Agent Drift](https://prassanna.io/blog/agent-drift/)).

## When NOT to Use

- **Single-session work inside one context window.** The PR round-trip is pure latency; regenerate per-task instead.
- **Teams without an invalidation discipline.** The plan becomes a retrieval hazard — outdated context creates mismatches the agent may rationalise rather than surface ([Tacnode](https://tacnode.io/post/your-ai-agents-are-spinning-their-wheels)).
- **High-churn exploratory sessions.** A speculative plan written before investigation is always wrong.
- **Regulated domains.** A committed plan is a discoverable record — in legal, HR, or finance it may surface pre-decisional reasoning the team did not intend to preserve.

## Example

A Codex-shape plan at `.agent/PLANS.md`, referenced from `AGENTS.md`:

```markdown
# Plan: Migrate auth to OIDC

## Goals (frozen — see SPEC.json)
- Replace password auth with Auth0 OIDC on /login and /signup.
- Preserve existing session cookies during rollout.

## Phases
- [x] Phase 1: Add Auth0 provider, feature-flagged off.
- [ ] Phase 2: Dual-write sessions from OIDC callback.
- [ ] Phase 3: Flip flag for 10% of traffic, monitor error budget.

## Decision Log
- 2026-04-09: Chose Auth0 over Cognito — existing SSO contract.
- 2026-04-11: Kept legacy cookie name to avoid client churn.

## Surprises
- `/api/v1/me` implicitly depended on the password hash in the session blob.

## Next Action
Implement Phase 2 callback handler in `auth/oidc.ts`.
```

The self-contained invariant holds: a fresh session can resume from this file alone.

## Key Takeaways

- The persisted plan is a mutable, version-controlled artifact — the companion to the frozen spec, not a replacement for in-session plan mode.
- The pattern pays for multi-session, recurring, or cross-functional work and costs negative value for single-session or undisciplined teams.
- Pick a shape (Ralph, Codex, or Manus) by team size and review surface; none has won.
- Supersession discipline is non-negotiable — stale plans are more dangerous than missing ones.

## Related

- [Plan mode as a knowledge artifact](plan-mode-knowledge-artifacts.md) — the posture half of the pair; this page is the persisted artifact
- [Plan mode](../../workflows/plan-mode.md) — the in-session thinking posture
- [Plan-first loop](../../workflows/plan-first-loop.md) — the general workflow the artifact is written into
- [Frozen spec file](../../instructions/frozen-spec-file.md) — the immutable sibling that fixes goals and done-when
- [Trajectory logging and progress files](../../observability/trajectory-logging-progress-files.md) — the status companion read on resumption
- [Context compression strategies](../../context-engineering/context-compression-strategies.md) — what the plan file survives
- [Team OS](index.md) — the framework this module composes into
