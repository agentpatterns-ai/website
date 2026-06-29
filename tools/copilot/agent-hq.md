---
title: "Agent HQ (Multi-Agent Platform) for AI Agent Development"
description: "GitHub's platform for running Copilot, Claude, and Codex within one interface, with centralized governance and parallel agent deployment."
aliases:
  - Multi-Agent Platform
  - GitHub Agent HQ
tags:
  - agent-design
  - multi-agent
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
---

# Agent HQ (Multi-Agent Platform)

> GitHub's platform for running multiple coding agents — Copilot, Claude, and Codex — within a single interface, with centralized governance and parallel agent deployment.

## What Agent HQ provides

Agent HQ shifts GitHub from a single-agent tool to a [multi-agent platform where teams pick the coding agent that fits the task](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/). Supported agents include GitHub Copilot, Anthropic Claude, and OpenAI Codex in public preview. GitHub has also announced [agents from Google, Cognition, and xAI as forthcoming](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/).

The core design principle is that agents are teammates producing reviewable artifacts, not autonomous actors shipping code.

## Invocation model

You trigger agents through familiar GitHub patterns:

- @-mention in PR comments — `@Copilot`, `@Claude`, or `@Codex` in any pull request comment triggers follow-up work
- Issue and PR assignment — assign one agent or several agents to a task for comparative output
- Repository Agents tab — submit requests and pick an agent through the repository's interface
- VS Code agent sessions — local, cloud, and background session types in the [command palette](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/) (VS Code v1.109+). From [v1.113](https://code.visualstudio.com/updates/v1_113), VS Code uses the official [Claude Agent SDK](../claude/agent-sdk.md) APIs and bridges registered MCP servers to CLI and Claude agent sessions automatically

## Parallel agent deployment

Agent HQ can [run multiple agents on identical tasks at the same time](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/). Assign Copilot, Claude, and Codex to the same issue, then compare their draft PRs side by side. You see which agent handles which problem type best without committing to one provider.

Agents run asynchronously. You can monitor progress live or review finished outputs later.

## Output artifacts

All agents produce the same reviewable artifact types:

- Draft pull requests — proposed code changes that need human review before merge
- Code comments — inline explanations and suggestions
- Session logs — detailed records of agent reasoning and actions taken

Agent HQ never merges a pull request automatically. Human review is the final gate.

## Enterprise governance

Agent HQ provides [centralized controls for enterprise environments](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/):

- Policy management — enterprise admins define which agents and models are allowed organization-wide
- Audit logging — full activity tracking across all agent interactions
- Code quality evaluation — GitHub Code Quality (public preview) assesses the maintainability and reliability effect of agent-generated changes
- Metrics dashboard — tracks usage and effect across organizations, with traceability for agent-generated work

## Platform availability

Agent HQ runs on GitHub.com, GitHub Mobile, and Visual Studio Code. The same agent capabilities and governance policies apply wherever you invoke an agent.

## Example

This example shows the same issue assigned to two agents at once for comparative evaluation. Assign both Copilot and Claude to issue #42 from the GitHub UI or with `gh`:

```bash
# Assign two agents to the same issue for parallel comparison
gh issue edit 42 --add-assignee "@copilot"
gh issue edit 42 --add-assignee "@claude"
```

Once the agents complete their work, two draft PRs appear — one from each agent. Review them side by side before merging either:

```bash
# List open draft PRs referencing the issue to compare outputs
gh pr list --state open --search "Fixes #42"
```

You can also trigger follow-up work from either agent directly in a PR comment:

```
@Claude Please refactor the `processPayment` function to use the repository pattern instead of direct DB calls.
```

The agent picks up the comment, makes the changes, and updates the same draft PR — no new context needed.

## Key Takeaways

- Agent HQ enables running Copilot, Claude, and Codex within a single GitHub interface
- Parallel agent deployment on the same task supports comparative evaluation of agent outputs
- All agent outputs are reviewable artifacts (draft PRs, comments, logs) — never autonomous merges
- Enterprise governance provides centralized policy, audit logging, and quality metrics
- @-mention invocation in comments follows existing GitHub collaboration patterns

## When this backfires

Parallel agent deployment only delivers value when concurrency and quota limits allow it. Running Copilot, Claude, and Codex at once on the same issue consumes per-model tokens faster than sequential use. A [March 2026 rate-limit recalibration produced multi-hour lockouts for customers whose workflows had grown to depend on the prior undercount](https://www.theregister.com/2026/04/15/github_copilot_rate_limiting_bug/).

Agent HQ underperforms alternatives under these conditions:

- Rate-limited environments: comparative evaluation uses up weekly token budgets quickly. GitHub's [Copilot usage limits](https://docs.github.com/en/copilot/concepts/usage-limits) enforce both session and 7-day caps, and parallel runs count against both
- Merge-conflict-heavy repos: once a weak spot, this narrowed after GitHub shipped [Fix with Copilot for merge conflicts on 2026-04-13](https://github.blog/changelog/2026-04-13-fix-merge-conflicts-in-three-clicks-with-copilot-cloud-agent/) (building on the [2026-03-26 `@copilot` conflict-resolution capability](https://github.blog/changelog/2026-03-26-ask-copilot-to-resolve-merge-conflicts-on-pull-requests/)). Remaining failures still need manual resolution
- Custom agent workflows: model selection is [available for Claude and Codex agents as of 2026-04-14](https://github.blog/changelog/2026-04-14-model-selection-for-claude-and-codex-agents-on-github-com/) but not for the Copilot coding agent itself, which limits teams that need fine-grained model control across every agent
- Cost-sensitive teams: comparative evaluation means paying for several agent runs per task rather than one. Without a clear decision framework for when to run parallel agents, costs scale without matching benefit

## Related

- [Coding Agent](coding-agent.md)
- [Agent Mode](agent-mode.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [Agent Mission Control](agent-mission-control.md)
- [Copilot Cloud Agent Organization Controls](cloud-agent-org-controls.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Agent Governance Policies](../../workflows/agent-governance-policies.md)
