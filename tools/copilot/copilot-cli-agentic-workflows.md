---
title: "Copilot CLI Agentic Workflows for AI Agent Development"
description: "Terminal-native agentic coding with GitHub Copilot CLI — interactive and headless modes, graduated authorization, cloud delegation, and MCP integration."
tags:
  - workflows
  - agent-design
  - copilot
  - code-review
aliases:
  - Copilot CLI
  - GitHub Copilot CLI
  - copilot terminal agent
applies_to: "copilot@1.x"
last_reviewed: 2026-06-10
status: current
---

# Copilot CLI Agentic Workflows

> Terminal-native agentic coding with GitHub Copilot CLI — interactive and headless modes, graduated authorization, delegation to cloud agents, and MCP integration in the terminal.

## Operating Modes

Copilot CLI (GA February 2026) provides two operating modes for all paid Copilot subscribers ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)):

**Interactive mode** (`copilot`) — conversational sessions where the agent reads files, runs commands, and edits code with human approval at each step.

**Programmatic mode** (`copilot -p "<prompt>"`) — single-command headless execution for CI/CD and scripting pipelines ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Authorization Model

Copilot CLI uses a graduated permission model ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)):

| Level | Flag | Behavior |
|-------|------|----------|
| Manual approval (default) | — | Prompt before each tool use; approve-once, approve-session, or reject |
| Granular allow | `--allow-tool 'shell(COMMAND)'` | Auto-approve specific commands |
| Granular deny | `--deny-tool 'TOOL(command)'` | Block specific tools; deny takes precedence over allow |
| Full auto-approval | `--allow-all-tools` | Skip all permission prompts |

Deny rules are evaluated after allow rules, so `--deny-tool` overrides any matching `--allow-tool` and reduces allow-list creep. The veto is not absolute: PromptArmor disclosed a bypass in Feb 2026 where `env curl ... | env sh` evades the allowlist because `env` is auto-approved and the validator treats `curl` and `sh` as arguments, not commands; GitHub closed it as a "known issue" ([PromptArmor](https://www.promptarmor.com/resources/github-copilot-cli-downloads-and-executes-malware); [Microsoft Security, May 2026](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)). Treat the allowlist as one layer of defense-in-depth, not a containment boundary.

For headless scripting, combine programmatic mode with tool restrictions:

```bash
copilot -p "Run the test suite and fix failures" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git commit *)'
```

Use `--allow-all-tools` only inside containers with bounded [blast radius](../../security/blast-radius-containment.md) ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Plan Mode

Activated via `Shift+Tab`, [plan mode](../../workflows/plan-first-loop.md) restricts the agent to analysis without execution: Copilot reads the request, asks clarifying questions, and builds a structured plan before writing code ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)).

- **Exploration** — understand a codebase before committing to an approach
- **Review** — inspect proposed changes as diffs before approving

## Delegation to Cloud Agents

`/delegate` dispatches work to the cloud coding agent for async execution via GitHub Actions, which opens PRs for review while the developer continues locally ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)); `/resume` switches between local and remote sessions.

## Slash Commands

Commands are grouped into five categories ([GitHub Blog: Cheat Sheet](https://github.blog/ai-and-ml/github-copilot/a-cheat-sheet-to-slash-commands-in-github-copilot-cli/)): session management (`/clear`, `/session`, `/exit`), directory access (`/add-dir`, `/list-dirs`, `/cwd`), configuration (`/model`, `/terminal-setup`, `/reset-allowed-tools`), external services (`/agent`, `/delegate`, `/mcp`, `/share`), and discovery (`/help`, `/feedback`).

## Custom Agents in the CLI

Custom agents work across CLI, IDE, and github.com; `/agent` lists and selects them for the current session and can bundle specialized MCP tools for domain-specific tasks ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)). GitHub's walkthrough on building custom agents in the CLI frames them as a way to turn one-off prompts into reusable, shareable workflows ([GitHub Blog: Custom Agents in Copilot CLI](https://github.blog/ai-and-ml/github-copilot/from-one-off-prompts-to-workflows-how-to-use-custom-agents-in-github-copilot-cli/)).

