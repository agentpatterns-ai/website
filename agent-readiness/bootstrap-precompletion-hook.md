---
title: "Bootstrap Pre-Completion Hook"
description: "Detect existing CI checks, generate a Stop-event hook that runs them deterministically, ship a checklist file with severity and remediation hints, and wire into the harness."
tags:
  - tool-agnostic
  - testing-verification
aliases:
  - pre-completion checklist hook
  - Stop event hook scaffold
  - completion gate scaffold
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-precompletion-hook/`

# Bootstrap Pre-Completion Hook

> Detect existing CI checks, generate a Stop-event hook that runs them, ship a checklist with severity and remediation hints, wire into the harness.

!!! info "Harness assumption"
    The hook script targets Claude Code's `Stop` event and `.claude/hooks/`/`.claude/checklists/` paths. Cursor and other harnesses with task-end events use a different file format — translate the script's input parsing and checklist location accordingly. See [Assumptions](index.md#assumptions).

!!! warning "Safety: write before wire"
    Create the hook script on disk, `chmod +x`, **and smoke-test it standalone** before adding the entry to `settings.json`. A registered-but-missing or registered-but-broken hook exits non-zero — Claude Code reads exit 2 as "block," and every subsequent tool call (including the one that would write the missing script) is blocked. The step ordering below is load-bearing: Step 5 (smoke test) precedes Step 6 (wire). See [Recovery](#recovery) if a session is already deadlocked.

The [pre-completion checklist](../verification/pre-completion-checklists.md) is the harness gate that holds the agent at task boundary, runs deterministic checks, and either lets the agent exit or hands back failures. This runbook generates one from the project's existing CI config — never inventing checks.

## Step 1 — Detect Harness and Existing Checks

```bash
# Harness in use
ls -d .claude .cursor .github/copilot-extension 2>/dev/null

# Existing CI checks (the source for the checklist)
find .github/workflows -name "*.y*ml" -exec grep -lE "run:" {} \;
test -f Makefile && grep -E "^(test|lint|check|verify):" Makefile
test -f justfile && grep -E "^(test|lint|check|verify)" justfile
test -f package.json && jq -r '.scripts | to_entries[] | select(.key | test("test|lint|check|verify")) | "\(.key): \(.value)"' package.json
test -f pyproject.toml && grep -E "^(test|lint|format|check)" pyproject.toml
test -f .pre-commit-config.yaml && yq '.repos[].hooks[].id' .pre-commit-config.yaml

# Existing pre-completion gate (do not overwrite)
test -f .claude/settings.json && jq '.hooks.Stop // empty' .claude/settings.json
```

Decision rules:

- **No harness directory** → ask the user which tool the project uses; do not create `.claude/` if the project uses Cursor
- **Stop hook already wired** → audit it ([`audit-hooks-coverage`](audit-hooks-coverage.md)); skip generation if clean
- **No discoverable checks** → no CI workflows, no `Makefile`/`justfile` targets, no `package.json` scripts, no `.pre-commit-config.yaml`. The hook has nothing to run. Lowest-overhead path: add a `Makefile` target wrapping the project's lint/test commands and re-run this runbook. Defer if the project genuinely has no automated checks; a pre-completion hook with nothing to run is theatre.

## Step 2 — Inventory Checks by Task Type

Map discovered checks to task type. The hook chooses the checklist based on what the agent touched in the session:

| Task type | Trigger | Checks |
|-----------|---------|--------|
| coding | files touched under `src/`, `lib/`, `pkg/` | tests pass, lint clean, no `TODO`/`FIXME` introduced, no placeholder stubs |
| docs | files touched under `docs/` | link-check, frontmatter present, build succeeds |
| infra | files touched under `infra/`, `terraform/`, `.github/workflows/` | terraform validate, action lint, secret scan |
| research | only `Read`, `Grep` tool calls | sources cited, claims attributable |

Use the project's actual commands. If `pytest` is the discovered runner, the coding-tasks check is `pytest -q`, not a generic stub.

## Step 3 — Generate the Hook Script

For Claude Code: `.claude/hooks/pre-completion-check.sh`. For Cursor: `.cursor/hooks/pre-completion.sh`. Adapt the input parsing per harness format.

```bash
#!/usr/bin/env bash
# Stop-event pre-completion hook: runs the checklist matching the session task type.
# Exit 2 blocks the agent; structured JSON on stdout describes the failure to the harness.
set -euo pipefail

EVENT="$(cat)"
TASK_TYPE="$(echo "$EVENT" | jq -r '.task_type // "coding"')"
CHECKLIST=".claude/checklists/${TASK_TYPE}.json"

[[ -f "$CHECKLIST" ]] || { echo '{"action":"allow","reason":"no checklist for task type"}'; exit 0; }

FAILED=()
while read -r check; do
  ID=$(echo "$check" | jq -r '.id')
  CMD=$(echo "$check" | jq -r '.cmd')
  SEV=$(echo "$check" | jq -r '.severity')
  FIX=$(echo "$check" | jq -r '.fix')
  if ! eval "$CMD" >/dev/null 2>&1; then
    FAILED+=("$(jq -nc --arg id "$ID" --arg sev "$SEV" --arg fix "$FIX" '{id:$id,severity:$sev,fix:$fix}')")
  fi
done < <(jq -c '.checks[]' "$CHECKLIST")

