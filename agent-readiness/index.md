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

The pages are tool-agnostic and apply to any codebase, not just this one. Background theory lives in the `docs/` sections each runbook links to; the runbooks themselves are operational.

## How an Agent Uses This Library

If you are an AI coding agent that has been pointed at this page, follow this sequence:

1. **Establish baseline**: open [`assess-agent-readiness`](assess-agent-readiness.md) and run the inventory + scoring steps. Output the L0–L5 scorecard.
2. **Resolve safety first**: if the scorecard flags any high-severity finding from [`audit-secrets-in-context`](audit-secrets-in-context.md) or [`audit-lethal-trifecta`](audit-lethal-trifecta.md), stop other work and remediate.
3. **Apply the punch list in order**: the scorecard prioritizes by `(severity × ease)`. Open each named runbook and execute it.
4. **Validate**: after each runbook, re-run [`assess-agent-readiness`](assess-agent-readiness.md). Confirm the targeted dimension's level moved.
5. **Report**: emit a final markdown summary with before/after scores, files created, files changed, and any work that requires human approval.

If the user has pointed you at a single page (e.g. "audit our AGENTS.md"), skip the assessment and go directly to that runbook.

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
| **Bootstrap** | Generate or scaffold missing artifacts | 5 |
| **Audit** | Check existing artifacts; report findings | 9 |

### Assess

- [`assess-agent-readiness`](assess-agent-readiness.md) — Score across instructions, harness, security, verification; output the punch list

### Bootstrap

- [`bootstrap-agents-md`](bootstrap-agents-md.md) — Generate root and subdirectory `AGENTS.md`
- [`bootstrap-llms-txt`](bootstrap-llms-txt.md) — Generate `/llms.txt` and `/llms-full.txt`
- [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) — Scaffold a Stop-event verification gate
- [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) — Scaffold an edit-count loop detector
- [`bootstrap-eval-suite`](bootstrap-eval-suite.md) — Scaffold `evals/` with paired baseline/with-skill runner

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

These pages are **specifications and runbooks**. They are written so an agent can execute them today using common tools (bash, grep, jq, python). Promotion to packaged `SKILL.md` files under `.claude/skills/` (or another tool's equivalent) is a follow-up; the pages are the source of truth in either form.

## Related

- [Brownfield-to-Agent-First Maturity](../frameworks/brownfield-to-agent-first/index.md)
- [AGENTS.md Standard](../standards/agents-md.md)
- [Harness Engineering](../agent-design/harness-engineering.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
