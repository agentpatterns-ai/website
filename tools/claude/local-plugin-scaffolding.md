---
title: "Local Plugin Scaffolding via `claude plugin init` and Auto-Loaded `.claude/skills`"
description: "Claude Code 2.1.157 auto-loads plugins from `.claude/skills/<name>/.claude-plugin/plugin.json` and `claude plugin init` scaffolds the layout in one command — when the manifest earns its keep over a loose skill, and when it does not."
tags:
  - claude
  - tool-engineering
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-30
status: current
---

# Local Plugin Scaffolding via `claude plugin init` and Auto-Loaded `.claude/skills`

> Claude Code 2.1.157 auto-loads plugins from `.claude/skills/<name>/.claude-plugin/plugin.json`, and `claude plugin init` scaffolds the layout in one command.

The pattern earns its keep when the bundle includes components beyond a single skill, when versioning or namespacing matter, or when the plugin is destined for distribution later. For a single `SKILL.md` in a single repo, loose `.claude/skills/<name>/SKILL.md` remains the cheaper default — the manifest forces namespaced names (`/my-plugin:hello` instead of `/hello`) and project-scope `@skills-dir` plugins do not walk up to the repo root the way plain skills do ([Plugins — When to use plugins vs standalone configuration](https://code.claude.com/docs/en/plugins#when-to-use-plugins-vs-standalone-configuration); [Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)).

## What 2.1.157 Shipped

Two entries landed together on 2026-05-29 ([Claude Code changelog](https://code.claude.com/docs/en/changelog)):

- "Plugins in `.claude/skills` directories are now automatically loaded, no marketplace required"
- "Added `claude plugin init <name>` to scaffold a new plugin in `.claude/skills`"

A skills-directory plugin is "any folder under a skills directory that contains a `.claude-plugin/plugin.json` manifest" — loaded as `<name>@skills-dir` on the next session "with no marketplace and no install step. Unlike a marketplace install, the plugin is discovered in place rather than copied into the plugin cache" ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)).

## The Three Shapes a Skills Tree Now Supports

A `.claude/skills/` (project) or `~/.claude/skills/` (personal) tree carries three coexisting things, distinguished by the presence of the manifest ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)):

