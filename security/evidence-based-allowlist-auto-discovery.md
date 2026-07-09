---
title: "Evidence-Based Allowlist Auto-Discovery for Agents"
term: "Evidence-Based Allowlist Auto-Discovery"
description: "Use Claude Code's PermissionRequest hook to turn manual approvals into persistent rules, building an allowlist from real usage instead of upfront configuration."
tags:
  - workflows
  - claude
  - technique
  - security
aliases:
  - automatic allowlisting
  - usage-based allowlisting
  - dynamic allowlist discovery
last_reviewed: 2026-06-12
maturity: adopted
---

# Evidence-Based Allowlist Auto-Discovery

> Claude Code's `PermissionRequest` hook turns every manual approval into a persistent rule, growing an allowlist from real usage instead of upfront configuration.

Evidence-based allowlist auto-discovery builds the allow list incrementally from real agent usage. [Manual allowlisting](safe-command-allowlisting.md) pre-authorizes known-safe commands, but teams must predict the list before they have usage data. Auto-discovery removes that requirement: each manual approval increments a counter, and once a command crosses a threshold it is written to the allow list.

## How it works

Claude Code's `PermissionRequest` hook fires before Claude Code shows the permission dialog. When it approves a call (`hookSpecificOutput.decision.behavior: "allow"`), the sibling `updatedPermissions` array can carry an `addRules` entry whose `destination` writes the allow rule to a settings file ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

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
        Note over L: On approval: increment count
    else count >= N
        H->>S: addRules → allow rule
        H-->>A: Auto-approve (no dialog)
    end
```

A `PostToolUse` hook tracks outcomes after execution. The rule lands only after you manually approve a command N times without flagged side effects.

## The two-hook implementation

`PermissionRequest` is the only hook with an `updatedPermissions` write-back path, per the [Claude Code hooks reference](https://code.claude.com/docs/en/hooks). `PostToolUse` cannot write settings via its return value; it writes to the counter log.

Both hooks run as `command` hooks, which default to a 600-second timeout before Claude Code cancels them ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)) — far more than a `jq` lookup against a local log file needs, so neither the count check nor the increment should ever hit the ceiling.

| Hook | Role | Can write to settings.json via API? |
|------|------|-------------------------------------|
| `PermissionRequest` | Checks count; writes allow rule when threshold met | Yes — via `updatedPermissions` |
| `PostToolUse` | Records outcome; increments counter on success | No — must write to a sidecar log file |

### PermissionRequest hook

```bash
#!/bin/bash
# .claude/hooks/permission-request.sh
# Reads approval counts; promotes to allowlist after N approvals

THRESHOLD=5
LOG_FILE=".claude/approval-log.json"
COMMAND=$(echo "$CLAUDE_INPUT" | jq -r '.tool_input.command // empty')

[ -z "$COMMAND" ] && exit 0

# Normalize: use first token as the key (e.g. "git" from "git status --short")
KEY=$(echo "$COMMAND" | awk '{print $1}')
COUNT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE" 2>/dev/null || echo 0)

