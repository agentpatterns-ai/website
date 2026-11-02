---
title: "Wait Primitive Plus Shell-Sleep Deny"
description: "Give an agent a first-class way to wait, then block the foreground shell sleep it would otherwise use, as Claude Code 2.1.310 did together."
term: "Wait Primitive Plus Shell-Sleep Deny"
tags:
  - pattern
  - agent-design
  - cost-performance
  - claude
aliases:
  - foreground sleep block
  - wait primitive pairing
  - deny shell sleep
applies_to: "claude-code@2.1.310"
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Wait Primitive Plus Shell-Sleep Deny

> Ship a first-class way for an agent to wait, then block the foreground shell sleep it would otherwise use.

An agent told to wait for something can reach for `sleep` in a shell. A foreground sleep holds the tool call open until the sleep ends. This is design reasoning, not a measured result. The pairing has two halves. Supply a primitive that waits without holding the conversation, then deny the shell equivalent. An instruction such as "do not sleep" asks the model to hold back; a deny rule does not.

## The Claude Code 2.1.310 change

Claude Code 2.1.310 (October 23, 2026) shipped both halves in one changelog line:

> "Added the Monitor tool and plugin monitors on Bedrock, Vertex, and Foundry, and when telemetry or nonessential traffic is disabled; long foreground sleeps are now blocked there too"

Source: [Claude Code changelog, 2.1.310](https://code.claude.com/docs/en/changelog).

The entry names the targets where the primitive was missing: Bedrock, Vertex, Foundry, and sessions with telemetry or nonessential traffic disabled. The sleep block lands on the same targets, in the same release. The entry gives no threshold for "long", no reason, and no billing effect.

The tools reference confirms the availability side. On those targets, "Monitor requires Claude Code v2.1.310 or later" ([Tools reference](https://code.claude.com/docs/en/tools-reference#monitor-tool)).

## What each half does

Monitor "lets Claude watch something in the background and react when it changes, without pausing the conversation" ([Tools reference](https://code.claude.com/docs/en/tools-reference#monitor-tool)).

A foreground `sleep` does the opposite. The tools reference says a foreground command that reaches its timeout moves to the background "unless the command starts with `sleep`" ([Tools reference](https://code.claude.com/docs/en/tools-reference#foreground-commands-that-move-to-the-background)). 

| Harness state | Result |
|---|---|
| Deny, no primitive | Waiting becomes impossible, so the agent improvises. |
| Primitive, no deny | The old foreground sleep stays available, and the model keeps choosing it. |
| Both | Long foreground sleeps are blocked, and a supported background wait mechanism is available. |

The first two rows are inference from the design, not measured results.

## The three waits an agent needs

Not every wait is the same problem. Match each to its own mechanism.

| Wait | Mechanism in Claude Code | Source |
|---|---|---|
| An external condition (a log line, a CI result, a file) | Monitor, or a scheduled re-check | [Tools reference](https://code.claude.com/docs/en/tools-reference#monitor-tool) |
| The agent's own background work | `run_in_background`, then `Read` of the task's output file | [Tools reference](https://code.claude.com/docs/en/tools-reference) |
| A human decision | `AskUserQuestion`, which stays open until answered | [Tools reference](https://code.claude.com/docs/en/tools-reference) |

Polling fits the first wait, where nothing signals the change. For the second, `Read` retrieves the task's output file. The reference does not say how a task reports completion, so check that for your build before you rely on it. For the third, the question stays open until answered unless the user sets `askUserQuestionTimeout` to `60s`, `5m`, or `10m` ([Tools reference](https://code.claude.com/docs/en/tools-reference)).

Match the check interval to how fast the watched thing changes; the [Monitor tool](../../tools/claude/monitor-tool.md) page covers when scheduled polling fits better. Every watch has a deadline: 5 minutes by default, at most 30, and at most 10 in a `-p` run ([Tools reference](https://code.claude.com/docs/en/tools-reference#monitor-tool)).

## Applying it in your own harness

You can build the deny half with Claude Code permissions. Deny rules are evaluated first, and "an allow rule can't carve an exception out of a deny rule" ([Permissions](https://code.claude.com/docs/en/permissions)). A rule such as `Bash(sleep *)` is a candidate. Deny and ask rules "apply when any subcommand matches them", including commands nested in a `for` loop or a command substitution ([Permissions](https://code.claude.com/docs/en/permissions)).

Rules match command text. A sleep inside a script file or an interpreter call such as `python -c` does not appear in that text. Audit for those separately.

Audit in this order. Search transcripts and scripts for agent-initiated `sleep` calls. Name the wait behind each one. Find the missing primitive for that wait; an added instruction is the last resort. Deny the sleep only after the primitive exists in every environment the agent runs in, as 2.1.310 did for Bedrock, Vertex, Foundry, and telemetry-off sessions.

## When this backfires

- A deny with no primitive. The agent loses its only way to wait, and the task stalls or ends early.
- A deny rule that matches text only. Sleeps hidden in scripts pass through, so the rule gives false confidence.
- A primitive with a deadline shorter than the wait. A 30-minute cap on Monitor does not cover an overnight job; use a scheduled job or an external supervisor.
- A short, legitimate pause. The changelog blocks "long" sleeps and does not define the line.

## Key Takeaways

- Treat the pairing as the unit of design: a primitive that waits without pausing the conversation, plus a deny on the shell equivalent.
- Classify each wait before choosing a fix. Polling fits waits on an external condition.
- Roll the primitive out to every environment before the deny reaches it, and audit scripts by hand, since a text-matching deny misses them.
- The source shows the release shipped both halves. It does not measure a cost or latency gain.

## Related

- [Monitor Tool: Event Streaming from Background Scripts](../../tools/claude/monitor-tool.md) — the wait primitive in this pairing
- [Plugin Background Monitors](../../tools/claude/plugin-background-monitors.md) — monitors a plugin starts without a prompt
- [Session Scheduling](../../tools/claude/session-scheduling.md) — timer-based re-checks for slow-changing conditions
- [Async Non-Blocking Subagent Dispatch](../multi-agent/async-non-blocking-subagent-dispatch.md) — the same non-blocking idea applied to delegates
- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — what an agent does when a deny leaves it no path
- [Bounding an Unattended Run's Wait on a Usage-Limit Reset](usage-limit-wait-ceiling.md) — a wall-clock ceiling on one kind of wait
