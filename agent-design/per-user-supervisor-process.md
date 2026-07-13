---
title: "Per-User Supervisor Process for Background Agent Sessions"
term: "Per-User Supervisor Process"
description: "A managed-daemon model where a per-user supervisor spawns each background agent session as a detached process, reconnects via on-disk roster, evicts idle non-pinned sessions, and restarts in place onto an updated binary — so terminal close, shell exit, and auto-update never end the work."
tags:
  - agent-design
  - tool-agnostic
  - reliability
aliases:
  - per-user agent daemon
  - background agent supervisor
  - agent session daemon
last_reviewed: 2026-06-12
maturity: established
---

# Per-User Supervisor Process for Background Agent Sessions

> A per-user daemon hosts background agent sessions as detached children, reconnects via an on-disk roster, evicts idle ones, and restarts onto updated binaries in place.

A per-user supervisor owns the lifecycle of background agent sessions: it spawns each as its own process, survives terminal close, restarts onto an updated binary, stops idle non-pinned sessions, and exits when none remain. It decouples three lifecycles the naive "terminal owns the agent" model conflates — the agent loop, the user's terminal, and the binary version.

## What the supervisor owns

Claude Code's reference implementation states the role exactly: "Background sessions are hosted by a per-user supervisor process, separate from your terminal and from agent view. The supervisor starts automatically the first time you background a session or open agent view, and you don't manage it directly" ([Claude Code: agent view](https://code.claude.com/docs/en/agent-view#the-supervisor-process)). Five responsibilities sit there and nowhere else:

