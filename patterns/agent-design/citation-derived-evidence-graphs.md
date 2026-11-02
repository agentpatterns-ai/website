---
title: "Citation-Derived Evidence Graphs for Agent Memory"
term: "Citation-Derived Evidence Graph"
description: "Materialize a memory layer's own citations as typed graph edges so the agent traverses to evidence instead of re-searching for it, without guaranteeing correctness."
tags:
  - agent-design
  - memory
  - context-engineering
  - tool-agnostic
aliases:
  - citation-derived evidence graph
  - evidence graph over wiki memory
  - citation edges as retrieval index
last_reviewed: 2026-10-30
maturity: emerging
---

# Citation-Derived Evidence Graphs for Agent Memory

> Turn a memory layer's existing citations into typed graph edges, so an agent traverses to evidence instead of re-searching for it each time.

A memory layer's accuracy and its citation stability measure different properties, and a gain in the first does not guarantee the second. Over an OpenWiki-compiled wiki of a 111-document library, a retrieval agent's accuracy on cross-document questions rose from 0.10 (plain search) to 0.52. The same wiki agent's citation overlap was lower on those questions: "Citation overlap dropped from 0.74 on simple lookups to 0.25 on connected questions" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). Accuracy rose while the cited sources still changed from run to run. This pattern narrows that gap, without closing it, by converting the citations the wiki already recorded into edges the agent can follow.

## When this earns its cost

Three conditions have to hold together.

Your questions span sources. On 80 simple lookup questions the wiki bought nothing measurable. Accuracy was 0.84 for plain search against 0.83 for the wiki. Citation overlap was 0.72 against 0.74, and latency rose from 9 to 12 seconds ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). An independent benchmark finds basic RAG comparable to or better than GraphRAG on simple fact retrieval. It reads that wash as active harm: the graph layer's "extra graph-based processing may introduce redundant or noisy information for simpler queries, degrading answer quality" ([Xiang et al., 2025](https://arxiv.org/abs/2506.05690v3)).

The citations already exist. OpenWiki writes source-linked claims during compilation, so the edges only need materializing. "Unlike an extraction-heavy knowledge graph pipeline, this layer reuses existing references and citations rather than extracting and reconciling entities with a model" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)).

Reproducibility is worth paying for. Consistency here is evidence overlap, which "measures whether the agent reliably grounds its answers in the *same* sources, not whether the answers are correct" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). If nobody audits which passage an answer came from, this axis buys you nothing.

## What the graph stores

The layer is "a map that turns wiki citations into explicit, typed edges between claims, wiki pages, paragraphs, and topics" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). Two deterministic steps build it. Split documents into paragraphs with stable identifiers. Then connect paragraphs, claims, and wiki pages with typed edges.

Scope is the discipline that keeps it cheap. "The graph's job is evidence navigation, not modeling everything the organization knows", and the wiki keeps doing the synthesis. It "took under a second to build and resolved every explicit cross-reference in the test library" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)).

Against the wiki alone, every reported measure moved: "Accuracy rose 27%, citation consistency doubled, median answer time fell 40%", and cost per correct answer fell 58% ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). LangChain built the corpus and its 972-fact grading ledger. It asked each question three times. Treat the reported gains as results from one vendor experiment.

## Why it works

This page's reading is that materializing the citations deletes a model-stochastic step from the retrieval path. With the wiki alone, citations stay text references inside Markdown, so the agent re-resolves each link by searching. That search is a sampled decision repeated per question. The graph replaces it with a lookup over an edge computed once. LangChain does not say where the wiki agent's variance comes from.

A related measurement shows that LLM citation extraction varies between runs. It does not test retrieval search, so it does not locate the wiki agent's variance. A legal-extraction pipeline ran twice at zero temperature with a fixed random seed and still produced "different results on identical inputs" ([Piccioli et al., 2026](https://arxiv.org/abs/2607.03325v1)). The two runs agreed on legal references at F1 73.2%, against 97.1% between two human annotators. Issue extraction in the same runs agreed at 78.3%. Read it with its caveats: 50 Italian tax-court judgments, raw output before the pipeline's hallucination filter, and "part of the reference disagreement is inherited from the imperfect alignment of issues across runs rather than from citation extraction proper."

