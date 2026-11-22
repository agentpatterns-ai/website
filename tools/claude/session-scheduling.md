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

Session scheduling re-runs a prompt automatically within an active session. Use it to poll a deployment, babysit a PR, check a long build, or set a one-time reminder. Tasks live in the current conversation. `claude --resume` or `claude --continue` restores unexpired ones — recurring tasks that have not expired, and one-shots whose fire time has not passed. Exiting between turns with `Exit and stop tasks` skips that restore ([details](#inspect-and-stop-scheduled-work-in-tasks)). This needs Claude Code v2.1.72 or later. [Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

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
- Expiry — recurring tasks end on their own. The limit is 7 days before v2.1.330 and up to 30 days from it ([lifetime details](#task-lifetime-and-the-v21330-change))
- No catch-up — a fire missed while Claude is busy runs once when idle, not once per missed interval

[Source: [Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)]

## Task lifetime and the v2.1.330 change

Claude Code v2.1.330 (2026-11-20) changed recurring scheduled tasks and `/loop` "to run up to 30 days instead of 7 while their session keeps running, and say when they end". Tasks made before that release "still end at 7 days" ([changelog 2.1.330](https://code.claude.com/docs/en/changelog#2-1-330)).

The two sources disagree for now. As of 2026-11-22 the scheduled-tasks page still has a "Seven-day expiry" section. It says recurring tasks "expire 7 days after creation" and that the task "fires one final time, then deletes itself". It does not mention 30 days ([Seven-day expiry](https://code.claude.com/docs/en/scheduled-tasks#seven-day-expiry)). The changelog does not say whether a 30-day task still fires once more at the end. It says only that Claude Code reports when tasks end.

What to change in a long-running loop design:

- Treat 30 days as a ceiling, not a guarantee. The changelog gives the limit only "while their session keeps running", and tasks still fire only while Claude Code is running and idle ([Limitations](#limitations)).
- Recreate a loop you made before upgrading. The changelog says only that tasks made before the release keep the 7-day end. That a task recreated after the upgrade gets the 30-day limit is an inference from that wording, not a stated rule.
- Keep the recreate-or-go-durable rule. The scheduled-tasks page advises canceling and recreating a recurring task before it expires, or using cloud or Desktop scheduled tasks for durable scheduling ([Seven-day expiry](https://code.claude.com/docs/en/scheduled-tasks#seven-day-expiry)). The page words that advice for the 7-day limit.

## Inspect and stop scheduled work in /tasks

Claude Code v2.1.329 added this session's scheduled tasks, `/loop` wakeups, the goal, and the conversation's forks to `/tasks`. Press `x` on a row and Claude Code asks before it stops that item ([changelog 2.1.329](https://code.claude.com/docs/en/changelog#2-1-329)).

- One count. The `/tasks` header and the footer's background count show a single number that covers shells, monitors, MCP calls, agents, workflows, and scheduled tasks ([changelog 2.1.329](https://code.claude.com/docs/en/changelog#2-1-329))
- No wait. Claude Code runs `/tasks` immediately, without interrupting a response in progress, so you can open the list mid-turn ([commands reference](https://code.claude.com/docs/en/commands))
- Not the checklist. `Ctrl+T` toggles Claude's to-do checklist, which is a different view from `/tasks` ([interactive mode](https://code.claude.com/docs/en/interactive-mode))

Choosing `Exit and stop tasks` now ends this session's scheduled tasks, so they do not run again after `--resume`. The exception is an exit while Claude is responding ([changelog 2.1.329](https://code.claude.com/docs/en/changelog#2-1-329)). The scheduled-tasks page describes the same rule as an exit "between turns" ([Scheduled Tasks — Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks#limitations)). If you must quit mid-response, the exit option will not end the tasks. Stopping them from `/tasks` first is an inference from that exception: no source states that a task stopped with `x` stays stopped on resume.

As of 2026-11-21 the scheduled-tasks page does not mention `/tasks`. It still says `Esc` and `Ctrl+C` do not stop a fixed-interval loop and tells you to ask Claude to cancel it ([stop a loop](https://code.claude.com/docs/en/scheduled-tasks#stop-a-loop)). For the self-paced case, see [Self-Paced /loop Ends When a Turn Does Not Reschedule](self-paced-loop-reschedule.md).

## Limitations

- Tasks fire only while Claude Code is running and idle. Closing the terminal or exiting stops them firing, but `claude --resume` or `claude --continue` restores unexpired `CronCreate` tasks. You lose a task if you exit between turns with `Exit and stop tasks`, and a self-paced `/loop` is not restored
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
- Tasks are session-scoped and recurring tasks expire: after 7 days before v2.1.330, and up to 30 days from v2.1.330 while the session keeps running. They are not persistent infrastructure
- For durable scheduling across restarts, reach for [Routines](https://code.claude.com/docs/en/routines) (cloud) or Desktop scheduled tasks, or a GitHub Actions `schedule` trigger
- Use one-time reminders via natural language for deferred checks without recurring overhead
- From v2.1.329, `/tasks` lists scheduled tasks, loop wakeups, the goal, and forks, and `x` stops one after asking. `Exit and stop tasks` also ends scheduled tasks unless you exit while Claude is responding

## Related

- [Self-Paced /loop Ends When a Turn Does Not Reschedule](self-paced-loop-reschedule.md) — the v2.1.319 end rule for loops without an interval, and when to set `CLAUDE_CODE_LOOP_KEEPALIVE=1`
- [Cloud-Scheduled Routines vs Local Session Scheduling](cloud-scheduled-routines.md) — the cloud counterpart when the schedule must survive a closed laptop or env drift
- [Allowing One Skill to Run in Scheduled Tasks and /loop](../../patterns/agent-design/unattended-skill-allow-rule.md) — the v2.1.325 prompt before a fire runs a skill with `allowed-tools` or hooks, and the `Skill(name)` rule that clears it
- [Parallel Agent Sessions](../../workflows/parallel-agent-sessions.md)
- [/batch & Worktrees](batch-worktrees.md)
- [Monitor Tool](monitor-tool.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Feature Flags & Environment Variables](feature-flags.md)
