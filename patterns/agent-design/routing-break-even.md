---
title: "Routing Break-Even: When a Cheaper Model Actually Pays"
term: "Routing Break-Even"
description: "The router's own judging cost is a fixed tax, so the price gap between your two models decides whether offloading agent calls to a cheaper one can pay."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - minimum offload fraction
  - router judge cost break-even
  - model routing break-even calculation
last_reviewed: 2026-08-16
maturity: emerging
---

# Routing Break-Even: When a Cheaper Model Actually Pays

> Routing pays only when the judge's cost is small against the price gap between the two models it chooses between.

`minimum offload = judge cost / (expensive cost - cheap cost)` gives the fraction of turns you must send to the cheap model before routing costs less than sending everything to the frontier model. LangChain publishes the rule after benchmarking NVIDIA's [NeMo Switchyard](https://github.com/NVIDIA-NeMo/Switchyard) router across 145 agent tasks ([LangChain, 11 August 2026](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).

## What the calculation can decide

The formula answers one question: is the gap between your two models wide enough to pay for the judge. When two models sit close in price, the required offload climbs above 100%, which asks you to send more turns to the cheap model than you have. LangChain is explicit that no judge configuration recovers this, and that the one escape is hosting the cheap model yourself, where inference cost falls near zero and the gap reopens ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).

Three things it does not decide. It cannot tell you whether the router picks well on your traffic. It compares routing against a frontier-only baseline, so it says nothing about running the cheap model on everything. And on a lopsided pairing it settles nothing, because the bar sits far below any plausible offload rate. As the authors put it: "Use it to rule routing out on cost. Run your own workload to rule it in" ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).

## The measured trade

LangChain ran its Deep Agents suite of 145 multi-step tasks through Switchyard's escalation router, pairing Nemotron 3.5 Lightning with Claude Opus 4.8 ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)):

| Arm | Accuracy | Cost per run |
|---|---|---|
| Opus 4.8 alone | 86.0% | $11.45 |
| Routed | 80.0% | $3.00 |
| Nemotron 3.5 Lightning alone | 77.7% | $0.72 |

Routing was 74% cheaper for about six points of accuracy. Treat that delta as specific to this suite. The benchmark is vendor-adjacent and ran on controlled scenarios that left "just 8 points of variance between a 30B parameter model and a frontier model," which the authors say "gives routing less room to prove its value than a harder workload would" ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).

## Why it works

Agent turns differ wildly in difficulty but cost the same per token, so spend concentrates far harder than call count does. Nemotron handled 93% of calls for 10.4% of the bill while Opus handled 7% of calls for 68.4% of it ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)). Each turn moved off the frontier model therefore saves roughly the whole price gap, and total savings rise linearly with the offload rate.

The judge does not scale down alongside those savings. It "runs on every turn until a task escalates, whether or not anything ends up escalating," gets no benefit from prompt caching, and took 21.2% of routed spend ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)). A fixed tax set against a linear saving is what produces the break-even, and why the binding variable is the price gap rather than the cheap model's competence. It also names the cheapest lever on a routed bill: a cheaper judge model, "or one that skips turns that are clearly going fine, comes straight off your bill" ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)). Decision-theoretic work on cascades reaches the same structural conclusion, finding performance "limited primarily by structural cost, since cascades pay the cheap model before any escalation decision" ([Bouchard, arxiv 2605.06350v1](https://arxiv.org/abs/2605.06350v1)).

## When this backfires

- Two models close in price. The required offload exceeds 100% and the trade is arithmetically unavailable, short of self-hosting the cheap tier ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).
- A narrow gap in practice. Cognition routed Opus 5 against Kimi K2.7 in Devin Desktop and landed "within 2.8 percentage points of Opus 5 accuracy at approximately 28% lower mean cost" ([NVIDIA, 11 August 2026](https://developer.nvidia.com/blog/route-ai-agent-workloads-across-models-with-nvidia-nemo-switchyard/)). The saving tracks the gap.
- A workload the cheap model already handles. Routing scored 2.3 points above Nemotron alone while runs varied by 2.7 points on their own, so "we cannot say routing beat the cheap model here," and cheap-only was the cost-minimal arm ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).
- Budgeting against a mean. Frontier traffic ranged from 4.1% to 9.1% across five identical runs, moving the bill from $2.16 to $3.61 with nothing changed but router decisions ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)). Plan against the top of that range.
- A router that routes badly. Break-even is a cost screen, and cost is not the failure mode LLMRouterBench found: across 400K instances, 21 datasets and 33 models, "several recent approaches, including commercial routers, fail to reliably outperform a simple baseline" ([arxiv 2601.07206v1](https://arxiv.org/abs/2601.07206v1)).

## Example

Work the LangChain pairing through the formula. The judge model cost $0.64 per run. The price gap was $10.73, the distance between the $11.45 Opus-only arm and the $0.72 Nemotron-only arm in the table above. Dividing gives a minimum offload of 5.9%. The router actually offloaded 93% of calls, clearing the bar by about 16x. Per call the spread was starker still, $0.0324 for Opus against $0.00037 for Nemotron, roughly 87x ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)).

Clearing the bar that far tells you little. The authors concede that "with a pairing this lopsided the formula is a bit of a formality" ([LangChain](https://www.langchain.com/blog/switchyard-agent-routing-benchmark)). Reach for the calculation when the spread is narrow, when you are pricing a self-hosted cheap tier against a hosted one, or when the judge is expensive enough to be a line item of its own.

## Key Takeaways

- Compute `judge cost / (expensive cost - cheap cost)` before building a router; it gives the offload fraction routing must clear to beat a frontier-only baseline.
- The question the formula asks is about the price gap, not about whether your cheap model is good enough.
- It rules routing out and cannot rule it in. Two models close in price make the required offload impossible, and only a self-hosted cheap tier reopens the trade.
- The judge is a fixed tax that misses prompt caching, so a cheaper judge or one that skips healthy turns comes straight off the bill.
- Routing widens the range around your average spend as well as lowering it; budget against the top of the observed escalation range.
- Compare against running the cheap model alone, not only against the frontier model. On a saturated workload that arm can win outright.

## Related

- [Within-Task Model Cascade: Designing the Escalation Gate](../../loop-engineering/within-task-model-cascade.md) — the other break-even in this family, expressed as an escalation-rate ceiling rather than a judge-cost floor.
- [Trajectory-Conditioned Model Escalation (SWE-Router)](trajectory-conditioned-model-escalation.md) — how an escalation router decides mid-task, once the break-even says the trade is affordable.
- [Auto Model Selection: Harness-Driven Routing per Task](auto-model-selection.md) — what a vendor-side router keys on, and a separate cost gate stated as a pass rate against the inter-tier price ratio.
- [Gateway Model Routing](gateway-model-routing.md) — the infrastructure layer that exposes the cheap and expensive targets a router picks between.
- [Model Economics of Agent Swarms](../multi-agent/model-economics-agent-swarms.md) — the same cost-concentration arithmetic applied to a planner and worker split.
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — the broader tier-routing frame this calculation sits inside.
