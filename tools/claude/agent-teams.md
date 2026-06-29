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
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-14
status: current
---

# Claude Code Agent Teams

> Agent teams coordinate multiple Claude Code sessions with shared task lists, direct messaging, and a team lead.

## How they work

[Agent teams](https://code.claude.com/docs/en/agent-teams) are an experimental Claude Code feature that needs v2.1.32 or later. Multiple sessions coordinate as a team. One session acts as team lead, assigning tasks and synthesizing results. Teammates work independently in their own context windows. They share a task list and message each other directly through a mailbox, rather than routing everything through the lead.

Enable the feature with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` in `settings.json` or as an environment variable. Then describe the team in natural language. Claude creates the team, spawns teammates, and coordinates the work from your prompt. There is no `--team-size` CLI flag; team size is part of the prompt.

!!! warning "Experimental — details may change"
    The feature flag, hook names, and environment variables on this page reflect the canonical [agent teams docs](https://code.claude.com/docs/en/agent-teams). Check the reference for the latest specifics.

## Teams vs sub-agents

| | Sub-Agents | Agent Teams |
|---|---|---|
| Communication | One-way (result to parent) | Two-way (direct messaging) |
| Coordination | Parent orchestrates | Teammates self-coordinate |
| Context | Fresh, isolated | Independent but can share findings |
| State | Ephemeral | Persistent within session |

Use sub-agents when you need quick, focused workers. Use agent teams when your agents need to share findings, challenge each other, and coordinate on their own.

Sub-agents can now nest. The [Claude Code changelog](https://code.claude.com/docs/en/changelog) records support for multi-level sub-agent nesting — sub-agents spawning sub-agents up to five levels deep — alongside nested-usage attribution headers that trace token usage back through the spawn chain. This differs from agent teams, where teammates still cannot spawn their own teams (see [when this backfires](#when-this-backfires)).

## Model inheritance

Team agents inherit the model configured on the leader. The [Claude Code v2.1.73 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) records two related fixes: "Fixed team agents to inherit the leader's model" and "Fixed subagents with `model: opus`/`sonnet`/`haiku` being silently downgraded to older model versions on Bedrock, Vertex, and Microsoft Foundry". Before that release, teammates could run on a different model than the lead even when nothing was set explicitly.

## Per-agent observability

Hook events include `agent_id` and `agent_type` fields, added in [v2.1.69](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md). These let hooks tell the team lead, teammates, and sub-agents apart. Use them to apply different enforcement rules per agent role, or to tag audit logs with agent identity. For example, let the lead push to a remote while teammates stay local.

## Hooks for teams

The canonical [hooks reference](https://code.claude.com/docs/en/agent-teams#enforce-quality-gates-with-hooks) documents three team-specific hook events:

- `TeammateIdle`: runs when a teammate is about to go idle — exit with code 2 to send feedback and keep the teammate working
- `TaskCreated`: runs when a task is being created — exit with code 2 to block creation and send feedback
- `TaskCompleted`: runs when a task is being marked complete — exit with code 2 to block completion and send feedback

## Best for

Use teams for research and review tasks, building new modules or features, debugging with competing hypotheses, and cross-layer coordination where different agents need different perspectives on the same codebase.

## Example

This example shows three agents — a team lead and two teammates — coordinating on a security audit. The team lead spawns teammates and they share findings via the mailbox rather than routing through the lead.

Enable the feature flag in `settings.json` before starting:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

With the flag set, describe the team in natural language inside a Claude Code session. The lead decides how many teammates to spawn unless you specify explicitly:

```text
Create an agent team to audit the authentication module. Spawn two reviewers:
one investigates the token lifecycle, one investigates session management.
Have them share findings with each other and synthesise a security report.
```

Claude creates the team, spawns the teammates, assigns tasks from a shared task list, and cleans up when the work is finished. In in-process mode, use Shift+Down to cycle through teammates and message them directly.

The `TaskCompleted` hook gates task completion. This helps when a synthesis step must check that all subtask outputs exist before the lead closes the task. Exit code 2 sends feedback and blocks the completion:

```bash
# .claude/hooks/TaskCompleted.sh
#!/usr/bin/env bash
# Block task completion until findings.md has been written
if [ ! -s findings.md ]; then
  echo "findings.md is empty or missing — record the synthesis before marking the task complete." >&2
  exit 2
fi
exit 0
```

The `TeammateIdle` hook works the same way for teammates about to stop: exit 2 re-prompts the teammate with feedback instead of letting it go idle.

## When this backfires

The canonical docs list concrete [limitations](https://code.claude.com/docs/en/agent-teams#limitations) that make teams the wrong choice for some work:

- Token costs scale linearly. Each teammate is a full Claude Code instance with its own context window, so a 5-person team burns roughly 5x the tokens of a single session. For sequential tasks or routine edits, one session is cheaper and faster.
- In-process teammates cannot resume. `/resume` and `/rewind` do not restore them. After a resume, the lead may try to message teammates that no longer exist.
- You get one team per session, no nested teams, and fixed leadership. The lead cannot be transferred, teammates cannot spawn their own teams, and cleanup must happen before a new team can start. Claude Code's file-locked task claiming prevents races, but it also rules out reshaping the team on the fly.
- File conflicts are easy to create. Two teammates editing the same file race each other. Teams need an up-front split of ownership. Without it, parallelism destroys work instead of speeding it up.
- Split-pane mode works in few terminals. It needs tmux or iTerm2 with the `it2` CLI, and it does not work in VS Code's integrated terminal, Windows Terminal, or Ghostty.

For sequential work, same-file edits, or anything with heavy dependencies, a single session or a [sub-agent](sub-agents.md) fan-out is more effective.

## Key Takeaways

- Teams enable multi-agent coordination with shared task lists and direct mailbox messaging
- Unlike sub-agents, teammates share findings and can challenge each other
- Team agents inherit the leader's model as of [v2.1.73](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- Experimental feature — enable explicitly in `settings.json`; requires v2.1.32 or later
- Team-specific hooks (`TeammateIdle`, `TaskCreated`, `TaskCompleted`) gate idle and task transitions

## Related

- [Sub-Agents](sub-agents.md)
- [Claude Code Hooks](hooks-lifecycle.md)
- [Claude Code Feature Flags and Environment Variables](feature-flags.md)
- [Claude Agent SDK](agent-sdk.md)
- [Fan-Out Synthesis](../../multi-agent/fan-out-synthesis.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../../multi-agent/sub-agents-fan-out.md)
- [Committee Review Pattern](../../code-review/committee-review-pattern.md)
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](../../observability/agent-observability-otel.md)
