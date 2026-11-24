---
title: "MCP Tasks in Claude Code: Background Calls and When to Wait"
description: "Claude Code backgrounds a server-run MCP task at once and a long main-conversation MCP call after two minutes. Two variables make Claude wait; limits and failure modes follow."
tags:
  - claude
  - mcp
  - agent-design
aliases:
  - MCP tasks in Claude Code
  - automatic backgrounding of MCP tool calls
  - wait for an MCP task result
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-24
status: current
---

# MCP Tasks in Claude Code: Background Calls and When to Wait

> Claude Code backgrounds a long MCP call as a server-run task or after two minutes; environment variables change when Claude waits.

A long MCP tool call reaches the background by one of two routes. A server that supports the MCP tasks extension can answer with a task, and the [2.1.319 changelog entry](https://code.claude.com/docs/en/changelog) says Claude Code then "moves it to the background right away and tells Claude the result when it finishes". Any other main-conversation call still running after two minutes moves there on a timer ([mcp](https://code.claude.com/docs/en/mcp.md#automatic-backgrounding-of-long-tool-calls)). The route decides whether the job can outlive the session. Two environment variables decide whether Claude waits.

## Three kinds of long MCP call

| | MCP task | Auto-backgrounded call | Plain call |
|---|---|---|---|
| Who runs the job | The server, after it accepts the call ([mcp](https://code.claude.com/docs/en/mcp.md#mcp-tasks-that-run-on-the-server)) | The server, inside the open tool call | The server, inside the open tool call |
| When Claude is released | When the server accepts the job, unless you make Claude wait; Claude Code backgrounds it at once from 2.1.319 | When the call is still running after two minutes by default | When the call ends |
| After you exit Claude Code | A remote server's task keeps running; a stdio server's process stops | The call does not survive exiting the session ([mcp](https://code.claude.com/docs/en/mcp.md#automatic-backgrounding-of-long-tool-calls)) | Not applicable |

Auto-backgrounding skips a call from a subagent or an IDE server, and any call in a non-interactive session unless `CLAUDE_AUTO_BACKGROUND_TASKS` is `1`. Those calls stay plain calls ([mcp](https://code.claude.com/docs/en/mcp.md#automatic-backgrounding-of-long-tool-calls)). The two-minute rule dates from 2.1.212, released July 17, 2026 ([changelog](https://code.claude.com/docs/en/changelog)).

An MCP task needs more. Per [mcp.md](https://code.claude.com/docs/en/mcp.md#what-a-call-needs-to-become-an-mcp-task), all of these hold:

- The server supports tasks, and connects over HTTP, stdio or as a claude.ai connector on protocol revision 2026-07-28. Setting `MCP_SDK_GENERATION=v1` or `MCP_PROTOCOL_NEGOTIATION=legacy` rules that out.
- The session is a terminal CLI, Agent SDK or GitHub Actions session on v2.1.304 or later. Cloud sessions have tasks only if Anthropic enabled them for the account or organization. The VS Code extension and local desktop sessions do not have them.
- The session fetches feature flags, so not on a third-party provider such as Amazon Bedrock, and not with telemetry or flag fetching turned off. The 2.1.319 changelog entry says otherwise for the terminal; see [Where the sources disagree](#where-the-sources-disagree).
- The call comes from the main conversation, not a subagent.
- A non-interactive Agent SDK or `--input-format stream-json` session has `CLAUDE_AUTO_BACKGROUND_TASKS` at `1`, `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` not at `1`, and `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` not at `0`.

The feature is in public beta ([mcp](https://code.claude.com/docs/en/mcp.md#mcp-tasks-that-run-on-the-server)). The protocol side is the [MCP tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview), which Claude Code reaches on revision 2026-07-28 connections (see [Stateless MCP](../../standards/stateless-mcp.md) for that revision).

## Where the sources disagree

The changelog and the two docs pages fetched on November 24, 2026 differ on four points. This page states each condition as written and settles none of them.

- On the first version, the changelog lists "Added support for MCP tasks in the terminal" under 2.1.319 (November 6, 2026) and adds `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` in the same entry. The mcp.md note says MCP tasks require v2.1.304 or later, and the env-vars row says `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND` requires v2.1.304 or later. The 2.1.304 changelog section (October 19, 2026) has no MCP-task entry. Version 2.1.319 or later satisfies both texts.
- On feature-flag fetching, the 2.1.319 changelog entry says it "Changed MCP tasks to work in the terminal without feature-flag fetching (Bedrock, Vertex, Foundry, LLM gateways, `DISABLE_TELEMETRY`)". The mcp.md requirements list still excludes a third-party provider and sessions with telemetry or flag fetching off, and the [env-vars list of flag-gated features](https://code.claude.com/docs/en/env-vars.md#features-that-need-feature-flag-fetching) still names MCP tasks. Neither docs page mentions 2.1.319 for this condition. The changelog entry names terminal sessions only.
- The opt-out variable `CLAUDE_CODE_DISABLE_MCP_TASKS=1` turns MCP tasks off in the 2.1.319 changelog entry. It appears in neither mcp.md nor env-vars.
- On answering later, mcp.md says answering a task's question later requires v2.1.324 or later. The changelog has no 2.1.324 section and lists the change under 2.1.325 (November 13, 2026). Version 2.1.325 or later satisfies both.

## What Claude and the person see

For a task, Claude's tool call returns once the server accepts the job, so Claude keeps working unless you make Claude wait ([mcp](https://code.claude.com/docs/en/mcp.md#mcp-tasks-that-run-on-the-server)). For an auto-backgrounded call, Claude receives the task ID at once and the result arrives as a task notification when the call settles ([mcp](https://code.claude.com/docs/en/mcp.md#automatic-backgrounding-of-long-tool-calls)).

The person sees a footer count such as `1 MCP task` and, when the job ends, one transcript line:

```text
MCP task <server task id> (<server>/<tool>) completed.
```

The result goes to Claude, not into the transcript, so you ask Claude for it. If Claude is idle when the result arrives, Claude starts on it unprompted ([mcp](https://code.claude.com/docs/en/mcp.md#stop-an-mcp-task-or-get-its-result)).

A running task can ask you a question through an elicitation dialog, covered in [MCP Elicitation](../../tool-engineering/mcp-elicitation.md). While `/tasks` is open the dialog stays hidden. Unless Claude is set to wait, `Esc` in the dialog answers later, and the question reopens from the task's details in `/tasks` ([mcp](https://code.claude.com/docs/en/mcp.md#answer-a-question-from-an-mcp-task)). From 2.1.325 Claude is told when a task waits for your answer and can point you to `/tasks` ([changelog](https://code.claude.com/docs/en/changelog)). In a non-interactive session Claude Code asks the server to cancel a task that requests input, without running your `Elicitation` hooks ([mcp](https://code.claude.com/docs/en/mcp.md#answer-a-question-from-an-mcp-task)).

## Wait or background

Two variables make Claude wait in an interactive session ([mcp](https://code.claude.com/docs/en/mcp.md#make-claude-wait-for-the-result-of-an-mcp-task)). The 2.1.319 changelog entry added the first.

| Variable | What Claude waits for | What still moves to the background |
|---|---|---|
| `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND=1` | A task's result | While automatic backgrounding is on, a call still running after two minutes by default moves as a plain background call, not an MCP task, and does not survive exiting the session |
| `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS=0` | Every MCP tool call, until the call ends | Nothing, because this turns automatic backgrounding off |

So the first switch keeps short tasks in place but gives up server-side durability for long ones. Only the second blocks for the whole call, and it covers every MCP call, not just tasks. Setting `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` or starting in bare mode does not make Claude wait for MCP tasks on its own ([mcp](https://code.claude.com/docs/en/mcp.md#make-claude-wait-for-the-result-of-an-mcp-task)). The `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` default is 120000 ([env-vars](https://code.claude.com/docs/en/env-vars)).

Waiting changes the time limits. A background task has no Claude Code time limit by default. The wall-clock limit and idle timeout apply until the server answers with the task, and apply to the whole task if you make Claude wait. Answered status checks count as activity for the idle timeout ([mcp](https://code.claude.com/docs/en/mcp.md#time-limits-on-mcp-tasks)). The wall-clock default is 100000000 ms, about 28 hours ([env-vars](https://code.claude.com/docs/en/env-vars)). The idle window defaults to five minutes for HTTP, SSE, WebSocket and claude.ai connector servers and 30 minutes for stdio ([mcp](https://code.claude.com/docs/en/mcp.md#time-limits-on-mcp-tool-calls)). While Claude waits, `Esc` or hitting either limit ends the call and Claude Code asks the server to cancel the task.

### Choosing

The sources list the switches and give no rule for choosing between them. The rule below is this page's own reading of the trade-off, not Anthropic's guidance.

- Keep the defaults when a job runs for minutes and nothing in the turn depends on it. The cost is that you ask Claude for the result, and a stdio server's process stops when you exit.
- Set `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND=1` when most jobs finish within two minutes and Claude's next step needs the result. The cost is that a job past two minutes becomes a plain call that does not survive exiting the session.
- Set `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS=0` only when the session must block on every MCP call. The cost is a blocked session for each slow call, with `Esc` canceling it.

## Failure modes

| Situation | What happens | What to do |
|---|---|---|
| A one-shot `claude -p "<prompt>"` run | It does not get MCP tasks. Agent SDK and stream-json runs can, but do not wait for tasks once input closes ([mcp](https://code.claude.com/docs/en/mcp.md#what-a-call-needs-to-become-an-mcp-task)) | Keep input open, or run interactively |
| You exit with a stdio server | The server's process stops, even though `/tasks` says its tasks keep running | Let the task finish or stop it in `/tasks` first, unless the server's documentation says the work outlives the process ([mcp](https://code.claude.com/docs/en/mcp.md#exit-clear-or-resume-while-an-mcp-task-runs)) |
| You exit with a remote server | The task keeps running, and no exit option cancels it | `claude --resume` or `--continue` with the same server name and connection settings; Claude gets the result if the server still knows the task ([mcp](https://code.claude.com/docs/en/mcp.md#exit-clear-or-resume-while-an-mcp-task-runs)) |
| You stop a task | In `/tasks`, press `x`. Claude Code stops following the task and asks the server to cancel it, though the server may still finish it. `Esc` does not stop a background task ([mcp](https://code.claude.com/docs/en/mcp.md#stop-an-mcp-task-or-get-its-result)) | Reconnect a disconnected server from `/mcp` first so the cancel request can go out |
| A transcript line ends `outcome unknown.` | Claude Code stopped following the task after the server rejected its ID or refused permanently | "A second call may repeat the work. Before calling the tool again, find out from the server what was done" ([mcp](https://code.claude.com/docs/en/mcp.md#status-messages-on-an-mcp-task)) |

The `outcome unknown.` case is the lost-response problem in [Tool Operability](../../patterns/agent-design/tool-operability-lost-responses.md): committed and uncommitted work look the same, so check state before a retry.

Three changelog fixes bear on older installs ([changelog](https://code.claude.com/docs/en/changelog)).

- 2.1.325 fixed background MCP tasks that stopped updating after another call to the same server lost the connection, when a later call reconnects.
- 2.1.329 fixed tasks that stalled after a slow reconnect.
- 2.1.330 fixed a running task being reported as stopped when you move a session to the background. The background session follows the task, but not if its server uses stdio or sets headers.

## If you write the server

The extension overview gives the reason for tasks: "Many clients and transport intermediaries impose timeouts that make this impractical beyond a few seconds", and "The server decides per-request whether to create a task" ([MCP tasks overview](https://modelcontextprotocol.io/extensions/tasks/overview)). On a revision 2026-07-28 connection, each request carries `"io.modelcontextprotocol/tasks": {}` under `extensions` in `params._meta["io.modelcontextprotocol/clientCapabilities"]`, and a request that cannot become a task omits it ([mcp](https://code.claude.com/docs/en/mcp.md#mcp-tasks-for-server-authors)).

Answer with a task only when the request carries the extension. Otherwise the call fails with the tool error `Unsupported result type 'task' for tools/call`. This is the task answer shape mcp.md gives, copied from the page:

```json
{
  "resultType": "task",
  "taskId": "build-7f3a9c2e",
  "status": "working",
  "statusMessage": "Compiling, 40 of 212 files done",
  "createdAt": "2026-10-22T14:03:07Z",
  "lastUpdatedAt": "2026-10-22T14:03:07Z",
  "ttlMs": null,
  "pollIntervalMs": 10000
}
```

- `taskId` is required, at most 128 printable ASCII characters with no spaces. `status` is one of `working`, `input_required`, `completed`, `failed` or `cancelled` ([mcp](https://code.claude.com/docs/en/mcp.md#answer-the-call-with-a-task)).
- `pollIntervalMs` is clamped to between 250 and 30000. Claude Code uses 2000 when the field is absent or `null` ([mcp](https://code.claude.com/docs/en/mcp.md#answer-the-call-with-a-task)).
- Claude Code polls with `tasks/get`. It does not use `tasks/result`, `tasks/list` or `notifications/tasks`, so put the outcome in your `tasks/get` responses ([mcp](https://code.claude.com/docs/en/mcp.md#report-status-results-and-questions)).
- Keep a finished task's result for at least an hour, and longer if you can, because a person can exit while a remote server's task runs and resume later ([mcp](https://code.claude.com/docs/en/mcp.md#choose-a-time-to-live-and-a-poll-interval)).
- On an HTTP or claude.ai connector server, the task answer must start within the per-request timer, so accept the job first and do the work after ([mcp](https://code.claude.com/docs/en/mcp.md#answer-the-call-with-a-task)).
- Cancellation is cooperative: "the server acknowledges the intent but is not obligated to stop the work" ([MCP tasks overview](https://modelcontextprotocol.io/extensions/tasks/overview)). Claude Code says the same of its stop action.

The 2025-11-25 specification defined an earlier, experimental form of tasks with `tasks/result` and `tasks/list` ([MCP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)). mcp.md says Claude Code does not use those methods, so do not build against that shape for Claude Code. For design context, see [MCP Server Design](../../tool-engineering/mcp-server-design.md).

## Key Takeaways

- Among calls that meet Claude Code's conditions, the server decides per request which become tasks. Your settings decide whether Claude waits, whether a long call moves to the background, and, through variables such as `MCP_SDK_GENERATION=v1` or `CLAUDE_AUTO_BACKGROUND_TASKS` in a non-interactive session, whether a call can become a task at all.
- `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND=1` still moves a call after two minutes, as a plain call that does not survive exiting the session. Only `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS=0` blocks for the whole call, on every MCP call.
- An `outcome unknown.` line means the work may have run. Ask the server what happened before you call the tool again.
- The docs and changelog disagree on the first version (2.1.304 or 2.1.319) and on flag fetching. Use 2.1.325 or later to satisfy both version texts, and test on your provider.
- Server authors check for the extension before answering with a task, and keep a finished result for at least an hour.

## Related

- [MCP Elicitation: Servers Requesting Structured Input Mid-Task](../../tool-engineering/mcp-elicitation.md) — the dialog a running task can open
- [Stateless MCP](../../standards/stateless-mcp.md) — the 2026-07-28 protocol revision
- [Judging MCP Capability Readiness by Client Adoption](../../tool-engineering/mcp-capability-readiness.md) — when a spec feature is dependable
- [Tool Operability: Interfaces That Survive a Lost Response](../../patterns/agent-design/tool-operability-lost-responses.md) — retrying after an unknown outcome
- [Monitor Tool](monitor-tool.md) — streaming output from a background script
- [Host-Controlled Backgrounding for Claude Subagent Calls](../../patterns/multi-agent/host-controlled-subagent-backgrounding.md) — the same decision for subagents
- [Define Async Task Update and Approval Contracts](../../patterns/multi-agent/async-task-update-contracts.md) — update and cancellation contracts
- [MCP Server Design](../../tool-engineering/mcp-server-design.md) — building agent-friendly servers
