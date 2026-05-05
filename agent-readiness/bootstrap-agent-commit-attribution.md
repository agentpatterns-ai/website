---
title: "Bootstrap Agent Commit Attribution"
description: "Configure agents to write commits with cryptographic signing plus structured metadata trailers (Agent-Session, Model, Task-Reference); generate the signing-key bootstrap script and the rotation playbook; wire branch protection to require signed commits — invoke when an agent has direct push access or before opening agent commit access on protected branches."
tags:
  - tool-agnostic
  - workflows
  - security
aliases:
  - agent commit signing bootstrap
  - agent identity bootstrap
  - signed commits for agents
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-agent-commit-attribution/`

# Bootstrap Agent Commit Attribution

> Wire agents to sign commits with a dedicated key plus structured metadata trailers, configure branch protection to require signing, and ship a rotation playbook before granting push access.

!!! info "Harness assumption"
    GitHub-hosted repository with branch protection or repository rulesets. Translates to GitLab, Gitea, Forgejo via that forge's signing-required rule. Local-only repos can skip the branch-protection step but still benefit from the trailers.

!!! info "Applicability"
    Run before granting an agent direct push access to a shared repository. Skip when the agent only opens PRs and a human pushes the merge — in that case the human's commit identity carries through, and the trailers alone (no signing) suffice for session traceability.

Cryptographic signing proves *who*; trailers record *what session and task*. The two are complementary, not alternatives ([`agent-commit-attribution`](../workflows/agent-commit-attribution.md)). Without trailers, a signed commit only identifies the bot account — incident triage cannot replay the originating session. Without signing, trailers are forgeable. Rules from [`agent-commit-attribution`](../workflows/agent-commit-attribution.md), and signing-rotation guidance from the same page §Trade-offs.

## Step 1 — Detect Existing Attribution

```bash
# Are agent commits already signed?
git log --since='30 days ago' --pretty='%H %G? %s' \
  | awk '$2 != "G" && $3 ~ /Co-authored-by.*\(bot\|copilot\|claude\)/ {print "unsigned: "$0}' \
  | head

# Are trailers present?
git log --since='30 days ago' --grep='Agent-Session:' -E --pretty='%H %s' | wc -l

# Branch protection state
gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/branches/main/protection" \
  -q '.required_signatures.enabled' 2>/dev/null
```

If signing is already enforced and trailers are present on every recent agent commit, the project is compliant — abort with "no work needed".

## Step 2 — Generate a Dedicated Signing Key

Never reuse a human's GPG/SSH key for the agent. Compromise of the agent's key must be containable without rotating human keys.

```bash
# SSH signing key (preferred — no GPG dependency)
ssh-keygen -t ed25519 -f ~/.ssh/agent-signing -C "agent@<repo-or-org>" -N ""

# Register the public key with the bot account on GitHub:
gh ssh-key add ~/.ssh/agent-signing.pub --type signing --title "agent-signing-$(date +%Y-%m-%d)"
```

GPG signing is the alternative — use it when the org standardizes on GPG. The branch-protection rule treats both equivalently; the choice is operational.

## Step 3 — Configure the Agent's Git Environment

```bash
# In the agent harness (CI runner, sandboxed VM, or local config)
git config --global user.signingkey ~/.ssh/agent-signing.pub
git config --global gpg.format ssh
git config --global commit.gpgsign true
```

For Claude Code, place this in the project's `.envrc`, hook init script, or `bootstrap.sh` so it runs at session start. For GitHub Copilot cloud agent, signing is platform-managed as of 2026-04-03 ([GitHub Changelog](https://github.blog/changelog/2026-04-03-copilot-cloud-agent-signs-its-commits/)) — skip Steps 2–3 and go to Step 4.

## Step 4 — Wire the Trailer-Producing Commit Hook

A `prepare-commit-msg` hook appends the trailers from environment variables the harness exposes. The trailers are not invented — they come from session metadata the harness already has.

```bash
cat > .git/hooks/prepare-commit-msg <<'BASH'
#!/usr/bin/env bash
set -e
COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Only annotate when running under an agent harness
[[ -z "$AGENT_SESSION" ]] && exit 0

# Skip merge/squash/amend (trailers should already be in the source commits)
[[ "$COMMIT_SOURCE" == "merge" || "$COMMIT_SOURCE" == "squash" ]] && exit 0

# Append trailers if not already present
grep -q '^Agent-Session:' "$COMMIT_MSG_FILE" || cat >> "$COMMIT_MSG_FILE" <<EOF