## When this backfires

- Single-passage lookups, the inverse of the first condition. Measured as neutral at best and noise-adding at worst ([Xiang et al., 2025](https://arxiv.org/abs/2506.05690v3)).
- No citations to harvest. Build the references with a model and you are running the extraction pipeline this pattern avoids. Indexing one roughly 56k-token book cost "nearly 655,000 tokens" for Microsoft's GraphRAG ([Xiang et al., 2025](https://arxiv.org/abs/2506.05690v3)).
- A wrong citation becomes a durable wrong edge. Construction needs no model calls, "though edges derived from the wiki still depend on the accuracy of its model-generated citations" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). The graph makes a bad path the one the agent follows reliably, which no consistency metric can see.
- Low query volume. Compilation cost $4.15 and each later document about $0.09, both excluded from the reported per-answer figures ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). Payback depends on a reuse rate the source never states.
- Mistaking consistency for determinism. Traversal still branches, so the result improves "both accuracy and consistency without making the agent fully deterministic" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). Doubled from 0.25, citation overlap (average pairwise Jaccard) lands near 0.5, so the cited evidence still varies between runs.

## Example

The edge vocabulary is the part a reader copies, because it decides what the agent can ask for. LangChain's `expand` tool exposes "cites, refers_to, supersedes, amends, attaches_to, and their inverses", and the post describes three of them concretely: "claims `cite` paragraphs, newer documents `supersede` older ones, and sections `refers_to` other documents" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)).

| Edge | Answers |
|---|---|
| `cites` | Which passage supports this statement |
| `supersedes` | Which version of a document is current |
| `refers_to` | Which declared cross-reference to follow next |

Two tools consume it. `locate` matches the question against titles, headings, wiki pages, and claim statements to find a starting node. `expand` opens a node and follows its typed edges. With `hops` above 1 and one edge type, it follows a single path and stops at a branch. At the branch, the agent chooses the next edge. The paragraph identifiers those edges point at come from a deterministic split: "A deterministic process splits each document into paragraphs and assigns each a unique identifier" ([LangChain, 2026](https://www.langchain.com/blog/building-agent-memory-openwiki-graphs)). The locate-then-expand shape is prior art from [Microsoft's GraphRAG](https://microsoft.github.io/graphrag/), which the source names.

## Key Takeaways

- Measure citation overlap separately from accuracy before building anything. The wiki improved connected-question accuracy, while citation overlap remained low on those questions.
- The cost argument depends on provenance you already recorded. If your memory layer emits no citations, pricing this against an extraction pipeline is the wrong comparison.
- Type the edges. A supersede link and a cite link answer different questions, and an untyped one makes the agent guess which it found.
- A reproducible evidence path is not a correct one. Budget review for the citations the graph hardens, because nothing in this layer checks them.
- Split your own question mix into cross-source and lookup before you pilot, then read each arm separately. Pooling them is how a wash on the larger arm disappears into an average.

## Related

- [Wiki Memory: Agent-Maintained Compressed Knowledge Base](wiki-memory-agent-maintained-knowledge-base.md) — the layer this indexes, covering how the compiled knowledge base is built and when it amortizes
- [Self-Correcting Memory: Evidence-Backed Claim Repair](self-correcting-memory-evidence-backed-claims.md) — the write-time half of the same runtime, where recorded evidence decides whether a claim is still trusted
- [Knowledge Graphs as Provenance-Carrying Agent Memory](knowledge-graph-shared-memory.md) — the model-extracted alternative, which pays for entity resolution to get provenance this pattern inherits
- [Memory Retrieval as a Control Decision](memory-retrieval-as-control.md) — the gating question at query time, deciding whether retrieved memory reaches the agent at all
- [Schema-Guided Graph Retrieval](../../context-engineering/schema-guided-graph-retrieval.md) — the typed-retrieval neighbour, where one shared schema spans construction and querying instead of edges derived from existing references
