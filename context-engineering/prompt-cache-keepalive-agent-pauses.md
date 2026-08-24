---
title: "Prompt Cache Keepalive for Agent Pauses"
term: "Prompt Cache Keepalive"
description: "Replay a cached prefix on a timer to survive tool runs and approval waits — and the billing, pause-length, and interval conditions that decide whether it saves money or costs more."
aliases:
  - cache keepalive ping
  - keeping the prompt cache warm
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-07-28
maturity: emerging
---

# Prompt Cache Keepalive for Agent Pauses

> Replaying a cached prefix on a timer keeps the cache resident through an agent pause — but only pays inside a narrow band.

A keepalive sends a cheap request that replays your cached prefix during an idle gap, so the entry stays warm instead of expiring while a tool runs or a human approves a step. The technique is real and the arithmetic is documented, but it pays only under four conditions at once. Most teams that ping today are outside at least one of them.

## When keepalive pays

Check all four before wiring a timer:

- You pay per token. On Claude Pro or Max, or any seat-based plan, there is no token bill to reduce and each ping consumes request quota instead ([claude-code-cache-keepalive](https://github.com/yujiachen-y/claude-code-cache-keepalive)).
- Your pauses exceed the cache lifetime. Anthropic's default entry lives five minutes ([Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)), so a two-second tool call never needed help.
- Your pauses stay under the break-even horizon. Repeated ping costs add up over a long pause, while the re-prefill they prevent is a single charge. Khailo puts the crossover near 46 minutes on Anthropic's five-minute tier ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214v2)).
- Your provider actually evicts. The same measurements found Google's implicit cache "never reliably evicts" and DeepSeek's re-prefill "too cheap to insure," which empties the paying band on both.

Miss any one and the honest answer is to do nothing, or to buy a longer lifetime instead. See [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md), which covers the five-minute against one-hour tier decision.

## Why it works

A cache read restarts the eviction clock, and providers charge far less for that read than for rebuilding the entry. Anthropic states the refresh semantics directly: "The cache is refreshed for no additional cost each time the cached content is used." The prices around it make the arbitrage: cache reads bill at 0.10x base input, while a five-minute cache write bills at 1.25x ([Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). A keepalive therefore buys a 0.10x read to avoid a 1.25x write. Khailo reports the same refresh-on-read behavior across the four providers measured — "In all four, reading a cached prefix refreshes it" — which is why the optimal interval falls out mechanically: the longest gap that still lands inside the retention window, minus margin for jitter and latency ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214v2)).

## Choosing the interval

Shipped tooling gets the interval wrong far more often than the idea. Roughly 240 seconds on Anthropic holds the same retention as the conventional 30-second ping: median cache hit rate stayed at or above 98% either way. The 30-second convention just spends about 8x more for it: 7.8x across the paper's interval runs, or about $3.60 per hour against about $0.45 per hour on a 100k-token prefix at July 2026 list prices ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214v2)).

Overshooting is the more expensive error. At Anthropic's 300-second lifetime, a 900-second interval means every ping lands on a dead entry and pays the full write price, so the keepalive "costs 4x more than never pinging" ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214v2)). Measure your own retention rather than copying a table: cross-provider lifetimes move, and OpenAI now defaults organizations without zero data retention to a 24-hour window. That contradicts the shorter lifetimes usually assumed ([OpenAI API changelog](https://developers.openai.com/api/docs/changelog)).

## When this backfires

- Subscription billing. Pings cost quota and save nothing ([claude-code-cache-keepalive](https://github.com/yujiachen-y/claude-code-cache-keepalive)).
- Long walk-aways. Past the break-even horizon, the pings' combined cost exceeds the one re-prefill they avoided ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214)).
- An interval above real retention, which inverts the result to 4x worse than doing nothing.
- Prefix mutation mid-pause. If tool definitions or the system prompt change while the timer runs, you warm a prefix the next real request will not match (the failure mode described in [Static Content First for Cache Hits](static-content-first-caching.md)).
- Fleet-wide adoption. Khailo argues keepalives manufacture recency, so "once every client keeps its prefixes alive, LRU has nothing left to rank and the tier degrades toward first-in-first-out-of-luck," which pushes providers toward metering residency directly and closes the arbitrage ([arXiv:2607.19214](https://arxiv.org/abs/2607.19214v2)).

## Example

Three shipped implementations, three different intervals, against Anthropic's documented 300-second lifetime:

```text
aider --cache-keepalive-pings N   → 300 s   no margin below the TTL; off by default
claude-code-cache-keepalive       → 240 s   Stop hook sleeps, then injects a turn
openclaw #62475 (proposed)        → TTL x 0.8 (~240 s), plus a $0.10/hour cost cap
```

Only the second and third leave headroom for jitter. Aider fires exactly at the documented lifetime ([aider docs](https://aider.chat/docs/usage/caching.html)); the Claude Code plugin sleeps 240 seconds and injects a keepalive turn through a Stop hook ([repo](https://github.com/yujiachen-y/claude-code-cache-keepalive)); openclaw derived an adaptive interval of 0.8 times the TTL with an automatic cost cap, then closed the proposal as not planned ([openclaw#62475](https://github.com/openclaw/openclaw/issues/62475)). Maintainers weighed the complexity against the saving and declined the proposal.

## Key Takeaways

- Check your own provider's read-versus-write price ratio before wiring a keepalive: Anthropic's 0.10x-read against 1.25x-write split is what makes the arbitrage pay, and a provider priced differently may not reward it.
- Do not copy a shipped tool's default interval without checking it against your provider's real cache lifetime: a 30-second ping can spend roughly 8x more than an interval tuned to the retention window, for no extra retention.
- When the retention window is uncertain, undershoot rather than overshoot: an interval past the real lifetime turns every ping into a full-price rebuild, about 4x worse than never pinging at all.
- Rule out all four disqualifying conditions before deploying: billing model, pause length against the cache lifetime, walk-away length against the break-even horizon, and whether the provider actually evicts. Missing any one erases the saving.
- Measure your provider's retention window; published cross-provider lifetimes conflict and change.

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — the five-minute against one-hour tier decision, the documented alternative to a client-side timer
- [Static Content First for Cache Hits](static-content-first-caching.md) — prefix layout, the prerequisite a keepalive cannot substitute for
- [Exclude Dynamic System Prompt Sections for Cross-Machine Cache Sharing](exclude-dynamic-system-prompt-sections.md) — removing per-machine variance so a prefix is shareable in the first place
- [KV Cache Invalidation in Local Inference](kv-cache-invalidation-local-inference.md) — the same prefix-match mechanism at the local serving layer
