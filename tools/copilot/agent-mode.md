---
title: "GitHub Copilot Agent Mode for AI Agent Development"
description: "Local, synchronous agentic execution that reads files, runs code, checks output, and iterates to fix errors autonomously inside the IDE."
aliases:
  - Copilot Agentic Mode
  - Agentic Mode
tags:
  - agent-design
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-07-28
status: current
---

# GitHub Copilot Agent Mode

> Local, synchronous agentic execution that reads files, runs code, checks output, and iterates to fix errors.

## How it works

Agent mode turns Copilot from a suggestion engine into an autonomous executor. When you submit a prompt, Copilot [iterates across files and works through changes autonomously](https://github.com/newsroom/press-releases/agent-mode). It proposes changes across multiple files, runs terminal commands, checks output, finds errors, and loops back to fix them. It installs packages, runs tests, and migrates code without waiting for your approval at each step.

Agent mode runs in [VS Code](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode) and is [generally available in JetBrains, Eclipse, and Xcode](https://github.blog/changelog/2025-07-16-agent-mode-for-jetbrains-eclipse-and-xcode-is-now-generally-available/).

## Planning mode

For complex tasks, Copilot generates a [plan that lists all steps](https://code.visualstudio.com/docs/copilot/agents/planning) before it makes changes. The plan supports structured reasoning and [progress tracking](../../patterns/agent-design/goal-monitoring-progress-tracking.md).

## Multi-file editing

[Copilot Edits](https://docs.github.com/en/copilot/get-started/features) lets you name a set of files and describe changes in plain language. Copilot then proposes inline edits across those files, one round at a time.

## Vision

[Feed Copilot a screenshot, mockup, or image](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/provide-visual-inputs) and it generates the UI code and implementation details.

## Inline agent mode (JetBrains)

Inline agent mode hosts the same agent toolkit — workspace search, multi-file edits, terminal commands, and editor lint and compile error reads ([GitHub Changelog 2025-05-19](https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/)) — in the JetBrains inline chat popover instead of the chat tool window, in public preview since April 24, 2026 ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)). Open inline chat with `Shift+Ctrl+I` (Windows) or `Shift+Cmd+I` (Mac), right-click and select **Open Inline Chat**, or click the gutter icon, then switch the popover to agent mode. On Copilot Business and Enterprise, an admin must enable the **Editor preview features** policy before the surface appears.

| Dimension | Inline agent mode | Chat-panel agent mode |
|-----------|------------------|----------------------|
| Invocation | `Shift+Ctrl/Cmd+I` from the editor | Tool window |
| Anchoring | Active selection / cursor / file | Workspace, last-active file |
| Plan and diff render area | Inline popover | Full chat tool window |
| Best fit | Selection-scoped edits, quick fixes against editor errors | Multi-file changes, long plans, terminal output review |

The trade is invocation cost against legibility: inline shortens the path from looking at code to having an agent act on it, while the chat panel keeps plans, file lists, and terminal output readable as a run grows — switch surfaces once a run outgrows the popover. The same release shipped **Global Auto Approve** settings (`Settings > GitHub Copilot > Chat > Auto Approve`) that approve every tool call across all workspaces, including destructive ones; combined with low-friction inline invocation this removes the [confirmation gate](../../security/human-in-the-loop-confirmation-gates.md) for agent-initiated changes, so keep it off outside sandboxed workspaces ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)).

## Why it works

Per [GitHub's agent mode overview](https://github.blog/ai-and-ml/github-copilot/agent-mode-101-all-about-github-copilots-powerful-mode/), the loop works because the language model reasons about the next step and issues tool calls to gather information or act — reading files, editing, running terminal commands. After each edit or command, agent mode [inspects syntax errors, terminal output, test results, and build failures to decide how to course-correct](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode). Deterministic feedback signals from the compiler, linter, and tests anchor the loop. The more structured the signals, the faster it converges.

## When this backfires

Agent mode degrades when the feedback loop is weak or the task exceeds its context window:

- Large refactors across many files. GitHub's own guidance positions agent mode for [low-to-medium complexity changes in well-tested repositories and small refactors — not massive rewrites, cross-repo changes, or codebases with little test coverage](https://github.blog/developer-skills/github/less-todo-more-done-the-difference-between-coding-agent-and-agent-mode-in-github-copilot/). Work one module at a time, and avoid "rewrite the app in one shot."
- Trial-and-error loops. When the agent cannot reconcile a failing test, it can [repeatedly retry without convergence](https://github.com/orgs/community/discussions/182145), burning credits on tokens that buy no progress, before stalling. Set a max-retry ceiling, or hand off to ask or edit mode on stalls.
- First-step assumption drift. A wrong assumption in step one propagates, so every later edit, test, and fix inherits it. Planning mode reduces this but does not eliminate it.
- Rate limits and context ceilings. Agent mode consumes [GitHub AI credits, metered by the tokens each interaction uses](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), and rate-limits the most powerful models, so sustained work across dozens of files is costly. On April 20, 2026, GitHub [paused new signups for Pro, Pro+, and Student plans, added session and weekly token-based limits, and removed Opus models from the Pro tier](https://github.blog/news-insights/company-news/changes-to-github-copilot-individual-plans/) — citing agent-mode workloads as the cause. That direction became the whole model on June 1, 2026, when GitHub [retired premium requests](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/what-changed-with-billing): budget tokens, not request counts. To ease that budgeting, GitHub made [Auto mode in Copilot Chat generally available to all users on June 17, 2026, auto-selecting the model per request](https://github.blog/changelog/2026-06-17-auto-mode-in-copilot-chat-available-for-all-users) rather than pinning one high-rate model for every turn.

## Example

This example shows agent mode's edit-run-fix loop. Open a project in VS Code with Copilot, switch to agent mode in the Copilot Chat panel, and submit a prompt like:

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
- [Agent Composition Patterns](../../patterns/agent-design/agent-composition-patterns.md)
- [MCP Integration](mcp-integration.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Copilot Extensions](copilot-extensions.md)
- [Migrating Copilot Extensions to MCP](../../tool-engineering/copilot-extensions-to-mcp-migration.md)
- [Copilot Memory](copilot-memory.md)
- [GitHub Copilot SDK](copilot-sdk.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Agent HQ (Multi-Agent Platform)](agent-hq.md)
