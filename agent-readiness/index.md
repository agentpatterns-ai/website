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

## Assumptions

Three things shape what these runbooks expect of the project they run against. Read before applying — if any assumption is wrong for your project, translate or skip.

### Harness

Templates, paths, and config schemas are **shaped for Claude Code today** — `.claude/settings.json`, `.claude/hooks/`, `.claude/skills/`, `.mcp.json`. The principles transfer to Cursor, Aider, Copilot, and Gemini, but the file locations and config formats differ. The inventory step in [`assess-agent-readiness`](assess-agent-readiness.md) detects those harnesses; parallel rubrics and config templates per harness are a follow-up — see [Known limitations](#known-limitations). When applying a runbook on a non-Claude-Code project, treat the templates as shape — adapt paths and schemas to your harness's equivalents.

### Platform

Detection scripts use bash + `find` + `jq` + `yq` + `python3`. Windows users should run the runbooks under WSL or Git Bash. PowerShell-only environments will need to translate the commands. Hooks and CI templates assume a Unix-shell runtime.

### Applicability

Not every runbook applies to every project:

- [`bootstrap-llms-txt`](bootstrap-llms-txt.md) is for projects that publish a documentation site or external API reference. Internal-only repos with no public docs should skip it.
- [`bootstrap-eval-suite`](bootstrap-eval-suite.md) needs an agent-customizable unit (skill, sub-agent, or system prompt fragment) to measure. A project with none yet has nothing to evaluate — defer until one ships.
- [`bootstrap-mcp-config`](bootstrap-mcp-config.md) is for projects that connect to external services through MCP. Skip if the agent talks only to the local filesystem and the user.
- [`bootstrap-egress-policy`](bootstrap-egress-policy.md) and [`audit-lethal-trifecta`](audit-lethal-trifecta.md) become load-bearing once an agent reads private data **and** processes untrusted input **and** has egress. Single-leg agents pass these by construction.

The `assess` runbook flags inapplicable pages instead of failing them. Background theory lives in the `docs/` sections each runbook links to; the runbooks themselves are operational.

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
4. **File backlog items** — for each deferred runbook, file an issue in the project's tracker using whatever tooling you have available (GitHub via `gh`, Linear, Jira, etc., detected from the repo configuration or your own MCP/tool surface). If no tracker is reachable, append to `agent-readiness-backlog.md` at the repo root (a sidecar file this runbook creates if absent — rename to match the project's existing convention if one exists). One item per runbook, including the punch-list score, the dimension uplift it would deliver, and the reason it was deferred.
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
| **Bootstrap** | Generate or scaffold missing artifacts | 22 |
| **Audit** | Check existing artifacts; report findings | 26 |

Every audit has a paired bootstrap. Run the audit to find the gaps; run the bootstrap to close them.

### Assess

- [`assess-agent-readiness`](assess-agent-readiness.md) — Score across instructions, harness, security, verification; output the punch list

### Bootstrap

