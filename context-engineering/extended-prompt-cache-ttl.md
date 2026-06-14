---
title: "Extended Prompt Cache TTL for Long Agent Sessions"
term: "Extended Prompt Cache TTL"
description: "Enable Anthropic's 1-hour cache TTL when interactive coding sessions sit idle longer than 5 minutes — the 2x write premium pays back on the first re-use past the default TTL."
tags:
  - context-engineering
  - cost-performance
  - claude
last_reviewed: 2026-06-02
maturity: established
---

# Extended Prompt Cache TTL for Long Agent Sessions

> Switch the prompt cache from 5-minute to 1-hour TTL when sessions idle past 5 minutes — the 2x write premium pays back on first re-use.

Anthropic's prompt cache defaults to a 5-minute TTL. A cached prefix is evicted 5 minutes after its last read, and the next request pays the full cache-write cost. The 1-hour TTL is an opt-in alternative: writes cost 2x base input (vs 1.25x for 5-minute) but the entry stays warm for an hour ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). In Claude Code, opt in via `ENABLE_PROMPT_CACHING_1H=1` — added in v2.1.108 on April 14, 2026 ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). At the raw API level, set `cache_control: {"type": "ephemeral", "ttl": "1h"}` on the breakpoint.

## When the Longer TTL Pays Back

Anthropic recommends 1-hour TTL for prompts *"used less frequently than every 5 minutes, but more frequently than every hour"* and *"agentic scenarios where side-agents may take longer than 5 minutes"* ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Stay on 5-minute when reuse is more frequent than every 5 minutes — cache reads refresh the 5-minute window for free.

The decision reduces to session shape:

| Session shape | Idle gap pattern | TTL |
|---|---|---|
| Autonomous loop, no human in the middle | Continuous turns, < 5 min apart | 5-minute |
| Interactive code review | Mixed: most < 5 min, some 5–30 min | 1-hour |
| Agent waiting on side-agents or human review | Mostly 5–60 min idle | 1-hour |
| Walk-away workflows (return next day) | > 60 min idle | Neither — cache will expire |

## Why It Works

A 1-hour cache write costs 2x base input; two consecutive 5-minute writes cost 2 × 1.25x = 2.5x base. When a session idles longer than 5 minutes but resumes within the hour, the 1-hour write is strictly cheaper than rewriting the 5-minute cache on resume — the premium buys out one rewrite up-front. Skidmore (2026) derives the closed form for the related *refresh vs let-expire* decision: `T = 5 × (W / R) = 5 × (1.25 / 0.10) = 62.5 min`, with token count and per-token price cancelling out — the crossover is identical for a 5K Sonnet prefix and a 500K Opus prefix ([Skidmore: 62.5-minute rule](https://skids.dev/blog/anthropic-cache-tokenomics/)). The same algebra sets the 1-hour break-even: the multiplier ratio decides it, not prefix size or model. Reads stay at 0.10x base for both TTLs, so the only difference is the one-time write premium.

## Pricing Reference

| Model | Base input | 5-min write | 1-hour write | Cache read |
|---|---|---|---|---|
| Opus 4.7 | $5/MTok | $6.25/MTok | $10/MTok | $0.50/MTok |
| Sonnet 4.6 | $3/MTok | $3.75/MTok | $6/MTok | $0.30/MTok |
| Haiku 4.5 | $1/MTok | $1.25/MTok | $2/MTok | $0.10/MTok |

Source: [Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

## Verifying the Flag Is Doing Work

The response `usage` block separates 5-minute and 1-hour writes ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)):

```json
{
  "usage": {
    "cache_creation": {
      "ephemeral_5m_input_tokens": 148,
      "ephemeral_1h_input_tokens": 100
    },
    "cache_read_input_tokens": 1800
  }
}
```

When the flag is on, the system prompt and tool definitions should appear in `ephemeral_1h_input_tokens` on turn 1 and in `cache_read_input_tokens` thereafter. If they keep landing in `ephemeral_5m_input_tokens` or `cache_creation_input_tokens` mid-session, the flag is not honoured or a prefix mutation is busting the cache before the longer TTL can help — same discipline as the default cache ([Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md)).

## When This Backfires

- **Autonomous loops with no idle time.** A continuous agent loop reads the cache every few seconds. The 5-minute TTL refreshes for free on every read, so the 1-hour write premium is pure cost ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- **Walk-away workflows past one hour.** When the gap exceeds 60 min the cache evicts anyway; you paid 2x for the write and still pay a rewrite on resume. Skidmore's worked example: at T = 90 min, holding a 500K Opus prefix costs $1.375 more than letting it expire ([Skidmore](https://skids.dev/blog/anthropic-cache-tokenomics/)).
- **Mostly-dynamic prefixes.** Timestamps, dynamic tool definitions, or rotating system prompt fragments mutate the prefix between turns. Neither TTL helps; the longer one just makes the wasted write 60% more expensive ([Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)).
- **Sub-minimum prefixes.** Caching does not activate below the per-model floor (1,024 tokens on Sonnet 4.6; 4,096 on Opus 4.5/4.6/4.7 and Haiku 4.5). The API silently does not cache; `cache_creation_input_tokens` stays at 0 ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [Skidmore](https://skids.dev/blog/anthropic-cache-tokenomics/)).
- **Session-wide flag with mixed block sizes.** `ENABLE_PROMPT_CACHING_1H` paints every breakpoint with the 1-hour premium, including small dynamic blocks that rarely pay back. For finer control, set `ttl: "1h"` per breakpoint — 1-hour blocks must precede 5-minute blocks in the same request ([Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- **20-block lookback exhaustion.** Each breakpoint scans at most 20 content blocks backwards for a prior write. A long tool-heavy session can exceed that depth and silently miss the cache regardless of TTL ([Skidmore](https://skids.dev/blog/anthropic-cache-tokenomics/)).

## Key Takeaways

- 1-hour TTL pays back on the first cache read past the 5-minute window — break-even is at the multiplier ratio, not the prefix size.
- Interactive review sessions are the canonical fit; autonomous loops and walk-away sessions are not.
- In Claude Code, opt in via `ENABLE_PROMPT_CACHING_1H=1` (v2.1.108, April 14, 2026). At the API level, set `cache_control.ttl: "1h"` per breakpoint for finer control.
- Verify with the `ephemeral_1h_input_tokens` and `cache_read_input_tokens` usage fields — a mid-session spike in `cache_creation_input_tokens` means a prefix mutation has busted the cache, and a longer TTL cannot save you.
- The longer TTL does not raise the minimum-prefix floor or the 20-block lookback window. Those are still the dominant silent-failure modes.

## Related

- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md)
- [Prompt Cache Economics](prompt-cache-economics.md)
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)
- [Attention Latch](../agent-design/attention-latch.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
