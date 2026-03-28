---
title: "Claude Code Agent Teams for Collaborative AI Workflows"
description: "Coordinated multi-agent sessions with shared task lists, direct messaging, and team lead orchestration for Claude Code projects."
aliases:
  - "team mode"
  - "multi-agent teams"
tags:
  - agent-design
  - multi-agent
  - claude
---

# Claude Code Agent Teams

> Coordinated multi-agent sessions with shared task lists, direct messaging, and team lead orchestration.

## How They Work

[Agent teams](https://code.claude.com/docs/en/agent-teams) are an experimental feature where multiple Claude Code sessions coordinate as a team. One session acts as team lead, assigning tasks and synthesizing results. Teammates work independently in their own context windows but can communicate directly with each other.

Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` in `settings.json` or as an environment variable.

!!! warning "Experimental — details may change"
    The feature flag, CLI flags, hook names, and environment variables on this page reflect the [agent teams docs](https://code.claude.com/docs/en/agent-teams) as of March 2026. Check the canonical reference for the latest specifics.

## Teams vs Sub-Agents

| | Sub-Agents | Agent Teams |
|---|---|---|
| Communication | One-way (result to parent) | Two-way (direct messaging) |
| Coordination | Parent orchestrates | Teammates self-coordinate |
| Context | Fresh, isolated | Independent but can share findings |
| State | Ephemeral | Persistent within session |

Use sub-agents when you need quick, focused workers. Use agent teams when your agents need to share findings, challenge each other, and coordinate autonomously.

## Model Inheritance

Team agents inherit the model configured on the leader agent. Prior to v2.1.73 [unverified], team agents could silently downgrade to a different model. This is now fixed — teammates use the leader's model unless overridden per-invocation via the `model` parameter on the Agent tool.

On Bedrock, Vertex, and Foundry, sub-agents specifying `model: opus/sonnet/haiku` were also silently downgraded to older model versions. This was resolved in v2.1.73 [unverified] alongside the team inheritance fix.

## Per-Agent Observability

Hook events include `agent_id` and `agent_type` fields (v2.1.69 [unverified]), enabling hooks to distinguish between the team lead, teammates, and sub-agents. Use these to apply different enforcement rules per agent role or to tag audit logs with agent identity — for example, allowing the lead to push to remote while restricting teammates to local operations.

## Hooks for Teams

- `TeammateIdle` [unverified]: fires when a teammate is about to go idle — exit with code 2 to send feedback and keep the teammate working
- `TaskCompleted` [unverified]: fires when a task is being marked complete — exit with code 2 to prevent completion and send feedback

## Best For

Research and review tasks, building new modules or features, debugging with competing hypotheses, and cross-layer coordination where different agents need different perspectives on the same codebase.

## Example

This example shows a team of three agents — a team lead, a researcher, and a reviewer — coordinating on a feature analysis task. The team lead delegates subtasks and the teammates communicate directly without routing everything through the lead.

Enable the feature flag in `settings.json` before starting:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

With the flag set, Claude Code prompts can delegate directly to team members:

```bash
# Spawn a team lead that coordinates two teammates [unverified]
claude --team-size 3 "Audit the authentication module: one agent reviews the token lifecycle, one reviews session management, and synthesise the findings into a security report"
```

The `TeammateIdle` hook can be used to prevent a teammate from going idle prematurely — exit code 2 [unverified] sends feedback and keeps the teammate working:

```bash
# .claude/hooks/TeammateIdle.sh
#!/usr/bin/env bash
# Keep the reviewer working if no findings have been documented yet
if ! grep -q "## Findings" "$CLAUDE_TEAMMATE_OUTPUT"; then  # $CLAUDE_TEAMMATE_OUTPUT [unverified]
  echo "No findings documented yet. Continue reviewing and record your observations." >&2
  exit 2
fi
exit 0
```

The `TaskCompleted` hook similarly gates completion — useful when a synthesis step must verify that all subtask outputs are present before the team lead closes the task.

## Key Takeaways

- Teams enable multi-agent coordination with shared task lists and direct messaging
- Unlike sub-agents, teammates share findings and challenge each other
- Team agents inherit the leader's model — silent downgrades fixed in v2.1.73 [unverified]
- Experimental feature — enable explicitly in settings
- Team-specific hooks (`TeammateIdle`, `TaskCompleted`) provide control over team behavior

## Unverified Claims

The following specifics are stated without individual inline citations. Verify against the [canonical agent teams docs](https://code.claude.com/docs/en/agent-teams) before relying on them:

- `--team-size 3` CLI flag
- `TeammateIdle` and `TaskCompleted` hook names
- Exit-code-2 behavior for hooks (send feedback / prevent completion)
- `$CLAUDE_TEAMMATE_OUTPUT` environment variable
- v2.1.73 model inheritance fix version
- v2.1.69 `agent_id`/`agent_type` hook fields version

## Related

- [Sub-Agents](sub-agents.md)
- [Claude Code Hooks](hooks-lifecycle.md)
- [Claude Code Feature Flags and Environment Variables](feature-flags.md)
- [Claude Agent SDK](agent-sdk.md)
- [Fan-Out Synthesis](../../multi-agent/fan-out-synthesis.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../../multi-agent/sub-agents-fan-out.md)
- [Committee Review Pattern](../../code-review/committee-review-pattern.md)
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](../../observability/agent-observability-otel.md)
- [Claude Code /batch and Worktrees](batch-worktrees.md)
- [Claude Code Extension Points](extension-points.md)
- [Session Scheduling](session-scheduling.md)
