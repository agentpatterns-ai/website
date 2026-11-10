---
title: "Self-Paced /loop Ends When a Turn Does Not Reschedule"
description: "Since Claude Code v2.1.319, a self-paced /loop stops on any turn that skips ScheduleWakeup. Make each turn reschedule or stop on purpose, or set keepalive."
tags:
  - claude
  - workflows
aliases:
  - CLAUDE_CODE_LOOP_KEEPALIVE
  - self-paced loop fallback wakeup
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-09
status: current
---

# Self-Paced /loop Ends When a Turn Does Not Reschedule

> From Claude Code v2.1.319, a self-paced `/loop` ends on the first turn that skips a reschedule, unless `CLAUDE_CODE_LOOP_KEEPALIVE=1` restores the old fallback wakeup.

A self-paced `/loop` in Claude Code v2.1.319 or later ends as soon as a turn finishes without a `ScheduleWakeup` call. Earlier versions scheduled a fallback wakeup instead, and `CLAUDE_CODE_LOOP_KEEPALIVE=1` brings that back ([changelog 2.1.319](https://code.claude.com/docs/en/changelog#2-1-319)). The entry names self-paced loops only, which are the loops started without an interval. A loop with an interval, such as `/loop 5m`, runs as a cron job ([scheduled tasks docs](https://code.claude.com/docs/en/scheduled-tasks#run-on-a-fixed-interval)).

## The old and new end rules

A self-paced loop has no schedule of its own. At the end of each iteration Claude calls `ScheduleWakeup` to pick the next run "between one minute and one hour out", or calls it with `stop: true` to cancel the pending wakeup ([tools reference](https://code.claude.com/docs/en/tools-reference)).

| How the turn ends | Default from v2.1.319 | Before v2.1.319, or with `CLAUDE_CODE_LOOP_KEEPALIVE=1` |
|---|---|---|
| `ScheduleWakeup` with a delay | Next iteration runs at that time | Same |
| No `ScheduleWakeup` call | Loop ends | One fallback wakeup about 20 minutes later; the loop ends if that iteration also skips the call |

The fallback row comes from the scheduled-tasks page, which in November 2026 still reads: "If an iteration ends without either rescheduling or stopping, Claude Code schedules one fallback wakeup about 20 minutes later and ends the loop when that iteration doesn't reschedule either" ([scheduled tasks docs](https://code.claude.com/docs/en/scheduled-tasks#stop-a-loop)). Read it as the pre-2.1.319 behavior.

## Make every turn end on a decision

A forgotten call and a deliberate stop now give the same result. Write the loop prompt so that each turn has to choose:

```text
/loop check whether CI passed on this branch's PR and address new review comments.
At the end of every turn, do exactly one thing: schedule the next check,
or stop the loop and say in one line why it is done.
```

You see that stop reason in the transcript. Since v2.1.284, Claude writes each self-paced status update, "and the outcome when the loop stops, as visible text" ([changelog 2.1.284](https://code.claude.com/docs/en/changelog#2-1-284)). For a bare `/loop`, put the same closing instruction in `.claude/loop.md`. That file replaces the built-in maintenance prompt, and edits take effect on the next iteration ([scheduled tasks docs](https://code.claude.com/docs/en/scheduled-tasks#customize-the-default-prompt-with-loop-md)).

## When to set the keepalive variable

Set `CLAUDE_CODE_LOOP_KEEPALIVE=1` when one missed reschedule costs more than one extra iteration, for example a watch loop on a deploy you are away from. A reschedule can also fail to take effect: v2.1.317 fixed "self-paced <code>/loop</code> wakeups sometimes not being scheduled when Claude left a field out of its request" ([changelog 2.1.317](https://code.claude.com/docs/en/changelog#2-1-317)).

Keep the default when an extra iteration costs real money, for example a loop that dispatches subagents. A May 2026 bug report describes a stale wakeup restarting a loop after Claude had declared it done, which led to "~$3-5 of additional Sonnet subagent work" the user had not authorized ([anthropics/claude-code#57660](https://github.com/anthropics/claude-code/issues/57660)). That report predates the change and involves a different mechanism, but it prices an iteration nobody asked for.

## Detect a loop that ended

A Stop hook receives a `session_crons` array that lists pending wakeups from `ScheduleWakeup`, and the docs say the arrays "are empty when nothing is in flight or scheduled" ([hooks reference](https://code.claude.com/docs/en/hooks#stop-input)). In a session with no other scheduled tasks, a hook can log or notify when a turn ends with that array empty. It cannot tell a forgotten reschedule from a `stop: true`, because both leave nothing pending.

## Why it works

The loop's next run exists only if Claude makes an explicit call ([tools reference](https://code.claude.com/docs/en/tools-reference)). The fallback gave a missing call one more iteration before it ended the loop. Since v2.1.319 a missing call means stop ([changelog 2.1.319](https://code.claude.com/docs/en/changelog#2-1-319)). A loop that forgets now ends at once instead of running one more uninstructed iteration.

## When this backfires

- Unattended watch loops lose their only retry. One turn that skips the call ends the loop, and nothing re-arms it.
- A prompt that never says how a turn ends invites a turn that does the work and stops, which now ends the loop.
- Keepalive does not make `/loop` durable. Tasks fire only while Claude Code is running and idle, a self-paced loop is not restored on `--resume`, and the seven-day expiry applies ([scheduled tasks docs](https://code.claude.com/docs/en/scheduled-tasks#limitations)). An open report also describes self-paced wakeups that never fired on a Windows machine that stayed awake ([anthropics/claude-code#93114](https://github.com/anthropics/claude-code/issues/93114)). For work that must run unattended, the docs point to cloud scheduled tasks, Desktop scheduled tasks, or GitHub Actions.
- Teams on mixed versions see different results. A loop that leaned on the fallback keeps running on older Claude Code and ends on v2.1.319 or later.

## Example

A release-branch watcher that may run while you are away. The project `loop.md` closes every turn with a decision:

```markdown
Check the `release/next` PR. If CI is red, pull the failing job log and
report the failing step. If new review comments arrived, list them.
End every turn with one action: schedule the next check (shorter while
CI is running, longer when the PR is quiet), or stop the loop and state
the reason in one line.
```

Start it with the keepalive variable so one skipped reschedule gets a second chance:

```bash
CLAUDE_CODE_LOOP_KEEPALIVE=1 claude
# then, in the session:
/loop
```

## Key Takeaways

- By default, a self-paced loop on v2.1.319+ has no retry: a missing reschedule is a stop.
- Put the end-of-turn choice in the prompt or `loop.md`, and ask for a one-line stop reason so a silent end stands out.
- Fixed-interval loops (`/loop 5m`) run on cron and are outside the changelog entry.
- Set `CLAUDE_CODE_LOOP_KEEPALIVE=1` only where a lost iteration costs more than an extra one.
- Neither setting turns `/loop` into unattended infrastructure; move that work to cloud or Desktop scheduled tasks.

## Related

- [Session Scheduling with Loop and Cron in Claude Code](session-scheduling.md) — the full `/loop` and cron tool reference this page narrows
- [Cloud-Scheduled Routines vs Local Session Scheduling](cloud-scheduled-routines.md) — where to move a loop that has to survive a closed session
- [Monitor Tool: Event Streaming from Background Scripts](monitor-tool.md) — stream output instead of polling, with no wakeup to forget
- [Claude Code Hooks: Deterministic Lifecycle Automation](hooks-lifecycle.md) — the Stop hook that sees `session_crons`
- [Loop Trigger Selection: Pairing the Start with the Stop](../../loop-engineering/loop-trigger-selection.md) — why every loop needs a stopping rule chosen with its trigger
