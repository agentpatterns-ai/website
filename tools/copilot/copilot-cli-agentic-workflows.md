---
title: "Copilot CLI Agentic Workflows for AI Agent Development"
description: "Terminal-native agentic coding with GitHub Copilot CLI — interactive and headless modes, graduated authorization, delegation to cloud agents, and MCP"
tags:
  - workflows
  - agent-design
  - copilot
  - code-review
aliases:
  - Copilot CLI
  - GitHub Copilot CLI
  - copilot terminal agent
---

# Copilot CLI Agentic Workflows

> Terminal-native agentic coding with GitHub Copilot CLI — interactive and headless modes, graduated authorization, delegation to cloud agents, and MCP integration in the terminal.

## Operating Modes

Copilot CLI (GA February 2026) provides two operating modes for all paid Copilot subscribers ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)):

**Interactive mode** (`copilot`) — conversational sessions in the terminal. The agent reads files, runs commands, and edits code with human approval at each step.

**Programmatic mode** (`copilot -p "<prompt>"`) — single-command headless execution. Runs non-interactively and exits, suitable for CI/CD automation and scripting pipelines ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Authorization Model

Copilot CLI implements a graduated permission model that controls what the agent can execute ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)):

| Level | Flag | Behavior |
|-------|------|----------|
| Manual approval (default) | — | Prompt before each tool use; approve-once, approve-session, or reject |
| Granular allow | `--allow-tool 'shell(COMMAND)'` | Auto-approve specific commands |
| Granular deny | `--deny-tool 'TOOL(command)'` | Block specific tools; deny takes precedence over allow |
| Full auto-approval | `--allow-all-tools` | Skip all permission prompts |

The graduated model works because deny rules are evaluated after allow rules, giving operators a reliable veto layer — `--deny-tool` takes precedence over any matching `--allow-tool` for the same command, preventing allow-list creep from accidentally permitting destructive operations.

For headless scripting, combine programmatic mode with tool restrictions:

```bash
copilot -p "Run the test suite and fix failures" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git commit *)'
```

Use `--allow-all-tools` only in containerized environments where the [blast radius](../../security/blast-radius-containment.md) is contained ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Plan Mode

Activated via `Shift+Tab`, [plan mode](../../workflows/plan-first-loop.md) restricts the agent to analysis without execution. Copilot reads the request, asks clarifying questions, and builds a structured plan before writing code ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)).

- **Exploration** — understand a codebase or problem space before committing to an approach
- **Review** — inspect proposed changes as diffs before approving execution

## Delegation to Cloud Agents

The `/delegate` command dispatches work to the cloud-based coding agent for background execution. The agent works asynchronously via GitHub Actions, opens PRs for review while the developer continues locally ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)). `/resume` switches between local and remote sessions.

## Slash Commands

Copilot CLI organizes commands into five categories ([GitHub Blog: Cheat Sheet](https://github.blog/ai-and-ml/github-copilot/a-cheat-sheet-to-slash-commands-in-github-copilot-cli/)): session management (`/clear`, `/session`, `/exit`), directory access (`/add-dir`, `/list-dirs`, `/cwd`), configuration (`/model`, `/terminal-setup`, `/reset-allowed-tools`), external services (`/agent`, `/delegate`, `/mcp`, `/share`), and discovery (`/help`, `/feedback`).

## Custom Agents in the CLI

Custom agents are available across CLI, IDE, and github.com. The `/agent` command lists and selects available agents for the current session ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

Agents can bundle specialized MCP tools for domain-specific tasks like security validation or team-specific code review.

## MCP in the Terminal

Copilot CLI ships with the GitHub MCP server built in, enabling repository queries, issue lookups, and PR management without leaving the terminal ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

Custom MCP servers are managed via `/mcp [show|add|edit|delete|disable|enable]`. Tool-level permission control applies: `--deny-tool 'My-MCP-Server(tool_name)'` blocks specific MCP tools while keeping others accessible ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

## Code Review from the CLI

As of March 2026, Copilot code review can be requested directly from the `gh` CLI ([GitHub Changelog](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/)):

```bash
# Add Copilot as a reviewer on the current PR
gh pr edit --add-reviewer @copilot
```

Combined with the [agentic code review architecture](../../code-review/agentic-code-review-architecture.md), this triggers the Copilot code review pipeline without leaving the terminal.

## Session Management

Auto-compaction compresses conversation history at 95% context window capacity, enabling extended sessions without manual intervention ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)). Repository memory persists conventions and patterns learned across sessions.

## Example

Hardening a CI pipeline with minimal blast radius — use programmatic mode with scoped tool permissions so the agent can run tests and commit fixes but cannot push to remote or modify pipeline configuration:

```bash
copilot -p "Run the test suite, identify failing tests, and fix them" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git add *)' \
  --allow-tool 'shell(git commit *)' \
  --deny-tool 'shell(git push)'
```

The `--deny-tool` takes precedence over `--allow-tool`, so push is blocked even if a broader allow rule would otherwise permit it. For exploratory work, omit `-p` and use interactive mode with `Shift+Tab` plan mode first to validate the approach before granting any execution permissions.

## When This Backfires

- **`--allow-all-tools` outside containers** — grants full shell access; a prompt injection or hallucinated command can modify files, install packages, or push commits without review. Restrict to containerized CI environments where blast radius is bounded.
- **Headless mode with underspecified prompts** — programmatic mode exits after the first attempt and cannot ask clarifying questions; ambiguous prompts produce partial or incorrect results with no opportunity for course correction.
- **Context window exhaustion on large codebases** — auto-compaction at 95% capacity can lose earlier context that constrains later decisions; long refactoring sessions may contradict earlier choices made before compaction.
- **`/delegate` latency mismatch** — cloud agent execution via GitHub Actions takes minutes to hours; delegating time-sensitive tasks introduces a latency gap that breaks flow if the developer expects synchronous completion.

## Key Takeaways

- Interactive and programmatic modes serve different needs — exploration versus automation
- `--allow-tool` / `--deny-tool` enables precise permission scoping for both modes
- `/delegate` bridges local CLI work and async cloud execution
- Plan mode (`Shift+Tab`) separates analysis from execution
- `gh pr edit --add-reviewer @copilot` requests agentic code review from the terminal
- Programmatic mode with tool restrictions makes Copilot CLI viable for CI/CD

## Related

- [Agentic Code Review Architecture](../../code-review/agentic-code-review-architecture.md)
- [Copilot Coding Agent](coding-agent.md)
- [Copilot CLI BYOK and Local Model Support](copilot-cli-byok-local-models.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [Copilot Agent Mode](agent-mode.md)
- [Agent HQ](agent-hq.md)
- [Agent Mission Control](agent-mission-control.md)
- [Copilot Cloud Agent Organization Controls](cloud-agent-org-controls.md)
- [CLI-IDE-GitHub Context Ladder](../../workflows/cli-ide-github-context-ladder.md)
- [Cloud-Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Copilot SDK](copilot-sdk.md)
- [Copilot Extensions](copilot-extensions.md)
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md)
- [Copilot Memory](copilot-memory.md)
- [Copilot Spaces](copilot-spaces.md)
