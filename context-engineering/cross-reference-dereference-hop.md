---
title: "Cross-Reference Dereference Hop in Retrieval Loops"
term: "Cross-Reference Dereference Hop"
description: "A retrieved passage that says 'see Section 7.2' ranks first and answers nothing. A bounded dereference hop detects the pointer, resolves it against the parser's own reference table, and re-answers — worth adding when references resolve deterministically and the corpus turns over faster than it is queried."
aliases:
  - cross-reference resolution hop
  - pointer dereference in retrieval
  - reference-following retrieval loop
tags:
  - context-engineering
  - tool-agnostic
  - rag
last_reviewed: 2026-08-12
maturity: emerging
---

# Cross-Reference Dereference Hop in Retrieval Loops

> A bounded second retrieval pass that detects a pointer in a retrieved passage, resolves it against the source's own reference table, and re-answers.

Retrieval can return a pointer instead of an answer. A passage reading "the two versions produced nearly identical results, see Table 3 row (E)" satisfies a top-1 retrieval policy and reads as a finished answer, while the figure the question asked for sits on another page ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)). The dereference hop adds one bounded pass: generation flags the pointer, the orchestrator looks its target up in a table the parser already built, re-retrieves that region, and regenerates.

## When this applies

Four conditions decide whether the hop belongs in the loop. Miss any one and index-time resolution is the better placement, for the reasons under [when this backfires](#when-this-backfires).

- References resolve to a key: a numbered section, a table or figure ID, a native PDF link, a table-of-contents anchor, or a symbol a compiler resolves.
- The corpus turns over faster than it is queried. A 200-page contract holds hundreds of references, and expanding all of them at index time spends effort on passages no query retrieves ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)).
- The corpus is trusted, because the pointer is written inside the document and selects the next fetch.
- A second retrieve-and-generate round-trip fits the latency budget.

## Detecting a pointer

