---
title: "Scoring a Context Policy on Executed Prefill"
term: "Executed-Prefill Accounting"
description: "Where a runtime reuses prefixes, a policy that rewrites already-sent history can cut prompt volume a third and still leave the server seven times the prefill to execute."
aliases:
  - uncached prefill accounting
  - prefix reuse accounting
  - physical cost of context
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-10-28
maturity: emerging
---

# Scoring a Context Policy on Executed Prefill

> Where the runtime reuses prefixes, a policy that rewrites sent history can cut prompt volume 33.3% and raise executed prefill 608.5%.

Executed-prefill accounting scores a context policy on the input tokens the server actually processes, which is the logical prompt minus the tokens served from a reusable prefix ([Yu et al., arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). Record it beside the request count instead of reporting prompt volume alone. Prompt volume misorders policies in one specific direction: "Prompt savings therefore increase executed prefill when a policy loses more reusable tokens than it removes" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

## Check these conditions first

- Your runtime reuses prefixes, and serves enough of them. The break-even has a stated form, offered as a first-order estimate. Set the 75.1k logical tokens one masking policy removed per attempt against the 135.9k reused tokens it lost, and executed prefill only rises above a reuse fraction of roughly 0.55. Below that, "without a prefix cache, masking would save prefill" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). Batching and cache pressure that evicts prefixes push the fraction down and the penalty with it.
- Your policy edits history the runtime has already sent. That masking arm kept every action and shortened each tool output older than the latest five to a placeholder, so "once the window fills, every request rewrites an observation that the previous request had already sent" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). Editing is the trigger, because policies "save physical work by shortening the trajectory and can multiply it by editing reusable history" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).
- You can read a server-side reuse counter. These figures come from server counters rather than a provider bill, and on the patching stack "SGLang counters also separate device hits from uncached prefill" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

## What to record

Four numbers per attempted task, with failed attempts kept in the denominators: logical prompt tokens, request count, reused prefix tokens, and executed prefill. "Reports should therefore expose request count, prefix reuse, and uncached prefill alongside prompt volume" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

Prompt volume and executed prefill are not interchangeable. Over a fixed 100-task localization set, 600 cells in all, turning on one vLLM prefix-cache flag raised the eager policy's logical prompt by 8.3%, with a 95% interval running from a 5.7% fall to a 24.7% rise, and cut its executed prefill by 67.7%, interval -71.0% to -63.8% ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). The first figure could not be signed. The second fell by two thirds.

## Gate on quality before you compare resources

Run the non-inferiority test first and compare resources only among the policies that pass. The study's rule admits a policy when the lower endpoint of a paired 95% interval on its quality difference stays above -5 points.

The cheapest policy on prompt volume is the one that fails. On 100 SWE-bench Verified instances under mini-SWE-agent with a 32-call budget, the masking arm resolved 26 against the eager arm's 29, a paired difference of -3.0 points whose lower endpoint of -8.6 crosses the threshold. The authors name the consequence directly: "token count alone would favor the policy that the gate excludes" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

## Why it works

A caching runtime such as vLLM or SGLang keeps the key-value entries of earlier requests and prefills only the tokens after the longest cached prefix, so editing an early token forces every later token to be recomputed ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). Re-serializing history on every request costs the whole tail, not the bytes removed. In the measured contrast, cached prefixes "serve about 96% of Eager's prompt but 53% of Mask-5's" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)), and removing 75.1k logical tokens per attempt lost 135.9k reused ones, adding 60.8k executed prefill. The authors hedge the attribution: "The prefill inversion is consistent with reduced prefix-cache reuse after repeated history edits. Trajectory changes may also contribute to the observed resource differences" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

Request count is the second channel, and on the localization cohort it was the one that paid. Preloading ten retrieved blocks cut successful server calls 35.7% and the GPU-energy proxy 33.2% against on-demand search, with prefix caching disabled for that matrix, while per-call latency rose: "Mean TTFT varies by less than 2%, and latency per successful call rises from 5.218 to 5.721 seconds (Eager) and 5.468 (Compact), so the task-time saving comes from fewer calls" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

