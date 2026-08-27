---
title: "Corpus Shape as a Retrieval Design Constraint"
term: "Corpus Shape Classification"
description: "Three yes/no questions about a document collection separate retrieval failures a re-ranker can fix from recall ceilings that sit above tuning entirely."
aliases:
  - "corpus shape classification"
  - "RAG corpus type classification"
tags:
  - context-engineering
  - tool-agnostic
  - rag
last_reviewed: 2026-08-23
maturity: emerging
---

# Corpus Shape as a Retrieval Design Constraint

> Three yes/no questions about a document collection predict which retrieval failures a re-ranker can fix and which sit above it.

Classify the collection when a measured baseline has already failed, not before. The classification is a diagnostic that tells you which lever is left, and it costs a domain-expert interview.

## When classification pays

Run the cheap baseline first. An agentic keyword-search loop with no vector database and no corpus analysis reaches 94.52% of a RAG baseline's faithfulness, 88.05% of its context recall, and 91.48% of its answer correctness averaged across five datasets, and beats it outright on FinanceBench, 32.71% against 24.24% answer correctness ([Subramanian et al., AAAI 2026](https://arxiv.org/abs/2602.23368v1)).

Classification then pays when three conditions hold together:

1. The baseline fails on retrieval, not generation. Wrong answers trace to documents that were never returned, not to a model that misread what it got.
2. A domain expert can answer the three questions below quickly. The method depends on a business user naming the structure, not on inferring it from the data.
3. The corpus is past what the baseline handles. The keyword agent degrades on large documents and struggles with ambiguous queries, by its authors' own account ([Subramanian et al., AAAI 2026](https://arxiv.org/abs/2602.23368v1)).

## The three questions

Ask a domain expert, in this order ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)):

Only the second and third pick the shape. The source is explicit about the first: "A yes here does not pick a shape. It adds a requirement to whichever shape you land on."

| Question, in the source's words | Yes means | What changes |
|---|---|---|
| "Do two documents in the collection ever point at each other?" | Amendments name masters, renewals cite prior policies | A relations table and validity dates, added to whichever shape questions two and three select |
| "Can a business user name a field that every document carries, meaning the same thing in each one?" | The collection is "one document type, many copies" | Filter on that field before similarity search, not after |
| "Do the documents arrive in bundles, several of them about one case?" | The bundle, not the document, is the unit of analysis | Retrieval assembles the whole case, then detects missing or contradictory pieces |

For question two the tell is not the answer but how fast it comes: "If four examples come back in two seconds, the collection is a database that nobody has typed yet, and typing it is the job. If the answer arrives after a pause and with qualifications, treat it as a no."

Two "no" answers to questions two and three leave "a pile of unrelated files", where summaries and outlines carry the index and routing is hierarchical. The source's claim is that "an architecture that suits any one of them suits the other two badly" ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)).

## Why it works

Recall has a representational ceiling that re-ranking cannot lift. The number of top-k document subsets a single-vector retriever can return is bounded by the embedding dimension. On the LIMIT stress test built from that proof, state-of-the-art models "struggle to reach even 20% recall@100", and fine-tuning moves recall@10 only from near zero to 2.8 ([Weller et al., 2026](https://arxiv.org/abs/2508.21038v2)). A re-ranker reorders the list the embedding step returned, so a document that never entered the list cannot be recovered by reordering ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)).

Structure changes the candidate set rather than its order, so it is a different lever. Filtering on a named field narrows the search space before similarity runs. A pile carries no such field, so in the source's words "there is nothing to build a filter with" ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)). The LIMIT results point at two alternatives to single-vector retrieval: BM25 "comes close to perfect scores", and a long-context reranker solved all 1,000 queries of the small setting in one forward pass ([Weller et al., 2026](https://arxiv.org/abs/2508.21038v2)).

## When this backfires

- Small corpora. The keyword baseline's 88% to 94% averages were measured over single papers and essays; the financial filings were scored separately, on answer correctness only ([Subramanian et al., AAAI 2026](https://arxiv.org/abs/2602.23368v1)). Classification buys nothing measurable at that scale.
- Mixed-shape collections. A store that is a pile, a typed set, and a set of bundles at once has no single correct label. Partition by collection and classify each part, or the taxonomy picks the wrong architecture for most of the data.
- Unknown query distribution. The second question is only useful if queries actually filter on the field named. Classify before the query shape is known and you build a schema nobody queries.
- No domain expert available. Without one you are guessing the shared field, and a guessed filter silently excludes correct documents.
- Untested premise. The three-type taxonomy comes from one uncontrolled practitioner essay whose own measurement is a naive for-loop, not a comparison between the architectures it recommends ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)). Treat it as a diagnostic checklist, not a validated design method.

The stronger counter-position is to skip classification: stand up keyword search as an agent tool, run fifty real questions through it, and let the measured failures name their own fix.

## Example

The source's reported baseline shows what an unclassified pile costs at small scale. A for-loop over five NIST PDFs, one parse plus one model call each, ran in 14.3 seconds, about 2.9 seconds per document. One document answered the question with the definition quoted at confidence 0.95. The other four returned nothing usable: two empty strings, one literal `NA`, and one bare slash ([Shi, 2026](https://towardsdatascience.com/three-kinds-of-rag-corpus-and-what-it-costs-to-build-for-the-wrong-one/)).

Four of five model calls did no work, and no re-ranker fixes that, because those four documents did not contain the answer. The routing question came first: something had to decide which document to read.

## Key Takeaways

- Measure a keyword-search baseline before classifying anything. It reaches 88% to 94% of RAG's metrics without an index ([Subramanian et al., AAAI 2026](https://arxiv.org/abs/2602.23368v1)), and its failures are the input the classification needs.
- Recall ceilings on single-vector retrieval are provable and dimension-bounded ([Weller et al., 2026](https://arxiv.org/abs/2508.21038v2)). Once you are hitting one, changing the retrieval primitive to BM25, a long-context reranker, or a pre-filter is the only move that helps.
- The second question is the highest-value one for a coding agent: if every document carries a version, a repo, or a service name, filtering on it costs almost nothing and removes a whole class of cross-document contamination.
- Partition a mixed-shape corpus before classifying it. Forcing one label onto a collection that holds several shapes optimizes for the smallest part of it.
- The taxonomy is single-sourced and untested against alternatives. Use it to read failures you measured, and record what the change actually bought.

## Related

- [Component-Wise RAG Prioritization for Software Engineering Tasks](rag-component-prioritization-software-engineering.md) — the same upstream-lever logic applied to component choice; retriever beats generator
- [Chunking Strategy for RAG-Based Code Completion](chunking-strategy-rag-code-completion.md) — chunk size is one of the downstream knobs this page argues cannot fix a recall ceiling
- [Structured Domain Retrieval: Knowledge Graphs and Case-Based Reasoning](structured-domain-retrieval.md) — what a cross-referenced corpus architecture looks like once built
- [Lexical-First Retrieval for Agentic Search](../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — the keyword baseline to measure before classifying
- [Exhaustive Retrieval for Listing Questions](exhaustive-retrieval-for-listing-questions.md) — bundle completeness as a retrieval requirement rather than a ranking one
