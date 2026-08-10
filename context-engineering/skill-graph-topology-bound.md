---
title: "When a Skill Graph Cannot Beat the Ranker (Pre-Filter Topology Bound)"
term: "Pre-Filter Topology Bound"
description: "A skill graph whose edges are drawn from the retriever's own embedding neighbors can relabel what retrieval found but cannot extend its reach. Test the bound before you build."
aliases:
  - pre-filter topology bound
  - skill graph retrieval ceiling
  - embedding-bounded graph retrieval
tags:
  - context-engineering
  - tool-agnostic
  - rag
  - skills
  - arxiv
last_reviewed: 2026-08-10
maturity: emerging
---

# When a Skill Graph Cannot Beat the Ranker (Pre-Filter Topology Bound)

> A skill graph built from the retriever's own embedding neighbors can relabel what retrieval found, never extend its reach.

Before you build a typed knowledge graph over a skill library, check where its candidate edges come from. When a model generates edges by inspecting each skill's top-K embedding neighbors, the graph inherits that embedding's topology. The model can name the relation between two skills, but it never sees a pair the retriever failed to surface. Kolluru and Sportsman name this the pre-filter topology bound and measure it over a 690-skill library ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)).

## The two conditions that decide it

Both conditions are properties of your build, not of graphs in general.

| Question | Structure pays | Structure cannot pay |
|---|---|---|
| Where do candidate edges come from? | A signal independent of the retriever: labeled query-tool training data ([COLT](https://arxiv.org/abs/2405.16089v2)), a separately trained dependency discriminator ([Tool Graph Retriever](https://arxiv.org/abs/2508.05152)), or hand-authored prerequisites | The retriever's own embedding top-K |
| How does the graph get used? | Added alongside ranked results, supplying prerequisites, next steps, and alternatives | Substituted for ranked results at a matched token budget |

Substitution is where the measured loss lands. Swapping graph neighbors in for additional ranked results at a matched token budget cost 11.2 points of hit@5 against a hybrid ranker combining BM25 with `all-MiniLM-L6-v2` embeddings, which scored 73.5% ±8.0 on 117 non-echoing queries (p=0.0007, McNemar) ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)). Used additively as a re-ranking boost, the same graph moved hit@5 by 0.85 points, 95% CI −4.8 to +6.5, p≈1.000. No gain, no loss: enrichment is defensible to ship, substitution is not.

## Run the overlay test first

The bound is cheap to measure before committing engineering budget. Overlay the typed edges on the embedding's own nearest-neighbor graph and count two things:

1. Newly connected nodes: skills the typed layer wires up that the embedding layer left isolated.
2. Merged components: clusters the typed layer joins that the embedding layer kept apart.

Both counters read zero on the 690-skill corpus. Adding 1,421 typed edges to a 1,626-edge embedding backbone left wired nodes at 594 and connected components at 112, neither number moving. Of the typed edges, 98.6% (1,008 of 1,022 pairs) joined skills the ranker had already surfaced together, and 73% of the queries the ranker missed were unreachable through the graph at all ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)).

Zero on both counters means the graph is a relabeling of retrieval you already have. The modeling budget is better spent on the descriptions the ranker discriminates on, which is where [skill loadout curation](skill-loadout-curation.md) locates the recoverable loss.

## Why it works

The causal reason is ordering, not model quality. Edge generation runs after a retrieval step that already truncated the candidate space, so the pairs the model may label are fixed before it is called. The authors state it directly: a model asked to type pairs drawn from an embedding's top-K "can enrich semantics by assigning a typed relation to a pair, but it cannot add reach, because it is never shown a pair the embedding did not already surface" ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)). A stronger labeler does not lift the ceiling, because the pre-filter set it. Graph methods that beat semantic retrieval break the ordering instead of the labeler: COLT learns collaborative structure from labeled query-tool data ([Qu et al., 2024](https://arxiv.org/abs/2405.16089v2)), and Tool Graph Retriever trains a dependency discriminator on a purpose-built corpus before any graph convolution runs ([Gao et al., 2025](https://arxiv.org/abs/2508.05152)).

