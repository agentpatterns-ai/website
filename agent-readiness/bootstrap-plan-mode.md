---
title: "Bootstrap Plan Mode Default"
description: "Detect harness, set plan mode as the default permission mode for new sessions, scaffold a plan-review checklist, and wire CI to require plan-mode for unfamiliar repositories."
tags:
  - tool-agnostic
  - workflows
  - safety
aliases:
  - default plan mode
  - read-only first
  - permission-mode plan bootstrap
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-plan-mode/`

# Bootstrap Plan Mode Default

> Set plan mode as the project's default permission mode, scaffold a plan-review checklist, wire headless CI invocations to plan-mode by default. Read-only first; implementation only after plan acceptance.

!!! info "Harness assumption"
    Plan mode is a Claude Code permission mode toggled via `Shift+Tab`, `--permission-mode plan`, or `defaultMode` in `.claude/settings.json` ([docs](https://code.claude.com/docs/en/iam#permission-modes)). Other harnesses with read-only modes (e.g., Cursor's "ask" mode) need analogous configuration. See [`plan-mode`](../workflows/plan-mode.md).

!!! info "Applicability"
    Apply to projects where multi-file changes are common, the codebase is unfamiliar to most contributors, or agents have been observed picking the wrong files to modify. Skip for trivial single-file utility repos where plan-mode overhead exceeds the cost of a bad attempt.

Plan mode forces an agent to explore and propose before modifying — so wrong approaches surface before broken diffs. Setting it as the default makes the read-only-first discipline the path of least resistance instead of an opt-in. Rules from [`plan-mode`](../workflows/plan-mode.md) and [`plan-first-loop`](../workflows/plan-first-loop.md).

## Step 1 — Detect Current Default Mode

```bash
# Claude Code settings
test -f .claude/settings.json && jq '.permissions.defaultMode // "normal"' .claude/settings.json
test -f .claude/settings.local.json && jq '.permissions.defaultMode // empty' .claude/settings.local.json

# Existing CI invocations
grep -rE 'claude .*--permission-mode|claude .*-p' .github/workflows/ scripts/ Makefile justfile 2>/dev/null
```

Decision rules:

- `defaultMode` already set to `plan` → audit it for completeness; skip Step 2
- `defaultMode` set to `acceptEdits` or `bypassPermissions` → ask the user before changing; document the rationale they cite
- No mode set → default is normal mode → proceed

## Step 2 — Configure Project Default

Edit `.claude/settings.json`:

```bash
jq '.permissions.defaultMode = "plan"' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

If `.claude/settings.json` does not exist yet, create it with the minimum:

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

This sets plan mode for new sessions started via the CLI or IDE. Existing sessions are unaffected; users still toggle via `Shift+Tab`.

## Step 3 — Wire Headless / CI Invocations

Audit every headless `claude` invocation. Each must set `--permission-mode` explicitly — relying on `defaultMode` for headless runs creates surprise mode flips when settings change.

```bash
for f in $(grep -rlE 'claude .*-p' .github/workflows/ scripts/ Makefile justfile 2>/dev/null); do
  grep -nE 'claude .*-p' "$f" | grep -v 'permission-mode' \
    && echo "fix: add --permission-mode plan to $f"
done
```

Patch each invocation:

```diff
- claude -p "Analyze the auth module"
+ claude --permission-mode plan -p "Analyze the auth module"
```

Side-effectful headless invocations (commit, deploy, file generation) keep `--permission-mode acceptEdits` and are gated by other checks — see [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md).

## Step 4 — Scaffold the Plan-Review Checklist

Create `.claude/checklists/plan-review.md` so the user (or a paired sub-agent) reviews against a fixed list, not memory:

```markdown
# Plan Review Checklist

Reject the plan if any item is unchecked.

- [ ] The plan identifies the correct files to modify (not adjacent / unrelated files)
- [ ] The approach matches existing codebase patterns (no parallel new abstractions)
- [ ] Scope matches the task — no creep into adjacent refactors
- [ ] Edge cases and error paths are addressed
- [ ] Tests are part of the plan, not deferred
- [ ] Destructive operations (deletions, force-pushes, schema changes) are called out explicitly

If two or more items are unchecked, request a revised plan rather than approving with caveats.
```

Reference: [`plan-mode` §Plan Review Checklist](../workflows/plan-mode.md#plan-review-checklist).

## Step 5 — Document in AGENTS.md

Add a one-line pointer so contributors and agents both know plan mode is the default:

```markdown
## Default permission mode

This project uses **plan mode** as the default. Sessions start read-only — plans must be reviewed and accepted before implementation. Toggle via `Shift+Tab` or `--permission-mode acceptEdits` for established change patterns. See `.claude/checklists/plan-review.md`.
```

## Step 6 — Validate

```bash
# Setting is in place
jq '.permissions.defaultMode' .claude/settings.json    # expect "plan"

# Checklist exists
test -f .claude/checklists/plan-review.md

# Smoke test (interactive only — confirm the status bar shows "⏸ plan mode on")
claude --version >/dev/null && echo "harness available"
```

For headless validation that the mode is honored:

```bash
echo "list files in src/" | claude --permission-mode plan -p
# Expect: model output describes files; no Write or Edit tool calls in transcript
```

## Idempotency

Re-running reads `.claude/settings.json` and only updates `permissions.defaultMode` if not already `plan`. The checklist is created if absent and left alone otherwise.

## Output Schema

```markdown
# Bootstrap Plan Mode Default — <repo>

| Action | File | Notes |
|--------|------|-------|
| Modified | .claude/settings.json | defaultMode set to plan |
| Created | .claude/checklists/plan-review.md | 6-item checklist |
| Modified | <CI files> | added --permission-mode plan |
| Modified | AGENTS.md | added default-mode pointer |

Headless invocations updated: <n>
```

## Recovery

If plan mode is too aggressive for the workflow (high-trust repos, established change patterns), unset rather than re-toggling per session:

```bash
jq 'del(.permissions.defaultMode)' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

Document why in AGENTS.md so the next contributor understands the deviation.

## Related

- [Plan Mode](../workflows/plan-mode.md)
- [The Plan-First Loop](../workflows/plan-first-loop.md)
- [Pre-Execution Codebase Exploration](../workflows/pre-execution-codebase-exploration.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md)
