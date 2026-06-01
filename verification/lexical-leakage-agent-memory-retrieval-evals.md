---
title: "Control Lexical Leakage in Agent-Memory Retrieval Evals (Entity-Collision)"
description: "A single hit@k confounds semantic retrieval with lexical overlap; pin BM25 by constructing distractors that share gold-answer entity tokens and stratify queries by tag so embedder lift is attributable rather than averaged."
tags:
  - testing-verification
  - evals
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - entity-collision retrieval evaluation
  - stratified retrieval eval for agent memory
  - BM25-pinned distractor protocol
last_reviewed: 2026-05-31
---

# Control Lexical Leakage in Agent-Memory Retrieval Evals (Entity-Collision)

> A single hit@k confounds embedder lift with lexical overlap; pin BM25 with shared-entity distractors and stratify queries by tag.

## When This Protocol Is the Right Instrument

Entity-collision answers one question: **does this embedder add signal beyond keyword overlap on agent-memory retrieval?** Adopt it when choosing between embedders for an agent-memory or RAG store, with the index and chunking held constant, and an eval set you can stratify into 3–5 query categories by retrieval mode. Skip it when you need end-to-end agent-memory quality — those require production traces and task-level grading. See *When This Backfires*.

## The Confound a Single hit@k Hides

A naïve agent-memory eval gives every retriever one number — hit@k or NDCG@k over a fixed query set — and ranks embedders by that score. Two effects mix inside:

1. **Lexical leakage.** When the gold answer shares words with the query, BM25 finds it for free, and any retriever above BM25 inherits the free win. The reported hit@k is partly a *property of the dataset*.
2. **Tag mixing.** Queries vary by retrieval mode — phrase lookup, paraphrase, intent, multi-hop. Averaging hides where each embedder actually wins or loses.

