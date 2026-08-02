---
title: "Persistent Teammate Workspace: Durable State for Agent Teams"
term: "Persistent Teammate Workspace"
description: "A per-teammate directory on disk that survives compaction and process exit — worth its token and security cost only when the team's work genuinely outlives one session."
tags:
  - agent-design
  - memory
  - claude
  - arxiv
aliases:
  - agent team work zone
  - teammate workstation
  - persistent agent workspace
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-02
maturity: emerging
---

# Persistent Teammate Workspace: Durable State for Agent Teams

> A per-teammate directory on disk carries an agent team's working state across compaction and process exit, which the transcript cannot.

A persistent teammate workspace gives each member of a [Claude Code agent team](../../tools/claude/agent-teams.md) its own directory holding the skills, hooks, and scripts that define how it works, plus periodic snapshots of its working state. The [Agent Team Work Zone paper](https://arxiv.org/abs/2607.22917v2) calls these directories workstations and pairs them with a single-command team restore. The pattern is narrow: it pays only under conditions most team runs do not meet.

## What Claude Code already keeps

Half the state people expect to lose already survives. Agent teams are experimental, so treat the layout below as version-bound. Claude Code stores a team's config at `~/.claude/teams/{team-name}/config.json` and its mailboxes at `~/.claude/teams/{team-name}/inboxes/{agent-name}.json`, while the shared task list lives separately under `~/.claude/tasks/{team-name}/`. Per the [agent teams documentation](https://code.claude.com/docs/en/agent-teams), "The team config directory is removed when the session ends. The task list directory persists locally and is never uploaded, so resumed sessions keep their tasks."

Tasks survive a resume. Teammate conversation state and mailboxes do not, and the docs are explicit: "`/resume` and `/rewind` do not restore in-process teammates. After resuming a session, the lead may attempt to message teammates that no longer exist."

## When a workspace earns its cost

Add one only when all four hold:

- The work outlives a single session. If the team runs to completion before any compaction or exit, nothing was at risk and the workspace was pure overhead.
- State is keyed on stable role identity, not team identity. Team names are `session-` plus the first eight characters of the session ID ([agent teams docs](https://code.claude.com/docs/en/agent-teams)), so a workstation keyed that way is orphaned by the next session and silently never found again.
- Restored state is re-verified against the repository before it drives work. Stale content restores exactly as cleanly as fresh content.
- The restore path treats workspace files as untrusted input, not as instructions.

## Why it works

Compaction and process exit destroy the conversation transcript but not the filesystem, and Claude Code exposes hooks on both sides of that boundary. The [hooks reference](https://code.claude.com/docs/en/hooks) documents `PreCompact` firing before compaction with `manual` and `auto` matchers, `TeammateIdle` firing when a teammate is about to go idle, and `SessionStart` firing with source `compact`, `resume`, or `startup` — with `SessionStart` stdout "added as context that Claude can see and act on." A write on the way out and a read on the way back in therefore carry working state across a boundary summarization cannot cross, at full fidelity.

For a teammate, disk is the only channel available. A teammate loads CLAUDE.md, MCP servers, skills, and its spawn prompt, and "the lead's conversation history does not carry over." Role definitions do not help: a subagent definition's `skills` and `mcpServers` fields "are not applied when that definition runs as a teammate" ([agent teams docs](https://code.claude.com/docs/en/agent-teams)). Durable role-specific behavior has to live at a path the teammate reads.

## When this backfires

- It becomes a stored-injection channel. [Xie et al. (2026)](https://arxiv.org/abs/2606.04425v2) name "memories, filesystems, tools, and other long-lived contextual artifacts" as persistent state across which injected instructions "can silently persist and influence future executions long after the original attacker interaction has ended." A `SessionStart` hook that replays a workstation into context is exactly that path. Their conclusion: the problem "is not merely filtering untrusted inputs, but governing how external information acquires authority as it crosses persistent system boundaries."
- Curated state can lower accuracy. In [Zhou et al. (2026)](https://arxiv.org/abs/2607.26637v1), a strong execution agent scored 87.1% working from a verbatim episode log against 82.1% from curated skills, and curation cost never amortized — roughly $10 to $11 per 140 tasks against zero for an append-only log. Tidying costs quality on exactly the models most likely to run a team.
- The token bill compounds where it is already worst. Anthropic's [cost guidance](https://code.claude.com/docs/en/costs) reports that "Agent teams use approximately 7x more tokens than standard sessions when teammates run in plan mode." Replaying a workspace at every boundary for every teammate multiplies that line.
- It keeps a team alive past the point of usefulness. The same agent teams docs advise that "Letting a team run unattended for too long increases the risk of wasted effort." Sometimes the right answer to lost teammate state is a shorter team whose durable output is commits and findings in the repository, where review already governs it — see [git-bound memory](git-bound-memory.md).

## Key Takeaways

- Claude Code already persists a team's task list across resume; teammate conversation state and mailboxes are what a workspace actually recovers
- `PreCompact` or `TeammateIdle` to write and `SessionStart` to read is the documented hook pair that carries state across a compaction or exit boundary
- Disk is the only durable channel a teammate has — the lead's history does not carry over and a subagent definition's `skills` field is ignored for teammates
- Key the workspace on stable role identity, never on the session-derived team name, or the next session will never find it
- A replayed workspace is untrusted input and a stored-injection channel; treat it as data and re-verify restored state before acting on it
- Skip the pattern when the work fits in one session, when tokens are the binding constraint, or when a strong model would do better on a raw log

## Related

- [Claude Code Agent Teams](../../tools/claude/agent-teams.md) — the feature this pattern extends, including the resumption limitation it works around
- [Session Recap: Goal-Shaped Handoff at Context Boundaries](session-recap.md) — the single-agent artifact written at one boundary, where this pattern spans a whole team
- [Clock-In / Clock-Out Protocol](clock-in-clock-out-protocol.md) — the read-on-entry, write-on-exit discipline the hook pair here automates
- [Long-Running Agents: Durability, Checkpoints, and Resumability](long-running-agents.md) — the broader operating shape for work that outlives one session
- [Organizing Filesystem Agent Memory for Retrieval Cost](filesystem-memory-organization.md) — the measured cost and quality trade-offs of curated filesystem state
- [Git-Bound Memory](git-bound-memory.md) — the alternative durable substrate when review, not restore, is what the state needs
