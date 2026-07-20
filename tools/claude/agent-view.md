---
title: "Agent View: Dispatch-Attach-Monitor Surface for Parallel Sessions"
description: "Claude Code's claude agents view groups background sessions by state, elevates blocked-on-input rows, and makes dispatch config first-class per session."
aliases:
  - claude agents view
  - dispatch attach monitor surface
  - claude code background session dashboard
tags:
  - claude
  - agent-design
  - observability
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
status: current
---

# Agent View: Dispatch-Attach-Monitor Surface for Parallel Sessions

> Agent view is one terminal screen for every background session, grouped by what attention each one needs and addressable with one key per direction.

Agent view is the surface Claude Code ships for managing N async sessions at once. `claude agents` opens a full-terminal list grouped `Pinned` → `Ready for review` → `Needs input` → `Working` → `Completed`, with a dispatch input at the bottom and a peek panel keyed to the selected row ([Agent view](https://code.claude.com/docs/en/agent-view)). It shipped in Claude Code v2.1.139 as a research preview ([Week 20 changelog](https://code.claude.com/docs/en/whats-new/2026-w20)). It sits apart from the worktree isolation underneath and the cross-tool [editor-and-manager surface convergence](../../patterns/agent-design/editor-manager-surface-separation.md). What it adds is the dispatch-attach-monitor loop itself: per-row spawn config, an elevated blocked-on-input group, and one-key attach-and-return that keeps you in the orchestrator role.

## Three surfaces in one screen

- Dispatch input at the bottom accepts a prompt, a sub-agent name (`<name>` or `@name`), a repository mention (`@<repo>`), a slash command, or a shell job prefix (`! pytest -x`). `Enter` starts a new background session; `Shift+Enter` dispatches and attaches immediately.
- State-grouped row list shows every background session across every project (filter with `claude agents --cwd <path>`, v2.1.141+). Each row carries a Haiku-generated one-line summary refreshed at most every 15 seconds, so it tells you what the session is doing without opening the transcript.
- Peek panel opens with `Space` and shows the most recent output, the question a blocked session is waiting on, and any opened pull requests. Multiple-choice prompts surface as number keys; `Tab` fills the input with a suggested reply; `!` prefix sends a Bash command.

`Enter` or `→` attaches — the session takes over the terminal as if you had run `claude` in that directory, with a recap of what happened while away. `←` on an empty prompt detaches back to the list. Detaching never stops a session; `/stop`, `Ctrl+X` twice, or `claude stop <id>` end it ([Agent view](https://code.claude.com/docs/en/agent-view)).

## Six session states

The state vocabulary is the load-bearing design choice. Without `Needs input` as a first-class state, a parallel-session screen reduces to "running vs done" and the operator has to scan transcripts to find blocked rows.

| State | Icon | Meaning |
|-------|------|---------|
| Working | Animated | Tools running or response generating |
| Needs input | Yellow | Waiting on a specific question or permission decision |
| Idle | Dimmed | Nothing to do; ready for the next prompt |
| Completed | Green | Task finished successfully |
| Failed | Red | Task ended with an error |
| Stopped | Grey | Stopped with `Ctrl+X` or `claude stop` |

Process-shape is encoded separately: `✻` or animated `✽` for a live process, `∙` for an exited process that can still be peeked and reattached (the supervisor restarts on demand), `✢` for a [`/loop`](session-scheduling.md) session sleeping between iterations. The terminal tab title also reflects blocked count (`2 awaiting input · claude agents`), so the signal escapes the agent view window itself ([Agent view](https://code.claude.com/docs/en/agent-view)).

## Per-row dispatch config

Flags passed to `claude agents` set defaults that apply to every session dispatched from that view; defaults appear in the footer. Per-session overrides come from `claude --bg --model <name>` in the shell, attaching and switching with in-session `/model s <name>`, or dispatching a sub-agent whose frontmatter sets `model`.

| Flag | Effect | Min version |
|------|--------|-------------|
| `--cwd <path>` | Scope the list to sessions under `<path>` | v2.1.141 |
| `--permission-mode <mode>` | Default `plan` / `acceptEdits` / `auto` / `bypassPermissions` | v2.1.142 |
| `--model <name>` | Override the dispatch model | v2.1.142 |
| `--effort <level>` | Reasoning effort for dispatched sessions | v2.1.142 |
| `--agent <name>` | Sub-agent run when a dispatch prompt names none | v2.1.157 |
| `--settings`, `--add-dir`, `--plugin-dir`, `--mcp-config`, `--strict-mcp-config` | Passed through to dispatched sessions | v2.1.142 |

`bypassPermissions` and `auto` are refused until accepted interactively once, since agent view dispatches let a session act without you watching ([Agent view](https://code.claude.com/docs/en/agent-view)).

The dispatch input doubles as a filter when typed instead of submitted: `a:<name>` filters by sub-agent, `s:<state>` by state (including `s:blocked`), `#<number>` or a PR URL jumps to the session working on that pull request. `Ctrl+S` switches grouping between state and directory; `Ctrl+T` pins (pinned sessions keep their process alive while idle); `Alt+1`–`Alt+9` jumps to one of the first nine sessions; `?` shows the full shortcut sheet.

## Why it works

Parallel async agents create two coordination problems a chat panel cannot solve. Operator attention is a serial resource that switches at non-trivial cost. And blocked-on-input is a latent state — a blocked agent stops emitting tokens, so without an external indicator the operator cannot tell which row needs them. Agent view splits these. The Haiku-generated row summary makes polling N sessions cheap, and the `Needs input` group elevates blocked rows so finding them is O(1) instead of O(N transcripts) ([Agent view](https://code.claude.com/docs/en/agent-view)). Attach-and-return keeps you in the orchestrator role: you drop into one full conversation only when judgment is required, then `←` back. This matches the cross-tool finding that aggregated per-agent state lives outside the editor once concurrency exceeds one ([Editor and Manager Surface Separation](../../patterns/agent-design/editor-manager-surface-separation.md)).

## When this backfires

- Concurrency ≤ 1. A single session pays the dashboard round-trip without the scannability gain — `claude` directly is simpler ([Editor and Manager Surface Separation](../../patterns/agent-design/editor-manager-surface-separation.md)).
- Quota-bound work. Background sessions consume subscription quota the same as interactive ones, so "running ten agents in parallel uses quota roughly ten times as fast as running one" ([Agent view](https://code.claude.com/docs/en/agent-view) §Limitations). The surface shows what runs; it does not curb cost.
- Sessions that need to talk to each other. Agent view rows report only to you. Cross-session coordination is the contract of [agent teams](agent-teams.md) or [dynamic workflows](dynamic-workflows.md), not agent view ([Run agents in parallel](https://code.claude.com/docs/en/agents)).
- Beyond ~10–20 concurrent sessions. A flat row list stops scaling. Cursor's parallel-agents research finds high-N populations need a structured task substrate — "a place to find work, understand who owns it, know what state it's in" — that a dispatch surface alone does not provide ([Cursor research on 100 parallel agents — MindStudio](https://www.mindstudio.ai/blog/cursor-research-100-agents-parallel-flat-agent-teams-issue-tracker)). At that scale, push into [issue-tracker agent dispatch](../../workflows/issue-tracker-agent-dispatch-surface.md).
- Bedrock, Vertex AI, or Foundry on older versions. Earlier releases printed a sub-agent list and exited instead of opening agent view; `claude update` picks up the fix ([Agent view](https://code.claude.com/docs/en/agent-view) §Troubleshooting).
- Non-git working directory without `WorktreeCreate` hook. File isolation falls through to direct writes; parallel sessions can trample each other's edits ([Agent view](https://code.claude.com/docs/en/agent-view) §How file edits are isolated).
- One local host as the ceiling. Sessions run on your machine under a per-user supervisor: they survive sleep but a shutdown stops them, and under memory pressure the supervisor evicts idle non-pinned sessions first ([Agent view](https://code.claude.com/docs/en/agent-view) §How background sessions are hosted). True fleet-scale parallelism needs a remote substrate the surface does not provide.

## Example

Open agent view scoped to one repo with a non-default model and permission mode, then dispatch two sessions from the input:

```bash
claude agents --cwd ~/projects/api --model opus --permission-mode plan
```

```text
> investigate the flaky SettingsChangeDetector test
> @code-reviewer address review comments on PR 1234
```

The first prompt dispatches a fresh session; the second routes to the `code-reviewer` [sub-agent](sub-agents.md). When a row turns yellow under `Needs input`, `Space` opens the peek panel with the exact question; `Tab` fills the input with a suggested reply; `Enter` sends it without leaving the list. `Enter` attaches for the full conversation; `←` on an empty prompt returns ([Agent view](https://code.claude.com/docs/en/agent-view)).

## Key Takeaways

- Agent view is the dispatch-attach-monitor surface for parallel Claude Code sessions — research preview, requires Claude Code v2.1.139 or later
- The state vocabulary has six values; `Needs input` (yellow) and the `Needs input` group at the top of the list are what makes blocked-on-input a first-class signal rather than a transcript-scan
- Per-row dispatch config (`--model`, `--effort`, `--permission-mode`, `--agent`, `--cwd`) lives on the spawn surface — flags passed to `claude agents` propagate as defaults to every dispatched session
- Attach is `Enter`/`→`; detach is `←` on an empty prompt; detaching never stops the session — only `/stop`, `Ctrl+X` twice, or `claude stop <id>` end it
- The surface buys back operator attention but does not change per-session quota cost; pair it with agent teams or dynamic workflows when sessions need to coordinate, or with an issue-tracker surface above ~10–20 concurrent rows

## Related

- [Editor and Manager Surface Separation in Agent IDEs](../../patterns/agent-design/editor-manager-surface-separation.md) — the cross-tool convergence this pattern is a Claude-specific instance of
- [Parallel Agent Sessions Shift the Bottleneck from Writing](../../workflows/parallel-agent-sessions.md) — the human-factors bottleneck shift that agent view absorbs
- [Claude Code Agent Teams](agent-teams.md) — cross-session coordination with shared task lists and mailbox messaging
- [Dynamic Workflows](dynamic-workflows.md) — script-driven parallelism when a job outgrows a handful of subagents
- [Sub-Agents](sub-agents.md) — the in-session delegation primitive dispatched via `@name` in agent view
- [/batch & Worktrees](batch-worktrees.md) — the worktree isolation primitive that backs every dispatched session
