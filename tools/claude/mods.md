---
title: "Claude Code Mods and When to Use One Instead of a Hook"
description: "A mod is plugin code Claude Code runs in its own process. It can draw panes, rewrite events, and approve a call a PreToolUse hook blocked, which makes it an interface surface rather than an enforcement one."
tags:
  - claude
  - tool-engineering
aliases:
  - Claude Code mods
  - in-process plugin hooks
  - the mods API
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-07
status: current
---

# Claude Code Mods and When to Use One Instead of a Hook

> A mod is plugin code running inside Claude Code's process, so it can draw panes, rewrite events, and approve a call your hook blocked.

Claude Code 2.1.287 shipped the surface on 1 October 2026 with one changelog line: "Added Claude Mods: plugins may now modify deeper behavior" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Nothing needs switching on, because "Mods require Claude Code v2.1.287 or later, and they're on by default" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)).

## What a mod is

A mod is a plugin "that changes how Claude Code looks and behaves. It's made of JavaScript or TypeScript event handlers" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). Three files carry it. The first is a `.claude-plugin/plugin.json` manifest. The second is a `hooks/hooks.json` whose `modules` array names one path to the hooks module. The third is the module itself, which "Exports `register(on, options)`" ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)). That same `hooks.json` "Can also hold settings hooks under `hooks`". A `types/index.d.ts` contract becomes required once the mod uses `$.state` or adds a namespace to the mods API.

The naming confuses people, and the docs settle it. Settings hooks run "as a shell command, HTTP request, or prompt you configure in a settings file", while a mod's handlers "are functions that run inside Claude Code instead" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). Both are called hooks. The docs reserve the term settings hook for the settings-file kind. One plugin can carry both, so the choice is per behavior.

Each handler takes `($, e, next)`. Calling `next(e)` "Runs the hooks after this one, then Claude Code's behavior" ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)). That leaves three moves. Await it and read the result. Pass a changed copy forward. Or return something like `{ deny: "Use the file tools." }` without calling it at all.

## Why it works

The claude.dev walkthrough draws the contrast in two sentences: "A settings hook runs a shell command for each event and passes JSON over stdin and stdout. A mod is loaded once and stays in the session" ([Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/)). A fresh subprocess per event holds no handle on the renderer and no identity between events. It can decide and it can log. Staying in the session gets a mod three things that subprocess cannot have. Those are a place in the middleware chain, the render tree for the component being drawn, and live state across events. A mod is the only one of the four extension points whose answer to "Can it draw in the interface" is yes ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)).

The same placement is the price. "Mods aren't sandboxed". The sharpest consequence lands on anyone who has already built a guard. "A mod that approves tool calls can approve one that an `ask` rule would prompt for, or that one of your own `PreToolUse` hooks blocked" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). One carve-out survives. "A mod can restyle much of Claude Code's interface, but not the permission prompt."

## The three reload paths

Mods get described as hot-reloading, which holds for two of the three ways one reaches a session.

