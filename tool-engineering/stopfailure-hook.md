---
title: "StopFailure Hook: Observability for API Error Termination"
description: "The StopFailure hook fires when a Claude Code turn ends due to an API error, giving harnesses a deterministic signal to log failures, alert operators, and feed external recovery workflows."
tags:
  - agent-design
  - claude
aliases:
  - StopFailure event
  - API error hook
---

# StopFailure Hook: Observability for API Error Termination

> The `StopFailure` hook fires when a Claude Code turn ends due to an API error — rate limit, auth failure, billing error, or server error — providing a deterministic signal for logging, alerting, and external recovery coordination.

## What It Is (and What It Is Not)

Added in [Claude Code v2.1.78](https://code.claude.com/docs/en/changelog), `StopFailure` is an **observational hook** — not a control hook. The runtime ignores its exit code and output. It cannot block behavior, initiate a retry, or resume the session. It fires after the turn has already failed.

The hook's role is notification: log the error, push a metric, trigger an alert. Any retry or re-launch logic must live in an external process — a CI supervisor, a cron job, a shell wrapper — that reads the hook's output and decides what to do next.

Contrast with `Stop`, which fires on successful turn completion. Both are non-blocking; `StopFailure` is the error branch.

## Input Schema

Claude Code passes JSON on stdin when `StopFailure` fires:

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../transcript.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "StopFailure",
  "error_type": "rate_limit",
  "error_message": "Rate limit exceeded: 100 requests per minute"
}
```

`error_type` carries one of seven values:

| Value | Cause |
|-------|-------|
| `rate_limit` | Request rate or quota exceeded |
| `authentication_failed` | Invalid or expired API credentials |
| `billing_error` | Account billing issue |
| `invalid_request` | Malformed API request |
| `server_error` | Provider-side error |
| `max_output_tokens` | Response exceeded token limit |
| `unknown` | Error type not classified |

## Matcher Scoping

Configure `StopFailure` hooks with an `error_type` matcher to fire only on specific failure classes:

```json
{
  "hooks": {
    "StopFailure": [
      {
        "matcher": "rate_limit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/log-rate-limit.sh"
          }
        ]
      },
      {
        "matcher": "authentication_failed|billing_error",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/alert-operator.sh"
          }
        ]
      }
    ]
  }
}
```

A hook without a matcher fires for all `StopFailure` events regardless of error type.

## Use Cases

- **Structured failure logging** — write `error_type`, `session_id`, and timestamp to a file external recovery scripts can poll
- **Operator alerting** — push to Slack, PagerDuty, or a webhook when `authentication_failed` or `billing_error` fires, since these require human action
- **Metrics collection** — increment failure counters by error type for dashboards and SLO tracking
- **Audit trails** — append to a session audit log alongside the `transcript_path` for post-mortem analysis

## Wiring into an External Recovery Loop

`StopFailure` fits into a recovery architecture as the notification layer. The retry/re-launch decision lives outside Claude Code:

```mermaid
sequenceDiagram
    participant Agent as Claude Code
    participant Hook as StopFailure Hook
    participant Log as Failure Log
    participant Supervisor as External Supervisor

    Agent->>Agent: Turn ends (API error)
    Agent->>Hook: Fire StopFailure (error_type, session_id)
    Hook->>Log: Append structured failure entry
    Supervisor->>Log: Poll for new entries
    Supervisor->>Supervisor: Decide: retry, alert, or abandon
    Supervisor->>Agent: Re-launch with last checkpoint
```

The hook writes the signal; the supervisor acts on it. This separation keeps the hook simple and the retry logic testable outside Claude Code.

## Example

A long-running overnight refactor agent uses `StopFailure` to log failures and alert on credential issues.

**`.claude/hooks/on-stop-failure.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
ERROR_TYPE=$(echo "$INPUT" | jq -r '.error_type')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Always log
echo "{\"timestamp\":\"$TIMESTAMP\",\"error_type\":\"$ERROR_TYPE\",\"session_id\":\"$SESSION_ID\",\"transcript\":\"$TRANSCRIPT\"}" \
  >> ~/agent-failures.jsonl

