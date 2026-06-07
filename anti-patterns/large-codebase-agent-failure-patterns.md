---
title: "Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)"
description: "Five named failure shapes coding agents exhibit in 400K+ LOC codebases — lost in the codebase, wrong symbol, partial completion, tool thrashing, context overflow."
tags:
  - anti-pattern
  - agent-design
  - workflows
  - tool-agnostic
aliases:
  - sourcegraph five failure patterns
  - large codebase agent failures
  - coding agent failure patterns
last_reviewed: 2026-06-02
---

# Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)

> Five repeatable failure shapes coding agents exhibit once a codebase passes roughly 400,000 lines — recognise each by its transcript signature before shipping the patch.

The Sourcegraph CodeScaleBench study scored 1,281 agent runs across 40+ open-source repositories in 9 languages and isolated five recurring failure patterns ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). Each is a transcript signature a reviewer can spot before merge.

## When This Applies

Apply it only when all three hold ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)): a codebase above ~400,000 LOC; a discovery-bound task where the agent must find which files to touch; and multi-file or cross-repo scope (a +0.209 F1 delta versus +0.085 single-repo). Single-file edits and hand-curated lists bypass the patterns.

## The Five Patterns

Each is a transcript signature paired with a remediation ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)):

1. **Lost in the Codebase** — the agent burns its timeout on `read`/`glob` chains with no edits. Fix: code search and indexing (+0.259 reward delta, 400K–2M LOC band).
2. **Wrong File, Wrong Symbol** — it picks the wrong symbol among dozens of similar matches. Fix: structural navigation (go-to-definition, find-references) short-circuits ambiguity grep cannot resolve.
3. **Partial Completion** — it edits some files and misses others — overlapping [premature completion](premature-completion.md) but rooted in discovery failure, not verification skip. Fix: hybrid keyword + semantic + structural retrieval, the most contested remediation (see below).
4. **Tool Thrashing** — Sourcegraph saw 96 calls against an optimal of 5. The same signature surfaces in autocompact loops that refill context within a few turns of compaction ([anthropics/claude-agent-sdk-python#958](https://github.com/anthropics/claude-agent-sdk-python/issues/958)). Fix: task-aware retrieval.
5. **Context Overflow** — it reads whole files, diluting signal despite finding the right ones — [the infinite context anti-pattern](infinite-context.md) triggered by discovery. Fix: fetch the function, type, and call site, not the file. All five remediations together: file recall 0.127 → 0.277, F1@5 0.099 → 0.262, 38% shorter runtime, 30% lower cost ([CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks)).

## Why It Works

All five share one cause: the working set exceeds what context plus search can carry. Below ~400K LOC the model holds it implicitly; above it, discovery degrades. Code intelligence externalises that indexing — precomputed import graphs, symbol tables, and reference chains let it retrieve rather than search ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). A 2026 study calls this the "Navigation Paradox": larger context windows do not remove the need for structural navigation, because architecturally critical but semantically distant files fall outside the model's attention without an index ([Zylos Research, 2026-04](https://zylos.ai/research/2026-04-19-codebase-intelligence-repository-understanding-ai-agents)).

## When This Backfires

- **Semantic retrieval for Partial Completion is contested.** Claude Code, Cursor, and Devin dropped vector-DB RAG for agentic search, which beat it on real code ([SmartScope, 2026](https://smartscope.blog/en/ai-development/practices/rag-debate-agentic-search-code-exploration/); [MindStudio, 2026](https://www.mindstudio.ai/blog/is-rag-dead-what-ai-agents-use-instead)). Hybrid retrieval is one answer among several.
- **Vendor-study framing.** Sourcegraph sells the remediation; a strong agentic-search harness may close the gap without indexing.
- **Polyglot or build-broken repos.** Structural navigation needs a working build — references degrade silently when compilation fails or no unified cross-language index exists.
- **Task restructuring beats infrastructure.** Per-repo PRs or scoping to one component often cost less than indexing a monorepo.

## Example

A reviewer reads an agent transcript on a 1.2M LOC monorepo and observes:

```
[turn 7]  glob "**/User*.java"          → 287 matches
[turn 8]  read User.java                → 4.2 KB
[turn 9]  read UserService.java         → 8.7 KB
...
[turn 24] read UserMapper.java          → 3.1 KB
[turn 25] edit UserService.java         → patch landed
[turn 26] declare task complete
```

Three patterns visible in one transcript:

- **Lost in the Codebase** at turns 7–24: 17 read calls without a single targeted lookup.
- **Wrong File, Wrong Symbol** at turn 25: the agent edited `UserService` when `UserAccountService` — also in the match set — was the change site for the bug report's "user account creation."
- **Partial Completion** at turn 26: the service-layer patch missed the matching repository and controller; three subclasses still reference the old contract.

A reviewer who spots these signatures stops the PR and either asks the agent to widen the change set or hands it find-references on the changed signature to enumerate the affected sites.

## Key Takeaways

- The five patterns — Lost in the Codebase, Wrong File / Wrong Symbol, Partial Completion, Tool Thrashing, Context Overflow — are sourced from 1,281 agent runs across 40+ repos and surface as observable transcript signatures ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).
- The catalogue applies above ~400K LOC and to discovery-bound, multi-file tasks. Below that, standard tools suffice.
- The mechanism is shared: the agent's working set exceeds what context plus naive search can carry, so externalised indexing replaces failed implicit search.
- Code intelligence on the recommended band delivered +0.259 reward delta, file recall 0.127 → 0.277, and F1@5 0.099 → 0.262 ([CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks)).
- The semantic-retrieval remediation for Partial Completion is contested — Claude Code, Cursor, and Devin dropped vector-DB RAG in favour of agentic search ([SmartScope, 2026](https://smartscope.blog/en/ai-development/practices/rag-debate-agentic-search-code-exploration/)).
- Use the patterns as a transcript-review checklist; treat the specific Sourcegraph stack as one remediation among several.

## Related

- [Five-Failure-Layers Diagnostic](../agent-design/five-failure-layers-diagnostic.md) — complementary layer-attribution ladder; this catalogue names behavioural symptoms, the diagnostic names the harness layer responsible.
- [Premature Completion](premature-completion.md) — verification-skip failure that overlaps with Partial Completion's transcript signature; root cause differs.
- [The Infinite Context](infinite-context.md) — the deliberate version of Context Overflow; same attention-dilution mechanism, different trigger.
- [Refactoring Runaway](refactoring-runaway.md) — adjacent multi-file failure where the agent does too much rather than too little.
- [Comprehension Debt](comprehension-debt.md) — the human-side consequence of agents that ship partial completions through merge without the team noticing the gap.
