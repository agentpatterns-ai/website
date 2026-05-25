---
title: "Bootstrap Evidence-Based Allowlist Auto-Discovery"
description: "Generate a PermissionRequest + PostToolUse hook pair that promotes a Bash command to the allow list after N successful manual approvals, with a never-auto-allow deny list and a sidecar approval log."
tags:
  - tool-agnostic
  - security
aliases:
  - bootstrap usage-based allowlist
  - bootstrap dynamic allowlist
  - generate auto-discovery hooks
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-evidence-based-allowlist/`

# Bootstrap Evidence-Based Allowlist Auto-Discovery

> Generate a PermissionRequest + PostToolUse hook pair that promotes a Bash command to the allow list after N successful manual approvals, gated by a never-auto-allow deny list and a sidecar approval log.

!!! info "Harness assumption"
    Templates target Claude Code's `PermissionRequest` and `PostToolUse` events; only `PermissionRequest` exposes a settings-write-back path via `updatedPermissions` ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). Other harnesses without an equivalent write-back hook need a wrapper script that edits the settings file out-of-band — translate the schema accordingly. See [Assumptions](index.md#assumptions).

!!! warning "Safety: write before wire"
    Create the two hook scripts on disk, `chmod +x`, **and smoke-test each standalone** before adding the entries to `settings.json`. A registered-but-broken `PermissionRequest` hook collapses the permission UX every time the agent asks — and a broken `PostToolUse` hook reads exit 2 as "block" on every Bash success. The step ordering below is load-bearing: Step 5 (smoke test) precedes Step 6 (wire). See [Recovery in `bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md#recovery) for the un-wedge procedure if you skip it.

This runbook complements [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md) — that one ships a default-deny **static** allowlist; this one adds an **evidence-based** path so commands the user manually approves enough times become permanent allow rules without manual editing. The pair: ship default-deny upfront, let real usage extend it. Source: [evidence-based allowlist auto-discovery](../human/evidence-based-allowlist-auto-discovery.md), [safe command allowlisting](../human/safe-command-allowlisting.md), [permission-gated commands](../security/permission-gated-commands.md).

## Step 1 — Detect Current State

```bash
# Hook events already wired
test -f .claude/settings.json && jq '.hooks | keys' .claude/settings.json

# Existing PermissionRequest entry (only one allowed at a time per matcher)
test -f .claude/settings.json && jq '.hooks.PermissionRequest // empty' .claude/settings.json

# Existing static allow rules (these stay; auto-discovery extends, not replaces)
test -f .claude/settings.json && jq '.permissions.allow // []' .claude/settings.json
```

Decision rules:

- **No `.claude/settings.json`** → run [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md) first; auto-discovery layers on top of a default-deny base.
- **PermissionRequest already wired with a different script** → audit it ([`audit-hooks-coverage`](audit-hooks-coverage.md)) and merge logic into one script; do not stack two PermissionRequest hooks fighting over `updatedPermissions`.
- **Headless / CI environment** → skip this runbook entirely. Auto-promotion in CI silently elevates commands no human reviewed; the `evidence-based-allowlist-auto-discovery` page calls this failure mode out as the "scripted runs" backfire.

## Step 2 — Choose Threshold and Destination

| Variable | Default | Rationale |
|---|---|---|
| `THRESHOLD` | 5 | Five distinct successful approvals before promotion. Lower for solo work; raise for shared repos. |
| `destination` | `localSettings` | Per-machine; never lands in version control unintentionally. Use `projectSettings` only with explicit team review. |
| `KEY` strategy | first token of the command | Matches per-command. For high-risk prefixes (e.g. `git`), narrow to two-token (`git push`, `git reset`) so safe reads don't elevate destructive variants — see Step 3 fingerprint extension. |

