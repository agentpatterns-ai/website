---
title: "Cloud-Local Agent Handoff for AI Agent Development"
term: "Cloud-Local Agent Handoff"
description: "Transferring agent sessions between cloud and local environments while preserving branch state, session logs, and conversation context."
tags:
  - agent-design
  - workflows
  - copilot
last_reviewed: 2026-06-19
maturity: adopted
---

# Cloud-Local Agent Handoff

> Cloud-local handoff moves an agent session between cloud and local surfaces while preserving the branch, session logs, and conversation context for continuous work.

## The problem

You work across several surfaces: web-based GitHub interfaces, local IDEs, and terminal CLIs. Without a handoff mechanism, switching between a [cloud agent](../tools/copilot/cloud-agent-org-controls.md) and a local environment loses your conversation history, restarts your context, and forces you to check out branches by hand. Cloud-local handoff fixes this. It treats the agent session as portable state that moves between surfaces.

## Cloud to local

GitHub's [coding agent](../tools/copilot/coding-agent.md) runs in the cloud and produces work on a branch. To continue that work locally, you [copy a "Continue in Copilot CLI" command](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/). It loads the session into the terminal with the branch, session logs, and conversation context intact. You pick up exactly where the cloud agent left off, and you can see what the agent tried, what failed, and what it decided.

This handoff preserves:

- the working branch, with every commit the cloud agent created
- session logs that show the agent's reasoning and actions
- conversation context, so the local session understands prior work

Without this mechanism, [switching contexts means starting the conversation over](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/). The handoff keeps agent sessions durable as you move between surfaces.

## Local to cloud

The reverse direction uses the [`/delegate` command in Copilot CLI](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/). It sends work to the cloud coding agent to run in the background:

```
/delegate Finish fixing the issue outlined in #1 and use the playwright MCP server to ensure that it's fixed
```

The delegated work follows the [standard coding agent workflow](https://github.blog/ai-and-ml/github-copilot/power-agentic-workflows-in-your-terminal-with-github-copilot-cli/). The agent runs asynchronously and opens a pull request with its results. You keep working locally on other tasks while the cloud agent handles the delegated work in the background.

The `&` shortcut in the CLI gives you a [quick way to delegate](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/): it sends the current task to the cloud so you can keep working locally.

## When to hand off

| Direction | Use when |
|-----------|----------|
| Cloud to local | The agent produced a draft that needs manual refinement, debugging, or testing against local infrastructure |
| Local to cloud | A well-defined subtask can run autonomously while you focus on other work |
| Bidirectional | Complex features where initial scaffolding runs in the cloud and iterative refinement happens locally |

## The transferable pattern

GitHub Copilot was an early example, but the handoff is no longer single-vendor. Cursor ships the same building blocks: `/in-cloud` cloud subagents that each run on their own VM and branch, a `/babysit` command that prepares a cloud PR for merge remotely, and reliable session pull-back to local for verification ([Cursor — cloud agents in the agents window](https://cursor.com/changelog/cloud-in-agents-window)). The pattern applies broadly: agent sessions should be serializable and portable across execution surfaces. It needs four properties:

- branch as shared state: Git branches coordinate any cloud and local agent
- session logs as context: the receiving surface needs to see what the sending surface did
- asynchronous execution: the cloud agent works independently after delegation
- reviewable artifacts: delegated work produces pull requests that keep human authority over the final result

Any agent system that supports these four properties can implement cross-surface handoff, even without a single vendor's integrated toolchain.

## Example

A developer assigns an issue to the GitHub Copilot coding agent. The agent creates a branch `copilot/fix-auth-redirect`, adds three commits, and opens a draft PR — but the CI pipeline fails on an integration test that requires a local database connection.

Cloud to local: the developer clicks "Continue in Copilot CLI" on the PR page and copies the generated command, which resumes the session in Copilot CLI:

```bash
copilot --resume <session-id>
```

Copilot CLI checks out the branch, loads the session logs, and restores the conversation context. The developer sees the agent's failed test output and fixes the database connection config locally:

```
> The integration test failed because the auth redirect URL is hardcoded to localhost:3000.
> I'll update the config to read from AUTH_REDIRECT_URL and re-run the tests.
```

After verifying the fix passes locally, the developer pushes the commit.

Local to cloud: while reviewing the fix, the developer notices a related issue with session expiry handling. Rather than switch context, they delegate it:

```
/delegate Fix the session expiry bug described in #247 — the refresh token rotation is not updating the stored token
```

The coding agent picks up the task on a new branch, works asynchronously, and opens a separate PR. The developer continues refining the auth redirect fix locally while the [cloud coding agent](../tools/copilot/coding-agent.md) handles session expiry in parallel.

## When this backfires

Cloud-local handoff depends on session state being transferable, which breaks down in several conditions:

- Stale or truncated session logs — cloud agents that run long tasks can produce logs that exceed the local context window. The receiving session then loads partial context and may misread prior decisions.
- Branch divergence — if the local branch has commits not yet on the remote, or the remote has moved ahead, the handoff leaves the developer resolving merge conflicts before work can resume. A [single-branch strategy](../workflows/single-branch-git-agent-swarms.md) sidesteps this class of conflict.
- Environment mismatch — cloud runners have different toolchains, credentials, and network access than local machines. A task that succeeded in the cloud (for example, calling an internal API with runner credentials) may fail locally without equivalent configuration.
- Toolchain lock-in — the integrated handoff is GitHub Copilot-specific. Teams using other agent stacks must implement session serialization by hand, through shared branch state and exported logs.

## Key Takeaways

- Cloud-to-local handoff preserves branch, session logs, and conversation context across surfaces
- The `/delegate` command and `&` shortcut send local work to the cloud coding agent for background execution
- Git branches serve as the universal coordination mechanism between cloud and local agents
- Agent sessions should be serializable and portable — not locked to a single execution surface
- Delegated work produces reviewable PRs, maintaining human authority over the final result

## Related

- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Seamless Background-to-Foreground Handoff](../workflows/background-foreground-handoff.md)
- [Coding Agent](../tools/copilot/coding-agent.md)
- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md)
- [Parallel Agent Sessions](../workflows/parallel-agent-sessions.md)
- [Programmatic Cloud-Agent Dispatch via REST API and Webhooks](../workflows/programmatic-cloud-agent-dispatch.md)
- [CLI-IDE-GitHub Context Ladder](../workflows/cli-ide-github-context-ladder.md)
- [Copilot CLI Agentic Workflows](../tools/copilot/copilot-cli-agentic-workflows.md)