## MCP in the Terminal

Copilot CLI ships with the GitHub MCP server built in for repo queries, issue lookups, and PR management. Custom servers are managed via `/mcp [show|add|edit|delete|disable|enable]`, and `--deny-tool 'My-MCP-Server(tool_name)'` scopes permissions per MCP tool ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

## Code Review from the CLI

Since March 2026, Copilot code review can be requested from the `gh` CLI ([GitHub Changelog](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/)):

```bash
# Add Copilot as a reviewer on the current PR
gh pr edit --add-reviewer @copilot
```

This triggers the [agentic code review architecture](../../code-review/agentic-code-review-architecture.md) without leaving the terminal.

## Session Management

Auto-compaction compresses conversation history at 95% context window capacity for extended sessions ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)), and repository memory persists conventions across sessions.

## Example

Hardening a CI pipeline with minimal blast radius — use programmatic mode with scoped tool permissions so the agent can run tests and commit fixes but cannot push to remote or modify pipeline configuration:

```bash
copilot -p "Run the test suite, identify failing tests, and fix them" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git add *)' \
  --allow-tool 'shell(git commit *)' \
  --deny-tool 'shell(git push)'
```

Push is blocked even if a broader allow rule would otherwise permit it. For exploratory work, omit `-p` and use interactive mode with `Shift+Tab` plan mode first to validate the approach.

## When This Backfires

- **`--allow-all-tools` outside containers** — grants full shell access; a prompt injection or hallucinated command can modify files, install packages, or push commits without review. Restrict to containerized CI environments where blast radius is bounded.
- **Validator bypass via shell indirection** — `env curl ... | env sh` evades the auto-approve allowlist and GitHub has declined to patch it; pair `--deny-tool` with sandboxing and egress controls (see Authorization Model above).
- **Headless mode with underspecified prompts** — programmatic mode exits after the first attempt and cannot ask clarifying questions; ambiguous prompts produce partial or incorrect results with no opportunity for course correction.
- **Context window exhaustion on large codebases** — auto-compaction at 95% capacity can lose earlier context that constrains later decisions; long refactoring sessions may contradict earlier choices made before compaction.
- **`/delegate` latency mismatch** — cloud agent execution via GitHub Actions takes minutes to hours; delegating time-sensitive tasks introduces a latency gap that breaks flow if the developer expects synchronous completion.
- **Usage caps on parallel workflows** — as of April 2026, GitHub tightened session and weekly token limits on Pro plans and explicitly warned that parallelized commands like `/fleet` consume tokens heavily enough to exhaust weekly quotas; agentic CLI workflows that fan out across monorepos can stall when limits hit, and Opus models were removed from Pro entirely ([GitHub Blog](https://github.blog/news-insights/company-news/changes-to-github-copilot-individual-plans/)).

## Key Takeaways

- Interactive and programmatic modes serve different needs — exploration versus automation
- `--allow-tool` / `--deny-tool` enables precise permission scoping for both modes
- `/delegate` bridges local CLI work and async cloud execution
- Plan mode (`Shift+Tab`) separates analysis from execution
- `gh pr edit --add-reviewer @copilot` requests agentic code review from the terminal
- Programmatic mode with tool restrictions makes Copilot CLI viable for CI/CD

## Related

- [Copilot CLI BYOK and Local Model Support](copilot-cli-byok-local-models.md)
- [Copilot Coding Agent](coding-agent.md)
- [Copilot Agent Mode](agent-mode.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [CLI-IDE-GitHub Context Ladder](../../workflows/cli-ide-github-context-ladder.md)
- [Cloud-Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md)
- [Agentic Code Review Architecture](../../code-review/agentic-code-review-architecture.md)
