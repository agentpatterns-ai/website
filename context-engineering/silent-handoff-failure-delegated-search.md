---
title: "Silent Handoff Failure in Delegated Code Search"
term: "Silent Handoff Failure"
description: "Delegating repository search to a subagent breaks at the planner-to-subagent handoff in 41.8% of its failures, and the breakdown is invisible in the answer."
tags:
  - context-engineering
  - multi-agent
  - rag
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - coordination breakdown
  - planner-to-subagent handoff failure
  - deep agentic search failure
last_reviewed: 2026-08-06
maturity: emerging
---

# Silent Handoff Failure in Delegated Code Search

> Delegating repository search to a subagent produces a confident wrong answer when the handoff breaks, and the breakdown is silent 91% of the time.

A silent handoff failure is a delegated search that returns nothing useful while the system reports success. Across 720 repository code questions, breakdowns at the planner-to-subagent handoff accounted for 41.8% of the delegated architecture's failures and 0% of the retrieval architecture's. In 91% of those cases "the agent still returned a fluent, confidently worded answer rather than reporting that anything had gone wrong, so the breakdown was not apparent from the output alone" ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).

## Where the finding applies

The study fixed three conditions, and none of them describes a general coding session ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)):

- The task is read-only question answering. Nothing here covers patch generation, test execution, or refactoring.
- The repository can be indexed ahead of time. The 15 SWE-QA repositories were frozen public Python projects, so the index was never stale.
- Each question runs in a fresh session, so the design cannot score the benefit delegation exists for: an orchestrator context that stays clean across many tasks.

## What the comparison measured

Two architectures answered the same 720 questions. One gave a ReAct agent vector retrieval over a pre-built index; the other gave a planning orchestrator a subagent that explored the repository in an isolated context and returned a condensed result ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).

| Model | Semantic index | Delegated search | Gap |
|---|---|---|---|
| Gemini 2.5 Flash | 48.4% | 42.8% | 5.6 pp |
| Gemini 2.5 Pro | 54.2% | 44.2% | 10.0 pp |
| Qwen3-235B | 68.8% | 58.2% | 10.6 pp |
| Gemini 3 Flash | 89.3% | 39.7% | 49.6 pp |
| Pooled | 65.2% | 46.2% | 19.0 pp |

Retrieval also cost $0.32 per correct answer against $0.74 for delegation, and delegation matched or beat it on 1 of the 15 repositories ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)). Plan against your own model, not the pooled row: the same choice buys 5.6 points on one model and 49.6 on another.

Delegation still located code well. Localization misses were 24.4% of its failures against 53.6% of retrieval's ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)). Applying each share to that architecture's own failure rate puts the absolute miss rate near 13% of questions for delegation and 19% for retrieval, so the accuracy gap traces to the handoff.

## Why it works

Delegation compresses twice, and the second compression destroys the evidence needed to audit the first. The planner sends a natural-language brief down to a subagent working in an isolated context, and the subagent sends a condensed result back up. Everything in between goes away with the subagent's context window: the queries it ran, the files it opened, the candidates it rejected. The planner cannot separate a well-scoped brief answered correctly from a mis-scoped brief answered plausibly, so it writes an answer from the summary either way ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).

Vector retrieval has no equivalent seam. It returns code blocks into the answering agent's own window, so a miss arrives as thin or irrelevant evidence that the same agent can weigh. Retrieval failures therefore concentrate in localization, which is visible, rather than in coordination, which is not.

## When this backfires

An index-first default is wrong in four situations.

- The tree is volatile or unindexable. The study names filesystems "too large, too volatile, or too arbitrary to index ahead of time" as the case delegation is built for ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)). Staleness costs most when the agent reads its own writes: it searches for text it just added, misses, and "it'll often go into a wild goose chase, waste tokens" ([Cursor](https://cursor.com/blog/fast-regex-search)).
- The session is long and spans many tasks. Isolation keeps the orchestrator's window clean over hours of work, which a single-question benchmark cannot register ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).
- The work writes or executes code. The benchmark is read-only, so none of the numbers transfer.
- The task is genuinely parallel exploration. Anthropic measured a lead agent with subagents beating a single agent by 90.2% on open-ended research, while noting that "most coding tasks involve fewer truly parallelizable tasks than research" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

The study's conclusion is a router: keep "a cheap semantic index for retrieval" and reserve delegated exploration "for the questions, repositories, or tasks that genuinely require it" ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).

## Key Takeaways

- Treat a search subagent's answer as unverified until the citations it returned are checked against the files, because a broken handoff reads exactly like a good one.
- Require file paths and line ranges back from a search subagent rather than prose, so the planner holds something it can re-open.
- Size the architecture decision against your own model. The measured gap ranged from 5.6 to 49.6 percentage points across four models on identical questions.
- Delegation localized code more reliably than retrieval on this benchmark. Its accuracy loss came from the handoff contract, which is the part you control.
- Non-terminating loops took 13.5% of delegated failures against 2.9% of retrieval's, so budget a turn ceiling on any exploration subagent ([Rafiei Oskooei et al., 2026](https://arxiv.org/abs/2608.01507v1)).

## Related

- [Semantic Context Loading](semantic-context-loading.md) — the LSP-backed alternative to vector retrieval, querying symbols and references instead of embedding chunks
- [Agent-Tuned Code Search](agent-tuned-code-search.md) — a hosted single-purpose search tool that returns paths and line ranges, the citation contract this page argues for
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — how cross-file retrieval is assembled on the index side
- [Trained Repository Explorer Sub-Agent (FastContext)](../patterns/agent-design/fastcontext-trained-repository-explorer.md) — the delegated design with a trained explorer and a citation-only return format
- [Persistent Shared Search Sub-Agent](../patterns/multi-agent/persistent-search-subagent.md) — delegation tuned for output-token reuse across many workers