The LoCo benchmark surfaced this: BM25 alone reached NDCG > 90 on 4 of 5 tasks, meaning lexical overlap dominated and any "win" over BM25 by a dense retriever was small and possibly noise. [Source: [LoCo Benchmark BM25 insights (HazyResearch/m2 issue #23)](https://github.com/HazyResearch/m2/issues/23)]

Entity-collision resolves both confounds at construction time. [Source: [Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory](https://arxiv.org/abs/2605.29630)]

## The Protocol: Two Construction Rules

### Rule 1: Pin BM25 with Shared-Entity Distractors

For each evaluation query, construct the candidate pool so that **every distractor shares the gold answer's entity tokens**. Pull the named entities, IDs, and content words from the gold answer; ensure each distractor carries the same set. BM25's score is dominated by IDF-weighted term overlap, so when every candidate shares the high-signal tokens, BM25 ranks them comparably by construction. The lexical baseline is *pinned*. [Source: [Entity-Collision](https://arxiv.org/abs/2605.29630)]

Any retriever that now outranks BM25 must be using non-lexical signal — semantic similarity, contextual encoding, or learned task structure — because the lexical channel has been saturated for every candidate.

### Rule 2: Stratify Queries by Discriminator Tag

Partition the query set into 3–5 disjoint tags that name the *retrieval mode* the query exercises. The paper uses 5 tags; team-scale evals can start with fewer. Tags should be orthogonal to topic — they describe how the embedder has to retrieve, not what the user asked about. Examples:

- `lexical` — exact term match should dominate
- `paraphrase` — same intent, different surface form
- `intent` — query expresses a goal, gold answer describes a tool or preference
- `multi-hop` — gold answer is reached only through an intermediate memory
- `temporal` — gold answer depends on session ordering

Report hit@k and NDCG@k **per tag**, not averaged. This surfaces the asymmetries averaging hides: in the paper's results, MiniLM-384 beats BGE-large on lexical tasks while losing on intent-based ones — a finding a single hit@k erases. [Source: [Entity-Collision](https://arxiv.org/abs/2605.29630)]

## Why It Works

The mechanism is well-grounded outside this protocol: hard-negative mining at *training* time exploits the same logic — force the model past easy lexical cues so it learns harder semantic ones. A 2025 ACL Industry paper on hard-negative mining for enterprise retrieval reports 15% MRR@3 and 19% MRR@10 improvements over baselines from this principle. [Source: [Hard Negative Mining for Domain-Specific Retrieval in Enterprise Systems (ACL 2025 Industry)](https://aclanthology.org/2025.acl-industry.72/)]

Stratification compounds the effect. 2026 work on semantic stratification shows aggregate metrics regularly obscure per-region failures that only appear when queries are partitioned by semantic class. [Source: [Coverage, Not Averages: Semantic Stratification for Trustworthy Retrieval Evaluation](https://arxiv.org/abs/2604.20763)]

## When This Backfires

Entity-collision answers a model-selection question, not a deployment-quality question. It is the wrong instrument when:

- **Production retrieval is hybrid.** Most production stacks fuse BM25 and dense retrieval. The protocol erases the BM25 component's real contribution and over-penalises the embedder for failing on queries where BM25 was doing the work. Use it for embedder selection, not end-to-end measurement. [Source: [Hybrid Search: BM25 and Dense Retrieval Combined](https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion)]
- **The domain rewards lexical match.** Code search, error-code lookup, product-catalog search, function-name resolution — exact term overlap is the correct retrieval signal. Forcing entity-collision distractors makes the eval bear no resemblance to production query mix. [Source: [Sparse Embedding or BM25 (Infiniflow)](https://medium.com/@infiniflowai/sparse-embedding-or-bm25-84c942b3eda7)]
- **Small teams without eval headcount.** Per-tag stratification, per-query distractor construction, and BM25 calibration cost real time. For teams making one model-selection decision a year, end-to-end task evals on real production traffic are cheaper and more directly informative.
- **Embedder change paired with index change.** The protocol measures the combined lift unless the index is held constant — rare in real upgrade cycles where teams rebuild the index for the new embedder dimensions.

## Example

A team is choosing between two embedders for a Claude Code memory store that persists user preferences, tool choices, and prior session intents across conversations. Without the protocol, they run a 500-query eval and report:

```text
embedder-A: hit@5 = 0.84
embedder-B: hit@5 = 0.81
```

Embedder A wins. But the team's queries are 60% lookup-by-phrase ("what's my preferred error-handling style"), 25% intent ("set up the same testing config as last time"), and 15% multi-hop ("the framework we picked for that React project"). After applying the entity-collision protocol — every distractor in the candidate pool shares the gold memory's named entities, queries tagged by retrieval mode — the same eval yields:

```text
                  lexical  intent  multi-hop
embedder-A         0.91     0.74     0.62
embedder-B         0.85     0.83     0.77
```

The lexical tier was carrying embedder A's average and BM25 was retrieving most of its winners for free. Once lexical overlap is pinned across both embedders, embedder B is the better choice for intent and multi-hop queries — which is exactly what an agent-memory system stores. The team that picked A on the single hit@k picked the wrong embedder for their workload.

(Numbers are illustrative of the protocol's mechanic; the paper provides the actual per-tag comparison across hash-trigram, MiniLM-384, and BGE-large embedders.)

## Key Takeaways

- A single hit@k for agent-memory retrieval confounds embedder lift with lexical overlap and tag mixing — model-selection decisions made on it can pick the wrong embedder
- Pinning BM25 by construction — every distractor shares the gold answer's entity tokens — converts the metric from "lexical overlap plus semantics" to "semantics only"
- Stratifying queries by retrieval mode (lexical / paraphrase / intent / multi-hop / temporal) surfaces per-mode asymmetries that averaging hides, and is the discipline the protocol couples with BM25-pinning
- Entity-collision answers a model-selection question, not a deployment-quality question; hybrid retrievers, lexical-favoured domains, and small teams may be better served by end-to-end task evals
- The protocol's mechanism (controlled hard-negative construction) is independently validated by 2025 ACL work on hard-negative mining showing 15–19% MRR improvements at training time

## Related

- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — a parallel measurement-validity failure mode where the eval set itself leaks signal to the system under test
- [Skill Retrieval Realism Gap](skill-retrieval-realism-gap.md) — idealised retrieval conditions inflate skill-augmented agent benchmarks the same way unstratified hit@k inflates embedder benchmarks
- [Golden Query Pairs as Continuous Regression Tests](golden-query-pairs-regression.md) — the production-trace half of the eval discipline this protocol does not cover
- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md) — the agent-memory systems this eval discipline measures
- [Abstention-Aware Memory Retrieval](../agent-design/abstention-aware-memory-retrieval.md) — adjacent agent-memory retrieval concern where false positives matter more than recall
