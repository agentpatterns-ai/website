---
title: "Refuse a Skill's Inline Shell Commands by Source with PreSkillShellCommand"
term: "PreSkillShellCommand Hook"
description: "Claude Code 2.1.332 adds a hook that can block a skill's injected shell commands as it loads. Key the policy on the skill's source, fail closed, and pin the version."
tags:
  - security
  - claude
  - hooks
  - skills
aliases:
  - PreSkillShellCommand
  - hook for injected skill commands
  - per-source skill shell gate
last_reviewed: 2026-11-25
maturity: emerging
---

# Refuse a Skill's Inline Shell Commands by Source with PreSkillShellCommand

> Since 2.1.332, a Claude Code `PreSkillShellCommand` hook can block a skill's injected shell commands one by one, if it fails closed and clients are current.

A skill can embed shell commands that run as it loads, and `PreToolUse` hooks don't fire for them. Claude Code 2.1.332 (November 25, 2026) added "a `PreSkillShellCommand` hook event that can refuse a skill or command's inline shell commands as it loads" ([changelog 2.1.332](https://code.claude.com/docs/en/changelog#2-1-332)). The hook gives per-command control only when four conditions hold:

1. Every client runs 2.1.332 or later. Earlier versions "run injected commands without calling it" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand)).
2. The hook sets `onFailure: "block"`. Without it, a hook that crashes or times out lets the command run ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand-decision-control)).
3. The hook lives in a settings file or a plugin, not in the skill's own frontmatter.
4. The same check also runs on `PreToolUse`, because auto mode turns some injected commands into ordinary tool calls.

## What the hook sees

