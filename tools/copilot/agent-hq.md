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

## What Agent HQ Provides

Agent HQ shifts GitHub from a single-agent tool to a [multi-agent platform where teams pick the coding agent that fits the task](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/). Supported agents include GitHub Copilot, Anthropic Claude, and OpenAI Codex in public preview, with [agents from Google, Cognition, and xAI announced as forthcoming](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/).

The core design principle: agents are teammates producing reviewable artifacts, not autonomous actors shipping code.

## Invocation Model

Agents are triggered through familiar GitHub patterns:

- **@-mention in PR comments** — `@Copilot`, `@Claude`, or `@Codex` in any pull request comment triggers follow-up work
- **Issue and PR assignment** — assign one agent or multiple agents to a task for comparative output
- **Repository Agents tab** — submit requests and pick an agent through the repository's dedicated interface
- **VS Code Agent Sessions** — local, cloud-based, and background session types in the [command palette](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/) (VS Code v1.109+). As of [v1.113](https://code.visualstudio.com/updates/v1_113), VS Code uses official [Claude Agent SDK](../claude/agent-sdk.md) APIs and bridges registered MCP servers to CLI and Claude agent sessions automatically

## Parallel Agent Deployment

The distinctive capability is [running multiple agents on identical tasks simultaneously](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/). Assign Copilot, Claude, and Codex to the same issue and compare their draft PRs side by side — teams evaluate which agent solves which problem type best without committing to one provider.

Agents run asynchronously; monitor progress live or review completed outputs later.

## Output Artifacts

All agents produce the same reviewable artifact types:

- **Draft pull requests** — proposed code changes requiring human review before merge
- **Code comments** — inline explanations and suggestions
- **Session logs** — detailed records of agent reasoning and actions taken

Pull requests are never merged automatically. Human review remains the final gate.

## Enterprise Governance

Agent HQ provides [centralized controls for enterprise environments](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/):

- **Policy management** — enterprise admins define which agents and models are permitted organization-wide
- **Audit logging** — full activity tracking across all agent interactions
- **Code quality evaluation** — GitHub Code Quality (public preview) assesses maintainability and reliability impact of agent-generated changes
- **Metrics dashboard** — tracks usage and impact across organizations with traceability for agent-generated work

## Platform Availability

Agent HQ runs across GitHub.com, GitHub Mobile, and Visual Studio Code, so the same agent capabilities and governance policies apply wherever a developer invokes an agent.

## Example

This example shows the same issue assigned to two agents simultaneously for comparative evaluation. Assign both Copilot and Claude to issue #42 from the GitHub UI or via `gh`:

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

## When This Backfires

Parallel agent deployment only delivers value when concurrency and quota limits allow it. Running Copilot, Claude, and Codex simultaneously on the same issue consumes per-model tokens faster than sequential use, and a [March 2026 rate-limit recalibration produced multi-hour lockouts for customers whose workflows had grown to depend on the prior undercount](https://www.theregister.com/2026/04/15/github_copilot_rate_limiting_bug/).

Conditions where Agent HQ underperforms alternatives:

- **Rate-limited environments**: Comparative evaluation burns through weekly token budgets quickly — GitHub's [Copilot usage limits](https://docs.github.com/en/copilot/concepts/usage-limits) enforce both session and 7-day caps, and parallel runs count against both
- **Merge-conflict-heavy repos**: Previously a weak spot, this narrowed after GitHub shipped [`Fix with Copilot` for merge conflicts on 2026-04-13](https://github.blog/changelog/2026-04-13-fix-merge-conflicts-in-three-clicks-with-copilot-cloud-agent/) (building on the [2026-03-26 `@copilot` conflict-resolution capability](https://github.blog/changelog/2026-03-26-ask-copilot-to-resolve-merge-conflicts-on-pull-requests/)); residual failures still require manual resolution
- **Custom agent workflows**: Model selection is [exposed for Claude and Codex agents as of 2026-04-14](https://github.blog/changelog/2026-04-14-model-selection-for-claude-and-codex-agents-on-github-com/) but not for the Copilot coding agent itself, constraining teams that need fine-grained model control across every agent
- **Cost-sensitive teams**: Comparative evaluation means paying for N agent runs per task rather than one; without a clear decision framework for when to run parallel agents, costs scale without proportional benefit

## Related

- [Coding Agent](coding-agent.md)
- [Agent Mode](agent-mode.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [Agent Mission Control](agent-mission-control.md)
- [Copilot Cloud Agent Organization Controls](cloud-agent-org-controls.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Agent Governance Policies](../../workflows/agent-governance-policies.md)
