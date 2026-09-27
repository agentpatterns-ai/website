---
title: "Give the Model the Target's Contract, Not Similar Solutions"
term: "Contract Context"
description: "For repository-level code generation, put the target's own test, required helpers, and namespace in context instead of a retrieved similar-problem solution."
aliases:
  - contract-over-similar-solutions
  - contract-context finding
  - target contract information
tags:
  - context-engineering
  - technique
  - code-generation
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-26
maturity: emerging
---

# Give the Model the Target's Contract, Not Similar Solutions

> On repository-level tasks, a target function's own test and required helpers beat a retrieved solution to a similar problem.

This applies to repository-level code generation, where the target function has to fit conventions and call helpers defined elsewhere in the codebase. It does not apply to self-contained algorithmic problems. On DevEval, adding the target's own unittest and its required functions to plain BM25 retrieval raised GPT-4o-mini's Pass@1 from 19.62% to 27.65%. Qwen2.5-32B-Instruct rose from 22.18% to 28.67% on the same swap ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)). Both numbers are an oracle upper bound: the researchers built the added fields by hand, pulling the correct solution first and extracting every variable, function, and class attribute it used, so no symbol-prediction step could fail. The study also does not hold the prompt budget constant. The contract fields sit on top of BM25's retrieved context, not swapped in at equal cost. All four tested models have training cutoffs before 2024: "we confirm that the knowledge cutoff dates of all four studied models precede 2024" ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)).

## What to put in context

Three fields make up the contract: the target's own unittest, the functions and class attributes it must call, and its namespace-qualified path. Namespace information alone adds a smaller, still-significant gain on top of the other two. GPT-4o-mini's BM25 score rose from 25.16% to 26.14%, and Qwen2.5-32B-Instruct's embedding-retriever score rose from 36.79% to 39.66%, once namespace metadata was added ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)).

For a coding agent, this means pointing it at the target's own test file and the modules it imports. Do not paste in a function that solved a similar-looking problem elsewhere. [Hints over embedded code samples](../instructions/hints-over-code-samples.md) recommends the same move for instruction files, for a different reason: staleness rather than transfer.

## Why it works

BM25 keyword search misses most of what a target function needs. It recalls only 2.38% of relevant unittests, against 51.93% to 66.92% for embedding-based retrievers: "We observed that for documents retrieved by BM25, unittest recall is only 2.38%, whereas the embedding-based retrievers achieve much higher recall, ranging from 51.93% to 66.92%" ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)). Supplying the missing facts directly closes that gap without a better retriever.

The model does not learn problem-solving logic from a retrieved similar-problem solution either. Output similarity to that solution, measured by CodeBLEU, does not shift when it is added to the prompt: "The results reveal no significant difference ( p ≥ 0.99 across all configurations), indicating that retrieved examples neither meaningfully influence the generation process nor introduce systematic bias" ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)). An independent study on GPT-4o-mini and Gemini 1.5 Flash found the same pattern: retrieved similar code degraded repository-level results by up to 15%, while in-context code and API information helped ([Gu et al., arXiv:2503.20589v1](https://arxiv.org/abs/2503.20589v1)). Repository-level failures are mostly missing facts — the wrong I/O format, a hallucinated helper, an omitted namespace — and the contract fields fix those directly instead of leaving the model to infer them from an analogous case.

## When this backfires

- On self-contained problems, adding the required functions and variables did nothing: "the required functions and variables do not enhance LLMs' performance on LeetCode questions ( p > 0.1 ; p H B > 0.6 ; no Bootstrap CI above zero for all models with both Python and Java), although they are helpful in DevEval tasks" ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)).
- A real pipeline cannot pull symbols from the ground truth, and a wrong or incomplete predicted list can mislead a model the same way a bad retrieved snippet does.
- On unfamiliar libraries, the missing knowledge is how an API is used, not the target's own contract. Retrieved documentation and tutorials lift results there instead ([CodeRAG-Bench, arXiv:2406.14497v2](https://arxiv.org/abs/2406.14497v2)).
- Retrieved same-repository code is not useless in general: on DevEval, similar snippets from the same project raised Qwen2.5-32B-Instruct's Pass@1 from 15.21% to 36.79% ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)). The no-help result is about simple retrievers on self-contained tasks, not examples as a class.
- A coding agent that already reads the repository and runs its own tests may get little from pre-assembled contract context. The paper tests single-shot prompts only, and no study measures the overlap with an agent loop.
- The paper covers four models from one generation. DeepSeek-R1, a reasoning model, loses accuracy under few-shot prompting, so these gains may not transfer to reasoning or frontier models.

The paper also drops any task with only one unittest, so a model cannot pass by matching the one visible test — a real task with no hidden test carries that same risk if you supply only the target's own test.

Identifier names inside the contract matter too: stripping them cost the weakest model up to 30 percentage points on self-contained tasks ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)), the naming-as-signal effect [source code minification](source-code-minification-trade-off.md) documents from the token-savings side.

## Example

**Before** — plain BM25 retrieval: a snippet of a function that solves a similar-looking problem elsewhere in the codebase, with no test, no helper signatures, and no namespace path attached.

**After** — BM25 plus contract fields: the target function's own unittest, the helper functions and class attributes DevEval labels as required, and the target's namespace-qualified path. That swap is what moved GPT-4o-mini's DevEval Pass@1 from 19.62% to 27.65% ([arXiv:2508.06414v2](https://arxiv.org/abs/2508.06414v2)).

## Key Takeaways

- Add the target's own test, required helper functions and class attributes, and its namespace path for repository-level tasks, instead of retrieving a solution to a similar problem.
- Treat the 19.62% to 27.65% GPT-4o-mini gain as an oracle upper bound: researchers built the fields from the ground-truth solution, not from a symbol predictor a real pipeline would run.
- Skip this for self-contained algorithmic tasks, where required functions and variables added nothing for any tested model.
- For unfamiliar libraries, retrieve documentation and tutorials instead — that is where retrieved examples measurably help.
- The finding holds on four models with training cutoffs before 2024; nothing published tests it on frontier or agentic coding models.

## Related

- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the retriever-architecture view of the same problem, and the source of the "up to 15%" similar-code noise figure cited above.
- [Source Code Minification for State-in-Context Agents](source-code-minification-trade-off.md) — identifier names as a semantic channel, examined from the token-savings side rather than the retrieval side.
- [Hints Over Code Samples in Agent Prompts](../instructions/hints-over-code-samples.md) — pointing an agent at a live file instead of a frozen example, for staleness rather than transfer.
- [Component-Wise RAG Prioritization](rag-component-prioritization-software-engineering.md) — where BM25 remains a strong retriever choice despite the low unittest recall behind this finding.
- [Comment Content as Code-Generation Context](comment-content-as-generation-context.md) — a related case where a model conditions on prefix content it did not retrieve.
