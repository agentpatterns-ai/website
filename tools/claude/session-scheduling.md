---
title: "Session Scheduling with Loop and Cron in Claude Code"
description: "Run prompts on a recurring interval or at a specific time using /loop and the cron tools — session-scoped, no external infrastructure required."
tags:
  - claude
  - workflows
aliases:
  - scheduled tasks
  - cron scheduling
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---

# Session Scheduling with Loop and Cron in Claude Code

> Run prompts on a recurring interval or at a specific time using `/loop` and the cron tools — session-scoped, no external infrastructure required.

Session scheduling re-runs a prompt automatically within an active session. Use it to poll a deployment, babysit a PR, check a long build, or set a one-time reminder. Tasks live in the current conversation. `claude --resume` or `claude --continue` restores unexpired ones — recurring tasks within 7 days, and one-shots whose fire time has not passed. This needs Claude Code v2.1.72 or later. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## /loop — interactive recurring prompts

The `/loop` [bundled skill](https://code.claude.com/docs/en/skills#bundled-skills) schedules a recurring prompt. Pass an optional interval and a prompt:

```text
/loop 5m check if the deployment finished and tell me what happened
```

Claude converts the interval to a cron expression and confirms the cadence and job ID.

| Form | Example | Result |
|------|---------|--------|
| Leading interval | `/loop 30m check the build` | Every 30 minutes |
| Trailing `every` | `/loop check the build every 2 hours` | Every 2 hours |
| No interval | `/loop check the build` | Dynamic — Claude picks a 1-minute to 1-hour delay per iteration |

Units are `s`, `m`, `h`, and `d`. Seconds round up to the nearest minute. Intervals that do not map cleanly (`7m`, `90m`) round to the nearest cron step. With dynamic intervals, Claude prints the chosen delay and reason each iteration. The [Monitor tool](monitor-tool.md) often works better than polling here, because it streams background-script stdout line by line. The prompt can invoke another command — `/loop 20m /review-pr 1234` re-runs that workflow each fire. Press `Esc` while a `/loop` waits to clear the pending wakeup. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

### Customize the default prompt with loop.md

A bare `/loop` runs a built-in maintenance prompt — continue unfinished work, tend to the current branch's PR, then run cleanup passes. Override it with `.claude/loop.md` (project-level, takes precedence) or `~/.claude/loop.md` (user-level). Plain Markdown; write it as if typing the `/loop` prompt directly. Edits take effect next iteration. Files over 25,000 bytes are truncated. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks#customize-the-default-prompt-with-loop-md)]

## Cron tools — programmatic scheduling

Agents and skills use three tools to manage scheduled tasks programmatically:

| Tool | Purpose |
|------|---------|
| `CronCreate` | Schedule a task — accepts a 5-field cron expression, prompt, and recurrence flag |
| `CronList` | List all tasks with IDs, schedules, and prompts |
| `CronDelete` | Cancel a task by its 8-character ID |

Standard 5-field expressions (`minute hour day-of-month month day-of-week`) with wildcards, steps (`*/15`), ranges (`1-5`), and comma lists. Day-of-week uses `0` or `7` for Sunday through `6` for Saturday. Extended syntax (`L`, `W`, `?`, `MON`, `JAN`) is not supported. When both day-of-month and day-of-week are constrained, a date matches if either field matches (vixie-cron). Maximum 50 tasks per session. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks#cron-expression-reference)]

## One-time reminders

Describe it in natural language — Claude schedules a single-fire task that auto-deletes after running:

```text
remind me at 3pm to push the release branch
in 45 minutes, check whether integration tests passed
```

## Execution semantics

- Fires between turns — the scheduler checks every second and enqueues at low priority. If Claude is mid-response, the task waits for the turn to end
- Local timezone — `0 9 * * *` means 9am wherever Claude Code runs, not UTC
- Jitter — recurring tasks fire up to 30 minutes after their scheduled time, or half the interval for sub-hourly tasks. One-shots scheduled for `:00` or `:30` fire up to 90s early. The offset is derived from the task ID, so it is deterministic. Use a minute like `3 9 * * *` to skip the one-shot offset
- Expiry after 7 days — recurring tasks fire one final time, then auto-delete 7 days after creation
- No catch-up — a fire missed while Claude is busy runs once when idle, not once per missed interval

[Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Limitations

- Session-scoped only — closing the terminal or restarting Claude Code cancels everything
- One-minute granularity — second-level precision is not available
- On Bedrock, Vertex AI, and Microsoft Foundry, a prompt with no interval runs on a fixed 10-minute schedule instead of a Claude-chosen dynamic interval, and bare `/loop` prints the usage message instead of starting the maintenance loop
- Set `CLAUDE_CODE_DISABLE_CRON=1` to disable the scheduler entirely

For scheduling that persists across sessions: [Routines](https://code.claude.com/docs/en/routines) (cloud, `/schedule` in CLI, 1-hour minimum), [Desktop Scheduled Tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), or [GitHub Actions](https://code.claude.com/docs/en/github-actions) with a `schedule` trigger. To react to events instead of polling, see [Channels](https://code.claude.com/docs/en/channels); to keep working turn after turn until a condition is met, see [`/goal`](https://code.claude.com/docs/en/goal). [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Example

A skill that monitors a GitHub Actions workflow run and notifies the user when it completes:

```text
/loop 5m check the status of the latest GitHub Actions run on this branch — if it finished, report the result and cancel this loop
```

Claude creates a recurring cron job that fires every 5 minutes. On each fire, it runs `gh run list`, checks the status, and — once the run completes — reports the outcome and calls `CronDelete` to cancel itself.

For programmatic use inside a skill or agent, the equivalent uses `CronCreate` directly:

```
CronCreate with expression "*/5 * * * *", prompt "check gh run status and cancel when done", recurring true
```

## Key Takeaways

- `/loop` provides quick interactive scheduling; cron tools provide programmatic control for agents and skills
- Tasks are session-scoped; recurring tasks expire 7 days after creation — they are not persistent infrastructure
- For durable scheduling across restarts, reach for [Routines](https://code.claude.com/docs/en/routines) (cloud) or Desktop scheduled tasks, or a GitHub Actions `schedule` trigger
- Use one-time reminders via natural language for deferred checks without recurring overhead

## Related

- [Cloud-Scheduled Routines vs Local Session Scheduling](cloud-scheduled-routines.md) — the cloud counterpart when the schedule must survive a closed laptop or env drift
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [/batch & Worktrees](batch-worktrees.md)
- [Monitor Tool](monitor-tool.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