| What you have | What it is |
|---|---|
| `<skills-dir>/foo/SKILL.md` with no manifest | A plain [skill](https://code.claude.com/docs/en/skills) named `foo`, invokable as `/foo` |
| `<skills-dir>/foo/.claude-plugin/plugin.json` | A plugin `foo@skills-dir` that can bundle skills, agents, hooks, MCP, LSP, and monitors |
| `<plugin>/skills/bar/SKILL.md` | A skill `bar` packaged inside a plugin, invoked as `/foo:bar` |

The first shape is the cheapest; the second is the unit this page is about; the third is what the second contains.

## The `claude plugin init` Command

```bash
claude plugin init my-tool
```

This creates `~/.claude/skills/my-tool/` with a `.claude-plugin/plugin.json` manifest and a starter `SKILL.md`. On the next session it loads as `my-tool@skills-dir` with no marketplace or install step ([Plugins — Develop a plugin in your skills directory](https://code.claude.com/docs/en/plugins#develop-a-plugin-in-your-skills-directory)).

Flags ([Plugins reference — plugin init](https://code.claude.com/docs/en/plugins-reference#plugin-init)):

| Flag | Effect | Default |
|---|---|---|
| `--description <text>` | Manifest description | — |
| `--author <name>` | Author name | `git config user.name` |
| `--author-email <email>` | Author email | `git config user.email` |
| `--with <components...>` | Scaffold extra component folders. Valid: `skills`, `agents`, `hooks`, `mcp`, `lsp`, `output-style`, `channel` | — |
| `-f, --force` | Overwrite an existing `.claude-plugin/` at the target | — |

The command has an alias: `claude plugin new`. Each `--with` value adds a starter file for the named component; for example `--with hooks` produces a `hooks/hooks.json` with a sample event handler.

## Scope: Personal vs Project

Where you scaffold the plugin determines who sees it and what it is allowed to do ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)):

| Skills directory | Scope | Loads |
|---|---|---|
| `~/.claude/skills/` | personal | In every project — the location is yours alone |
| `<cwd>/.claude/skills/` | project | Only after you accept the workspace trust dialog for that folder |

Project-scope plugins ship with the repository, so their components run with extra restrictions because the content comes from the repo rather than from you:

- MCP servers go through the same per-server approval as a project `.mcp.json` ([MCP](https://code.claude.com/docs/en/mcp))
- LSP servers start only after you trust the workspace
- Background monitors do not load at all

Personal-scope plugins under `~/.claude/skills/` have none of these restrictions — they are treated as yours.

## Why It Works

Claude Code already scans skill directories at session start to build the set of skills the model can invoke ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)). v2.1.157 extends the same scan: a child folder containing `.claude-plugin/plugin.json` is loaded in place as a plugin instead of being treated as a single skill. Because nothing is copied into the plugin cache, there is no install step to round-trip through a marketplace — the manifest is read where it sits, on every launch. `claude plugin init` collapses the manual scaffold — `mkdir -p`, hand-write `plugin.json`, hand-write a starter `SKILL.md` — into one command, with sensible defaults pulled from `git config user.name`/`user.email` ([Plugins reference — plugin init](https://code.claude.com/docs/en/plugins-reference#plugin-init)). The pair removes both the "scaffold ceremony" and the "marketplace round-trip" frictions in the same release, so for project-local bundles the scaffold-to-running-plugin loop is one command and one session restart.

## When This Backfires

The path is not always cheaper than loose skills, and the trade-off is concrete:

- **Single-repo, single-skill collection with no sharing intent.** The namespacing tax (`/my-plugin:deploy` vs `/deploy`) and version-field maintenance buy nothing; loose `.claude/skills/<name>/SKILL.md` is shorter to invoke and the auto-discovery walks up the repo root from any subdirectory ([Plugins — When to use plugins vs standalone configuration](https://code.claude.com/docs/en/plugins#when-to-use-plugins-vs-standalone-configuration); [Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)). Plugins earn their keep when bundling components beyond a single skill or when versioning and distribution matter.
- **Teams that launch Claude Code from subdirectories.** Project-scope `@skills-dir` plugins do not walk up to the repo root; a plugin at the repo root is silently missed when launching from `apps/api/`. Mitigation is either launching from the repo root or running `/reload-plugins` after `cd` ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)).
- **Enterprises that have set `strictKnownMarketplaces` to deny `skills-dir`.** Admins can block the `@skills-dir` source via `strictKnownMarketplaces` or by adding `{"source": "skills-dir"}` to `blockedMarketplaces` in [managed settings](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions); `plugin init` fails before writing. Teams in this posture must distribute via an approved marketplace instead ([Plugins reference — plugin init](https://code.claude.com/docs/en/plugins-reference#plugin-init)).
- **Plugins that need background monitors at project scope.** Background monitors do not load for project-scope `@skills-dir` plugins; a plugin whose value depends on monitors must be installed via a marketplace or moved to `~/.claude/skills/` ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)).
- **Edits to non-skill components require a reload.** Changes to a `SKILL.md` inside a skills-directory plugin take effect immediately in the current session, but changes to `hooks/`, `.mcp.json`, `agents/`, and `output-styles/` need `/reload-plugins` or a restart ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)).

## Removing a Skills-Directory Plugin

There is no `uninstall` because nothing was installed from a marketplace. Either delete the folder or disable by name ([Plugins reference — Skills-directory plugins](https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins)):

```bash
claude plugin disable my-tool@skills-dir
```

## Example

Scaffold a project-local plugin with a hook bundled alongside the default skill, in one command:

```bash
# From the repository root
claude plugin init repo-helper --with hooks --description "Repo conventions and lint hook"
```

This produces:

```text
.claude/skills/repo-helper/
├── .claude-plugin/
│   └── plugin.json        # name, description, author from git config
├── skills/
│   └── repo-helper/
│       └── SKILL.md       # starter skill — invoked as /repo-helper:repo-helper
└── hooks/
    └── hooks.json         # sample event handler, ready to edit
```

After the next session start (and after accepting the workspace trust dialog), the plugin loads as `repo-helper@skills-dir` with no marketplace registration. The skill is invokable as `/repo-helper:repo-helper`; the hook fires per its matcher.

## Key Takeaways

- v2.1.157 makes a `.claude/skills/<name>/.claude-plugin/plugin.json` folder auto-load as `<name>@skills-dir` with no marketplace, and `claude plugin init` scaffolds the layout in one command ([Claude Code changelog](https://code.claude.com/docs/en/changelog), 2026-05-29).
- Take the path when the bundle includes components beyond a single skill, when versioning matters, or when distribution is a near-term plan. Skip it for one-off skills in a single repo where loose `.claude/skills/<name>/SKILL.md` is shorter to invoke and walks up the repo root from subdirectories.
- Project-scope `@skills-dir` plugins load only after the workspace trust dialog; MCP and LSP servers face extra approval, and background monitors do not load at project scope.
- Subdirectory launches miss project-root `@skills-dir` plugins — launch from the repo root or run `/reload-plugins` after `cd`.
- Admins can block the `@skills-dir` source via `strictKnownMarketplaces` or `blockedMarketplaces` in managed settings; `plugin init` fails before writing.

## Related

- [Reloading Skills Mid-Session](reload-skills-mid-session.md) — `/reload-plugins` and `/reload-skills` are the companion commands when iterating on a scaffolded plugin without restarting.
- [Extension Points](extension-points.md) — Decision framework for choosing between CLAUDE.md, rules, skills, hooks, subagents, MCP, and plugins.
- [Plugin Background Monitors](plugin-background-monitors.md) — Why `monitors` declared by a plugin do not arm at project scope, and what to do about it.
- [Skill disallowed-tools Frontmatter](skill-disallowed-tools.md) — The skill-layer denial mechanism that survives unchanged when a skill is packaged inside a plugin.
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md) — Where admins set `strictKnownMarketplaces` and `blockedMarketplaces` to allow or deny the `@skills-dir` source organisation-wide.
