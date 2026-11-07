---
title: "Declaring a Per-Hook Failure Mode for Agent Policy Gates"
term: "Per-Hook Failure Mode"
description: "A hook that breaks is a third outcome beside allow and deny. Declare it per hook: fail closed on a verdict gate, fail open on an advisory check."
tags:
  - security
  - hooks
  - agent-design
  - tool-agnostic
aliases:
  - fail-closed hook callbacks
  - hook failure mode declaration
  - onFailure block for hooks
last_reviewed: 2026-11-03
maturity: emerging
---

# Declaring a Per-Hook Failure Mode for Agent Policy Gates

> A gate that breaks renders no verdict, so decide each hook's failure mode rather than inheriting the harness default.

A hook allows, denies, or renders no verdict at all because the script is missing, an import throws, the endpoint is unreachable, or the process runs past its timeout. Command and HTTP hook failures in Claude Code usually let the action through. Cursor also defaults to fail-open for crashes and timeouts. Copilot CLI's answer depends on how the hook is wired. Claude Code states its default in one line: "On most events, when a hook fails or times out, Claude Code still carries out the action" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)). Leaving the default in place is a decision.

## When a hook earns fail-closed

Two questions decide it, both about the one hook in front of you.

Does this hook render a verdict? A deny rule, a secret scan, or a merge gate exists to stop something, so its silence is a gap. A formatter or a style notice has nothing to protect. Cursor scopes its own recommendation the same way, naming security-critical MCP-execution hooks rather than hooks in general ([Cursor hooks](https://cursor.com/docs/agent/hooks#beforeshellexecution-beforemcpexecution)).

Can the person who hits the block fix it? The error message is the only thing between a stopped action and someone deleting the hook. Claude Code's block message carries the interpreter's own output, so a missing script surfaces as a module-resolution trace ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)). That reads as a fix to the hook's author and as noise to everyone else. Write the reason first, then set the field.

## What counts as a failure

For Claude Code command and HTTP hooks with `onFailure: "block"`, five things count as a failure: a hook that cannot start, an exit code other than 0 or 2, an HTTP error, a timeout, and output that fails JSON parsing or schema validation ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)). Two of them are easy to miss. A timeout counts, which turns a slow dependency into a stopped agent. An unexpected exit code counts "even if it printed JSON that allows the action, such as `permissionDecision: "allow"`". So a hook that exits 1 to warn starts blocking the day the field goes on. Have it exit 0 where it only warns. The [hook catalog](../tool-engineering/hook-catalog.md) covers the exit-code semantics underneath this.

## Where each harness puts the choice

The three harnesses disagree about who owns the decision.

