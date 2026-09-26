---
title: "Stage Elision Before Summarization"
term: "Staged Elision"
description: "Fire deterministic elision at a soft context threshold and the summarizer only at a hard one; across 176 matched coding-agent settings the staged policy held success rates and was cheapest in seven of eight panels."
aliases:
  - staged elision
  - soft-threshold elision
  - two-threshold context management
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-18
maturity: emerging
---

# Stage Elision Before Summarization

> Run rule-based elision at a soft threshold and summarization only at a hard one. Success rates hold; it is cheapest in seven of eight panels.

Adopt this only when the context window binds. That condition carries the whole result. Across four models and two benchmarks, the success-rate gap between managed context and none "shrinks steadily across 32k, 64k, 96k, and 128k windows: from 35.7 to 15.9, 5.5, and 2.7 percentage points on SWE-Bench, and from 9.5 to 7.5, 4.8, and 2.8 on Terminal-Bench" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). Where it does bind, the firing order of your compaction mechanisms decides what you spend.

## The two thresholds

The study fixes the execution loop and varies planning, action space, and context management across 176 matched settings. Context management accounts for 20 of the 22 settings in each model–benchmark pair, five strategies against four window budgets ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). Only the staged tier uses two trigger points. As tested, it also keeps the reversible tier's `recall_event` tool, so every staged result below includes a recall channel.

| Threshold | Mechanism | Price |
|---|---|---|
| Soft (B1) | Elision: bulky middle-region tool observations become short stubs | A string operation, no model call |
| Hard (B2) | Summarization: the oldest middle events fold into a running summary | One extra model call on the transcript middle |

Single-mechanism tiers act only at the hard threshold: "Because Tiers 1–3 each have only one action, they operate at the hard threshold B2, whereas Tier 4 elides at B1 and summarizes at B2" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). What the extra trigger buys is cost, not accuracy. Success rates come out "comparable to T1–T3, with the lowest cost in seven of eight model–benchmark panels" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

## Why it works

Elision is cheap and summarization is not, so firing the cheap one earlier means the expensive one fires less often. Peak context stays below the window and the hard threshold arrives later, or not at all. The paper measures both halves: the staged tier "invokes M3 less often than T3 on average at every budget" and "has the lowest average peak-context ratio at all four window budgets", and reads it this way: "These results suggest that T4's early elision handles many cases before summarization is needed, reducing costly LLM summarization calls and helping explain its lower cost" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

## Skip the recall channel

The study also isolates whether making elision reversible pays, comparing elision alone against elision plus a retrievable external copy of every stub. It does not pay here: "T2 outperforms T1 in 15 settings, underperforms in 14, and ties in three; the equal-weight mean difference is −0.36 percentage points" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

The reason is demand, not implementation. Of the 64 settings that exposed the recall tool, "36 (56.3%) never call recall_event, the median invocation rate is zero", and mean calls per task fall from 0.540 at 32k to 0.007 at 128k ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). Those 64 settings are the T2 and T4 runs. The paper never ran the staged pair without recall, so dropping it rests on the T1–T2 match and on that disuse, not on a direct test. Spend the engineering on overflow prevention instead, where the benefit sits: every managed tier recorded zero overflow failures, against a model-averaged 78.7% for unmanaged SWE-Bench runs at 32k ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

## When this backfires

- Workloads that turn on recovering an exact earlier span. Addressable recall averages 99.40% exact-answer accuracy on needle-in-a-haystack against 88.12% for the best baseline, and only 29.97% against 28.25% on the reasoning-bound LongBench-v2 Hard subset ([Dang et al., arXiv:2607.25066v1](https://arxiv.org/abs/2607.25066v1)). Coding benchmarks sit at the reasoning end of that split. A workload that must quote an old log does not, and there the recall channel is the point.
- Constraints living in the compacted region. Staging adds a second lossy pass over the same text. Across seven models and 1,323 episodes, "compaction raises violation from 0% to 30% (up to 59%)" ([Chen, arXiv:2606.22528v2](https://arxiv.org/abs/2606.22528v2)), so pin governance text out of both passes — see [per-type retention under compaction](per-type-retention-under-compaction.md).
- A wide window. Two thresholds and a stub format are real engineering to aim at the sub-three-point gap left at 128k.
- Reading this as "elision is the cheap tier". On SWE-Bench at 32k, Nemotron-3 120B cost $0.35 per task under elision alone against $0.18 under summarization alone ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). The win belongs to the staged pair, not to elision by itself.
- An evidence base narrower than the recommendation. Four models, three of them one family, two benchmarks, one harness. The authors treat them as "probes of capability and interaction style, not as permanent optimization targets" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

## Example

Nemotron-3 550B on SWE-Bench Verified at a 128k window, summarization alone against the staged policy ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

**Before** — T3, summarization alone at the hard threshold:

```text
success rate   65.80 %
cost per task  $2.54
```

**After** — T4, elision at the soft threshold and summarization at the hard one, recall tool exposed:

```text
success rate   65.80 %
cost per task  $2.33
```

Identical score, 8% less spend. The same model at 32k goes the other way, and this is the seven-of-eight caveat in one panel: summarization alone cost $1.25 per task and scored higher, 58.40% against 55.60% ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)).

## Key Takeaways

- Check whether runs are ending on window length. Below a binding window the whole effect is under three percentage points.
- Order the mechanisms by price: the deterministic pass gets the lower trigger, the model call gets the higher one.
- Expect a cost result, not an accuracy result — success rates were comparable across all four managed strategies.
- Leave the recall channel unbuilt for coding workloads; 56.3% of settings that had it never called it once.
- Revisit the recall decision if your workload has to recover an old observation verbatim. That is the one case where reversibility paid.

## Related

- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](half-life-tool-result-truncation.md) — the elision half on its own, with the same tight-window-only precondition
- [Addressable Recall Compaction](addressable-recall-compaction.md) — the reversibility this page declines to buy, and the retrieval-shaped workload where it wins
- [Observation Masking](observation-masking.md) — replacing a used tool result with a one-line summary, the mechanism the soft threshold fires
- [Per-Type Retention Policy for Agent Compaction](per-type-retention-under-compaction.md) — keeping constraints out of a lossy pass, which staging makes twice as necessary
- [Context Compression Strategies](context-compression-strategies.md) — the wider tiered-compression picture this policy is one instance of
