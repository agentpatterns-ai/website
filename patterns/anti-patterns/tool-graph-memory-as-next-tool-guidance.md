---
title: "Tool Graph Memory as Next-Tool Guidance"
term: "Tool Graph Memory as Next-Tool Guidance"
description: "Across nine models and two benchmarks the graph's gain was reliable in four of eighteen settings. On ToolSandbox it averaged 2.72x the baseline's LLM calls."
tags:
  - anti-pattern
  - tool-agnostic
  - memory
  - context-engineering
  - arxiv
aliases:
  - tool transition graph memory
  - next-tool suggestion memory
  - tool graph prescription
last_reviewed: 2026-10-19
maturity: emerging
status: current
---

# Tool Graph Memory as Next-Tool Guidance

> A tool transition graph can increase tool use without giving useful next-tool advice; test its suggestions separately from its keep-trying effect.

## The anti-pattern

You record which tool your agent called after which, build a weighted transition graph from the successful runs, and show the agent the likely successors each turn. H-EPM's authors report that this "consistently delivers substantial inference-time gains over strong baselines across multi-turn tool-use benchmarks, reaching up to 50%+" ([Li et al., 2026](https://arxiv.org/abs/2512.07287v3)).

A re-evaluation on nine open-weight models from 2B to 120B parameters, two multi-turn benchmarks and three runs each with paired t-tests does not reproduce that. H-EPM beats the memory-free baseline in most of the eighteen model-benchmark settings, but its gain is "reliable in only four settings". ToolNet, the other method tested, "underperforms Base in most cases, including all nine models on BFCL-v4". Averaged over the nine models, H-EPM uses 14.62 LLM calls per ToolSandbox scenario against the baseline's 5.37, a factor of 2.72, and 2.21 times the tokens ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Tables 6 and 8).

The suggestions are mostly wrong even where the graph helps. Across the 86 turns that decided the 30 scenarios H-EPM rescued on Mistral-Small-3.2-24B, its suggestion was correct at 30%. At the 43 decisive turns of the 15 scenarios it degraded, "98% of the suggestions at the decisive turns of the degraded scenarios are incorrect" ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), §3.1 and §C.1).

## Why it works

The agent is paying for extra attempts and the graph takes the credit. Split the baseline-failing scenarios into those a condition rescues and those it does not, and "the flipped scenarios show a much larger increase in tool calls over Base than those that still fail". That difference is positive in all 27 comparisons, with 95% bootstrap intervals excluding zero and each comparison still significant after Holm correction. The authors qualify the grouping themselves: it "does not make them comparable in other respects, such as task difficulty" ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), §C.3).

The control that needs no grouping is the decisive one. Delete the suggestions, or swap in randomly chosen tools, and "random or no guidance retains most of the gain". Add instead a single system-prompt instruction. It opens "IMPORTANT: Do not give a final answer or give up until you have tried the available tools." and ends "Keep calling tools until the task is fully resolved." At roughly baseline call cost, it "outperforms H-EPM on two of the three models" ablated ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Tables 2, 9 and 10).

Perfect suggestions still leave other failures. Under an oracle that always names the correct next tool, tool-selection "errors almost disappear (4% of failures), while the other three modes account for the rest": whether to call a tool at all, when to call it, and with what arguments. A transition cannot answer those, because "tool transitions alone do not tell agents whether, when, or with what arguments to call tools" ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1)).

## Example

Three arms separate the structure from the extra calls. Run them before you build a graph, and again before you keep one.

| Arm | What it isolates |
|---|---|
| Graph, suggestions removed from the prompt | whether the suggestion carries the gain |
| Graph, random successors substituted | whether the suggestion's content matters |
| No graph, one keep-trying instruction | whether extra tool calls explain the effect |

If arm two matches the graph, the suggested tool identities are not necessary for that result. If arm three matches it, a keep-trying instruction buys the same result without the graph. The re-evaluation's own replacement stores the same episodic experience as clustered natural-language insights: its "gains over Base are significant in far more settings than those of either tool graph memory", and it "keeps LLM calls close to Base and uses fewer tokens than H-EPM across models" ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1)).

## When this backfires

- Large tool libraries. ToolNet exists to scale "the number of tools to thousands with a moderate increase in token consumption" ([Liu et al., 2024](https://arxiv.org/abs/2403.00839v1)), and pruning the candidate list is its point. Neither benchmark stresses that: ToolSandbox has 34 tools over 11 domains and the BFCL-v4 multi-turn subset has eight APIs ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Appendix A.1). ToolNet was the cheaper method there: it "uses fewer tokens than Base, as it presents only a subset of tools to the agent, but is not notably better in any setting" ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1)).
- Models where no memory moves the number. On ToolSandbox, GPT-4.1 scores 0.724 with no memory, 0.725 with H-EPM and 0.729 with insights; GPT-5.1 scores 0.701, 0.702 and 0.702 ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Table 5).
- The replacement regresses specific models. Insight memory cost Ministral-3-8B 0.092 on ToolSandbox at p<0.001 while the graph gained that model 0.041 at p=0.024 ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Table 6). Measure on your own model first.
- Richer graphs are untested, and stacking is worse than either. The authors scope their result to tool-node, transition-edge graphs: "graph memories whose nodes and edges also represent states, arguments, or other entities go beyond what we target here". Insights alongside the graph "performs worse than insight memory alone on seven of the nine models" at 2.68 times baseline LLM calls ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1)).
- One inference strategy. Memory results are confounded by the method around them, because "the same memory method produces statistically distinct results under different inference strategies on the same examples" ([Li and Tao, 2026](https://arxiv.org/abs/2605.28224v1)). Treat the numbers as evidence about this setup rather than a general verdict.

## Key Takeaways

- Ask what a gain is attributable to before asking whether there is one. On Mistral-Small-3.2-24B, correct suggestions covered 30% of the decisive turns in the scenarios H-EPM rescued ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1)).
- The no-suggestion and random-suggestion arms cost one run each. Skipping them is how a structure keeps credit for 2.72x the LLM calls on ToolSandbox.
- In the three-model ablation, a keep-trying instruction outperformed H-EPM on two models at roughly baseline call cost ([Hwang et al., 2026](https://arxiv.org/abs/2610.21571v1), Tables 2 and 9).
- Residual failures are about whether, when and with what arguments to call a tool. Store situation-level guidance, not transitions.
- Scope: small tool sets (34 tools in ToolSandbox, eight APIs in BFCL-v4 multi-turn), inference-time memory, tool-node graphs. Large libraries and richer graph schemas are open.

## Related

- [Belief Inertia After Tool-Map Drift](belief-inertia-after-tool-map-drift.md) — the live-surface counterpart: stored tool knowledge the agent holds but does not act on.
- [Memory-Induced Tool-Drift](memory-induced-tool-drift.md) — what stored memory does to tool arguments rather than to tool choice.
- [CoALA Memory Taxonomy as a Classifier for Harness Artifacts](../agent-design/coala-memory-taxonomy-classifier.md) — the taxonomy this page supplies an evidence-backed preference within.
- [When a Skill Graph Cannot Beat the Ranker (Pre-Filter Topology Bound)](../../context-engineering/skill-graph-topology-bound.md) — the same shape in retrieval: a graph that relabels what was already found.
- [Self-Healing Tool Routing](../../tool-engineering/self-healing-tool-routing.md) — a cost-weighted tool graph used as a deterministic router rather than as experience memory.
