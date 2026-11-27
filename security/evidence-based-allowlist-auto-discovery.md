---
title: "Evidence-Based Allowlist Auto-Discovery for Agents"
term: "Evidence-Based Allowlist Auto-Discovery"
description: "Use Claude Code's PermissionRequest hook to turn repeated successful commands into persistent allow rules, building an allowlist from real usage instead of upfront configuration."
tags:
  - claude
  - technique
  - security
  - automation
  - hooks
aliases:
  - automatic allowlisting
  - usage-based allowlisting
  - dynamic allowlist discovery
last_reviewed: 2026-06-12
maturity: adopted
---

# Evidence-Based Allowlist Auto-Discovery

> Claude Code's `PermissionRequest` hook can turn a command that has run successfully N times into a persistent allow rule, growing an allowlist from real usage instead of upfront configuration.

Evidence-based allowlist auto-discovery builds the allow list incrementally from real agent usage. [Manual allowlisting](safe-command-allowlisting.md) pre-authorizes known-safe commands, but teams must predict the list before they have usage data. Auto-discovery removes that requirement: each successful run of a command increments a counter, and once a command crosses a threshold it is written to the allow list.

## How it works

Claude Code's `PermissionRequest` hook fires before Claude Code shows the permission dialog. When it approves a call (`hookSpecificOutput.decision.behavior: "allow"`), the `updatedPermissions` array inside the same `decision` object can carry an `addRules` entry whose `destination` writes the allow rule to a settings file ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)).

```mermaid
sequenceDiagram
    participant A as Agent
    participant H as PermissionRequest Hook
    participant L as Approval Log
    participant S as settings.json

    A->>H: Requests permission for command
    H->>L: Check approval count
    alt count < N
        H-->>A: Forward to user (show dialog)
        Note over L: On successful run: PostToolUse increments count
    else count >= N
        H->>S: addRules → allow rule
        H-->>A: Auto-approve (no dialog)
    end
```

A `PostToolUse` hook tracks outcomes after execution. The rule lands after a command runs successfully N times. The tracker counts every successful run, whether you approved it in the dialog or an existing rule allowed it.

## The two-hook implementation

`PermissionRequest` is the only hook with an `updatedPermissions` write-back path, per the [Claude Code hooks reference](https://code.claude.com/docs/en/hooks). `PostToolUse` cannot write settings via its return value; it writes to the counter log.

Both hooks run as `command` hooks, which default to a 600-second timeout before Claude Code cancels them ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)) — far more than a `jq` lookup against a local log file needs, so neither the count check nor the increment should ever hit the ceiling.

| Hook | Role | Can write to settings.json via API? |
|------|------|-------------------------------------|
| `PermissionRequest` | Checks count; writes allow rule when threshold met | Yes — via `updatedPermissions` |
| `PostToolUse` | Records outcome; increments counter on success | No — must write to a sidecar log file |

Command hooks receive their event JSON on stdin ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)), so each script reads it once with `INPUT=$(cat)`. Both scripts are sketches to adapt. Test each one by piping a sample event into it, for example `echo '<json>' | .claude/hooks/permission-request.sh`.

### PermissionRequest hook

```bash
#!/bin/bash
# .claude/hooks/permission-request.sh
# Reads success counts; promotes a command prefix to the allowlist after N runs

THRESHOLD=5
LOG_FILE=".claude/approval-log.json"
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

[ -z "$COMMAND" ] && exit 0

# Normalize: key on the first two tokens ("git status" from "git status --short")
KEY=$(echo "$COMMAND" | awk '{print $1, $2}' | sed 's/ *$//')

# Never auto-allow these prefixes; they always fall through to the dialog
NEVER_AUTO_ALLOW=("rm" "rmdir" "curl" "wget" "mv" "dd" "git push")
for blocked in "${NEVER_AUTO_ALLOW[@]}"; do
  case "$KEY " in "$blocked "*) exit 0 ;; esac
done

COUNT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE" 2>/dev/null || echo 0)

if [ "$COUNT" -ge "$THRESHOLD" ]; then
  # Approve the call and add a persistent allow rule to .claude/settings.local.json.
  # updatedPermissions is a field of decision; an addRules entry carries
  # rules[], behavior, and destination.
  jq -n \
    --arg rule "$KEY *" \
    '{
      hookSpecificOutput: {
        hookEventName: "PermissionRequest",
        decision: {
          behavior: "allow",
          updatedPermissions: [{
            type: "addRules",
            rules: [{ toolName: "Bash", ruleContent: $rule }],
            behavior: "allow",
            destination: "localSettings"
          }]
        }
      }
    }'
fi
# Fall through: show dialog as normal
```

