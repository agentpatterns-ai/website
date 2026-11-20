---
title: "Fair Lexical Baselines for Code Search"
term: "Fair Lexical Baseline"
description: "On curated Python queries, whole-file BM25 cut an embedding model's lead from +0.121 to +0.034 nDCG@10. An LLM-written query then removed the lead."
tags:
  - tool-engineering
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - dense premium in code search
  - generate-then-grep
  - lexical baseline for code retrieval
last_reviewed: 2026-11-19
maturity: emerging
---

# Fair Lexical Baselines for Code Search

> Before you build an embedding index for repository search, score it against whole-file BM25 with stripped queries and test-free relevance labels.

On a Python benchmark of 1,265 queries over 10 repositories, the embedding model jina-code-embeddings-0.5b led BM25 by +0.121 nDCG@10 on 472 curated queries when BM25 was chunked like the encoder. Against whole-file BM25 the lead was +0.034 ([Xue et al., 2026](https://arxiv.org/abs/2611.20455v1), §5.1, Table 2). On raw pull-request queries the lead survived, at +0.059 to +0.125 (n=288, 138 and 367).

Limits:

- "Grep" in the paper means ranked BM25. Real grep appears only in a 96-task agent run (§1, §5.7).
- Every main result is Python. Outside Python, each per-language pull-request pool is a single repository (§5.1).
- The authors picked BM25's settings on the evaluation queries and call the gaps lower bounds for dense retrieval (§5.1).

## Three choices that inflate the gap

- BM25 chunked like the encoder. Encoders truncate long files and BM25 improves with larger windows, so a shared 1,000-character chunk favors dense (§5.1).
- Edited test files counted as relevant. Dense retrievers rank a test file first far more often, so counting them as relevant raises the curated lead from +0.034 to +0.165 and the Raw-Post lead from +0.059 to +0.136 (§5.1, App. B.3).
- PR template text left in the query. On Raw-Post queries, stripping templates roughly halves the lead (+0.369 to +0.175), "entirely through BM25 gains" (App. D.1).

## Generate-then-grep

One LLM call (qwen35-122B, temperature 0) writes identifiers, APIs, error terms and a code skeleton for the query. You prepend that text to the BM25 query. With whole-file BM25 in both arms, BM25 then led dense retrieval by 0.081 on the curated pool (interval excludes zero) and by 0.054 to 0.062 on the three raw pools (intervals cover zero) (Table 2, §5.2). The authors "say that the premium is removed, but not that the two retrievers are equal" (App. E).

The same text lifts BM25 by +0.12 to +0.21 and the encoder by +0.03 to +0.07 (§5.2). Identifiers carry the effect: "Identifiers, APIs and error terms alone close the premium; prose search phrases do not" (§5.2).

Conditions:

- Smaller generators close "two thirds to 80%" of the lead, not all of it (§5.2).
- Generation is cheaper than a dense index below about 158 queries per repository. That estimate times Qwen3-8B, the weak generator that closes a little over half (App. E).

## Where the dense lead holds, and where it does not

- On the preregistered lockbox (539 queries, 91 repositories, labels as released), whole-file BM25 scored 0.432 and dense 0.533. Generate-then-grep scored 0.534 (Table 3).
- On DeepSWE task descriptions (68 tasks, 56 repositories), the canonical encoder's lead was +0.036 [−0.030, +0.100] and Qwen3-Embedding-0.6B's was −0.078. The paper ties the lead to "how queries are written" (App. R).
- Cursor's A/B test reports code retention up 0.3% with semantic search, and 2.6% on codebases of 1,000 files or more. Its other arm is "traditional search tools like grep", not tuned BM25 ([Cursor, 2025](https://cursor.com/blog/semsearch)).

## Fuse, and measure the agent

The paper's guideline is to keep dense retrieval and fuse it with BM25 (G2). On the lockbox, fixed fusions beat dense by +0.019 and +0.045 on labels as released (§5.3).

With the LLM held fixed on 96 tasks, exact-match localization ran from 0.135 (raw shell with grep) to 0.177 (router), and no paired difference excluded zero (Table 21). Across four setups of three LLMs on a 30-query subset it ran from 0.03 to 0.30. No tests ran (§5.7).

## What to do

1. Score the embedding index on your own merged PRs against whole-file BM25. Strip templates and state which edited files count as relevant (the paper's G1).
2. Add a fused arm (G2). Keep a dense-only index only if it beats the fusion.
3. Build eval checkouts with `git archive`, not `git worktree add`. The shared object store let 8 of 30 shell trajectories read the merged fix. Raw-shell exact-match fell from 0.333 to 0.133 after a clean rerun (App. Q.2).

## When this backfires

- Searches run all day. Generation costs one LLM call per query.
- Queries state the work and name no code, as in DeepSWE. The lead is unresolved there and BM25 wins 38% to 52% of queries (App. R).
- The codebase is private or new. The generator may have known the paper's public repositories (§5.2).
- The repository is large. Cursor's gain grows past 1,000 files, and the paper's largest has 2,752 (§3.1).

## Key Takeaways

- Run the three checks (whole files, stripped templates, test-free labels) before you cite a dense-over-lexical gap.
- Treat generate-then-grep as a Python result with one 122B generator, not a replacement for an index.
- A leaky eval checkout can reverse a tool comparison, so check the object store.

## Related

- [Lexical-First Retrieval for Agentic Search](lexical-first-retrieval-for-agentic-search.md)
- [The Recall Trap](../patterns/anti-patterns/recall-trap-retriever-tuning.md)
- [Chunking Strategy for RAG-Based Code Completion](../context-engineering/chunking-strategy-rag-code-completion.md)
- [Agent-Tuned Code Search](../context-engineering/agent-tuned-code-search.md)
- [Indexed Regex Search for Agent Tools](indexed-regex-search-agent-tools.md)
- [Benchmark Contamination as Eval Risk](../verification/benchmark-contamination-eval-risk.md)
- [Benchmark-Driven Tool Selection for Code Generation](../verification/benchmark-driven-tool-selection.md)
