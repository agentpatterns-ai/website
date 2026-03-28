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

The `/delegate` command dispatches work to the cloud-based coding agent for background execution. The agent works asynchronously via GitHub Actions, opens PRs for review while the developer continues locally ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)) [unverified]. `/resume` switches between local and remote sessions.

## Slash Commands

Copilot CLI organizes commands into five categories ([GitHub Blog: Cheat Sheet](https://github.blog/ai-and-ml/github-copilot/a-cheat-sheet-to-slash-commands-in-github-copilot-cli/)): session management (`/clear`, `/session`, `/exit`), directory access (`/add-dir`, `/list-dirs`, `/cwd`), configuration (`/model`, `/terminal-setup`, `/reset-allowed-tools`), external services (`/agent`, `/delegate`, `/mcp`, `/share`), and discovery (`/help`, `/feedback`).

## Custom Agents in the CLI

Custom agents defined via `.agent.md` files [unverified] are available across CLI, IDE, and the coding agent on github.com. The `/agent` command lists and selects available agents for the current session ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

Agents can bundle specialized MCP tools for domain-specific tasks like security validation or team-specific code review [unverified].

## MCP in the Terminal

Copilot CLI ships with the GitHub MCP server built in, enabling repository queries, issue lookups, and PR management without leaving the terminal ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

Custom MCP servers are managed via `/mcp [show|add|edit|delete|disable|enable]`. Tool-level permission control applies: `--deny-tool 'My-MCP-Server(tool_name)'` [unverified] blocks specific MCP tools while keeping others accessible ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

## Code Review from the CLI

As of March 2026, Copilot code review can be triggered directly from the `gh` CLI ([GitHub Changelog](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/)):

```bash
# Request Copilot code review on the current PR
gh pr review --copilot
```

Combined with the [agentic code review architecture](../../code-review/agentic-code-review-architecture.md), CLI-triggered reviews run the full tool-calling pipeline — reading files, tracing dependencies, and evaluating architectural fit [unverified] — without leaving the terminal.

## Session Management

Auto-compaction compresses conversation at 95% context window capacity, enabling extended sessions without manual intervention. Manual compression via `/compact` [unverified] is available when needed ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

## Key Takeaways

- Interactive and programmatic modes serve different needs — exploration versus automation
- `--allow-tool` / `--deny-tool` enables precise permission scoping for both modes
- `/delegate` bridges local CLI work and async cloud execution
- Plan mode (`Shift+Tab`) separates analysis from execution
- `gh pr review --copilot` triggers agentic code review from the terminal
- Programmatic mode with tool restrictions makes Copilot CLI viable for CI/CD

## Unverified Claims

- Authorization model table details (flag names and behavior descriptions) [unverified]
- `/delegate` dispatches work to the cloud-based coding agent for background execution [unverified]
- `--deny-tool 'My-MCP-Server(tool_name)'` blocks specific MCP tools [unverified]
- Manual compression via `/compact` is available [unverified]
- Custom agents defined via `.agent.md` files [unverified]
- Agents can bundle specialized MCP tools for domain-specific tasks [unverified]
- CLI-triggered reviews run the full tool-calling pipeline (reading files, tracing dependencies, evaluating architectural fit) [unverified]

## Related

- [Agentic Code Review Architecture](../../code-review/agentic-code-review-architecture.md)
- [Copilot Coding Agent](coding-agent.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [Copilot Agent Mode](agent-mode.md)
- [CLI-IDE-GitHub Context Ladder](../../workflows/cli-ide-github-context-ladder.md)
- [Cloud-Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Copilot SDK](copilot-sdk.md)
- [Copilot Extensions](copilot-extensions.md)
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md)
- [Copilot Memory](copilot-memory.md)
- [Copilot Spaces](copilot-spaces.md)
