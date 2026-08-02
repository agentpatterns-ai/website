---
title: "Cursor Customize Page: Unified Surface for Agent Primitives"
description: "Cursor 3.9's Customize page consolidates plugins, skills, MCPs, subagents, rules, commands, and hooks at user/team/workspace scope — with a leaderboard, canvases, and team marketplaces."
tags:
  - cursor
  - tool-engineering
  - instructions
aliases:
  - cursor customize surface
  - cursor unified customization
applies_to: "cursor@3.x"
last_reviewed: 2026-06-28
status: current
---

# Cursor Customize Page

> The Cursor Customize page is one surface to add and manage plugins, skills, MCPs, subagents, rules, commands, and hooks at user, team, or workspace scope.

Cursor 3.9, released June 22, 2026, ships a Customize page that federates seven customization primitives behind a single UI with explicit install scopes and a team-popularity leaderboard ([Cursor changelog — Customize](https://cursor.com/changelog/customize); [Cursor docs, Customize Cursor](https://cursor.com/docs/customize-cursor)). It is a discovery and management surface, not a new storage backend, and its value depends on team size, config-as-code discipline, and supply-chain posture.

## When This Pays Off

The Customize page assumes three preconditions; treat the absence of any of them as a signal to ignore it.

- Multiple developers share a setup. The leaderboard signal and team marketplaces are zero-value for a solo workflow.
- Primitive accumulation has overrun discoverability. Inside the Claude Code ecosystem, practitioners explicitly call out "great file sprawl" — each primitive in its own location, format, and manual setup — as the problem plugins solve ([DEV.to — Plugins: Share Your Entire Claude Code Setup](https://dev.to/rajeshroyal/plugins-share-your-entire-claude-code-setup-with-one-command-294n)). Two rules and one MCP do not have this problem.
- No strict config-as-code discipline. Customize federates the UI over existing file stores; it does not replace them. Teams already operating IaC-style on `.cursor/rules/` see the page as a regression surface.

## What the Page Manages

| Primitive | What it is |
|---|---|
| Plugins | Distributable bundles that package rules, skills, subagents, commands, MCP servers, and hooks ([Cursor docs](https://cursor.com/docs/customize-cursor)) |
| Rules | Persistent instructions across project / user / team / `AGENTS.md` scope |
| Skills | `SKILL.md`-packaged domain knowledge, workflows, and scripts |
| Subagents | Isolated assistants for parallel work in separate context windows |
| Commands | Markdown prompts invoked via `/` in Agent chat |
| Hooks | Scripts that observe, control, or extend the agent loop at lifecycle events |
| MCPs | Model Context Protocol servers, including bring-your-own |

Each primitive installs at three scopes, user (cross-project, per-developer), team (organization-wide via the dashboard), or workspace (this project only), through the same UI ([Cursor changelog — Customize](https://cursor.com/changelog/customize)).

## Discovery Features

Three discovery surfaces shipped together ([Cursor changelog — Customize](https://cursor.com/changelog/customize)):

- Marketplace leaderboard ranks the most popular plugins, skills, and MCPs across the team, with one-click install.
- Plugin canvases are prebuilt setup templates teammates can open and reuse — the launch examples are a Hex Canvas for data visualizations and an Atlassian Canvas for issue, project, and document viewing.
- Team marketplaces import plugin repositories from GitLab, BitBucket, and Azure DevOps, broadening the supply beyond GitHub.

## Cross-Tool Pattern

The same primitive-bundle-as-shareable-unit shape exists in two other harnesses, which is why the underlying constraint is a category property of agent harnesses, not a Cursor quirk:

- [Claude Code plugins](../claude/extension-points.md) bundle skills, agents, hooks, commands, MCP servers, and LSP servers into a self-contained directory and surface them through `/plugin`. Marketplaces register via `.claude/settings.json`'s `extraKnownMarketplaces`; `enabledPlugins` pins which are active per project ([Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces); [Plugins reference](https://code.claude.com/docs/en/plugins-reference)). [Local plugin scaffolding](../claude/local-plugin-scaffolding.md) gives `claude plugin init` for one-command setup.
- [Copilot custom agents, skills, and plugins](../copilot/custom-agents-skills.md) form the same three-layer shape. The [`awesome-copilot`](https://github.com/github/awesome-copilot) registry is registered by default in Copilot CLI and VS Code; the launch post reports 175+ agents, 208+ skills, 176+ instructions, and 48+ plugins from community contribution ([Awesome GitHub Copilot — launch post](https://developer.microsoft.com/blog/awesome-github-copilot-just-got-a-website-and-a-learning-hub-and-plugins)).

Customize is Cursor's catch-up to that pattern with a UI-first delivery rather than the file-format-first delivery Claude Code and Copilot reached first.

## Why It Works

Customization primitives in agent harnesses accumulate faster than developer attention does. Each primitive lives in its own file, format, and scope, and the cost of "finding what your teammate set up" grows multiplicatively, not linearly — the [DEV.to plugin-setup post](https://dev.to/rajeshroyal/plugins-share-your-entire-claude-code-setup-with-one-command-294n) names this "file sprawl" inside Claude Code itself. A single management surface with explicit install scope collapses the per-primitive discovery cost to one mental model. The leaderboard adds team-internal social proof — the strongest signal a developer has for "which colleague's setup should I adopt" absent a formal review process. Three independent ecosystems converging on the same shape (Cursor Customize, Claude Code `/plugin`, Copilot `awesome-copilot`) is the strongest available evidence that the underlying constraint is general to harness design.

## When This Backfires

- UI / config-as-code drift. Customize does not unify storage. Project Rules live in `.cursor/rules/` as version-controlled `.mdc` files; User Rules live in Customize settings; Team Rules live in the team dashboard ([Cursor docs — Rules](https://cursor.com/docs/rules)). UI-driven changes routinely diverge from version-controlled config — the click-ops failure mode IaC discipline exists to close ([JetBrains blog — Jenkins config drift](https://blog.jetbrains.com/teamcity/2025/12/jenkins-configuration-drift/)). Reviewing a PR shows project rules; nothing in the PR tells you what your teammate's user-scope rules add or override.
- Popularity is not provenance. Generic broadly-useful items dominate the leaderboard; technically superior niche items do not surface ([gocodeo — Navigating VSCode's Marketplace](https://www.gocodeo.com/post/navigating-vscodes-marketplace-how-to-vet-and-trust-extension-quality)). The 2026 WordPress case — 30+ trusted plugins bought on Flippa and dormant-backdoored for eight months — demonstrates how popularity signals are weaponized when ownership transfers go un-audited ([InfoQ — WordPress plugin supply chain](https://www.infoq.com/news/2026/05/wordpress-plugins-supply-chain/)). One-click install from a leaderboard does not expose ownership history or pinned commit SHAs.
- AGENTS.md-first repos. Teams centralizing on the [AGENTS.md open standard](https://agents.md) get a tool-specific surface back from Customize, not a cross-tool one. An AGENTS.md-first repo has already paid the consolidation cost in plain markdown a teammate can read in any editor.

## Key Takeaways

- The Customize page is a discovery and management UI; underlying storage is still split across `.cursor/rules/` (repo), Customize settings (user), and the team dashboard (team).
- The seven-primitive × three-scope matrix — plugins, skills, MCPs, subagents, rules, commands, hooks × user, team, workspace — is the load-bearing model.
- The pattern pays off when primitive sprawl and team-sharing friction are real; it adds drift and supply-chain surface when they are not.
- Cursor's release is convergence with [Claude Code plugins](../claude/extension-points.md) and [Copilot's awesome-copilot](../copilot/custom-agents-skills.md), not invention.

## Related

- [Cursor for AI Agent Development](index.md) — section index for Cursor-specific reference pages
- [Cursor SDK](cursor-sdk.md) — the programmable TypeScript counterpart to Customize for embedding the harness rather than configuring the IDE
- [Cursor 3 Agents Window](agents-window.md) — the parallel-agent surface that hosts the subagents Customize manages
- [Claude Code Extension Points](../claude/extension-points.md) — the same primitive-bundle decision space in Claude Code
- [GitHub Copilot Custom Agents and Skills](../copilot/custom-agents-skills.md) — Copilot's three-layer extensibility and its `awesome-copilot` marketplace
