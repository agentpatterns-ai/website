---
title: "Usage-Reinforced Memory Decay for Long-Running Agents"
term: "Usage-Reinforced Memory Decay"
description: "Score retention with a forgetting curve whose stability compounds on every recall, so frequently-consulted facts outlive the idle stretches that silently evict them from a fixed recency window."
aliases:
  - usage-reinforced decay
  - forgetting-curve memory eviction
  - reinforced stability decay
tags:
  - tool-agnostic
  - context-engineering
  - memory
  - agent-design
last_reviewed: 2026-07-26
maturity: emerging
---

# Usage-Reinforced Memory Decay for Long-Running Agents

> Each recall multiplies a memory item's stability, so heavily-used facts survive idle stretches that a fixed recency window silently evicts.

Reach for usage-reinforced decay when the facts you cannot afford to lose are ones the agent keeps consulting. It replaces the recency window's binary "touched within N turns" test with a continuous retention score that rises every time an item is recalled. It gives you nothing for a constraint stated once and never referenced again.

## How it differs from a recency window

A recency window evicts on elapsed turns alone. Usage-reinforced decay evicts on a retention score, and each recall permanently reshapes that item's future curve ([Towards Data Science, 2026-07-24](https://towardsdatascience.com/context-windows-forget-what-matters-i-used-a-140-year-old-psychology-paper-to-fix-ai-memory/)).

| Behavior | Recency window | Usage-reinforced decay |
|---|---|---|
| Eviction test | `current_turn - last_touched > window` | retention below threshold (default 0.20) |
| Effect of a recall | resets the clock | raises stability, flattening the whole future curve |
| Day-one fact recalled six times | evicted on the first long gap | still resident |
| Fact stored once, never recalled | evicted | evicted, on the same schedule |

The reference implementation is deterministic by construction. It counts turns with an explicit integer rather than reading `time.time()` and uses only the Python 3.12 standard library. It also produced byte-identical output when the same suite was diffed across Linux and Windows ([the decay-engine writeup](https://towardsdatascience.com/context-windows-forget-what-matters-i-used-a-140-year-old-psychology-paper-to-fix-ai-memory/)).

## Why it works

Retention decays as `Ret = e^(-t / S)` over turn-distance `t`. A recall updates the item's stability with `S_new = S_old × (1 + ln(1 + recall_count))` ([the decay-engine writeup](https://towardsdatascience.com/context-windows-forget-what-matters-i-used-a-140-year-old-psychology-paper-to-fix-ai-memory/)). Stability sits in the denominator of the exponent. Raising it flattens the entire remaining curve instead of moving the item to the front of a queue. A recency window can only answer "how long since this was touched", which discards the evidence that the agent has needed the item repeatedly. The logarithm keeps compounding sublinear, so stability grows without the resident set growing with it. The same run reports a token-footprint reduction of 0.911 against the baseline's 0.898.

The same causal structure appears independently in [FadeMem](https://arxiv.org/abs/2601.18642), which strengthens memories on access under an Ebbinghaus-style decay. It reports 82.1% critical-fact retention against Mem0's 78.4% at 45% lower storage on LoCoMo, Multi-Session Chat, and LTI-Bench.

## When this backfires

- Write-once constraints get no protection. A "never edit this file" rule recalled zero times decays at the baseline rate. [The decay-engine writeup](https://towardsdatascience.com/context-windows-forget-what-matters-i-used-a-140-year-old-psychology-paper-to-fix-ai-memory/) measures both policies at 0.000 terminal recall for single-use facts. That is the most common shape of the silent failure the technique is sold to fix. Pair it with an explicit pin or a write-time salience score.
- Frequency diverges from importance. A config path re-read out of habit accrues stability while a rarely-surfaced safety constraint does not. [Novel Memory Forgetting Techniques for Autonomous AI Agents](https://arxiv.org/abs/2604.02280) adds a semantic-alignment term alongside frequency for exactly this reason. It scores importance as `I = α·recency + β·frequency + γ·semantic alignment`.
- Contradictory facts both survive. The engine ships no conflict resolution. If two incompatible statements are each reinforced, each stays resident, and the compounding makes the stale one progressively harder to evict.
- Item sizes vary widely. Retention is scored per item, not per token, so a four-token rule and a multi-kilobyte stack trace compete on equal terms. Weight by payload length before trusting it as a budget control.
- The session shape differs from the tuning set. The defaults (threshold 0.20, base stability 8.0) were fitted to a burst-then-silence pattern and need re-fitting for a steady drip of recalls.
- Recall detection is unsolved outside simulation. Production has to infer what counts as genuine memory usage; a loose detector inflates every item's stability and the policy collapses toward keeping everything.

The strongest case against the technique is that importance belongs on the write, not the read. A salience score set by the model that extracted the fact is available on turn one, before any recall exists to count. [A rate-distortion account of memory compaction](https://arxiv.org/abs/2607.08032) formalizes this: retention should minimize downstream task degradation, and access count is at best a correlate of that.

## Example

The published harness runs 50 seeded 150-turn sessions across 15 threshold and window combinations (thresholds 0.10, 0.20, 0.30; windows 10, 15, 20, 30, 50). It seeds three foundational facts recalled at turns 3, 8, 20, 45, 90, and 150 with 30% jitter, against three throwaway items per turn. Terminal foundational recall comes out at 1.000 for the decay engine and 0.000 for the recency baseline, both with zero standard deviation ([the decay-engine writeup](https://towardsdatascience.com/context-windows-forget-what-matters-i-used-a-140-year-old-psychology-paper-to-fix-ai-memory/)).

Read that contrast against its schedule. The last two scheduled recalls sit roughly 60 turns apart, wider than the widest window tested. A fixed window therefore cannot reach the terminal measurement holding the fact. The 0.000 is a property of the harness rather than a field result. Take the run as evidence that reinforcement changes the retention curve, then measure the gain on your own recall distribution before budgeting for it.

## Key Takeaways

- Usage-reinforced decay pays off only where recall frequency tracks importance; it is not a general replacement for a recency window.
- The reinforcement is structural — a recall raises stability and flattens the item's whole future curve, rather than resetting a timer.
- A fact stored once and never recalled decays exactly as it would under a plain window, so critical write-once constraints still need an explicit pin.
- The published 100%-versus-0% contrast comes from a synthetic schedule whose final recall gap exceeds every window tested; treat it as a mechanism demonstration, not a benchmark.
- Systems that ship this on real workloads combine usage with a semantic or importance term rather than relying on the recall counter alone.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the tiered offload-and-summarize frame whose recency-window pruning tier this technique replaces.
- [Tiered Memory Architecture](../patterns/agent-design/tiered-memory-architecture.md) — where a decay policy sits relative to working, episodic, and long-term stores.
- [Generative Agents Memory Stream](../patterns/agent-design/generative-agents-memory-stream.md) — scores retrieval by recency, relevance, and importance; the read-side counterpart to this write-side eviction policy.
- [Memory Retrieval as Control](../patterns/agent-design/memory-retrieval-as-control.md) — why stale-entry lockout makes eviction and freshness discipline mandatory in any persistent memory.
- [Context Lifecycle Management](context-lifecycle-management.md) — the decide, extract, store, consolidate, compact loop that an eviction policy plugs into.
