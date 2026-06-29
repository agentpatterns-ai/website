---
title: "Claude Code for AI Agent Development"
description: "Tool-specific reference for Claude Code's agentic features. - Sub-Agents — Ephemeral, isolated agents for focused task execution - Agent Teams — Coordinated"
tags:
  - claude
  - index
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-14
status: current
---
# Claude Code

> Tool-specific reference for Claude Code's agentic features.

These features run on Anthropic's current model line. As of June 2026 the Claude models reference lists Claude Fable 5 at general availability and Claude Mythos 5 in preview, both fronting adaptive thinking and a 1M-token context window — positioned above the prior Opus 4.8 generation ([Claude models overview](https://platform.claude.com/docs/en/docs/about-claude/models)).

## Pages

- [Sub-Agents](sub-agents.md) — Ephemeral, isolated agents for focused task execution
- [Agent Teams](agent-teams.md) — Coordinated multi-agent sessions with shared task lists
- [Agent View](agent-view.md) — Dispatch-attach-monitor surface for parallel background sessions, with blocked-on-input as a first-class state
- [Auto Mode](auto-mode.md) — Classifier-based permission gating for unattended execution
- [Hard-Deny Classifier Rule](hard-deny-classifier-rule.md) — Unconditional block layer inside auto mode's classifier — user intent and allow exceptions do not apply
- [Parameter-Level Permission Rules](tool-param-value-permission-rules.md) — `Tool(param:value)` syntax matches deny/ask rules against a tool's input-parameter values, e.g. `Agent(model:opus)` to block Opus subagents
- [Bare Mode](bare-mode.md) — Deterministic headless CI mode — skip all local config discovery with `--bare`
- [Extension Points](extension-points.md) — Decision framework for choosing between CLAUDE.md, rules, skills, hooks, subagents, MCP, and plugins
- [Hooks & Lifecycle](hooks-lifecycle.md) — Deterministic automation at 12+ lifecycle events
- [Agent SDK](agent-sdk.md) — The Claude Code runtime as a library for custom applications
- [/batch & Worktrees](batch-worktrees.md) — Parallel execution with worktree isolation
- [Feature Flags & Environment Variables](feature-flags.md) — Curated reference for the most impactful configuration knobs
- [Session Scheduling](session-scheduling.md) — /loop and cron tools for recurring prompts within a session
- [Cloud-Scheduled Routines vs Local Session Scheduling](cloud-scheduled-routines.md) — When to move schedule out of the local box; cloud Routines trade working-tree fidelity for uptime continuity
- [Skill Eval Loop](skill-eval-loop.md) — Test, benchmark, A/B-compare, and optimize agent skills with the skill-creator eval framework
- [Reloading Skills Mid-Session](reload-skills-mid-session.md) — Re-scan skill directories with /reload-skills or a SessionStart hook, picking up edits without losing context
- [Monitor Tool](monitor-tool.md) — Stream stdout from background scripts to Claude line-by-line, eliminating polling loops
- [Plugin Background Monitors](plugin-background-monitors.md) — Declarative supervision auto-armed at session start via the `monitors` manifest key
- [Plugin-Activated Main-Agent Override and Bin/ PATH Injection](plugin-main-agent-override-and-path-injection.md) — Plugin `settings.json` swaps the main thread agent; `bin/` injects executables onto the Bash tool's PATH for the plugin's enabled lifetime
- [Channels Permission Relay](channels-permission-relay.md) — Forward tool-use approval prompts to your phone for unattended agent runs
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md) — Deploy independent policy fragments per team without merge conflicts
- [PowerShell Tool](powershell-tool.md) — Native Windows shell for Claude Code via PowerShell instead of Git Bash
- [Skill disallowed-tools Frontmatter](skill-disallowed-tools.md) — Skill-layer tool denial: remove tools from the model while a skill is active, the deny-side complement to allowed-tools
- [Local Plugin Scaffolding (`claude plugin init`)](local-plugin-scaffolding.md) — Auto-load plugins from `.claude/skills/<name>/.claude-plugin/plugin.json` and scaffold the layout in one command — when the manifest earns its keep over a loose skill, and when it does not
