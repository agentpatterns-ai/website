---
title: "A PermissionRequest Rewrite Can Move a Command Outside the Sandbox"
description: "Claude Code 2.1.328 runs a shell command that a PermissionRequest hook rewrote to a sandbox-excluded command outside the sandbox. Review rewrites as exits."
tags:
  - security
  - hooks
  - claude
aliases:
  - hook rewrite to an excluded command
  - updatedInput sandbox exclusion
  - PermissionRequest rewrite sandbox scope
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-20
maturity: emerging
status: current
---

# A PermissionRequest Rewrite Can Move a Command Outside the Sandbox

> A PermissionRequest rewrite that lands on an excluded command runs that command outside the sandbox, so the hook's rewrite rules set sandbox scope.

Claude Code 2.1.328 (November 19, 2026) lists one change on this path under Changed: "a shell command rewritten by a PermissionRequest hook to a sandbox-excluded command to run outside the sandbox" ([changelog 2.1.328](https://code.claude.com/docs/en/changelog#2-1-328)). The entry states no earlier behavior, so this page claims none.

## What the rewrite touches

A PermissionRequest hook that allows a call can return `updatedInput`. The field "Replaces the entire input object, so include unchanged fields alongside modified ones. The modified input is re-evaluated against deny and ask rules" ([hooks reference](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)). These hooks run "only when Claude Code is about to ask you for permission, or when it would otherwise auto-deny a call that can't prompt" ([hooks reference](https://code.claude.com/docs/en/hooks#permissionrequest-input)).

An `excludedCommands` entry takes a command out of the sandbox. Listing a pattern runs "matching commands outside the sandbox, which means no filesystem restrictions and no network proxy", and "An excluded command runs with your full access" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands)).

Matching reads call text. "Claude Code matches the text of the call: a script or make target that calls docker internally doesn't match, and neither does /usr/local/bin/docker." And "Every command in the call has to match: npm ci && docker compose build stays sandboxed unless another entry covers npm ci" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands)).

As of 2026-11-20, the sandboxing guide never mentions PermissionRequest and the hooks reference never mentions excluded commands. Only the changelog line joins them.

## Why the hook joins the boundary

The exclusion list decides sandbox membership from the text of a call. A hook that edits that text decides which side of the list a command lands on, so a review of the list alone misses the hook.

## Review the rewrite rules

1. List every command your hooks can return in `updatedInput.command`.
2. List the `excludedCommands` entries in effect. Under an admin-required sandbox, Claude Code "ignores entries from the repository's settings", so check which scope each entry comes from ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#commands-refused-with-sandbox-is-required)).
3. Mark each rewrite output that matches an entry under the matching rules above. Each mark is a sandbox exit.
4. For each exit, check whether the tool acts on a file Claude can write. The guide warns that if a pattern covers "an interpreter, a script inside your working directory, or a tool that acts on a file there, as docker compose does with its compose file, Claude can write that file and then run it outside the sandbox" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands)).
5. Narrow the hook output or the entry. "A narrower pattern leaves less that Claude can run outside the sandbox" (same section).

## Test that a rewrite stays inside

Use regular permissions mode, where "All Bash commands go through the regular permission flow, even when sandboxed" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#regular-permissions-mode)). A PermissionRequest hook runs only when Claude Code is about to ask for permission or would otherwise auto-deny the call, as quoted above, so a command that runs with no prompt never reaches it. This procedure has not been run against a live sandbox.

1. Add a test-only entry, `touch ~/sandbox-probe`, with no wildcard so it matches exactly.
2. Have the hook rewrite `mkdir probe-dir` to `touch ~/sandbox-probe`, then ask Claude to run `mkdir probe-dir`.
3. Check for `~/sandbox-probe`. The vendor's own sandbox probe says a sandboxed `touch ~/sandbox-probe` "Fails with Operation not permitted on macOS, or Read-only file system on Linux and WSL2" ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)). If the file appears and your home directory is not a sandbox write path, the rewrite ran outside the sandbox. Delete the file.
4. Remove the entry and repeat, declining any unsandboxed retry. The file should not appear.

A missing file proves nothing until the hook's log shows it fired.

## Example

A sandbox configuration with the guide's own exclusion example ([sandboxing guide](https://code.claude.com/docs/en/sandboxing#run-commands-outside-the-sandbox-with-excludedcommands)):

```json
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": ["docker compose *"]
  }
}
```

A PermissionRequest hook then prints this on exit 0, in the output shape the hooks reference documents ([hooks reference](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)). The command is illustrative.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "docker compose up -d"
      }
    }
  }
}
```

The rewritten text matches `docker compose *`. Per the 2.1.328 entry, the command runs outside the sandbox. The guide warns that for a pattern like this one, Claude can write the compose file and then run it outside the sandbox.

## When this backfires

- No entry matches. A hook that rewrites only to commands outside `excludedCommands`, or a setup with no entries, has no exits, and the review finds nothing.
- The entry was already a trust decision. If every rewrite target is a command the operator accepted as excluded, the hook adds no command the operator had not named.
- The rewrite is a script or a compound call. A `make` target that calls docker, an absolute path, or a chain with one unmatched command stays sandboxed under the matching rules above.
- The hook never fires. Claude Code "doesn't run PermissionRequest hooks for a sandboxed command's network request" ([hooks reference](https://code.claude.com/docs/en/hooks#permissionrequest)). Tightening a hook does nothing for paths it does not see.
- The evidence is one changelog line, and no page states the behavior before it. Re-run the probe after each upgrade.

## Key Takeaways

- A PermissionRequest rewrite that matches an `excludedCommands` entry runs outside the sandbox, per the 2.1.328 changelog entry.
- Review the hook's outputs against the exclusion list together. Each match is a sandbox exit.
- Test with a probe in regular permissions mode, and confirm the hook fired before you read a missing file as safe.
- The docs state no behavior before 2.1.328, so do not rely on the old path either way.

## Related

- [Fall Back to the No-Hook Decision When a Permission Check Errors](hook-allow-failed-permission-check.md) — the 2.1.323 rule for a call whose permission check errors after a PreToolUse hook allowed it.
- [Fail Closed When the Sandbox Cannot Start](fail-closed-sandbox-startup.md) — what excluded commands do when the sandbox is down.
- [Sandbox Capability Opt-In as a Compatibility Setting](../patterns/anti-patterns/sandbox-capability-opt-in-as-compatibility-setting.md) — the per-tool exclusion route and its cost.
- [Parser-Versus-Shell Evasion in Command Permission Checks](parser-versus-shell-permission-evasion.md) — why a rule that reads command text leaves gaps.
- [Scope Demotion for Repository-Committed Settings](repo-committed-settings-scope-demotion.md) — which scope may add `excludedCommands` entries.
- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](per-hook-failure-mode.md) — what a hook decides when it breaks.