The `evidence-based-allowlist-auto-discovery` page documents the broad-key-matching backfire ([Claude Code v2.1.77 changelog](https://code.claude.com/docs/en/changelog) noted the related bug of compound commands saving a single rule for the full string). Default to first-token; promote the high-risk-prefix list to two-token deliberately.

## Step 3 — Generate the PermissionRequest Hook

`.claude/hooks/permission-request-promote.sh`:

```bash
#!/usr/bin/env bash
# PermissionRequest hook: read approval count for the command's key; if
# the count meets THRESHOLD, return updatedPermissions to add an allow rule
# to localSettings. Otherwise exit 0 to let the dialog show as normal.
set -euo pipefail

THRESHOLD="${ALLOWLIST_PROMOTE_AFTER:-5}"
LOG_FILE=".claude/state/approval-log.json"
NEVER_AUTO_ALLOW=( rm rmdir curl wget mv dd sudo chmod chown ssh scp rsync )

EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Bash" ] || exit 0

CMD=$(echo "$EVENT" | jq -r '.tool_input.command // empty')
[ -z "$CMD" ] && exit 0

KEY=$(printf '%s\n' "$CMD" | awk '{print $1}')
[ -z "$KEY" ] && exit 0

# Two-token narrowing for high-risk prefixes
case "$KEY" in
  git|docker|kubectl|gh)
    SECOND=$(printf '%s\n' "$CMD" | awk '{print $2}')
    [ -n "$SECOND" ] && KEY="$KEY $SECOND"
    ;;
esac

# Hard deny: never auto-promote these regardless of count
for blocked in "${NEVER_AUTO_ALLOW[@]}"; do
  [ "${KEY%% *}" = "$blocked" ] && exit 0
done
# Also deny git pushes specifically
[ "$KEY" = "git push" ] && exit 0
[ "$KEY" = "git reset" ] && exit 0

[ -f "$LOG_FILE" ] || exit 0
COUNT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE" 2>/dev/null || echo 0)

if [ "$COUNT" -ge "$THRESHOLD" ]; then
  PATTERN=$(printf 'Bash(%s *)' "$KEY")
  jq -n --arg p "$PATTERN" '{
    updatedPermissions: {
      addRules: [{type:"allow", pattern:$p}],
      destination:"localSettings"
    }
  }'
fi
```

Make executable: `chmod +x .claude/hooks/permission-request-promote.sh`.

## Step 4 — Generate the PostToolUse Outcome Tracker

`.claude/hooks/post-tool-use-approval-tracker.sh`:

```bash
#!/usr/bin/env bash
# PostToolUse hook: increment the approval counter for the command's KEY
# only on a successful Bash invocation. Flagged failures do not count.
set -euo pipefail

LOG_FILE=".claude/state/approval-log.json"
mkdir -p "$(dirname "$LOG_FILE")"
[ -f "$LOG_FILE" ] || echo '{}' > "$LOG_FILE"

EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')
[ "$TOOL" = "Bash" ] || exit 0

SUCCESS=$(echo "$EVENT" | jq -r '.tool_response.success // false')
[ "$SUCCESS" = "true" ] || exit 0

CMD=$(echo "$EVENT" | jq -r '.tool_input.command // empty')
KEY=$(printf '%s\n' "$CMD" | awk '{print $1}')
[ -z "$KEY" ] && exit 0

# Same two-token narrowing as the PermissionRequest hook — stay in sync
case "$KEY" in
  git|docker|kubectl|gh)
    SECOND=$(printf '%s\n' "$CMD" | awk '{print $2}')
    [ -n "$SECOND" ] && KEY="$KEY $SECOND"
    ;;
esac

CURRENT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE")
NEW=$((CURRENT + 1))
TMP=$(mktemp)
jq --arg k "$KEY" --argjson v "$NEW" '.[$k] = $v' "$LOG_FILE" > "$TMP" && mv "$TMP" "$LOG_FILE"
```

Make executable: `chmod +x .claude/hooks/post-tool-use-approval-tracker.sh`.

Add `.claude/state/` to `.gitignore` if not already present — the approval log is per-machine state, not project history.

## Step 5 — Smoke Test (Before Wiring)

Run each hook standalone with synthetic event payloads. Do not proceed to Step 6 if either fails — see [recovery procedure](bootstrap-loop-detector-hook.md#recovery).

```bash
# Verify both scripts exist and are executable
test -x .claude/hooks/permission-request-promote.sh
test -x .claude/hooks/post-tool-use-approval-tracker.sh

# Reset state for a clean test
rm -f .claude/state/approval-log.json

# Simulate 5 successful 'ls' invocations via the tracker
for i in 1 2 3 4 5; do
  printf '{"tool_name":"Bash","tool_input":{"command":"ls -la"},"tool_response":{"success":true}}' \
    | .claude/hooks/post-tool-use-approval-tracker.sh
done

# Verify the counter
jq '.["ls"]' .claude/state/approval-log.json
# Expect: 5

# Simulate the next PermissionRequest — should return updatedPermissions
printf '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' \
  | .claude/hooks/permission-request-promote.sh \
  | jq '.updatedPermissions.addRules[0].pattern'
# Expect: "Bash(ls *)"

# Hard-deny test — rm should NOT promote regardless of count
echo '{"rm": 999}' > .claude/state/approval-log.json
printf '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/foo"}}' \
  | .claude/hooks/permission-request-promote.sh
# Expect: empty output (falls through to dialog)

# Cleanup
rm -f .claude/state/approval-log.json
```

If any expectation fails, fix the script and re-run before wiring.

## Step 6 — Wire into Harness Config

Only after Step 5 passes:

```bash
jq '.hooks.PermissionRequest = (.hooks.PermissionRequest // []) + [{
  matcher:"Bash",
  hooks:[{type:"command", command:".claude/hooks/permission-request-promote.sh"}]
}] | .hooks.PostToolUse = (.hooks.PostToolUse // []) + [{
  matcher:"Bash",
  hooks:[{type:"command", command:".claude/hooks/post-tool-use-approval-tracker.sh"}]
}]' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

Match `Bash` only on both events. Auto-discovery for `Edit`, `Write`, or `Read` is out of scope — those tools have file-path matchers in static rules, not command-based promotion.

## Step 7 — Document the Threshold and Deny List

Add to `AGENTS.md` (or `.claude/README.md`):

```markdown
## Allowlist auto-discovery

PermissionRequest + PostToolUse hooks promote a Bash command to `permissions.allow`
in `localSettings` after 5 successful manual approvals. Override via env var
`ALLOWLIST_PROMOTE_AFTER`. The following keys never auto-promote regardless of
count: rm, rmdir, curl, wget, mv, dd, sudo, chmod, chown, ssh, scp, rsync,
git push, git reset.
```

## Idempotency

Re-running with the same configuration produces no diff. The PermissionRequest hook only emits `updatedPermissions` when the counter crosses the threshold; once a rule is added to `localSettings`, the harness routes future invocations directly to the allow path and the hook short-circuits naturally. The PostToolUse tracker continues to increment, but no new rules are added.

If the threshold env var changes downward, already-tracked commands may auto-promote on the next request — expected behavior. If it changes upward, no rollback is needed; the existing `localSettings` allow rules remain valid.

## Output Schema

```markdown
# Bootstrap Evidence-Based Allowlist — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | .claude/hooks/permission-request-promote.sh | mode 0755 |
| Created | .claude/hooks/post-tool-use-approval-tracker.sh | mode 0755 |
| Modified | .claude/settings.json | added PermissionRequest + PostToolUse Bash matchers |
| Modified | .gitignore | ignore .claude/state/ |
| Modified | AGENTS.md | added auto-discovery pointer |

Smoke test: 5x ls increments → PermissionRequest emits Bash(ls *) (pass/fail)
Hard-deny test: rm at count 999 → no updatedPermissions (pass/fail)
```

## Related

- [Evidence-Based Allowlist Auto-Discovery](../human/evidence-based-allowlist-auto-discovery.md)
- [Safe Command Allowlisting](../human/safe-command-allowlisting.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
- [Bootstrap Loop Detector Hook](bootstrap-loop-detector-hook.md) — same write-before-wire safety pattern
- [Permission-Gated Commands](../security/permission-gated-commands.md)
