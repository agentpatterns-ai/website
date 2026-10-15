---
title: "Evidence-Path Divergence for Multi-Agent Fault Tolerance"
term: "Evidence-Path Divergence"
description: "A second delivery route held 53.0% of faulted runs against 3.3% for a single chain, but only where it branches downstream of the evidence it carries and escapes the same fault."
tags:
  - agent-design
  - multi-agent
  - reliability
  - tool-agnostic
  - arxiv
aliases:
  - redundant evidence path
  - alternate evidence route
  - evidence branch point
last_reviewed: 2026-10-14
maturity: emerging
---

# Evidence-Path Divergence for Multi-Agent Fault Tolerance

> A second evidence route held 53.0% of faulted runs against 3.3% for a single chain, and its fault tolerance turns on where it branches.

Evidence-path divergence is the point where a redundant delivery route splits from the primary one, measured against the point where the information it carries gets produced. Downstream of that point, and only while the fault does not also reach it, the second route is a fault-tolerance control. Upstream of it the measured gain stays under 0.7%, because both routes then wait on the same message that never arrived.

## The two conditions

Zhou and colleagues injected receiver-visible communication faults into three AutoGen topologies, over 100 tasks from five domains and three model configurations ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1)). Injection landed at three boundaries: the action request, the observation return, and the evidence handoff to the verifier. Flat is Sequential plus one direct branch forwarding the same worker evidence to the decision agent. Across applied faulted executions with known outcomes, Flat kept 53.0% task success where Sequential kept 3.3% and Hierarchical 3.2%.

That aggregate hides where the money is. In the paired comparisons the gain sits at one boundary: "Its success-rate gain reaches 66.5% to 66.6% for evidence-handoff non-delivery and 41.3% to 42.3% for evidence-handoff corruption. The gain remains below 0.7% when the affected communication occurs before the additional path receives the required evidence" (§4.4). That is the positional condition, and it is sharp.

Independence is the other one. A second copy of the affected message is not redundancy: "Forwarding another copy of corrupted evidence preserves the same incorrect information, whereas independent reacquisition obtains a fresh observation for downstream agents" ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1), §4.5). With 18 runs per arm, Flat held all 18 while the fault touched the handoff and the recovery deliveries, and recovered 0 of 18 once it reached every evidence path.

## Why it works

The branch works because it does not depend on the thing that broke. The paper names the structure plainly ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1), §4.4): "The Flat branch diverges after the Worker has generated the required evidence. A fault at the evidence handoff can affect one route while the second route continues to carry the same evidence to the final decision. Faults at the request and state return stages occur before this divergence." It calls the result consistent with a dependability principle from earlier work: "redundancy helps when an alternative path avoids the affected dependency" (§4.4). What decides the outcome is whether a surviving route reaches information the fault never touched. That is why a later tool observation recovers an upstream loss that duplicated delivery cannot.

Changing the model configuration does not substitute for it either. The comparison runs over 1,408 faulted units common to all three models and all three topologies: "changing the LLM recovers only 0.2% to 4.5% of baseline failures, while changing to Flat recovers 19.3% to 27.0%". The two recovered sets barely intersect, at a Jaccard similarity of 0 to 0.047 ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1), §4.4).

## What the redundancy leaves behind

Adding the route removes the loud failures and leaves the quiet ones. Among 8,335 failures with complete detection records, 20.7% produced no immediate failure signal. The share rises to 76.2% for partial-content faults and falls to 2.3% for non-delivery at the request boundary ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1), §4.2). Delivery faults announce themselves. A message with three evidence fields stripped out still parses.

The per-execution silent rate barely moves, at 17.6% under Sequential against 16.6% under Flat in the detection-complete matched cohort. The share of remaining failures that are silent goes from 18.6% to 51.6% (§4.4). A team that stops after adding the route has a smaller failure count and a harder one to diagnose. Pair the route with a check on the evidence contract.

In the targeted study, Flat's baseline completed every evaluated faulted execution successfully while 97.2% of them contained a recorded incorrect intermediate evidence acceptance.

Gate that recheck on a contract violation rather than running it always: guarded readback removed two workflow HTTP requests per clean execution, 15.4% under Sequential and 13.3% under Flat, with task success and model-call count unchanged (§4.5).

