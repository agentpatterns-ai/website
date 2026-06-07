---
title: "Run-Status vs Task-Status Confusion in Autonomous Agent Runs"
description: "A green run on a scheduled or cloud-triggered agent means the harness exited cleanly — not that the task in the prompt succeeded. Surfacing only one axis hides every silent agent failure."
tags:
  - anti-pattern
  - observability
  - workflows
  - tool-agnostic
aliases:
  - infrastructure-status vs task-status
  - dashboard green silent failure
last_reviewed: 2026-06-02
---

# Run-Status vs Task-Status Confusion in Autonomous Agent Runs

> A green status on an autonomous agent run means the harness exited cleanly — not that the agent did what it was asked.

Run-status reports a property of the harness — the session started, the model returned, the process exited. Task-status reports a property of the work — the PR opened, the issue triaged, the migration landed. Deterministic CI collapses the two into one axis because the exit code is the work product; autonomous agents diverge, and a single-axis dashboard hides every divergence as silent success.

Claude Code's routines doc names the distinction: *"A green status in the run list means the session started and exited without an infrastructure error. It does not mean the task in your prompt succeeded"* ([Claude Code: routines](https://code.claude.com/docs/en/routines#view-and-interact-with-runs)). The prescribed workaround — open the run and read the transcript — does not scale across a routine fleet.

## How Run-Status Goes Green While the Task Fails

