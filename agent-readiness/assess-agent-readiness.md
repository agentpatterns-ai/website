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

# Assess Agent Readiness

> Inventory the codebase, run the audit suite, score L0–L5 across four dimensions, and emit a prioritized punch list.

This is the orchestration runbook for the [agent-readiness library](index.md). Run it first on any unfamiliar codebase. It produces the scorecard that determines which other runbooks to execute and in what order.

## Pre-Flight

Confirm the working directory is a code repository, not a docs site or scratchpad:

```bash
test -d .git || { echo "FATAL: not a git repository — abort"; exit 1; }
git rev-parse --is-bare-repository | grep -q false || { echo "FATAL: bare repo"; exit 1; }
```

## Step 1 — Inventory

Enumerate every agent-relevant artifact. Run these in parallel, capture results:

```bash
# Instruction surfaces
find . -maxdepth 4 -type f \( \
  -iname "AGENTS.md" -o \
  -iname "CLAUDE.md" -o \
  -iname "CLAUDE.local.md" -o \
  -iname "copilot-instructions.md" -o \
  -path "*/.cursor/rules/*" -o \
  -path "*/.cursor/mdc/*" -o \
  -name ".cursorrules" -o \
  -name ".aider.conf.yml" -o \
  -name "GEMINI.md" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*"

# Skill / sub-agent surfaces
find . -path "*/.claude/skills/*/SKILL.md" \
  -o -path "*/.claude/agents/*.md" \
  -o -path "*/.claude/commands/*.md" \
  -o -name "settings.json" -path "*/.claude/*"

# Discoverability
ls -la llms.txt llms-full.txt docs/llms.txt docs/llms-full.txt 2>/dev/null

# Verification
find . -maxdepth 3 -type d -name "evals" -o -name "evaluations"
ls -la .github/workflows/*.y*ml 2>/dev/null

# Permissions / hooks
test -f .claude/settings.json && jq '.permissions, .hooks' .claude/settings.json 2>/dev/null
test -d .claude/hooks && ls .claude/hooks/

# MCP servers
find . -maxdepth 3 -name "mcp.json" -o -name ".mcp.json" 2>/dev/null
```

Record presence/absence per artifact. The result is the `inventory` object referenced below.

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

Order recommendations by `severity × ease`:

1. Any `high` security finding → immediate action (no other work proceeds)
2. Any L0 dimension → corresponding bootstrap runbook
3. Any L1 dimension → audit + targeted bootstrap
4. Mid-level gaps (L2–L3) → audit-driven refinement
5. Polish (L4–L5) → backlog, not active

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

Ask the user which punch-list items to execute now. For each chosen item, open the corresponding runbook and apply it. Re-run this assessment after each batch to confirm uplift.

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
