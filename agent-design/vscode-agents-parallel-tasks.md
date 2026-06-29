---
title: "VS Code Agents App: Agent-Native Parallel Task Execution"
term: "VS Code Agents App"
description: "Run multiple agent sessions simultaneously across projects in VS Code's Agents app — each session inherits workspace config and can interact with background processes via send_to_terminal."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - VS Code Agents App
  - Agent-Native Parallel Execution
last_reviewed: 2026-06-12
maturity: adopted
---

# VS Code Agents App: Agent-Native Parallel Task Execution

> The VS Code Agents app runs multiple agent sessions in parallel across projects, each inheriting workspace custom instructions and MCP servers automatically.

## Agent-native vs chat-native

Chat-native IDEs attach agents to the editor's conversation panel. You run one task at a time and wait for it to finish before you start the next. This creates a bottleneck for compound tasks that hold independent subtasks.

The [VS Code Agents app](https://code.visualstudio.com/updates/v1_115) (introduced in VS Code 1.115, April 2026, VS Code Insiders preview; see also the [VS Code multi-agent development overview](https://code.visualstudio.com/blogs/2026/02/05/multi-agent-development)) gives you a companion panel where multiple agent sessions run headlessly in parallel. You submit tasks, switch back to your editor, and check results when sessions finish. The Agents app is not a better chat panel. It is a task execution surface.

## How the Agents app works

Each session in the Agents app is an independent agent context:

- Workspace config inheritance: custom instructions and MCP server configuration carry over automatically from workspace settings. You do not configure each session separately. Every session runs under the same behavioral constraints as the main editor.
- Project isolation: sessions can target different projects at the same time. A refactor in one repo, a documentation pass in another, and a test-writing run in a third can all run at once. This is the [fan-out shape](agent-composition-patterns.md) applied across projects.
- Headless execution: sessions run without the editor's foreground. You watch status in the Agents panel, and the main editor stays unblocked.

## The send_to_terminal tool

Headless agents block when they need a process that is already running, such as a dev server, a file watcher, or a build daemon. Without a way to reach these processes, agents must start and stop them on every run or assume they are already running.

The `send_to_terminal` tool solves this. Sessions can send commands to terminal processes as they run, such as starting a dev server or triggering a build, without you switching context. The process dependency becomes an agent task, not a human precondition. See [Terminal Tools for Agents: send_to_terminal and Background Interaction](../tool-engineering/send-to-terminal-background-interaction.md) for the full terminal I/O model, including `backgroundNotifications`.

An experimental companion setting, `chat.tools.terminal.backgroundNotifications`, alerts agents when background commands finish or need input. This removes manual polling through `get_terminal_output`. Enable it in VS Code settings.

## Parallel fan-out pattern

The Agents app supports a practical fan-out workflow:

```
Compound task (e.g., "audit and refactor the auth module")
    ├── Session A: security audit (auth/session.py)
    ├── Session B: performance profiling (auth/tokens.py)
    └── Session C: update tests (tests/test_auth.py)
```

Each session works on a scoped slice of work. The sessions do not share context, so one session's reads or decisions cannot pollute another's. You collect results when all three finish, then apply or discard each one on its own.

This differs from three Claude Code processes in three terminals. The Agents app sessions share workspace config, appear in a single management panel, and can reach shared terminal processes through `send_to_terminal`.

## Cursor comparison

Cursor's [Agents Window](../tools/cursor/agents-window.md) introduced the same concept: a dedicated sidebar for concurrent agent tasks. The VS Code Agents app follows that model, and workspace-settings integration is what sets it apart. Sessions inherit custom instructions and MCP servers automatically, which cuts per-session setup cost. Cursor passes custom instructions through project-level Rules files (`.cursor/rules/*.mdc`) and user-level settings, but background agent sessions do not inherit MCP server configuration the same way. Each session needs explicit tool configuration.

## Why it works

Headless parallel sessions remove the two main sources of serial bottleneck in chat-native IDEs. The first is the editor foreground lock, where only one task holds the panel at a time. The second is per-session configuration, where each new context needs manual setup. The Agents app removes both. Sessions run detached from the editor window, so the foreground is never blocked, and workspace config inheritance means every session starts with the same custom instructions and MCP servers already in scope. Task latency becomes parallel rather than cumulative. Three independent subtasks that each take ten minutes finish in ten minutes, not thirty.

The `send_to_terminal` integration closes a second bottleneck. Background agents used to either start fresh processes, which costs cold-start time, or assume a human had already set up the required daemons. Letting agents reach running terminals removes the dependency on human precondition work.

## Limitations

- Available in VS Code Insiders only as of the 1.115 preview. Stable release availability is not yet confirmed.
- The maximum number of concurrent sessions is not documented.
- The Agents app targets discrete, scope-bounded tasks. Open-ended exploratory sessions still fit the main chat panel better.

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
