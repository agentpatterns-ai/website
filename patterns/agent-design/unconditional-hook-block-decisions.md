---
title: "Hook Block Decisions Hold in More Cases Since Claude Code 2.1.326"
term: "Unconditional hook block decision"
description: "Claude Code 2.1.326 honors a hook's decision: block in more cases without listing them. Find hooks that print a block on allow paths and test them before upgrading."
tags:
  - technique
  - agent-design
  - hooks
  - claude
aliases:
  - always-block hook
  - hook block decision audit
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-21
maturity: emerging
status: current
---

# Hook Block Decisions Hold in More Cases Since Claude Code 2.1.326

> Claude Code 2.1.326 makes a hook's block decision hold in more cases. The changelog does not list them, so audit every hook that prints one.

Claude Code 2.1.326 (November 16, 2026) "Changed a hook’s `"decision": "block"` to hold in more cases, so a hook that always prints one may start blocking calls" ([changelog 2.1.326](https://code.claude.com/docs/en/changelog#2-1-326)). The entry names no cases, so you cannot check whether your hook falls in one. Treat every block your hook prints as live, and make it print one only when it means to refuse.

## What a block does on each event

`"block"` is the only value `decision` takes. The [hooks reference](https://code.claude.com/docs/en/hooks#decision-control) says: "To allow the action to proceed, omit `decision` from your JSON, or exit 0 without any JSON at all". A hook that prints `{"decision": "block"}` on its allow path asks Claude Code to block.

What that costs depends on the event:

| Event | Effect of `"block"`, per the [hooks reference](https://code.claude.com/docs/en/hooks) |
|---|---|
| `UserPromptSubmit` | "rejects the prompt" |
| `PostToolUse` | "adds the `reason` next to the tool result". The tool has already run. |
| `Stop` | "prevents Claude from stopping". After eight consecutive continuations the cap overrides the next block; the count resets when Claude calls a tool |
| `PreToolUse` | Top-level `decision` is deprecated, and `"block"` maps to `"deny"` |

An old-format `PreToolUse` hook still gates tool calls. The reference says the deprecated values "`"approve"` and `"block"` map to `"allow"` and `"deny"` respectively" ([hooks reference](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)).

A printed block has gone unhonored before. The reference records that "Claude Code ignored a top-level `decision` from `Elicitation` and `ElicitationResult` hooks from v2.1.105 until the fix in v2.1.284" ([hooks reference](https://code.claude.com/docs/en/hooks#other-ways-to-decline-an-elicitation)).

## Find and fix the hooks

1. List the hooks that run. The hooks guide says to "Run `/hooks` and confirm the hook appears under the correct event", and warns that `/hooks` "doesn’t list hooks from a skill that hasn’t been invoked in the session" ([hooks guide](https://code.claude.com/docs/en/hooks-guide#hook-not-firing)). Invoke those skills first, then run `/hooks` again.
2. In each script, find every place it prints `decision`. Check that each print sits inside a branch that runs only when the hook means to refuse.
3. On the allow path, exit 0 and print nothing, or print JSON without `decision`. Build the JSON "with a JSON encoder such as `jq` instead of string concatenation" ([hooks guide](https://code.claude.com/docs/en/hooks-guide#hook-error-in-output)).
4. Move `PreToolUse` hooks to `hookSpecificOutput.permissionDecision`, which the reference says to use instead.

## Test before you upgrade

The hooks guide gives a manual test: pipe sample JSON to the script and check its exit code ([hooks guide](https://code.claude.com/docs/en/hooks-guide#hook-error-in-output)). Run it on inputs the hook should allow:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
echo $?
```

If stdout carries `"decision": "block"` for an input the hook should allow, the hook blocks unconditionally on that path. After the upgrade, start Claude Code with `claude --debug-file <path>`, which writes hook execution details to that file ([hooks reference](https://code.claude.com/docs/en/hooks#debug-hooks)), and look for blocks you did not expect.

## Why it works

On exit 0, Claude Code applies the JSON output fields a hook prints ([hooks reference](https://code.claude.com/docs/en/hooks#exit-code-output)), and the documented way to allow is to omit `decision` ([hooks reference](https://code.claude.com/docs/en/hooks#decision-control)). A hook that never prints a block on an allow path has nothing for a newly honored case to act on. The audit removes the need to know which cases 2.1.326 covers.

## When this backfires

- A hook meant to refuse every call its matcher catches gets flagged for nothing. Leave it alone.
- Async hooks gain nothing from the audit. The reference says "Async hooks can’t block or control Claude’s behavior" ([hooks reference](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background)).
- A text search for `"block"` misses JSON built from a template or in another language. Read the code path as well as the string.
- A `Stop` hook that always blocks shows up as extra continuations, not as a refused call, so it is easy to miss in a short test.

## Key Takeaways

- The 2.1.326 entry does not list its cases, so an audit cannot target them.
- Print `decision` only inside the branch that refuses. To allow, omit it and exit 0.
- Old-format `PreToolUse` hooks still deny on `"block"`. Move them to `permissionDecision`.
- Pipe allow inputs through each hook and check stdout before you upgrade.

## Related

- [Hooks and Lifecycle Events: Intercepting Agent Behavior](../../tool-engineering/hooks-lifecycle-events.md)
- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](../../security/per-hook-failure-mode.md)
- [PostToolUse continueOnBlock: Refusal With a Load-Bearing Reason](../../tool-engineering/posttooluse-continue-on-block.md)
- [PostToolUse Hooks After an Interrupted Turn in Claude Code](posttooluse-hooks-after-interrupt.md)
- [Per-Surface Hook Matchers for Shell-Starting Tools](shell-surface-hook-matcher-coverage.md)
