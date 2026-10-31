---
title: "Bounding an Unattended Run's Wait on a Usage-Limit Reset"
term: "Usage-Limit Wait Ceiling"
description: "Claude Code retry-watchdog settings bound per-request waiting and optionally recheck subscription limits before their reported reset."
tags:
  - technique
  - agent-design
  - automation
  - cost-performance
  - claude
aliases:
  - usage limit wait ceiling
  - bounding an unattended run's quota wait
  - retry watchdog usage limit settings
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-28
maturity: emerging
status: current
---

# Bounding an Unattended Run's Wait on a Usage-Limit Reset

> Claude Code retry-watchdog settings bound usage-limit waits and optionally recheck subscription limits before their reported reset.

Consider a wait ceiling when a stalled run blocks other work or outlives the next useful scheduled run. Weigh that delay against restart costs. The watchdog uses the reported reset time when available ([environment variables](https://code.claude.com/docs/en/env-vars)); choose a bound for your scheduler's needs.

## How the watchdog waits on a usage limit

`CLAUDE_CODE_RETRY_WATCHDOG=1` is the unattended retry posture. The reference gives its effect as: "Retries `429` and `529` capacity errors indefinitely instead of failing after `CLAUDE_CODE_MAX_RETRIES` attempts" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). For a usage limit the wait is not backoff. The watchdog "backs off up to 5 minutes between attempts, or until the limit resets when the response carries a rate-limit reset time, so a session that hits a usage limit waits out the remaining window" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)).

The error carries the reset time: `You've hit your session limit · resets 3:45pm`, or `You've hit your weekly limit · resets Mon 12:00am` ([Claude Code errors](https://code.claude.com/docs/en/errors#youve-hit-your-session-limit)).

Spend-limit and exhausted-credit errors have separate handling. Since v2.1.239 Claude Code "fails at once when a standard-speed request gets a `429` that reports a spend limit or exhausted usage credits, even one from a gateway spend cap that resets on a schedule" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)).

## Choosing the wait bound

Compare the reported reset distance with the cost of restarting and any work queued behind the run.

With expensive setup, waiting can preserve useful work. With contention and cheap setup, consider ending the request and letting the schedule retry it.

## The two ceilings behave differently

`CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` (v2.1.295 or later) is a spent-time budget. The reference defines it as the "Maximum time in milliseconds that each API request spends waiting out `429` and `529` errors", and adds: "Once that time is spent, the next such error ends the request" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). It covers those errors per API request. It does not promise to interrupt an existing sleep at the deadline or bound the whole job.

`CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS` arrived in v2.1.301 and decides up front. It makes unattended retry mode end "a request at a usage limit that resets too far away instead of waiting" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)), so the test named there is the reported distance rather than the time already burned.

`MAX_WAIT_MS` and the recheck interval both have rows in the [environment variables reference](https://code.claude.com/docs/en/env-vars) and on the [retry behavior table](https://code.claude.com/docs/en/errors#tune-retry-behavior) in the errors reference. `MAX_USAGE_LIMIT_WAIT_MS` appears on neither. The v2.1.301 changelog documents its purpose; these references supply no default, range, or validation behavior for it.

## Rechecking only pays on one auth path

`CLAUDE_CODE_RETRY_WATCHDOG_USAGE_LIMIT_RECHECK_MS` (v2.1.305 or later) is the "Minimum interval in milliseconds between checks of whether a usage limit was already lifted, while a request waits for that limit to reset". The reference continues: "When a check finds the limit lifted, the request goes out at once" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)).

Checks "are made only for a claude.ai subscription's session or weekly limit while usage credits aren't in use, and not while `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). An unattended run on API-key auth, Bedrock, Vertex, or a gateway gets nothing from the variable.

The accepted range runs "from `60000`, one minute, to `10800000`, three hours", and the reference adds: "When this variable is unset or its value is outside that range, no checks are made" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)). A value below the floor does not clamp. An operator tightening `60000` to `30000` turns rechecking off.

## When this backfires

- A ceiling shorter than the usual time until reset. Every stall becomes a kill, and a run with expensive setup re-pays it on the next fire. Measure typical reset distances before picking a number.
- A run that ends on the ceiling and says nothing. Its artifact looks like a run that found nothing, which is the state an [unattended run reporting contract](../../workflows/unattended-run-reporting-contract.md) exists to keep distinguishable.
- Sole ownership of the quota, with nothing queued. Waiting can preserve completed setup work. For `MAX_WAIT_MS`, the documented unset behavior is "the wait has no limit" ([Claude Code environment variables](https://code.claude.com/docs/en/env-vars)).

## Example

The reference gives `1800000` as a 30-minute value for `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` ([environment variables](https://code.claude.com/docs/en/env-vars)). With the watchdog enabled, that budget applies to each API request's waiting on `429` and `529` errors. Once spent, the next such error ends the request. Do not read the value as a timer that terminates the process after 30 minutes.

Set these documented values in the shell that starts the unattended run:

```bash
export CLAUDE_CODE_RETRY_WATCHDOG=1
export CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS=1800000
```

## Key Takeaways

- Compare the reported reset with your scheduler's next useful run before choosing a wait ceiling.
- Choose a ceiling based on contention, reset distance, and restart cost.
- `MAX_WAIT_MS` ends a request on the next qualifying error after its wait budget is spent; `MAX_USAGE_LIMIT_WAIT_MS` declines up front on the reported reset distance.
- The recheck interval works only for a claude.ai subscription's session or weekly limit, without usage credits in play, and a value outside one minute to three hours turns it off.
- A run that ends on its ceiling has to report that, or it is indistinguishable from a run that found nothing.

## Related

- [Unattended Run Reporting: What the One Message Must Say](../../workflows/unattended-run-reporting-contract.md) — the contract the ceiling's failure state has to report into
- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — the permission sibling of the same unattended posture
- [Headless Claude in CI: Using -p and --max-turns for Safe Pipeline Integration](../../workflows/headless-claude-ci.md) — the step-count bound that sits alongside this wall-clock one
- [Bounding a Headless Codex Run Without a Turn Cap](../../workflows/headless-codex-bounding.md) — the same bounding problem on a harness with no turn cap
- [Recurring Agent Job Delegation: Widen Remit on Evidence](../../workflows/recurring-agent-job-delegation.md) — where the scheduled fire that a killed run falls back to comes from
