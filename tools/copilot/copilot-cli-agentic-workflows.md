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

## Operating modes

Copilot CLI (GA February 2026) gives all paid Copilot subscribers two operating modes ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)):

Interactive mode (`copilot`) runs conversational sessions. The agent reads files, runs commands, and edits code, with your approval at each step.

Programmatic mode (`copilot -p "<prompt>"`) runs a single headless command, for CI/CD and scripting pipelines ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Authorization model

Copilot CLI uses a graduated permission model ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)):

| Level | Flag | Behavior |
|-------|------|----------|
| Manual approval (default) | — | Prompt before each tool use; approve-once, approve-session, or reject |
| Granular allow | `--allow-tool 'shell(COMMAND)'` | Auto-approve specific commands |
| Granular deny | `--deny-tool 'TOOL(command)'` | Block specific tools; deny takes precedence over allow |
| Full auto-approval | `--allow-all-tools` | Skip all permission prompts |

Copilot evaluates deny rules after allow rules. So `--deny-tool` overrides any matching `--allow-tool` and reduces allow-list creep. The veto is not absolute. PromptArmor disclosed a bypass in February 2026 where `env curl ... | env sh` evades the allowlist, because `env` is auto-approved and the validator treats `curl` and `sh` as arguments rather than commands. GitHub closed it as a "known issue" ([PromptArmor](https://www.promptarmor.com/resources/github-copilot-cli-downloads-and-executes-malware); [Microsoft Security, May 2026](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)). Treat the allowlist as one layer of defense-in-depth, not a containment boundary.

For headless scripting, combine programmatic mode with tool restrictions:

```bash
copilot -p "Run the test suite and fix failures" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git commit *)'
```

Use `--allow-all-tools` only inside containers with bounded [blast radius](../../security/blast-radius-containment.md) ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)).

## Plan mode

[Plan mode](../../workflows/plan-first-loop.md) restricts the agent to analysis without execution. Activate it with `Shift+Tab`. Copilot reads the request, asks clarifying questions, and builds a structured plan before writing code ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)).

- Exploration: understand a codebase before committing to an approach
- Review: inspect proposed changes as diffs before approving

## Delegation to cloud agents

`/delegate` dispatches work to the cloud coding agent for async execution via GitHub Actions. The cloud agent opens PRs for review while you keep working locally ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)). `/resume` switches between local and remote sessions.

## Slash commands

Commands fall into five categories ([GitHub Blog: Cheat Sheet](https://github.blog/ai-and-ml/github-copilot/a-cheat-sheet-to-slash-commands-in-github-copilot-cli/)): session management (`/clear`, `/session`, `/exit`), directory access (`/add-dir`, `/list-dirs`, `/cwd`), configuration (`/model`, `/terminal-setup`, `/reset-allowed-tools`), external services (`/agent`, `/delegate`, `/mcp`, `/share`), and discovery (`/help`, `/feedback`).

## Custom agents in the CLI

Custom agents work across the CLI, IDE, and github.com. `/agent` lists and selects them for the current session, and can bundle specialized MCP tools for domain-specific tasks ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/)). GitHub's walkthrough on building custom agents in the CLI frames them as a way to turn one-off prompts into reusable, shareable workflows ([GitHub Blog: Custom Agents in Copilot CLI](https://github.blog/ai-and-ml/github-copilot/from-one-off-prompts-to-workflows-how-to-use-custom-agents-in-github-copilot-cli/)).

## MCP in the terminal

Copilot CLI ships with the GitHub MCP server built in for repo queries, issue lookups, and PR management. You manage custom servers with `/mcp [show|add|edit|delete|disable|enable]`, and `--deny-tool 'My-MCP-Server(tool_name)'` scopes permissions per MCP tool ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)).

## Code review from the CLI

Since March 2026, you can request Copilot code review from the `gh` CLI ([GitHub Changelog](https://github.blog/changelog/2026-03-11-request-copilot-code-review-from-github-cli/)):

```bash
# Add Copilot as a reviewer on the current PR
gh pr edit --add-reviewer @copilot
```

This triggers the [agentic code review architecture](../../code-review/agentic-code-review-architecture.md) without leaving the terminal.

## Session management

Auto-compaction compresses conversation history at 95% context window capacity, which keeps long sessions going ([GitHub Changelog](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)). Repository memory persists conventions across sessions.

## Example

To harden a CI pipeline with minimal blast radius, use programmatic mode with scoped tool permissions. The agent can run tests and commit fixes, but cannot push to remote or modify pipeline configuration:

```bash
copilot -p "Run the test suite, identify failing tests, and fix them" \
  --allow-tool 'shell(npm test)' \
  --allow-tool 'shell(git add *)' \
  --allow-tool 'shell(git commit *)' \
  --deny-tool 'shell(git push)'
```

Push stays blocked even if a broader allow rule would otherwise permit it. For exploratory work, omit `-p` and use interactive mode with `Shift+Tab` plan mode first to validate the approach.

## When this backfires

- `--allow-all-tools` outside containers grants full shell access. A prompt injection or hallucinated command can modify files, install packages, or push commits without review. Restrict it to containerized CI environments where blast radius is bounded.
- Validator bypass via shell indirection: `env curl ... | env sh` evades the auto-approve allowlist, and GitHub has declined to patch it. Pair `--deny-tool` with sandboxing and egress controls (see Authorization model above).
- Headless mode with underspecified prompts: programmatic mode exits after the first attempt and cannot ask clarifying questions. Ambiguous prompts produce partial or incorrect results, with no chance to course-correct.
- Context window exhaustion on large codebases: auto-compaction at 95% capacity can lose earlier context that constrains later decisions. Long refactoring sessions may contradict earlier choices made before compaction.
- `/delegate` latency mismatch: cloud agent execution via GitHub Actions takes minutes to hours. Delegating time-sensitive tasks introduces a latency gap that breaks flow if you expect synchronous completion.
- Usage caps on parallel workflows: in April 2026, GitHub tightened session and weekly token limits on Pro plans, and warned that parallelized commands like `/fleet` consume tokens heavily enough to exhaust weekly quotas. Agentic CLI workflows that fan out across monorepos can stall when limits hit, and GitHub removed Opus models from Pro entirely ([GitHub Blog](https://github.blog/news-insights/company-news/changes-to-github-copilot-individual-plans/)).

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
