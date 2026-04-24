---
title: "GitHub Copilot Coding Agent for AI Agent Development"
description: "Asynchronous agent that works via GitHub Actions to plan, implement, test, and open pull requests — Copilot's cloud counterpart to agent mode."
tags:
  - agent-design
  - copilot
---

# GitHub Copilot Coding Agent

> Asynchronous agent that works via GitHub Actions to plan, implement, test, and open pull requests.

## How It Works

The [coding agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) is Copilot's asynchronous counterpart to agent mode. Assign a GitHub issue or prompt via Copilot Chat, and the agent spins up an ephemeral development environment powered by GitHub Actions. It explores code, plans the work, writes changes, runs automated tests and linters, and opens a pull request.

[Generally available September 2025](https://github.blog/changelog/2025-09-25-copilot-coding-agent-is-now-generally-available/) for all paid Copilot subscribers.

## Self-Review & Security

Before opening a PR, the coding agent implements the [agent self-review loop](../../agent-design/agent-self-review-loop.md): it [reviews its own changes](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/) using Copilot code review, iterates on feedback, and runs security scanning: [CodeQL code scanning, secret scanning, and dependency vulnerability checks](https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-automatically-validates-code-security-and-quality/).

## MCP Server Support

The coding agent can use tools provided by [MCP servers](https://docs.github.com/en/copilot/concepts/agents/coding-agent/mcp-and-coding-agent) — both local and remote. Currently limited to tools (not resources or prompts).

## CLI Handoff

Prefix any CLI prompt with `&` to delegate work to the cloud-based coding agent — [GitHub describes it as pressing "the ampersand symbol (`&`) in the CLI to delegate work back to the cloud and keep going locally"](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/). Use `/resume` to pull a cloud session back into your local CLI.

## Best For

Low-to-medium complexity tasks in well-tested codebases: adding features, fixing bugs, extending tests, refactoring, and documentation improvements.

## When This Backfires

- **Large multi-file refactors.** Practitioners report the coding agent struggles when changes span many interconnected files and architectural concerns; a local IDE agent with richer context is often a better fit ([community report, Jan 2026](https://github.com/orgs/community/discussions/183877)).
- **Tight iteration loops.** Webapp sessions can take 90+ seconds to spin up an Actions runner, and the cycle repeats if the agent times out before finishing — interactive local agents avoid this overhead ([community report, Jan 2026](https://github.com/orgs/community/discussions/183877)).
- **Heavy daily usage under flat-rate plans.** Agentic workflows routinely exceed the compute included in paid tiers; in late 2025 GitHub paused new Copilot sign-ups and tightened usage limits on agent-heavy plans ([The New Stack](https://thenewstack.io/github-copilot-signups-paused/), [TNW](https://thenextweb.com/news/github-copilot-signup-pause-agentic-ai-usage-limits)).
- **Work the agent cannot self-verify.** The self-review + test loop only catches what the repo's own tests and scanners catch; changes that need human judgement (UX, API design, security-sensitive logic) still require a close human review before merge.

## Example

Assign the coding agent to a GitHub issue directly from the issue sidebar by selecting **Copilot** as the assignee, or trigger it via Copilot Chat with a specific issue reference:

```
@copilot Fix the N+1 query problem described in #312. The issue is in the `OrderRepository.findByUser` method — add eager loading for the related `items` and `product` associations and add a regression test.
```

The agent spins up a GitHub Actions runner, explores the codebase, and opens a draft PR. The Actions log shows each step:

```
▶ Exploring codebase
  Reading src/repositories/OrderRepository.ts
  Reading tests/repositories/OrderRepository.test.ts
▶ Planning changes
  - Add .include(:items, :product) to findByUser query
  - Add test asserting single query for 3 orders
▶ Implementing
  Modified: src/repositories/OrderRepository.ts
  Modified: tests/repositories/OrderRepository.test.ts
▶ Running tests (npm test)
  All 47 tests passing
▶ Self-review
  No issues detected
▶ Opening draft PR #318
```

After the PR opens, add an MCP server to extend what the agent can access during future tasks — for example, a database introspection tool registered in `.github/copilot/mcp.json`:

```json
{
  "mcpServers": {
    "db-schema": {
      "type": "http",
      "url": "<your-mcp-server-url>"
    }
  }
}
```

With the MCP server registered, the coding agent can query live table schemas during implementation instead of inferring them from existing code.

## Key Takeaways

- Fully asynchronous — works in the background via GitHub Actions while you continue
- Self-reviews changes and runs security scanning before opening PRs
- MCP server support extends capabilities to external tools
- CLI handoff enables seamless switching between local and remote agent work

## Related

- [Agent Mode](agent-mode.md)
- [Custom Agents & Skills](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [Cloud-Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Agent HQ](agent-hq.md)
- [Cloud Agent Research-Plan-Code](cloud-agent-research-plan-code.md)
- [Copilot Cloud Agent Organization Controls](cloud-agent-org-controls.md)
