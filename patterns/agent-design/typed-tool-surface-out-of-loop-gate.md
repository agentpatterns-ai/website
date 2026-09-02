---
title: "Typed Tool Surfaces and Out-of-Loop Correctness Gates"
term: "Typed Tool Surface"
description: "A typed tool surface with code-enforced bounds and a downstream gate. Against a fixed retrieval pipeline it won multi-hop by 9 points, lost single-hop by 25."
tags:
  - agent-design
  - tool-agnostic
  - cost-performance
aliases:
  - typed tools for agents
  - semantic tool contract
  - out-of-loop correctness gate
last_reviewed: 2026-08-28
maturity: emerging
---

# Typed Tool Surfaces and Out-of-Loop Correctness Gates

> A typed tool surface names the domain's operations as tools, and a gate outside the loop checks what the agent hands back.

A typed tool surface replaces one general search tool with a few tools that name what the knowledge layer means: evidence, entity identity, typed relationships, time, change, and disagreement. Miodrag Cekikj built eight such tools and measured them against a fixed retrieval pipeline on the same 15 questions ([Towards Data Science, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)). The result splits by question shape.

## Adopt it only when questions need more than one hop

On gpt-5-mini the fixed pipeline scored 0.95 on single-hop questions and the full-tool agent scored 0.70. On multi-hop questions the order reverses: 0.83 for the pipeline, 0.92 for the agent, at roughly 11,400 tokens and 29 seconds per question against the pipeline's 31 seconds ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)). Nine points of multi-hop accuracy cost 25 points of single-hop accuracy. So Cekikj routes rather than picks: the pipeline answers by default, and the agent is an escalation path triggered by sequential dependency, an insufficient-evidence flag, a contradiction, or a temporal comparison.

What makes the routing safe is the asymmetry of its errors, not the accuracy of the classifier. "Misroute to the fixed lane and the failure is visible (an insufficient or contested answer that can escalate); misroute to the agent and the failure is a few cents" ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).

## Where each part lives

| Part | Where it lives | What it does |
|------|----------------|--------------|
| Typed tools | The model's tool list | Resolve an entity, traverse typed relations, read a timeline, diff a date window, query the contradiction register |
| Hard bounds | Loop code | Caps tool-call rounds at 8, plus a token budget and a wall-clock timeout; a tripped bound composes from the trace so far, and the answer says so |
| Correctness gate | A composer downstream of the loop | Drops claims it cannot map to a citation or a walked path, re-runs contradiction lookups on touched entities, forwards insufficient flags |

The gate repeats the lookups instead of reading the agent's. Cekikj's reason: "governance that lives inside the loop is advisory; governance that survives agency must live outside it" ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).

## Why it works

The tool list is the model's action vocabulary, so it bounds the plan space before any prompt is written. An operation the surface does not name is a step the model cannot take, and one it does name collapses a sequence of guesses into a single call. Cekikj frames it as iteration against navigation: a search box plus a retry budget buys "rephrased guesses," while typed traversal, timelines, diffs and a contradiction register make iteration "something closer to navigation" ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).

Naming matters as much as semantics here. Anthropic reports "non-trivial effects on our tool-use evaluations" from the choice between prefix- and suffix-based namespacing alone, and cautions that "more tools don't always lead to better outcomes" ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)). Repantis and colleagues measured the count side with Claude Sonnet 4.6: a short adaptive shortlist raised correct tool selection to 93.1% from 87.1% for a fixed list of five, and to 76.8% from 60.9% on medium-difficulty queries ([arXiv:2605.24660v2](https://arxiv.org/abs/2605.24660v2)).

## When this backfires

- Lookup-shaped work. Where the answer sits in one document, the surface costs 25 accuracy points against a fixed pipeline and pays a token premium for the loss ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).
- A corpus with no relationships recorded. In Cekikj's worked trace the typed traversal "returned nothing" because the relation edges lived elsewhere, and the agent fell back to plain search.
- A model that cannot plan over the surface. With the identical eight tools, gpt-4o-mini scored 0.36 single-hop and 0.58 multi-hop, leaning on search iterations rather than entity resolution or traversal ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).
- The router becomes the ceiling. Across 21 routing methods and five benchmarks, Lu and colleagues find a "routing plateau" where methods converge to a narrow band "far below the oracle router" ([arXiv:2606.07587v1](https://arxiv.org/abs/2606.07587v1)).
- The gate may be insurance you never claim. Cekikj predicted the plain search-box agent would talk past the governance check; it did not. All four models presented both sides of a contested question 3 times out of 3, even with the policy off: "my prediction was wrong, in the reassuring direction". He keeps the gate regardless: it "converts *the model complied this time* into *the system enforces it every time*", and the run's one governance failure came from the fixed pipeline, not the agent ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).

The ablation's third arm shows how blunt the metric is. A search-only agent scored 1.00 on the multi-hop subset, above the eight-tool agent's 0.92 and the pipeline's 0.83 — because it "iterates the same query and dumps large spans of evidence text, which is exactly what a keyword-coverage score rewards". Cekikj reads his own number down: "B's 1.00 is the metric flattering verbosity, not the search box out-reasoning the graph." The corpus was 21 documents, and the coverage score is one Cekikj calls "deliberately blunt."

## Key Takeaways

- Decide by hop count before you design tools. One published ablation puts the crossover at the single-hop and multi-hop boundary ([Cekikj, 2026](https://towardsdatascience.com/stop-giving-your-ai-agent-a-search-box-and-start-giving-it-typed-tools-hard-bounds-and-a-gate-it-cannot-talk-past/)).
- Put the round cap, token budget, and timeout in the loop code, and make a tripped bound visible in the answer.
- Name tools after what the data means, not after retrieval mechanics, and keep the list short enough to pick from ([arXiv:2605.24660v2](https://arxiv.org/abs/2605.24660v2)).
- A downstream check that repeats the lookups itself is the kind the agent cannot argue with. Budget for the duplicated calls, and keep it even if it never fires — an unfired gate is still the difference between complied once and enforced every time.
- Escalation routing inherits the router's error, and routers plateau well below an oracle ([arXiv:2606.07587v1](https://arxiv.org/abs/2606.07587v1)).

## Related

- [Bounded Agent Steps Inside a Deterministic Workflow](bounded-agent-step.md) — the fence around one agent stage, where hard bounds come from the surrounding workflow
- [Product-Operation Tool Surfaces for In-Product Agents](product-operation-tool-surface.md) — the opposite split, many shallow tools per product action rather than a few domain operations
- [Typed Context Buys Addressability, Not Token Savings](../../context-engineering/typed-context-addressability.md) — the same typing argument applied to what enters the context rather than what the model can call
- [Decoupled Search Grounding](decoupled-search-grounding.md) — moving retrieval behind an inspectable boundary instead of into the reasoning model
