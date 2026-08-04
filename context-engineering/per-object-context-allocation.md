---
title: "Per-Object Context Allocation (Selective Invariance)"
term: "Per-Object Context Allocation"
description: "Retrieved code can vanish before the model sees it. Group fragments by code object and cap each object's tokens so redundant views stop crowding out dependencies."
aliases:
  - selective invariance
  - authority multiplication
  - view-quotiented allocation
  - retrieval-to-context gap
tags:
  - context-engineering
  - rag
  - code-generation
  - arxiv
  - tool-agnostic
last_reviewed: 2026-08-02
maturity: emerging
---

# Per-Object Context Allocation (Selective Invariance)

> Allocate context to canonical code objects, not to retrieved fragments, so repeated views of one function stop displacing the dependencies a task needs.

Per-object context allocation assigns the token budget to canonical code objects rather than to retrieved fragments. A repository index can return a function's signature, body, call site, and test fragment as four separate results. Fragment-level allocation lets that one function claim four positions in the model input; object-level allocation gives it one, then caps how many tokens that position may spend.

## When this applies

This technique targets one architecture: a retrieval stage that ranks candidates, then a rendering stage that packs them into a bounded prompt. Two conditions must hold before it pays.

You need a provenance-preserving index. Object identity comes from a repository-index adapter — parser-qualified symbol IDs, graph nodes, or at minimum a normalized path plus identifier ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)). Without one, you cannot tell that a signature and a body describe the same object.

Your evidence also has to exceed the budget. Recall of the complete labeled snippet measured 63.67% at a 4,096-token budget and 63.68% at 8K ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)) — once the evidence fits, the allocation rule stops earning anything.

## The gap it closes

Retrieval recall and context recall are different numbers, and most pipelines only measure the first. Across 16,490 RepoBench tasks, required evidence entered the selected top five for 64.16% of tasks but survived the 4,096-token model input for only 39.59% — a 24.57-point drop after retrieval had already succeeded ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)). Instrumenting that second number is the transferable move here, independent of whether you adopt the rest.

## Why it works

Context share follows how many ways an index renders an object, not how much distinct information that object carries. When allocation scores each view independently, one function claims several input positions and displaces independent evidence even where the ranking is correct — the failure the paper names authority multiplication ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)).

Byte-level deduplication cannot intervene, because the views are genuinely different strings. Exact deduplication moved recall within the budget by 0.02 points, from 25.08% to 25.10% ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)).

The fix has two halves, and an ablation separates them. Quotienting authority so one object owns at most one position reaches 39.59% on its own. Compact bounded rendering — a path, identifier, and signature descriptor, then a query-centered window under a per-object cap — reaches 46.15% on its own. Together they reach 63.67% while using 35.63% fewer evidence tokens ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)). Rendering carries the larger share, so cap and compact before you invest in grouping.

That ordering matches an independent result: on SWE-bench Verified with localization held fixed, compressed context matched whole files at a third of the tokens — 19K per resolved issue rather than 94K ([Sam-Bodden, 2026](https://arxiv.org/abs/2607.09691v1)).

## When this backfires

Agentic retrieval removes the stage this optimizes. Where the agent greps, opens files, and reads on demand across turns, no bounded rendering step exists to attach to. Anthropic recommends that posture as the default, keeping ["lightweight identifiers"](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and loading data at runtime. Frontier coding agents navigating a filesystem with native tools beat published state of the art by 17.3% on average, which their authors present as an alternative to semantic search and to context-window scaling ([Cao et al., 2026](https://arxiv.org/abs/2603.20432v1)).

Neighboring context may also matter less than the framing implies. Across every multi-file instance in SWE-bench Verified, rendering a file's remainder as skeletons and signatures resolved no more issues than deleting that remainder outright (N=70, exact McNemar p=0.75) — a registered hypothesis the author reports as failed ([Sam-Bodden, 2026](https://arxiv.org/abs/2607.09691v1)). If the evidence being crowded out was never going to be used, protecting its slot buys nothing.

Reserving a slot for a local companion is a trade. Moving from five canonical objects to four plus one companion lowered broad recall from 39.59% to 38.94% while raising strict recall from 16.26% to 21.31%, on a subset of just 33 of 231 tasks ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)). Where a provenance-local helper is rarely needed, that slot costs coverage.

Downstream gains are uneven. On 227 RepoClassBench tasks the method led on one backend but tied the strongest baseline on the other two ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)). Execution results were stronger — the highest raw Pass@1 on all three backends across 355 RepoExec tasks — so judge by execution, not by similarity to a reference implementation.

The source is a single preprint from July 2026 whose own limitations section runs two sentences. Treat the measurement as the durable part and the four-plus-one configuration as tuned to its benchmarks.

## Key Takeaways

- Measure recall at the model input, not only at retrieval. A 64.16% retrieval hit rate delivered 39.59% surviving evidence in the studied setup ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)).
- Deduplicate by object identity, not by exact-match strings. Exact-string dedup recovers only 0.02 points of recall ([Lu et al., 2026](https://arxiv.org/abs/2607.26937v1)).
- Compact rendering under a per-object cap carries more of the gain than object grouping does — do that first.
- The technique needs a provenance-preserving index and a bounded render step. Agentic file-system exploration has neither.
- Check whether evidence already fits the window before adopting this technique. A window large enough to hold all retrieved evidence removes the crowding problem on its own.

## Related

- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the retrieval stage that produces the candidates this technique allocates
- [Context Budget Allocation: Spending Every Token Wisely](context-budget-allocation.md) — the session-level budget framing, one layer above per-object rendering
- [Chunking Strategy for RAG-Based Code Completion](chunking-strategy-rag-code-completion.md) — how code is split before indexing, which determines how many views one object produces
- [Component-Wise RAG Prioritization](rag-component-prioritization-software-engineering.md) — which pipeline component to tune first when SE-task RAG underperforms
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the just-in-time alternative that removes the bounded rendering stage entirely
