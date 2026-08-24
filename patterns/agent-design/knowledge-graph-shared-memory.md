---
title: "Knowledge Graphs as Provenance-Carrying Agent Memory"
term: "Provenance-Carrying Graph Memory"
description: "Store agent memory as typed relations that each record their source document, so an evaluator can check a claim rather than judge it — worth the construction cost only on cross-document joins and citable feedback."
tags:
  - agent-design
  - memory
  - tool-agnostic
aliases:
  - provenance-carrying graph memory
  - knowledge graph as agent memory
  - source-attributed graph memory
last_reviewed: 2026-07-26
maturity: emerging
---

# Knowledge Graphs as Provenance-Carrying Agent Memory

> A knowledge graph stores each fact with the document that asserted it, so an evaluator can check a claim instead of judging it.

Build a knowledge graph for agent memory under two conditions: your agents ask questions that chain facts across documents sharing no common passage, or an evaluator has to say which document asserted a claim. Outside those regimes, plain files and vector retrieval win on accuracy and cost, and the graph's construction stage adds a failure surface that fails quietly.

## When this earns its cost

Either one justifies the build; neither means a simpler store wins:

- Answers span documents. If every answer sits in one source, traversal never fires and extraction is pure overhead.
- Feedback must cite, not judge. Edge-level provenance is the only part of this pattern that vector chunks cannot supply.

The construction preconditions are the ones any graph memory carries — a controlled entity vocabulary, sessions long enough to amortize the build, and someone who owns the schema. Maintenance has a prescribed shape too: "When a new document arrives, extract its entities, resolve them against the existing canonical set (not against each other), and add only the new edges. Re-summarize an entity only when its source-document set changes materially" ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/knowledge_graph/guide.ipynb)) — guidance the guide states in prose, not logic the pipeline ships. [Context-Graph Shared Memory for Multi-Agent Systems](../multi-agent/context-graph-shared-memory.md) works through those and the graph-versus-vector retrieval question; this page is about what provenance adds on top.

## Grounding evaluator feedback

Anthropic's knowledge-graph pipeline runs five stages — corpus build, entity and relation extraction, entity resolution, graph assembly, and multi-hop querying — and the assembly step attaches the originating document to every edge, writing `source_doc` alongside the predicate ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/capabilities/knowledge_graph)). The stored unit is not a passage that mentions two entities; it is one relation, attributed to one document.

