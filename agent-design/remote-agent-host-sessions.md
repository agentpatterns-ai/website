---
title: "Remote Agent Host Sessions over SSH and Dev Tunnels"
description: "Run the agent loop on a remote host whose lifecycle is decoupled from the client editor — SSH attach, dev tunnel reverse, or cloud worker — so the session survives laptop sleep, network drops, and editor restarts."
tags:
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - remote agent host
  - remote agent execution
  - agent host over SSH
last_reviewed: 2026-06-02
maturity: established
---

# Remote Agent Host Sessions over SSH and Dev Tunnels

> A remote agent host is an agent loop running in a process on a remote machine, attached to over SSH or a dev tunnel; the host owns the session log so disconnects, sleeps, and editor restarts are UI events rather than state events.

The pattern applies when three conditions hold: the host is a process or service whose lifecycle is decoupled from the client editor, the tunnel auth is account-bound (not anonymous), and the team owns the operational cost of keeping that host alive. Without all three, [a cloud agent](cloud-agent-session-bootstrap.md) or a [tmux-wrapped local CLI](#example) is the lighter choice.

## What the pattern is not

| Pattern | Where the loop runs | What survives disconnect |
|---------|--------------------|--------------------------|
| Cloud agent dispatch | Vendor cloud | Vendor manages |
| [Remote session control](remote-session-control.md) | Local workstation | Local-loop output, streamed to client |
| Remote agent host (this pattern) | Remote host you operate | Host-owned session log |
| Plain SSH agent | Client-attached process | Nothing — process dies on disconnect |

This is [Session Harness Sandbox Separation](session-harness-sandbox-separation.md) — durable session, stateless harness, disposable sandbox — projected across a network boundary.

## Three transports

- SSH attach. The client uses `~/.ssh/config` or `user@host`; "the Agents window automatically installs and starts the VS Code CLI on the remote machine" ([VS Code Agents window docs](https://code.visualstudio.com/docs/copilot/agents/agents-window)), which runs the agent host process. No inbound port beyond `sshd`, and the host outlives the editor.
- Dev tunnel. A pre-started `code tunnel` exposes an outbound reverse tunnel; "both hosting and connecting to a tunnel requires authentication with the same Github or Microsoft account on each end" with AES-256-CTR over SSH ([VS Code Remote Tunnels docs](https://code.visualstudio.com/docs/remote/tunnels)).
- Cloud worker. Cursor's self-hosted cloud agents invert the network shape — "a worker process connects outbound via HTTPS to Cursor's cloud—no inbound ports, firewall changes, or VPN tunnels required" — with inference in the cloud and tool execution on the worker ([Cursor: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)).

All three colocate the agent loop with the filesystem it edits and put session state on something that outlives the client.

## State location matters

Three places state can live; only the first delivers the durability claim:

| Location | What disconnect costs | Reconnect semantics |
|----------|----------------------|---------------------|
| Remote host (durable) | Nothing — host keeps stepping | Re-attach or replay-from-log |
| Tunnel process | In-flight turn | Re-run the turn |
| Client editor | Whole session | Start fresh |

AHP keeps state authoritative on the host with monotonic `serverSeq` numbers; clients carry `lastSeenServerSeq` and the server replays a 100-action buffer on reconnect or returns a fresh snapshot for larger gaps ([opencode AHP plugin implementation](https://github.com/maxious/opencode-plugin-agent-host-protocol)). Cursor's self-hosted cloud agent worker takes the inverse approach with outbound HTTPS only, no inbound ports or VPN tunnels ([Cursor: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)).

## Why it works

Disconnects only cost work when the disconnected component holds load-bearing state. Putting the agent loop on a host whose lifecycle is independent of the editor relocates the turn pointer, tool-call queue, and permission-decision state to a process the editor does not own — so a closed laptop is a UI event, not a state event. Anthropic documents the underlying mechanism: "Because the session log sits outside the harness, nothing in the harness needs to survive a crash. When one fails, a new one can be rebooted with `wake(sessionId)`, use `getSession(id)` to get back the event log, and resume from the last event" ([Anthropic Managed Agents](https://www.anthropic.com/engineering/managed-agents)). The same lever is why a tmux-wrapped CLI survives detach — the multiplexer is the lightweight equivalent of a vendor-managed agent host. The transport (SSH, dev tunnel, outbound HTTPS) is just how the client reattaches; the durability comes from the host-owns-state split.

## When this backfires

- The agent host process is the editor. A VS Code window on the remote dies when the editor crashes or restarts; "the remote machine will only be reachable through a tunnel while VS Code remains running there" ([VS Code Remote Tunnels docs](https://code.visualstudio.com/docs/remote/tunnels)). Durability needs a service or tmux-wrapped process, not the editor itself.
- Anonymous dev tunnels. A discoverable tunnel URL with auto-approval can let an unauthenticated visitor trigger AI-assisted command execution under the host's credentials — documented by Microsoft ([VS Code Remote Tunnels docs](https://code.visualstudio.com/docs/remote/tunnels)) and detected in the wild ([Elastic Security: VScode Remote Tunnel rule](https://www.elastic.co/guide/en/security/8.19/attempt-to-establish-vscode-remote-tunnel.html); [The Hacker News, 2024-12](https://thehackernews.com/2024/12/hackers-weaponize-visual-studio-code.html)).
- State trapped in the tunnel. Microsoft's own self-host testing issue lists "remote connection drops lacking recovery mechanisms" and "turns that fail to resume after reconnection" as known failure modes as of 2026-05 ([microsoft/vscode#311105](https://github.com/microsoft/vscode/issues/311105)).
- Cancellation across two hops is incomplete. The same issue flags "turn never finishes, can't be cancelled" — Ctrl-C in the client does not reliably interrupt a model call in the host or a tool execution in a sandbox.
- Short-horizon interactive work. A sub-30-minute task does not pay the operational cost of running a host process.
- Regulated environments restrict outbound tunnels. SOC2 or FedRAMP boundaries often deny dev tunnels and exposed `sshd`, so on-host execution wrapped in tmux may be the only viable transport.
- A cloud runner is the better fit. When the agent does not need local filesystem, local MCP servers, or local network reachability, a [cloud agent](cloud-agent-session-bootstrap.md) sidesteps the host operational cost entirely.

## Example

The tmux-on-a-bastion form costs less than half a screen of config and gets most of the durability:

```bash
# On the remote box (a bastion, a dev VM, a workstation in the office)
tmux new-session -d -s claude 'claude --dangerously-skip-permissions'

# From the laptop, before closing the lid
ssh bastion -t 'tmux attach -t claude'

# Lid closes, train ride, hotel WiFi — reattach later
ssh bastion -t 'tmux attach -t claude'
```

The multiplexer is the agent host — lifecycle independent of `sshd`, session log in tmux scrollback plus whatever the harness persists to disk, reattach is `tmux attach`. tmux is "the perfect runtime for AI agent orchestration — sandboxed panes, session persistence, real-time visibility" ([How tmux Became the Runtime for AI Agent Teams](https://dev.to/battyterm/how-tmux-became-the-runtime-for-ai-agent-teams-gmi)).

VS Code 1.121's Agents window ships the same shape behind AHP: "Sessions keep running on the remote even when you disconnect, so you can close your laptop and check back later" ([VS Code Agents overview](https://code.visualstudio.com/docs/copilot/agents/overview)). Cursor's cloud-worker form moves inference off-host and keeps the worker on-host — same state-survives-client property, outbound HTTPS only ([Cursor: Self-Hosted Cloud Agents](https://cursor.com/blog/self-hosted-cloud-agents)).

## Key Takeaways

- A remote agent host is an agent loop in a process whose lifecycle is decoupled from the client editor — disconnects become UI events because the session state is host-owned, not client-owned
- Three transports cover the design space: SSH attach to a remote host process, dev tunnel reverse from `code tunnel` plus the agent host, outbound-HTTPS worker reporting to a cloud control plane
- State location decides whether the pattern delivers — on the remote host (durable), in the tunnel (lost on drop), or in the client (lost on disconnect)
- AHP's Redux-like sync (`serverSeq` + 100-action replay buffer) is the reference reconnect protocol for editor-attached clients; outbound-HTTPS workers with server-pushed events are the cloud-runner equivalent; tmux is the low-tech form
- The pattern is Qualified: lifecycle-decoupled host, account-bound tunnel auth, and operational ownership of the host are all required — without them, prefer a cloud agent or accept that a plain SSH session loses state on disconnect
- Anonymous dev tunnels under auto-approval are an active attack surface; cancellation propagation across two hops is a known incomplete area in 2026

## Related

- [Remote Session Control for Local CLI Agents](remote-session-control.md) — control-plane sibling: the loop stays local, the client steers from a phone or browser
- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the operational shape that makes the host-owns-state split worth running
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive architecture this pattern projects across a network boundary
- [Cloud-Agent Session Bootstrap: Cached Install plus Per-Session Start](cloud-agent-session-bootstrap.md) — the cloud-runner alternative when no local execution context is required
- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the decision frame for when to outsource the host versus operate it
