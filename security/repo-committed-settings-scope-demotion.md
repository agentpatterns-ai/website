---
title: "Scope Demotion for Repository-Committed Settings"
term: "Scope Demotion"
description: "A repository's settings file may not widen a session. Capability-enabling and limit-relaxing keys are honored only from shell, user, or managed scope, and the settings reference publishes the answer per key."
tags:
  - security
  - claude
  - agent-design
  - instructions
aliases:
  - repository-committed settings scope
  - capability-enabling settings keys
  - project scope settings demotion
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-11
status: current
maturity: adopted
---

# Scope Demotion for Repository-Committed Settings

> A settings key that grants a capability is honored only from shell, user, or managed scope, not from a repository's committed file.

Claude Code resolves a settings key by direction as well as by scope. A value in `.claude/settings.json` that restricts the session can apply, sometimes over managed settings. A value in the same file that grants a capability or relaxes a limit is dropped. The rule is dependable for that capability and limit-relaxing class. Each key's reference entry states the answer, so read its Scope field rather than deduce one from the precedence stack.

## Where the rule applies

The settings reference gives the condition in one sentence: "Project and local settings can't set variables that a checked-out repository shouldn't control; set those in your shell, user settings, or managed settings instead" ([ignored `env` variables](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env)).

Each key's entry carries a Scope field naming the files it can go in. Tallying that field across the reference gives 155 of 243 keys at `Any file` and 27 at `User or managed` ([settings reference](https://code.claude.com/docs/en/settings-reference)). The second group holds `autoMode`, `skipAutoPermissionPrompt`, `processWrapper`, eight `sandbox.*` keys, and `appendPlugins`, `prependPlugins`, and `pluginConfigs`.

The demotions landed one entry at a time across six releases:

