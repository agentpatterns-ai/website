---
title: "Fact Supersession Memory for Code Assistants"
term: "Fact Supersession Memory"
description: "Key each remembered fact by subject and relation and close the old row when the value changes, so retrieval returns the current value instead of ranking stale against fresh by cosine distance."
aliases:
  - deterministic supersession memory
  - bi-temporal fact ledger
  - stale-fact retirement
tags:
  - context-engineering
  - agent-design
  - memory
  - rag
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-24
maturity: emerging
---

# Fact Supersession Memory for Code Assistants

> Fact supersession memory keys each stored assertion by subject and relation, then retires the old row when the value changes.

Fact supersession memory stores what an assistant learns as (subject, relation, object) assertions carrying validity intervals. A new assertion whose (subject, relation) key matches an active row with a different object closes that row and opens its own. Retrieval then surfaces "only currently-valid rows" ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)) with "no similarity threshold and no LLM call" ([Yadav 2026](https://arxiv.org/abs/2606.26511v1)). It fixes one narrow shape of change, and the operating range decides whether it is worth building.

## When it applies

The condition is that the change reduces to a single value swapping under a stable key. Mining 707 real GitHub issues from SWE-bench Lite and Verified, Yadav kept 130 scenarios: "Yield: 130 clean scenarios from 707 records (18.4%); the rest are real fixes that are not atomic transitions" ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)). A renamed function, a moved endpoint, a bumped version, and a changed config value all qualify. A behavior fix or a multi-file refactor does not, because nothing single supersedes.

Two further bounds come from outside that paper. The gain is bounded "to current-value questions with explicit version metadata", and on LongMemEval the same class of fix showed no significant advantage, 26/45 against 29/45 with paired exact McNemar p=0.45 ([Reddy and Challaram 2026](https://arxiv.org/abs/2606.01435v2)). Rankings between memory backends also invert with history length, so a three-week comparison does not predict the winner at nine weeks ([Spencer 2026](https://arxiv.org/abs/2607.21962v1)).

## Why it works

Embedding similarity carries no ordering over time. Yadav measures the consequence: cosine similarity separates a contradicted fact from a duplicated one at AUROC 0.59, near chance, because "contradictions are often more embedding-similar to the original than rephrased duplicates" ([Yadav 2026](https://arxiv.org/abs/2606.26511v1)). The old function name and the new one both land in the retrieved set with near-identical scores, and the model picks one.

Keying by (subject, relation) replaces that judgment with a lookup. The reranker result shows the gap is structural rather than a tuning problem: adding an LLM reranker served the superseded value slightly more often, 37.7% against 36.1%, because reordering retrieved chunks cannot tell a stale value from a current one ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)).

## What the numbers show

Across the 130 scenarios, accuracy in the forced regime ran 0.615 for naive RAG, 0.592 for RAG plus an LLM reranker, and 0.985 for the supersession ledger. The stale-fact-error rate is the sharper figure. "Forced to commit, RAG serves the superseded value 36.1% of the time", against 0.000 to 0.015 across runs for the ledger, at mean retrieval latencies of 2.16 s, 18.1 s, and 2.13 s ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)).

Weigh those against their provenance. The evaluation used a single 7B local model on 130 scenarios, and the paper lists the author's affiliation as MemStrata.dev, the product under test. It is a v1 preprint posted on 21 August 2026 ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)). The underlying problem does have independent grounding: replacing an agent's full context with a bounded, self-maintained memory drops accuracy from 92% to 77%, and across a 24x increase in conversation length accuracy falls from 68% to 28% ([Patel 2026](https://arxiv.org/abs/2606.27472v1)).

## When this backfires

- Most of your changes are not atomic, so the ledger never replaces the retriever. It runs beside it, answers a minority of questions, and you maintain two systems and the extractor that feeds one of them.
- The extractor mis-keys the two states. That step is load-bearing and it is the fragile one. Independent work reports triple extraction producing "thematically inconsistent, logically conflicting, and structurally fragmented graphs that degrade retrieval performance" ([Wu et al. 2026](https://arxiv.org/abs/2606.00610v1)).
- Your read path is naive in some other way. On MemoryAgentBench, "most of the gain therefore comes from separating evidence identification from final policy execution rather than from the freshness operator itself", which contributed 2.0 pp on average and 0 pp at 262K ([Reddy and Challaram 2026](https://arxiv.org/abs/2606.01435v2)).
- The failure you have is retrieval, not currency. An assistant that opens the wrong file has a different problem, and so does one reasoning from a file it read before the last edit, which is the [execution-state ledger](../patterns/agent-design/execution-state-ledger-coding-agents.md)'s territory.

## Example

The bug the paper discloses about itself is the clearest picture of where this breaks. Mid-study, the assertion path "compared values with a normalization that lowercases and strips punctuation", so these pairs read as duplicates rather than changes ([Yadav 2026](https://arxiv.org/abs/2608.20685v1)):

```
Status('Good')  ->  Status['GOOD']    normalized equal, no supersession recorded
/API            ->  /api              normalized equal, no supersession recorded
```

A comparison too loose records a real change as a repeat and leaves the old row valid. A comparison too tight reads a rephrasing as a change and retires a row that was still current. The ledger is worth exactly what that equality test is worth, and the test is hand-written.

## Key Takeaways

- Test the fit before you build. Write down three stale facts your assistant repeated last month; if each reduces to one (subject, relation) pair with a wrong object, this is your shape. If any needs two values true at once, it is not.
- Check coverage before building. If your assistant's stale facts do not reduce to one value under a stable key, 18.4% is your ceiling too.
- The equality test is the system. Too loose and real changes vanish; too tight and current rows get retired.
- The numbers are vendor-reported: a v1 preprint posted 21 August 2026, one 7B local model, 130 scenarios, and an author affiliated to the product under test. Treat the direction as sound and the magnitude as a hypothesis to test against your own history.

## Related

- [Execution-State Ledger for Long-Horizon Coding Agents](../patterns/agent-design/execution-state-ledger-coding-agents.md) — the observation-freshness sibling; tracks whether a file read still describes the repository, where this tracks whether a stored fact is still true.
- [Usage-Reinforced Memory Decay for Long-Running Agents](usage-reinforced-memory-decay.md) — the other axis of memory hygiene; decides what to keep rather than which version is current.
- [Context Lifecycle Management](context-lifecycle-management.md) — the surrounding lifecycle this ledger sits inside: decide, extract, store, consolidate, compact.
- [Schema-Guided Graph Retrieval](schema-guided-graph-retrieval.md) — the same triple-extraction dependency, applied to multi-hop retrieval instead of currency.
- [Dual-Trace Memory Encoding](../patterns/agent-design/dual-trace-memory-encoding.md) — pairs each fact with the scene it was learned in, a different answer to the question of when a memory was formed.