That attribution changes what an evaluator can say. Building Effective Agents defines the evaluator-optimizer workflow as one call generating a response while another "provides evaluation and feedback in a loop," and names its precondition directly: it works "when we have clear evaluation criteria, and when iterative refinement provides measurable value" ([Schluntz and Zhang, 2024](https://www.anthropic.com/engineering/building-effective-agents)). A provenance-carrying graph supplies exactly that criterion. The evaluator stops estimating whether a claim looks right and instead resolves whether the relation exists and which document backs it.

That lookup is only as good as the extraction behind it, and Anthropic publishes the error bar. Running the guide's prompt with `claude-haiku-4-5`, expect entities at "P 0.80–0.90 | R 0.70–0.85" and relations at "P 0.70–0.85 | R 0.55–0.70" ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/knowledge_graph/evaluation/README.md)). Relation recall is the binding number, and the same source calls it generous: predicate wording is ignored when scoring, "which makes the reported relation recall an upper bound — it measures whether the extractor found the right *connections*, not whether it labeled them correctly." Three in ten stated relations are missing from the graph at best, and some that survive carry the wrong predicate.

That ceiling dictates one design rule: a missing edge means *unknown*, never *refuted*. An evaluator that reads absence as disproof turns the recall gap into confident false accusations, which is worse than the vague judgment the graph replaced — a wrong answer delivered with a citation format. Measure extraction recall against your own gold set before wiring an evaluator to the graph.

## Surviving a context flush

Long-running loops lose their working state at the context boundary. Anthropic's research system treats this as a design constraint — "if the context window exceeds 200,000 tokens it will be truncated and it is important to retain the plan" — and has agents store "essential information in external memory before proceeding to new tasks," alongside "artifact systems where specialized agents can create outputs that persist independently" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). A graph is one substrate for that requirement, and a demanding one.

Anthropic met the requirement with memory files and artifacts, not a graph, and still reported that a multi-agent system "outperformed single-agent Claude Opus 4 by 90.2%" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Reach for the graph when the retained state has to be queried by relation, not when it merely has to survive.

## Why it works

The mechanism has two halves, and both are regime-bound. First, chaining: when the answer spans documents, similarity search has nothing to score, because the linking facts never co-occur in a passage. The cookbook states the consequence plainly — "No single document contains the answer. RAG retrieval won't chain the facts for you. You need a knowledge graph" ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/capabilities/knowledge_graph)). Second, attribution: because provenance rides on the edge rather than the chunk, verification becomes a lookup with a citation attached, which is the checkable criterion the evaluator-optimizer loop requires to converge ([Schluntz and Zhang, 2024](https://www.anthropic.com/engineering/building-effective-agents)). If your queries need no join and your feedback needs no citation, neither half engages and construction cost buys nothing.

## When this backfires

The evidence against general adoption is stronger than the evidence for it, so adopt narrowly:

- Single-document question answering. A systematic pipeline analysis finds that "GraphRAG frequently underperforms vanilla RAG on many real-world tasks" ([Xiang et al., 2025](https://arxiv.org/abs/2506.05690v3)).
- Cost-sensitive deployments. In a distributed multi-agent comparison on LoCoMo, vector memory reached "77% to 81% accuracy" against graph memory's "55% to 56%" — traced to "retrieval incompleteness rather than reasoning failure" — while a plain retrieval baseline matched the top cluster "at 8.4 times lower total cost of ownership" ([Wolff and Bennati, 2026](https://arxiv.org/abs/2601.07978v4)). Multi-agent operation already runs "about 15× more tokens than chats" ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)); a construction stage compounds that.
- Free-text agents with no controlled vocabulary. The pipeline's resolver has no fallback for stragglers, so "any raw name Claude leaves out of every cluster silently disappears from the graph" ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/capabilities/knowledge_graph)). A construction error becomes an invisible retrieval gap, not a loud failure.
- Ungoverned schemas. The same pipeline documents over-merging, where a specific entity gets folded into a broader one ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/capabilities/knowledge_graph)), degrading answers without raising an error.
- Evaluators wired to treat a missing edge as a refuted claim. This is the pattern's signature failure: it inverts the one role that justifies the construction cost, and the published relation-recall ceiling above says how often it fires.

## Example

The cookbook's Apollo graph resolves 36 raw entities and 34 raw relations extracted from six source summaries down to 22 canonical entities, then assembles edges that keep their origin ([Anthropic claude-cookbooks](https://github.com/anthropics/claude-cookbooks/tree/main/capabilities/knowledge_graph)):

```python
G.add_edge(src, tgt, predicate=r["predicate"], source_doc=r["source_doc"])
```

One argument carries the whole pattern. Without `source_doc`, an evaluator reviewing a generated claim can only report that something seems off. With it, the evaluator resolves the relation and answers with the document that asserted it — the difference between an opinion and a citation.

## Key Takeaways

- Provenance on the edge, not the chunk, is what a knowledge graph adds that vector retrieval cannot; it turns evaluator feedback from a judgment into a lookup with a citation
- Anthropic's pipeline attaches `source_doc` to every relation, and the evaluator-optimizer workflow it feeds requires exactly that kind of checkable criterion to converge
- The mechanism is capped by extraction: published relation recall is 0.55–0.70 and explicitly an upper bound, so a missing edge must resolve to unknown rather than refuted
- Persistence alone does not justify a graph — Anthropic's own multi-agent system used memory files and artifacts, and reported a 90.2% gain over a single agent without one
- Construction failures are silent: unmatched entity names vanish from the graph and over-merging degrades answers without erroring, so an unowned schema is worse than no graph
- Independent benchmarks favor simpler stores outside the join-plus-citation regime, including a plain retrieval baseline matching graph memory at 8.4 times lower cost of ownership

## Related

- [Context-Graph Shared Memory for Multi-Agent Systems](../multi-agent/context-graph-shared-memory.md) — the retrieval-side argument for graph state across agents, with the vector-versus-graph benchmark evidence this page defers to
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — the generate-and-critique loop whose feedback quality provenance-carrying edges are meant to raise
- [Anthropic's Effective Agents Framework: A Pattern Map](anthropic-effective-agents-framework.md) — the workflow taxonomy that supplies the evaluator-optimizer definition used here
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md) — the broader scoped-memory decision this pattern sits inside
- [Epistemic Working Memory for Multi-Hop Reasoning (SLEUTH)](epistemic-working-memory-multi-hop-reasoning.md) — an explicit fact ledger for multi-hop work when a full graph is more machinery than the task needs