### PostToolUse hook (outcome tracker)

```bash
#!/bin/bash
# .claude/hooks/post-tool-use-tracker.sh
# Increments approval counter on successful Bash runs

LOG_FILE=".claude/approval-log.json"
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
# A failed call's tool_response is an error string; a successful Bash call
# returns an object with stdout, stderr, interrupted, and isImage.
SUCCESS=$(echo "$INPUT" | jq -r '
  (.tool_response | type == "object") and (.tool_response.interrupted != true)')

[ "$TOOL" != "Bash" ] && exit 0
[ "$SUCCESS" != "true" ] && exit 0

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
# Same key as the PermissionRequest hook: the first two tokens
KEY=$(echo "$COMMAND" | awk '{print $1, $2}' | sed 's/ *$//')
[ -z "$KEY" ] && exit 0

[ -s "$LOG_FILE" ] || echo '{}' > "$LOG_FILE"
CURRENT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE" 2>/dev/null || echo 0)
NEW=$((CURRENT + 1))
TMP=$(mktemp)
jq --arg k "$KEY" --argjson v "$NEW" '.[$k] = $v' "$LOG_FILE" > "$TMP" && mv "$TMP" "$LOG_FILE"
```

The `PostToolUse` tracker reads `tool_response` by its documented shape. A successful `Bash` call returns an object with `stdout`, `stderr`, `interrupted`, and `isImage`, and a failed call returns the error text as a string ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-input)). There is no `success` field to test.

With a two-token key, five runs of `git status` promote `Bash(git status *)` and nothing wider. The deny check runs before the threshold test, so `git push` reaches the dialog however many times it has run.

## When this backfires

Counter-based auto-promotion assumes past approvals predict future safety. That assumption breaks under several conditions:

- Broad key matching: first-token normalization (`git` from `git status`) counts safe reads toward the same key as destructive variants. The [v2.1.77 Claude Code changelog](https://code.claude.com/docs/en/changelog) noted the related bug of compound bash commands saving a single rule for the full string rather than per-subcommand. Claude Code's own current rule-generation now caps this the other way: approving a compound command saves up to 5 separate subcommand rules rather than one collapsed key ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)) — the platform itself treats per-subcommand fidelity as correct, which is the standard a first-token counter falls short of.
- Scripted or CI runs: automated pipelines can build up approval counts for commands no human ever consciously reviewed, then promote them silently.
- Accidental approvals: five rushed approvals promote a command permanently, and threshold counts do not filter careless clicks.

Mitigations:

- Count full command fingerprints, not just first tokens. The example keys on two tokens; use the full command for high-risk prefixes.
- Maintain an explicit deny list (`rm`, `curl`, `wget`, `git push`, `mv`, `dd`) that always falls through to the dialog. The example checks it before the threshold test.
- For shared or version-controlled allowlists, raise the threshold and require explicit review before any auto-promoted rule lands in `projectSettings`.

## Relationship to static allowlists

Static and evidence-based allowlists are additive, not competing:

| Approach | Best for |
|----------|---------|
| Static allowlist (`settings.json`) | Known-safe commands established upfront |
| Evidence-based auto-discovery | Commands that emerge from real usage |

Claude Code's default auto-approval list has itself grown over releases to include read-only utilities such as `lsof`, `pgrep`, `tput`, `ss`, `fd`, and `fdfind`, per the [Claude Code changelog](https://code.claude.com/docs/en/changelog). The "Yes, don't ask again" built-in is a manual variant; the hook-based approach automates the threshold across sessions.

## Key Takeaways

- Auto-discovery builds the allowlist from real usage, so teams skip predicting the safe-command list before they have data.
- The `PermissionRequest` hook is the only one that can persist an allow rule, via an `updatedPermissions` `addRules` entry inside `hookSpecificOutput.decision`; `PostToolUse` can only write to a sidecar counter log.
- Promote to the allowlist only after N successful runs, and always keep a never-auto-allow deny list (`rm`, `curl`, `git push`, …) that falls through to the dialog.
- Count full command fingerprints, not just first tokens, so a safe read can't promote a destructive variant under the same key.

## Related

- [Safe Command Allowlisting: Reducing Approval Fatigue](safe-command-allowlisting.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks and Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
- [PostToolUse Hook for BSD/GNU Tool Miss Detection](../tool-engineering/posttooluse-bsd-gnu-detection.md)
- [Empirical Baseline: How Developers Configure Agentic AI Coding Tools](../instructions/empirical-baseline-agentic-config.md)
- [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md)
- [Permission Replies That Rewrite Coding-Agent Policy](permission-reply-policy-updates.md) — the same field used to delete deny rules or widen the sandbox