| Harness | Default | Where the choice lives |
|---|---|---|
| Claude Code | Fail open on most events | `onFailure: "block"` per hook, added for command and HTTP hooks in 2.1.295 and extended to Agent SDK hook callbacks in 2.1.317 ([changelog](https://code.claude.com/docs/en/changelog#2-1-317)) |
| Cursor | Fail open | `failClosed: true` per hook, default `false`; unavailable on hooks configured from the dashboard ([Cursor hooks](https://cursor.com/docs/agent/hooks#cloud-distribution-enterprise-only)) |
| Copilot CLI | Mixed, fixed by transport | No per-hook field. A command `preToolUse` hook fails closed on a crash or non-zero exit; its timeouts and every HTTP `preToolUse` failure fail open ([hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference#hook-event-input-payloads)) |

The 2.1.317 release adds a declarative failure choice for Agent SDK callbacks ([changelog](https://code.claude.com/docs/en/changelog#2-1-317)). An Agent SDK callback runs inside the host process, and the SDK's advice for an HTTP logging callback is: "Catch errors inside your hook instead of letting them propagate." ([Claude Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks#make-http-requests-from-hooks)). A `try/catch` that catches a policy-check error and returns no denial leaves that check unenforced. Review callback bodies as well as configuration.

The cited SDK example catches errors in an advisory `PostToolUse` logger; it does not implement a policy gate. SDK callback timeouts already block `PreToolUse` calls ([SDK timeout reference](https://code.claude.com/docs/en/agent-sdk/hooks#hook-timeout)). A second event has that default: a `UserPromptSubmit` callback that times out blocks the prompt, "because a callback there can be acting as a policy gate that must not fail open" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#userpromptsubmit)). The Agent SDK hooks page does not document the new field as of 3 November 2026, so the changelog is its only source.

## Why it works

The two failure directions are not detected on the same timescale. Saltzer and Schroeder named the asymmetry in 1975: "A design or implementation mistake in a mechanism that gives explicit permission tends to fail by refusing permission, a safe situation, since it will be quickly detected. On the other hand, a design or implementation mistake in a mechanism that explicitly excludes access tends to fail by allowing access, a failure which may go unnoticed in normal use" ([Saltzer and Schroeder](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)).

A broken fail-open gate is the second case. It emits a transcript notice and a successful tool call, and the successful call is the part a developer sees, so the gap lasts as long as nobody reads notices. A broken fail-closed gate stops the action, and the person waiting reports it. The field does not make a gate more accurate. It moves the cost of the gate's own breakage from an unobserved security gap to an observed interruption.

## When this backfires

Fleet-deployed hooks with a network dependency are the clearest case against hardening. Timeouts count as failures, so one slow endpoint stalls every session at once. GitHub declines to make this case fail-closed at all, holding that "a slow or unreachable hook must not silently block tool calls or work, even when the hook was deployed by an administrator as policy" ([hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference#exit-codes-for-command-hooks)). A vendor is arguing against hardening its own hook system.

Some events ignore the field. `onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted` and `TeammateIdle`, nor on background command hooks that set `async` or `asyncRewake`, because "exit code 2 on these events sends Claude back to keep working, and Claude can't repair a hook that won't run" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)). Hardening a stop-class gate buys nothing and looks like it bought something.

Sometimes the hook was never the real control. Anthropic's own reference tells readers to use the permission system "rather than a hook to enforce a hard allow or deny" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#bash-if-matching)). Where a sandbox, a permission rule, or branch protection already blocks the outcome, a hardened hook adds interruptions and no coverage.

Neither mode catches a gate that answers wrongly without erroring. A hook handed a silently truncated input starts, finishes in time, and returns a well-formed allow, so no failure mode applies. [A guard hook approves the truncated input it was handed](../patterns/anti-patterns/guard-approves-truncated-input.md) covers that case.

A few failures block whatever you configure. Claude Code 2.1.288 changed `PreToolUse` and `PermissionRequest` matcher and serialization failures from skipped to blocked ([changelog](https://code.claude.com/docs/en/changelog#2-1-288)), and Cursor permission hooks block invalid JSON or invalid responses even with `failClosed: false` ([Cursor hooks](https://cursor.com/docs/agent/hooks#per-script-configuration-options)).

## Example

A Claude Code `PreToolUse` gate that blocks Bash when its own script will not run ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.js"],
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

Delete `check-command.js` and an `ls` call is refused rather than run. The documented error reads `failed; blocking because onFailure is "block"`, followed by node's own error output. Without the field, the same missing script is a non-blocking error and `ls` proceeds. In Cursor the equivalent is `"failClosed": true` on the hook definition.

## Key Takeaways

- Set the failure mode on each hook as you write it. Every one of the three harnesses lets some gate failures through unless you intervene, so an untouched default is a decision somebody has to defend.
- Audit for the inverse as well as the gap: in Claude Code a hook that exits 1 to warn becomes a blocker the day you harden it.
- Pair every fail-closed gate with a reason that names the fix. A stack trace is not one, and a block nobody can clear gets the hook deleted.
- Check whether your event supports the field before trusting it. In Claude Code the stop-class and background hooks ignore it.
- In the Agent SDK, check what each error handler returns. Returning no denial after a policy-check error bypasses that check.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — where a control is evaluated decides whether the agent can argue with it.
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — the same reasoning at startup scope, as one global setting rather than a per-hook field.
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — the layers beneath a hook that decide how much a fail-open window actually costs.
- [Distributing Security Controls Through the Agent Harness](harness-distributed-security-controls.md) — what happens to a control when it ships to a fleet in one install.
- [A Skill's Tool Grant Travels With Its Hooks](skill-tool-grant-travels-with-hooks.md) — what a policy should do to a tool grant when it stops that component's hooks from running at all.
