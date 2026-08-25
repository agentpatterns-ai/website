---
title: "Choosing a Skill Loading Method for Agents"
term: "Skill Loading Method Selection"
description: "Pick how an agent loads a skill from two properties, the skill's size and how much of it each turn needs, and rank the options on cache-corrected input rather than raw tokens."
aliases:
  - skill block loading
  - conditional skill loading
  - skill loading method selection
tags:
  - context-engineering
  - cost-performance
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-18
maturity: emerging
---

# Choosing a Skill Loading Method for Agents

> No skill loading method wins everywhere; a skill's size and how much of it each turn needs decide the choice.

Choose a loading method from two properties of the skill: how large it is, and how much of it a typical turn needs. A controlled comparison of four content-preserving methods across five benchmarks found no universal winner. One method cut multi-turn effective input by 73.0% on the largest skill, while an aggressively nudged, ungated arm of that same method raised single-turn raw input by 48.4% on the smallest — an arm the authors call "an overhead diagnostic, not a recommended configuration" ([Nakasuji, arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

## The four methods

| Method | Always in context | Arrives later |
|---|---|---|
| Full | The entire skill, on every request | Nothing |
| Skill Block | A small core plus one `load_skill_block(name)` tool | Optional sections, verbatim, when the model calls the tool |
| Reference | A compact catalog plus the core, with no tool schema | One section, after the model spends a turn selecting it |
| Hybrid | The core plus a one-line stub for every optional block | Full block detail, only when a stub proves insufficient |

All four preserve the same content. They differ only in when each part is shown ([arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

## What the measurements show

Single-turn benchmarks are scored on raw input tokens, and multi-turn benchmarks on cache-corrected effective input, defined as new input plus a tenth of the cache reads.

| Benchmark | Skill size | Turns | Result against Full |
|---|---|---|---|
| SearchQA | ~2K | Single | Hybrid −27.4%, Reference +10.4%, Skill Block +48.4% (aggressively nudged, ungated — the authors' overhead diagnostic) |
| SpreadsheetBench | ~8K | Single | Hybrid −39.8%, Skill Block −35.6%, Reference −31.7% |
| ALFWorld | ~1K | Multi | Skill Block −12.6%, Hybrid −3.2%, Reference +24.2% |
| ScienceWorld | ~6K | Multi | Skill Block −62.5%, Hybrid −52.8% |
| SynthProc | ~10K | Multi | Skill Block −73.0%, Hybrid −66.6% |

Paired outcome tests detected no quality difference in the principal comparisons. The authors are explicit that this warrants "'no detected difference' only" — the tests "do not prove equivalence or rule out regression" ([arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

Two patterns survive the noise, and both match the paper's own regime guidance: reach for Hybrid on a single-turn skill *when all of its content must stay available*, because its stubs hold fetch rates down without paying for a catalog, and evaluate Skill Block on a large multi-turn skill whose optional mass goes unread most turns. Where reduced coverage is acceptable, try static pruning first — it is cheaper still, and on SpreadsheetBench the non-content-parity `original8` treatment cut input by 55.5% against Hybrid's 39.8% ([arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

## Why it works

Conditional loading separates coverage from per-query cost, so an optional block nobody reads costs nothing. In a multi-turn session the effect compounds, because the agent resubmits its context every turn, so the always-on footprint of core content plus fetch-tool schema is paid once per turn for the life of the session ([arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

That only nets out positive when the loading mechanism leaves the cached prefix alone. Anthropic's cache follows a `tools` → `system` → `messages` hierarchy, and modifying tool definitions invalidates all three levels ([Anthropic on tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching)). The four methods avoid that, because their fetch tool has a fixed schema and the content arrives as appended conversation. Anthropic's own deferred tool loading takes the same shape, keeping discovered definitions out of the prefix so that "prompt caching is preserved" ([Anthropic on tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Load a skill by swapping tool definitions instead and you reprocess the whole conversation to save a few hundred tokens, which is the failure documented in [Dynamic Tool Fetching Breaks KV Cache](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md).

The accounting follows from the same mechanism. Raw input counts cache reads at full weight, which flatters the preload baseline and can rank the methods wrongly.

## When this backfires

- The skill is small and needed on nearly every turn. ALFWorld's ~1K skill of short, repeatedly used procedures gave Skill Block only −12.6%, and Hybrid's confidence interval crossed zero. The paper's advice for this regime is to treat the options as near parity and avoid a heavy catalog.
- Sessions are short or the cache is cold. The effective-input metric assumes cache reads cost roughly a tenth of fresh ones, which matches [Anthropic's published cache-read rate](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). One-shot calls and sessions that outlive the cache TTL pay the round trips with no discounted reads to offset them.
- Latency is the binding constraint. Reference costs a whole turn before answering, and the tool-based methods cost a round trip per fetch. The study excludes measured latency.
- Block boundaries are drawn badly. Routing correctness was never labeled, and the authors call task accuracy a weak proxy for it, because later feedback can recover a wrong fetch. A badly split skill degrades quietly.
- You need a number that transfers. Primary runs come from a single GitHub Copilot endpoint reported as gpt-5.5, with no provider-attested model identity, and the size guidance is described as a post-hoc heuristic rather than a validated gate.

## Example

Rank candidate methods on your own traffic before adopting one. For each arm, subtract the cache-read tokens from the provider's reported input tokens, then add back a tenth of the cache reads:

```
effective_input = (raw_input - cache_read) + 0.1 * cache_read
```

Run that over a representative multi-turn session per method and compare medians. If your provider prices cache reads differently, substitute your own discount for 0.1, since the factor is a sensitivity assumption in the paper rather than a billed rate ([arXiv:2608.14943v1](https://arxiv.org/abs/2608.14943v1)).

## Key Takeaways

- Two properties decide the method: the skill's token size, and the share of it a typical turn needs.
- Hybrid was the only method that beat preloading on both single-turn benchmarks; Skill Block was worse than preloading on the smallest one, in the aggressively nudged arm the authors flag as a diagnostic rather than a configuration to run.
- Conditional loading pays off only when the fetch mechanism leaves the cached prefix intact.
- Rank methods on cache-corrected input, because raw token counts favor the preload baseline.
- The measurements come from one provider endpoint and establish no quality equivalence, so treat the percentages as a shape to test locally rather than a rule to adopt.

## Related

- [Progressive Disclosure for Layered Agent Definitions](../patterns/agent-design/progressive-disclosure-agents.md) — the underlying principle these four methods implement in different ways
- [Dynamic Tool Fetching Breaks KV Cache](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md) — what happens when conditional loading mutates the cached prefix
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md) — the same eager-or-deferred decision at MCP server granularity
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — why the prefix hierarchy constrains any loading design
- [Skill Loadout Curation for Coding Agents](skill-loadout-curation.md) — which skills to carry at all, before deciding how to load each one
