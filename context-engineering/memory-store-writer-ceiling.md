---
title: "Memory Store Writer Ceiling: Test Rebuilding When You Upgrade the Model"
term: "Memory Store Writer Ceiling"
description: "Lossy extraction can limit later answer accuracy. In one writer-reader study, rebuilding the store improved correct-answer rates more than upgrading the reader alone."
aliases:
  - memory writer ceiling
  - write-time extraction ceiling
  - stale memory store after model upgrade
tags:
  - context-engineering
  - memory
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-26
maturity: emerging
---

# Memory Store Writer Ceiling: Test Rebuilding When You Upgrade the Model

> A memory store can omit facts a stronger reader needs; test rebuilding it alongside a reader upgrade.

Version a persistent memory store against the model that built it. Move the answering model to a stronger one and the store still holds whatever the old model chose to extract. The new model answers from the same retrievals. Budget a rebuild comparison into the upgrade, or preserve searchable raw records as a fallback.

Two conditions scope this. An LLM extraction pass builds the store, writing facts, entity summaries or graph edges. Retrieval then reads it back without calling a model of its own. A lexical or vector index over verbatim text has no writer in this sense, because no model decided what to keep.

## How large the ceiling is

One study swapped readers across pre-built stores on a 419-turn conversation, holding each store fixed and varying only the model that answered. The metric is correct-answer rate on 152 questions, not retrieval recall. The stores are Zep, a temporal graph, and Mem0, a set of extracted facts ([MemoryTax, arXiv:2610.29823v1](https://arxiv.org/abs/2610.29823v1)):

| Store, by its writer | Weakest reader | Strongest reader | Re-extracted and read by the strongest |
|---|---|---|---|
| Zep graph, written by GPT-4o-mini | 43% | 45% | 87% |
| Mem0 store, written by GPT-4o-mini | 78% | 84% | 95% |

On the Zep graph the reader upgrade is worth two points and the writer upgrade forty-two. The Mem0 split is six against eleven. The author puts it as "A stronger reader does not recover what the writer left out."

## Why it works

Extraction runs before any question arrives, and it discards source text. One controlled ablation held the model, retriever, reranker and judge constant and swapped only the stored representation. It reports that "The mechanism is lossy distillation, not structure per se: accuracy tracks how much source text survives in the store" ([arXiv:2601.00821v4](https://arxiv.org/abs/2601.00821v4)). A reader upgrade cannot reach the dropped sentence. The retrieval step is identical for every reader, because "Retrieval calls no language model, so the reader can be swapped" ([arXiv:2610.29823v1](https://arxiv.org/abs/2610.29823v1)). Both stages can affect accuracy, but a reader cannot retrieve source text absent from its available evidence.

Price the re-extraction against one full run of the same questions. The two stores fall on opposite sides of that line. With the strongest model, Mem0's build cost $25.88 and Zep's cost $6.22, against $17.84 to read the whole conversation for all 152 questions ([arXiv:2610.29823v1](https://arxiv.org/abs/2610.29823v1)). The bill for a writer upgrade is a property of the extraction design, so measure yours rather than assuming a multiple of a run.

## When this backfires

- The history does not fit the reader's window. The study's conversation fit every model tested, so reading all of it was always an option. Where it is not, the store is not competing against the raw record.
- One history serves thousands of questions. The same study puts Mem0's break-even against full context at 372, 545 and 596 questions depending on the model, and the benchmark asked 152. Compare your own query volume and costs; those break-even counts apply to this measured history.
- Latency or token budget binds instead of accuracy. Mem0's own evaluation reports "a 91% lower p95 latency and saves more than 90% token cost" against full context ([arXiv:2504.19413v1](https://arxiv.org/abs/2504.19413v1)). A store can be right on those axes while losing on answer accuracy.
- The task is organizing knowledge rather than recalling a fact. On ledger, to-do list and tree tasks, "simple retrieval-augmented LLMs struggle with these tasks, whereas memory agents can reliably solve them if prompted how to organize their memory" ([StructMemEval, arXiv:2602.11243v4](https://arxiv.org/abs/2602.11243v4)).
- A better extraction design raises the ceiling. One four-network store lifted a 20B open model from 39% to 83.6% and outperformed full-context GPT-4o ([arXiv:2512.12818v1](https://arxiv.org/abs/2512.12818v1)). The ceiling is a property of the extraction, not a law about stores.

Read those magnitudes as one measurement, not a constant. MemoryTax covers "One conversation of LoCoMo's ten, and one run per cell". A GPT-4o-mini judge graded it, with a lenient rubric and at least one wrong answer key. A separate controlled protocol found that "the ranking reverses across models" and recommends you "report write-path cost before attributing gains to architecture" ([MemDelta, arXiv:2606.29914v1](https://arxiv.org/abs/2606.29914v1)). Test whether the same information loss limits your corpus; these magnitudes do not establish that.

## Example

MemoryTax's writer-reader swap shows the migration decision on an existing Zep graph. GPT-4o-mini wrote the original graph. Upgrading its reader to Claude Opus 5.5 moved the correct-answer rate from 43% to 45%. Rebuilding the graph with Claude Opus 5.5 and using that model to read it reached 87%. These are separate cells in Table 3, not repeated trials ([MemoryTax, arXiv:2610.29823v1](https://arxiv.org/abs/2610.29823v1)).

For this comparison, the store's writer is the variable to record before judging the reader upgrade. In the study, each build starts from the original conversation ([MemoryTax, arXiv:2610.29823v1](https://arxiv.org/abs/2610.29823v1)).

## Key Takeaways

- Record which model wrote each store, and treat a model upgrade as a trigger to test re-extraction rather than assume an accuracy gain.
- Test writer and reader separately when diagnosing an accuracy shortfall. A reader swap moved one graph two points where re-extraction moved it forty-two.
- Report the write-path cost alongside any accuracy figure a store is credited with, which is MemDelta's own recommendation to memory evaluations ([arXiv:2606.29914v1](https://arxiv.org/abs/2606.29914v1)).
- Where the history fits the reader's window, keeping it searchable removes the writer from the design, so model upgrades carry no store migration at all.

## Related

- [Long Context vs Retrieval: The Break-Even Decision](long-context-vs-retrieval-break-even.md) — the query-volume arithmetic that decides whether to build a pipeline at all
- [Addressable Recall Compaction: Compact to Citations, Not Summaries](addressable-recall-compaction.md) — keeping exact bytes recoverable instead of a summary, inside one session
- [Fact Supersession Memory for Code Assistants](fact-supersession-memory.md) — what to do about stale rows once a store exists
- [Usage-Reinforced Memory Decay for Long-Running Agents](usage-reinforced-memory-decay.md) — retention scoring for items the store already holds
- [Organizing Filesystem Agent Memory for Retrieval Cost](../patterns/agent-design/filesystem-memory-organization.md) — the read-side cost of how a store is laid out