| Runbook | Closes the gap from |
|---------|---------------------|
| [`bootstrap-agents-md`](bootstrap-agents-md.md) — root + subdirectory `AGENTS.md` | [`audit-agents-md`](audit-agents-md.md) |
| [`bootstrap-llms-txt`](bootstrap-llms-txt.md) — `/llms.txt` and `/llms-full.txt` | (no audit; greenfield) |
| [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md) — default-deny `.claude/settings.json` | [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) |
| [`bootstrap-evidence-based-allowlist`](bootstrap-evidence-based-allowlist.md) — `PermissionRequest` + `PostToolUse` hooks promoting Bash commands to allow rules after N successful approvals, with hard-deny list | (extends `bootstrap-permissions-allowlist`) |
| [`bootstrap-egress-policy`](bootstrap-egress-policy.md) — host allowlist + trifecta decomposition | [`audit-lethal-trifecta`](audit-lethal-trifecta.md) |
| [`bootstrap-mcp-config`](bootstrap-mcp-config.md) — `.mcp.json` with per-server scope | [`audit-tool-descriptions`](audit-tool-descriptions.md), [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) |
| [`bootstrap-hooks-scaffold`](bootstrap-hooks-scaffold.md) — `.claude/hooks/` stubs for every event | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) — Stop-event verification gate | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) — edit-count loop detector | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| [`bootstrap-tool-descriptions`](bootstrap-tool-descriptions.md) — rewrite tool descriptions to spec | [`audit-tool-descriptions`](audit-tool-descriptions.md) |
| [`bootstrap-skill-template`](bootstrap-skill-template.md) — opinionated `SKILL.md` skeleton | [`audit-skill-quality`](audit-skill-quality.md) |
| [`bootstrap-eval-suite`](bootstrap-eval-suite.md) — `evals/` with paired baseline/with-skill runner | [`audit-eval-suite`](audit-eval-suite.md) |
| [`bootstrap-incident-to-eval`](bootstrap-incident-to-eval.md) — incident → regression eval pipeline with P0/P1/P2 CI gate | (extends `bootstrap-eval-suite`) |
| [`bootstrap-subagent-template`](bootstrap-subagent-template.md) — opinionated sub-agent skeleton with scoped tools, isolation, injection guard | [`audit-subagent-definitions`](audit-subagent-definitions.md), [`audit-handoff-protocols`](audit-handoff-protocols.md) |
| [`bootstrap-plan-mode`](bootstrap-plan-mode.md) — plan-mode default + plan-review checklist + CI flag wiring | (no audit; configuration) |
| [`bootstrap-tool-test-harness`](bootstrap-tool-test-harness.md) — per-tool isolated selection / parameter / output tests with CI gate | (extends `bootstrap-eval-suite`) |
| [`bootstrap-frozen-spec-file`](bootstrap-frozen-spec-file.md) — SPEC.json + PreToolUse hook + re-read directive that survives compaction | (no audit; configuration) |
| [`bootstrap-otel-init`](bootstrap-otel-init.md) — Claude Code OTel exporter, metrics, and tool-decision events with reachability smoke test | [`audit-debug-log-retention`](audit-debug-log-retention.md) |
| [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md) — wrap `WebFetch` with a public-web index check (Common Crawl); default-deny in headless mode | [`audit-lethal-trifecta`](audit-lethal-trifecta.md), [`audit-mcp-control-plane-bypass`](audit-mcp-control-plane-bypass.md) |
| [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md) — CODEOWNERS + branch protection for tiered AI/human review on agent-authored PRs | (no audit; configuration) |
| [`bootstrap-reasoning-execution-routing`](bootstrap-reasoning-execution-routing.md) — per-role model routing (frontier for reasoning, fast/cheap for execution) with pinned model IDs and OTel smoke-test | (no audit; configuration) |
| [`bootstrap-agent-commit-attribution`](bootstrap-agent-commit-attribution.md) — dedicated signing key, structured trailers, branch-protection rule, and rotation playbook | [`audit-agent-built-code-health`](audit-agent-built-code-health.md), [`audit-agent-pr-quality-metrics`](audit-agent-pr-quality-metrics.md) |

### Audit

