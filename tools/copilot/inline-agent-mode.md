---
title: "Copilot Inline Agent Mode in JetBrains IDEs"
description: "Public-preview surface that runs Copilot agent capabilities inside the JetBrains inline chat popover instead of the dedicated chat panel."
tags:
  - agent-design
  - copilot
---

# Copilot Inline Agent Mode in JetBrains

> Public-preview surface that runs Copilot agent capabilities inside the JetBrains inline chat popover instead of the dedicated chat panel.

## What It Is

Inline agent mode brings agent capabilities into the JetBrains inline chat experience, so you can invoke them from the editor without switching to the chat panel ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)). It rides on the inline chat popover anchored to the active selection and file, and exposes the same agent toolkit — workspace search, multi-file edits, terminal commands, and editor lint/compile error reads — used by chat-panel agent mode ([GitHub Changelog 2025-05-19](https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/)).

It shipped in public preview on April 24, 2026. Chat-panel [agent mode](agent-mode.md) has been GA in JetBrains since [July 16, 2025](https://github.blog/changelog/2025-07-16-agent-mode-for-jetbrains-eclipse-and-xcode-is-now-generally-available/) — inline agent mode is an additional surface, not a replacement.

## Invocation

Open Inline Chat using `Shift+Ctrl+I` (Windows) or `Shift+Cmd+I` (Mac), via right-click → **Open Inline Chat**, or via the gutter icon, then switch to agent mode in the inline chat panel ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)).

Copilot Business and Copilot Enterprise tenants need an admin to enable the **Editor preview features** policy before the surface appears for users ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)).

## Inline Surface vs. Chat Panel

Both surfaces share the same four-phase loop — semantic understanding, plan proposal, plan execution, task completion ([GitHub Changelog 2025-05-19](https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/)). They differ in where the conversation, plan, and diffs render.

| Dimension | Inline agent mode | Chat-panel agent mode |
|-----------|------------------|----------------------|
| Invocation | `Shift+Ctrl/Cmd+I` from the editor | Tool window |
| Anchoring | Active selection / cursor / file | Workspace, last-active file |
| Plan and diff render area | Inline popover | Full chat tool window |
| Best fit | Edits scoped to a single file or selection | Multi-file changes, long plans, terminal output review |

The trade-off is invocation cost vs. legibility. Inline mode shortens the path from "looking at this code" to "an agent acting on this code"; the chat panel keeps multi-step plans, file lists, and terminal output readable as a run grows.

## Same-Release Controls That Affect This Surface

The April 24, 2026 release also shipped two settings under `Settings > GitHub Copilot > Chat > Auto Approve` that govern any agent run, including inline ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)):

- **Global Auto Approve** — auto-approves all tool calls across all workspaces and overrides per-category auto-approve settings, including for destructive actions such as file edits, terminal commands, and external tool calls.
- **Auto-approve commands not covered by rules** and **Auto-approve file edits not covered by rules** — narrower variants for tool calls that have no explicit rule.

GitHub's own guidance is to enable these only if you understand and accept the security risks ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)). The combination of inline invocation (low friction) and global auto-approve (no confirmation) collapses the [confirmation gate](../../security/human-in-the-loop-confirmation-gates.md) for agent-initiated changes — keep them off unless the workspace is sandboxed.

The same release also adds inline edit previews for [Next Edit Suggestions](../../tool-engineering/next-edit-suggestions.md) and a gutter direction indicator for far-away edits, so reviewing proposed changes can stay inside the editor as well ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)).

## When to Use Inline Over Chat Panel

- **Selection-scoped refactors** where the prompt and the target are the same code under the cursor.
- **Quick fixes against editor lint or compile errors** the agent can read directly ([GitHub Changelog 2025-05-19](https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/)).
- **Tight feedback loops** where invocation cost dominates — staying on the same shortcut and surface as inline chat eliminates a context switch.

Prefer the chat panel when the task spans many files, requires reading a long plan before approving, or needs the larger terminal-output area. The chat panel also keeps the broader [plan-first loop](../../workflows/plan-first-loop.md) more legible when the plan agent is involved ([GitHub Changelog 2026-03-11](https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides/)).

## When This Backfires

- **Long agent runs from a popover.** Plans, terminal output, and diff stacks all crowd the inline panel. Switch to the chat panel once the run outgrows what the popover can show.
- **Global auto-approve on a non-sandboxed checkout.** Cheap inline invocation plus global auto-approve removes the per-step confirmation that would catch destructive tool calls. Keep [blast radius](../../security/blast-radius-containment.md) contained.
- **Habits carried over from edit mode.** Edit mode was deprecated from the chat mode dropdown in March 2026 ([GitHub Changelog 2026-03-11](https://github.blog/changelog/2026-03-11-major-agentic-capabilities-improvements-in-github-copilot-for-jetbrains-ides/)); inline agent mode runs the full agent loop, not a single edit.
- **Business/Enterprise tenants without the policy enabled.** The surface stays invisible until the **Editor preview features** policy is on ([GitHub Changelog 2026-04-24](https://github.blog/changelog/2026-04-24-inline-agent-mode-in-preview-and-more-in-github-copilot-for-jetbrains-ides/)).

## Example

You are in IntelliJ IDEA looking at a failing test method. Select the test body, press `Shift+Cmd+I` (Mac) to open inline chat, switch the inline chat panel to agent mode, and submit:

```
Fix this test. Read the failing assertion, the function under test, and any related fixtures. Re-run the test until it passes.
```

The agent runs the four-phase loop in place: it gathers context from the selection plus the workspace, proposes a plan, edits the test and any supporting files, and runs the test through the terminal until it converges ([GitHub Changelog 2025-05-19](https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/)). When the diff or terminal output outgrows the popover, fall back to the chat panel.

## Key Takeaways

- Inline agent mode is the same Copilot agent capability hosted in the JetBrains inline chat popover, available in public preview from April 24, 2026
- Invocation is `Shift+Ctrl/Cmd+I` then switch the inline panel to agent mode; Business/Enterprise tenants need the Editor preview features policy enabled
- Prefer the inline surface for selection-scoped tasks and the chat panel for runs whose plan, diff, or terminal output need more space
- Same-release global auto-approve combined with inline invocation removes confirmation gates — only enable in sandboxed workspaces

## Related

- [Copilot Agent Mode](agent-mode.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [MCP Integration](mcp-integration.md)
- [Next Edit Suggestions](../../tool-engineering/next-edit-suggestions.md)
- [Human-in-the-Loop Confirmation Gates](../../security/human-in-the-loop-confirmation-gates.md)
- [Blast Radius Containment](../../security/blast-radius-containment.md)
- [Plan-First Loop](../../workflows/plan-first-loop.md)