A ranker cannot flag the problem, because it scores relevance and the failure is insufficiency. A pointer passage names the section, table, or entity the question asked about, so it tops both lexical and dense similarity while carrying none of the answer. Per-chunk verification misses it too, because it assumes one chunk is a sufficient premise for the answer. Entailment scoring against the original query reaches 0.951 AUC on single-hop SQuAD and drops to 0.643, 0.523, and 0.560 on HotpotQA, 2WikiMultiHopQA, and MuSiQue ([arXiv:2608.00585v1](https://arxiv.org/abs/2608.00585v1)).

Generation is the remaining stage that can see it. Shi's design returns two typed fields beside the answer: `pending_references`, holding pointers that would change the answer if resolved, and `answer_completeness`, one of `complete`, `references_unresolved`, or `partial`. The orchestrator branches on that enum, not on a confidence score ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)).

Keep the signal structural rather than discretionary. Where a dependency-navigation tool was merely available to a coding agent, 58% of trials made zero tool calls, which the authors read as a behavioral alignment gap ([arXiv:2602.20048v1](https://arxiv.org/abs/2602.20048v1)).

## Resolving the pointer and bounding the hop

Resolution runs against a cross-reference table the parser emits, carrying each row's origin page, anchor text, reference type, target, target page, and provenance. Provenance orders the ladder: `native_link` and `toc_anchor` come free from the parser, an `object_registry` entry normalizes "Table 3 row (E)" to a key and joins it to a page, `regex` covers in-prose forms, and `llm` handles what is left ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)).

A budget is what keeps the hop from becoming general iterative retrieval. Shi's orchestrator compares a loop counter against `max_loops`, which defaults to 1, then exits to a normal return or an explicit `give_up_partial` state. A clause pointing at a schedule that points at an annex exhausts that budget, and the give-up state keeps the truncated result from being reported as complete.

## The code analogue

Indirection is the norm in a codebase: an inherited config block, a base class, a re-exported constant. The resolver is stronger than in prose, because a compiler or language server maps a symbol to its declaration exactly.

The payoff concentrates on dependencies sharing no vocabulary with the task description. On those hidden-dependency tasks, an agent given a graph of static dependencies completed 99.4% against 76.2% for a vanilla agent and 78.2% for BM25 retrieval. That measurement covers 258 trials on 30 tasks in a production FastAPI repository ([arXiv:2602.20048v1](https://arxiv.org/abs/2602.20048v1)). [Repository-level retrieval](repository-level-retrieval-code-generation.md) reports its largest gains on the same tasks, and [semantic context loading](semantic-context-loading.md) supplies the resolver.

## Why it works

The hop uses what the document already wrote down. Multi-hop questions defeat per-chunk filtering because the bridge is implicit, so finding it needs another semantic search. Gold decomposition on MuSiQue's later hop lifts entailment AUC from 0.560 to 0.840, a +0.355 paired lift ([arXiv:2608.00585v1](https://arxiv.org/abs/2608.00585v1)). The signal is there once the question is split. A cross-reference is the tractable case of that split: the source names its own second hop, so resolution becomes a lookup. That is why a budget of one suffices here and would be useless for general iterative retrieval.

## When this backfires

- Static corpus, heavy query load. Index-time bridging materializes cross-document links as retrievable units, then answers multi-hop questions in one pass with a single LLM call, improving F1 over naive RAG by 4.6 points on average across the same three benchmarks ([arXiv:2603.16415v1](https://arxiv.org/abs/2603.16415v1)). Paid once per reference, it beats a hop paid on every affected query.
- Reference chains deeper than the budget. At `max_loops` of 1 a two-link chain ends in `give_up_partial`, and a fluent partial answer one hop out is the original failure relocated.
- Ambiguous in-prose references. "As described above" has no deterministic target, so the LLM fallback reintroduces the guess the hop removes.
- Latency-bound paths. Inline completion and interactive chat cannot absorb a second pass at 16–22× naive inference time ([arXiv:2605.06285v1](https://arxiv.org/abs/2605.06285v1)).
- Untrusted corpora. A poisoned passage chooses the next fetch, so constrain targets to the same trusted corpus and treat the fetched region as data ([arXiv:2601.10923v2](https://arxiv.org/abs/2601.10923v2)).
- No measured baseline. The design is argued from token accounting, and the primary source reports no metrics ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)).

## Example

A question about the Transformer paper's positional-embedding ablation retrieves page 6, which reports the qualitative result and points at a table on page 9 ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-cross-references-when-rag-answers-see-section-7-2-instead-of-the-actual-answer/)).

**Before** — generation returns an answer field only:

```json
{
  "answer": "The two versions produced nearly identical results. See Table 3 row (E)."
}
```

The orchestrator has nothing to branch on, so this returns to the user as a finished answer.

**After** — generation returns the completeness signal alongside it:

```json
{
  "answer": "The two versions produced nearly identical results. See Table 3 row (E).",
  "answer_completeness": "references_unresolved",
  "pending_references": [
    {"anchor_text": "Table 3 row (E)", "ref_type": "table", "ref_target": "3"}
  ]
}
```

The orchestrator normalizes `Table 3 row (E)` to the key `(table, 3)`, joins it against the object registry to reach page 9, re-retrieves that region under the row sub-selector, and regenerates. Loop count moves from 0 to 1, hitting the default `max_loops`, so a still-unresolved second pass exits as `give_up_partial` rather than looping again.

## Key Takeaways

- Add the completeness signal at generation, not the ranker, because a pointer passage is maximally relevant and minimally sufficient and no relevance score separates the two ([arXiv:2608.00585v1](https://arxiv.org/abs/2608.00585v1)).
- Make the hop an orchestrator branch on a typed enum rather than a tool the model may call, because agents leave an available navigation tool uncalled in most trials ([arXiv:2602.20048v1](https://arxiv.org/abs/2602.20048v1)).
- Set the budget to one hop and give the loop an explicit give-up state, so a truncated reference chain is reported as partial instead of read as complete.
- Choose the placement by rebuild-to-query ratio: loop-time resolution for corpora that churn, index-time bridging for corpora queried far more often than they change ([arXiv:2603.16415v1](https://arxiv.org/abs/2603.16415v1)).
- In code, wire the hop to a language server rather than a regex, and expect the gain on dependencies with no lexical overlap with the task ([arXiv:2602.20048v1](https://arxiv.org/abs/2602.20048v1)).

## Related

- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the code-side retrieval stage this hop extends, including co-retrieving a helper's current declaration alongside its usage
- [LLM-Driven Logical Retrieval: Boolean Queries over an Inverted Index](llm-driven-logical-retrieval.md) — moves precision to the query author instead of adding a resolution pass after the answer
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — encodes reference structure as typed graph edges at index time rather than resolving pointers at query time
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md) — the resolver the code analogue depends on
- [Epistemic Working Memory for Multi-Hop Reasoning (SLEUTH)](../patterns/agent-design/epistemic-working-memory-multi-hop-reasoning.md) — tracks open questions across hops when the bridge is implicit and no pointer names the target
