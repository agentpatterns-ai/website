---
title: "Agent Readiness: Bootstrap and Audit Runbooks for Real Codebases"
description: "Operational runbooks an agent can execute against any codebase to bootstrap missing infrastructure, audit existing setups, and score holistic agent readiness against the L0–L5 ladder."
tags:
  - tool-agnostic
  - workflows
  - instructions
aliases:
  - agent readiness library
  - agent readiness framework
  - bootstrap and audit runbooks
---

# Agent Readiness

> Operational runbooks an agent can execute end-to-end against any codebase — bootstrap missing infrastructure, audit existing setups, and score holistic agent readiness.

This section is the **entry point for an agent operating on an unfamiliar codebase**. Every page below is a self-sufficient runbook: detection commands, file templates, decision rules, validation steps, and output schemas. Pointed at a repository, an agent should be able to read one of these pages and complete the work without further research.

The principles and templates apply to any AI coding harness. The deeper detection scripts and config schemas are **shaped for Claude Code today** — paths like `.claude/settings.json`, `.claude/hooks/`, `.claude/skills/`, and the `mcp.json` schema. Cursor, Aider, Copilot, and Gemini surfaces are detected at the inventory layer (so the assess scorecard accounts for them), but parallel rubrics and config templates per harness are a follow-up — see [Status](#status). Background theory lives in the `docs/` sections each runbook links to; the runbooks themselves are operational.

## How an Agent Uses This Library

If you are an AI coding agent that has been pointed at this page, first decide the mode.

### Mode Selection

**Interactive (default)** — the user opened a session with you ("follow the instructions on https://agentpatterns.ai/agent-readiness/", "run the agent readiness assessment", etc.). Narrate each step, surface findings as you go, pause at the punch list, and confirm before applying any bootstrap.

**Autonomous** — the user explicitly opted out of interaction ("non-interactively", "autonomously", "headless", "no questions", invoked from CI or a scheduled job). Run the full loop, apply what is safe to apply unattended, defer the rest to a backlog, and emit a single end-of-run report.

When the signal is ambiguous, default to interactive and ask one clarifying question.

### Interactive Flow

1. **Open** with one paragraph: what the assessment does, that you will not change files without asking, rough scope.
2. **Assess** — run [`assess-agent-readiness`](assess-agent-readiness.md), narrating each phase ("inventorying instruction surfaces", "auditing AGENTS.md against pointer-map rules") and surfacing findings live, not only at the end.
3. **Halt on safety** — a high finding from [`audit-secrets-in-context`](audit-secrets-in-context.md) stops everything; walk the user through rotation before any other work.
4. **Present the punch list** — show the prioritized table; ask which items to apply now, defer, or skip.
5. **Apply each chosen bootstrap one at a time** — explain what will change, list the files involved, apply, then re-run the matching audit and report the dimension uplift. Confirm before destructive ops (deletions, force-pushes, history rewrites) regardless of prior approvals.
6. **Close** with a delta report (see [`assess-agent-readiness`](assess-agent-readiness.md) §Re-Run) and the list of deferred items.

### Autonomous Flow

1. **Assess** — run [`assess-agent-readiness`](assess-agent-readiness.md) end-to-end, no commentary.
2. **Halt on safety** — any high finding from [`audit-secrets-in-context`](audit-secrets-in-context.md) or a `(1,1,1)` principal in [`audit-lethal-trifecta`](audit-lethal-trifecta.md) aborts the run; emit only that finding.
3. **Auto-apply safe-by-construction items only** — pure additions where no file exists (greenfield [`bootstrap-llms-txt`](bootstrap-llms-txt.md), default-deny [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md), [`bootstrap-hooks-scaffold`](bootstrap-hooks-scaffold.md)), template scaffolds with no merge required, and config edits with punch-list `ease ≥ 4` and `severity ≥ 3`. Anything that mutates user content, requires user-supplied context (incidents, gotchas, project conventions), or is destructive is deferred.
4. **File backlog items** — for each deferred runbook, file an issue in the project's tracker using whatever tooling you have available (GitHub via `gh`, Linear, Jira, etc., detected from the repo configuration or your own MCP/tool surface). If no tracker is reachable, append to `agent-readiness-backlog.md` at the repo root. One item per runbook, including the punch-list score, the dimension uplift it would deliver, and the reason it was deferred.
5. **Emit the report** — the standard scorecard plus an "Applied / Deferred" split and pointers to the filed issues or backlog file.

### Single-Page Invocation

If the user pointed you at a single runbook ("audit our AGENTS.md"), skip the assessment and run that page directly. Mode still applies: narrate interactively, or run silently and emit one report autonomously.

## Operating Principles

- **No invention**: every command, template, and rule cites or matches the existing docs/ source page. Do not generate a template the runbook does not specify.
- **Detect before write**: every bootstrap runbook detects the current state first; never overwrite without reading.
- **Idempotency**: every runbook can be re-run safely. Re-runs produce no diff when the codebase is already compliant.
- **Default-deny on destructive ops**: deletions, force-pushes, and history rewrites require explicit user confirmation, not just an agent decision.
- **Stop on uncertainty**: when the runbook's decision rules don't cover the situation, surface the question to the user rather than guessing.

## Library Layout

| Type | Purpose | Pages |
|------|---------|-------|
| **Assess** | Holistic L0–L5 scoring; produces the punch list | 1 |
| **Bootstrap** | Generate or scaffold missing artifacts | 11 |
| **Audit** | Check existing artifacts; report findings | 9 |

Every audit has a paired bootstrap. Run the audit to find the gaps; run the bootstrap to close them.

### Assess

- [`assess-agent-readiness`](assess-agent-readiness.md) — Score across instructions, harness, security, verification; output the punch list

### Bootstrap

| Runbook | Closes the gap from |
|---------|---------------------|
| [`bootstrap-agents-md`](bootstrap-agents-md.md) — root + subdirectory `AGENTS.md` | [`audit-agents-md`](audit-agents-md.md) |
| [`bootstrap-llms-txt`](bootstrap-llms-txt.md) — `/llms.txt` and `/llms-full.txt` | (no audit; greenfield) |
| [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md) — default-deny `.claude/settings.json` | [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) |
| [`bootstrap-egress-policy`](bootstrap-egress-policy.md) — host allowlist + trifecta decomposition | [`audit-lethal-trifecta`](audit-lethal-trifecta.md) |
| [`bootstrap-mcp-config`](bootstrap-mcp-config.md) — `.mcp.json` with per-server scope | [`audit-tool-descriptions`](audit-tool-descriptions.md), [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) |
| [`bootstrap-hooks-scaffold`](bootstrap-hooks-scaffold.md) — `.claude/hooks/` stubs for every event | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) — Stop-event verification gate | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) — edit-count loop detector | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-tool-descriptions`](bootstrap-tool-descriptions.md) — rewrite tool descriptions to spec | [`audit-tool-descriptions`](audit-tool-descriptions.md) |
| [`bootstrap-skill-template`](bootstrap-skill-template.md) — opinionated `SKILL.md` skeleton | [`audit-skill-quality`](audit-skill-quality.md) |
| [`bootstrap-eval-suite`](bootstrap-eval-suite.md) — `evals/` with paired baseline/with-skill runner | (no audit; greenfield) |

### Audit

- [`audit-agents-md`](audit-agents-md.md) — `AGENTS.md` against pointer-map rules
- [`audit-claude-md`](audit-claude-md.md) — `CLAUDE.md` and equivalents
- [`audit-instruction-rule-budget`](audit-instruction-rule-budget.md) — Cross-file rule count vs ~150 ceiling
- [`audit-skill-quality`](audit-skill-quality.md) — `SKILL.md` description craft, gotchas, CLI-first body
- [`audit-tool-descriptions`](audit-tool-descriptions.md) — Tool / MCP description quality
- [`audit-hooks-coverage`](audit-hooks-coverage.md) — Lifecycle event coverage
- [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) — Allow/deny lists, sandboxing
- [`audit-secrets-in-context`](audit-secrets-in-context.md) — Live credentials in agent-readable files
- [`audit-lethal-trifecta`](audit-lethal-trifecta.md) — Per-agent map of private data + untrusted content + egress

## Status

These pages are **specifications and runbooks**. They are written so an agent can execute them today using common tools (bash, grep, jq, python). The pages are the source of truth.

Two follow-ups are scoped but not done in this iteration:

- **Promotion to packaged skills** under `.claude/skills/agent-readiness/` (or another tool's equivalent) so the runbooks are description-matched at session start, not URL-pointed by a human
- **Parallel rubrics and config templates per harness** (Cursor, Aider, Copilot) — today the inventory detects them, but the deeper checks and bootstrap templates are Claude-Code-shaped

## Related

- [Brownfield-to-Agent-First Maturity](../frameworks/brownfield-to-agent-first/index.md)
- [AGENTS.md Standard](../standards/agents-md.md)
- [Harness Engineering](../agent-design/harness-engineering.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
