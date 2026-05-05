---
title: "Audit Confirmation Gate Logs"
description: "Inventory consequential actions an agent can take, validate that each one is gated, audit the gate-decision log for action-data fidelity and rejection-pattern signals, and detect the alert-fatigue and Lies-in-the-Loop failure modes that defeat gates in practice."
tags:
  - tool-agnostic
  - security
  - human-factors
aliases:
  - confirmation gate audit
  - human-in-the-loop gate audit
  - approval gate log audit
---

Packaged as: `.claude/skills/agent-readiness-audit-confirmation-gate-logs/`

# Audit Confirmation Gate Logs

> Inventory consequential actions, validate each one is gated, audit the gate-decision log for fidelity and pattern signals, detect alert fatigue and Lies-in-the-Loop bypass.

!!! info "Harness assumption"
    The runbook treats the gate as application-layer: a function or middleware the agent's tool calls flow through. Where the harness implements gates as PreToolUse hooks (Claude Code) or as platform-level approval prompts (Cursor, Copilot, Bedrock AgentCore), the inventory step adapts to those surfaces. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Run this audit when the agent can take **send / purchase / delete / share / modify-auth** actions per the consequential-action taxonomy in [Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md). Agents whose tool surface is read-only or filesystem-bounded can defer this audit to the next time write capabilities expand.

[Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md) documents the failure mode the audit targets: a gate that exists at code level but fails at human level — fatigue-driven rubber-stamping, summaries that conceal injection artifacts, headless pipelines that bypass the gate, and Lies-in-the-Loop dialog manipulation. This audit walks the gate definition, the gate decision log, and the rejection patterns to surface those failures before they ship a bad action.

## Step 1 — Enumerate Consequential Actions

```bash
# Tools and MCP methods that match the consequential-action taxonomy
grep -rEn "send_(email|message|notification)|publish|post_to|notify|alert" \
  .claude/skills/*/SKILL.md .claude/agents/*.md tools/ src/ 2>/dev/null

grep -rEn "delete|drop_table|rm[_-]rf|destroy|terminate|force.push" \
  .claude/skills/*/SKILL.md .claude/agents/*.md tools/ src/ 2>/dev/null

grep -rEn "purchase|charge|create_(invoice|subscription)|payment|stripe\." \
  tools/ src/ 2>/dev/null

grep -rEn "share|grant_(access|permission)|invite|publish_(repo|gist)" \
  tools/ src/ 2>/dev/null

grep -rEn "rotate_(token|credential|secret)|create_(api_key|oauth)|set_(role|policy)" \
  tools/ src/ 2>/dev/null
```

For each hit, record: tool name, file:line, category (send / purchase / delete / share / modify-auth). The output is the gate-coverage denominator — every entry must show up gated in Step 2.

## Step 2 — Validate Each Action Is Gated

```bash
# Look for gate wrappers on each consequential action
for tool in $(jq -r '.allow[]?' .claude/settings.json 2>/dev/null); do
  case "$tool" in
    *delete*|*publish*|*send*|*rotate*|*purchase*)
      grep -nE "confirm|approve|gate|prompt_user|require_confirmation" \
        $(grep -rl "$tool" tools/ src/ 2>/dev/null) 2>/dev/null \
        || echo "UNGATED: $tool"
      ;;
  esac
done

# PreToolUse hook coverage for consequential matchers
test -f .claude/settings.json && \
  jq '.hooks.PreToolUse[]? | {matcher, command: .hooks[].command}' .claude/settings.json
```

A consequential action with no gate wrapper and no PreToolUse hook matching it is a **high-severity finding**. Per [Confirmation Gates §Placement in the Defense Stack](../security/human-in-the-loop-confirmation-gates.md), gates are the last layer; their absence on irreversible actions makes a successful injection unrecoverable.

## Step 3 — Validate the Gate Surfaces Exact Action Data

Read the gate implementation and confirm it surfaces verbatim values, not summaries. Pattern check:

```bash
# Gate code that prints summaries instead of raw fields → finding
grep -nE "f\"forwarding to .*\"|format\(.*recipient.*\)|summary\s*=" \
  $(grep -rl "confirm_send\|require_confirmation\|gate(" tools/ src/) 2>/dev/null
```

[Confirmation Gates §What to Surface at Confirmation](../security/human-in-the-loop-confirmation-gates.md) is explicit: "show the exact action and exact data — not a summary." A gate that prints "forwarding to a contact" instead of `attacker@external.com` is the Lies-in-the-Loop failure mode by design. Flag any gate that:

- Truncates recipient lists, paths, or identifiers below their full value
- Renders Markdown or HTML in the dialog (allows attacker to push fields out of view)
- Defaults to approval (`[Y/n]` instead of `[y/N]`), or auto-approves on timeout

## Step 4 — Audit the Gate Decision Log

Per [Confirmation Gates §Logging Confirmed and Rejected Actions](../security/human-in-the-loop-confirmation-gates.md), every gate decision must be logged independently of the agent transcript with: full action, full data, timestamp, decision (approved / rejected), reviewer identity.

```bash
# Locate the decision log
find . -type f \( -name "*gate*.log*" -o -name "approvals.jsonl" -o -name "confirmation*.log*" \) 2>/dev/null

# Schema check — required fields
head -100 $(find . -type f -name "*gate*.log*" 2>/dev/null | head -1) \
  | jq -e '.action and .data and .timestamp and .decision and .reviewer' \
  || echo "FINDING: log missing required fields"

# Independence check — log not co-located with transcript
test -d .claude/transcripts && \
  find .claude/transcripts -name "*gate*" \
  && echo "FINDING: gate log inside transcript dir — not independent"
```

Findings:

- **No log present** → high. The gate cannot be audited and rejection patterns cannot be analysed.
- **Missing fields** → medium. Reconstruct from the surrounding agent transcript only if the timestamp matches; otherwise unrecoverable.
- **Log co-located with transcript** → medium. Transcript truncation or corruption takes the log with it.

## Step 5 — Detect Alert-Fatigue Patterns

[Confirmation Gates §When This Backfires](../security/human-in-the-loop-confirmation-gates.md) identifies fatigue as the dominant gate-failure mode, with the [Agent Approval Fatigue Problem](https://molten.bot/blog/agent-approval-fatigue/) reference and Rippling's T10 threat classification. Compute fatigue indicators from the log:

```python
import json
from collections import Counter
from datetime import timedelta

events = [json.loads(l) for l in open("approvals.jsonl")]
total = len(events)
approved = sum(1 for e in events if e["decision"] == "approved")
median_review_ms = sorted(e["review_ms"] for e in events)[total // 2] if total else 0

# Approval rate above 95% with median review time below 2 s = rubber-stamping
if approved / total > 0.95 and median_review_ms < 2000:
    print("FINDING high: rubber-stamp pattern — gate is performative")

# Spike volumes that swamp the queue
per_hour = Counter(e["timestamp"][:13] for e in events)
peak = max(per_hour.values()) if per_hour else 0
if peak > 60:
    print(f"FINDING medium: queue flood — peak {peak}/hour invites flooding attack (T10)")
```

Decision rules:

| Indicator | Threshold | Severity |
|-----------|-----------|----------|
| Approval rate | > 95% with median review < 2 s | high — rubber-stamping |
| Peak gate frequency | > 60/hour | medium — flooding-attack surface |
| Same action approved repeatedly without inspection | > 10 identical approvals/day | medium — pattern blindness |
| Action approved after rejection within 30 s | any | high — coercion or confusion |

## Step 6 — Detect Lies-in-the-Loop Surface

The [Bypassing AI Agent Defenses With Lies-In-The-Loop](https://checkmarx.com/zero-post/bypassing-ai-agent-defenses-with-lies-in-the-loop/) demonstration exploits dialog rendering: injected content pushes dangerous arguments out of view or exploits Markdown rendering. Audit the dialog renderer:

```bash
# Markdown / HTML rendering in confirmation dialogs
grep -nE "render_markdown|markdown\.render|html\.escape" \
  $(grep -rl "confirm_\|gate(" tools/ src/) 2>/dev/null

# Field truncation by length without escape — visible artifact loss
grep -nE "\[:[0-9]+\]|truncate\(|\.\.\." \
  $(grep -rl "confirm_\|gate(" tools/ src/) 2>/dev/null
```

Findings:

- **Markdown or HTML rendered in dialog body** → high. Render fields as plain text only.
- **Field truncation in dialog** → medium. Either show the full value or split into multiple visible lines.
- **Approved action does not equal shown action** → critical. Add a post-approval equality check between the value displayed and the value committed.

## Step 7 — Validate Headless-Pipeline Posture

Per the When-This-Backfires entry on headless pipelines, gates that block in headless mode either halt automation or are silently bypassed. The correct posture: gates fail closed in headless mode, and the project documents which actions are intentionally out of reach in headless runs.

```bash
# Look for headless detection that bypasses the gate
grep -rnE "if.*(non.?interactive|headless|CI=true).*return|skip_gate" \
  $(grep -rl "confirm_\|gate(" tools/ src/) 2>/dev/null
```

A gate that returns `True` (approved) in headless mode is a **high-severity finding**. The correct fall-through is to fail the call, log the deferral, and surface in the run report.

## Step 8 — Emit Findings

```markdown
# Audit Report — Confirmation Gate Logs

## Action coverage
| Category | Tools found | Gated | Ungated |
|----------|------------:|------:|--------:|
| send | <n> | <n> | <n> |
| purchase | <n> | <n> | <n> |
| delete | <n> | <n> | <n> |
| share | <n> | <n> | <n> |
| modify-auth | <n> | <n> | <n> |

## Log fidelity
| Check | State |
|-------|-------|
| Log present | yes / no |
| Required fields | <missing list> |
| Independent of transcript | yes / no |

## Pattern signals
| Indicator | Value | Threshold | Severity |
|-----------|-------|-----------|----------|

## Top fixes
| Severity | Finding | Source page | Suggested change |
|----------|---------|-------------|------------------|
```

## Step 9 — Hand Off

For ungated consequential actions: wire either a code-level wrapper or a PreToolUse hook (Claude Code), then re-run [`audit-hooks-coverage`](audit-hooks-coverage.md). For Lies-in-the-Loop findings: replace Markdown rendering with plain-text printing in the gate dialog. For rubber-stamping: tighten the gated-action set to the truly irreversible subset per [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md).

## Idempotency

Read-only. Re-runs after fixes show fewer ungated actions, smaller fatigue indicators, and a healthier rejection rate.

## Output Schema

```markdown
# Audit Confirmation Gate Logs — <repo>

| Actions | Gated | Ungated | Log present | Fatigue | Lies-in-Loop | Headless-safe |
|--------:|------:|--------:|:-----------:|:-------:|:------------:|:-------------:|
| <n> | <n> | <n> | y/n | low/med/high | n/y | y/n |

Top fix: <one-liner — usually an ungated send/delete or a Markdown-rendered dialog>
```

## Related

- [Confirmation Gates for Consequential Agent Actions](../security/human-in-the-loop-confirmation-gates.md)
- [Bypassing AI Agent Defenses With Lies-In-The-Loop](https://checkmarx.com/zero-post/bypassing-ai-agent-defenses-with-lies-in-the-loop/)
- [The Agent Approval Fatigue Problem](https://molten.bot/blog/agent-approval-fatigue/)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
