---
title: "Metadata Index for Agent File Search: Where It Cuts Cost"
term: "Metadata-Assisted Search"
description: "A prebuilt SQLite index of paths and line ranges replaces a chain of search calls. Alone it cut cost 32% on document retrieval; on code it was rarely queried."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - metadata-assisted search
  - filesystem metadata index
  - SQL file metadata index
last_reviewed: 2026-11-19
maturity: emerging
---

# Metadata Index for Agent File Search: Where It Cuts Cost

> A prebuilt metadata index replaces an agent's chain of file searches with one query, and pays mainly on deep, opaquely named document corpora.

Metadata-assisted search is a harness-side technique for cutting search turns. An offline extractor builds SQLite tables that describe a corpus's files and their line ranges. The agent queries those tables with SQL before it opens anything. In the paper that proposed it, "one SQL lookup query replace[s] a chain of search tool calls" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 4.2.2). Run alone on a document-retrieval benchmark, with GPT-6-Luna on a basic ReAct harness, it cut cost by 32%. On coding tasks, agents queried it 0.2 times per run ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.2, Sec. 5.3).

## When the index pays

The paper's gains came under these conditions:

- The layout hides where things are. Agents made "3 to 6 search turns per run in a flat directory with plaintext names, but 7 to 16 in a tree with UUID names" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 3.5). With all five of the paper's cost techniques combined, OfficeQA Pro cost fell to 0.51 to 0.66 of baseline in a UUID tree. In a flat directory with plaintext names it stayed at 0.81 to 0.96 ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.2).
- The model does not already know the corpus. On coding tasks "the index is rarely queried with 0.2 lookups per run, compared with 4.8 on OfficeQA." The authors explain that models "can recall exact files from memory without searching" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.2).
- The model follows a schema prompt reliably. GPT-6-Luna, one of the paper's "smaller models", fell to an accuracy ratio of 0.93 on some OfficeQA tasks. The cause was "incorrect understanding and utilization of the SQLite tables" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 4.2.2, Sec. 5.2).
- The files stay fixed during the task. The paper's code prompt tells the agent that files it changes are not updated in the index and must be read directly ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), App. D.2).

## How it works

The index has two tables, and they follow the two steps of a search ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 4.2.2):

- A `files` table holds one row per file, with its path and attributes such as file type or date. The path column holds the directory tree, so a whole subtree becomes one prefix match.
- An `entries` table holds one row per line range in each file, with its metadata and line numbers. One join returns the file and the lines to read.

A rule-based extractor fills both tables. For source code it parses the abstract syntax tree for function and class signatures. For documents it parses sections with their captions and headings. The paper states it "needs no LLM outputs, and can be re-executed whenever files change" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 4.2.2). The harness describes the tables in the user prompt. A query returns a pointer: the file and the line range to read.

## Why it works

Each search is its own LLM call: "Every search also adds an LLM call that re-reads the cached prefix" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 3.5). Averaged over its benchmark traces, searches took "about 43% of agent turns and 28% of cost." Sessions also repeat each other, with 42% of directory listings duplicating one that another session of the same model and harness had already made ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 3.5).

Fewer hops means fewer prefix reads. Turns multiply the input bill rather than add to it, as the [four-term agent cost model](../../token-engineering/four-term-agent-cost-model.md) sets out. Run alone on OfficeQA Pro, the index cut search calls by up to 80%, and agents found target files in 5.6 turns instead of 8.1 ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 4.2.2). In the paper's ablation with GPT-6-Luna on its basic ReAct harness, it produced "a 42% reduction in cache reads, a 27% reduction in new input, a reduction in steps from 16.7 to 13.5, and a 32% reduction in cost" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.3).

## When this backfires

- Code repositories the model has seen. At 0.2 lookups per run, the index is a build step the agent seldom opens ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.2). Compare the [repository map pattern](../../context-engineering/repository-map-pattern.md) for code.
- Indexes that push content instead of pointers. In a separate study, a retrieved evidence package of up to 1,000 lines "cuts read and search commands by 18–34%" on every benchmark and Qwen model tested. An index of its locations replaced the package at the first edit or turn 8. Runs still cost at least 33 to 42% more when cached input cost a tenth of uncached input, and 25 to 33% more with no cache discount ([arXiv:2611.22238v1](https://arxiv.org/abs/2611.22238v1), Sec. 4, Table 4). The authors conclude that "for the retrieval designs tested here, location pointers are less costly than retaining large evidence packages in the prompt" (Sec. 8). Its models were open models served locally, mostly from the Qwen family.
- Planning on the 32% figure. It comes from one ablation (one model, one harness, one benchmark), and the authors present their results as "proof-of-concept baseline values" ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), Sec. 5.3, Sec. 6). Measure search turns and cost on your own corpus first.

## Example

The prompt text the paper's harness appended for the OfficeQA Pro document corpus ([arXiv:2611.12122v1](https://arxiv.org/abs/2611.12122v1), App. D.1):

```text
A read-only SQLite index of the corpus is at /index/corpus.db (open it with
`sqlite3 -readonly /index/corpus.db`). It holds metadata about the files, not
their text. Paths are relative to /corpus; line numbers are 1-based and
inclusive. Tables:
- files(name, path, date): one row per file; name is the file name (unique in
  the corpus); date is the first date in its opening lines (YYYY-MM or
  YYYY-MM-DD), which can be missing or wrong
- entries(name, section, caption, heading_date, line_start, line_end, n_rows):
  one row per markdown table in the file with that name. caption is the
  table's title line (the nearest line above it); section is the all-capitals
  section heading it is printed under; heading_date is a date written in the
  caption or a short line below it (e.g. "as of June 30, 1956"), else in the
  section (YYYY-MM or YYYY-MM-DD), NULL if neither has one
```

The prompt names its own weak spot: the `date` column "can be missing or wrong". The agent can treat the index as a guide and check the file it points to.

## Key Takeaways

- Before you build an index, count search turns per run. The paper's combined savings were largest in the layout where agents spent 7 to 16 turns searching and smallest where they spent 3 to 6.
- Do not expect a gain on a code repository the model already knows. Agents there issued 0.2 lookups per run.
- Prefer an index that returns paths and line ranges. In another study, a retrieved code package cut read and search commands by 18 to 34% and still raised cost by 33 to 42% when cached input cost a tenth of uncached input.
- Tell the agent which entries can be stale or wrong, as the paper's prompts do for edited files and extracted dates.
- Test with your smallest production model, because a model that misreads the schema loses accuracy.

## Related

- [Repository Map Pattern: AST + PageRank for Dynamic Code](../../context-engineering/repository-map-pattern.md) — a structural overview for code, where the metadata index went almost unused
- [The Four Terms That Decide What an Agent Task Costs](../../token-engineering/four-term-agent-cost-model.md) — why removing a turn removes a full read of the cached context
- [Pricing a Context Change Across the Cache-Read Range](../../token-engineering/cache-price-range-context-evaluation.md) — the evidence package that cut search and raised cost
- [Harness-Controlled Token Economics (The Harness Effect)](../../token-engineering/harness-token-economics.md) — the wider case that harness changes move cost at a fixed model
- [Lexical-First Retrieval for Agentic Search: When BM25 Is Enough](../../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — a different retrieval layer for agents, judged under its own conditions
