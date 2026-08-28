---
title: "Multi-Client Session Attachment: One Session, Many Clients"
term: "Multi-Client Session Attachment"
description: "Several front ends attach to one live agent session at once. The host holds the only authoritative state, and client-contributed tools stay behind."
tags:
  - agent-design
  - tool-agnostic
  - reliability
aliases:
  - multi-client agent session
  - shared agent session
  - attachable agent front end
last_reviewed: 2026-08-27
maturity: emerging
---

# Multi-Client Session Attachment: One Session, Many Clients

> Several clients attach to one running agent session, and ordered updates from the host keep every view in step.

Multi-client session attachment means the agent session runs in a host process that "owns agent sessions independently of the clients that display and control them," holding session state as "the source of truth" ([VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)). An editor window, a separate agents window, and a browser can each attach to that one session at the same time. Every attached client can "observe progress, contribute actions, approve tool calls, or cancel work" ([VS Code, 2026-08-26](https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture)).

## Conditions this depends on

Three conditions carry the pattern, and the first two are easy to assume wrongly.

The host has to outlive the clients for real, not nominally. VS Code's own documentation limits the local case: "For local sessions, VS Code must remain running because it manages the local Agent Host" ([VS Code, 2026-08-26](https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture)). Only the remote mode, where "the host can run next to the workspace on another machine while clients connect from elsewhere," separates the two lifetimes ([VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)).

The session must not depend on tools that a single client supplies. Clients "can also contribute tools based on their own capabilities" ([VS Code, 2026-08-26](https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture)), and those tools leave when that client does.

The wire format has to be one you can afford to track. The Agent Host Protocol is MIT-licensed with client implementations in six languages, and VS Code is "the reference AHP server implementation" ([microsoft/agent-host-protocol](https://github.com/microsoft/agent-host-protocol)). It is also pre-1.0: v0.8.0 shipped on 2026-08-18 carrying a type rename and a session-status behavior change ([AHP releases](https://github.com/microsoft/agent-host-protocol/releases)).

## What synchronizes and what does not

| Travels with the session | Stays with one client |
|---|---|
| Turn state, progress, and the session log | Tools an extension contributes in that window |
| Actions, tool-call approvals, and cancellations from any client | Capabilities only that client can reach |

Extension tools are the sharp edge. "Tools from extensions are only available in chats in an editor window where the extension is running" ([VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)). Reattach from a browser and the session keeps its full history but loses part of its tool set, with nothing in the transcript marking the change.

## Why it works

Convergence comes from making updates ordered and deterministic instead of harness-specific. The host translates each harness's backend events into one display-ready state shape plus a sequence of actions, and "shared reducers apply those actions consistently, so an editor, the Agents window, and a browser client converge on the same view without each client having to understand the harness's SDK or session model" ([VS Code, 2026-08-26](https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture)). Clients therefore need no agreement with each other: each one replays the same ordered actions and lands in the same place. That same translation layer is why the protocol stays agent-neutral: Copilot runs "powered by the GitHub Copilot SDK, which manages its runtime as a child process," while Claude "loads Anthropic's Claude Agent SDK. Its adapter maps sessions, tools, permissions, and subagents into AHP" (same source). Two different agent runtimes drive identical clients.

## When this backfires

- Local-only work. The host dies with the application, so you gain window-level survival and pay for a second process anyway.
- Sessions built on extension tools. The tool set narrows when the contributing window closes, and the next turn degrades with no error naming the cause.
- Third-party clients pinned against a moving spec. Renames land in AHP minor releases, so six client SDKs cost more to track than the MIT license suggests.
- Treating attached clients as review. Sabotage survived 94% of sessions with no monitor and 63% with one, and in the 16 sessions where the monitor alerted correctly it still survived 9 ([arXiv:2606.05647v1](https://arxiv.org/abs/2606.05647v1), 107 sessions). Extra windows add views, not scrutiny.
- Short interactive tasks. A session that never detaches collects none of the benefit.

## Key Takeaways

- One host process holds the authoritative session state; clients are views that attach and detach without owning anything
- Ordered actions through shared reducers make an editor, an agents window, and a browser agree, and keep the protocol agent-neutral across the Copilot and Claude SDKs
- Client-contributed tools are the exception to portability: they leave with the client that supplied them, and the session does not announce the loss
- Local hosts die with the editor application; only the remote mode separates host and client lifetimes
- AHP is MIT-licensed and pre-1.0 at v0.8.0 (2026-08-18), with renames shipping in minor releases
- Attaching more clients does not buy oversight: developers accepted the sabotaged code in 9 of the 16 sessions where a monitor alerted correctly

## Related

- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — the durability half: what survives a disconnect, and the SSH, tunnel, and cloud-worker transports
- [Long-Running Agents: Durability, Checkpoints, and Resumability](long-running-agents.md) — the operational shape that makes a host-owned session worth running
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive split these clients attach to
- [Editor and Manager Surface Separation in Agent IDEs](editor-manager-surface-separation.md) — why attached clients serve different attention modes instead of duplicating one panel
- [Per-User Supervisor Process for Background Agent Sessions](per-user-supervisor-process.md) — the daemon form of keeping a session alive with no client attached
