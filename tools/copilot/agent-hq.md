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
---

# Agent HQ (Multi-Agent Platform)

> GitHub's platform for running multiple coding agents — Copilot, Claude, and Codex — within a single interface, with centralized governance and parallel agent deployment.

## What Agent HQ Provides

Agent HQ shifts GitHub from a single-agent tool to a [multi-agent platform where teams select and deploy different coding agents](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/) depending on the task. Supported agents include GitHub Copilot, Anthropic Claude, and OpenAI Codex in public preview, with [agents from Google, Cognition, and xAI announced as forthcoming](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/).

The core design principle: agents operate as teammates that produce reviewable artifacts, not autonomous actors that ship code.

## Invocation Model

Agents are triggered through familiar GitHub interaction patterns:

- **@-mention in PR comments** — `@Copilot`, `@Claude`, or `@Codex` in any pull request comment triggers the named agent to perform follow-up work
- **Issue and PR assignment** — assign an agent directly to an issue or PR; assign multiple agents to the same task for comparative output
- **Repository Agents tab** — submit requests and select a preferred agent through the repository's dedicated agent interface
- **VS Code Agent Sessions** — local, cloud-based, and background session types accessible via the [command palette](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/) (VS Code v1.109+). As of [v1.113](https://code.visualstudio.com/updates/v1_113), VS Code uses official [Claude Agent SDK](../claude/agent-sdk.md) APIs for session management and bridges registered MCP servers to CLI and Claude agent sessions automatically

## Parallel Agent Deployment

The most distinctive capability is [running multiple agents on identical tasks simultaneously](https://github.blog/news-insights/company-news/pick-your-agent-use-claude-and-codex-on-agent-hq/). Assign Copilot, Claude, and Codex to the same issue and compare their draft PRs side by side. This enables teams to evaluate which agent produces better solutions for specific problem types without committing to a single provider.

Agents operate asynchronously — users monitor progress in real time or review completed outputs later.

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

Agent HQ functions across GitHub.com, GitHub Mobile, and Visual Studio Code. This cross-surface consistency means the same agent capabilities and governance policies apply regardless of where a developer invokes an agent.

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

Parallel agent deployment only delivers value when concurrency limits allow it. Practitioner reports from 2025 flag rate limits as the primary constraint — running Copilot, Claude, and Codex simultaneously on the same issue burns through per-model quotas faster than sequential use, and hitting a cap mid-session leaves draft PRs incomplete.

Conditions where Agent HQ underperforms alternatives:

- **Rate-limited environments**: Teams on Copilot Pro (not Enterprise) hit concurrent mission ceilings quickly; parallel evaluation becomes sequential in practice
- **Merge-conflict-heavy repos**: Copilot running within Agent HQ has documented difficulty resolving merge conflicts, requiring manual intervention that erodes the asynchronous workflow benefit
- **Custom agent workflows**: The configuration surface for custom agents is limited — model selection for the Copilot coding agent is not exposed, constraining teams that need fine-grained control
- **Cost-sensitive teams**: Comparative evaluation means paying for N agent runs per task rather than one; without a clear decision framework for when to run parallel agents, costs scale without proportional benefit

## Related

- [Coding Agent](coding-agent.md)
- [Agent Mode](agent-mode.md)
- [Custom Agents and Skills](custom-agents-skills.md)
- [Agent Governance Policies](../../workflows/agent-governance-policies.md)
- [Agent Mission Control](agent-mission-control.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Copilot SDK](copilot-sdk.md)
- [GitHub Agentic Workflows](github-agentic-workflows.md)
