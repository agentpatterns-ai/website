---
title: "Bootstrap Hooks Scaffold"
description: "Detect harness, generate a full .claude/hooks/ directory with no-op stubs for every lifecycle event with inline guidance, register all events in settings.json, and hand off event-specific deep dives to dedicated runbooks."
tags:
  - tool-agnostic
  - testing-verification
aliases:
  - scaffold lifecycle hooks
  - hooks directory bootstrap
  - PreToolUse PostToolUse SessionStart scaffold
---

# Bootstrap Hooks Scaffold

> Detect harness, generate a full `.claude/hooks/` directory with no-op stubs for every lifecycle event, register them in `settings.json`, hand off event-specific deep dives to dedicated runbooks.

[`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) and [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) cover the two highest-leverage events. This runbook is the broader scaffold — it lays down stubs for the remaining lifecycle events so the harness has a place for every kind of enforcement to land. Paired remediation for [`audit-hooks-coverage`](audit-hooks-coverage.md). Source: [hooks lifecycle](../tools/claude/hooks-lifecycle.md).

## Step 1 — Detect Current State

```bash
test -d .claude/hooks && ls -la .claude/hooks/
test -f .claude/settings.json && jq '.hooks // empty' .claude/settings.json
```

Decision rules:

- **No `.claude/`** → ask the user which harness to target; do not create `.claude/` for a Cursor or Aider project (parallel scaffolders for those harnesses are a separate concern)
- **Existing hooks for some events** → only generate stubs for the missing events; never overwrite
- **Existing Stop or PostToolUse loop detector** → defer to [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) and [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md); link rather than duplicate

## Step 2 — Lay Down the Hook Directory

```bash
mkdir -p .claude/hooks .claude/state
echo "/state/" > .claude/.gitignore
```

## Step 3 — Generate Per-Event Stubs

Each stub is a no-op by default, reads the event payload from stdin, and contains inline guidance comments showing where to add real enforcement.

### `pre-tool-use.sh` — Block destructive operations

```bash
#!/usr/bin/env bash
# PreToolUse: runs before each tool call. Exit 2 to block.
# Common uses: deny rules for paths/commands the harness allowlist does not cover,
# rate limiting, semantic input validation.
set -euo pipefail

EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')

# Example — block edits to vendored directories
# if [[ "$TOOL" =~ ^(Edit|Write|MultiEdit)$ ]]; then
#   FILE=$(echo "$EVENT" | jq -r '.tool_input.file_path // empty')
#   if [[ "$FILE" == *"/vendor/"* || "$FILE" == *"/node_modules/"* ]]; then
#     echo '{"action":"block","reason":"refusing edit under vendored path"}'
#     exit 2
#   fi
# fi

exit 0
```

### `post-tool-use.sh` — Format and lint after edits

```bash
#!/usr/bin/env bash
# PostToolUse: runs after each tool call. Exit 0 to continue.
# Common uses: formatter, lint, structural checks on the result, telemetry.
set -euo pipefail

EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')

# Example — run prettier on edited files
# if [[ "$TOOL" =~ ^(Edit|Write|MultiEdit)$ ]]; then
#   FILE=$(echo "$EVENT" | jq -r '.tool_input.file_path // empty')
#   case "$FILE" in
#     *.ts|*.tsx|*.js|*.jsx|*.json) bunx prettier --write "$FILE" >/dev/null 2>&1 || true ;;
#   esac
# fi

exit 0
```

### `user-prompt-submit.sh` — Pre-process / annotate user input

```bash
#!/usr/bin/env bash
# UserPromptSubmit: runs when the user submits a prompt. Exit 2 to block.
# Common uses: prompt-injection screening, secret scanning of pasted content,
# auto-attaching context (current branch, recent issues), enforcing ticket prefixes.
set -euo pipefail

EVENT="$(cat)"
PROMPT=$(echo "$EVENT" | jq -r '.prompt // empty')

# Example — block prompts that paste live tokens
# if echo "$PROMPT" | grep -qE 'sk-[a-zA-Z0-9]{32,}|ghp_[A-Za-z0-9]{36,}|xoxb-[0-9a-zA-Z-]{10,}'; then
#   echo '{"action":"block","reason":"prompt contains a credential pattern; rotate and retry without it"}'
#   exit 2
# fi

exit 0
```

### `session-start.sh` — Warm context on session begin

```bash
#!/usr/bin/env bash
# SessionStart: runs once when a session opens. Exit 0 to continue.
# Common uses: refresh derived files, attach a short status line (current branch,
# uncommitted changes, recent CI status), check init.sh has run, warm caches.
set -euo pipefail

# Example — emit a short status block the agent will see
# echo "{\"action\":\"context\",\"context\":\"branch=$(git rev-parse --abbrev-ref HEAD), uncommitted=$(git status --porcelain | wc -l)\"}"

exit 0
```

### `pre-compact.sh` — Preserve state before compaction

```bash
#!/usr/bin/env bash
# PreCompact: runs before the agent compacts conversation history. Exit 0 to continue.
# Common uses: write progress.txt, stash feature-state.json, dump a summary the
# post-compact handoff can re-attach.
set -euo pipefail

# Example — append a progress note
# echo "$(date -Iseconds): pre-compact checkpoint" >> .claude/state/progress.txt

exit 0
```

### `post-compact.sh` — Re-attach state after compaction

```bash
#!/usr/bin/env bash
# PostCompact: runs after the agent compacts conversation history.
# Common uses: re-inject load-bearing context that compaction dropped (current
# task, feature spec pointer, recent decisions).
set -euo pipefail

# Example — re-attach progress.txt
# if [[ -s .claude/state/progress.txt ]]; then
#   echo "{\"action\":\"context\",\"context\":\"$(tail -20 .claude/state/progress.txt | jq -Rs .)\"}"
# fi

exit 0
```

Make every stub executable:

```bash
chmod +x .claude/hooks/*.sh
```

## Step 4 — Register in settings.json

Splice each event into `.claude/settings.json` if not already present:

```bash
add_hook() {
  local event="$1" matcher="$2" cmd="$3"
  jq --arg ev "$event" --arg m "$matcher" --arg c "$cmd" '
    .hooks[$ev] = (.hooks[$ev] // []) |
    if (.hooks[$ev] | any(.hooks[]?.command == $c)) then . else
      .hooks[$ev] += [{matcher:$m, hooks:[{type:"command", command:$c}]}]
    end
  ' .claude/settings.json > .claude/settings.json.tmp \
    && mv .claude/settings.json.tmp .claude/settings.json
}

add_hook PreToolUse "Edit|Write|MultiEdit|Bash" .claude/hooks/pre-tool-use.sh
add_hook PostToolUse "Edit|Write|MultiEdit"     .claude/hooks/post-tool-use.sh
add_hook UserPromptSubmit "*"                   .claude/hooks/user-prompt-submit.sh
add_hook SessionStart "*"                       .claude/hooks/session-start.sh
add_hook PreCompact "*"                         .claude/hooks/pre-compact.sh
add_hook PostCompact "*"                        .claude/hooks/post-compact.sh
```

The `Stop` event and the `PostToolUse` loop-detector matcher are handled by the dedicated runbooks — do not stub them here.

## Step 5 — Run the Specialized Bootstraps

After the scaffold is in place:

1. [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) — Stop-event verification gate (highest-leverage hook)
2. [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) — PostToolUse edit-count detector

These runbooks add their hooks alongside the stubs from this scaffold; they do not conflict.

## Step 6 — Smoke Test

```bash
for hook in .claude/hooks/*.sh; do
  echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/x"}}' | "$hook" >/dev/null \
    && echo "$hook: OK" \
    || echo "$hook: FAIL exit=$?"
done
```

Every stub returns 0 by default; failures indicate a bash error in the file.

## Step 7 — Document in AGENTS.md

```markdown
## Lifecycle hooks

Stubs in `.claude/hooks/` for every event. See `.claude/settings.json` for which are registered. Real enforcement lives in:
- `.claude/hooks/pre-tool-use.sh` — destructive-operation guards
- `.claude/hooks/pre-completion-check.sh` — pre-completion checklist (see `.claude/checklists/`)
- `.claude/hooks/loop-detector.sh` — edit-count loop detection
```

## Idempotency

Re-running adds missing stubs; never overwrites existing ones. The `add_hook` helper is duplicate-safe (checks for the command before appending).

## Output Schema

```markdown
# Bootstrap Hooks Scaffold — <repo>

| Action | File | Mode | Registered |
|--------|------|:----:|:----------:|
| Created | .claude/hooks/pre-tool-use.sh | 0755 | ✅ |
| Created | .claude/hooks/post-tool-use.sh | 0755 | ✅ |
| Created | .claude/hooks/user-prompt-submit.sh | 0755 | ✅ |
| Created | .claude/hooks/session-start.sh | 0755 | ✅ |
| Created | .claude/hooks/pre-compact.sh | 0755 | ✅ |
| Created | .claude/hooks/post-compact.sh | 0755 | ✅ |
| Modified | .claude/settings.json | - | <n> entries added |

Smoke test: <n>/<n> stubs return 0
Next: bootstrap-precompletion-hook, bootstrap-loop-detector-hook
```

## Related

- [Hooks Lifecycle](../tools/claude/hooks-lifecycle.md)
- [Hooks vs Prompts](../verification/hooks-vs-prompts.md)
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md)
- [Bootstrap Loop Detector Hook](bootstrap-loop-detector-hook.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
