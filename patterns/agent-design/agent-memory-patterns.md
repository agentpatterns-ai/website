---
title: "Agent Memory Patterns: Learning Across Conversations"
term: "Agent Memory Patterns"
description: "Persist knowledge across conversations using scoped memory systems so agents accumulate institutional knowledge rather than starting fresh every session."
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
  - tool-agnostic
last_reviewed: 2026-08-13
maturity: established
---

# Agent Memory Patterns: Learning Across Conversations

> Persist knowledge across conversations using scoped memory systems so agents accumulate institutional knowledge rather than starting fresh every session.

!!! info "Also known as"
    Layered Context Architecture, Multi-Layer Context Grounding, Agent Memory Persistence, Persistent Scoped Corrections, Non-Obvious Corrections Memory

## Memory scopes

Every agent conversation starts with an empty context. [Claude Code's memory system](https://code.claude.com/docs/en/memory) defines three scopes:

| Scope | Storage | Sharing | Use For |
|-------|---------|---------|---------|
| Managed Policy | Org-level configuration | Org-wide, admin-controlled | Org standards, compliance rules |
| Project | `CLAUDE.md` or `.claude/CLAUDE.md` | Version-controlled, shared | Architecture decisions, conventions |
| User | `~/.claude/CLAUDE.md` | Cross-project, personal | Cross-repo preferences, tool config |

[Sub-agents](https://code.claude.com/docs/en/sub-agents) can operate with their own scopes. Use project scope for team conventions and user scope for personal preferences — mixing them degrades the experience for one party.

The scope idea is not Claude-specific. LangChain frames the same problem vendor-neutrally: memory has a scope (which conversations it applies to) backed by a store, plus explicit write and read mechanics that decide when a fact is saved and when it is recalled ([LangChain — How to give your agent memory](https://blog.langchain.com/blog/how-to-give-your-agent-memory)). IDE plugins ship it too: GitHub added Copilot memory to GitHub Copilot for JetBrains in August 2026 ([GitHub — Copilot memory and Ollama in GitHub Copilot for JetBrains](https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains)).

## Temporal memory: episodic and working

Scope organizes memory by where it lives. OPENDEV adds a temporal dimension that separates cross-session recall from within-session observations ([Bui, 2026 §2.3.3](https://arxiv.org/abs/2603.05344)).

Episodic memory persists across sessions. The agent summarizes key decisions and failed approaches at session end, then re-injects them on the next start.

Working memory is session-scoped. It holds observations gathered during execution, re-injected each iteration and bounded to prevent context growth. Episodic memory maps to project or user scope. Working memory maps to session-local state.

## What to persist

Effective memory entries are stable, general, and verified.

Persist these: architectural decisions and rationale, conventions that deviate from defaults, recurring debugging solutions, and non-obvious API behaviors.

Do not persist these: session-specific state, single-case conclusions, instructions that duplicate code comments or AGENTS.md, and unverified hypotheses.

### Non-obvious corrections: the highest-value memory category

[OpenAI's data agent](https://openai.com/index/inside-our-in-house-data-agent/) targets "non-obvious corrections, filters, and constraints critical for correctness but difficult to infer from other layers alone." General model knowledge does not belong in memory. Only store domain-specific deviations the model would otherwise get wrong. For example:

- "`sessions` excludes first-party traffic — always filter `source_type = 'third_party'` for comparable metrics"
- "API key rotation in March 2024 split auth schemes for earlier data"
- "This client's 'active user' definition excludes weekend-only users"

### Proactive save prompts

When the agent receives a correction, it should prompt you to save it ([OpenAI's data agent](https://openai.com/index/inside-our-in-house-data-agent/)). Without the prompt, corrections evaporate at session end.

## Memory versus codebase breadcrumbs

Memory and [seeded codebase context](../../context-engineering/seeding-agent-context.md) serve different purposes:

| Memory | Seeded Context |
|--------|---------------|
| What the agent learned from work | What humans want agents to know |
| Agent-authored | Human-authored |
| Follows the agent across sessions | Follows the codebase |
| Scoped to agent or project | Scoped to directory or file |

For shared conventions, seeded context (AGENTS.md, inline comments) fits better. Memory suits knowledge the agent discovers and applies repeatedly.

## Why it works

Without external persistence, the agent rediscovers the same facts — codebase conventions, recurring failure modes, domain-specific exceptions — on every session. Injecting relevant prior knowledge at session start lets the model reason from accumulated state rather than ground zero. OPENDEV pairs a cross-session memory pipeline that accumulates project-specific knowledge with persistent context that lets agents "build on past attempts rather than starting fresh," reducing redundant exploration ([Bui, 2026](https://arxiv.org/abs/2603.05344)). Scoping prevents cross-contamination: org policies stay separate from personal preferences, so one user's corrections don't override another's conventions.

## When this backfires

Persistent memory introduces failure modes an amnesiac agent avoids:

- Stale entries silently degrade output. A correction that was accurate six months ago may now contradict a refactored API. The agent applies it confidently because it cannot tell the context changed.
- Contradictory entries produce unpredictable behavior. Conflicting instructions accumulate in `CLAUDE.md` when someone adds an updated rule without removing the old one. The agent then guesses which is correct and produces inconsistent results.
- High-volume environments cause context pollution. Agents that span many domains or users fill memory with low-signal entries that dilute retrieval quality and exceed token budgets.
- Shared-scope memory creates coordination problems. Concurrent writes to shared project memory can introduce race conditions or leave stale artifacts visible after updates ([multi-agent memory challenges](https://arxiv.org/html/2603.10062v1)).

Use memory only for stable, general, verified facts. Establish a curation cadence: review entries that have not influenced behavior in several sessions, then revalidate or remove them.

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

## FAQ

**What should never go into memory?**

Session-specific state, single-case conclusions, unverified hypotheses, and instructions that merely duplicate code comments or AGENTS.md. General model knowledge does not belong there either — an entry earns its context cost only when it captures a domain-specific deviation the model would otherwise get wrong, such as a table that excludes first-party traffic or an auth split introduced by a key rotation.

**How does working memory differ from episodic memory?**

Episodic memory persists across sessions: the agent summarizes key decisions and failed approaches at session end, then re-injects them on the next start. Working memory is session-scoped, holding observations gathered during execution, re-injected each iteration and bounded to prevent context growth. Episodic memory maps to project or user scope; working memory maps to session-local state.

**What goes wrong when a team shares project memory?**

Concurrent writes to shared project memory can introduce race conditions or leave stale artifacts visible after updates ([multi-agent memory challenges](https://arxiv.org/html/2603.10062v1)). Scoping is the mitigation: keep team conventions in project scope and personal preferences in user scope, since mixing them degrades the experience for one party and org policies must stay separate from individual corrections.

## Key Takeaways

- Memory has two axes: *scope* (managed / project / user) decides who sees it, and *time* (episodic vs. working) decides whether it survives the session.
- The highest-value entries are non-obvious corrections — domain-specific deviations the model would otherwise get wrong — not facts already in the model's general knowledge.
- Persistent memory and seeded codebase context (AGENTS.md, comments) are complementary: memory captures what the agent learns, seeded context captures what humans want the agent to know.
- The dominant failure mode is rot: stale, contradictory, or low-signal entries silently degrade output, so a curation cadence is mandatory.
- Prompt the user to save corrections at the moment they happen; otherwise the lesson evaporates at session end.

## Related

- [Episodic Memory Retrieval](episodic-memory-retrieval.md)
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md)
- [Subtask-Level Memory for SE Agents](subtask-level-memory.md)
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md)
- [Generative Agents Memory Stream](generative-agents-memory-stream.md)
- [CoALA Memory Taxonomy Classifier](coala-memory-taxonomy-classifier.md) — classify-what taxonomy that complements this page's scope-based architecture
- [Continual-Learning Layers](continual-learning-layers.md) — update-target / persistence-scope taxonomy, a distinct lens on the same memory problem
- [CLAUDE.md Convention](../../instructions/claude-md-convention.md)
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](../../instructions/hierarchical-claude-md.md)
- [Seeding Agent Context: Breadcrumbs in Code](../../context-engineering/seeding-agent-context.md)