## When this backfires

- There is no prefix reuse to lose. At a reuse fraction of zero the identity reverses, and prompt volume is then the right score.
- Your policy appends instead of rewriting. The eligible arm with the largest saving prepended evidence and kept its full history, so prefill accounting would credit the wrong channel for its win.
- Token accounting already reached the same answer. The masking study this paper cites reports simple observation masking as efficient as model summarization for agent context management ([Lindenbauer et al., arXiv:2508.21433](https://arxiv.org/abs/2508.21433)), and [observation masking](observation-masking.md) covers that case. The result holds where reuse is low, so the inversion narrows where masking pays rather than retiring it.
- Measuring prefill does not endorse compacting. The anchored compaction arm passed the quality gate and bought nothing, using 8.5% more prompt tokens, 13.3% more calls, 8.2% more wall time and 9.4% more energy than its retrieval-matched control, because "shorter requests do not offset its additional calls" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).
- You need the magnitudes rather than the direction. "Results cover two stacks on one DGX Spark serving one request at a time; batching, cache pressure, and cloud GPUs remain untested" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)). Quality came from 450 localization cases and the cost figures from a separate 100-task cohort, server and energy intervals rest on three shards, and the energy figure is a sampled GPU proxy that "is not whole-system energy" ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

## Example

Mini-SWE-agent v2.4.6 ran 100 SWE-bench Verified instances under a 32-call budget, served by SGLang with RadixAttention. Both arms received the same ten retrieved blocks, and the masking arm additionally shortened every tool output older than the latest five. Percentages are the paper's, relative to the eager arm ([arXiv:2610.34763v1](https://arxiv.org/abs/2610.34763v1)).

| Per attempt | Eager | Mask-5 |
|---|---|---|
| Prompt tokens | 225.6k | 150.5k (-33.3%) |
| Executed prefill | 10.0k | 70.8k (+608.5%) |
| Model calls | 25.66 | 26.33 (+2.6%) |
| Wall seconds | 122.7 | 167.9 (+36.9%) |
| GPU-energy proxy | 1.956 kJ | 4.412 kJ (+125.6%) |
| Resolved of 100 | 29 | 26 |

On the prompt column the masking arm wins outright. On the prefill column it does seven times the server work, takes a third longer, and fails the quality gate. Both the prompt and the prefill direction held across all eight paired shards.

## Key Takeaways

- Log executed prefill, reused prefix tokens and request count beside prompt volume. One toggle of a prefix-cache flag moved prompt volume by an unsignable 8.3% and executed prefill by -67.7%.
- Apply the quality gate before the resource comparison. The arm that cut prompt volume 33.3% also fell 3.0 resolve points, with a lower endpoint of -8.6 against a -5 threshold.
- Work out your break-even before deleting history. Masking removed 75.1k logical tokens and lost 135.9k reused ones, which only pays below a reuse fraction of about 0.55.
- Check which channel a saving came from. Against on-demand search, with caching off, the eager arm finished localization 29.4% faster on 35.7% fewer calls while each call got slower.

## Related

- [Batched Context Eviction for Cache Reuse](batched-context-eviction.md) — the cadence prescription this page supplies a counter for: cut in large batches so the prefix holds still between cuts.
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — why an invalidated prefix is the expensive part of any rewrite.
- [Scoring a Compaction Policy on Latency and Billed Cost](compaction-policy-latency-and-cost.md) — the same warning reached through an estimated bill, on a model served with prefix caching disabled.
- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](half-life-tool-result-truncation.md) — a per-step trimming policy of the family that triggers the inversion, scored on fix rate instead.
- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md) — the policy class under test, and the token-accounting case for it.
- [Measuring Reacquisition Cost Under Context Compaction](reacquisition-cost-measurement.md) — the tool-call side of the same ledger, splitting calls into retrieval and execution.
