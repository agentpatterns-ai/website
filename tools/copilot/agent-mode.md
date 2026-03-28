---
title: "GitHub Copilot Agent Mode for AI Agent Development"
description: "Local, synchronous agentic execution that reads files, runs code, checks output, and iterates to fix errors autonomously inside the IDE."
aliases:
  - Copilot Agentic Mode
  - Agentic Mode
tags:
  - agent-design
  - copilot
---

# GitHub Copilot Agent Mode

> Local, synchronous agentic execution that reads files, runs code, checks output, and iterates to fix errors.

## How It Works

Agent mode transforms Copilot from a suggestion engine into an autonomous executor. When you submit a prompt in agent mode, Copilot [iterates across files and works through changes autonomously](https://github.com/newsroom/press-releases/agent-mode), proposes changes across multiple files, runs terminal commands, checks output, identifies errors, and loops back to fix them. It installs packages, runs tests, and migrates code without waiting for approval at each step.

Available in [VS Code](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode), and [generally available in JetBrains, Eclipse, and Xcode](https://github.blog/changelog/2025-07-16-agent-mode-for-jetbrains-eclipse-and-xcode-is-now-generally-available/).

## Planning Mode

For complex tasks, Copilot generates a [transparent plan](https://code.visualstudio.com/docs/copilot/agents/planning) outlining all steps before making changes. The plan supports structured reasoning and [progress tracking](../../agent-design/goal-monitoring-progress-tracking.md).

## Multi-File Editing

[Copilot Edits](https://docs.github.com/en/copilot/get-started/features) allows specifying a set of files and describing changes in natural language. Copilot proposes inline edits across files iteratively.

## Vision

[Feed Copilot a screenshot, mockup, or image](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/provide-visual-inputs) and it generates the UI code and implementation details.

## Example

This example demonstrates agent mode's edit-run-fix loop. Open a project in VS Code with Copilot, switch to agent mode in the Copilot Chat panel, and submit a prompt like:

```
Migrate the user authentication module from express-session to JWT. Update all routes, add token refresh logic, and fix any test failures.
```

Copilot responds by reading the affected files, proposing changes across the codebase, running the test suite, and looping back on failures — without asking for step-by-step confirmation. A representative trace looks like:

```
[agent] Reading src/auth/session.ts, src/routes/user.ts, tests/auth.test.ts
[agent] Proposing changes to 4 files
[agent] Running: npm test
[agent] 2 tests failed — fixing token expiry handling in src/auth/jwt.ts
[agent] Running: npm test
[agent] All tests passing
```

For complex migrations, enable planning mode first — Copilot shows the full plan before touching any files. In VS Code, this is available via the `#plan` directive in the prompt:

```
#plan Migrate express-session to JWT across the auth module
```

Review the plan, approve, and then Copilot executes all steps.

## Key Takeaways

- Agent mode is the local, synchronous counterpart to the async coding agent
- It iterates autonomously: edit, run, check, fix — without step-by-step approval
- Planning mode adds transparency for complex multi-step tasks
- Generally available across VS Code, JetBrains, Eclipse, and Xcode

## Related

- [Coding Agent](coding-agent.md)
- [Custom Agents & Skills](custom-agents-skills.md)
- [Agent Composition Patterns](../../agent-design/agent-composition-patterns.md)
- [MCP Integration](mcp-integration.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Copilot Extensions](copilot-extensions.md)
- [Copilot Memory](copilot-memory.md)
- [GitHub Copilot SDK](copilot-sdk.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Agent HQ (Multi-Agent Platform)](agent-hq.md)
