---
title: "Claude Code Cloud Sessions: What Crosses the VM Boundary"
description: "A cloud session runs Claude Code in an Anthropic-managed VM. Learn when it fits, what config and credentials reach the VM, and where the network allowlist leaks."
tags:
  - claude
  - workflows
term: "Claude Code cloud session"
aliases:
  - "Claude Code on the web"
  - "cloud session"
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-07
status: current
---

# Claude Code Cloud Sessions: What Crosses the VM Boundary

> A cloud session runs Claude Code on an Anthropic-managed VM, so the repository, credentials, and network policy all change hands.

A Claude Code cloud session runs the agent on a machine of its own. "Each task gets a fresh virtual machine with your repository cloned onto a new branch and your environment's setup already done." ([field guide](https://claude.dev/blog/claude-code-in-the-cloud/))

## When to choose cloud

A local session shares your working tree, runs with your credentials, and stops when your computer sleeps. A cloud session removes all three dependencies ([field guide](https://claude.dev/blog/claude-code-in-the-cloud/)). Stay local for a database with real local data, a VPN service, a GPU, or a device simulator, and in Zero Data Retention organizations, where cloud sessions are off. For a few tasks with the full local toolchain, use [Remote Control](../../patterns/agent-design/remote-session-control.md).

## What crosses the boundary

The VM clones your GitHub remote, not your checkout: "The cloud VM clones your current directory's GitHub remote at your current branch, not your local checkout, so push first if you have local commits." ([docs](https://code.claude.com/docs/en/claude-code-on-the-web)) Without a remote, or for a github.com repository the Claude GitHub App is not installed on, Claude Code uploads a bundle. On macOS, Linux, and WSL it leaves uncommitted changes to credential-named files such as `.env` out of the upload. On native Windows, uncommitted changes to tracked files upload as they are.

Repo-level config travels. User-level config does not ([cloud environments](https://code.claude.com/docs/en/cloud-environments)):

- Skills, agents, and commands under `~/.claude/` stay behind. Commit them to the repo's `.claude/` directory.
- MCP servers added with `claude mcp add` at local or user scope stay behind.
- User-level SessionStart hooks do not run.

## What the session can reach

The GitHub token stays outside the VM. The git client holds a scoped credential, "which the proxy verifies and swaps for your actual GitHub token." ([GitHub proxy](https://code.claude.com/docs/en/cloud-environments#github-proxy))

The sources disagree on push scope. The field guide says the credential "can push only to its own working branch." The docs say the proxy "doesn't limit which branches a push can update." This page follows the docs, so use GitHub branch protection or rulesets.

Network access has four levels: None, Trusted (package registries, GitHub, cloud SDKs), Full, and Custom ([access levels](https://code.claude.com/docs/en/cloud-environments#access-levels)). At every level, four paths skip the allowlist: GitHub, enabled MCP connectors, API-credential hosts, and the Anthropic API for Claude Code's own requests, even at None. The docs warn that this "may allow data to exit the VM." Treat the allowlist as a narrower egress surface, not an exfiltration guarantee. Environment variables are readable by anyone who uses the environment ([cloud environments](https://code.claude.com/docs/en/cloud-environments)).

## Pause, reclaim, and restore

An idle VM pauses with its files saved, and your next message restores it. If the paused VM was reclaimed, reopening provisions a fresh one ([cloud environments](https://code.claude.com/docs/en/cloud-environments)). Conversation history returns. Subagents and shell commands still running do not ([docs](https://code.claude.com/docs/en/claude-code-on-the-web#environment-expired)). A session waiting on an MCP approval counts as inactive and can expire, so commit and push as you go.

## Make the session verify its own work

Setup scripts run as root on Ubuntu 24.04 ([setup scripts](https://code.claude.com/docs/en/cloud-environments#setup-scripts)). To scope a hook to the cloud, test `CLAUDE_CODE_REMOTE`, which is `true` in the VM and never `true` locally. See also [Cloud Agent Session Bootstrap](../../patterns/agent-design/cloud-agent-session-bootstrap.md).

## Parallel sessions and handoff

Sessions cannot see each other. The guide advises: "Split parallel tasks along file boundaries, merge the branches in a sensible order, and expect a session to report problems that another session is already fixing." ([field guide](https://claude.dev/blog/claude-code-in-the-cloud/)) Pull a session into your terminal with `--teleport` after you push its branch. You cannot push a terminal session to the cloud ([docs](https://code.claude.com/docs/en/claude-code-on-the-web)).

## Why it works

Each task gets its own VM, checkout, processes, and ports, so two sessions cannot edit the same files. The GitHub token sits in a proxy outside the VM ([GitHub proxy](https://code.claude.com/docs/en/cloud-environments#github-proxy)). On Pro and Max plans, keys you add as API credentials stay outside it too. Code in the VM cannot read those secrets. The same boundary hides anything not in the remote repo or environment config.

## When this backfires

- The task needs a VPN-only service, local data, a GPU, or a simulator, unless the organization runs a self-hosted environment (beta, Team and Enterprise).
- Build and test commands live in user-level config. The session cannot verify its work until they move into `CLAUDE.md`, `.claude/`, and `.mcp.json`.
- Setup takes longer than about 5 minutes, so it is never cached.
- Parallel tasks touch the same files, so you pay the merge cost.
- Willison reports the same output as the local CLI: "I would likely have got the exact same result running this prompt against Claude CLI on my laptop." One alternative: worktrees plus Remote Control give parallelism without sending repo contents to a hosted VM.

## Key Takeaways

- Push before you start a cloud session, because the VM clones the remote.
- Move skills, hooks, and MCP servers into the repo.
- Add branch protection, because the push proxy does not limit which branches a session updates.
- Four paths bypass the allowlist at every level.

## Related

- [Cloud-Scheduled Routines vs Local Session Scheduling](cloud-scheduled-routines.md) — scheduled cloud runs
- [Batch and Worktrees](batch-worktrees.md) — local parallel isolation
- [Cloud Agent Session Bootstrap](../../patterns/agent-design/cloud-agent-session-bootstrap.md) — install versus session-start split
- [Remote Session Control](../../patterns/agent-design/remote-session-control.md) — steer a local session remotely
- [Cloud Planning, Execute Anywhere](../../workflows/cloud-planning-execute-anywhere.md) — ultraplan review across the cloud boundary