An injected command is a line written as `` !`<command>` `` or a ```` ```! ```` block in a skill or command file. The hook runs before each one, and "PreToolUse hooks don't fire for injected commands" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand)). Its input adds these fields to the common ones ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand-input)):

| Field | Value |
|---|---|
| `tool_name` | `Bash` or `PowerShell`, the tool that runs the command |
| `tool_input.command` | The shell command as it would run |
| `command_name` | The loading skill, such as `pr-summary` or `my-plugin:deploy` |
| `command_source` | Where the skill comes from, such as `userSettings`, `projectSettings`, `policySettings`, `plugin`, or `builtin` |
| `invoked_by` | `user`, `claude`, or `other` |

`command_source` and `command_name` are what the hook adds. A permission rule is a tool-and-pattern string such as `"Bash(git *)"` ([Claude Code hooks](https://code.claude.com/docs/en/hooks)), and that syntax has no field for the skill that wrote the command.

## What a refusal does

The hook can say no and nothing else. "You can block a command from this hook, but you can't approve or change one" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand-decision-control)).

| Hook output | Result |
|---|---|
| Exit 0 with no decision, or `permissionDecision: "allow"` | The command runs unless another hook blocks it |
| Exit 2, `permissionDecision: "deny"`, or `decision: "block"` | The command does not run. The skill loads, and Claude reads `[not run: blocked by hook: <reason>]` in place of the output |
| `"ask"`, `"defer"`, or any `updatedInput` | Blocked the same way as `"deny"` |
| `continue: false` | The whole invocation fails, and none of its injected commands runs |
| The hook fails or times out | The command runs, unless the hook sets `onFailure: "block"` |

The last row is the trap. A policy hook with a mistyped path lets every command through. When you type the skill's name, a `Ran anyway in /<name>` line "reports a command that ran after its hook failed or timed out" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand-decision-control)).

## Where it sits among the other controls

Claude Code checks injected commands against your permission rules first. A command a deny rule matches "aborts the invocation" ([Claude Code skills](https://code.claude.com/docs/en/skills#permission-checks-on-injected-commands)). The hook "runs after the permission check on injected commands, so it gets the commands that passed", and it still runs in `bypassPermissions` mode ([Claude Code hooks](https://code.claude.com/docs/en/hooks#commands-that-reach-a-preskillshellcommand-hook)).

| Control | Scope | What it decides on |
|---|---|---|
| Permission rules | Every injected command | Command text. A deny aborts the whole skill |
| `PreSkillShellCommand` | Commands that passed the rules | Command text plus skill name, source, and invoker. A block drops one command |
| [`disableSkillShellExecution`](skill-shell-execution-gate.md) | User, project, plugin, and additional-directory skills | Nothing. Every command in scope becomes `[shell command execution disabled by policy]` ([Claude Code skills](https://code.claude.com/docs/en/skills#inject-dynamic-context)) |
| `PreToolUse` | Claude's own tool calls | Command text. Never sees injected commands |

Auto mode opens a gap between the hook and `PreToolUse`. There, a command that needs approval does not run as the skill loads. "Claude can run it afterward as a tool call, which fires `PreToolUse` and not this event, so keep your script on both events" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#commands-that-reach-a-preskillshellcommand-hook)). The hooks reference lists `command_source` as an input for `PreSkillShellCommand` and `UserPromptExpansion`, not for `PreToolUse`. A source-keyed policy therefore cannot follow a deferred command, and the `PreToolUse` copy has to judge the command text alone.

## Why it works

Without the hook, the documented controls on injected commands are permission rules, which match tool-and-command patterns, and `disableSkillShellExecution`, which turns off every command in scope. The hook moves the decision to the one point where Claude Code knows both what will run and which skill asked for it. A policy can then trust skills from managed settings and refuse the same command from a project or plugin skill. Blocking costs little, because the skill still loads with a marker in place of the output ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand-decision-control)). Claude sees that the command was refused, and the rest of the skill still loads.

Keying on the source also avoids the weakness of text matching. A blocklist on command text misses any spelling its author did not foresee, which [parser-versus-shell evasion](parser-versus-shell-permission-evasion.md) documents for permission rules. A source check asks a question the command text cannot answer.

## Roll it out across a fleet

Order matters, because the hook and an old client do not mix. If a settings file names the event first, "an earlier version such as v2.1.331 opens each interactive terminal session with a warning dialog" that reads `Unknown hook event "PreSkillShellCommand" was ignored` ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand)). That client then runs every injected command without calling the hook.

1. Upgrade every client to 2.1.332 or later.
2. Set `requiredMinimumVersion` to `2.1.332` in managed settings. Below that floor, "Claude Code exits at startup and tells the user to update" ([settings reference](https://code.claude.com/docs/en/settings-reference#requiredminimumversion)). The key works only in managed settings, and Claude Code "gives no warning when it ignores the key elsewhere". The key itself requires Claude Code 2.1.163 or later, so it cannot stop a client older than 2.1.163.
3. Add the hook in managed settings or a plugin. A skill's injected commands run without the hooks in its own frontmatter "on its first load in a session and on loads inside a subagent" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand)).
4. Test it with a one-line skill. The hooks reference suggests `.claude/skills/hook-test/SKILL.md` containing `` !`echo 'rm -rf'` ``, which deletes nothing. Typing `/hook-test` should print a `Not run in /hook-test` line.

The version check "runs at startup only, so a session that's already running continues" ([settings reference](https://code.claude.com/docs/en/settings-reference#requiredminimumversion)). A session already running on an old client keeps running injected commands without the hook until it restarts.

## Example

This policy refuses injected commands from project and plugin skills and lets managed, built-in, and personal skills run theirs. It is a sample built on the documented input fields and exit codes, not a vetted policy, so adjust the trusted list to your own sources. Save it at an absolute path that neither users nor the repository under work can write, such as `/etc/claude-code/hooks/skill-shell-policy.sh`. A copy under `${CLAUDE_PROJECT_DIR}`, "the project root where the session started" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#reference-scripts-by-path)), comes from the repository the policy distrusts, which can replace it with a script that exits 0:

```bash
#!/usr/bin/env bash
# PreSkillShellCommand: refuse injected commands from untrusted skill sources.
input=$(cat)
src=$(jq -r '.command_source // empty' <<<"$input")
name=$(jq -r '.command_name // empty' <<<"$input")

