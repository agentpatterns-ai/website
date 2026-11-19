---
title: "PostToolUse Hooks After an Interrupted Turn in Claude Code"
term: "PostToolUse After an Interrupt"
description: "Since v2.1.319, PostToolUse hooks survive message interrupts with a 10-second command-hook limit. Queued ! commands or disabled background tasks make Ctrl+Enter cancel them."
tags:
  - pattern
  - agent-design
  - hooks
  - claude
aliases:
  - PostToolUse interrupt budget
  - 10-second PostToolUse budget
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-09
maturity: emerging
status: current
---

# PostToolUse Hooks After an Interrupted Turn in Claude Code

> PostToolUse hooks survive message interrupts, except when a queued shell command or disabled background tasks make `Ctrl+Enter` act as `Esc`.

Claude Code v2.1.319 runs `PostToolUse` hooks on a tool call that finishes after a new message interrupts the turn, and gives them 10 seconds to finish. The changelog states it as "Changed PostToolUse hooks to run, with up to 10 seconds to finish, on tool calls that finish after a new message interrupts the turn" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Before that release, "the hooks didn't start after you interrupted the turn with a message, and a running hook was stopped" ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-after-an-interrupt)). The guarantee is narrow. Which key you press decides whether the hooks run at all.

## Which interrupts run the hooks

The [hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-after-an-interrupt) splits the case by key:

| Key | Turn | PostToolUse hooks |
|---|---|---|
| `Ctrl+Enter`, tool still running, tool finishes | Ends | Run on the result, with 10 seconds to finish |
| `Ctrl+Enter` with a `!` command queued first, or background tasks disabled | Ends, the key acts as `Esc` | Canceled |
| `Enter` | Not interrupted | Keep their configured `timeout` |
| `Esc` | Ends | Canceled at once |

`Ctrl+Enter` does not always end the turn. Shell commands, subagents, and other work that can move to the background keep running there, and "Claude reads your messages in the same turn". Apart from the two `Esc` cases in the table, the key interrupts only when Claude is writing a response or "running something that can't move to the background" ([interactive mode](https://code.claude.com/docs/en/interactive-mode#when-claude-code-sends-what-you-queued)).

`PostToolUse` also needs a successful tool. The reference opens its entry with "Runs immediately after a tool completes successfully" ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse)). `PostToolUseFailure` does not cover the gap either: "Cancelling a running tool does not fire this hook" ([hooks reference](https://code.claude.com/docs/en/hooks#posttoolusefailure-input)).

## The 10-second kill

On this path 10 seconds is the ceiling. "When the 10 seconds are up, Claude Code kills a command hook that is still running, whatever its `timeout`" ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-after-an-interrupt)). The default `timeout` for a command hook is 600 seconds ([hooks reference](https://code.claude.com/docs/en/hooks#common-fields)), so a hook that relies on the default gets one sixtieth of its usual time.

The documented escape is `async: true`. It removes the cap, and the cost is that the hook "can't block or rewrite the result" ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-after-an-interrupt)). Async hooks have a second limit: under `claude -p`, Claude Code "kills any async hook still running at teardown and finalizes it with outcome `cancelled`" ([hooks reference](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background)).

## Design rules for hook authors

- Keep synchronous `PostToolUse` work under 10 seconds if it must survive an interrupt. The hooks reference already lists "deployments, test suites, or external API calls" as long-running work for `async: true` ([hooks reference](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background)).
- Write state so a kill at any line leaves it readable. One complete record per run survives a kill better than several dependent updates.
- Split a hook that both gates and does slow work. A fast synchronous check keeps the block, and an async hook carries the slow part.
- Do not treat `PostToolUse` as a complete audit log. `Esc` and canceled tools still leave gaps. The tool's side effects are already done either way: "The tool has already run by the time the hook fires" ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-decision-control)).

## Why it works

The change adds hook runs and then bounds them. Before v2.1.319 an interrupt with a message stopped post-tool work outright. Now the hooks start on the finished result, and the 10-second kill caps how long they run after the turn ends, whatever their `timeout` ([hooks reference](https://code.claude.com/docs/en/hooks#posttooluse-after-an-interrupt)). The docs state the behavior and the kill. They do not state the design reason.

## When this backfires

- A gating hook that needs more than 10 seconds has no clean fix. `async: true` lifts the cap but gives up the block, so the hook has to get faster.
- A multi-step state write gets cut between steps. An append to a log followed by an index update leaves the two out of step.
- Teams that interrupt with `Esc` by habit, or run with background tasks disabled, keep the pre-2.1.319 behavior and see no change.
- The async escape does not hold under `claude -p`, which kills async hooks still running at teardown.

## Example

Test the interrupt path with a hook that is slower than the budget. This `PostToolUse` command logs a start line, sleeps 15 seconds, then logs an end line:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo start >> /tmp/ptu-interrupt.log; sleep 15; echo end >> /tmp/ptu-interrupt.log"
          }
        ]
      }
    ]
  }
}
```

Start Claude Code with `claude --debug-file <path>`, which writes hook execution details to that file ([hooks reference](https://code.claude.com/docs/en/hooks#debug-hooks)). Then trigger the hook three times:

| Trigger | Expected from the docs |
|---|---|
| `Ctrl+Enter` while a tool that cannot move to the background runs | Start line, no end line: killed at 10 seconds |
| `Enter` during the same tool | Start and end lines: the 600-second default `timeout` applies |
| `Esc` during the same tool | No complete run: hooks canceled at once |

An end line on the `Ctrl+Enter` run means the key did not end the turn. Check whether the tool moved to the background instead ([interactive mode](https://code.claude.com/docs/en/interactive-mode#when-claude-code-sends-what-you-queued)).

## Key Takeaways

- Use `Enter` to keep the hook’s normal timeout. For `Ctrl+Enter`, check that background tasks are enabled and no `!` command is queued first.
- Budget a synchronous hook for 10 seconds, not its configured `timeout`, if it has to finish after an interrupt.
- Give slow observers `async: true` and keep gating hooks fast, because only synchronous hooks can block.
- Run a 15-second test hook once per key before trusting a hook that writes state.

## Related

- [Hooks and Lifecycle Events: Intercepting Agent Behavior](../../tool-engineering/hooks-lifecycle-events.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../../tools/claude/posttooluse-auto-formatting.md)
- [PostToolUse continueOnBlock: Refusal With a Load-Bearing Reason](../../tool-engineering/posttooluse-continue-on-block.md)
- [Per-Surface Hook Matchers for Shell-Starting Tools](shell-surface-hook-matcher-coverage.md)
- [StopFailure Hook: Observability for API Error Termination](../../tool-engineering/stopfailure-hook.md)
