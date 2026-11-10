---
title: "Choosing a Scheduled Agent's Firing Interval"
term: "Firing Interval Selection"
description: "Where a scheduled agent run must poll, set its interval from the job it does and cap it at the rate its reader can absorb: one vendor's cadences span ten minutes to once a day."
tags:
  - agent-design
  - automation
  - tool-agnostic
aliases:
  - scheduled agent cadence
  - cron interval for an agent run
  - proactive agent firing cadence
last_reviewed: 2026-10-30
maturity: emerging
---

# Choosing a Scheduled Agent's Firing Interval

> Choose a scheduled agent's polling interval from the finding's useful lifetime and the reader's capacity to act.

Pick the interval from the job the run does, not from a round number. LangChain's post on proactive agents names three jobs and three cadences that differ by two orders of magnitude. Memory consolidation uses "a cron that runs on some cadence (e.g. once a day)", goal progress a cron that "runs on some cadence (once an hour)", and event-stream triage "a cron that runs on a cadence (once every ten minutes)" ([LangChain](https://www.langchain.com/blog/proactive-agents)). The job picks the row.

## Two conditions before the interval is the question

Both have to hold. Settle the first before spending any thought on the number.

The watched source cannot push. Where it can, a subscription deletes the parameter rather than tuning it. Claude Code's [Monitor tool](../../tools/claude/monitor-tool.md) streams a background script's output line by line, which "avoids polling altogether and is often more token-efficient and responsive than re-running a prompt on an interval" ([Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)).

A person reads the output. The ceiling on this parameter comes from reader fatigue, which needs a reader to fatigue. A run whose findings land in a queue is bounded by whatever drains it.

## Cadence follows the job

| Job | Cadence in the source | What the interval decides |
|---|---|---|
| Memory consolidation | once a day | how old the agent's picture of the user can get |
| Goal progress | once an hour | how long a next action waits unproposed |
| Event-stream triage | once every ten minutes | how late a notification arrives |

On the platform that post describes, scheduled firing is the majority of traffic: "More than 70% of Managed Deepagent runs on LangSmith come from scheduled runs" rather than a human typing a message ([LangChain](https://www.langchain.com/blog/proactive-agents)). That figure is LangChain's own platform telemetry, self-reported, with no method and no absolute run count given.

The chosen cadence then decides which surface can host the run. Ten minutes rules out Claude Code cloud tasks, whose documented minimum interval is 1 hour ([Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)).

## Why it works

A scheduled run gets no second turn. It is "just the prompt that was passed in, triggered at a schedule, with the thread and memory based on the principal who created the schedule" ([LangChain](https://www.langchain.com/blog/proactive-agents)). Unless a scheduling tool is attached, nothing inside the run can change the gap it was started on. Then the interval is the only parameter that decides how long a finding sits undetected.

The interval is therefore a function of how fast the watched thing changes, and one harness ships it as a function instead of a constant. In Claude Code's self-paced loop, after each iteration "it picks a delay between one minute and one hour based on what it observed: short waits while a build is finishing or a PR is active, longer waits when nothing is pending" ([Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)).

The reader bounds the same parameter from the other side, at a rate that does not move. Rizk et al. describe the failure: "too many notifications make individuals desensitized to them", which "causes them to miss some critical notifications that may have detrimental consequences" ([arXiv:2003.02097v1](https://arxiv.org/abs/2003.02097v1)). Their proposed framework keys issuance, suppression and aggregation on "event severity, user preferences, or schedules". That 2020 paper proposes its framework and reports no evaluation, so take the mechanism and no number.

## When this backfires

- Shortening the interval is the chosen fix for a missed finding. Past the reader's absorption rate that makes things worse, because desensitization makes them "miss some critical notifications" ([arXiv:2003.02097v1](https://arxiv.org/abs/2003.02097v1)). Suppression and aggregation are the levers there.
- The volume the cadence was sized for has changed. A static schedule holds a fixed prompt and a fixed cron, so a daily digest keeps arriving daily long after its source went quiet. Managed Deep Agents also offers dynamic schedules, which an agent creates and deletes at runtime ([LangChain](https://www.langchain.com/blog/proactive-agents)).
- The finding carries no deadline. Where it is worth the same whenever it arrives, the interval only sets the bill, and the slowest cadence the task tolerates wins.
- The cadence sits below the floor of every surface you can run on. Claude Code's Desktop and `/loop` options accept sub-hour schedules but require your machine to stay on. Cloud tasks have a one-hour floor. A ten-minute job buys granularity with uptime ([Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)).
- Nothing changes between fires. That failure sits upstream in the trigger choice, and [Loop Trigger Selection](../../loop-engineering/loop-trigger-selection.md) covers it.

## Example

A weekday sales readout runs on a daily cadence, and the schedule file says so in one line ([LangChain](https://www.langchain.com/blog/proactive-agents)):

```python
# schedules/daily_digest.py
from managed_deepagents import define_schedule

schedule = define_schedule(
    cron="0 8 * * 1-5",
    timezone="America/Los_Angeles",
    prompt="Inspect the sales report using your tools and send a KPI readout.",
)
```

In this static schedule, the cron is the entire cadence decision and the prompt is the entire run.

## Key Takeaways

- Name the job class before picking a number. One vendor's own cadences for three jobs span ten minutes to once a day.
- Check whether the source can push before choosing any interval. A stream removes the parameter instead of tuning it.
- The reader's absorption rate is the real ceiling, and past it the levers are suppression and aggregation rather than a shorter gap.
- Cadence picks the hosting surface. A sub-hour job cannot run where the documented floor is 1 hour.
- Where the harness lets a run set its own next delay from what it observed, prefer that to a constant.

## Related

- [Loop Trigger Selection: Pairing the Start with the Stop](../../loop-engineering/loop-trigger-selection.md) — the upstream choice of trigger shape and its stopping rule, which has to pass before an interval is worth setting
- [Unattended Run Reporting: What the One Message Must Say](../../workflows/unattended-run-reporting-contract.md) — what a fire does with a finding once it has one, and the states its message has to separate
- [Verdict-Driven Inspection Cadence for Agent Monitors (Cadence)](verdict-driven-inspection-cadence.md) — the same adaptive-interval idea applied inside a single run, keyed on a monitor's own last verdict
- [Self-Paced /loop Ends When a Turn Does Not Reschedule](../../tools/claude/self-paced-loop-reschedule.md) — what happens to Claude Code's adaptive-interval loop when one iteration picks no next interval at all
- [Cloud-Scheduled Routines vs Local Session Scheduling](../../tools/claude/cloud-scheduled-routines.md) — the surface trade a sub-hour cadence forces, with the 1-hour cloud floor in full
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — why a shorter interval raises the cost of a fire that duplicates the last one's output
- [Whose Permissions a Self-Scheduled Agent Run Carries](../../security/self-scheduled-run-authority.md) — the authority a fire spends, decided when the schedule is written rather than when it runs