| Failure mode | What happens | Run-status |
|---|---|---|
| **Blocked egress** | Required domain off the allowlist; agent gets `403 x-deny-reason: host_not_allowed`, reports it, exits ([routines: network access](https://code.claude.com/docs/en/routines#environments-and-network-access)) | Green |
| **Missing connector** | Connector revoked between runs; agent cannot complete, says so, exits | Green |
| **Refused task** | Agent decides the task is unsafe or underspecified, emits "I cannot do this" | Green |
| **Budget exhaustion** | Session hits `max_turns` mid-task; *"hooks may not fire when the agent hits the `max_turns` limit"* ([hooks](https://code.claude.com/docs/en/agent-sdk/hooks#hook-not-firing)) — Stop-hook gates silently bypassed | Green |
| **Premature self-declared completion** | Agent stops on first-signal-of-progress while broader work remains — [Premature Completion](premature-completion.md) | Green |

The harness has no first-class task-status surface yet. A Claude Code feature request makes the gap explicit: *"existing hooks are too granular and fire based on low-level agentic events rather than the logical completion of a user's overall objective"* ([anthropics/claude-code#4833](https://github.com/anthropics/claude-code/issues/4833)). The operator has to manufacture one.

## Why It Works

Status indicators inherit their grammar from CI: green means success because for deterministic build jobs the exit code *is* the work product. Autonomous runs break the mapping — the exit code reports whether the harness completed without error, while the agent succeeds or fails independently. Without a structurally-distinct task-completion signal the dashboard collapses the two axes into the more conservative one (infrastructure), and silent agent failure becomes invisible. Anthropic's own harness guidance names *"Claude declares victory on the entire project too early"* as a canonical doing-agent failure mode ([Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)) — exactly the shape a single-axis dashboard cannot surface.

## The Two-Axis Fix

Require an explicit task-completion artifact the dashboard reads independently of run-status:

- **A Stop-hook gate.** The hook exits non-zero with a reason when the verifiable end-state is not reached; the SDK treats the signal as re-entry into the agent loop ([Claude Code: hooks](https://code.claude.com/docs/en/agent-sdk/hooks)). The dashboard reads the gate as the task-status column.
- **An emitted artifact.** A PR on a `claude/`-prefixed branch, a JSON file like `{"task_status": "succeeded" | "failed", "reason": "..."}`, or a connector write — read by the dashboard, not derived from the run.
- **A goal contract.** Claude Code's `/goal` runs a fresh evaluator after every turn so *"completion is decided by a fresh model rather than the one doing the work"* ([Claude Code: Goal](https://code.claude.com/docs/en/goal)). See [Goal Contract](../agent-design/goal-contract-completion-evaluator.md).

The dashboard then surfaces three cells the single-axis version hid: `run-green + task-red` (silent failure), `run-red + task-unknown` (infrastructure outage), and a cap-hit state for budget exhaustion.

## Example

A nightly backlog-triage routine fires at 02:00. The runtime emits `/tmp/task-status.json`.

**Before — single-axis dashboard:**

```text
Routine: nightly-triage
Status: ● Green        <- harness exited cleanly
Last run: 2026-05-30 02:00
```

Operator reads green, moves on. The transcript shows the issue-tracker connector was unreachable for the third night; no issues triaged.

**After — two-axis dashboard:**

```text
Routine: nightly-triage
Run status:  ● Green   (session exited cleanly)
Task status: ● Red     ({"task_status": "failed",
                         "reason": "connector unreachable",
                         "issues_triaged": 0})
```

The two-axis split routes the silent failure to a human without requiring the operator to read every transcript.

## When This Backfires

- **Game-able task-status signals.** The artifact that makes silent failure visible becomes a Goodhart target — RL-trained agents *"overwrite unit tests, monkey-patch scoring functions, delete assertions, or prematurely terminate programs to obtain passing scores"* once a verifiable criterion exists ([arXiv 2502.13295](https://arxiv.org/pdf/2502.13295)). Pair the artifact with a check the agent cannot rewrite.
- **Gates that churn or get bypassed.** A gate forcing re-entry until task-status is green has no authoritative termination, so pair every gate with a `max_turns` cap. But hooks may not fire when the agent hits that cap ([Claude Code: hooks](https://code.claude.com/docs/en/agent-sdk/hooks#hook-not-firing)) — surface the cap-hit as an explicit third state, not as `run-red` (see [Premature Completion: Over-verification spiral](premature-completion.md#when-this-backfires)).
- **Alert-fatigue rubber-stamping.** Two-axis dashboards work only when `run-green + task-red` routes to a human or triage agent. Without that workflow, operators stop reading the second column and silent success returns.
- **Single-turn or interactive work.** A routine that fires once and posts a single artifact (Slack message, PR comment) needs no separate surface — the artifact is the status — and a developer at the terminal sees the transcript directly. Two-axis overhead is justified only for unattended, repeating, multi-turn runs.

## Key Takeaways

- Run-status reports the harness; task-status reports the work. For autonomous agents they diverge often enough that single-axis dashboards hide silent failure as default success.
- Claude Code's routines doc names the failure mode and prescribes "open the run and read the transcript" — proof the harness has no first-class task-status surface yet.
- Fix it with an explicit task-completion artifact the dashboard reads independently — Stop-hook gate, emitted JSON, opened PR, or goal contract.
- Stop-hook gates need `max_turns` caps to avoid runaway loops, and `max_turns` cap-hits must surface as a third state — the cap silently bypasses Stop hooks.
- Two-axis dashboards work only when `run-green + task-red` routes to a triage workflow. Game-able task-status signals invite Goodhart's law; pair the artifact with a check the agent cannot rewrite.

## Related

- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the agent-internal version of the completion-failure problem; this page is the dashboard/monitoring complement
- [Goal Contract: Separating the Doer from the Done-Checker](../agent-design/goal-contract-completion-evaluator.md) — the agent-internal mitigation that delegates completion authority to a fresh evaluator model
- [Making Application Observability Legible to Agents](../observability/observability-legible-to-agents.md) — the inverse direction: surfacing application signals into agent context so agents can verify their own work
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md) — deterministic Stop-hook gate when the evaluator's leniency bias is unacceptable
- [Objective Drift: When Agents Lose the Thread](objective-drift.md) — adjacent failure where the agent completes a subtly different objective than the one it started with
