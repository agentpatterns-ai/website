---
title: "Exact-File Selection Over Compression at a Fixed Budget"
term: "Exact-File Selection"
description: "At a matched per-issue budget on 300 SWE-rebench issues, showing a few whole files verbatim resolved 6.3 points more than the best of three drop-in compressors with either model tested."
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - whole-file context selection
  - exact file selection
  - picking files instead of compressing
last_reviewed: 2026-10-16
maturity: emerging
---

# Exact-File Selection Over Compression at a Fixed Budget

> At a matched token budget, showing a few whole files verbatim resolved 6.3 points more issues than the best of three drop-in compressors.

Spend the budget on which files the model sees rather than on shrinking a larger context. This holds under three conditions: the agent writes a patch in one call, the budget is fixed before the call, and the edit format makes the model reproduce the lines it changes.

Yang and colleagues matched every context to the same per-issue budget on 300 SWE-rebench issues and graded each patch with the benchmark's tests. Exact-file selection resolved 43.7% with GPT-5.6 and 46.7% with Claude Opus 5. The best of three drop-in compressors resolved 6.3 points less with either model, and the best of three untrained retrievers resolved 9.3 and 12.7 points less ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).

The paper's own control narrows that finding. Given the same candidate files, a code-aware compressor that cuts whole lines resolved 44.7% against the selector's 43.7%. The authors read their result as "a rule rather than a ranking: choose the candidate files well, then cut whole lines if anything must be cut" ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).

## What the comparison measured

| Context, GPT-5.6 | Verbatim lines | Files-to-edit recall | Patches that apply | Resolved |
|---|---|---|---|---|
| Exact-file selection (CQ2-CARE) | 100.0% | 79.0% | 98.0% | 43.7% |
| LongCodeZip | 96.8% | 72.2% | 89.7% | 37.3% |
| LLMLingua-2 | 17.5% | 78.3% | 70.7% | 30.0% |
| BM25 over chunks | 100.0% | 58.3% | 86.7% | 29.0% |
| Gold files (upper bound) | 100.0% | 97.0% | 97.7% | 49.3% |

Figures are Table 1 of [arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1). Two caveats travel with them. The budget is the selector's own realized context size for that issue, so the comparison sits at its operating point, which the authors list as a limitation. Files-to-edit recall is the paper's gold-file recall, computed after the fact from the gold patch and never shown to a model. The selector is small: with GPT-5.6 "its context holds 1.7 selected files on average (median 1)".

## Why it works

Two properties of a context predict whether the patch lands, and the three strategies trade one for the other. Similarity-ranked retrieval keeps every line real and loses the file that must change, because tests, issue templates and documentation echo the report's wording. Chunk retrievers "put a fifth or less of their lines in the files to edit, against half for CQ2-CARE, and show none of them on over a quarter of the issues". Token pruning keeps the right file and alters its text, so the diff quotes lines that do not exist. Non-applying patches account for 28 of the 48 issues the selector resolves and LLMLingua-2 does not ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).

A controlled test separates the two causes. Deleting 20% of the tokens of every line of the selector's own contexts, leaving file choice untouched, "lowers patch applicability from 98.0% to 78.7% and resolution by 9.7 points" ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)). A second sample of patches from the intact contexts resolved exactly as many issues. The paper puts it as "Altering the text alone, with the files fixed, costs about ten points." With search/replace blocks instead of diffs on 100 GPT-5.6 issues, "quotes taken from compressed contexts often match no unique location in the real file", on 45 issues for LLMLingua-2 against 4 for the selector.

The selector buys one thing, measured at 100.0% of context lines with both models. Every line the model might quote exists in the file its header names.

## When this backfires

- Your agent reads files on demand. The study grades one patch call per context: "We study one patch call per context on Python issues from one benchmark, not a multi-turn agent that could read more files or run tests" ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)). The authors note that agents able to re-open files "may recover some of the losses we measure", but each re-read costs a turn and tokens. They leave measuring it to future work.
- Your localization is already good. Once a compressor starts from the right candidate files and cuts whole lines, it matched the selector at the same budget ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).
- The file that must change is very large. The method cuts a selected file over 60K tokens to its first 60K and skips any block that would take the context past 80K tokens, so a very large module is not shown whole. With GPT-5.6, 7 of 300 contexts reach a cap ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).
- The task produces no patch. LongCodeZip reports "up to a 5.6× compression ratio without degrading task performance" on code completion, summarization and question answering ([Shi et al., arXiv:2510.00446v1](https://arxiv.org/abs/2510.00446v1)). Nothing there has to be quoted back exactly.
- Trained retrieval of whole functions nearly matches it. SweRank, trained to rank functions for an issue, trails by 0.7 and 1.7 points while keeping every line verbatim. The authors add that it may have trained on other pull requests from the same repositories, so its small gap "does not show equal performance". It also "shows every line the gold patch changes on only 39% of the GPT-5.6 issues, against 70% for CQ2-CARE" ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).
- Your repair needs diagnostic context. Localization frameworks "are still evaluated as file retrieval rather than actionable diagnosis, producing locations without the diagnostic context a repair agent needs" ([Tamoyan et al., arXiv:2606.24820v2](https://arxiv.org/abs/2606.24820v2)).
- Single-sample gaps are fragile. Most cells carry one patch sample, and "a second one flips 8.7-18.9% of outcomes" ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).

## Example

The paper's Table 3 shows one issue, `iterative__dvc-10844`, with GPT-5.6. The issue is a shell script that runs `dvc add` and `dvc diff`. The fix edits `dvc/repo/diff.py`, which no retriever shows. The table lists what fills the budget under each context:

| Context | What fills the budget | Resolved |
|---|---|---|
| BM25 (chunks) | 7 test files, e.g. `test_ignore.py` | no |
| Dense (chunks) | 7 test files, e.g. `test_diff.py` | no |
| BM25 (files) | `cli/parser.py`, `commands/diff.py` | no |
| Exact-file selection | `repo/diff.py` whole, callers, 2 tests | yes |

The authors chose this issue for illustration from the 12 where the selector resolves and both chunk retrievers fail without showing any file to edit ([Yang et al., arXiv:2610.21073v1](https://arxiv.org/abs/2610.21073v1)).

## Key Takeaways

- The selector's context holds 1.7 files on average (median 1), and every line in it is verbatim, so the model can quote it back exactly.
- Read the patch-apply rate as a context metric. In Yang's controlled test it fell from 98.0% to 78.7% when 20% of the tokens of every line were deleted and the files were held fixed.
- The rule the authors draw is about granularity. Pick the candidate files well, then cut whole lines if you must cut.
- Nothing here is measured for a multi-turn agent that can read more files or run tests.
- SweRank, trained to rank functions for an issue, came within 0.7 and 1.7 points. File-level BM25, which picks whole files by similarity to the issue, trailed by 9.3 and 12.7 points, so whole files chosen by similarity are not enough.

## Related

- [Source Code Minification for State-in-Context Agents](source-code-minification-trade-off.md) — the same text-fidelity cost measured on one transform, with its own resolution-rate drop
- [Chunking Strategy for RAG-Based Code Completion](chunking-strategy-rag-code-completion.md) — what chunk granularity does on a task where nothing has to be quoted back
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the case for cross-file retrieval, which this comparison scopes rather than refutes
- [Symbol Ranking for Agent File Pickers](symbol-ranked-file-picker.md) — a cheaper way to rank candidate files when a localization call is too expensive
- [Context Budget Allocation: Spending Every Token Wisely](context-budget-allocation.md) — the wider question of what a fixed window is spent on
