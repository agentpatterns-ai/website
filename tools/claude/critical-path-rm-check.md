---
title: "Claude Code Critical-Path rm Check for Unattended Runs"
description: "Claude Code asks before an rm aimed at root, home or the working folder and denies it where no one can answer. Which paths count, which modes deny, and what it misses."
tags:
  - claude
  - security
  - automation
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-22
status: current
---

# Claude Code Critical-Path rm Check for Unattended Runs

> Claude Code asks before an `rm` or `rmdir` aims at a critical path, and denies it where nobody can answer.

Claude Code treats the filesystem root, your home directory and your working directory as critical paths. An `rm` or `rmdir` that targets one gets a prompt or a denial, and no allow rule or `PreToolUse` hook that returns `"allow"` approves it ([permission modes](https://code.claude.com/docs/en/permission-modes#critical-paths)). Release 2.1.330 (November 20, 2026) "Changed more `rm` commands aimed at the root, home, a top-level folder or the working folder to ask for approval; where nobody can answer, they're refused" ([changelog](https://code.claude.com/docs/en/changelog#2-1-330)). The entry does not list the added commands, so this page follows the current permission modes reference.

## What counts as a critical path

Claude Code treats a target as critical when it is the filesystem root, a direct child of the root such as `/usr` or `/etc`, your home directory, or your working directory and its parents. Your additional working directories count only for a glob under them, such as `rm -rf <dir>/*` ([permission modes](https://code.claude.com/docs/en/permission-modes#which-paths-are-critical)).

The check also flags targets it cannot resolve in advance ([permission modes](https://code.claude.com/docs/en/permission-modes#other-targets-that-count-as-critical-paths)):

- A glob or trailing slash under a shell variable, such as `rm -rf "$DIR"/*`. An empty variable turns it into a removal from the root.
- A recursive `rm` whose target is only command substitution output, such as `rm -rf "$(pwd)"`.

## What happens when nobody can answer

The outcome depends on the permission mode ([permission modes](https://code.claude.com/docs/en/permission-modes#critical-path-removals-in-each-permission-mode)).

| Mode | Outcome |
|------|---------|
| `default`, `acceptEdits` | Asks you to approve it |
| `plan` | Asks you to approve it. If the classifier reviews commands during planning and no bypass permissions are available, it follows `auto` |
| `auto` | Asks in the terminal with a time limit. Elsewhere, denies it |
| `dontAsk` | Denies it |
| `bypassPermissions` | Asks in the terminal before a time limit runs out. Elsewhere, see below |

For a `-p` run or an Agent SDK session, `auto` denies the removal. In `bypassPermissions`, your `--permission-prompt-tool` or `canUseTool` callback decides. With neither, or under `--permission-prompts none`, Claude Code denies it unless a `PermissionRequest` hook allows it ([permission modes](https://code.claude.com/docs/en/permission-modes#time-limits-and-denials-in-auto-and-bypasspermissions-modes)).

In the terminal, the `auto` and `bypassPermissions` prompt counts down two minutes, then denies the command. After three unanswered prompts, Claude Code denies further removals at once. This applies from v2.1.281 ([permission modes](https://code.claude.com/docs/en/permission-modes#time-limits-and-denials-in-auto-and-bypasspermissions-modes)).

## How it layers with rules and hooks

- An explicit ask rule that matches the command asks you even in `auto` mode, with no time limit ([permission modes](https://code.claude.com/docs/en/permission-modes#critical-path-removals-in-each-permission-mode)).
- A deny rule that matches the command blocks it, though a mod you installed can still approve some of those calls. A deny rule matches command text, so `Bash(rm *)` stops `rm -rf build/` but not `/bin/rm -rf build/` ([permissions](https://code.claude.com/docs/en/permissions#what-a-bash-rule-doesnt-match)).
- A `PermissionRequest` hook can answer the prompt in modes that ask ([permission modes](https://code.claude.com/docs/en/permission-modes#critical-path-removals-in-each-permission-mode)).

## What the check does not cover

Anthropic states the limit: "The check can miss some commands, so it doesn't replace an operating-system control such as sandboxing" ([permission modes](https://code.claude.com/docs/en/permission-modes#critical-paths)). Three gaps follow:

- A command the check misses gets no special handling, so an allow rule, `bypassPermissions` or the sandbox's auto-allow mode can approve it with no prompt.
- The check applies to `rm` and `rmdir`. Other approved commands can delete critical paths too.
- Sandboxed commands can still delete your working directory.

Four environment variables weaken the check. `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS=1` (v2.1.311 or later) runs these removals with no prompt in `bypassPermissions` mode ([permission modes](https://code.claude.com/docs/en/permission-modes#turn-off-the-critical-path-removal-prompt-in-bypasspermissions-mode)). `CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT=1` hands `auto` mode's decision to the classifier in `-p` runs, instead of the denial ([permission modes](https://code.claude.com/docs/en/permission-modes#time-limits-and-denials-in-auto-and-bypasspermissions-modes)). `CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT=1` turns off the check on a target that is only command substitution output ([permission modes](https://code.claude.com/docs/en/permission-modes#other-targets-that-count-as-critical-paths)). `CLAUDE_CODE_DISABLE_INLINE_SHELL_RM_PROMPT=1` turns it off on a critical path typed directly in a `-c` script, such as `~` ([permission modes](https://code.claude.com/docs/en/permission-modes#removals-inside-nested-commands-and-inline-scripts)).

## Rewrite a flagged command

Since v2.1.277 the permission prompt names the flagged `rm` and suggests a `${VAR:?}` guard, "so headless runs can recover" ([changelog](https://code.claude.com/docs/en/changelog#2-1-277)). The reference gives four rewrites ([permission modes](https://code.claude.com/docs/en/permission-modes#rewrite-a-flagged-command)):

- A glob or trailing slash under `$DIR`: guard the expansion, as in `rm -rf "${DIR:?}"/*`, or use a literal path.
- A glob or trailing slash under a variable that is normally set, such as `$HOME`: use a literal path.
- A variable assigned from a directory-printing substitution, such as `D=$(pwd); rm -rf "$D"`: use a literal path. A `"${D:?}"` guard does not clear this check, because the variable is not empty.
- A target that is only command substitution output: run the substitution first, then remove the literal paths it prints.

## Test the guard before an unattended run

Use a throwaway directory or container, never a checkout you care about. Confirm that `claude --version` reports 2.1.330 or later ([changelog](https://code.claude.com/docs/en/changelog)). Then, with `CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT` and `CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT` unset, run a `-p` session in `auto` mode with `--output-format stream-json` and ask Claude to run `rm -rf "$(pwd)"`, an example from the reference. The table above predicts a denial. Denials appear as `permission_denied` system messages, and the final result message lists them in `permission_denials` ([headless guide](https://code.claude.com/docs/en/headless#turn-off-permission-prompts-in-unattended-runs)). The guide does not say whether a critical-path denial appears there, so read the whole output. If Claude declines before it tries the command, the run says nothing about the check.

## Key Takeaways

- The check covers `rm` and `rmdir` only, and it can miss commands.
- In a `-p` run, `auto` denies the removal. `bypassPermissions` denies it unless your permission host or a `PermissionRequest` hook decides.
- Pair the check with a sandbox. A deny rule matches command text, so `/bin/rm` slips past `Bash(rm *)`.
- Do not set `CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT`, `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS`, `CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT` or `CLAUDE_CODE_DISABLE_INLINE_SHELL_RM_PROMPT` on a scheduled run.

## Related

- [Deny-Fallback Permissions for Unattended Agent Runs](../../patterns/agent-design/deny-fallback-unattended-permissions.md)
- [Claude Code Auto Mode](auto-mode.md)
- [Bypass Permissions Overrides Your Allowlist](../../patterns/anti-patterns/bypass-permissions-overrides-allowlist.md)
- [Hard-Deny Classifier Rule](hard-deny-classifier-rule.md)