# Alert on credential/billing errors — these require human action
if [[ "$ERROR_TYPE" == "authentication_failed" || "$ERROR_TYPE" == "billing_error" ]]; then
  curl -s -X POST "$SLACK_WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"Agent stopped: $ERROR_TYPE — session $SESSION_ID\"}" \
    || true  # never block on webhook failure
fi
```

**`.claude/settings.json`**:

```json
{
  "hooks": {
    "StopFailure": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/on-stop-failure.sh"
          }
        ]
      }
    ]
  }
}
```

An external cron job polls `~/agent-failures.jsonl`. When it finds a `rate_limit` entry, it waits and re-launches the agent from the last git checkpoint. The hook writes the signal; the cron job acts on it.

## Why It Works

`StopFailure` is non-blocking by design because it fires after an unrecoverable error — the turn has already ended. Claude Code distinguishes pre-action hooks (which can block: `PreToolUse`, `UserPromptSubmit`, `PermissionRequest`) from post-action hooks (observational only: `PostToolUse`, `StopFailure`). Control hooks execute *before* the action and can influence it; observational hooks execute *after* and cannot. At the point `StopFailure` fires, the API call has already failed and no exit code from the hook can alter that outcome. The design keeps the runtime's error path clean: it executes the notification command, ignores what it returns, and terminates. See the [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) for the full hook lifecycle and exit-code behavior table.

## When This Backfires

- **Short-lived or interactive sessions rarely justify the overhead** — for a developer running `claude` in a terminal, inspecting the CLI's [exit code](https://code.claude.com/docs/en/hooks#exit-code-output) directly is simpler than wiring a `StopFailure` hook plus an external supervisor. The hook pays off for long-running, unattended agents (overnight refactors, CI, cron loops) where no human watches the exit code. If a human is already present, skip it.
- **Silent hook script failures** — `StopFailure`'s exit code is ignored, so a broken hook script (missing `jq`, typo in the path, unset `$SLACK_WEBHOOK_URL`) fails invisibly. No alert fires, no log line appears, and the operator believes the supervisor is healthy. Test hook scripts in isolation and monitor the log file itself for staleness.
- **Supervisor polling lag defers recovery** — the hook writes to a log; the external supervisor polls on an interval. Polling lag (30s, 1min) stacks on top of the API failure, extending mean time to recovery. Push-based signaling (the hook calls the supervisor directly) trades hook latency for faster reaction.
- **Slow hooks delay shutdown** — `StopFailure` runs synchronously before the process exits. A hook that calls a slow external service (webhook, metrics endpoint) or has no timeout holds the process open. Add a timeout (`timeout` field in the hook config, or `timeout` in your shell script) and always use `|| true` on external calls.
- **`unknown` error type limits scoping** — matchers can't distinguish the root cause when `error_type` is `unknown`. A hook scoped to `rate_limit` will silently skip genuine rate-limit failures that the runtime couldn't classify. Maintain a catch-all unscoped hook for audit logging alongside any type-scoped hooks.
- **Log files fill on repeated crashes** — an agent restart loop (cron re-launches on every failure) combined with an append-only log hook writes one entry per crash indefinitely. Cap log file size or use a structured logging system with rotation.

## Key Takeaways

- `StopFailure` fires when a Claude Code turn ends due to an API error — exit codes and output are ignored
- It is an observability hook, not a control hook: use it for logging, alerting, and metrics
- `error_type` matchers scope the hook to specific failure classes
- Retry and re-launch logic must live in an external process; the hook provides the signal, not the recovery

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [Reactive Environment Hooks: CwdChanged and FileChanged](reactive-environment-hooks.md)
- [Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md)
- [PreCompact Hook Compaction Veto](precompact-hook-compaction-veto.md)
