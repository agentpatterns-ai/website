---
title: "Scoring a Compaction Policy on Latency and Billed Cost"
term: "Compaction Policy Scoring"
description: "Token count does not predict what compaction costs: score a policy on wall-clock latency and billed input cost, per model and per workload."
aliases:
  - compaction policy evaluation
  - context compaction cost measurement
  - compression policy latency and cost
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-29
maturity: emerging
---

# Scoring a Compaction Policy on Latency and Billed Cost

> On SWE-bench with Qwen, compaction policies using about 0.6x the tokens of full context still billed 0.71 to 0.95x the cost.

Compaction policy scoring is judging a trajectory-compaction setting by the latency and the bill it produces rather than by the tokens it removes. A harness that compacts picks what gets removed or rewritten, when that fires, and how much goes ([Satish et al., arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). The evidence is a 65-policy sweep across three open-weight models, two coding benchmarks, and "nearly 35,000 agent executions" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Every cost figure from that paper is an estimated billed input cost, not a provider invoice.

## Check these conditions first

- Compaction fires before the context limit rather than at it. Triggers sat near the 5th, 15th and 25th percentile of the peak context each uncompressed run reached. Qwen's SWE-bench settings correspond to about the 5th, 16th and 28th. The paper places Claude Code's mechanism, from documentation it accessed in September 2026, "at the context limit (0.97 on a 1M window)" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).
- You can read a real bill. Cost here is estimated under an assumed cache discount where cached input costs a tenth of fresh input: "This is an estimate under the assumed cache discount, not a measured provider bill or cache-hit rate; Qwen was served with prefix caching disabled" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).
- Your latency profile resembles theirs. All three models ran locally under vLLM on A100 and RTX A6000 GPUs ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## What token count misses

Most policies tested cut token use, and token count did not predict latency or cost. On SWE-bench with Qwen, policies clustered at 0.56 to 0.63x the tokens spanned about 12 percentage points of resolve rate, 0.79 to 1.0x latency, and 0.71 to 0.95x billed cost ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Terminal-Bench traded differently. Policies at roughly a third of the tokens can take 1.2 to 1.8x as long, and some cost more than leaving the context alone, though billed cost still fell for 9 of the 12 ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

Two mechanisms break the link. Billed cost follows what stays eligible for the cached rate, and the paper names the cause directly: "A policy that frequently rewrites the trajectory can remove tokens while invalidating much of the reusable prefix" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Latency depends on call count and on the calls themselves. Step-triggered policies cut the most tokens per step but "require 10–27% more calls across models". On Qwen, "faster calls more than offset the additional calls"; on Devstral, "calls themselves become slower" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Terminal-Bench triggers compression more often than SWE-bench, with Qwen's TR policy compressing about 9 times per run against fewer than 2 on shared solved tasks. In the same comparison, "summarization calls account for 28–46% of solved-run wall-clock time for the 4 summarization primitives" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

Start with the trigger. Raising Qwen's SWE-bench threshold from 10K to 20K tokens at depth 0.5 cut compaction from 4.85 to 1.15 events per attempt. For whole-window summarization, resolve rate rose from 50.7% to 62.7%, input cost fell from 1.10x to 0.92x, and latency fell from 653 to 599 seconds ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## What a matching resolve rate hides

Aggregate success is not task coverage. Compaction policies newly solved 2 to 7 of the 47 SWE-bench tasks Qwen had missed, and lost 6 to 14 of the 53 it had solved. One stacked policy finished 52 tasks against full context's 53, and it "newly solves 7 tasks while losing 8 previously solved tasks" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). The authors conclude that "approximately matching full-context success does not mean preserving its task coverage".

The policy also moves with the model. Per-step tool-result clearing reached 51.3% resolve on Qwen and 41.3% on GLM, cutting latency below full context in both. On Devstral the same policy dropped to 38.7% and raised latency to 1.42x. Across the grid, "no single compression policy performs best across models, and a policy that is effective for one model can be substantially worse for another" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

Two design choices did carry. On SWE-bench, preserving recent history under structured rewriting gained 6.7, 8.7 and 8.0 percentage points across the three models. Clearing tool outputs before structured rewriting gained 7.7, 9.7 and 9.7 ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## Why it works

The study prices cached input at a tenth of fresh, so the bill depends on how many input tokens remain eligible for the cached rate. A policy that rewrites the trajectory often can remove tokens and still lose that rate. Another team, measuring compaction on HotpotQA and LoCoMo rather than a coding benchmark, reports that "the blocking call stalls agent inference for tens of seconds" ([Parallel Context Compaction, arXiv:2605.23296v1](https://arxiv.org/abs/2605.23296v1)).

## When this backfires

- Blame the compactor before the policy. On HotpotQA and LoCoMo, not a coding benchmark, parallel compaction "reduces end-to-end wall time and improves compaction throughput over the sequential baseline" at matched decode volume ([arXiv:2605.23296v1](https://arxiv.org/abs/2605.23296v1)). Check whether the summarizer call blocks the agent before you re-rank anything.
- A policy designed around cost delivers cost. CliffCompaction "reduces cost by up to 50% under a bounded context while maintaining or improving performance on Terminal-Bench", by only truncating or dropping content and "never rephrasing or rewriting" it ([arXiv:2609.26779v1](https://arxiv.org/abs/2609.26779v1)).
- You cannot run the sweep. Nearly 35,000 executions produced these ratios, and the paper's Terminal-Bench call-count estimates "use only 2–15 tasks and should be interpreted alongside their uncertainty intervals" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).
- Your agent can cheaply re-derive what compaction dropped. The authors suspect workload explains the benchmark gap, since "SWE-bench agents can recover working context from code and patches, whereas Terminal-Bench's varied workflows may depend more on intermediate observations and action history" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

## Example

Scoring two policies the way this page describes, both on Qwen and SWE-bench. The first clears older tool results once the primary token threshold is reached. The second is the standalone step-triggered policy, which the paper runs without an operative token threshold ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)).

| Policy | Resolve rate | Latency vs full context | Billed cost vs full context |
|---|---|---|---|
| Clear older tool outputs at the threshold | 53.7% | 0.79x | 0.71x |
| Clear tool outputs after every agent step | 51.3% | 0.88x | 0.95x |

The second policy bills a third more for 2.4 percentage points less resolve.

## Key Takeaways

- Record latency and billed input cost per policy alongside tokens. A 0.6x token ratio came with bills between 0.71x and 0.95x on one model and one benchmark.
- Sweep the trigger threshold before you change the compaction operation. Raising Qwen's SWE-bench threshold from 10K to 20K improved resolve rate for every tested primitive, and for whole-window summarization it also cut cost and latency.
- Compare task sets rather than aggregate resolve rates. One SWE-bench policy solved 52 tasks against full context's 53, yet it newly solved 7 and lost 8.
- Treat a policy choice as model-scoped. The same per-step clearing policy helped two models and cost Devstral 1.42x latency.

## Related

- [Measuring Reacquisition Cost Under Context Compaction](reacquisition-cost-measurement.md) — the interaction-cost half: split tool calls into retrieval and execution to see what a flat completion rate hides.
- [Stage Elision Before Summarization](stage-elision-before-summarization.md) — one policy inside this design space, staging a deterministic step ahead of the summarizer.
- [Choosing a Compression Budget for Agent Control Context](control-context-compression-budget.md) — the same argument applied to the static instruction layer rather than the running trajectory.
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — why an invalidated prefix is the expensive part of a rewrite.
- [Context Compression Strategies](context-compression-strategies.md) — the compaction operations themselves, offloading and summarization.
