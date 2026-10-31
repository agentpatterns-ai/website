---
title: "Decision Unbundling: What Moves Into the Orchestrator"
term: "Decision Unbundling"
description: "Moving a routing or classification call onto a decision model shrinks the model call and grows the harness, which owns the candidate list, the threshold number, and the durability even when a gateway carries the escalation route."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - model-routing
aliases:
  - unbundled decision model orchestration
  - decision model harness load
  - cheap-by-default escalation routing
last_reviewed: 2026-10-25
maturity: emerging
---

# Decision Unbundling: What Moves Into the Orchestrator

> Moving a decision onto a decision model hands the orchestrator the candidate list, the threshold number, and the durability the model drops.

A decision model answers one bounded question and returns a typed value with a probability. It does not hold the conversation, pick what to ask next, or survive a crash. Those jobs land in your code the moment the decision leaves the driver model. LangChain quotes TypeSafe AI for the split: "code owns the workflow and AI handles narrow, structured decisions" ([Runkle and Lovell, LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)). OpenAI announced general availability of its Decisions API on 22 October 2026, another instance of this bounded-question shape ([OpenAI, Decisions API](https://openai.com/index/decisions-api)).

## Conditions before the swap pays

- Decision volume is high enough for a per-step saving to show up in the run.
- The question fits the model's cardinality limit. TypeSafe's `Choice` type "selects one option from a defined set (of max 255)" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)), so an open action space has to become a list first.
- You can measure what share of calls escalate. That share, not the decision model's speed, sets the saving.

## What the orchestrator takes on

The orchestrator owns candidate assembly, the threshold comparison, routing and recovery. A gateway can now take the comparison and the escalation route. LangChain describes the knowledge split: "Instead of packing domain knowledge into prompts, you encode it in the topology of the graph: which decisions get made, in what order, and what state each one sees" ([Runkle and Lovell, LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).

Vercel AI Gateway reads a confidence condition from `providerOptions.gateway.models` and escalates on it: "AI Gateway can now escalate a decision request to a fallback model when the primary model's answer trips a confidence condition you set." Confidence conditions cover two of the three question types, because "Confidence conditions cover Choice and Score questions. Boolean questions escalate on a probability range instead." Vercel also names the cost: "Because a triggered fallback runs a second decision, it bills both stages." The changelog gives no calibration data, so you still pick the threshold number, and the resume path stays yours ([Vercel, 6 October 2026](https://vercel.com/changelog/confidence-based-decision-fallbacks)).

LangChain states: "None of this is specific to LLMs. Jev still takes in unstructured text context and returns a judgment, so it needs the same guarantees, and a graph gives them to every node automatically." It claims Jev returns stable answers, based on one early experiment where scores "barely moved across 100 repeated runs" ([LangChain](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).

Both multiples are vendor-reported. LangChain measured its own graph: "Jev was 5–6x faster on the classification step across trials" against Sonnet in the judge role. The relayed multiple is TypeSafe's own benchmark, and the source states its baseline and its task scope: "On narrow decision tasks, like the routing and classification steps many agents are built around, TypeSafe's benchmarks show Jev running up to 200x faster and 400x cheaper than leading LLMs" ([LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)). Neither figure covers a whole request.

## Why it works

A cascade pays for every stage it executes. Bouchard's current formulation sums each stage's cost through the stopping index ([Bouchard, arXiv:2605.06350v2, §3.1](https://arxiv.org/abs/2605.06350v2)). Applied to a two-stage decision workflow, this means the first call is always paid and the fallback adds another cost. A step-level speedup therefore does not establish whole-workflow savings.

## When this backfires

- Generation and open-ended reasoning dominate the run. LangChain caps the claim itself: "Jev doesn't fully replace an LLM for most use cases. It handles the bounded choices it's confident about and hands everything else to an LLM" ([LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).
- You have no runtime supplying durability, interrupts and traces to every node. Building one is the project; the cheapened decision is a line of it.
- Nobody owns the escalation share as a metric. Without it you cannot tell a saving from a redistribution.

## Example

Browserbase rebuilt Stagehand's `act()` around this split, and its five-step flow shows where the work landed. The decision model answers two of the steps. It "classifies the instruction into an action (like click, fill, or scroll)", then picks which candidate is best and whether any candidate matches at all, "with an acceptance threshold of 0.7". Stagehand does the other three: it "parses arguments and builds candidate list for that action", executes an accepted action, and otherwise "falls back to an LLM" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)). Before the flow starts, Browserbase also marks nodes in the accessibility tree as interactable or not.

Three of the five steps are orchestration code. Browserbase's own number covers the `act()` step, compares against the LLM call it replaced, and carries its own hedge: "In early testing, Act median latency drops from 1.97 seconds to 0.46 seconds which is about 4.3× faster (or 77% less time)." Browserbase also caps the wider claim: "With computer use, Jev is a piece of the pie but not a standalone solution" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)).

## Key Takeaways

- Unbundling a decision moves reliability work into the orchestrator rather than deleting it. Your code gains the candidate list, the threshold number and the resume path, plus the comparison and the escalation route unless a gateway supplies them.
- Published speedups for this shape are step-scoped and vendor-reported: 5–6x on one classification step, and a median `act()` latency of 1.97 seconds falling to 0.46 seconds in early testing.
- Cost follows the escalation share, because the system pays the cheap stage on every call and the expensive one only on the fraction that escalates.
- A decision node still takes unstructured context and returns a judgment, so checkpointing, interrupts and traces have to cover it as they cover the model node, even though the vendor claims it returns stable answers.

## Related

- [Calibrated Deciders for In-Loop Agent Decisions](calibrated-deciders-in-loop-decisions.md) — whether the decision may move at all, and how to derive the threshold this page assumes you already have.
- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the two-model price-gap arithmetic behind the escalation share.
- [Deterministic Orchestration for Structured Modernization](deterministic-orchestration-structured-modernization.md) — the wider case for keeping control flow in code when a workflow has a stable shape.
- [Bounded Agent Steps Inside a Deterministic Workflow](bounded-agent-step.md) — fencing the model step the escalation path still routes to.
- [Browser as Agent Action Space](browser-as-agent-action-space.md) — the action-space framing the Stagehand example rebuilds around.
