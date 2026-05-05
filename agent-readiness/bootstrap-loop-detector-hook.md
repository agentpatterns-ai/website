---
title: "Bootstrap Loop Detector Hook"
description: "Detect the harness, generate a PostToolUse hook that tracks per-file edit counts in a session, escalate from nudge to pause to block on threshold, and persist counts safely."
tags:
  - tool-agnostic
  - observability
aliases:
  - edit-count loop detector
  - doom loop detection hook
  - agent loop detection scaffold
---

Packaged as: [`.claude/skills/agent-readiness-bootstrap-loop-detector-hook`](../../.claude/skills/agent-readiness-bootstrap-loop-detector-hook/SKILL.md)

# Bootstrap Loop Detector Hook

> Detect the harness, generate a PostToolUse hook that tracks per-file edit counts in a session, escalate from nudge to pause to block on threshold, persist counts safely.

!!! info "Harness assumption"
    The hook script targets Claude Code's `PostToolUse` event and `.claude/hooks/`/`.claude/state/` paths. Other harnesses with per-tool-call hooks use different formats — translate the input parsing and state path accordingly. See [Assumptions](index.md#assumptions).

A common failure mode in long-running agents is the edit loop: the same file rewritten N times against the same failing test, with each pass making the code worse. [Loop detection](../observability/loop-detection.md) puts a cheap counter at the harness level so the loop is visible and breakable before it consumes the session.

## Step 1 — Detect Harness

```bash
ls -d .claude 2>/dev/null && echo "claude-code"
ls -d .cursor 2>/dev/null && echo "cursor"
ls -d .github/copilot-extension 2>/dev/null && echo "copilot"

# Existing PostToolUse coverage
test -f .claude/settings.json && jq '.hooks.PostToolUse // empty' .claude/settings.json
```

Decision rules:

- **No harness** → ask which tool to target; do not create `.claude/` for a Cursor project
- **Existing PostToolUse loop detector** → audit ([`audit-hooks-coverage`](audit-hooks-coverage.md)) and merge; do not duplicate
- **Slow PostToolUse hook present** → warn the user; loop detection adds <50ms but stacks behind any existing slow hook

## Step 2 — Choose Storage

| Scenario | Storage |
|----------|---------|
| Short interactive sessions | in-memory shell variable, dies with the session |
| Resumable / long-running sessions | JSON sidecar at `.claude/state/edit-counts.json` (gitignored) |
| Multi-agent / parallel sessions | per-session subdirectory: `.claude/state/<session-id>/edit-counts.json` |

Default: JSON sidecar with the session ID prefix. Add `.claude/state/` to `.gitignore` if not already covered.

## Step 3 — Generate the Hook Script

`.claude/hooks/loop-detector.sh`:

```bash
#!/usr/bin/env bash
# PostToolUse hook: track per-file edit counts; nudge → pause → block on threshold.
# Counts persist for the duration of the session (keyed by SESSION_ID env var if present).
set -euo pipefail

EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')
[[ "$TOOL" =~ ^(Edit|Write|MultiEdit)$ ]] || exit 0

FILE=$(echo "$EVENT" | jq -r '.tool_input.file_path // empty')
[[ -z "$FILE" ]] && exit 0

SESSION="${CLAUDE_SESSION_ID:-default}"
STATE=".claude/state/${SESSION}/edit-counts.json"
mkdir -p "$(dirname "$STATE")"
[[ -f "$STATE" ]] || echo '{}' > "$STATE"

COUNT=$(jq --arg f "$FILE" '(.[$f] // 0) + 1' "$STATE")
jq --arg f "$FILE" --argjson n "$COUNT" '.[$f] = $n' "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"

# Threshold ladder
NUDGE=${LOOP_NUDGE_AFTER:-3}
PAUSE=${LOOP_PAUSE_AFTER:-5}
BLOCK=${LOOP_BLOCK_AFTER:-8}

if   [[ $COUNT -ge $BLOCK ]]; then
  printf '{"action":"block","reason":"%s edited %s times — escalating to human","file":"%s","count":%s}\n' "$FILE" "$COUNT" "$FILE" "$COUNT"
  exit 2
elif [[ $COUNT -ge $PAUSE ]]; then
  printf '{"action":"pause","reason":"%s edited %s times — write the failure mode in one sentence and propose a different approach","file":"%s","count":%s}\n' "$FILE" "$COUNT" "$FILE" "$COUNT"
  exit 2
elif [[ $COUNT -ge $NUDGE ]]; then
  printf '{"action":"nudge","reason":"%s edited %s times — re-read the original spec before another edit","file":"%s","count":%s}\n' "$FILE" "$COUNT" "$FILE" "$COUNT"
fi
```