## When this backfires

Every figure below is from the same study ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1)) unless another source is named.

- The fault lands upstream of the branch. At the request boundary the paired success-rate difference stayed within 0.5%, and at the state-return boundary within 0.7% for non-delivery and 0.3% for semantic corruption. The second route is cost for a return under one point there.
- One shared dependency carries both routes. Same transport, same endpoint, same provider, and the fault reaches both: 0 of 18 runs recovered under full evidence-path exposure.
- The task does not gate its answer on delivered evidence. Shopping was the weak case here, with Flat's success at the evidence handoff ranging from 0% to 53.3% across the three models. There, an environment action can already have succeeded before the fault changes the evidence used for acceptance.
- The added structure is itself a risk. MAST's authors report that for multi-agent systems "their performance gains on popular benchmarks are often minimal", and one of its three failure categories is inter-agent misalignment ([Cemri et al., 2025](https://arxiv.org/abs/2503.13657v3)). Each new edge is a surface, not only a spare.
- Protection may have been the cheaper buy. Pairing execution-side with evidence protection restored every Sequential failure, 0 to 18 of 18, where corruption stayed at the initial handoff and the recovery delivery was unaffected (§4.5). Evidence protection on its own uniquely recovered 32.1% of 106 baseline failures that execution-side protection missed. Both rest on small samples, and the two recovery sets did not overlap, so neither mechanism substitutes for the other.
- This study's settings differ from yours. The authors restrict their conclusions to the evaluated settings, with effects that "may still depend on the evaluated communication paths, task contracts, runtime mechanisms, and framework implementation" (§5.3).

## Example

The WebArena Admin results show both conditions inside one table. Under non-delivery at the evidence handoff, DeepSeek-backed Sequential succeeded on 0.0% of matched runs and Flat on 94.4%. Move the same fault one boundary earlier, to the observation return, and the gap closes: Sequential 72.2%, Flat 75.9% ([Zhou et al., 2026](https://arxiv.org/abs/2610.15459v1), §4.3).

The traces say why. Admin's observation return sits inside an iterative tool loop, so another observation can still arrive. Of 110 matched DeepSeek executions under Sequential and Hierarchical, 82 received a later table carrier after the fault. Of those, 74 eventually succeeded, and all 28 with no later carrier failed. By the evidence handoff the navigation loop has finished, and none of the 110 matched runs at that boundary contained a later tool call. The only surviving source of the information is then a branch that already holds it.

## Key Takeaways

- Site the branch by where the information it carries is produced. Draw the workflow, mark that point, and a branch upstream of it is not redundancy.
- Write down which dependency each route shares with the other, then assume a fault can take the shared one. Count two routes over one transport, endpoint or provider as one.
- Prefer reacquiring the information to forwarding a second copy of it. A copy of corrupted evidence carries the same error forward.
- Do not reach for a different model configuration to fix a delivery fault. Changing it recovered 0.2% to 4.5% of baseline failures across the common cohort, against 19.3% to 27.0% for changing the route.
- Budget for a second control once the route is in. The route changed the failure mix more than the silent rate, so just over half of what survived it was the class nothing reported.
- Trigger the evidence recheck on a contract violation rather than on every handoff, so the clean path stops paying for reacquisition it does not need.

## Related

- [Difficulty-Aware Topology Selection for Coding Agents](difficulty-aware-topology-selection.md) — picks the collaboration structure per task on cost and pass@1, the other axis of the same topology decision
- [Handoff-Boundary Fault Injection (llmmas-otel)](../../verification/handoff-boundary-fault-injection.md) — injects a delay at an agent-to-agent send and measures runtime amplification rather than correctness
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — the vocabulary for the topologies compared here, chosen from task structure and shared state
- [Failure-Aware Observability for Multi-Agent LLM Systems](../../observability/failure-aware-observability-multi-agent.md) — the trace signals that make an accepted-but-wrong evidence handoff visible mid-run
- [Auditing Agent Tool Chains for Silent Partial Success](../../verification/tool-chain-silent-failure-audit.md) — the single-agent form of the same defect, where a successful call returns an incomplete payload
