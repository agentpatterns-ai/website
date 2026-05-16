---
title: "Session Scheduling with Loop and Cron in Claude Code"
description: "Run prompts on a recurring interval or at a specific time using /loop and the cron tools — session-scoped, no external infrastructure required."
tags:
  - claude
  - workflows
aliases:
  - scheduled tasks
  - cron scheduling
---

# Session Scheduling

> Run prompts on a recurring interval or at a specific time using `/loop` and the cron tools — session-scoped, no external infrastructure required.

Session scheduling lets Claude re-run a prompt automatically within an active session. Use it to poll a deployment, babysit a PR, check a long-running build, or set a one-time reminder. Tasks are session-scoped: they live in the current conversation, but `claude --resume` or `claude --continue` restores unexpired tasks — recurring tasks created within the last 7 days, and one-shots whose scheduled time hasn't passed. Requires Claude Code v2.1.72 or later. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## /loop — Interactive Recurring Prompts

The `/loop` [bundled skill](https://code.claude.com/docs/en/skills#bundled-skills) is the fastest way to schedule a recurring prompt. Pass an optional interval and a prompt:

```text
/loop 5m check if the deployment finished and tell me what happened
```

Claude converts the interval to a cron expression and confirms the cadence and job ID. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

| Form | Example | Result |
|------|---------|--------|
| Leading interval | `/loop 30m check the build` | Every 30 minutes |
| Trailing `every` | `/loop check the build every 2 hours` | Every 2 hours |
| No interval | `/loop check the build` | Dynamic — Claude picks a delay between 1 minute and 1 hour after each iteration based on what it observed |

Supported units: `s` (seconds), `m` (minutes), `h` (hours), `d` (days). Seconds are rounded up to the nearest minute — cron has one-minute granularity, and intervals that don't map to a clean cron step (such as `7m` or `90m`) are rounded to the nearest one that does. When the interval is dynamic, Claude prints the chosen delay and reason at the end of each iteration; for that shape of loop, the [Monitor tool](monitor-tool.md) often replaces polling entirely by streaming stdout from a background script as each line arrives. The prompt can invoke another command: `/loop 20m /review-pr 1234` re-runs that workflow on each fire. Press `Esc` while a `/loop` is waiting for its next iteration to clear the pending wakeup. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

### Customize the default prompt with loop.md

A bare `/loop` (no interval, no prompt) runs a built-in maintenance prompt — continue unfinished work, tend to the current branch's PR, then run cleanup passes. Replace it with your own by writing `.claude/loop.md` (project-level, takes precedence) or `~/.claude/loop.md` (user-level). The file is plain Markdown — write it as if you were typing the `/loop` prompt directly. Edits take effect on the next iteration. Files over 25,000 bytes are truncated. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks#customize-the-default-prompt-with-loop-md)]

## Cron Tools — Programmatic Scheduling

Agents and skills use three tools to manage scheduled tasks programmatically:

| Tool | Purpose |
|------|---------|
| `CronCreate` | Schedule a task — accepts a 5-field cron expression, prompt, and recurrence flag |
| `CronList` | List all tasks with IDs, schedules, and prompts |
| `CronDelete` | Cancel a task by its 8-character ID |

Standard 5-field cron expressions (`minute hour day-of-month month day-of-week`) with wildcards (`*`), steps (`*/15`), ranges (`1-5`), and comma lists. Day-of-week uses `0` or `7` for Sunday through `6` for Saturday. Extended syntax (`L`, `W`, `?`, name aliases like `MON` or `JAN`) is not supported. When both day-of-month and day-of-week are constrained, a date matches if either field matches (vixie-cron semantics). Maximum 50 tasks per session. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks#cron-expression-reference)]

## One-Time Reminders

Describe what you want in natural language — Claude schedules a single-fire task that auto-deletes after running:

```text
remind me at 3pm to push the release branch
in 45 minutes, check whether the integration tests passed
```

## Execution Semantics

- **Fires between turns** — the scheduler checks every second, enqueues at low priority; if Claude is mid-response, the task waits until the current turn ends
- **Local timezone** — `0 9 * * *` means 9am wherever you run Claude Code, not UTC
- **Jitter** — recurring tasks fire up to 30 minutes after their scheduled time, or up to half the interval for sub-hourly tasks (e.g. a `*/10` task may fire up to 5 minutes late); one-shot tasks scheduled for `:00` or `:30` fire up to 90s early. The offset is derived from the task ID, so deterministic per task. Pick a minute that isn't `:00` or `:30` (e.g. `3 9 * * *`) to skip the one-shot offset
- **7-day expiry** — recurring tasks fire one final time then auto-delete 7 days after creation; recreate before expiry if needed
- **No catch-up** — if a fire is missed while Claude is busy, it fires once when idle, not once per missed interval

[Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Limitations

- Session-scoped only — closing the terminal or restarting Claude Code cancels everything
- One-minute granularity — second-level precision is not available
- On Bedrock, Vertex AI, and Microsoft Foundry, a prompt with no interval runs on a fixed 10-minute schedule instead of a Claude-chosen dynamic interval, and bare `/loop` prints the usage message instead of starting the maintenance loop
- Set `CLAUDE_CODE_DISABLE_CRON=1` to disable the scheduler entirely

For durable scheduling that persists across sessions, use [Routines](https://code.claude.com/docs/en/routines) (Anthropic-managed cloud, formerly "Cloud Scheduled Tasks"; create via `/schedule` in the CLI, minimum interval 1 hour), [Desktop Scheduled Tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), or a [GitHub Actions workflow](https://code.claude.com/docs/en/github-actions) with a `schedule` trigger. To react to events as they happen instead of polling, see [Channels](https://code.claude.com/docs/en/channels); to keep a session working turn after turn until a condition is met, see [`/goal`](https://code.claude.com/docs/en/goal). [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

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

- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [/batch & Worktrees](batch-worktrees.md)
- [Monitor Tool](monitor-tool.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