Agent-Session: ${AGENT_SESSION}
Model: ${AGENT_MODEL:-unknown}
Task-Reference: ${AGENT_TASK_REF:-none}
EOF
BASH
chmod +x .git/hooks/prepare-commit-msg
```

Track the hook in-repo (e.g., under `scripts/git-hooks/`) and install it via the project's bootstrap script — `.git/hooks/` is not versioned by default.

## Step 5 — Branch Protection: Require Signed Commits

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Repository ruleset (recommended) — actor-scoped to bot accounts only
gh api "repos/$REPO/rulesets" -X POST -f name='agent-signing' -f target='branch' \
  -F enforcement='active' \
  -f conditions='{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}}' \
  -f rules='[{"type":"required_signatures"}]' \
  -f bypass_actors='[]'

# Or classic branch protection (whole-branch enforcement)
gh api "repos/$REPO/branches/main/protection" -X PUT \
  -f required_signatures.enabled=true
```

Use the ruleset path for organizations migrating — it allows actor-scoped enforcement so humans can keep pushing unsigned commits during the transition while the bot is held to the rule from day one ([`agent-commit-attribution`](../workflows/agent-commit-attribution.md) §Branch Protection Configuration).

## Step 6 — Smoke Test

```bash
# Test commit produced by the agent harness
AGENT_SESSION=test-001 AGENT_MODEL=claude-opus-4-7 AGENT_TASK_REF=#0 \
  git -c user.email='agent@example.com' commit --allow-empty -m "test: signing smoke test"

# Verify the trailers landed and signature is good
git log -1 --pretty='%G? %s%n%b'
# Expect: G (good signature), Agent-Session/Model/Task-Reference trailers present
```

If `%G?` is not `G`, the signing key is wrong or unregistered. If trailers are missing, the hook did not run — `chmod +x` and harness env-var exposure are the usual culprits.

## Step 7 — Key Rotation Playbook

Key compromise has real blast radius and is operational overhead the team must own ([`agent-commit-attribution`](../workflows/agent-commit-attribution.md) §Key Rotation). Ship the playbook with the bootstrap, not after.

```markdown
## Agent signing-key rotation

Triggers:
- Annual rotation (calendar)
- Suspected exposure (key file leaked, env var logged, harness compromise)
- Bot-account credential change

Steps:
1. Generate replacement key (Step 2 of bootstrap-agent-commit-attribution).
2. Add the new public key to the bot account *before* removing the old one.
3. Update the harness configuration to use the new key.
4. Wait for the agent to produce one commit signed with the new key; verify.
5. Remove the old public key from the bot account.
6. Revoke any previously-signed commits with the old key only if exposure is confirmed (rewriting history is destructive — confirm with the team).
```

Place the playbook at `docs/runbooks/agent-key-rotation.md` or equivalent and link it from `AGENTS.md`.

## Step 8 — Register the Policy in AGENTS.md

```markdown
## Agent commit attribution

- All agent commits are signed with the dedicated `agent-signing` SSH key.
- Trailers required: `Agent-Session`, `Model`, `Task-Reference`.
- Branch protection on `main` enforces "Require signed commits".
- Key rotation playbook: docs/runbooks/agent-key-rotation.md
```

## Idempotency

Re-runnable. Step 1 detects existing state. Steps 2–5 produce no diff when already configured. Step 6 smoke test is read-only verification.

## Output Schema

```markdown
# Bootstrap Agent Commit Attribution — <repo>

| Signing | Trailer hook | Branch protection | Smoke-test | Rotation playbook |
|:-------:|:------------:|:-----------------:|:----------:|:-----------------:|
| ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ |

Top fix: <one-liner — usually wire the prepare-commit-msg hook or enable required_signatures>
```

## Remediation

- [`audit-agent-built-code-health`](audit-agent-built-code-health.md) — depends on commit attribution to identify agent-touched code
- [`audit-agent-pr-quality-metrics`](audit-agent-pr-quality-metrics.md) — uses author and trailer signals to scope agent PR analysis
- [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md) — branch protection is the wiring point for both signing and CODEOWNERS gating

## Related

- [Agent Commit Attribution](../workflows/agent-commit-attribution.md)
- [Bootstrap Human Review Gate (PR)](bootstrap-human-review-gate-pr.md)
- [Audit Agent-Built Code Health](audit-agent-built-code-health.md)
- [Audit Agent PR Quality Metrics](audit-agent-pr-quality-metrics.md)
