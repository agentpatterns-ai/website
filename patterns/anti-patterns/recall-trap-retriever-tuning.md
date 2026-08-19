---
title: "The Recall Trap: Tuning a Code Retriever on Recall@k at a Fixed Slot Budget"
term: "Recall Trap"
description: "At a fixed context slot budget, the retriever configuration that maximizes file recall@k can lower issue resolution; the metric to A/B is the task, not the flag."
aliases:
  - recall-maximizing retriever configuration
  - file dedup at fixed context budget
  - retriever objective mismatch on code repair
tags:
  - anti-pattern
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-18
maturity: emerging
---

# The Recall Trap: Tuning a Code Retriever on Recall@k at a Fixed Slot Budget

> At a fixed slot budget, the retriever configuration that maximizes file recall@k can lower issue resolution — A/B the task, not the flag's own metric.

The recall trap is the failure to notice that raising retrieval recall@k under a fixed slot budget can lower the downstream task the retrieval feeds. A controlled SWE-bench Verified study toggles one production flag — one-chunk-per-file deduplication — on an otherwise identical retriever, generator, and 12-slot pack. Deduplication is the higher-recall arm (gold file present in 0.878 of served packs against 0.806), yet turning it off raises the single-shot resolve rate on gpt-5.6-sol from 39.2% to 46.8% (n=500, McNemar exact p=0.0003), and a pre-registered open-weights replication on Qwen3.6-27B carries +3.6pp (n=499, p=0.0133) ([Adkins & Trapaidze, 2026, /abs/2608.14838v1](https://arxiv.org/abs/2608.14838v1)).

## When this applies

The result is scoped, and every scope clause is load-bearing. Treat the pattern as an anti-pattern only inside these conditions:

- The regime is fixed-slot pack-as-sole-context — pack-style RAG serving, seed contexts for constrained agents, cost-capped batch pipelines, or local models that cannot run agentic loops. Retrieval is zero-sum: every slot given to one file is a slot taken from another ([Adkins & Trapaidze, 2026, §1](https://arxiv.org/abs/2608.14838v1)).
- The retriever is an embedding retriever. The effect is confirmed for a multi-signal fusion retriever and reproduces directionally on dense-only. It reverses under a lexical BM25 configuration (dedup-OFF minus dedup-ON = -3.2pp, clustered CI [-5.8, -0.3]pp, significant cross-paradigm interaction) ([Adkins & Trapaidze, 2026, §5.3](https://arxiv.org/abs/2608.14838v1)).
- The budget is tight and the fix is single-file. The trap concentrates on the ~86% of SWE-bench Verified issues that touch one file; the multi-file stratum is a null (+2.2pp, p=0.13). The advantage grows with the slot budget from +4.8pp at K=4 to +9.2pp at K=40 on a clean model ([Adkins & Trapaidze, 2026, §5.9](https://arxiv.org/abs/2608.14838v1)).

Outside those conditions the diversification default is often correct — file-level recall@k is the metric a one-per-cluster rule is designed to move, and the underlying preference (MMR, α-nDCG, xQuAD) has a long IR literature behind it.

## Why it works

The recall-maximizing configuration is defensible for the metric it targets. If the pack budget is k slots, spending two slots inside one file cannot help the "does the gold file appear anywhere" metric, so one-per-file post-filtering diversifies coverage and raises file recall@k in the index eval (0.666 to 0.817 in the paper's system) and on served packs (0.806 to 0.878) ([Adkins & Trapaidze, 2026, §2](https://arxiv.org/abs/2608.14838v1)).

The trap is that the reader's objective is not the retriever's. The model reading a code-repair pack needs the exact lines to reproduce a fix, and file-level recall@k does not see them. Anchor dose — line-level localization recall on the served pack — shifts approximately 15 percentage points of instances into a stratum where resolve rates jump from ~35% to ~55%, and the depth arm delivers that shift by roughly doubling gold-line coverage from 0.090 to 0.179 on fusion packs ([Adkins & Trapaidze, 2026, §5.4](https://arxiv.org/abs/2608.14838v1)).

The mediator is partial rather than full. A within-stratum residual remains after conditioning on anchor visibility (dedup-OFF still beats dedup-ON by +7 to +13.6pp among anchor-visible instances), so anchor dose accounts for roughly 40% of the effect and the rest is unexplained ([Adkins & Trapaidze, 2026, §5.4](https://arxiv.org/abs/2608.14838v1)). A random-chunk-per-file control on Qwen3-Coder-30B refutes the alternative that dedup-ON keeps the wrong within-file chunk: replacing the kept argmax with a random non-argmax chunk from the same file drops resolve from 6.6% to 3.0% rather than recovering toward the depth arm's 12.4% ([Adkins & Trapaidze, 2026, §5.4](https://arxiv.org/abs/2608.14838v1)).

The paper frames this as an execution-graded, code-repair instance of the known relevance-diversity and objective-mismatch tradeoff, not a new phenomenon. The nearest prior mechanism holds context length and gold position fixed in multi-hop QA and varies only document count, isolating up to a 20% degradation from breadth alone ([Levy et al., 2025, /abs/2503.04388v3](https://arxiv.org/abs/2503.04388v3)).

## When this backfires

The "disable file deduplication" recommendation itself has scope conditions. Applying it outside them costs recall for nothing:

- A BM25 or other lexical retriever flips the sign. BM25's depth arm raises within-file anchor dose by only +0.029 against fusion's +0.089, so the mechanism the trap runs on barely materializes ([Adkins & Trapaidze, 2026, §5.3, §5.4](https://arxiv.org/abs/2608.14838v1)).
- An unrestricted-Read agentic harness stops the fixed budget from binding. Every model-matched agentic comparison the paper ran is a powered null (fusion, sonnet-5, n=499, Δ -1.4pp, MDE 4.5pp), including on the primary retriever. A tool-using agent that reads on demand is a different regime ([Adkins & Trapaidze, 2026, §5.5](https://arxiv.org/abs/2608.14838v1)).
- A large agent context window is where breadth recovery pays. `From Fragments to Paths` reports +8.2pp on SWE-bench Verified (70.4% to 78.6%, p<0.01) by expanding task-level context, in a regime where every compared system retrieves roughly ten times the gold set ([He et al., 2026, /abs/2606.22906v1](https://arxiv.org/abs/2606.22906v1)). Any breadth-favoring crossover lies well beyond the recall trap's tested K=40 ceiling.
- Multi-file fixes are a null. The single-arm advantage on multi-file gold patches does not reach significance. The trap is a single-file-fix effect ([Adkins & Trapaidze, 2026, §6.2](https://arxiv.org/abs/2608.14838v1)).
- Non-Python or non-SWE-bench-Verified workloads are unconfirmed. The pre-registered pooled multilingual test on SWE-PolyBench (Java, JavaScript, Python, TypeScript, N=617) is directionally positive but not significant (+2.6pp, p=0.056); heterogeneity tracks the instance pool rather than the surface language. Treat generality as a mapped boundary, not a confirmed extension ([Adkins & Trapaidze, 2026, §5.10](https://arxiv.org/abs/2608.14838v1)).

## Example

The transferable action is not "always disable dedup". It is: measure the retrieval flag against the downstream task under the deployment regime, not against the retrieval metric the flag was tuned to. The paper's own operational rule reads: "do not hard-deduplicate by file, and A/B packing policies against the task, not the metric the flag was tuned to" ([Adkins & Trapaidze, 2026, §6.3](https://arxiv.org/abs/2608.14838v1)).

**Before — recall-maximizing default at a tight fixed budget:**

```yaml
retriever: fusion            # dense + lex + graph
pack:
  budget_slots: 12           # tight, zero-sum
  file_dedup: true           # one chunk per file, raises file recall@k
grading:
  metric: file_recall_at_k   # tuned against the retrieval index eval
```

**After — task-graded A/B, dedup toggled:**

```yaml
retriever: fusion
pack:
  budget_slots: 12
  file_dedup: false          # spend slots on within-file depth
grading:
  metric: issue_resolve_rate # graded by the task the pack feeds
  paired: true               # McNemar on per-instance outcomes
```

Ship the arm the paired task test picks, and re-run the test whenever the retriever, chunker, budget, or model changes. The recommendation is scoped to embedding retrievers under a tight fixed budget; a BM25 arm or an agentic harness that adds Read must be tested separately because the sign changes under both ([Adkins & Trapaidze, 2026, §5.3, §5.5](https://arxiv.org/abs/2608.14838v1)).

## Key Takeaways

- Under a fixed slot budget, retrieval recall@k and downstream resolve rate are different objectives and can point in opposite directions. Grading a retrieval flag against the metric it directly moves is the trap.
- The pattern's mechanism is anchor dose. Depth roughly doubles gold-line coverage and shifts instances into a stratum with dramatically higher resolve rates ([Adkins & Trapaidze, 2026, §5.4](https://arxiv.org/abs/2608.14838v1)).
- The gain is quality-driven, not producibility-driven. On gpt-5.6-sol and DENSE-1 the "correct given attempt" channel carries 88 to 94% of the delta, so the effect is not "depth produces more anchorable patches" ([Adkins & Trapaidze, 2026, §5.2](https://arxiv.org/abs/2608.14838v1)).
- The recommendation is scoped. Verify the retriever paradigm, the harness regime, the budget range, and the fix locality against the paper's boundary map before adopting.
- Task-graded A/B is the durable move, and it does not need an oracle. Anchor dose is a retrospective diagnostic, not an inference-time signal.

## Related

- [Per-Object Context Allocation (Selective Invariance)](../../context-engineering/per-object-context-allocation.md) — the adjacent allocation lever; caps how many slots one code object may claim, where the recall trap is about which files claim slots at all
- [Chunking Strategy for RAG-Based Code Completion](../../context-engineering/chunking-strategy-rag-code-completion.md) — chunking decides how many views one object produces; the recall trap decides how they compete for a fixed slot budget
- [Component-Wise RAG Prioritization for Software Engineering Tasks](../../context-engineering/rag-component-prioritization-software-engineering.md) — retriever choice dominates generator choice for SE-task RAG; the recall trap is a scoped counter-example on packing policy inside a retriever
- [Exhaustive Retrieval for Listing Questions](../../context-engineering/exhaustive-retrieval-for-listing-questions.md) — a different objective-mismatch case: ranked retrieval optimizes the wrong objective when the answer is a set
- [Density-Normalized Quality Metrics Mask AI-Driven Code Growth](density-normalized-quality-metric.md) — the moving-denominator sibling: an intuitively defensible ratio moves for reasons the ratio itself cannot report