| Release | What a repository-committed file can no longer do |
|---|---|
| [2.1.222](https://code.claude.com/docs/en/changelog#2-1-222), Aug 4 | Turn on Remote Control auto-start. It can still turn it off. |
| [2.1.232](https://code.claude.com/docs/en/changelog#2-1-232), Aug 13 | Override `sandbox.ripgrep`, the binary the sandbox runs for search |
| [2.1.257](https://code.claude.com/docs/en/changelog#2-1-257), Sep 1 | Set `permissions.defaultMode` to `bypassPermissions`, already ignored for `auto` |
| [2.1.282](https://code.claude.com/docs/en/changelog#2-1-282), Sep 24 | Add `sandbox.excludedCommands` entries under managed `allowUnsandboxedCommands: false` |
| 2.1.282 | Set the OpenTelemetry variables that turn export on, choose its endpoint, or capture content |
| [2.1.285](https://code.claude.com/docs/en/changelog#2-1-285), Sep 29 | Set `ALLUSERSPROFILE`, `SystemDrive`, or `CommonProgramFiles` on Windows |
| [2.1.290](https://code.claude.com/docs/en/changelog#2-1-290), Oct 5 | Turn on Claude in Chrome |
| 2.1.290 | Set `CLAUDE_CODE_DISABLE_ATTACHMENTS`, in either direction |

Release 2.1.282 carried the rule a layer down as well. On Windows and WSL, an admin policy "that is present but invalid or unreadable (HKLM, `managed-settings.json`) keeps user-writable HKCU and WSL `/etc/claude-code` from applying" ([2.1.282](https://code.claude.com/docs/en/changelog#2-1-282)). A broken policy blocks the scopes below it instead of falling through to them.

An ignored telemetry variable is reported rather than dropped silently. That release also added "a startup notice, and `/status` and `claude doctor` entries, listing telemetry variables in a project's settings files that were ignored or that turned telemetry off" ([2.1.282](https://code.claude.com/docs/en/changelog#2-1-282)).

## Why it works

A repository-committed settings file arrives by the same route as the code, through a clone or a pull request. Nothing reviews it between the commit and the behavior change. Claude Code "watches your settings files and reloads them when they change, so it applies most edits to the running session without a restart" ([when edits take effect](https://code.claude.com/docs/en/settings#when-edits-take-effect)), so a pulled branch reaches a session already in progress. The check sits in the config loader rather than in the model's context, which is why it holds where prose in the same file does not (see [Enforced Versus Advisory Controls](enforced-versus-advisory-controls.md)).

Direction decides the outcome because a value that only narrows a session gives an attacker nothing. Claude Code honors that half from scopes that otherwise lose: "For a few keys whose values restrict a session, Claude Code honors a restrictive value from a scope that otherwise couldn't override managed settings" ([settings precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)). `remoteControlAtStartup` carries both halves in one row. A `false` in `.claude/settings.json` is "Honored even when a managed source sets `true`; a project or local `true` is ignored". Same key, same file, opposite answers.

## Where the split is not clean

Not every demoted key grants anything. `spellcheck`, `vimInsertModeRemaps`, `bashEditDiffEnabled`, and `desktopSessionCleanupPeriodDays` sit at `User or managed` alongside the sandbox keys, and none of them widens a limit. `CLAUDE_CODE_DISABLE_ATTACHMENTS` left project scope in both directions although setting it restricts the session. For `useAutoModeDuringPlan`, `syncClaudeAiSkills`, and `syncClaudeAiPlugins`, the exceptions table honors `false` from `.claude/settings.local.json` and records that "a `false` in `.claude/settings.json` is ignored" ([settings precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)). A restrictive project value loses for those three.

The `env` group is also coarser than the boundary it defends. It drops a variable from `.claude/settings.local.json`, a file that the docs describe this way: Claude Code "keeps it out of git when it creates the file" ([settings files](https://code.claude.com/docs/en/settings#settings-files-and-who-they-affect)), so moving a demoted key there does not get it back.

## When this backfires

- Headless runs lose the audit surface. "A non-interactive run with `-p` or an Agent SDK session shows no notice, so check that your collector still receives data after you upgrade" ([settings reference](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env)). A CI job whose repository settings enabled export stops reporting with nothing saying so.
- A shared exemption stops being recordable in the repository. A build step that needs an unsandboxed command now depends on each developer's user settings or a `--settings` file.
- A private repository with one maintainer pays the cost for a threat it does not have. The demotion assumes a contributor who can edit the committed file.
- The demoted set grows release by release, so a key that works from a project file today may stop on the next upgrade. The table above lists eight changes across six releases between 4 August and 5 October 2026.

Per-key classification is not the only shipped answer. Codex gates the whole layer on one trust decision: project config files apply to "trusted projects only", and "If you mark a project as untrusted, Codex skips project-scoped `.codex/` layers, including project-local config, hooks, and rules" ([Codex config basics](https://developers.openai.com/codex/config-basic)). That needs no per-key list, at the price of handing the whole layer back on a yes. Neither control reaches the prose in `AGENTS.md` or `.cursorrules`, which stays an injection surface of its own ([Rule-File Package Substitution](rule-file-package-substitution.md)).

## Example

**Before** — a repository-committed `.claude/settings.json` that enables export:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel-collector.example.com:4317"
  }
}
```

From 2.1.282 all three are dropped, and `claude doctor` lists them by name.

**After** — the enabling half moves to the job environment or `~/.claude/settings.json`, and the committed file keeps only the values that narrow what leaves the machine:

```json
{
  "env": {
    "OTEL_LOG_USER_PROMPTS": "0",
    "OTEL_LOG_TOOL_CONTENT": "0"
  }
}
```

Those two still apply from project scope, "because they turn something off" ([settings reference](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env)).

## Key Takeaways

- Run `claude doctor` after an upgrade to list the telemetry variables your project file set that Claude Code ignored. The names appear there; the values never do.
- Put the enabling half of a pair in the job environment and leave the narrowing half committed. An `OTEL_LOG_*` off value still applies from project scope when the endpoint beside it does not.
- A `-p` or SDK pipeline gets no startup notice, so confirm a collector still receives data rather than assuming the settings file carried over.
- When a key's Scope field disagrees with the direction rule, the field is the answer. Some demoted keys grant nothing, and three ignore a restrictive project value.

## Related

- [A Containment Floor for Agent Self-Configuration](agent-self-config-field-classes.md) — the grant-versus-limit field split applied to config an agent writes about itself
- [Rule-File Package Substitution](rule-file-package-substitution.md) — the prose half of the same repository-committed file
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — why a loader check holds where a rules file loses to the task
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — the startup half of the same question, when policy has not yet arrived
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — varying agent config inside an admin-owned ceiling rather than below it
