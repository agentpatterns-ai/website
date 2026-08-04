---
title: "Organizational Context Layer for Agents (Company Brain)"
term: "Organizational Context Layer"
description: "A shared context layer maps many source systems into one governed store that many agents query. Three of its engineering rules transfer well below that scale."
aliases:
  - company brain
  - org-wide context layer
  - shared organizational context layer
tags:
  - context-engineering
  - agent-design
  - rag
  - tool-agnostic
last_reviewed: 2026-08-03
maturity: emerging
---

# Organizational Context Layer for Agents (Company Brain)

> A shared organizational context layer maps many source systems into one governed store that many agents query, at platform-team cost.

!!! info "Also known as"
    Company brain, org-wide context layer

An organizational context layer sits one tier above a single agent's context window. It continuously maps warehouses, wikis, and chat into typed items, indexes them several ways, and composes a scoped subset into each query's token budget. Building one is a platform commitment. Three of its engineering rules pay off long before you reach that scale.

## When the full layer is the right bet

Tomer Mesika, co-founder and CTO of modus, documents a production system running across dozens of sources for many tenants and states the build decision plainly: "build if the context layer *is* your product; buy if it's a feature. The demo takes a weekend. The brain takes a platform team" ([Towards Data Science, 2026](https://towardsdatascience.com/how-to-build-a-context-layer-and-a-company-brain/)). Treat the account as vendor-authored: modus sells this product, and the publisher discloses that its owner is an investor in modus.

Four conditions push a team over the line: several source systems with different hierarchies, more than one permission domain, a corpus that changes daily, and a query mix that includes traversals such as "what breaks if I drop this table?". Below that, a single index and a scheduled rescan answer the same questions for far less.

## Rule 1: deterministic identity and idempotent operations

Derive each item's identity from stable attributes of the item rather than from the run that mined it. Mesika uses `(tenant, type, path)`, and names the reason: "your orchestrator *will* retry and workers *will* crash mid-batch". The closing principle is stronger still: "Retries aren't an edge case in this architecture; they are the architecture."

This is the ingestion counterpart to [idempotent agent operations](../patterns/agent-design/idempotent-agent-operations.md), which governs an agent's own side effects such as branches, comments, and pull requests. Same rule, different subject.

## Rule 2: rebuildable projections over a relational ground truth

Keep one relational store as truth and treat every other index as a cache you can throw away. Mesika compresses it to a line: "search indexes are caches, the database is the truth." Writes commit to a per-tenant relational schema first, access controls are enforced there last, and the keyword index, the vector collections, and the [knowledge graph](structured-domain-retrieval.md) all rebuild from it. The failure this prevents: "The moment an index becomes unrebuildable truth, you've lost the ability to fix mistakes."

Mesika makes that guarantee conditional, not automatic: projections lagging the truth is "fine only if every pipeline has explicit cleanup phases and a rebuild runbook you've rehearsed."

## Rule 3: measure before the third retrieval strategy

Retrieval quality decays without anyone reporting it, because "no user files a ticket saying 'the context was 8% worse this week.'" The described harness pairs [golden datasets](../verification/golden-query-pairs-regression.md) of real questions carrying labeled ground truth with deterministic precision and recall against what the composer actually selected, plus recall at several token-budget checkpoints. LLM judges cover only what determinism cannot settle. Two failures need separate metrics: whether the right item was retrieved, and whether it survived into the tokens the model read.

## Why it works

Rules 1 and 2 have causes documented independently of the vendor source, which is why they generalize below its scale. Idempotency is load-bearing because exactly-once delivery is an impossibility result rather than an engineering gap. A sender cannot distinguish a lost message from a lost acknowledgement, so any system that guarantees delivery retries, and retries produce duplicates. Tyler Treat states the consequence: "The way we achieve exactly-once delivery in practice is by faking it. Either the messages themselves should be idempotent, meaning they can be applied more than once without adverse effects, or we remove the need for idempotency through deduplication" ([Brave New Geek, 2015](https://bravenewgeek.com/you-cannot-have-exactly-once-delivery/)). A key derived from the item, not the run, collapses a repeated write onto the same row.

Rebuildable projections hold for the symmetric reason: derivation code changes. Jay Kreps put it this way in his critique of the Lambda Architecture: "Code will always change. So, if you have code that derives output data from an input stream, whenever the code changes, you will need to recompute your output to see the effect of the change" ([O'Reilly Radar, 2014](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)). Separating ground truth from derived indexes turns a chunking change, an embedding-model swap, or an enrichment-prompt bug into a rebuild instead of data loss.

Rule 3 rests on the weaker claim of the three. Mesika reports the harness as what worked in one production system; no independent replication was found, so treat it as practice worth copying rather than a measured result.

## When this backfires

- One source, one tenant, one team. Declarative source maps, per-connection state machines, and per-tenant isolation exist to absorb heterogeneity. With a single wiki and a single warehouse they absorb nothing, and the source's own build-or-buy line puts this case on the buy side.
- Low-churn corpora. The never-terminating reconciliation loop is justified by the claim that a week-stale brain is worse than useless. If content changes monthly, a scheduled full rescan is cheaper and sidesteps the deletion-semantics trap entirely.
- Lookup-dominated query mixes. A graph index pays off on traversals. Where the answer sits in one or two passages, vector search already wins, and Microsoft Research reports that full GraphRAG's up-front indexing cost "may be prohibitive for some users and use cases" ([LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/)).
- Rebuildability costs storage. Kreps priced his reprocessing approach at "temporarily having 2x the storage space in the output database" plus a database that tolerates the reload, and called the efficiency trade-off "somewhat of a wash". The payoff is recoverability, not throughput.
- Reorganizing sources break path-derived identity. Identity from `(tenant, type, path)` holds only while paths hold. A wiki restructure reads as mass deletion followed by mass creation, and the human notes attached to the old identities go with them.

## Example

Deletion is the case where a prototype's assumptions fail silently. Mesika counts at least six channels through which an item disappears, then shows that bounded collections and unbounded streams need opposite handling: "manifest-diff deletion on a cursored stream wipes all history below the watermark; full-rescan tombstoning on a bounded collection wastes enormous work. Neither throws an error."

A table's columns are a bounded collection, so a full rescan can safely tombstone anything it did not see. A ticket feed is an unbounded cursored stream, so the same logic deletes every ticket older than the cursor. Apply one rule to both and the layer keeps describing a table that was dropped in March, with no failure anywhere to point at.

## Key Takeaways

- Derive item identity from the item, not the run, so a crashed worker's retry overwrites rather than duplicates
- Name one relational store as truth and hold every other index to a rehearsed rebuild, so a bad embedding model or chunking change stays recoverable
- Build the eval harness before the third retrieval strategy; retrieval regressions produce no error and no ticket
- Score retrieval and survival-into-budget separately, because an item can rank first and still be cut by the token budget
- The full layer is single-sourced from a vendor and priced for a platform team; below multi-source, multi-tenant, daily-churn scale, buy or stay simple

## Related

- [Layered Context Architecture](layered-context-architecture.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Structured Domain Retrieval](structured-domain-retrieval.md)
- [Context Hub](context-hub.md)
- [Idempotent Agent Operations](../patterns/agent-design/idempotent-agent-operations.md)
- [Governed Sources of Truth for Analytics Agents](../patterns/agent-design/governed-sources-of-truth-analytics-agents.md)
