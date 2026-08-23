---
title: "Organizing Filesystem Agent Memory for Retrieval Cost"
term: "Filesystem Memory Organization"
description: "Organizing an agent's markdown memory tree roughly halves per-query retrieval cost on large stores while leaving answer quality unchanged — a cost optimization with a size threshold, not a quality one."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - filesystem-based agent memory
  - markdown memory store organization
last_reviewed: 2026-08-01
maturity: emerging
---

# Organizing Filesystem Agent Memory for Retrieval Cost

> Organizing an agent's markdown memory tree roughly halves retrieval cost on large stores and changes nothing measurable about answer quality.

Asking an agent to keep its markdown memory tidy buys a cheaper read, not a better answer. The first systematic study of filesystem-based memory compared organized stores against a verbatim dump, splitting the system into three roles: a management agent that files incoming content, a search agent that answers queries against the store, and an execution agent that runs tasks from retrieved skills. Organization more than halved per-query search cost on the largest store, 1.6 cents against 3.9, but "correctness has no shape that wins everywhere" ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637v1)). Budget the work as a cost optimization and judge it on cost.

## When organizing pays

Three conditions have to hold together. Miss one and curation is overhead.

The store has to be large. The saving appeared on the two densest stores, 137 KB and 612 KB when dumped verbatim, where organized variants cost 1.4 and 1.6 cents per query against 4.0 and 3.9 for the dump. The paper reports the halving only for those two tiers; its conversational stores dump to 102 KB and 105 KB ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)).

A capable model has to do the managing. Adherence to the taxonomy eroded as most stores grew, and only the strongest management agent held the contract across a full accumulation run ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)). A weak manager gives you the bill without the structure.

You have to keep paying. Curation cost stayed flat per episode and never amortized, about $10 to $11 per 140 tasks against zero for an append-only episode log ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637v1)).

## Why it works

Structure buys selective reading, not a smaller store: organized stores make seven to nine tool calls against the dump's four to five, each pulling far fewer tokens ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)). [Wiki memory](wiki-memory-agent-maintained-knowledge-base.md) rests on the same amortization argument.

## Match the memory form to the model that reads it

The most actionable result concerns form, not layout. In the skill setting a weak execution agent did better on synthesized guidance than on raw logs, 76.4% against 66.4%. A strong execution agent reversed that: the verbatim episode log led at 87.1%, with curated skills second at 82.1% ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637v1)).

Synthesis discards detail. A weaker consumer cannot recover it from a raw trajectory and gains from having it pre-digested; a stronger one can, and loses by being handed someone else's summary. Choose the form by which model reads the store, not by which looks tidier. [Memory synthesis from execution logs](memory-synthesis-execution-logs.md) covers the distillation side.

## Organization style says more about the model than the content

Given the same stream and instruction, three management models produced 122, 2, and 105 files, with cross-reference counts from 7 to 233, while correctness stayed in an unsystematic 66.7% to 73.8% band. The harness moves the shape as much as the model does, which is direct evidence for treating [memory as a property of the harness](harness-memory-coupling.md): holding instruction and backbone fixed, a shell tool set produced 36 files where a restricted file-operations set produced 45, and "changing the tool set alone reshapes the store as strongly as swapping the model" ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637v1)). Pin the tools as deliberately as you pin the model.

## When this backfires

- A strong model consumes procedural memory. Curation cost 5 points against a raw episode log at gpt-4.1 level ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)).
- The store is small. The saving appears at the 137 KB and 612 KB tiers, not at the 102 KB and 105 KB conversational tiers ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)).
- Several agents or users share the store. A file records what was written, not what it replaced or why; git "reconciles text, not meaning", so concurrent writers race without it and diverge logically with it, and file permissions cannot express per-user isolation or retention ([Zep, 2026](https://blog.getzep.com/markdown-is-not-agent-memory/)). Organizing a substrate that cannot record provenance treats a data-model problem as a layout problem — see [knowledge graphs as provenance-carrying memory](knowledge-graph-shared-memory.md).
- You read the correctness null as settled. An audit of LoCoMo, one benchmark behind it, found 99 score-corrupting errors in 1,540 questions and a judge that accepted 62.81% of deliberately wrong answers ([Penfield Labs, 2026](https://dev.to/penfieldlabs/we-audited-locomo-64-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg)). A purpose-built memory system reports 92.5 on LoCoMo at under 7,000 tokens per retrieval ([Mem0, 2026](https://mem0.ai/research)), so structure can buy quality — an agent freelancing a directory layout may just be the wrong organizer.

## Example

The five store shapes on PersonaMem 128k, whose verbatim dump measures 612 KB ([Zhou et al., 2026](https://arxiv.org/abs/2607.26637)):

| Store shape | What the management agent does | Search cost per query |
|---|---|---|
| Verbatim dump | Appends every session unmodified | 3.9 cents |
| Foldered sessions | Moves the dump's session files into a folder taxonomy, unedited | 3.5 cents |
| Reorg. (preserve) | Splits and merges content across sessions, keeping every fact | 1.6 cents |
| Reorg. (condense) | Restructures the same way, without the keep-every-fact rule | 1.7 cents |
| Agent-curated store | Builds the store from empty, choosing content and layout together | 2.6 cents |

Rewriting content across files captured the saving: both reorganized stores read at 1.6 to 1.7 cents. Mechanical foldering moves the same bytes into directories and keeps most of the cost, at 3.5 cents.

## Key Takeaways

- Organize a filesystem memory store to cut read cost, not to raise answer quality — the measured payoff is 1.6 cents against 3.9 cents per query on a 612 KB store.
- The saving has a size threshold. The smallest store showing it is 137 KB, and curation costs about $10 to $11 per 140 tasks regardless.
- Match memory form to the consuming model: synthesized guidance for weaker agents, verbatim records for stronger ones.
- Structure decays. Only the strongest management agent held its taxonomy as the store grew, so budget maintenance rather than assuming self-curation holds.
- The tool set shapes the store as much as the model does, so pin both when the layout matters.

## Related

- [Wiki Memory: Agent-Maintained Compressed Knowledge Base](wiki-memory-agent-maintained-knowledge-base.md) — the precomputed-synthesis version of the same amortization argument
- [Tiered Memory Architecture: Episodic-to-Semantic Consolidation](tiered-memory-architecture.md) — promotion between an episodic and a semantic tier, and when it pays
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md) — turning trajectories into reusable lessons, the form choice this page conditions
- [Knowledge Graphs as Provenance-Carrying Agent Memory](knowledge-graph-shared-memory.md) — what a substrate with provenance and validity buys over plain files
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — the scoped-memory baseline these stores extend
