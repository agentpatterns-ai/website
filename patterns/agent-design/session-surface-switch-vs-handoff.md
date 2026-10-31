---
title: "Surface Switch or Harness Handoff: What Each Preserves"
term: "Surface Switch vs. Harness Handoff"
description: "Continuing an agent session in another interface keeps its harness, workspace, and worktree. A handoff keeps the conversation and can re-scope the tools."
tags:
  - agent-design
  - copilot
  - reliability
aliases:
  - session surface switch
  - continue a session in another interface
  - harness handoff
last_reviewed: 2026-10-20
maturity: emerging
---

# Surface Switch or Harness Handoff: What Each Preserves

> A surface switch keeps the session's harness, workspace, and worktree. A harness handoff keeps the conversation and can re-scope the tools.

Two operations continue an agent session, and they preserve different things. A surface switch opens the same live session in another interface. A handoff continues the same work under a different agent configuration. Both leave a transcript that reads as one unbroken conversation, so pick the move before you make it.

## When each move applies

A surface switch is available for Agent Host-backed sessions, which means Copilot and Claude, plus Codex through its experimental integration. Those sessions are reachable from both the Chat view and the Agents window, and "Switching between these interfaces doesn't create a session, fork the conversation, or change its harness, workspace, or worktree" ([VS Code sessions and chats documentation](https://code.visualstudio.com/docs/agents/concepts/sessions)). VS Code also discovers local sessions from Copilot CLI, the GitHub Copilot app, Claude Code, and Codex. A discovered session stays at arm's length until you write to it: it "is external until you send a message from VS Code" (same source).

A handoff applies when the next part of the task wants a different configuration. It "continues an ongoing task with a different harness or execution environment and carries the conversation history and context with it. The tools, permissions, and models might change because the new configuration provides different capabilities" ([VS Code agent harness documentation](https://code.visualstudio.com/docs/agents/run/agent-harnesses)). The destination governs what the agent can then do. For a handoff started from a Local harness session through the Session Target dropdown, the destination session "uses the selected harness's tools, permissions, and models" ([VS Code sessions and chats documentation](https://code.visualstudio.com/docs/agents/concepts/sessions)). Handoffs start from Local harness sessions. Copilot, Claude, and experimental Codex sessions can receive them but "can't hand off to another harness or to a cloud session" ([VS Code agent harness documentation](https://code.visualstudio.com/docs/agents/run/agent-harnesses)).

## What each one preserves

| | Surface switch | Harness handoff |
|---|---|---|
| Conversation history | Kept | Kept |
| Harness, workspace, worktree | Unchanged | May change |
| Permissions and models | Not documented | Re-scoped to the destination |
| Client-contributed tools | Held only while that client stays connected | May change with the destination configuration |

## Why it works

The split follows from where each thing is stored. The Agent Host is "the process that runs supported harnesses and owns their sessions, independently of the clients displaying them", and "The host is the source of truth. Each client subscribes to URI-addressed channels for resources such as sessions, chats, terminals, and changesets. The client receives an initial state snapshot followed by ordered actions" ([VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)). A second client attaches to the session state owned by the host; it does not create a separate session. Tools travel the opposite direction. Connected clients contribute them, the host "adds those definitions to the session and routes each tool call back to the contributing client", and "These tools require that client to remain connected" (same source). The Agent Host holds session state, and connected clients contribute tools.

## When this backfires

- Local and extension-host sessions. The move does not exist for them. "Extension-host sessions are closely integrated with the current editor window and its extensions. This integration comes with a tradeoff: the window owns the session, so closing the window stops ongoing work, and you can't continue the session from another interface" ([VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host)). Write a [handoff summary](handoff-skill-context-transfer.md) and start fresh instead.
- Work that depends on a canvas. "Canvases aren't supported in Claude, Codex, extension-host Local sessions, remote Agent Host sessions, browser clients, or auxiliary windows" ([VS Code canvases documentation](https://code.visualstudio.com/docs/agents/run/canvases)). The list includes browser clients and remote Agent Host sessions, which are the hops you make to reach another machine.
- Sessions leaning on an extension-contributed or browser tool. [Multi-Client Session Attachment](multi-client-session-attachment.md) describes the tools that require a connected client.
- Enterprise-managed environments. "Enterprise-managed sandbox or permission settings might automatically move a Local session to the Copilot harness so the Agent Host can enforce the policy" ([VS Code agent harness documentation](https://code.visualstudio.com/docs/agents/run/agent-harnesses)), and that move archives the original Local session as read-only. The harness changed without you choosing it.
- A long exploratory session with one small edit left. A chat's conversation history "contributes to the language model's context window" ([VS Code sessions and chats documentation](https://code.visualstudio.com/docs/agents/concepts/sessions)), so carrying all of it spends budget on finished work. Where supported, a new nested session starts blank and uses the parent's folder or worktree by default. Supported harnesses can select another folder or worktree ([VS Code sessions and chats documentation](https://code.visualstudio.com/docs/agents/concepts/sessions)).

## Example

GitHub's walkthrough for continuing a Copilot app session in VS Code calls the move handing the session off. It behaves like a surface switch in what it carries over: the worktree, the branch, and the conversation. The associated worktree carries the agent's edits. "VS Code opens the project using the worktree associated with the session". A hand edit therefore builds on the agent's diff. "Because VS Code opened the worktree and branch associated with the session, pushing the branch updates the pull request already tracking that work" ([GitHub Blog, 2026-10-19](https://github.blog/ai-and-ml/github-copilot/how-to-continue-a-github-copilot-app-session-in-vs-code/)). The article is explicit that no summary step is needed: "You do not need to summarize that history or copy it into a new chat before moving to VS Code" (same source). For a fresh session, write a handoff summary instead.

## Key Takeaways

- A surface switch preserves harness, workspace, and worktree; client-contributed tools depend on their client staying connected
- A handoff preserves the conversation, and the destination configuration then supplies the tools, permissions, and models
- The Agent Host holds session state, and clients contribute capability, and that asymmetry decides who keeps what
- The Copilot app path carries the worktree and branch, so a push lands on the pull request already tracking the session
- Local and extension-host sessions cannot change surface at all, and canvases are unsupported in browser clients, remote Agent Host sessions, or auxiliary windows
- An enterprise policy can move a Local session to the Copilot harness by itself and archive the original read-only

## Related

- [Multi-Client Session Attachment: One Session, Many Clients](multi-client-session-attachment.md) — the host-and-clients architecture this decision rests on
- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — the transports that carry a session off the machine you are sitting at
- [Handoff Skill: Structured Context Transfer Between Agent Sessions](handoff-skill-context-transfer.md) — the write-a-summary route when a fresh session is the better buy
- [Session Recap: Goal-Shaped Handoff at Context Boundaries](session-recap.md) — the goal-shaped artifact for boundaries a live session cannot cross
- [Delegation Scoping: Session Relationship and Workspace](delegation-scoping-session-and-workspace.md) — the dispatch-time version of the same two-choice split
