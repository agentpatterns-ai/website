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

Session scheduling lets Claude re-run a prompt automatically within an active session. Use it to poll a deployment, babysit a PR, check a long-running build, or set a one-time reminder. Tasks are session-scoped: they exist only while Claude Code is running and are lost on exit or restart. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

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
| No interval | `/loop check the build` | Every 10 minutes (default) |

Supported units: `s` (seconds), `m` (minutes), `h` (hours), `d` (days). Seconds are rounded up to the nearest minute — cron has one-minute granularity. The prompt can invoke another skill: `/loop 20m /review-pr 1234` re-runs that skill on each fire. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Cron Tools — Programmatic Scheduling

Agents and skills use three tools to manage scheduled tasks programmatically:

| Tool | Purpose |
|------|---------|
| `CronCreate` | Schedule a task — accepts a 5-field cron expression, prompt, and recurrence flag |
| `CronList` | List all tasks with IDs, schedules, and prompts |
| `CronDelete` | Cancel a task by its 8-character ID |

Standard 5-field cron expressions (`minute hour day-of-month month day-of-week`) with wildcards (`*`), steps (`*/15`), ranges (`1-5`), and comma lists. Extended syntax (`L`, `W`, `?`, name aliases) is not supported. Maximum 50 tasks per session. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## One-Time Reminders

Describe what you want in natural language — Claude schedules a single-fire task that auto-deletes after running:

```text
remind me at 3pm to push the release branch
in 45 minutes, check whether the integration tests passed
```

## Execution Semantics

- **Fires between turns** — the scheduler enqueues at low priority; if Claude is mid-response, the task waits until the current turn ends
- **Local timezone** — `0 9 * * *` means 9am wherever you run Claude Code, not UTC
- **Jitter** — recurring tasks fire up to 10% of their period late (capped at 15 min); one-shot tasks near `:00`/`:30` fire up to 90s early. Derived from task ID, so deterministic per task
- **7-day expiry** — recurring tasks fire one final time then auto-delete 7 days after creation; recreate before expiry if needed
- **No catch-up** — if a fire is missed while Claude is busy, it fires once when idle, not once per missed interval

[Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Limitations

- Session-scoped only — closing the terminal or restarting Claude Code cancels everything
- One-minute granularity — second-level precision is not available
- On Bedrock, Vertex AI, and Microsoft Foundry, a prompt with no interval runs on a fixed 10-minute schedule instead of a Claude-chosen dynamic interval, and bare `/loop` prints the usage message instead of starting the maintenance loop
- Set `CLAUDE_CODE_DISABLE_CRON=1` to disable the scheduler entirely

For durable scheduling that persists across sessions, use [Cloud Scheduled Tasks](https://code.claude.com/docs/en/web-scheduled-tasks), [Desktop Scheduled Tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), or a [GitHub Actions workflow](https://code.claude.com/docs/en/github-actions) with a `schedule` trigger. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

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
- For durable scheduling across restarts, reach for Cloud or Desktop scheduled tasks, or a GitHub Actions `schedule` trigger
- Use one-time reminders via natural language for deferred checks without recurring overhead

## Related

- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [/batch & Worktrees](batch-worktrees.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