| How the mod is loaded | What picks up a change |
|---|---|
| `--plugin-dir ./my-mod` | Claude Code "watches a directory loaded with `--plugin-dir` and hot-reloads the hooks module when a file in it changes" ([Create a mod](https://code.claude.com/docs/en/plugins/mods/create)) |
| Written by Claude in-session | "the mods in the session's mods folder load when the turn ends, and reload at the end of each turn that changes them" ([Create a mod](https://code.claude.com/docs/en/plugins/mods/create)) |
| Installed from a marketplace | "If you install or update a mod from your shell while a session is open, run `/reload-plugins` in that session to load it" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)) |

Reloading costs you module scope. "Each reload runs `register` again, so `calls` resets to `0`" ([Create a mod](https://code.claude.com/docs/en/plugins/mods/create)). Put a counter or a history in `$.state` instead, declared in the manifest's type contract. A directory passed to `--plugin-dir` is also a protected path, "so in `default` and `acceptEdits` modes you're asked to approve each of Claude's edits to the mod". Skills reload by a separate mechanism, covered in [reloading skills mid-session](reload-skills-mid-session.md).

## The ceiling and agentId fields on tool.check

Claude Code 2.1.290, released 5 October 2026, added two fields to a mod's permission check. One changelog line reads: "Added `ceiling` to the question and verdict a mod's `tool.check` hook reads, naming the approval an organization requires for a tool". The other reads: "Added `agentId` to the `tool.check` event of plugin hooks, so a hook can tell a subagent's permission check from the main session's" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

No published page describes the shape of `ceiling`. Its type, its values, and whether every call carries it are undocumented. The public typings predate it: the file header says Claude Code 2.1.277 wrote it, and neither `ToolCheckInput` nor `ToolCheckResult` lists the field ([claude-code.d.ts](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts)). The `.d.ts` files a local load writes into `.claude-plugin/types/` show the real shape, so do not branch on specific values.

No source says where the organization's level comes from, so this link is inferred from shared wording. The nearest match is the 2.1.287 changelog entry on "organization per-tool permission ceilings" for MCP tools, and the per-tool controls an organization sets on claude.ai connectors. Claude Code "reads these settings at startup and enforces them locally" ([MCP docs](https://code.claude.com/docs/en/mcp)). Treat `ceiling` as naming "the approval an organization requires for a tool", and do not assume which tools carry it.

For a connector tool set to `ask`, the engine prompts, not your hook. "Claude Code prompts on every call with the reason `Your organization requires approval for this tool`". The prompt appears even in `acceptEdits`, `auto`, and `bypassPermissions` modes, and `dontAsk` mode denies the call instead ([MCP docs](https://code.claude.com/docs/en/mcp)). The permissions page says such tools still prompt when a settings hook returns allow ([Permissions](https://code.claude.com/docs/en/permissions)). It does not say in plain words whether a mod's allow gets the same treatment, so verify that before you rely on it. Release 2.1.292 fixed a different case: a plugin's `tool.check` allow ran a tool that requires your answer, such as a question or a plan approval, without showing its dialog ([changelog](https://code.claude.com/docs/en/changelog)).

The changelog says `ceiling` names "the approval an organization requires for a tool". It does not document what a hook should do with it, so test any use against your build's `.d.ts` files first.

Settings hooks already carried `agent_id`, which is "Present only when the hook fires inside a subagent call" ([Hooks reference](https://code.claude.com/docs/en/hooks)). The 2.1.290 changelog adds `agentId` to the `tool.check` event. Use it to apply different checks to subagent calls.

The pattern fails in two cases:

- Desktop app local and SSH sessions do not receive the organization's `ask` setting ([MCP docs](https://code.claude.com/docs/en/mcp)).
- A Claude Code older than 2.1.290 sees neither field, and a mod written against the 2.1.277 typings gets no type hints for either. Whether a missing `ceiling` means no organization requirement is undocumented, so a hook should not treat absence as approval.

## When this backfires

- Nothing draws outside the terminal and the Desktop app's Code tab. A mod's hooks run wherever the plugin loads. But "Drawing is narrower: only the terminal and the Desktop app show a mod's panes, bands, and replaced rows" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). The same table marks the VS Code extension's chat panel, `claude -p`, the Agent SDK, and cloud sessions as hooks-yes and draws-no. A pane is dead weight in a [headless CI session](bare-mode.md).
- A WSL session in the Desktop app loads no plugin at all, so the handlers never fire there.
- A mod is not an enforcement point. The guard mod in the claude.dev walkthrough says so: "It's a safety net, not a permission system. [...] Use permission rules for a hard block" ([Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/)). A handler also gets 10 seconds of its own time per event. That budget excludes time inside `next` and inside any mods API call other than `$.clock.sleep`. "Claude Code skips a hook that exceeds a time limit" ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)).
- On a managed machine, a user's mod stops before a user's settings hook does. Under `allowManagedModsOnly`, only the organization's mods and the built-in ones load, and "Users' settings hooks keep running" ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)).
- The API is unfinished. The walkthrough warns that "The API can change between releases" ([Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/)). Each load writes "TypeScript declaration files, ending in `.d.ts`, into `.claude-plugin/types/` inside the mod's directory" ([Create a mod](https://code.claude.com/docs/en/plugins/mods/create)). Those beat the published ones, because "The copy on GitHub can be older than the Claude Code version you have installed" ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)).

## Example

Blast Radius, one of the three mods in the claude.dev walkthrough, hooks `tool.call` with a `{ tool: "Bash" }` matcher. It matches risky commands such as `rm -rf`, `git reset --hard`, or a force push. It collects a report with `$.process.run`, using the tools' own dry-run commands (`git status --porcelain`, `git clean -n`). It then opens a pane with Proceed and Cancel, and returns a `deny` carrying the reason if you cancel ([Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/)).

The pane and the held call are only possible in-process, so no settings hook could have built it. The gap it leaves is also why it is not the control. It reads command text, so a `$(…)` substitution or a script that calls `rm` walks straight through. The build that actually holds pairs it with a `deny` rule from [parameter-level permission rules](tool-param-value-permission-rules.md). The mod shows you the blast radius, and the rule does the blocking.

## Key Takeaways

- Pick a mod when you want a pane, a band above the prompt, a custom command, or to rewrite an event. Pick a settings hook when you want to block, allow, or log one with a script you already have ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)).
- Installing a mod is a trust decision rather than a configuration change. Run `claude plugin validate` on its directory first. "The `hooks:` and `calls:` lines in the output list the events the mod handles and what it asks Claude Code to do" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). That listing is possible only because "A hook has no other way to do those things" than the mods API.
- A mod outranks your own `PreToolUse` hook on tool approval. A hook you rely on stops being a floor once a mod is installed.

## Related

- [Claude Code Extension Points: When to Use What](extension-points.md) — the decision framework mods now extend, covering CLAUDE.md, rules, skills, hooks, subagents, MCP, and plugins
- [Claude Code Hooks Lifecycle](hooks-lifecycle.md) — the settings-hook events a mod's handlers sit beside
- [Local Plugin Scaffolding via `claude plugin init`](local-plugin-scaffolding.md) — the manifest layer underneath a mod, and when it beats a loose skill
- [Reloading Skills Mid-Session in Claude Code](reload-skills-mid-session.md) — the adjacent reload mechanism, for skills rather than plugin code
- [Enterprise-Managed Plugin Governance for Agent CLIs](../../security/enterprise-managed-plugin-governance.md) — the managed settings and hooks that a user's mod cannot override
- [Plugin Background Monitors](plugin-background-monitors.md) — the other way a plugin runs work for the length of a session
- [Watcher Side Agents](../../patterns/agent-design/watcher-side-agents.md) — the pattern behind the `you-should-know` built-in, and the trigger it needs to pay off
