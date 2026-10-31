---
title: "Batched Context Eviction for Cache Reuse"
term: "Batched Context Eviction"
description: "Trimming an agent's history every step leaves the whole history uncacheable. Evict in large batches instead, once you have confirmed you must evict at all."
aliases:
  - batched history pruning
  - batch screenshot pruning
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-10-12
maturity: emerging
---

# Batched Context Eviction for Cache Reuse

> Evicting an agent's history in large batches instead of at every step holds the prefix byte-identical between cuts, so the cache keeps serving it.

Batched context eviction cuts old observations out of an agent's conversation history in one large removal every N calls. The alternative it replaces is trimming a little on every call. The removal still breaks the prompt cache, once per batch instead of once per turn, and every call in between is a pure prefix extension that reads from cache.

## First check whether you must evict at all

An append-only history is the cheaper policy where the budget covers the task. Asana's 144-run study of its StackAI browser agent ran a 12-run follow-up that kept every screenshot, and reports "[c]ost per call was 1.2x lower than the best condition on Model B and GPT-6.1 Sol, and about 5% lower on Model C" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). Not evicting at all is the limit case of batching, where the prefix stops moving entirely.

Batching is for when the history will outgrow its budget. Asana names the three conditions: "Pruning still matters for long tasks, small context windows and more expensive cache reads" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)).

## Why it works

A prompt cache keys on an exact prefix, so reuse extends only as far as the first changed byte. Asana states it plainly: "a cache only reuses the longest unchanged prefix of a request" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). Dropping one screenshot from the middle of the history therefore does not cost one screenshot. It moves the divergence point back to that screenshot's position, and the provider recomputes and rewrites everything after it.

At a per-step cadence the divergence point resets on every call, so the cache is written and rarely read. That makes caching the history actively worse than leaving it uncached. In Asana's words: "Without batch pruning, caching the history at the larger budget cost more than not caching it on three of four models: the cache was continually rewritten and rarely read" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)).

The rule is not specific to one provider. Anthropic documents the same hierarchy: "Changes at each level invalidate that level and all subsequent levels." Its invalidation table also lists image add/remove as invalidating the message cache, which is the screenshot-eviction case ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

## When this backfires

- The task is short. At Asana's 20-to-1 ratio, "the agent keeps up to 20 and then cuts back to 1, so about 19 consecutive calls reuse the cached history" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). An agent that finishes in eight calls never reaches a cut, so tuning the batch size changes nothing.
- Cache reads are not cheap enough. The economics rest on reads at "0.05x to 0.1x the standard input price" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). As that ratio rises, holding 19 extra observations stops paying for itself.
- The budget is sized for the wrong model. Trim points move between models: "Model C first trimmed its history at call 10, Model A at call 64. At 120,000 characters, Model C answered in none of 18 runs and GPT-6.1 Sol in 3, most hitting the step limit" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). A batch size tuned against call 64 does no work on a model that starts trimming at call 10.
- Nothing caps a drifting run. Asana keeps the guardrail: "a drifting agent grows toward the context limit, and if the cache breaks, every call pays full price" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). Caps on steps, tokens, and cost per run bound a bad run. A batch policy does not.
- Answer quality under a longer window is the binding constraint. Holding 20 observations instead of one lengthens every request. NoLiMa reports of the 13 long-context models it evaluated that while they "perform well in short contexts (<1K), performance degrades significantly as context length increases" ([arxiv 2502.05167v3](https://arxiv.org/abs/2502.05167v3)). Asana scored cost and answer correctness on a catalog-extraction task, not reasoning quality under a backlog. See [Lost in the Middle](lost-in-the-middle.md) and [The Context Window Dumb Zone](context-window-dumb-zone.md).

One caveat sits under all five. Asana bounds its own resolution: "this study shows broad patterns rather than distinguishing conditions only a few percent apart" ([Asana](https://asana.com/inside-asana/cut-browsers-agent-cost)). Only the Model C figure (about 5%) sits near that floor. The 1.2x figures on Model B and GPT-6.1 Sol sit above it, so the no-prune result stands as counter-evidence. Asana limits it to runs that avoid its three conditions: long tasks, small context windows, and more expensive cache reads.

## Example

Asana's browser agent cached its system prompt and tool definitions but not its history, and removed the previous screenshot at every step. The study tested six caching and screenshot policies at history budgets of 120,000 and 480,000 characters, three runs per condition on each of four models. Every configuration ran the same task: collecting six fields for each of 32 books from a public demo catalog ([OpenAI](https://openai.com/index/asana-browser-agent)).

The winning policy let screenshots accumulate to 20 before cutting back to the most recent one, which "kept earlier history unchanged for longer stretches between removals" ([OpenAI](https://openai.com/index/asana-browser-agent)). Holding the budget constant on one model isolates what the change bought: "On GPT-6.1 Sol alone, with the larger history budget, the new caching and screenshot policy reduced cost 4x, from $1.97 to $0.47 per run. Each call was about 3x cheaper, because 89% of the input came from cache at 5% of the uncached price" ([OpenAI](https://openai.com/index/asana-browser-agent)).

The headline figure carries a different baseline. That same $0.47 run is "76x cheaper and 5x faster than the original production setup on Model B" ([OpenAI](https://openai.com/index/asana-browser-agent)), a cross-model comparison against the unoptimized agent rather than a measurement of batching alone.

## Key Takeaways

- Measure whether the history ever exceeds its budget before designing an eviction policy. If it does not, raise the budget and evict nothing.
- Turning on history caching without changing a per-step eviction cadence raised cost on three of four models Asana tested. Ship the two changes together or neither.
- Instrument the call at which your own history first trims, per model, and set the batch size from that. Asana measured that call at 10 on one model and 64 on another.
- Caps on steps, tokens, and cost per run stay necessary. A batch policy bounds cache churn, not run length.
- Report the cache-read share of input per call, not just the bill. It is the number that tells you whether the cadence change took effect.

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — protects the static prefix; this page covers the growing history that page treats as uncached tail
- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md) — replacing a tool output with a summary is an edit to the history, and carries the same cache cost
- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](half-life-tool-result-truncation.md) — a per-step trimming policy, scored on fix rate rather than cache reuse
- [Attributed Cache Misses: Reading Why a Prefix Diverged](attributed-cache-miss-diagnostics.md) — the provider field that names where the prefix diverged after an eviction
- [Action-Gated Context Trimming](action-gated-context-trimming.md) — deciding what to hold by the agent's next action, the orthogonal axis to when to cut
- [Scoring a Context Policy on Executed Prefill](executed-prefill-accounting.md) — the counter that prices a cadence: logical prompt minus reused prefix, with the break-even for deleting history at all
