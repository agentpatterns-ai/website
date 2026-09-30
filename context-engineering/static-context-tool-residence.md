---
title: "Static-Context Tool Residence: Two Overrides on Hit Rate"
term: "Static-Context Tool Residence"
description: "Hit rate decides which tool definitions stay resident every turn, except for a tool the model calls when it is absent and a tool a product flow depends on."
aliases:
  - static context tool residence
  - non-deferred tool selection
  - which tools to keep resident
tags:
  - context-engineering
  - cost-performance
  - cursor
last_reviewed: 2026-09-27
maturity: emerging
---

# Static-Context Tool Residence: Two Overrides on Hit Rate

> Hit rate decides which tool definitions stay resident, except for a tool the model calls when absent and a tool a product flow depends on.

Static-context tool residence is the choice of which tool definitions load into every request up front. The rest load only when the agent searches for them. Published guidance settles it on frequency alone: "Keep your 3–5 most frequently used tools non-deferred so Claude can call them without searching first" ([Anthropic, tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Cursor made the same decision against production traffic and kept tools that frequency would have deferred ([Cursor, 2026-09-23](https://cursor.com/blog/improved-token-efficiency)).

## Check these conditions first

An override to the frequency rule pays under three conditions. Miss one and deferring the tool is the better call.

- The static set has room. Selection accuracy falls as the resident set grows: "Claude's ability to pick the right tool degrades once you exceed 30–50 available tools" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Each override spends part of the budget that deferral was protecting, so an exception list has a short ceiling.
- The model reaches for the tool often. Weigh the recovery turns an override prevents, summed across conversations, against carrying that definition in every request. Rare reaches lose that comparison.
- You can measure the quality side. Cursor "A/B tested several configurations based on how often each tool was used and whether models needed to see it from the start", tracking "token usage, cost, latency, tool-call errors, and overall agent usage" ([Cursor](https://cursor.com/blog/improved-token-efficiency)). Offline evals are a fast proxy that "often represent" hard problems, and they "don't properly reflect the true distribution of user requests". Cursor reports the whole programme moved user token cost 7% "without reducing agent quality". Confirming an effect that small takes volume. Without it you copy a verdict instead of reproducing one. That is the [amortization floor Copilot's levers hit](../token-engineering/copilot-cost-levers-fixed-quality.md).

## What frequency alone would defer

Nearly everything. Cursor reports that of the built-in tools in its agent, "Most of these tools are important, but each is needed in fewer than 20% of conversations" ([Cursor](https://cursor.com/blog/improved-token-efficiency)). Acting on that: moving MCP tools into dynamic context "reduced total tokens by 46.9% across sessions that called an MCP tool", and offloading built-in tools "cut static-context description tokens by 60%" ([Cursor](https://cursor.com/blog/improved-token-efficiency)).

The keep-list that survived the A/B tests has members selected on frequency and members selected on two other signals:

> Ultimately, we kept the high-frequency tools for reading, searching, editing, and using the shell in static context. We also retained `ask_question`, which some models tended to hallucinate calls for, and tools that are crucial to specific product flows, such as `create_plan` in Plan Mode. ([Cursor](https://cursor.com/blog/improved-token-efficiency))

Two signals therefore sit outside hit rate. A tool the model invents calls to stays resident because the invented call is the cost. A tool that a product flow depends on stays resident because the flow breaks without it. Cursor names `create_plan` in Plan Mode as its example.

## Why it works

A model's prior over tool names comes from pretraining, not from the schema in front of it. A name it expects gets called whether the current request declares it or not. The PA-Tool authors name the failure and locate its cause: "models hallucinate plausible tool names that are absent from the provided tool schema, due to different naming conventions internalized during pretraining" ([Lee et al., arXiv:2510.07248v3](https://arxiv.org/abs/2510.07248v3)). Renaming schema components toward pretraining-familiar forms cut those errors by 80% on MetaTool and RoTBench, measured on small language models.

Deferring such a tool removes the definition. The impulse survives, so a real call becomes a fabricated one. Two properties make this a residence question rather than a model-quality one. Scale does not fix it: across ten hosted models, "model scale does not help (a 675B model matches a 7-8B one)" ([arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). Nor does a permission layer, because "a hallucinated call is by construction not a decision any gate made, so no gate can reject it" ([arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). Keeping the definition visible acts before the failure exists.

## When this backfires

- The exception list grows. A short override list beside the high-frequency tools is affordable. A dozen rebuilds the problem deferral solved.
- The tool is rarely reached for. Resolve the bad call at the boundary instead. A closed-world resolver needs only "registry membership plus a signature check", and registry membership catches a call to a tool that does not exist ([arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)). It is not complete: the same authors "characterize the one irreducible residue (borrowed arguments schema-indistinguishable from a valid call)". It also rejects the call without supplying the capability. The agent still has to recover or go without, and that trade is fair only on a rare turn.
- You copy the list instead of measuring it. Cursor's retention of `ask_question` is keyed to "some models". The same post reports a different set of instructions removed once "models learned this pattern natively". An override that earned its place on one model generation becomes dead weight on the next.
- The flow-critical tool is resident in every mode. Cursor retained `create_plan` in static context, and the post does not say it is scoped to Plan Mode.
- Prefix caching constrains the mechanics. A deferred tool cannot carry its own cache breakpoint: "A tool with `defer_loading: true` can't also carry `cache_control`: the API returns a 400" ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).

## Key Takeaways

- Frequency is the published rule for static residence and it is incomplete: Cursor's production keep-list holds tools that hit rate would have deferred ([Cursor](https://cursor.com/blog/improved-token-efficiency)).
- Add a hallucination signal to the rubric. A tool the model calls when absent costs more deferred than resident, because pretraining supplies the name the schema no longer does ([arXiv:2510.07248v3](https://arxiv.org/abs/2510.07248v3)).
- Add a product-flow signal. Cursor retained `create_plan` in static context because Plan Mode depends on it.
- Bound the exception list by the selection budget. Past 30 to 50 resident tools, accuracy degrades and the overrides cost more than they save ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)).
- Below the rate where recovery turns outweigh a definition, drop the override and resolve the bad call at the boundary instead ([arXiv:2609.19425v1](https://arxiv.org/abs/2609.19425v1)).

## Related

- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md) — the four-signal residence rubric this page adds two signals to
- [Mask Tools Instead of Removing Them](mask-tools-instead-of-removing.md) — the other half of the tool-context decision: what varying the declared set costs the cache
- [Reducing System-Prompt Token Bloat in Coding Agents](system-prompt-bloat-reduction.md) — trimming the same static payload from the user's side rather than the harness author's
- [GitHub's Copilot Cost Levers at Constant Task Quality](../token-engineering/copilot-cost-levers-fixed-quality.md) — the sibling vendor account, and the traffic-volume condition that gates copying any of these levers
- [Choosing a Skill Loading Method for Agents](skill-loading-method-selection.md) — the same preload-or-fetch decision applied to skills instead of tool definitions
