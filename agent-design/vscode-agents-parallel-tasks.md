---
title: "VS Code Agents App: Agent-Native Parallel Task Execution"
description: "Run multiple agent sessions simultaneously across projects in VS Code's Agents app — each session inherits workspace config and can interact with background processes via send_to_terminal."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - VS Code Agents App
  - Agent-Native Parallel Execution
---

# VS Code Agents App: Agent-Native Parallel Task Execution

> The VS Code Agents app runs multiple agent sessions in parallel across projects without occupying the main editor window — each session inherits workspace custom instructions and MCP servers automatically.

## Agent-Native vs Chat-Native

Chat-native IDEs attach agents to the editor's conversation panel: one active task at a time, waiting for completion before starting the next. This creates a bottleneck for compound tasks with independent subtasks.

The [VS Code Agents app](https://code.visualstudio.com/updates/v1_115) (introduced in VS Code 1.115, April 2026, VS Code Insiders preview; see also [VS Code multi-agent development overview](https://code.visualstudio.com/blogs/2026/02/05/multi-agent-development)) provides a companion panel where multiple agent sessions run headlessly in parallel. You submit tasks, switch back to your editor, and check results when sessions complete. The Agents app is not a better chat panel — it is a task execution surface.

## How the Agents App Works

Each session in the Agents app is an independent agent context:

- **Workspace config inheritance** — custom instructions and MCP server configuration propagate automatically from workspace settings. You do not configure each session separately; all sessions operate under the same behavioral constraints as the main editor.
- **Project isolation** — sessions can target different projects simultaneously. A refactor in one repo, a documentation pass in another, and a test-writing run in a third can all execute at the same time.
- **Headless execution** — sessions run without requiring the editor's foreground. You observe status in the Agents panel; the main editor remains unblocked.

## The send_to_terminal Tool

Headless agents block when they need an already-running process — a dev server, a file watcher, a build daemon. Without a way to interact with these, agents must start and stop them on every run or assume they are already running.

The `send_to_terminal` tool solves this. Sessions can send commands to terminal processes as part of their execution — start a dev server, trigger a build — without the user switching context. The process dependency becomes an agent task, not a human precondition. See [Terminal Tools for Agents: send_to_terminal and Background Interaction](../tool-engineering/send-to-terminal-background-interaction.md) for the full terminal I/O model including `backgroundNotifications`.

An experimental companion setting, `chat.tools.terminal.backgroundNotifications`, alerts agents when background commands complete or require input — eliminating manual polling via `get_terminal_output`. Enable it via VS Code settings.

## Parallel Fan-Out Pattern

The Agents app enables a practical fan-out workflow:

```
Compound task (e.g., "audit and refactor the auth module")
    ├── Session A: security audit (auth/session.py)
    ├── Session B: performance profiling (auth/tokens.py)
    └── Session C: update tests (tests/test_auth.py)
```

Each session operates on a scoped slice of work. They do not share context — no risk of one session's reads or decisions polluting another's. You collect results when all three complete, then apply or discard independently.

This differs from three Claude Code processes in three terminals: the Agents app sessions share workspace config, appear in a single management panel, and can interact with shared terminal processes via `send_to_terminal`.

## Cursor Comparison

Cursor's Agents Window introduced the same concept — a dedicated sidebar for concurrent agent tasks. The VS Code Agents app follows that model with workspace-settings integration as the distinguishing property: sessions inherit custom instructions and MCP servers automatically, reducing per-session setup cost. Cursor propagates custom instructions via project-level Rules files (`.cursor/rules/*.mdc`) and user-level settings, but MCP server configuration is not automatically inherited by background agent sessions in the same way — each session requires explicit tool configuration.

## Why It Works

Headless parallel sessions eliminate the two dominant sources of serial bottleneck in chat-native IDEs: the editor foreground lock (only one task occupies the panel at a time) and per-session configuration overhead (each new context requires manual setup). The Agents app removes both: sessions run detached from the editor window, so the foreground is never blocked, and workspace config inheritance means all sessions start with the same custom instructions and MCP servers already in scope. The result is that task latency becomes parallel rather than cumulative — three independent subtasks that each take ten minutes complete in ten minutes, not thirty.

The `send_to_terminal` integration closes a second bottleneck: background agents previously had to either start fresh processes (incurring cold-start cost) or assume a human had already set up required daemons. By letting agents interact with running terminals, the dependency on human precondition work is eliminated.

## Limitations

- Available in VS Code Insiders only as of the 1.115 preview — stable release availability is not yet confirmed
- Maximum concurrent sessions is not documented
- The Agents app targets discrete, scope-bounded tasks; open-ended exploratory sessions still fit the main chat panel better

## Key Takeaways

- The Agents app is a headless task execution surface, not an extended chat panel — the design intention is parallel fan-out, not conversational turn-by-turn work
- Workspace config inheritance (custom instructions + MCP servers) is the practical advantage over ad-hoc multi-terminal setups — sessions are pre-configured, not blank contexts
- `send_to_terminal` closes the background-process gap that makes headless agents brittle in real dev environments
- Fan-out tasks work best when subtasks are genuinely independent — shared state between sessions reintroduces the serialization bottleneck the Agents app is designed to avoid

## Related

- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md) — structural patterns for distributing work across agents
- [Specialized Agent Roles](specialized-agent-roles.md) — assigning distinct responsibilities to parallel sessions to avoid redundant output
- [Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md) — criteria for deciding which subtasks warrant agent delegation
- [Steering Running Agents: Mid-Run Redirection and Follow-Ups](steering-running-agents.md) — how to redirect a session mid-execution without discarding accumulated context
- [Harness Engineering](harness-engineering.md) — runtime infrastructure design for agent execution environments
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md) — the protocol behind MCP server configuration that sessions inherit automatically
