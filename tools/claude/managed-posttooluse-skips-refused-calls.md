---
title: "Managed PostToolUse Hooks Skip Refused Tool Calls"
description: "Claude Code 2.1.328 stops firing managed PostToolUse hooks for refused calls. Log refusals at PreToolUse and PermissionDenied, and reconcile by tool_use_id."
tags:
  - claude
  - hooks
  - security
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-20
status: current
---

# Managed PostToolUse Hooks Skip Refused Tool Calls

> Managed PostToolUse hooks skip tool calls refused before they ran (Claude Code 2.1.328), so an audit log built on them misses refusals.

Claude Code 2.1.328 (November 19, 2026) changed managed `PostToolUse` hooks so they no longer fire for calls refused before they ran. A managed hook that wrote a log entry, rewrote a result, blocked, or stopped the turn on those calls does none of that now. Log refusals at an event that sees the decision, and treat `PostToolUse` as a record of calls that completed.

## What changed

The changelog entry reads:

> "Changed managed `PostToolUse` hooks to no longer fire for calls refused before they ran: no log entry, rewrite, block or stop there; `PostToolBatch` gets most, not marked as refused" ([Claude Code changelog, 2.1.328](https://code.claude.com/docs/en/changelog#2-1-328))

Three details limit what you can conclude from it:

- It names managed hooks. Managed hooks come from managed policy settings, the organization-wide, admin-controlled location in the [hooks reference](https://code.claude.com/docs/en/hooks). The entry does not say whether hooks in user, project, or plugin settings changed.
- It says `PostToolBatch` "gets most", not marked as refused. It does not say what "most" counts.
- It does not list which refusal routes count as "refused before they ran".

The hooks reference describes `PostToolUse` as an event that "Runs immediately after a tool completes successfully." ([Hooks reference](https://code.claude.com/docs/en/hooks)).

## What each event sees after a refusal

| Event | Sees a refused call? |
|---|---|
| `PreToolUse` | Yes. These hooks run "before the permission prompt, for every tool except" `EndConversation` ([permissions reference](https://code.claude.com/docs/en/permissions)). Input carries `tool_name`, `tool_input`, and `tool_use_id`. |
| `PostToolUse` (managed) | No, per the 2.1.328 entry. |
| `PostToolUseFailure` | No. "Permission denials fire `PreToolUse` but not this event." |
| `PermissionDenied` | Only for auto-mode denials. It does not run "when you manually deny a permission dialog, when a `PreToolUse` hook blocks a call, or when a `deny` rule matches." |
| `PostToolBatch` | It "gets most", not marked as refused, per the 2.1.328 entry. |

The `PostToolUseFailure` and `PermissionDenied` rows quote the [hooks reference](https://code.claude.com/docs/en/hooks). The reference lists `tool_use_id` in the input of `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionDenied`, and `PostToolBatch` entries. No documented `PreToolUse` input field reports the permission outcome.

## Where to log refusals instead

The right event depends on the route that refused the call.

| Refusal route | Where to log it |
|---|---|
| Auto-mode denial | `PermissionDenied`, which also receives a `reason` field. |
| A deny from your own `PreToolUse` hook | Inside that hook, at the moment it returns the deny. `PermissionDenied` does not run for it. |
| A deny rule, or a manual denial in the permission dialog | No documented event reports the outcome. Reconcile instead. |

To reconcile, record every call at `PreToolUse` and compare its `tool_use_id` against later events. A call with a `PreToolUse` record and no `PostToolUse` or `PostToolUseFailure` record is a candidate refusal. Do not use `PostToolBatch` as the other side of the comparison, because the changelog entry says it "gets most".

## When this backfires

- Your audit only needs executed calls. The change then removes noise, and a `PostToolUse` log needs no work.
- Your hooks live outside managed settings. The entry names managed hooks only, so test an unmanaged hook against a refused call before you assume either behavior.
- You assume a refusal route is covered. The entry does not define "refused before they ran". Trigger a deny rule and a `PreToolUse` block in a test session and see which one your log records.
- You trust the reconciliation as a verdict. A call that never completed for any other reason also has a `PreToolUse` record and no completion record. Treat the output as a list to review.
- You log at `PreToolUse` alone. That records attempts, including calls a later check allowed.
- You rely on `PermissionDenied` outside auto mode. The reference says it only fires in auto mode.

## Example

A managed settings file that records the events above as one JSON line each, using only the event names and input fields in the hooks reference. The commands are a sketch, not a tested deployment.

```json
{
  "hooks": {
    "PreToolUse": [{ "matcher": "*", "hooks": [{ "type": "command",
      "command": "jq -c '{event: .hook_event_name, id: .tool_use_id, tool: .tool_name}' >> /var/log/claude/calls.jsonl" }] }],
    "PostToolUse": [{ "matcher": "*", "hooks": [{ "type": "command",
      "command": "jq -c '{event: .hook_event_name, id: .tool_use_id, tool: .tool_name}' >> /var/log/claude/calls.jsonl" }] }],
    "PostToolUseFailure": [{ "matcher": "*", "hooks": [{ "type": "command",
      "command": "jq -c '{event: .hook_event_name, id: .tool_use_id, tool: .tool_name}' >> /var/log/claude/calls.jsonl" }] }],
    "PermissionDenied": [{ "matcher": "*", "hooks": [{ "type": "command",
      "command": "jq -c '{event: .hook_event_name, id: .tool_use_id, tool: .tool_name, reason: .reason}' >> /var/log/claude/calls.jsonl" }] }]
  }
}
```

List candidate refusals after a session:

```bash
jq -s '([.[] | select(.event == "PreToolUse") | .id]
        - [.[] | select(.event == "PostToolUse" or .event == "PostToolUseFailure") | .id])' \
  /var/log/claude/calls.jsonl
```

Each id the command prints has a `PreToolUse` line and no completion line. If a `PermissionDenied` line exists for the same id, the call was an auto-mode denial.

## Key Takeaways

- From 2.1.328, a managed `PostToolUse` log lists calls that completed. Refusals leave no entry there.
- The changelog entry covers managed hooks and leaves the status of other hook locations unstated.
- No documented event reports a deny-rule or dialog denial. Reconcile `PreToolUse` ids against completion events and review the remainder.
- `PostToolBatch` carries no refused marker and "gets most", per the changelog, so it cannot close the gap.

## Related

- [PostToolBatch Hook](../../tool-engineering/posttoolbatch-hook-batch-boundary.md) — Batch-boundary hook and its input
- [Hooks and Lifecycle](hooks-lifecycle.md) — Hook events and decision control
- [Hard-Deny Classifier Rule](hard-deny-classifier-rule.md) — Unconditional denials inside auto mode
- [Auto Mode](auto-mode.md) — The classifier whose denials fire PermissionDenied
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md) — Where managed hooks are defined
- [PostToolUse Output Replacement](../../tool-engineering/posttooluse-output-replacement.md) — The rewrite that managed hooks no longer apply to refused calls
- [Per-Hook Failure Mode](../../security/per-hook-failure-mode.md) — Declaring how an audit hook fails