case "$src" in
  policySettings|builtin|userSettings) exit 0 ;;
esac

echo "Injected command from $src skill '$name' refused by policy" >&2
exit 2
```

An empty or unknown source falls through to the refusal, so a missing field blocks instead of allowing. Make the script executable, for example with `sudo chmod 755 /etc/claude-code/hooks/skill-shell-policy.sh`. With `args` set, Claude Code spawns `command` directly as an executable ([Claude Code hooks](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form)), so a script without the execute bit cannot start. With `onFailure: "block"`, that failure blocks every injected command, trusted sources included ([Claude Code hooks](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)). Register the script in managed settings with the matcher, type, and failure setting the hooks reference prescribes ([Claude Code hooks](https://code.claude.com/docs/en/hooks#preskillshellcommand)):

```json
{
  "hooks": {
    "PreSkillShellCommand": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "command": "/etc/claude-code/hooks/skill-shell-policy.sh",
            "args": [],
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

`Bash|PowerShell` covers both tools that can run injected commands. The hook must not be `async`, because an async hook cannot block. Claude Code cannot run a `prompt` or `agent` hook on this event, and it blocks every command such a hook matches. To allow one vetted plugin skill, add a line above the `case` that checks the source and the `command_name` together, such as `[ "$src" = plugin ] && [ "$name" = my-plugin:deploy ] && exit 0`. A branch inside the existing `case` cannot match, because that `case` tests the source, not the name.

## When this backfires

- A mixed fleet with no version floor. Clients on 2.1.331 or older run every injected command without calling the hook, and their interactive terminal sessions open with a warning dialog, so the policy holds on some machines and not others.
- A hook without `onFailure: "block"`. A wrong script path, a crash, or a timeout lets the command run. A missing `jq` has the opposite effect. The sample reads an empty source, falls through to exit 2, and blocks every command, trusted sources included.
- Auto mode sessions. Deferred commands come back as Claude's tool calls, which `PreToolUse` sees without a `command_source`, so the source policy does not apply to them.
- Teams with no third-party skills. If every skill is written in-house, the hook adds a script to maintain and changes nothing. Where no skill needs live context, [`disableSkillShellExecution`](skill-shell-execution-gate.md) in managed settings is simpler. It has no script to crash, and Claude Code has shipped it since 2.1.91 ([changelog 2.1.91](https://code.claude.com/docs/en/changelog#2-1-91)).
- Trusting `userSettings` by default. The sample trusts every skill that reports that source. Drop that branch where users install skills they have not read.

## Key Takeaways

- `PreSkillShellCommand`, added in 2.1.332, runs before each of a skill's injected commands. `PreToolUse` hooks don't fire for them.
- It can only block. A block drops one command and the skill still loads; `continue: false` stops the whole invocation.
- Decide on `command_source` and `command_name`, which a permission rule on the command text cannot see, and refuse when the source is missing.
- Set `onFailure: "block"`, define the hook in managed settings or a plugin, and keep a text-based check on `PreToolUse` for auto mode.
- Upgrade first, then set `requiredMinimumVersion` to 2.1.332, then ship the hook.

## Related

- [Skill Shell Execution Gate: Disabling Inline Shell from Skills](skill-shell-execution-gate.md) — the all-or-nothing switch this hook refines.
- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](per-hook-failure-mode.md) — why a policy hook should fail closed.
- [Parser-Versus-Shell Evasion in Command Permission Checks](parser-versus-shell-permission-evasion.md) — the text-matching weakness a source check avoids.
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the threat that makes a skill's source worth checking.
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md) — deterministic gates against model guidance.
