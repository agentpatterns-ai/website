---
title: "Claude Code /status Diagnostics for Broken and Ignored Config"
description: "From Claude Code 2.1.327, /status lists broken agent, skill, command, and output style files, plus keybinding, sandbox, permission, and hook-matcher faults."
tags:
  - claude
  - agent-design
  - workflows
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-23
status: current
---

# Claude Code /status Diagnostics for Broken and Ignored Config

> From Claude Code 2.1.327, `/status` lists broken agent, skill, command and output style files, keybinding errors, an unavailable sandbox, ignored permission settings and hook matchers that never match.

Claude Code 2.1.327 (November 17, 2026) "added a list in `/status` of broken agent, skill, command and output style files, keybinding errors, an unavailable sandbox, ignored permission settings and hook matchers that never match" ([changelog](https://code.claude.com/docs/en/changelog)). The docs describe two of these faults as silent and two as a warning in the debug log. The commands page, as fetched on November 23, 2026, describes `/status` as showing "version, model, account, and connectivity" and does not mention the list ([commands](https://code.claude.com/docs/en/commands.md)). The changelog line is the only source for the list itself.

## What the list covers

The changelog names eight kinds of fault. The table pairs each with the way the official docs say it fails when nothing reports it.

| Fault in the entry | How the docs describe the failure | Source |
|---|---|---|
| Broken skill file | If the frontmatter YAML does not parse, the skill loads with empty metadata. `/skill-name` still works, but Claude cannot match the skill's description. | [Skills](https://code.claude.com/docs/en/skills.md#skill-not-triggering) |
| Broken output style file | "A misspelled field is ignored without an error." If the YAML does not parse, the style loads under its file name with no fields set. | [Output styles](https://code.claude.com/docs/en/output-styles.md) |
| Keybinding error | A misspelled modifier such as `ctl+k` makes Claude Code ignore the whole binding. Validation writes a warning to the debug log. | [Keybindings](https://code.claude.com/docs/en/keybindings.md#validation) |
| Unavailable sandbox | By default, when the platform does not support the sandbox or the startup dependency check fails, "Claude Code runs commands without sandboxing". Setting `sandbox.failIfUnavailable` to `true` makes it exit at startup instead. | [Sandboxing](https://code.claude.com/docs/en/sandboxing.md) |
| Hook matcher that never matches | "A misspelled tool name produces a matcher that matches nothing, so the hook fails silently." Matching is case-sensitive, and tool names are capitalized, so `"bash"` does not match `Bash`. Before v2.1.191 a comma-separated matcher such as `"Edit,Write"` matched nothing. | [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md#check-hooks) |
| Broken agent file | The sources I fetched name one case. If two files in the same `.claude/agents/` directory share a name, Claude Code loads only one of them. The docs name `/doctor` for that case, not `/status`. | [Sub-agents](https://code.claude.com/docs/en/sub-agents.md) |
| Broken command file, ignored permission setting | This page cites no source for how a broken command file fails. The entry does not say which permission settings count as ignored. | [Changelog](https://code.claude.com/docs/en/changelog) |

The permission row stays open, but the docs name two cases that fit the wording. With `allowManagedPermissionRulesOnly` set (v2.1.282 or later), `/status` lists each skill whose `allowed-tools` Claude Code has ignored in the session ([Skills](https://code.claude.com/docs/en/skills.md#when-only-managed-permission-rules-apply)). A `mcp__` permission rule written with parentheses is skipped on load, and Claude Code lists it in the invalid-settings dialog and in `claude doctor` ([Permissions](https://code.claude.com/docs/en/permissions.md)). The changelog does not say whether either case is in the 2.1.327 list.

## Matcher faults and the /hooks view

`/hooks` lists every hook registered for the session. A hook missing from that list was not loaded. A hook that appears there but does not fire usually has a matcher problem ([Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md#check-hooks)). The second case fits the entry's phrase "hook matchers that never match". That reading is my inference. The entry does not say which matcher faults it detects, so test a deliberately misspelled matcher before you rely on the list to catch yours.

One matcher fault is silent by design. A `matcher` field on an event that does not support matchers "is silently ignored" ([Hooks reference](https://code.claude.com/docs/en/hooks.md)). The entry does not say whether `/status` reports it.

## Earlier moves from startup warnings to /doctor and /status

The change continues a move from startup warnings to on-demand views.

- 2.1.183 (June 19, 2026) removed the startup "setup issues" line under the logo. The entry says to run `/doctor` to see configuration issues, or to use `--debug` ([changelog](https://code.claude.com/docs/en/changelog)).
- 2.1.203 (July 7, 2026) removed the startup "claude command missing or broken" warnings. They "now appear in `/doctor` and `/status` instead" ([changelog](https://code.claude.com/docs/en/changelog)).
- 2.1.327 added the list to `/status`.

The changelog does not say the new list also appears at startup. Treat it as a view you open, not an alert that finds you.

## Which command answers which question

| Question | Command | Source |
|---|---|---|
| Is a file loaded, and from where? | `/context`, `/skills`, `/hooks`, `/permissions` | [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md#see-what-loaded-into-context) |
| Which settings sources are active? | `/status` | [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md#see-what-loaded-into-context) |
| What is broken in the setup, with proposed fixes? | `/doctor` in a session. It reports findings first and asks before it changes anything. | [Skills](https://code.claude.com/docs/en/skills.md) |
| Which settings files are invalid, without starting a session? | `claude doctor` in the shell. It prints read-only diagnostics. | [Debug your configuration](https://code.claude.com/docs/en/debug-your-config.md#check-resolved-settings) |
| Why did a keybinding or a frontmatter field not apply? | `claude --debug`, then read the log. | [Keybindings](https://code.claude.com/docs/en/keybindings.md#validation) |
| Which `SKILL.md` files have frontmatter that does not parse? | `claude plugin validate .claude/skills` (v2.1.233 or later). | [Skills](https://code.claude.com/docs/en/skills.md#skill-not-triggering) |

`/status` runs at once even while Claude is responding, so you can open it mid-turn without queuing it ([commands](https://code.claude.com/docs/en/commands.md)).

## Build the same check for your own harness

This section is inference from the sources above, not a documented Claude Code workflow.

The built-in list covers the file classes the entry names. A team's harness has faults it cannot know about: a skill that must carry a team field, a hook matcher that must name a tool your harness has, a convention for agent names. Two layers fit.

1. Run `claude plugin validate .claude/skills` in CI. It finds `SKILL.md` files whose frontmatter does not parse, which is the fault that otherwise loads with empty metadata.
2. Add a script for the faults specific to your repo. Read each hook's `matcher` from `settings.json` and compare it to the tool names your harness exposes. Fail the build when a name matches nothing. A matcher that matches nothing is the silent failure the docs describe.

Keep the CI check separate from `/status`. `/status` reports on one machine's loaded session. A CI check reports on what a commit would load, and it runs before anyone starts a session.

## When this backfires

- A clean list is not a clean bill. The list covers the classes the entry names. A skill with a vague description, a conflicting instruction, or a hook that fires but does the wrong thing does not appear on it (inference from the entry's scope).
- The list shows one machine and one version. A teammate on a release before 2.1.327 has no list, and a repo-committed fault shows only on a machine where someone runs `/status` (inference).
- The entry does not say which sessions show the list. It does not mention headless `claude -p` runs. Nobody is there to open `/status` in one (inference). Unattended runs need the shell command `claude doctor` or a CI check instead.
- The sandbox entry reports a fault but does not stop it. By default a session with an unavailable sandbox keeps running commands without one. Only `sandbox.failIfUnavailable` set to `true` stops the session ([Sandboxing](https://code.claude.com/docs/en/sandboxing.md)).

## Key Takeaways

- From 2.1.327, `/status` lists broken agent, skill, command, and output style files, keybinding errors, an unavailable sandbox, ignored permission settings, and hook matchers that never match.
- The changelog is the only source for the list. The commands page, as fetched on November 23, 2026, does not mention it.
- The entry does not say which matcher faults or which permission settings it detects. Test a deliberate fault before you rely on it.
- The list is on demand. The startup "setup issues" line moved to `/doctor` in 2.1.183, and the "claude command missing or broken" warnings moved to `/doctor` and `/status` in 2.1.203. The changelog does not say the new list also appears at startup.
- For unattended runs and for faults specific to your repo, add a CI check such as `claude plugin validate .claude/skills`. That pairing is inference, not documented workflow.

## Related

- [Harness Preflight Doctor Command for Agent Diagnostics](../../observability/harness-preflight-doctor-command.md)
- [Policy File Validation](../../instructions/policy-file-validation.md)
- [Agent Debugging](../../observability/agent-debugging.md)
- [Claude Code Hooks Lifecycle](hooks-lifecycle.md)
- [Claude Code Sub-Agents for Delegating Complex Tasks](sub-agents.md)
