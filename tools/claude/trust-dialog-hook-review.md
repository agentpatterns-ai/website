---
title: "Claude Code Trust Dialog: Review Hooks Before You Accept"
description: "From v2.1.329 the Claude Code trust dialog warns where a folder declares its hooks. Which hooks the gate holds back, which sessions skip it, and how to review a clone first."
tags:
  - claude
  - security
  - hooks
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-21
status: current
---

# Claude Code Trust Dialog: Review Hooks Before You Accept

> Claude Code's trust dialog names where a folder declares its hooks, so you can review them before you accept trust.

Since v2.1.329 (released November 19, 2026), the workspace trust dialog warns where a folder's hooks are declared ([changelog](https://code.claude.com/docs/en/changelog)). A command hook runs shell commands with your full user permissions ([hooks reference](https://code.claude.com/docs/en/hooks)). A cloned repository can commit hooks in `.claude/settings.json`, so the dialog is where Claude Code asks you about them.

## What the gate holds back

In an interactive session, Claude Code holds back hooks from every settings file until you accept the trust dialog for the folder, or for a parent directory whose trust extends to it. That includes your own `~/.claude/settings.json` ([hooks reference](https://code.claude.com/docs/en/hooks#workspace-trust)).

The changelog entry says only that the dialog names where the hooks are declared. It does not describe the dialog's layout, so this page does not either.

## Where hooks come from

Hook scope follows the file that declares them ([hooks reference](https://code.claude.com/docs/en/hooks#hook-locations)):

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All your projects | No, local to your machine |
| `.claude/settings.json` | Single project | Yes, can be committed to the repo |
| `.claude/settings.local.json` | Single project | No, gitignored when Claude Code saves a setting to it |
| Managed policy settings | Organization-wide | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | When the plugin is enabled | Yes, bundled with the plugin |
| Skill frontmatter | The rest of the session once the skill is invoked | Yes, defined in the skill file |
| Subagent frontmatter | While that subagent is running | Yes, defined in the subagent file |

For a clone, `.claude/settings.json` is the main file to read. Frontmatter hooks in a project skill follow the same trust rule as settings-file hooks. Frontmatter hooks in a project subagent follow a stricter rule: they run only after you accept the dialog for the folder the agent file came from ([hooks reference](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents)).

## How the session type changes the gate

| Situation | What happens to repository hooks | Source |
|-----------|----------------------------------|--------|
| `claude -p` or SDK session | Claude Code never shows the dialog and treats the folder as trusted, so hooks in `.claude/settings.json` run | [Hooks reference](https://code.claude.com/docs/en/hooks#workspace-trust) |
| You trusted only a parent folder | Settings-file hooks are used. Project subagent frontmatter hooks are not used, and no dialog is offered | [Permissions](https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder) |
| A clone inside a folder you trusted outside any repository | Parent trust does not cover a git repository nested in it, so an interactive session shows the dialog for the clone | [Permissions](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust) |
| `/cd` into an untrusted directory | The trust prompt lists the hooks the directory's settings would activate | [Permissions](https://code.claude.com/docs/en/permissions) |

The `claude -p` row is the one that bites. A script that points `claude -p` at a repository you did not write runs the hooks committed in its `.claude/settings.json` with no prompt at all.

## Review a clone before you trust it

1. Read `.claude/settings.json` and `.claude/settings.local.json` in the clone before the first interactive launch.
2. After you accept trust, type `/hooks`. It opens a read-only browser that labels each hook with its source, such as user settings, project settings, local settings, or a plugin, and shows the full command and the path of its settings file ([hooks reference](https://code.claude.com/docs/en/hooks#the-hooks-menu)).
3. For a `-p` run over a repository you did not write, start with `--bare`, or pass `--settings '{"disableAllHooks": true}'` ([hooks reference](https://code.claude.com/docs/en/hooks#workspace-trust)).
4. To skip the project's settings files entirely in a `-p` run, pass `--setting-sources user` ([permissions](https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder)).

Setting `disableAllHooks` in your user settings is not enough. A `"disableAllHooks": false` in the project's `.claude/settings.json` overrides it. To turn hooks off for one run whatever the project says, pass `--settings '{"disableAllHooks": true}'`, which takes precedence over project and local settings ([hooks reference](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks)).

## Managed hooks that fail to load

The same release adds a warning in the conversation when hooks in managed settings fail to load. It appears in Claude Desktop and other non-interactive hosts ([changelog](https://code.claude.com/docs/en/changelog)). It is not part of the trust dialog.

## Key Takeaways

- From v2.1.329 the trust dialog names where a folder declares its hooks.
- Interactive sessions hold back hooks from every settings file, including your user file, until you accept trust.
- `claude -p` and SDK sessions skip the dialog and run the hooks committed in a repository's `.claude/settings.json`.
- Use `/hooks` to read each hook's command and source, and `--bare` or `--settings '{"disableAllHooks": true}'` for scripted runs.
- The managed-settings load-failure warning appears in the conversation in non-interactive hosts, not in the dialog.

## Related

- [Pre-Trust Execution Surface in Coding Agent Harnesses](../../security/pre-trust-execution-surface.md)
- [Claude Code `--bare` Flag](bare-mode.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md)