if [[ ${#FAILED[@]} -eq 0 ]]; then
  echo '{"action":"allow"}'
  exit 0
fi

# Block if any check is severity=block
if printf '%s\n' "${FAILED[@]}" | jq -es 'any(.[]; .severity=="block")' | grep -q true; then
  printf '{"action":"block","failures":[%s]}\n' "$(IFS=,; echo "${FAILED[*]}")"
  exit 2
fi

printf '{"action":"warn","failures":[%s]}\n' "$(IFS=,; echo "${FAILED[*]}")"
exit 0
```

Make executable: `chmod +x .claude/hooks/pre-completion-check.sh`.

## Step 4 — Generate the Checklist Files

`.claude/checklists/coding.json`:

```json
{
  "task_type": "coding",
  "checks": [
    {"id": "tests", "cmd": "<discovered test command>", "severity": "block",
     "fix": "Run failing test in isolation; read output; fix the cause, not the symptom."},
    {"id": "lint", "cmd": "<discovered lint command>", "severity": "block",
     "fix": "Run the lint --fix variant if available, then re-verify."},
    {"id": "no-todo-introduced", "cmd": "! git diff --cached -U0 -- '*.py' '*.ts' '*.go' | grep -E '^\\+.*\\b(TODO|FIXME)\\b'", "severity": "block",
     "fix": "Replace placeholders with real implementation or remove the change."},
    {"id": "no-stubs", "cmd": "! git diff --cached -U0 | grep -E '^\\+\\s*(pass|raise NotImplementedError|throw new Error\\(.unimplemented.\\))\\s*$'", "severity": "block",
     "fix": "Implement the function or remove it."}
  ]
}
```

`.claude/checklists/docs.json`:

```json
{
  "task_type": "docs",
  "checks": [
    {"id": "build", "cmd": "<docs build command>", "severity": "block",
     "fix": "Read the build output; fix the syntax or link error reported."},
    {"id": "links", "cmd": "<link-check command>", "severity": "warn",
     "fix": "Replace broken links or remove."},
    {"id": "frontmatter", "cmd": "<frontmatter linter>", "severity": "block",
     "fix": "Add the missing frontmatter field reported by the linter."}
  ]
}
```

Substitute discovered commands into the `cmd` fields. Do not ship the placeholder text.

## Step 5 — Smoke Test (Before Wiring)

Run the hook script standalone with a synthetic event payload **before** registering it in `settings.json`. If this step fails, fix the script — do not proceed to Step 6 with a broken script.

```bash
# Verify the file exists and is executable
test -x .claude/hooks/pre-completion-check.sh || { echo "FAIL: hook missing or not executable"; exit 1; }

# Pass case — checklist allows
echo '{"task_type":"coding"}' | .claude/hooks/pre-completion-check.sh
# Expect: {"action":"allow"} with exit 0

# Fail case — checklist blocks (use a tmp file outside the repo to avoid staging side effects)
TMP=$(mktemp); echo '# TODO: nothing' > "$TMP"; git add -N "$TMP" 2>/dev/null
echo '{"task_type":"coding"}' | .claude/hooks/pre-completion-check.sh
# Expect: {"action":"block",...} with exit 2
rm -f "$TMP"
```

Both invocations must produce structured JSON. If the script exits with an unhandled error, the harness will read it as a block on every Stop event once wired — fix before proceeding.

## Step 6 — Wire into Harness Config

Only after Step 5 passes. For Claude Code, edit `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {"type": "command", "command": ".claude/hooks/pre-completion-check.sh"}
        ]
      }
    ]
  }
}
```

If the file exists, merge — do not overwrite. Use `jq` to splice:

```bash
jq '.hooks.Stop = (.hooks.Stop // []) + [{matcher:"*", hooks:[{type:"command", command:".claude/hooks/pre-completion-check.sh"}]}]' \
  .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

For Cursor or other harnesses, follow the equivalent registration mechanism for that tool.

## Step 7 — Document in AGENTS.md

Add a one-line pointer so the agent knows the gate exists:

```markdown
## Verification gate

A pre-completion hook runs the project checklist on Stop. See `.claude/checklists/` for what is enforced.
```

## Recovery

If a hook is wired into `settings.json` but the script is missing, broken, or non-executable, the harness blocks every tool call on the relevant event and the agent cannot fix it from inside the session. Break the loop from outside:

1. Open `.claude/settings.json` in an editor that does not go through the agent (e.g., open the file directly in the IDE, `code .claude/settings.json`, or any external editor)
2. Remove the broken Stop hook entry from `.hooks.Stop[]` (or temporarily empty the array)
3. Save and resume the agent — it can now read and write files normally
4. Restart from Step 5 (smoke test) before re-wiring

The same recovery applies if a script is missing the executable bit or has a syntax error — the harness will read non-zero exit as block until the entry is removed.

## Idempotency

Re-running merges new checks into existing checklists; never overwrites. If a check ID already exists, leave it alone unless the discovered command changed.

## Output Schema

```markdown
# Bootstrap Pre-Completion Hook — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | .claude/hooks/pre-completion-check.sh | mode 0755 |
| Created | .claude/checklists/coding.json | <n> checks |
| Created | .claude/checklists/docs.json | <n> checks |
| Modified | .claude/settings.json | added Stop hook entry |
| Modified | AGENTS.md | added verification-gate pointer |

Smoke test: <pass/fail>
```

## Related

- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Hooks vs Prompts](../verification/hooks-vs-prompts.md)
- [Hooks Lifecycle](../tools/claude/hooks-lifecycle.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
