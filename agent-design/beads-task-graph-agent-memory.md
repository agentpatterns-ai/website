---
title: "Beads: Structured Task Graphs as External Agent Memory"
description: "Use the bd CLI to maintain a git-backed dependency graph of work items so agents resume sessions without re-discovering project state from scratch."
aliases:
  - "bd CLI"
  - "Beads task graph"
tags:
  - agent-design
  - context-engineering
  - memory
---

# Beads: Structured Task Graphs as External Agent Memory

> Use the `bd` CLI to maintain a git-backed dependency graph of work items so agents resume sessions methodically rather than re-discovering project state from scratch.

## The Problem

Agents restart cold each session. When work spans many sessions, agents rediscover completed steps, re-derive task order, and generate redundant plans. Steve Yegge coined this the "50 First Dates" problem [unverified — original source for this attribution not located]: every conversation is the agent's first.

Markdown plan files make the problem worse. Agents produce new plan files each session, none referencing the others. After weeks of development, a plans/ directory accumulates hundreds of overlapping, partially-complete files. When context is tight, agents hallucinate completion, skip phases, and disavow discovered problems rather than log them.

## How Beads Works

[Beads (`bd`)](https://github.com/steveyegge/beads) stores tasks in a [Dolt](https://github.com/dolthub/dolt)-powered version-controlled database committed to git as a `.beads/` directory, giving agents both queryability and full git versioning.

### Task Structure

Each task is a first-class object with:

- **Status**: `open`, `in_progress`, `blocked`, `closed`
- **Priority**: 0 (critical) to 4 (backlog)
- **Dependency edges**: `blocks`, `depends_on`, `relates_to`, `parent-child` (epics)
- **Hash-based ID**: `bd-a1b2` format — prevents merge conflicts across parallel agents or branches

Tasks nest into epics using dotted IDs:

```
bd-a3f8        (Epic)
bd-a3f8.1      (Task)
bd-a3f8.1.1    (Sub-task)
```

### Agent Interface

The core agent interface is [`bd ready`](https://github.com/steveyegge/beads), which lists tasks with no open blockers. Agents query this at session start instead of reading plans or re-deriving state.

```bash
bd init                           # initialise in project root
bd create "Add auth middleware" -p 1   # create a priority-1 task
bd dep add bd-a1b2 bd-c3d4        # bd-a1b2 blocks bd-c3d4
bd update bd-a1b2 --claim         # atomically claim (sets assignee + in_progress)
bd ready                          # list unblocked tasks
bd update bd-a1b2 --status closed # mark done [unverified: exact flag syntax]
```

`--claim` is atomic: it sets both assignee and status in one operation, preventing two parallel agents from acquiring the same task.

### Semantic Compaction

Closed tasks are semantically summarised over time rather than retained in full. This bounds context overhead as work accumulates — long-lived projects do not pay an unbounded context cost for completed history.

## What Beads Tracks vs. What Memory Patterns Track

Beads tracks *work state* — what is done, what is blocked, what is next. It does not replace knowledge memory systems ([CLAUDE.md](../instructions/claude-md-convention.md), [agent memory patterns](agent-memory-patterns.md)), which track *learned conventions*: architectural decisions, codebase quirks, debugging solutions.

| Beads (`bd`) | Knowledge memory (CLAUDE.md) |
|---|---|
| What tasks exist and their status | Architectural decisions and rationale |
| Dependency order between work items | Codebase-specific conventions |
| Who claimed which task | Debugging solutions for recurring issues |
| What was discovered and filed mid-session | Team standards and tooling preferences |

Agents use `bd ready` to find what to do next; they consult CLAUDE.md to understand how to do it correctly.

## Multi-Agent Safety

Hash-based IDs (`bd-a1b2`) avoid merge conflicts when multiple agents create tasks in parallel on different branches. `bd update --claim` provides atomic task acquisition to prevent duplicate work within a shared session.

## Practical Setup

Install once, use across projects:

```bash
npm install -g @beads/bd   # or: brew install beads
cd your-project
bd init
echo "Use 'bd' for task tracking. Start each session with bd ready." >> AGENTS.md
```

The agent instruction in AGENTS.md is the only per-project change needed. Agents exposed to this convention spontaneously file new issues when they discover problems mid-session [unverified], rather than silently ignoring them to save context.

For personal use on shared or open-source projects, `bd init --stealth` keeps the `.beads/` directory local and untracked.

## Example

A two-agent workflow on a backend project uses Beads to coordinate across sessions:

```bash
# Session 1 — Agent A sets up the project graph
bd init
bd create "Implement user auth" -p 1          # bd-a1b2
bd create "Add rate limiting middleware" -p 2  # bd-c3d4
bd create "Write auth integration tests" -p 2 # bd-e5f6
bd dep add bd-a1b2 bd-e5f6                     # tests depend on auth

# Agent A claims and completes auth
bd update bd-a1b2 --claim
# ... implements auth ...
bd update bd-a1b2 --status closed
```

```bash
# Session 2 — Agent B picks up where Agent A left off
bd ready
# Output:
#   bd-c3d4  [P2] Add rate limiting middleware
#   bd-e5f6  [P2] Write auth integration tests

# Agent B discovers a missing migration while working
bd create "Add missing users table migration" -p 1  # bd-g7h8
bd dep add bd-g7h8 bd-e5f6                           # tests now blocked on migration

bd update bd-c3d4 --claim
# ... implements rate limiting ...
bd update bd-c3d4 --status closed
```

Agent B did not need to read plan files or ask what was already done. `bd ready` surfaced actionable tasks, and the new dependency (`bd-g7h8` blocking `bd-e5f6`) was recorded for the next session rather than lost.

## Key Takeaways

- `bd ready` gives agents a dependency-resolved list of unblocked tasks without requiring them to parse plan files or re-derive project state.
- Hash-based IDs and atomic `--claim` operations make Beads safe for parallel agents working on the same project.
- Semantic compaction keeps context overhead bounded over long-lived projects.
- Beads tracks work state; knowledge memory systems track conventions — the two complement rather than replace each other.
- A single line in AGENTS.md activates the pattern for any agent on the project.

## Related

- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — broader survey of memory strategies for agents
- [Episodic Memory Retrieval](episodic-memory-retrieval.md) — retrieving past interaction episodes to improve first moves on recurring problems
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md) — complementary approach storing memory at the granularity of individual reasoning stages
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md) — turning agent execution traces into persistent knowledge
- [Session Initialization Ritual: How Agents Orient Themselves](session-initialization-ritual.md) — the startup sequence that pairs with `bd ready` for full session orientation
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](../instructions/hierarchical-claude-md.md) — how CLAUDE.md knowledge memory is scoped across project, user, and local levels
- [File-Based Agent Coordination](../multi-agent/file-based-agent-coordination.md)
- [Seeding Agent Context: Breadcrumbs in Code](../context-engineering/seeding-agent-context.md)
- [Encode Project Conventions in Distributed AGENTS.md Files](../instructions/agents-md-distributed-conventions.md)
- [Context Engineering](../context-engineering/context-engineering.md) — the discipline of designing what enters an agent's context window to maximise output quality