- [`audit-agents-md`](audit-agents-md.md) — `AGENTS.md` against pointer-map rules
- [`audit-claude-md`](audit-claude-md.md) — `CLAUDE.md` and equivalents
- [`audit-instruction-rule-budget`](audit-instruction-rule-budget.md) — Cross-file rule count vs ~150 ceiling
- [`audit-instruction-placement`](audit-instruction-placement.md) — Critical rules in primacy/recency, mid-file flags, contradictory restatements
- [`audit-skill-quality`](audit-skill-quality.md) — `SKILL.md` description craft, gotchas, CLI-first body
- [`audit-tool-descriptions`](audit-tool-descriptions.md) — Tool / MCP description quality (incl. ToolLeak signatures)
- [`audit-tool-error-format`](audit-tool-error-format.md) — RFC 9457 problem+json compliance and token cost on tool error responses
- [`audit-tool-idempotency`](audit-tool-idempotency.md) — MCP `idempotentHint` / `destructiveHint` / `readOnlyHint` annotation hygiene and retry-safety
- [`audit-tool-output-token-cost`](audit-tool-output-token-cost.md) — Per-tool output sizing measured from real invocations; band classification and pagination remediations
- [`audit-hooks-coverage`](audit-hooks-coverage.md) — Lifecycle event coverage
- [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) — Allow/deny lists, sandboxing
- [`audit-secrets-in-context`](audit-secrets-in-context.md) — Live credentials in agent-readable files
- [`audit-lethal-trifecta`](audit-lethal-trifecta.md) — Per-agent map of private data + untrusted content + egress
- [`audit-rules-files-injection`](audit-rules-files-injection.md) — Rules and instruction files scanned for injection markers, classified by trust tier
- [`audit-subagent-definitions`](audit-subagent-definitions.md) — Sub-agent frontmatter, tools tightness, local trifecta, isolation
- [`audit-slash-command-catalog`](audit-slash-command-catalog.md) — Model-invocable command surface, side-effect gates, listing budget
- [`audit-handoff-protocols`](audit-handoff-protocols.md) — Multi-agent output schema declarations, raw-transcript forwarding, uncertainty preservation
- [`audit-fan-out-capacity`](audit-fan-out-capacity.md) — Parallel dispatch sites validated against rate-limit tier, cost budget, staggering, and wait-for-all semantics
- [`audit-eval-suite`](audit-eval-suite.md) — Eval scaffold completeness, case provenance, idle-state / build-parity / per-model ablation, judge-calibration coverage
- [`audit-premature-completion`](audit-premature-completion.md) — Test suite run pre/post each agent PR; classification on the fixed-correct-code / failing-tests-remain matrix
- [`audit-debug-log-retention`](audit-debug-log-retention.md) — Persisted log surfaces, secret redaction, backend-side processor rules, retention bounds, default-off posture
- [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md) — Consequential-action coverage, gate-decision log fidelity, alert-fatigue indicators, Lies-in-the-Loop dialog rendering, headless-pipeline posture
- [`audit-mcp-control-plane-bypass`](audit-mcp-control-plane-bypass.md) — Off-protocol egress paths (shell, raw HTTP, DB drivers, headless browser, in-thread side-channels), skipped-plane clients, argument-blind policies
- [`audit-action-audit-divergence`](audit-action-audit-divergence.md) — F1-F4 divergence taxonomy walked against the runtime; chokepoint, integrity mechanism, liveness probe, and target validator named or flagged
- [`audit-trojan-hippo-memory`](audit-trojan-hippo-memory.md) — Long-term memory write surfaces classified by source-trust; trifecta-leg removal validated; cross-session `(1,1,1)` pivot flagged that per-session trifecta audits miss
- [`audit-agent-built-code-health`](audit-agent-built-code-health.md) — Inventory of agent-authored files, structural-complexity ratio vs repo baseline, single-impl factories, refactoring share, shadow utilities, ADR compliance
- [`audit-agent-pr-quality-metrics`](audit-agent-pr-quality-metrics.md) — Agent PR merge rate, comment volume, conflict rate, post-merge defect rate, and force-push during review against AIDev/AgenticFlict/Beyond-Bug-Fixes baselines; task-routing fit per agent class
- [`audit-pr-narrative-quality`](audit-pr-narrative-quality.md) — Issue specs, PR descriptions, and commit messages on agent-authored PRs scored for visible-thinking discipline; section coverage, issue-as-spec, force-push, generic branch names

## Known limitations

These pages are **specifications and runbooks** — written so an agent can execute them with bash, `jq`, and `python` available. The pages themselves are the source of truth.

One known limitation:

- **Templates are Claude-Code-shaped.** The runbooks ship as packaged Claude Code skills under `.claude/skills/agent-readiness-*` so the harness can description-match them at session start. The inventory step detects Cursor, Aider, Copilot, and Gemini, but the deeper checks and bootstrap templates use Claude Code paths and config schemas. The [Harness Translation Reference](harness-translation.md) maps the main concepts (instruction files, MCP config, lifecycle events, skills, sub-agents) to their equivalents per harness, with primary-source citations and explicit gaps where parallel features don't yet exist.

## Related

- [Brownfield-to-Agent-First Maturity](../frameworks/brownfield-to-agent-first/index.md)
- [AGENTS.md Standard](../standards/agents-md.md)
- [Harness Engineering](../agent-design/harness-engineering.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
