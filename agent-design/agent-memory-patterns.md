---
title: "Agent Memory Patterns: Learning Across Conversations"
description: "Persist knowledge across conversations using scoped memory systems so agents accumulate institutional knowledge rather than starting fresh every session"
aliases:
  - Layered Context Architecture
  - Multi-Layer Context Grounding
  - Agent Memory Persistence
  - Persistent Scoped Corrections
  - Non-Obvious Corrections Memory
tags:
  - context-engineering
  - agent-design
  - source:opendev-paper
  - memory
---

# Agent Memory Patterns: Learning Across Conversations

> Persist knowledge across conversations using scoped memory systems so agents accumulate institutional knowledge rather than starting fresh every session.

!!! info "Also known as"
    Layered Context Architecture, Multi-Layer Context Grounding, Agent Memory Persistence, Persistent Scoped Corrections, Non-Obvious Corrections Memory

## Memory Scopes

Every agent conversation starts with an empty context. [Claude Code's memory system](https://code.claude.com/docs/en/memory) defines three scopes:

| Scope | Storage | Sharing | Use For |
|-------|---------|---------|---------|
| Managed Policy | Org-level configuration | Org-wide, admin-controlled | Org standards, compliance rules |
| Project | `CLAUDE.md` or `.claude/CLAUDE.md` | Version-controlled, shared | Architecture decisions, conventions |
| User | `~/.claude/CLAUDE.md` | Cross-project, personal | Cross-repo preferences, tool config |

[Sub-agents](https://code.claude.com/docs/en/sub-agents) can operate with their own scopes. Use project scope for team conventions and user scope for personal preferences — mixing them degrades the experience for one party.

## Temporal Memory: Episodic and Working

Scope organizes memory by *where* it lives. OPENDEV adds a temporal dimension separating cross-session recall from within-session observations ([Bui, 2026 §2.3.3](https://arxiv.org/abs/2603.05344)).

**Episodic memory** persists across sessions: the agent summarizes key decisions and failed approaches at session end, re-injected on the next start.

**Working memory** is session-scoped: observations accumulated during execution, re-injected each iteration, bounded to prevent context growth. Episodic maps to project or user scope; working maps to session-local state.

## What to Persist

Effective memory entries are stable, general, and verified.

**Persist:** architectural decisions and rationale, conventions that deviate from defaults, recurring debugging solutions, non-obvious API behaviors.

**Do not persist:** session-specific state, single-case conclusions, instructions duplicating code comments or AGENTS.md, unverified hypotheses.

### Non-Obvious Corrections: The Highest-Value Memory Category

[OpenAI's data agent](https://openai.com/index/inside-our-in-house-data-agent/) targets "non-obvious corrections, filters, and constraints critical for correctness but difficult to infer from other layers alone." General model knowledge does not belong in memory — only domain-specific deviations the model would otherwise get wrong. Examples:

- "`sessions` excludes first-party traffic — always filter `source_type = 'third_party'` for comparable metrics"
- "API key rotation in March 2024 split auth schemes for earlier data"
- "This client's 'active user' definition excludes weekend-only users"

### Proactive Save Prompts

When the agent receives a correction, it should prompt the user to save it ([OpenAI's data agent](https://openai.com/index/inside-our-in-house-data-agent/)). Without the prompt, corrections evaporate at session end.

## Memory vs. Codebase Breadcrumbs

Memory and [seeded codebase context](../context-engineering/seeding-agent-context.md) serve different purposes:

| Memory | Seeded Context |
|--------|---------------|
| What the agent learned from work | What humans want agents to know |
| Agent-authored | Human-authored |
| Follows the agent across sessions | Follows the codebase |
| Scoped to agent or project | Scoped to directory or file |

For shared conventions, seeded context (AGENTS.md, inline comments) is more appropriate. Memory suits knowledge the agent discovers and applies repeatedly.

## Why It Works

Without external persistence, the agent rediscovers the same facts — codebase conventions, recurring failure modes, domain-specific exceptions — on every session. Injecting relevant prior knowledge at session start lets the model reason from accumulated state rather than ground zero; OPENDEV measured a ~30% drop in redundant exploration from eliminating these re-discovery loops ([Bui, 2026 §2.3.3](https://arxiv.org/abs/2603.05344)). Scoping prevents cross-contamination: org policies stay separate from personal preferences, so one user's corrections don't override another's conventions.

## When This Backfires

Persistent memory introduces failure modes an amnesiac agent avoids:

- **Stale entries silently degrade output.** A correction accurate six months ago may now contradict a refactored API. The agent applies it confidently because it has no way to know the context changed.
- **Contradictory entries produce unpredictable behavior.** When conflicting instructions accumulate — an updated rule added without removing the old one — the agent guesses which is correct, producing inconsistent results.
- **High-volume environments cause context pollution.** Agents across many domains or users fill memory with low-signal entries that dilute retrieval quality and exceed token budgets.
- **Shared-scope memory creates coordination problems.** Concurrent writes to shared project memory can introduce race conditions or leave stale artifacts visible after updates ([multi-agent memory challenges](https://arxiv.org/html/2603.10062v1)).

Use memory only for stable, general, verified facts. Establish a curation cadence: review entries that haven't influenced behavior in several sessions and either revalidate or remove them.

## Example

A project `CLAUDE.md` for a data pipeline codebase with scoped memory entries:

```markdown
# Project Memory

## Architecture
- ETL runs in three stages: extract → validate → load. Never skip validate, even for small datasets.
- The `runs` table is append-only; use `run_id` to identify the latest state per job.

## Non-Obvious Corrections
- `sessions` excludes first-party traffic — always filter `source_type = 'third_party'` for comparable metrics.
- API key rotation (March 2024) split auth schemes: queries spanning that date require two separate credential sets.

## Preferences [user-level, not committed]
- Output diffs, not full file rewrites, when editing existing code.
- Prefer `pytest` fixtures over `setUp`/`tearDown` in new tests.
```

The first two sections belong in the project `CLAUDE.md` (version-controlled, shared). The third belongs in `~/.claude/CLAUDE.md` (personal, not committed).

## Related

- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [CLAUDE.md Convention](../instructions/claude-md-convention.md)
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](../instructions/hierarchical-claude-md.md)
- [Seeding Agent Context: Breadcrumbs in Code](../context-engineering/seeding-agent-context.md)
- [Context Priming](../context-engineering/context-priming.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Layered Context Architecture](../context-engineering/layered-context-architecture.md)
- [Session Initialization Ritual](session-initialization-ritual.md)
- [Episodic Memory Retrieval](episodic-memory-retrieval.md)
- [Agent Harness: Initializer and Coding Agent](agent-harness.md)
- [Model a Single Agent Turn](agent-turn-model.md)
- [Beads: Structured Task Graphs as External Agent Memory](beads-task-graph-agent-memory.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Claude Code Sub-Agents](../tools/claude/sub-agents.md)
- [Context Engineering](../context-engineering/context-engineering.md)
- [Agent Self-Review Loop](agent-self-review-loop.md)
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md)
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md)
- [AST-Guided Agent Memory for Repository-Level Code Generation](ast-guided-agent-memory.md)
- [Memory Reinforcement Learning](memory-reinforcement-learning.md)
- [Generative Agents Memory Stream](generative-agents-memory-stream.md)
