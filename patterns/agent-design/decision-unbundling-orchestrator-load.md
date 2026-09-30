---
title: "Decision Unbundling: What Moves Into the Orchestrator"
term: "Decision Unbundling"
description: "Moving a routing or classification call onto a decision model shrinks the model call and grows the harness, which now owns the candidate list, the threshold, the escalation route, and the durability."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - unbundled decision model orchestration
  - decision model harness load
  - cheap-by-default escalation routing
last_reviewed: 2026-09-29
maturity: emerging
---

# Decision Unbundling: What Moves Into the Orchestrator

> Moving a decision onto a decision model hands the orchestrator the candidate list, the threshold, the escalation route, and the durability the model drops.

A decision model answers one bounded question and returns a typed value with a probability. It does not hold the conversation, pick what to ask next, or survive a crash. Those jobs land in your code the moment the decision leaves the driver model. LangChain quotes TypeSafe AI for the split: "code owns the workflow and AI handles narrow, structured decisions" ([Runkle and Lovell, LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).

## Conditions before the swap pays

All three have to hold. The third has no vendor number behind it.

- Decision volume is high enough for a per-step saving to show up in the run.
- The question fits the model's cardinality limit. TypeSafe's `Choice` type "selects one option from a defined set (of max 255)" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)), so an open action space has to become a list first.
- You can measure what share of calls escalate. That share, not the decision model's speed, sets the saving.

## What the orchestrator takes on

The decision model answers. Your code assembles the options, applies the cutoff, routes each outcome to its own downstream, and keeps a resumed run from repeating work. LangChain reports the same relocation on the knowledge side: "Instead of packing domain knowledge into prompts, you encode it in the topology of the graph: which decisions get made, in what order, and what state each one sees" ([Runkle and Lovell, LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).

Runtime guarantees do not relax. LangChain is direct: "None of this is specific to LLMs. Jev still takes in unstructured text context and returns a judgment, so it needs the same guarantees, and a graph gives them to every node automatically." The post argues durability for model-driven steps in general: "Restarting from scratch after a failure is worse than slow, since the rerun might not retrace the same path". It also claims the decision model itself is stable: "Jev is designed to return the same answer for the same input." Its evidence is one early experiment in which Jev's scores "barely moved across 100 repeated runs" ([LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).

Treat both published multiples as vendor-reported. LangChain measured its own graph: "Jev was 5–6x faster on the classification step across trials" against Sonnet in the judge role. The relayed multiple is TypeSafe's own benchmark, and the source states its baseline and its task scope: "On narrow decision tasks, like the routing and classification steps many agents are built around, TypeSafe's benchmarks show Jev running up to 200x faster and 400x cheaper than leading LLMs" ([LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)). Neither figure covers a whole request.

## Why it works

A cheap-first system pays its cheap stage on every call, before anything has been decided. Bouchard's decision-theoretic study of cascades ends there: "These results suggest that cascade performance is limited primarily by structural cost, since cascades pay the cheap model before any escalation decision, rather than by a shortage of intermediate stages" ([Bouchard, arXiv:2605.06350v1](https://arxiv.org/abs/2605.06350v1)). That study's cheap stage generates text, so a decision model pays a smaller version of the same cost rather than none of it. You pay the expensive stage only on the fraction that escalates. That fraction governs the total, and a step multiple does not compose into a system multiple.

Reliability has a different cause. LangChain rests it on the input and output shape, not on run-to-run variance: the decision model "still takes in unstructured text context and returns a judgment, so it needs the same guarantees". That means durable execution, interrupts and traces. Supplying them to a second node type is orchestration work the swap creates rather than removes.

## When this backfires

- A cheap feature already predicts difficulty before any model runs. Dispatching up front then beats paying the cheap stage first: "A lightweight pre-generation router exceeds the best cascade policy on four of five datasets, mainly because it avoids the cheap model's generation cost on queries sent directly to a larger model rather than because of a stronger routing signal" ([Bouchard, arXiv:2605.06350v1](https://arxiv.org/abs/2605.06350v1)). Bouchard measured that margin against a generating cheap stage, so expect a narrower one with a decision model. Where such features are uninformative, the same paper finds "confidence-based cascading remains competitive".
- Generation and open-ended reasoning dominate the run. LangChain caps the claim itself: "Jev doesn't fully replace an LLM for most use cases. It handles the bounded choices it's confident about and hands everything else to an LLM" ([LangChain, 25 September 2026](https://www.langchain.com/blog/building-prod-with-jev-and-langgraph)).
- You have no runtime supplying durability, interrupts and traces to every node. Building one is the project; the cheapened decision is a line of it.
- Nobody owns the escalation share as a metric. Without it you cannot tell a saving from a redistribution.

The honest alternative is to leave the decision with the driver model, which already holds the conversation, the prior tool results and the reasoning behind the proposed action. You keep one vendor, one trace surface, and no threshold to recalibrate.

## Example

Browserbase rebuilt Stagehand's `act()` around this split, and its five-step flow shows where the work landed. The decision model answers two of the steps. It "classifies the instruction into an action (like click, fill, or scroll)", then picks which candidate is best and whether any candidate matches at all, "with an acceptance threshold of 0.7". Stagehand does the other three: it "parses arguments and builds candidate list for that action", executes an accepted action, and otherwise "falls back to an LLM" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)). Before the flow starts, Browserbase also marks nodes in the accessibility tree as interactable or not.

Three of the five steps are orchestration code. Browserbase's own number covers the `act()` step, compares against the LLM call it replaced, and carries its own hedge: "In early testing, Act median latency drops from 1.97 seconds to 0.46 seconds which is about 4.3× faster (or 77% less time)." Browserbase also caps the wider claim: "With computer use, Jev is a piece of the pie but not a standalone solution" ([Browserbase, What is Jev](https://www.browserbase.com/blog/what-is-jev)).

## Key Takeaways

- Unbundling a decision moves reliability work into the orchestrator rather than deleting it. Your code gains the candidate list, the cutoff, the routing and the resume path.
- Published speedups for this shape are step-scoped and vendor-reported: 5–6x on one classification step, and a median `act()` latency of 1.97 seconds falling to 0.46 seconds in early testing.
- Cost follows the escalation share, because the system pays the cheap stage on every call and the expensive one only on the fraction that escalates.
- When a cheap pre-decision feature predicts difficulty, routing before the cheap stage beat the cascade shape on four of five datasets in Bouchard's evaluation.
- A decision node still takes unstructured context and returns a judgment, so checkpointing, interrupts and traces have to cover it as they cover the model node, even though the vendor claims it returns stable answers.

## Related

- [Calibrated Deciders for In-Loop Agent Decisions](calibrated-deciders-in-loop-decisions.md) — whether the decision may move at all, and how to derive the threshold this page assumes you already have.
- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the two-model price-gap arithmetic behind the escalation share.
- [Deterministic Orchestration for Structured Modernization](deterministic-orchestration-structured-modernization.md) — the wider case for keeping control flow in code when a workflow has a stable shape.
- [Bounded Agent Steps Inside a Deterministic Workflow](bounded-agent-step.md) — fencing the model step the escalation path still routes to.
- [Browser as Agent Action Space](browser-as-agent-action-space.md) — the action-space framing the Stagehand example rebuilds around.
