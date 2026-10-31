---
title: "Tool Discovery Architecture: Retrieve-Then-Plan or Plan-Then-Retrieve"
term: "Tool Discovery Architecture Selection"
description: "Retrieve-then-plan wins when a request names its tool. Writing tool stubs first wins multi-tool pass rate with one planner, once raising k is ruled out."
aliases:
  - plan-then-retrieve tool discovery
  - retrieve-then-plan
  - abstract tool stubs
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-17
maturity: emerging
---

# Tool Discovery Architecture: Retrieve-Then-Plan or Plan-Then-Retrieve

> Retrieve-then-plan wins when the query names its tool. Plan-then-retrieve wins multi-tool pass rate with one planner, once raising k is ruled out.

Two conditions decide whether a tool-discovery pipeline earns a planning call before retrieval. First, your retrieval budget k has to be pinned by something other than habit. Second, the metric you are trying to move has to be pass rate rather than recall. A 46,984-API comparison of both paradigms supplies the numbers for both conditions ([Zhang et al., arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).

Retrieve-then-plan (RtP) embeds the user's request and hands the top-k nearest tool documents to the planner. Plan-then-retrieve (PtR) asks the model to invent function signatures first, called Abstract Tool Stubs, embeds each stub, and retrieves against those instead.

## Raise k before you add a discovery call

PtR generates 2.1 to 2.5 stubs per query, each retrieving its own top-k. At a nominal k of 5 that examines 10 to 13 candidates where RtP examines 5. The study reports the same ratio: at equal nominal k, PtR explores two to two and a half times RtP's candidate width (Table 5, [arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).

Match the candidate budget and the recall half of the result goes away. The paper's own budget-equivalent column puts RtP at k=10 against PtR at k=5. Both columns below read off the same k-sweep table, so the comparison is internal to one measurement:

| Query group | PtR recall at k=5 | RtP recall at k=10 | Recall delta |
|---|---|---|---|
| G1, single-tool (n=200) | 0.279 | 0.453 | +0.174 to RtP |
| G2, intra-category multi-tool (n=200) | 0.184 | 0.186 | +0.002, a tie |
| G3, cross-category multi-tool (n=100) | 0.177 | 0.217 | +0.040 to RtP |

Raising k spends context tokens on five more tool definitions. The paper notes that RtP at k=10 passes ten APIs to the planner, which halves its precision relative to PtR's k=5 output. A discovery call spends 75% to 104% more tokens plus one serial LLM round-trip before retrieval starts (Table 8, [arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)). First ask whether your context window has room for ten definitions.

## Pass rate measures tool selection, not task success

The main experiment reports a PtR pass-rate advantage: 0.855 against 0.747 on G2 and 0.820 against 0.732 on G3, both p<0.001 ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)). Three facts weaken that result. The authors rank the metric below the others. The definition does not require the selected API to be correct. And the lead holds for one planner. With gpt-oss-120b, G2 is a statistical tie (RtP 0.826, PtR 0.820) and PtR's G3 lead (0.805 against 0.790) is not significant.

On the first point, pass rate "is reported here as a supplementary indicator; the main text focuses on precision and recall as the primary retrieval metrics". On the second, the paper defines pass rate as the "fraction of queries where the planner's intended plan selects at least one API". That definition does not require the selected API to be correct. I read it as counting a wrong tool as a pass, which is my inference and not a statement in the paper. When retrieval misses everything, both architectures call a wrong tool about 70% of the time. RtP's planner refuses more often on G2, 47% against 27%, "likely because RtP's misses are obviously unrelated while PtR's stubs retrieve plausible-looking but functionally wrong tools". The paper does not tie refusals to pass rate. I read part of PtR's lead as a planner that stopped refusing, because on that reading a wrong tool still passes.

## Why it works

The mechanism the authors name is Intent-Registry Coupling, the gap between how people phrase requests and how APIs are documented. Where coupling is high, "the raw query often contains the API's name or brand directly, giving RtP a direct embedding match while a planning step only abstracts away this signal" ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)). Four of the paper's worked examples go from RtP recall 1.00 to PtR recall 0.00 on exactly that. In one, a request for "programming memes from Reddit" produces the stub `reddit_api_client`, which misses the gold Programming Memes endpoint that the raw query matched.

Where coupling is low, one query embedding cannot represent several functional sub-needs at once, and each stub anchors to a different one. PtR works through coverage. Only 40.6% of G1 stubs and 24.8% of G3 stubs match a relevant API at all. Multi-stub coverage compensates because finding the right tool for one sub-need does not require every stub to land.

Either way the retrieval step, not the planner, sets the ceiling. Trajectory fidelity is at least 96% on all three subsets, so "the planner almost always selects from the retrieved set, confirming retrieval is the binding constraint on what the agent can do".

## Routing on a signal you already have

