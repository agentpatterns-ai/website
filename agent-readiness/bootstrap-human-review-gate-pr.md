---
title: "Bootstrap Human Review Gate for Agent-Authored PRs"
description: "Wire a CODEOWNERS-plus-branch-protection gate that routes agent-authored PRs through tiered review — non-critical paths merge after AI-only review, core and security-sensitive paths require mandatory human approval — and emit the merge-rate metric that proves the gate is doing work."
tags:
  - tool-agnostic
  - code-review
  - workflows
aliases:
  - agent pr human approval gate
  - tiered review bootstrap
  - codeowners review gate scaffold
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-human-review-gate-pr/`

# Bootstrap Human Review Gate for Agent-Authored PRs

> Wire CODEOWNERS + branch protection so agent-authored PRs route through tiered review — non-critical merges after AI-only review, core and security-sensitive paths require human approval — and emit the merge-rate metric that proves the gate works.

!!! info "Harness assumption"
    Templates target GitHub. GitLab, Gitea, and Bitbucket have equivalent CODEOWNERS / branch-protection mechanisms; the per-tier table and the rule set transfer. Where a project hosts only locally, pair the tier table with a pre-merge script that enforces the same routing. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Apply once the project receives **agent-authored PRs at any cadence**. The gate is cheap to wire and pays off on the first agent PR that touches a security-sensitive path. Skip only when the repository is single-author and accepts no external contributions.

[CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md) measures the failure mode the gate prevents: CRA-only review yields 45.2% merge rates versus 68.4% for human-only — a 23-point gap closed almost entirely by adding a single human reviewer. [Tiered Code Review](../code-review/tiered-code-review.md) provides the structural template: AI handles every PR's first pass, non-critical merges after AI-only review, and critical paths escalate to mandatory human review.

This runbook generates the CODEOWNERS file, branch-protection ruleset, and merge-rate emitter — write before wire, smoke test before declaring done.

## Step 1 — Detect Existing Review State

```bash
# CODEOWNERS presence and scope
find . -path ./node_modules -prune -o \( -name "CODEOWNERS" -print \) 2>/dev/null

# Branch protection configured at GitHub
gh api repos/{owner}/{repo}/branches/main/protection 2>/dev/null | jq '.required_pull_request_reviews'

# Existing CRA configuration (Copilot review, Claude Action, Codex)
test -f .github/copilot.yml && echo "copilot review configured"
find .github/workflows -name "*.y*ml" -exec grep -l "claude-code\|claude/claude-code-action\|codex" {} \; 2>/dev/null
```

Decision rules:

- **No CODEOWNERS, no branch protection** → run all steps.
- **CODEOWNERS exists but no branch protection** → skip Step 2; jump to Step 3 to wire enforcement.
- **CRA configured, no CODEOWNERS** → skip Step 5; jump to Step 2 to define tiers.

## Step 2 — Define the Three Tiers

Per [Tiered Code Review](../code-review/tiered-code-review.md), each tier has a different merge bar:

| Tier | Paths (examples) | Review requirement | Merge gate |
|------|------------------|-------------------|------------|
| **1. Automated** | `tests/`, `docs/`, `*.md`, `config/`, CSS, migrations | AI review only | AI passes, CI green |
| **2. AI + Human** | `src/api/`, `src/models/`, `src/services/` | AI first pass + 1 human approval | CODEOWNERS approval |
| **3. Human-only** | `src/auth/`, `src/payments/`, `src/crypto/`, `src/pii/` | Mandatory human review | Security team approval |

The classification step is the hardest part. Apply the four heuristics from [Tiered Code Review §Classification Framework](../code-review/tiered-code-review.md):

1. **Security boundary** — auth, authorization, encryption, PII → Tier 3.
2. **Financial impact** — payments, billing, subscriptions → Tier 3.
3. **Blast radius** — affects all users → Tier 2 or 3 by reversibility.
4. **Reversibility** — corrupts persistent state → Tier 2 or 3.

If the project has no security-sensitive paths, ship a two-tier configuration (Tier 1 + Tier 2). Do not invent Tier-3 paths to fill the table.

## Step 3 — Generate CODEOWNERS

```bash
mkdir -p .github
cat > .github/CODEOWNERS <<'EOF'
# Agent Readiness: tiered review per docs/agent-readiness/bootstrap-human-review-gate-pr.md
#
# Tier 3: Human-only — mandatory security-team review
/src/auth/           @<org>/security
/src/payments/       @<org>/security
/src/crypto/         @<org>/security
/src/pii/            @<org>/security

# Tier 2: AI + Human — domain owner approval
/src/api/            @<org>/backend
/src/models/         @<org>/backend
/src/services/       @<org>/backend

