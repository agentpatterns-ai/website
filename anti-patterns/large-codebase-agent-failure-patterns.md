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
last_reviewed: 2026-05-27
---

# Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)

> Five repeatable failure shapes coding agents exhibit once a codebase passes roughly 400,000 lines — recognise each by its transcript signature before shipping the patch.

The Sourcegraph CodeScaleBench study scored 1,281 agent runs across 40+ enterprise open-source repositories in 9 programming languages and isolated five recurring failure patterns ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). The patterns are behavioural — each has a transcript signature a reviewer can spot before merge, paired with a remediation measured against the same patches.

## When This Applies

The catalogue is qualified, not universal. Apply it when all three conditions hold ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)):

- **Codebase above ~400,000 LOC.** Below this threshold standard tools (`grep`, `read`, `glob`) suffice and code-intelligence infrastructure is overhead.
- **Discovery-bound task.** The patterns surface when the agent must locate which files to touch. Single-file edits, hand-curated file lists, and tightly-scoped refactors inside a known directory bypass them entirely.
- **Multi-file or cross-repo scope.** Sourcegraph measured a +0.209 F1 delta from code-intelligence tools on multi-repo tasks versus +0.085 on single-repo — the patterns scale with change-set dispersion, not just repo size.

## The Five Patterns

### 1. Lost in the Codebase

**Symptom signature.** The agent exhausts its timeout exploring files without producing output, following import chains that branch exponentially ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). The transcript shows long sequences of `read` or `glob` calls with no edits.

**Remediation.** Code search and indexing — Sourcegraph measured a +0.259 reward delta when intelligence tools were added for codebases in the 400K–2M LOC band ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).

### 2. Wrong File, Wrong Symbol

**Symptom signature.** The agent locates files matching search terms but selects the wrong symbol among dozens of similarly-named matches across the tree. The patch lands in the wrong module ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).

**Remediation.** Structural navigation — go-to-definition, find-references, type-hierarchy resolution. Compiler-driven navigation short-circuits textual ambiguity that pure grep cannot resolve.

### 3. Partial Completion

**Symptom signature.** The agent modifies some affected files but misses others, leaving the change set in an inconsistent state ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). The signature overlaps with [premature completion](premature-completion.md), but the root cause is discovery failure rather than verification skip.

**Remediation.** Hybrid retrieval combining keyword, semantic, and structural search to enumerate affected files comprehensively. This is the most contested remediation — see *When This Backfires* below.

### 4. Tool Thrashing

**Symptom signature.** Excessive tool calls with repeated backtracking — Sourcegraph observed 96 calls against an optimal of 5 on the same task ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). Token and time costs balloon. The same observable pattern surfaces in autocompact loops that refill context within a few turns of compaction ([anthropics/claude-agent-sdk-python#958](https://github.com/anthropics/claude-agent-sdk-python/issues/958)).

**Remediation.** Task-aware retrieval and context management — reduce unnecessary exploration through better initial search quality so the agent does not have to grope for the file set.

### 5. Context Overflow

**Symptom signature.** The agent reads entire file contents into context, diluting relevant signal with surrounding code despite having found the correct files ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). Closely related to [the infinite context anti-pattern](infinite-context.md) but triggered by discovery, not by deliberate overloading.

**Remediation.** Smart context selection via code intelligence — fetch the function, the type, the call site, not the file.

Aggregate effect across all five remediations on the same benchmark: file recall 0.127 → 0.277, Precision@5 0.140 → 0.478, F1@5 0.099 → 0.262, with 38% shorter execution time and 30% lower per-task cost ([CodeScaleBench](https://sourcegraph.com/blog/codescalebench-testing-coding-agents-on-large-codebases-and-multi-repo-software-engineering-tasks)).

## Why It Works

The five patterns share one root cause: the agent's effective working set exceeds what its context window plus naive search can carry. Below ~400K LOC the model can hold the working set implicitly; above it, the discovery step degrades together with everything downstream — symbol resolution, file selection, change application, context retention. Code intelligence works because it externalises the indexing the model would otherwise perform implicitly inside its context window. Indexes precompute import graphs, symbol tables, and reference chains, so the agent retrieves the answer rather than searching for it ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)). The +0.259 reward delta appears specifically in the 400K–2M LOC band because that is where externalised indexing replaces failed implicit search.

The same mechanism explains why structural navigation (Pattern 2) outperforms textual matching: it short-circuits a search that would otherwise consume context to no useful end. A 2026 study on repository-scale agent navigation names this the "Navigation Paradox" — larger context windows do not eliminate the need for structural navigation, because architecturally critical but semantically distant files fall outside the model's attention without an external index ([Zylos Research, 2026-04](https://zylos.ai/research/2026-04-19-codebase-intelligence-repository-understanding-ai-agents)).

## When This Backfires

- **Small or single-repo codebases.** Below Sourcegraph's own ~400K LOC threshold, the failure patterns rarely fire and code-intelligence infrastructure is overhead without measurable benefit ([Sourcegraph, 2026-05](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).
- **Semantic retrieval as the Partial Completion remediation is contested.** Claude Code, Cursor, and Devin dropped vector-DB-based RAG in favour of agentic search (grep, file-tree walk, named-file reads) because agentic search outperformed semantic retrieval on real code exploration ([SmartScope, 2026](https://smartscope.blog/en/ai-development/practices/rag-debate-agentic-search-code-exploration/); [MindStudio, 2026](https://www.mindstudio.ai/blog/is-rag-dead-what-ai-agents-use-instead)). Hybrid retrieval is one of several plausible answers, not the only one.
- **Vendor-study framing.** Sourcegraph sells the recommended remediation. The five patterns are independently observable; the specific stack Sourcegraph benchmarks against is not the only solution and a competing harness with strong agentic search may close the gap without the indexing infrastructure.
- **Polyglot or build-broken repos.** Structural navigation depends on a working build — type hierarchies and references silently degrade when compilation fails, types are partial (legacy Python, JavaScript without TS), or the repo spans languages with no unified index.
- **Hand-curated file lists in the prompt.** When the human can name the files, the discovery patterns (Lost, Wrong File, Partial Completion) cannot fire. The remediation cost dominates and the simpler harness wins.
- **Task restructuring is cheaper than infrastructure.** Splitting a multi-repo change into per-repo PRs, narrowing the discovery scope, or scoping the task to one bounded component often costs less than standing up indexing for the whole monorepo.

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

- **Lost in the Codebase** at turns 7–24: 17 read calls without a single targeted lookup; the agent groped through the match set.
- **Wrong File, Wrong Symbol** at turn 25: the agent edited `UserService` when `UserAccountService` (also in the match set) was the change site. The bug report referenced "user account creation," but textual `User*` matching surfaced both.
- **Partial Completion** at turn 26: the patch updated the service layer but missed the matching repository and controller — three subclasses still reference the old contract.

A reviewer who recognises these signatures stops the PR before merge and either asks the agent to widen the change set or hands the agent a structural-navigation tool (find-references on the changed signature) to enumerate the affected sites.

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