Running both architectures needs a per-query router, and the cheapest candidate signal is one your pipeline already computes. "RtP's own top-1 cosine similarity is a zero-cost routing signal already produced by the pipeline": a high score means the request named a tool and can stay on RtP, a low or diffuse one means abstract multi-step intent. The paper also lists four proxies computable before any LLM call, namely query length, clause count, named-entity density, and the presence of conjunctive sub-goals. The paper projects that routing single-tool traffic to RtP and multi-tool traffic to PtR saves about 16% of total inference tokens, or 36% of PtR's discovery overhead ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).

Treat that as a design sketch. The authors state plainly: "We leave empirical validation of such classifiers to future work". The paper computes the 16% figure by routing whole subsets: G1 to RtP, G2 and G3 to PtR. It assumes each query's group is known, so no classifier has delivered that saving.

## Example

Two queries from the paper's Table 2 show the split a router has to find ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).

| Query | PtR stubs | RtP recall | PtR recall |
|---|---|---|---|
| "programming memes from Reddit" | `reddit_api_client` | 1.00 | 0.00 |
| "London trip: hotels + IP + currency" | `hotel_search`, `ip_forensics`, `currency` | 0.00 | 0.50 |

These examples show opposite retrieval outcomes. The paper does not report their top-1 cosine scores or validate a routing threshold. Its proposed router still needs evaluation on labeled queries.

## When this backfires

- Your context budget can absorb a larger k, which reaches the same candidate width for no LLM call at all.
- Requests name their tool or brand. Stubs abstract away the one signal that was already working, and on G1, single-tool recall is 0.372 for RtP against 0.289 for PtR ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).
- Latency sits on the critical path. Because "discovery and retrieval are sequential, PtR adds one full LLM round-trip of latency before retrieval and planning begin". The study measured tokens, not wall clock.
- You planned to filter weak stubs by similarity. You cannot. Correct and incorrect stub matches score 0.874 against 0.872 on G1, so "the embedding space provides no signal to distinguish good routing from bad".
- Your registry is internal. The study ran on ToolBench only, and one of its own win categories is "RtP wins when queries contain niche brand references". The authors flag the gap: "generalization to other registry types (e.g., enterprise-internal APIs with different naming conventions) remains to be validated".
- Your planner is not Gemini. On a gpt-oss-120b replication the pass-rate lead disappears. G2 is a statistical tie (RtP 0.826, PtR 0.820) and PtR's G3 lead is not significant (0.805 against 0.790). The G3 recall gap reverses toward RtP, 0.160 against 0.146±0.008, p=0.035 ([arXiv:2610.19068v1](https://arxiv.org/abs/2610.19068v1)).
- The benchmark scores recall against a single gold tool set. A separate study found that tool-retrieval benchmarks "annotate each query with a single relevant tool combination, collapsing this one-to-many mapping into a rigid one-to-one annotation and causing valid retrieved tools to be misjudged as failures". It reports that 67.9% of sub-queries on the 7,360-query Tool-DE benchmark admit equivalent alternatives ([Zhu et al., arXiv:2609.08327v1](https://arxiv.org/abs/2609.08327v1)). Tool-DE is a separate benchmark from the ToolBench subsets above, and that study does not examine PtR. I read the two together as a warning. An architecture whose stubs retrieve plausible non-gold tools is the one a single-gold metric punishes hardest.
- The problem may be your index rather than your architecture. Document expansion changes the index, not the query path. One benchmark effort reports that it "substantially improves retrieval performance" and argues that "progress in tool retrieval remains hindered by incomplete and heterogeneous tool documentation" ([Lu et al., arXiv:2510.22670v1](https://arxiv.org/abs/2510.22670v1)).

## Key Takeaways

- Ask what your k is pinned by before asking which architecture to build. At matched candidate budget RtP ties PtR on intra-category multi-tool recall and beats it on the other two groups. This is the matched-budget question that any added retrieval stage owes an answer to, not a fact about stubs.
- Check whether the planner names a correct tool before treating its pass-rate gain as useful. The paper's definition does not require a correct API, so I read the metric as accepting wrong tools.
- On that reading, a higher pass rate can mean a planner that stopped refusing. That is the worse failure if nothing downstream checks the tool it picked.
- Do not filter stubs by cosine score alone: the paper reports almost identical scores for correct and incorrect matches.
- Expand thin tool documentation before changing architecture. The change lands on the index, not on every query.

## Related

- [Chance-Corrected Shortlist Depth Sizing](../../tool-engineering/chance-corrected-shortlist-depth-sizing.md) — how to size the k this page tells you to raise, with a chance-corrected metric instead of a fixed default.
- [Hypothetical Classification for Large Label Vocabularies](../../context-engineering/hypothetical-classification.md) — the same invent-then-resolve mechanism applied to a label taxonomy, with the same instruction to beat a plain retrieval baseline first.
- [Lexical-First Retrieval for Agentic Search](../../tool-engineering/lexical-first-retrieval-for-agentic-search.md) — the scorer choice underneath either architecture, and when BM25 is enough.
- [Natural Language Tool Selection (NLT)](natural-language-tool-selection.md) — what to do once candidate tools are in context, which is the step after discovery.
- [Retrieval Tools That Refuse](retrieval-tool-refusal.md) — making a retrieval miss visible, which is the control the refusal-rate finding above argues for.