# Tier 1: AI-only — no CODEOWNERS entry
# tests/, docs/, *.md, config/, CSS, migrations: AI review only
EOF
```

Replace `<org>` with the actual GitHub org or team slug. Validate the syntax:

```bash
gh api repos/{owner}/{repo}/codeowners/errors --jq '.errors'
```

A non-empty errors array means the file references unknown teams or invalid paths — fix before wiring branch protection.

## Step 4 — Wire Branch Protection

```bash
# Require CODEOWNERS approval on main
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[require_code_owner_reviews]=true \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]="ai-review"
```

Two separate effects:

- `require_code_owner_reviews=true` → Tier-2 and Tier-3 paths block on CODEOWNERS approval.
- `required_status_checks[contexts]` includes the AI-review check → Tier-1 paths still block on the AI first pass.

## Step 5 — Wire the AI First Pass

If a CRA is not yet configured, choose one referenced by [Tiered Code Review §Real-World Implementations](../code-review/tiered-code-review.md):

| CRA | Wiring |
|-----|--------|
| GitHub Copilot review | Enable [Copilot automatic code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review) at repo or org level |
| Claude Code GitHub Action | `.github/workflows/claude-review.yml` per [Claude Code GitHub Actions](https://docs.claude.com/en/docs/claude-code/github-actions) |
| Codex (OpenAI) | Webhook on draft → review transition per the [Codex internal pattern](https://newsletter.pragmaticengineer.com/p/how-codex-is-built) |

The AI-review job's GitHub status check name is what populates `required_status_checks[contexts]` in Step 4.

## Step 6 — Severity-Driven Findings

Per [Tiered Code Review §Severity-Driven Merge Gates](../code-review/tiered-code-review.md), the AI review must classify findings into three buckets:

| Severity | Effect | Example |
|----------|--------|---------|
| Action Required | Blocks merge | SQL injection, auth bypass, data loss |
| Recommended | Advisory, mergeable | Missing error handling |
| Minor Suggestion | Optional | Naming, style |

Wire the AI-review action so only Action Required findings fail the status check. Recommended and Minor findings post as comments without blocking. Without this filter the gate becomes alert-fatigue noise — the same failure mode [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md) audits for.

## Step 7 — Emit the Merge-Rate Metric

The gate's value is empirical. Per [CRA Merge Rate Gap](../code-review/cra-merge-rate-gap.md), the controllable signal ratio metric ranges from 0.0 (all noise) to 1.0 (all signal). Emit a daily merge-rate-by-tier report so the gate is observable:

```bash
cat > scripts/agent-pr-merge-rate.sh <<'EOF'
#!/usr/bin/env bash
# Emits agent-PR merge rate by tier for the last 30 days.
# Source: docs/code-review/cra-merge-rate-gap.md, agent-pr-volume-vs-value.md
since=$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)
gh pr list --state merged --search "author:app/claude author:app/copilot author:app/codex created:>${since}" \
  --json number,files,mergedAt,reviewDecision \
  | jq '[.[] | {tier: (
        if (.files[]?.path // "") | test("^src/(auth|payments|crypto|pii)/") then 3
        elif (.files[]?.path // "") | test("^src/(api|models|services)/") then 2
        else 1 end),
       merged: (.mergedAt != null),
       human_approved: (.reviewDecision == "APPROVED")
    }]'
EOF
chmod +x scripts/agent-pr-merge-rate.sh
```

Track three numbers per tier — total agent PRs, merged, human-approved. A Tier-3 PR merged without `human_approved=true` is a **gate breach**: branch protection drift, force-merge by an admin, or a CODEOWNERS gap.

## Step 8 — Smoke Test

```bash
# Open a draft PR touching only Tier-1 paths — must mergeable after AI passes
gh pr create --draft --base main --head smoke-tier1 \
  --title "smoke: tier-1 only" --body "tests only"

# Open a draft PR touching a Tier-3 path — must require security team approval
gh pr create --draft --base main --head smoke-tier3 \
  --title "smoke: tier-3" --body "src/auth touched"
gh pr view smoke-tier3 --json mergeable,reviewDecision \
  | jq -e '.mergeable == "MERGEABLE" and .reviewDecision != "APPROVED"' \
  || echo "FINDING: tier-3 PR mergeable without human approval"
```

Both PRs are draft and never merged — the smoke test reads only `mergeable` and `reviewDecision` to confirm the gate's behaviour. Delete after.

## Step 9 — Document the Bypass and Override

Record the documented overrides so reviewers and incident responders know what is allowed:

```markdown
## Agent-PR Review Gate

PRs touching `src/auth/`, `src/payments/`, `src/crypto/`, `src/pii/` require
security-team approval. Override is admin-only and audited via the
branch-protection bypass log. AI-only merges are restricted to Tier-1 paths
listed in `.github/CODEOWNERS`.
```

Add to `AGENTS.md` and the project's `SECURITY.md` if present.

## Idempotency

Re-running on a configured repo: detection finds CODEOWNERS, branch protection, and the AI-review action; the smoke test passes; no diff. Re-running after CODEOWNERS drift: Step 1 surfaces the gap, Step 3 regenerates only the missing tier rows.

## Output Schema

```markdown
# Human Review Gate (Agent PRs) — <repo>

| Component | State |
|-----------|-------|
| CODEOWNERS file | present / generated |
| Branch protection | wired / pending |
| AI review status check | <check name> |
| Smoke test | tier-1 ok, tier-3 blocked |
| Merge-rate emitter | scripts/agent-pr-merge-rate.sh |

Merge-rate (last 30 days): tier-1 <pct>, tier-2 <pct>, tier-3 <pct>; gate breaches: <n>
```

## Related

- [CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md)
- [Tiered Code Review](../code-review/tiered-code-review.md)
- [Agent PR Volume vs. Value](../code-review/agent-pr-volume-vs-value.md)
- [Signal Over Volume in AI Review](../code-review/signal-over-volume-in-ai-review.md)
- [Audit Premature Completion](audit-premature-completion.md)
- [Audit Confirmation Gate Logs](audit-confirmation-gate-logs.md)
- [Bootstrap Precompletion Hook](bootstrap-precompletion-hook.md)