- Detached child sessions. "Each background session is its own Claude Code process, managed by the supervisor rather than tied to your terminal" ([agent view docs](https://code.claude.com/docs/en/agent-view#the-supervisor-process)). Closing the terminal does not signal the session.
- Roster-backed reconnect. Running sessions are listed in `~/.claude/daemon/roster.json` — "List of running background sessions, used to reconnect after a restart" ([agent view docs](https://code.claude.com/docs/en/agent-view#where-state-is-stored)). When the supervisor crashes or is replaced, the roster lets it re-attach rather than orphan its children.
- Idle eviction with pinning exemption. "Once a session finishes and sits unattached for about an hour, the supervisor stops its process to free resources. A session you have pinned with `Ctrl+T` is exempt and keeps its process running while idle" ([agent view docs](https://code.claude.com/docs/en/agent-view#the-supervisor-process)). Pinning is how the user says "keep this hot" — no per-session lifetime API.
- Memory-pressure tier ladder. "When the host runs low on memory, the supervisor stops idle non-pinned sessions first and stops idle pinned ones only if that freed nothing" ([agent view docs](https://code.claude.com/docs/en/agent-view#the-supervisor-process)).
- Binary-on-disk watch as rolling-upgrade trigger. "The supervisor watches the installed Claude Code binary on disk and restarts into the new version after the regular auto-updater replaces it. This is a local file watch, not a network check. Background sessions are detached processes, so they keep running through the restart and the new supervisor reconnects to them" ([agent view docs](https://code.claude.com/docs/en/agent-view#the-supervisor-process)).

When every session finishes and no terminal is attached, the supervisor exits and restarts on next demand — daemon-managed, but not always-on.

## State lives where the supervisor can find it

Three on-disk locations carry the supervisor's authoritative state, independent of process memory ([Claude Code: Where state is stored](https://code.claude.com/docs/en/agent-view#where-state-is-stored)):

| Path | Purpose |
|------|---------|
| `~/.claude/daemon.log` | Supervisor log |
| `~/.claude/daemon/roster.json` | Running-sessions list for reconnect |
| `~/.claude/jobs/<id>/state.json` | Per-session state |

A session's short ID is its directory name under `~/.claude/jobs/`. `claude daemon status` reports reachability, PID, version, socket directory, and live session count.

## Why it works

The supervisor decouples three lifecycles with different churn rates. The agent loop is long-lived and expensive to restart with hot context. The terminal is short-lived and dies on shell exit. The binary version changes whenever the auto-updater runs. Glued into one process, closing the terminal kills the loop and a mid-task auto-update crashes it. The supervisor is the indirection that lets each evolve independently: the loop lives in a detached child, the terminal becomes a UI attached at will, and binary updates become in-place restart with roster-driven reconnect.

This is [session, harness, and sandbox separation](session-harness-sandbox-separation.md) projected onto local desktop tooling. Anthropic makes the same split for managed agents, deciding "to decouple what we thought of as the 'brain' (Claude and its harness) from both the 'hands' (sandboxes and tools that perform actions) and the 'session' (the log of session events)" ([Anthropic: managed agents](https://www.anthropic.com/engineering/managed-agents)) — the supervisor projects that same separation onto local processes.

The shape is not Claude-specific. The cocoindex semantic-code tool independently moved "from a monolithic per-session process to a persistent daemon with a thin CLI" with "auto-start on first use via Unix socket probe, version handshake on every connection for transparent upgrades" ([cocoindex: Building an Invisible Daemon](https://cocoindex.io/blogs/building-an-invisible-daemon/)). An open Codex request proposes the same shape — `codex run --bg`, `codex sessions list/attach/logs` — rejecting tmux/screen as adding "complexity and reduces portability" and nohup as offering "limited functionality without lifecycle management" ([openai/codex#3968](https://github.com/openai/codex/issues/3968)).

## When this backfires

The pattern is per-user desktop scoping. Several conditions invert the value:

- Single-session, single-machine usage. One agent in one terminal pays the daemon's roster, socket, and log complexity for zero parallelism benefit. It earns its complexity only at two-plus [concurrent sessions](../workflows/parallel-agent-sessions.md).
- Multi-user shared host. A per-user supervisor scales by user count, not session count. Shared dev boxes give you N supervisors competing for the same binary watch and memory budget. The architecture is deliberately not multi-tenant — see Codex's open multi-user gap: "to serve N users, you need N processes" ([openai/codex#14916](https://github.com/openai/codex/issues/14916)).
- Restricted environments where daemons cannot persist. Sandboxed CI runners and ephemeral containers where the supervisor cannot outlive the shell make roster and idle-eviction guarantees meaningless. The pattern presupposes the process survives the dispatcher's exit.
- Long-lived elevated permissions. A supervisor holding `bypassPermissions` across reattach has a wider blast radius than a per-invocation foreground session, because it outlives user attention.
- Power-cycle compared with sleep. "Shutting down or restarting your machine stops running background sessions, so they show as failed when you next open agent view" ([agent view docs](https://code.claude.com/docs/en/agent-view#sessions-show-as-failed-after-shutdown)). Sleep is recovered; shutdown is not.

## Why not just tmux or `systemd --user`

The steelman is "wrap the agent CLI in `tmux` or `systemd --user` and reuse decades of supervision tooling." Both ship pieces the supervisor reimplements — detach/reattach, restart policies, log capture, resource limits — but not the combination:

- Binary-on-disk watch with in-place restart and session reconnect. `systemd --user` can restart on file change via `systemd.path` units, but the agent-process and session-reconnect protocol remain your code.
- Idle eviction with pinning exemption. Two-tier ladder driven by one keystroke. tmux has no concept of session importance; `systemd --user` units are uniformly long-lived per unit.
- No-install assumption. `systemd --user` instances "will be killed as soon as the last session for the user is closed" by default and need `loginctl enable-linger` plus admin setup ([Arch Wiki: systemd/User](https://wiki.archlinux.org/title/Systemd/User)). A self-reviving per-user supervisor with a roster file resurrects on next CLI invocation with zero admin setup — required for a tool installed into `~/.local/bin/`.

The [Beyond process supervisors](https://catern.com/supervisors.html) essay makes the strongest opposite case: general-purpose supervisors often subsume responsibilities that belong elsewhere. A domain-specific supervisor for one process class avoids that trap by keeping its responsibilities narrow.

## Example

The shell-facing surface, taken from Claude Code's documented commands ([agent view: Manage sessions from the shell](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell)):

```bash
# Spawn a detached background session — supervisor starts if not running
claude --bg "investigate the flaky SettingsChangeDetector test"
# → backgrounded · 7c5dcf5d · investigate-flaky-test

claude daemon status        # reachability, PID, version, socket dir, session count
claude attach 7c5dcf5d      # reattach to a detached session
claude respawn --all        # roll every running session onto an updated binary
claude stop 7c5dcf5d        # supervisor exits when none remain
```

The supervisor is invisible until inspected. The user-facing surface is the agent view TUI and per-session commands; the daemon's existence is an implementation detail of "this session survives my shell exit and the next auto-update."

## Key Takeaways

- A per-user supervisor decouples three lifecycles — agent loop, user terminal, binary version — that the naive "terminal owns the agent" model conflates.
- Detached child processes plus an on-disk roster (`~/.claude/daemon/roster.json`) let the supervisor crash, restart, or be replaced without orphaning sessions.
- Idle eviction with pinning exemption is the resource-management lever; the user expresses "keep this hot" with one keystroke instead of a per-session lifetime API.
- Binary-on-disk watch is the rolling-upgrade lever: in-place restart through detached child sessions, no manual respawn step.
- The pattern is per-user desktop scoping — multi-user shared hosts, backend services, and ephemeral CI runners need different architecture.
- tmux and `systemd --user` ship pieces of supervision but not the combination that makes background agent sessions feel ambient.

## Related

- [Session, Harness, and Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the underlying three-primitive split the supervisor projects onto local desktop tooling
- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the broader execution-shape problem the supervisor solves at the desktop layer
- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — the same lifecycle-decoupling argument projected over a network boundary instead of a process boundary
- [Programmatic Agent Session Export via `claude agents --json`](../observability/claude-agents-json-session-export.md) — the read-only inventory primitive that pairs with the supervisor's roster
- [Parallel Agent Sessions Shift the Bottleneck from Writing](../workflows/parallel-agent-sessions.md) — the use case the supervisor exists to make ergonomic
