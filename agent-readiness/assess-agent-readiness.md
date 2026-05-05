---
title: "Assess Agent Readiness"
description: "Inventory a codebase, run the audit suite in parallel, score L0–L5 across four dimensions, and emit a prioritized punch list of bootstrap and audit work."
tags:
  - tool-agnostic
  - workflows
  - agent-design
aliases:
  - agent readiness scorecard
  - L0 to L5 maturity audit
  - brownfield agent assessment
---

Packaged as: [`.claude/skills/agent-readiness-assess-agent-readiness`](../../.claude/skills/agent-readiness-assess-agent-readiness/SKILL.md)

# Assess Agent Readiness

> Inventory the codebase, run the audit suite, score L0–L5 across four dimensions, and emit a prioritized punch list.

!!! info "Harness assumption"
    Inventory paths and config schemas in this runbook target Claude Code. Cursor, Aider, Copilot, and Gemini surfaces are detected at the inventory layer but scored against the same rubric — adapt the deeper checks if your harness uses different file locations. See [Assumptions](index.md#assumptions).

This is the orchestration runbook for the [agent-readiness library](index.md). Run it first on any unfamiliar codebase. It produces the scorecard that determines which other runbooks to execute and in what order.

## Pre-Flight

Confirm the working directory is a code repository, not a docs site or scratchpad:

```bash
test -d .git || { echo "FATAL: not a git repository — abort"; exit 1; }
git rev-parse --is-bare-repository | grep -q false || { echo "FATAL: bare repo"; exit 1; }
```

## Step 1 — Inventory

Enumerate every agent-relevant artifact. Run these in parallel, capture results. `maxdepth` is set generously (8) to cover monorepos; tighten only on confirmed-flat repos.

```bash
# Instruction surfaces
find . -maxdepth 8 -type f \( \
  -iname "AGENTS.md" -o \
  -iname "CLAUDE.md" -o \
  -iname "CLAUDE.local.md" -o \
  -iname "copilot-instructions.md" -o \
  -path "*/.cursor/rules/*" -o \
  -path "*/.cursor/mdc/*" -o \
  -name ".cursorrules" -o \
  -name ".aider.conf.yml" -o \
  -name "GEMINI.md" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/dist/*" ! -path "*/build/*"

# Skill / sub-agent surfaces
find . -maxdepth 8 \( \
  -path "*/.claude/skills/*/SKILL.md" -o \
  -path "*/.claude/agents/*.md" -o \
  -path "*/.claude/commands/*.md" -o \
  -path "*/.cursor/skills/*/SKILL.md" -o \
  -path "*/.cursor/hooks/*" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*"

# Discoverability
ls -la llms.txt llms-full.txt docs/llms.txt docs/llms-full.txt 2>/dev/null

# Verification
find . -maxdepth 4 -type d \( -name "evals" -o -name "evaluations" \) ! -path "*/node_modules/*"
ls -la .github/workflows/*.y*ml 2>/dev/null

# Permissions / hooks — parse explicitly; surface malformed JSON as a finding,
# do not silently swallow with `2>/dev/null`
if [[ -f .claude/settings.json ]]; then
  if ! jq empty .claude/settings.json 2>/tmp/_jqerr; then
    echo "FINDING: settings.json malformed — $(cat /tmp/_jqerr)"
  else
    jq '{permissions, hooks, mcpServers}' .claude/settings.json
  fi
fi
test -d .claude/hooks && ls .claude/hooks/

# MCP servers (deeper search; some monorepos place the file in a subpackage)
find . -maxdepth 6 \( -name "mcp.json" -o -name ".mcp.json" \) ! -path "*/node_modules/*"
```

Record presence/absence per artifact. The result is the `inventory` object referenced below. **Every silent failure (malformed JSON, missing-but-expected file, permission-denied read) becomes a finding** — never let a parse error short-circuit the inventory into a false negative.

## Step 2 — Run Audits in Parallel

For each present-or-expected artifact, run the matching audit runbook. Treat the results as structured findings (severity, surface, finding, action):

| Audit | Required when | Runbook |
|-------|---------------|---------|
| Secrets in context | Always — runs first, blocks others on high finding | [`audit-secrets-in-context`](audit-secrets-in-context.md) |
| AGENTS.md | `inventory.agents_md` exists | [`audit-agents-md`](audit-agents-md.md) |
| CLAUDE.md | `inventory.claude_md` or equivalent exists | [`audit-claude-md`](audit-claude-md.md) |
| Instruction rule budget | Any instruction surface exists | [`audit-instruction-rule-budget`](audit-instruction-rule-budget.md) |
| Skill quality | `inventory.skills` non-empty | [`audit-skill-quality`](audit-skill-quality.md) |
| Tool descriptions | `inventory.mcp` non-empty or custom tools defined | [`audit-tool-descriptions`](audit-tool-descriptions.md) |
| Hooks coverage | `.claude/`, `.cursor/hooks/`, or equivalent exists | [`audit-hooks-coverage`](audit-hooks-coverage.md) |
| Permissions / blast radius | Agent runs with write access | [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) |
| Lethal trifecta | More than one agent or sub-agent defined | [`audit-lethal-trifecta`](audit-lethal-trifecta.md) |

If `audit-secrets-in-context` returns any `high` finding, **halt the assessment** and surface only that finding to the user. Other audits are moot until the secret is rotated.

## Step 3 — Score Each Dimension

Score each dimension 0–5 using the rubric. Use the strictest matching level (don't claim L3 if any L2 criterion fails).

### Instructions

| Level | Criterion |
|-------|-----------|
| L0 | No `AGENTS.md`, `CLAUDE.md`, or equivalent |
| L1 | Instruction file exists with executable commands |
| L2 | Pointer-map structure; ≤100 lines (root) / ≤30 (subdir); skills loaded on demand |
| L3 | Audit-clean against [`audit-agents-md`](audit-agents-md.md), [`audit-claude-md`](audit-claude-md.md); rule count ≤150 |
| L4 | `llms.txt` published; tool descriptions audit-clean; cross-tool ecosystem (`@AGENTS.md` import in `CLAUDE.md`) |
| L5 | All instruction surfaces written for agent consumption first; human docs derive from them |

### Harness

| Level | Criterion |
|-------|-----------|
| L0 | No `.claude/`, `.cursor/`, or equivalent |
| L1 | At least one sub-agent or skill defined |
| L2 | `PreToolUse`/`PostToolUse` hooks wired with correct matchers |
| L3 | Stop-event pre-completion checklist; loop detection in place |
| L4 | `SessionStart`, `PreCompact`, progress files; checklist auto-derives from task type |
| L5 | Harness self-audits via [`audit-hooks-coverage`](audit-hooks-coverage.md) on every PR |

### Security

| Level | Criterion |
|-------|-----------|
| L0 | No permission allowlist; no deny rules; secrets readable |
| L1 | Bash allowlist; no live secrets in instruction files |
| L2 | Sensitive-path deny rules; no high-severity lethal trifecta principal |
| L3 | Per-sub-agent tool restrictions; egress allowlisted; URL exfiltration guard |
| L4 | Approval gates on destructive ops; safe-outputs declared on automations |
| L5 | Default-deny posture; periodic [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) in CI |

### Verification

| Level | Criterion |
|-------|-----------|
| L0 | No tests or only ad-hoc tests |
| L1 | Test suite + linter wired in CI |
| L2 | Pre-commit deterministic guardrails; structural lint rules with remediation messages |
| L3 | `evals/` directory with paired baseline/with-skill cases; CI gates merge on P0 regression |
| L4 | Incident-to-eval pipeline live; eval suite covers ≥80% of past incident classes |
| L5 | Eval-driven development is the default workflow; new features ship behind evals |

The aggregate level is the **minimum across dimensions** (a project at L4 instructions / L1 security is L1).

## Step 4 — Build the Punch List

Score every candidate runbook on two axes and order by the product:

| Axis | Values | Weight |
|------|--------|-------:|
| **Severity** | `5` security high, `4` L0 dimension, `3` L1 dimension, `2` audit findings without level regression, `1` polish | 1.0 |
| **Ease** | `5` mechanical (config edit), `4` template scaffold, `3` requires user probe, `2` requires user content (incidents, gotchas), `1` requires architectural decisions | 0.6 |

Score = `severity + (ease × 0.6)`. Sort descending. Ties broken by severity, then by dimension order: **Security > Instructions > Harness > Verification**. Rationale: security findings can manifest as live incidents (exfiltration, credential leak) and gate everything else; instruction quality compounds across every later step; the harness shapes daily work; verification has the longest lead time but the lowest immediate blast radius.

Worked examples:

| Candidate | Severity | Ease | Score | Reason |
|-----------|---------:|-----:|------:|--------|
| `audit-secrets-in-context` finds live key | 5 | 5 | 8.0 | high security; fix is rotate-and-remove |
| `bootstrap-permissions-allowlist` (no `.claude/settings.json`) | 4 | 4 | 6.4 | L0 security; template scaffold |
| `bootstrap-precompletion-hook` (Stop event missing) | 4 | 4 | 6.4 | L0 harness; template scaffold |
| `bootstrap-eval-suite` (no evals/) | 4 | 2 | 5.2 | L0 verification but content-heavy (incidents to mine) |
| `audit-claude-md` patches | 2 | 5 | 5.0 | mid-level findings; mechanical fixes |
| `bootstrap-llms-txt` | 1 | 4 | 3.4 | polish; nav-aware scaffold |

The formula intentionally penalizes `bootstrap-eval-suite` despite its L0 weight — eval design is the work, scaffolding the directory is not. Surface this in the report so the user can override.

Apply the gates:

1. **Halt-on-secrets**: any `audit-secrets-in-context` high finding stops the assessment; the only emitted recommendation is rotation
2. **Lethal trifecta close**: any `(1,1,1)` principal in `audit-lethal-trifecta` is high severity even if the dimension is mid-level
3. **Default-deny check**: missing `permissions` block scores L0 security regardless of other dimensions

For each gap, name the runbook to execute next and the expected level uplift.

## Step 5 — Emit the Report

Output the scorecard in this exact schema:

```markdown
# Agent Readiness Report — <repo-name>

> Assessed on <YYYY-MM-DD>. Aggregate level: **L<n>** (limited by <dimension>).

## Inventory

| Artifact            | Present | Notes |
|---------------------|:-------:|-------|
| AGENTS.md           |   <yn>  | <path / size> |
| CLAUDE.md           |   <yn>  | <path / size> |
| llms.txt            |   <yn>  | |
| .claude/skills/     |   <yn>  | <count> |
| .claude/agents/     |   <yn>  | <count> |
| .claude/hooks/      |   <yn>  | <count> |
| evals/              |   <yn>  | |
| Permission config   |   <yn>  | |

## Dimension scores

| Dimension     | Level | Top finding |
|---------------|:-----:|-------------|
| Instructions  |  L<n> | <finding>   |
| Harness       |  L<n> | <finding>   |
| Security      |  L<n> | <finding>   |
| Verification  |  L<n> | <finding>   |

## Punch list

1. [<severity>] **<runbook-name>** — <one-line reason>; expected uplift: <dim> L<n>→L<m>
2. ...
```

## Step 6 — Hand Off

Hand off according to the [mode set by the orchestrator](index.md#mode-selection):

- **Interactive** — present the punch list and ask which items to apply now. For each chosen item, open the corresponding runbook, narrate the change, apply it, then re-run this assessment to confirm uplift.
- **Autonomous** — apply only safe-by-construction items (see [`index.md` §Autonomous Flow](index.md#autonomous-flow)); file the rest to the backlog; re-run this assessment once at the end and emit the delta.

## Re-Run: Delta Schema

A re-run **does not** replace the previous report — it produces a delta against it. Persist the prior scorecard at `.claude/state/agent-readiness/last.json` (this runbook creates the path if absent; substitute `.cursor/state/`, `.aider/state/`, or any project-local cache directory if the project uses a different harness). Emit the delta:

```markdown
# Agent Readiness — Delta vs <prior YYYY-MM-DD>

| Dimension | Prior | Now | Δ |
|-----------|:-----:|:---:|:-:|
| Instructions | L1 | L2 | ↑1 |
| Harness | L0 | L1 | ↑1 |
| Security | L1 | L1 | — |
| Verification | L2 | L2 | — |

**Aggregate**: L0 → L1 (limited by Harness)

## Resolved

- ✅ `bootstrap-permissions-allowlist` — created `.claude/settings.json` with default-deny; security L0→L1
- ✅ `bootstrap-precompletion-hook` — wired Stop event; harness L0→L1

## Still open (re-prioritized)

1. [score 6.4] `bootstrap-loop-detector-hook` — close harness L1→L2
2. [score 5.2] `audit-claude-md` patches — close instructions L2→L3
3. [score 3.4] `bootstrap-llms-txt` — polish

## Regressions

(none) — or list any dimension that dropped, with the suspected cause.
```

The delta is what feeds the agent's improvement loop; the full scorecard is also emitted (for absolute state) but the delta is what the user reads.

## Operating Notes

- Run the audit phase in parallel; the runbooks do not interfere
- Always run `audit-secrets-in-context` first; halt on a high finding
- Re-run quarterly even when no work is queued — readiness regresses as codebases evolve
- The aggregate level is constrained by the minimum dimension; raising the lowest dimension is always the highest-leverage move

## Related

- [Brownfield-to-Agent-First Maturity](../frameworks/brownfield-to-agent-first/index.md)
- [Agent-First Software Design](../agent-design/agent-first-software-design.md)
- [Harness Engineering](../agent-design/harness-engineering.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