if [ "$COUNT" -ge "$THRESHOLD" ]; then
  # Approve the call and add a persistent allow rule to .claude/settings.local.json.
  # updatedPermissions is a sibling of decision under hookSpecificOutput; an
  # addRules entry carries a rules[] array and a destination.
  jq -n \
    --arg rule "$KEY *" \
    '{
      hookSpecificOutput: {
        hookEventName: "PermissionRequest",
        decision: { behavior: "allow" },
        updatedPermissions: [{
          type: "addRules",
          destination: "localSettings",
          rules: [{ toolName: "Bash", rule: $rule, behavior: "allow" }]
        }]
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
TOOL=$(echo "$CLAUDE_INPUT" | jq -r '.tool_name // empty')
SUCCESS=$(echo "$CLAUDE_INPUT" | jq -r '.tool_response.success // false')

[ "$TOOL" != "Bash" ] && exit 0
[ "$SUCCESS" != "true" ] && exit 0

COMMAND=$(echo "$CLAUDE_INPUT" | jq -r '.tool_input.command // empty')
KEY=$(echo "$COMMAND" | awk '{print $1}')
[ -z "$KEY" ] && exit 0

touch "$LOG_FILE"
CURRENT=$(jq -r --arg k "$KEY" '.[$k] // 0' "$LOG_FILE" 2>/dev/null || echo 0)
NEW=$((CURRENT + 1))
TMP=$(mktemp)
jq --arg k "$KEY" --argjson v "$NEW" '.[$k] = $v' "$LOG_FILE" > "$TMP" && mv "$TMP" "$LOG_FILE"
```

## When this backfires

Counter-based auto-promotion assumes past approvals predict future safety. That assumption breaks under several conditions:

- Broad key matching: first-token normalization (`git` from `git status`) counts safe reads toward the same key as destructive variants. The [v2.1.77 Claude Code changelog](https://code.claude.com/docs/en/changelog) noted the related bug of compound bash commands saving a single rule for the full string rather than per-subcommand. Claude Code's own current rule-generation now caps this the other way: approving a compound command saves up to 5 separate subcommand rules rather than one collapsed key ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)) — the platform itself treats per-subcommand fidelity as correct, which is the standard a first-token counter falls short of.
- Scripted or CI runs: automated pipelines can build up approval counts for commands no human ever consciously reviewed, then promote them silently.
- Accidental approvals: five rushed approvals promote a command permanently, and threshold counts do not filter careless clicks.

Mitigations:

- Count full command fingerprints, not just first tokens, for high-risk prefixes.
- Maintain an explicit deny list (`rm`, `curl`, `wget`, `git push`, `mv`, `dd`) that always falls through to the dialog.
- For shared or version-controlled allowlists, raise the threshold and require explicit review before any auto-promoted rule lands in `projectSettings`.

```bash
NEVER_AUTO_ALLOW="rm rmdir curl wget git-push mv dd"
for blocked in $NEVER_AUTO_ALLOW; do
  [ "$KEY" = "$blocked" ] && exit 0  # Fall through to dialog
done
```

## Relationship to static allowlists

Static and evidence-based allowlists are additive, not competing:

| Approach | Best for |
|----------|---------|
| Static allowlist (`settings.json`) | Known-safe commands established upfront |
| Evidence-based auto-discovery | Commands that emerge from real usage |

Claude Code's default auto-approval list has itself grown over releases to include read-only utilities such as `lsof`, `pgrep`, `tput`, `ss`, `fd`, and `fdfind`, per the [Claude Code changelog](https://code.claude.com/docs/en/changelog). The "Yes, don't ask again" built-in is a manual variant; the hook-based approach automates the threshold across sessions.

## Key Takeaways

- Auto-discovery builds the allowlist from real usage, so teams skip predicting the safe-command list before they have data.
- The `PermissionRequest` hook is the only one that can persist an allow rule, via `hookSpecificOutput.decision` plus an `updatedPermissions` `addRules` entry; `PostToolUse` can only write to a sidecar counter log.
- Promote to the allowlist only after N flagged-side-effect-free approvals, and always keep a never-auto-allow deny list (`rm`, `curl`, `git push`, …) that falls through to the dialog.
- Count full command fingerprints, not just first tokens, so a safe read can't promote a destructive variant under the same key.

## Related

- [Safe Command Allowlisting: Reducing Approval Fatigue](safe-command-allowlisting.md)
- [Permission-Gated Custom Commands](../security/permission-gated-commands.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks and Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
- [PostToolUse Hook for BSD/GNU Tool Miss Detection](../tool-engineering/posttooluse-bsd-gnu-detection.md)
- [Empirical Baseline: How Developers Configure Agentic AI Coding Tools](../instructions/empirical-baseline-agentic-config.md)
- [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md)