## When this backfires

- Independent-signal graphs. If edges come from usage co-occurrence, a trained discriminator, or human authorship, the pre-filter never applies, and the counter-literature reports gains over semantic-similarity retrieval ([COLT](https://arxiv.org/abs/2405.16089v2)).
- Ordered multi-skill execution. Hit@5 against one gold skill measures single-item lookup. On an n-skill chain, the authors' analysis puts graph traversal ahead of repeated search whenever per-hop edge accuracy exceeds single-query hit rate. Measured directional accuracy of 0.67 to 0.83 straddles the 0.735 threshold, so the sequencing case stays undecided ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)).
- Enrichment read as a loss. The substitution result says nothing against attaching prerequisites and next steps to a resolved skill, though 8.5% of surviving typed pairs pointed the wrong way and direction quality has to be fixed first ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)).
- A different corpus, embedder, or domain. The paper disclaims generalization outright: one corpus, one organization, one embedding model.
- Multi-hop reasoning over a document corpus rather than skill lookup. Graph structure carries a separate argument there, covered by [schema-guided graph retrieval](schema-guided-graph-retrieval.md).

## Example

The measured system indexed one line of frontmatter per skill, the name and description, after a sibling effort found that indexing skill bodies degraded retrieval. Edges came from a coarse-to-fine pipeline: take each skill's eight nearest embedding neighbors, then make one `claude-haiku-4-5` call under forced tool use to emit typed relations from a fixed vocabulary of eight (`requires`, `specializes`, `feeds_into`, `routes_to`, `precedes`, `complements`, `alternative_to`, `verifies`). Cycle detection dropped 113 hallucinated edges ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)).

Every design choice there is reasonable in isolation. The bound comes from the first line: because the candidate shortlist is the embedding top-K, the eight relation types describe the ranker's existing neighborhood rather than reaching past it.

One measurement caveat travels with the result. The same paper scored a 37-query set written by its author while reading the corpus at 0.946 hit@5, against 0.735 on the non-echoing set, a gap of 21.1 points for the hybrid ranker and 44.2 for keyword-only, because queries written against visible descriptions reuse their vocabulary ([arXiv:2608.06196v1](https://arxiv.org/abs/2608.06196v1)). [Controlling lexical leakage in retrieval evals](../verification/lexical-leakage-agent-memory-retrieval-evals.md) covers the construction rules that keep this out of your own numbers.

## Key Takeaways

- Ask where a proposed skill graph's candidate edges come from before asking how good its edge labels are. The candidate source sets the ceiling.
- Run the overlay test before the build, not after. A non-zero count on either counter is the evidence that justifies the modeling budget; two zeros mean you already have the graph's reach in your index.
- Never trade ranked results for graph neighbors at a fixed token budget. That specific swap cost 11.2 points of hit@5 on the measured corpus.
- Audit edge direction before shipping enrichment. Prerequisites and next steps attached to a resolved skill are only useful pointing the right way.
- Graphs built from usage data or a trained dependency model sit outside this bound entirely, and the tool-retrieval literature reports them beating semantic similarity.

## Related

- [Skill Loadout Curation for Coding Agents](skill-loadout-curation.md) — where the recoverable selection loss sits once retrieval is already in place
- [Compositional Skill Routing for Large Skill Libraries](compositional-skill-routing.md) — the decompose-retrieve-compose alternative to adding structure at index time
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — the case for typed graphs on multi-hop document reasoning, a different task shape
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the on-demand retrieval baseline both approaches extend
- [Control Lexical Leakage in Agent-Memory Retrieval Evals](../verification/lexical-leakage-agent-memory-retrieval-evals.md) — why an author-written query set overstates every retriever it scores
