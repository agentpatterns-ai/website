---
title: "Agent Project State Purge: Clean-Slate Session Reset"
term: "Agent Project State Purge"
description: "A clean-slate primitive for tearing down per-project session state when contamination is the real diagnosis, not an instruction-file bug."
tags:
  - agent-design
  - memory
  - workflows
  - claude
aliases:
  - project state nuke
  - session state reset primitive
last_reviewed: 2026-06-01
maturity: adopted
---

# Agent Project State Purge: Clean-Slate Session Reset

> A primitive that tears down per-project session state — transcripts, auto-memory, indexed sessions — when contamination is the diagnosis, not an instruction or hook bug.

A project state purge deletes every artifact a coding-agent harness built up for one project — transcripts, auto-memory, sessions index, and the harness's project record. Claude Code v2.1.126 (May 1, 2026) added `claude project purge [path]` with `--dry-run`, `-y/--yes`, `-i/--interactive`, and `--all` ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). It matters because long-running projects build up stale plans and half-finished todos that bias future sessions. Without it, operators hand-edit state files they do not understand.

## When the purge is the right move

The trigger is specific: the agent keeps proposing the old plan after you changed direction. Error output that was useful at turn 5 becomes misleading at turn 40 ([TianPan.co: Stale World Model Problem](https://tianpan.co/blog/2026-04-10-stale-world-model-long-running-agents)).

Run this diagnostic gate before you reach for the purge:

1. Is the direction stale in `CLAUDE.md` or a rule file? Edit the file. Purging will not help, because the next session re-reads the same stale instruction.
2. Is a hook auto-injecting an old recap or progress file? The hook is the bug, so disable or fix it.
3. Is one session contaminating the rest? Use `/resume` and abandon that session rather than wipe the project record.
4. Has the direction genuinely changed? A post-mortem hand-off, scope inversion, or abandoned approach is what the primitive is for.

## What survives, what dies

Claude Code's `.claude/` directory separates project source (version-controlled files the team shares) from project state (the ambient files the harness writes) ([Claude Code: Explore the .claude directory](https://code.claude.com/docs/en/claude-directory)). The purge crosses only the second boundary.

| Surface | Survives `claude project purge` |
|---------|---------------------------------|
| `CLAUDE.md` (project + global) | Yes — project source |
| `.claude/settings.json`, hooks, skills, agents, commands | Yes — project source |
| `.mcp.json` | Yes — project source |
| `~/.claude/projects/<project>/<session-id>.jsonl` (transcripts) | No — deleted |
| `~/.claude/projects/<project>/memory/` (auto-memory the agent wrote) | No — deleted |
| `~/.claude/projects/<project>/sessions-index.json` | No — deleted |
| Claude Code's per-project config entry | No — deleted |

Instruction surfaces and tool-source files stay untouched, so the next session boots against the same rules and skills but rebuilds context from current code rather than persisted history.

## How it works

```mermaid
graph TD
    A[Agent proposes stale plan] --> B{Diagnostic gate}
    B -->|Instruction bug| C[Fix CLAUDE.md / rule / hook]
    B -->|One bad session| D[Abandon via session picker]
    B -->|Direction genuinely changed| E[claude project purge --dry-run]
    E --> F[Review what would be deleted]
    F --> G{Snapshot for forensics?}
    G -->|Yes| H[Copy ~/.claude/projects/<project>/ aside]
    G -->|No| I[claude project purge -y]
    H --> I
    I --> J[Next session boots from authoritative sources]
```

Three modes matter:

- `--dry-run` lists what would be deleted without touching disk. Run it first; a wrong inventory means a wrong diagnosis.
- `-i/--interactive` lets the operator pick which sessions to drop, for when only part of the record is contaminated.
- `-y` (with or without `--all`) is the unattended form. Reserve it for batch cleanups in disposable environments.

The snapshot-then-purge variant (`cp -r ~/.claude/projects/<project> /tmp/backup-$(date +%s) && claude project purge -y`) keeps the JSONL audit trail; without it, you delete the diagnostic record at the worst moment.

## Why it works

Each kind of state under `~/.claude/projects/<project>/` loads back on resume ([Claude Code: Manage sessions](https://code.claude.com/docs/en/sessions)). When it diverges from current intent, the next session rebuilds the old objective on a wrong goal — the "stale world model" failure, where agents look operational while reasoning on outdated information ([TianPan.co](https://tianpan.co/blog/2026-04-10-stale-world-model-long-running-agents)).

A purge breaks that loop. An empty baseline forces the next session to rebuild from current sources — `CLAUDE.md`, code, and prompt. Removing stale tokens is context engineering: every token competes for the model's attention ([Anthropic postmortem](https://www.anthropic.com/engineering/april-23-postmortem)).

## When this backfires

The purge is the wrong move under four conditions:

- Purging masks an instruction bug. If `CLAUDE.md` still holds the old direction, or a `SessionStart` hook auto-injects an old recap, the purge wipes the symptom and the bug returns next session. If this recurs weekly, fix upstream — narrower rules, tighter hooks, smaller [recap schemas](session-recap.md).
- Purging destroys cross-session learning. Auto-memory under `~/.claude/projects/<project>/memory/` holds build commands, debugging insights, and architecture notes — the durable asset [agent memory patterns](agent-memory-patterns.md) describe. On the LOCOMO benchmark, persistent-memory architectures outperform stateless approaches ([Mem0 research](https://mem0.ai/research-3)), so reflexive purges undo what that memory was meant to compound.
- No backup before a purge means no forensics. The per-session JSONL files are the audit trail, and `--dry-run` does not preserve them — only an explicit copy does.
- Tool-agnostic harnesses lack an equivalent. Copilot CLI has `/clear` and `/reset` in-session but no per-session-folder deletion, so users manually `rm -rf ~/.copilot/session-state/` ([open request](https://github.com/github/copilot-cli/issues/2869)). The advice does not port across tools until equivalents ship.

## Example

A team spent two weeks on a refactor that the architect canceled this morning. The next agent session opens with "let's continue the dependency-injection migration on `UserService`" — the abandoned direction, not the new one.

Before, without a purge, hand-editing state:

```bash
# The operator tries to find and remove just the stale auto-memory
$ ls ~/.claude/projects/-home-team-app/
ce8f2a3b-...jsonl  7d2e1f4c-...jsonl  memory/  sessions-index.json
$ rm -rf ~/.claude/projects/-home-team-app/memory/
# Did that work? The next session still has 47 JSONL transcripts to pick from.
# The session picker resurfaces a transcript from yesterday — same stale plan.
```

After, using the primitive:

```bash
$ claude project purge ~/team/app --dry-run
Would delete:
  ~/.claude/projects/-home-team-app/  (47 sessions, 12.4 MB)
  config entry for /home/team/app

$ cp -r ~/.claude/projects/-home-team-app /tmp/backup-$(date +%s)
$ claude project purge ~/team/app -y
Deleted 47 sessions and project config entry.

$ claude --continue
# No prior session found in this directory.
# The next prompt reads from current CLAUDE.md and current code only.
```

The `CLAUDE.md`, hooks, skills, and `.mcp.json` remain untouched. The team's new architectural direction is the only state the next session sees.

## Key Takeaways

- A project state purge is a primitive for the specific case where stale persisted state is biasing the next session — not a routine cleanup command
- Diagnose before purging: rule out instruction-file bugs, hook bugs, and one-session contaminators first
- Project source files (`CLAUDE.md`, hooks, skills, settings, `.mcp.json`) survive; project state (transcripts, auto-memory, sessions index, config entry) does not
- Snapshot before unattended purges if you need a forensic trail — the per-session JSONL files are the audit record
- Claude Code's `claude project purge` (v2.1.126, May 2026) is the only first-class implementation today; Copilot CLI users do the equivalent manually

## Related

- [Session Recap: Goal-Shaped Handoff at Context Boundaries](session-recap.md) — the goal-shaped handoff that purge is the opposite of; preserve when continuation is right, purge when reset is right
- [Agent Memory Patterns](agent-memory-patterns.md) — the cross-session memory layer a purge wipes; understand what is being destroyed
- [Session Initialization Ritual](session-initialization-ritual.md) — what every session does after a purge, when there is no prior state to read
- [Post-Compaction Re-read Protocol](../../instructions/post-compaction-reread-protocol.md) — a softer intervention for instruction-fidelity drift, distinct from a state nuke
- [Trajectory Logging via Progress Files and Git History](../../observability/trajectory-logging-progress-files.md) — the persistent audit surface a purge does not touch, useful as the source-of-truth that survives reset
