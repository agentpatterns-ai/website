---
title: "Monitor Tool: Event Streaming from Background Scripts"
description: "The Monitor tool streams stdout from a background process back to Claude line-by-line, eliminating polling loops for deploy logs, CI status, and file watchers."
tags:
  - claude
  - agent-design
  - observability
aliases:
  - Monitor tool
  - background script monitoring
  - agent event streaming
---

# Monitor Tool: Event Streaming from Background Scripts

> Stream stdout from a background process directly to Claude — each output line arrives as a notification, no polling required.

The [Monitor tool](https://code.claude.com/docs/en/tools-reference#monitor-tool), added in Claude Code v2.1.98 (April 9, 2026), lets Claude watch a long-running process and react to its output mid-conversation. Claude writes a small watch script, runs it in the background, and receives each stdout line as it arrives. The conversation continues normally; Claude interjects only when an event lands.

## Push vs Poll

Before Monitor, watching a background process meant using `Bash` with `run_in_background: true` and polling for results. Background tasks write output to a file; the agent calls `Read` to check progress. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference)]

```text
Bash (run_in_background: true) → agent calls Read on output file to check progress
```

Monitor inverts this. Each stdout line is pushed to Claude as a notification:

```text
Monitor → each line arrives as a notification → Claude reacts immediately
```

The polling loop disappears. The agent handles other work and responds to events as they arrive.

## Use Cases

| Scenario | What to watch |
|----------|--------------|
| Deploy monitoring | Tail deploy logs, flag errors or completion |
| CI status | Watch a `gh run list` poller until a run finishes |
| File watching | Watch a directory for build artifacts |
| Test suite streaming | Stream test runner output, surface failures as they occur |
| Long-running scripts | Any process that emits progress lines over time |

## Starting and Stopping a Monitor

Ask Claude in natural language — no special syntax required:

```text
Watch the deploy log at /var/log/deploy.log and tell me if any errors appear.
```

```text
Poll the GitHub Actions run for this branch every 30 seconds and report when it finishes.
```

Claude writes the watch script internally and starts it. To stop, ask Claude to cancel the monitor, or end the session. All monitors are session-scoped: they stop when the session exits.

## Permissions and Availability

Monitor uses the same [`allow` and `deny` permission rules as Bash](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules). Any pattern you have set for Bash applies to Monitor automatically. No separate permission configuration is needed.

Monitor is not available on Amazon Bedrock, Google Vertex AI, or Microsoft Foundry. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference)]

## Monitor vs Scheduled Polling

Both Monitor and [session scheduling](session-scheduling.md) handle recurring background activity, but they differ in mechanism:

| | Monitor | CronCreate / /loop |
|--|---------|-------------------|
| Trigger | Each stdout line from a process | Timer interval |
| Cadence | Continuous stream | Minimum 1 minute |
| Script lifecycle | Managed by Monitor | Re-runs Claude each fire |
| Best for | Streaming logs, file watchers | Periodic status checks |

Use Monitor when the process already emits events and you want zero-latency reactions. Use scheduling when you want Claude to run a fresh check on a timer.

## When This Backfires

Push beats poll when events are rare and meaningful. It loses when any of the following hold:

- **Chatty processes flood context — and Monitor will kill them.** Every stdout line becomes a notification. Watching a verbose test runner, webpack rebuild, or `pytest -vv` pipes thousands of events into the conversation, and monitors that produce too many events are automatically stopped — restart with a tighter filter if that happens. [Source: [Monitor tool description](https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/tool-description-background-monitor-streaming-events.md)] Pipe through `grep` before monitoring, or capture to a file and `Read` on demand.
- **Pipe buffering silently delays events.** When piping to `grep` or similar filters, use `grep --line-buffered` — without it, standard block buffering holds output until a ~4 KB chunk fills, which can delay events by minutes on low-traffic streams. [Source: [Monitor tool description](https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/tool-description-background-monitor-streaming-events.md)]
- **Stderr and exit codes are invisible.** Monitor forwards stdout only. A script that logs errors to stderr, crashes silently, or communicates via non-zero exit status will look healthy to Monitor. Use `Bash` with captured output for anything where failure is silent.
- **Outcome filters must match every terminal state.** When watching a job for a result, the filter has to match both success *and* failure signals — otherwise a failed run produces silence, which Claude will read as "still running". [Source: [Monitor tool description](https://github.com/Piebald-AI/claude-code-system-prompts/blob/main/system-prompts/tool-description-background-monitor-streaming-events.md)]
- **Low-cadence checks don't need streaming.** If the thing you're watching changes every few minutes (a slow CI run, a nightly build), scheduled polling with `CronCreate` or `/loop` is just as responsive, does not hold a background process open, and survives across idle windows.
- **Session-scoped lifetime.** Monitors die when the Claude session exits. For batch jobs that need to outlive a conversation, or monitoring across reboots, use an external supervisor (systemd, cron, CI) instead.
- **Not available on Amazon Bedrock, Google Vertex AI, or Microsoft Foundry**, or when `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set. [Source: [Claude Code Tools Reference](https://code.claude.com/docs/en/tools-reference)]

## Example

Monitor a Docker Compose deployment and surface errors the moment they appear:

```text
Run `docker compose up --build` in the background and monitor its output.
Flag any lines containing "error" or "failed" immediately, and tell me when
all services report "healthy".
```

Claude starts `docker compose up --build`, monitors its stdout, and interjects on error lines or when the health check passes — without blocking the conversation or requiring manual polling.

## Key Takeaways

- Monitor pushes each stdout line to Claude as a notification; `Bash run_in_background` requires the agent to poll manually
- Session-scoped: monitors stop when the session exits
- Uses the same permission rules as Bash — no separate configuration required
- Not available on Bedrock, Vertex AI, or Foundry

## Related

- [Session Scheduling](session-scheduling.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [/batch & Worktrees](batch-worktrees.md)
- [Observability](../../observability/index.md)