Make executable: `chmod +x .claude/hooks/loop-detector.sh`.

## Step 4 — Wire into Harness Config

For Claude Code, splice into `.claude/settings.json`:

```bash
jq '.hooks.PostToolUse = (.hooks.PostToolUse // []) + [{
  matcher:"Edit|Write|MultiEdit",
  hooks:[{type:"command", command:".claude/hooks/loop-detector.sh"}]
}]' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

Important: match `Edit|Write|MultiEdit` only. Do not fire on `Read`, `Grep`, `Bash`, or other non-mutating tools.

## Step 5 — Add Doom-Loop Detection (Optional)

If the project runs `Bash` heavily and produces stable error signatures, also detect identical-error doom loops:

```bash
# In a separate hook or appended to the same one:
LAST_ERR_FILE=".claude/state/${SESSION}/last-stderr.sha"
if [[ "$TOOL" == "Bash" ]]; then
  STDERR=$(echo "$EVENT" | jq -r '.tool_response.stderr // empty')
  [[ -z "$STDERR" ]] && exit 0
  HASH=$(echo "$STDERR" | shasum | awk '{print $1}')
  PREV=$(cat "$LAST_ERR_FILE" 2>/dev/null || echo "")
  if [[ "$HASH" == "$PREV" ]]; then
    REPEAT=$(jq -r '.repeat // 0' "$LAST_ERR_FILE.json" 2>/dev/null || echo 0)
    REPEAT=$((REPEAT + 1))
    echo "{\"hash\":\"$HASH\",\"repeat\":$REPEAT}" > "$LAST_ERR_FILE.json"
    if [[ $REPEAT -ge 3 ]]; then
      printf '{"action":"pause","reason":"identical Bash error %s times — change approach"}\n' "$REPEAT"
      exit 2
    fi
  else
    echo "$HASH" > "$LAST_ERR_FILE"
  fi
fi
```

## Step 6 — Smoke Test

```bash
mkdir -p .claude/state/smoke
CLAUDE_SESSION_ID=smoke

# Simulate 4 edits to the same file
for i in 1 2 3 4; do
  echo "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"/tmp/x.py\"}}" \
    | CLAUDE_SESSION_ID=smoke .claude/hooks/loop-detector.sh
done
# Expect: silent, silent, nudge action, nudge action

rm -rf .claude/state/smoke
```

## Step 7 — Document Thresholds

Add to `AGENTS.md` (or to a `.claude/README.md` if present):

```markdown
## Loop detection

PostToolUse hook tracks per-file edits per session. Defaults: nudge at 3, pause at 5, block at 8.
Override via env vars `LOOP_NUDGE_AFTER`, `LOOP_PAUSE_AFTER`, `LOOP_BLOCK_AFTER`.
```

## Idempotency

Re-running with the same configuration produces no diff. If thresholds change, the hook script updates; counts are session-local so existing state is not invalidated.

## Output Schema

```markdown
# Bootstrap Loop Detector Hook — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | .claude/hooks/loop-detector.sh | mode 0755 |
| Modified | .claude/settings.json | added PostToolUse Edit\|Write\|MultiEdit matcher |
| Modified | .gitignore | ignore .claude/state/ |
| Modified | AGENTS.md | added loop-detection pointer |

Smoke test: nudge fires at edit 3 (pass/fail)
```

## Related

- [Loop Detection](../observability/loop-detection.md)
- [Agent Loop Middleware](../agent-design/agent-loop-middleware.md)
- [Behavioral Drivers of Agent Success](../agent-design/behavioral-drivers-agent-success.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
