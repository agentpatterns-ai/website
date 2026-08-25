---
title: "Cache-Prefix Staggering for Sibling Agent Fan-Out"
term: "Cache-Prefix Staggering"
description: "When the shared prompt prefix is cacheable, delaying each sibling in a fan-out until the first response begins lets later siblings read that prefix instead of each writing their own cache entry."
tags:
  - multi-agent
  - cost-performance
  - tool-agnostic
aliases:
  - prompt prefix cache staggering
  - cache warming before fan-out
last_reviewed: 2026-08-18
maturity: emerging
---

# Cache-Prefix Staggering for Sibling Agent Fan-Out

> When the shared prefix is cacheable, delaying each sibling until the first response begins turns N cache writes into one write plus N-1 reads.

A provider writes a prompt-cache entry while serving a request, not while receiving one. Siblings launched at the same instant therefore have no entry to read, so each prefills the shared prefix and is billed for it. Anthropic states the constraint directly: "For concurrent requests, note that a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests" ([Prompt caching, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

## When this pays

All of the following have to hold before a stagger returns anything:

- The shared prefix clears the provider's minimum cacheable length. Anthropic's per-model floor runs from 512 to 4,096 tokens, and shorter prompts are processed without caching and without an error ([Prompt caching, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). OpenAI caches automatically "for prompts that are 1,024 tokens or longer" ([Prompt caching, OpenAI API](https://developers.openai.com/api/docs/guides/prompt-caching)).
- Every sibling sends the same prefix. Anthropic invalidates in the hierarchy tools, then system, then messages, and "changes at each level invalidate that level and all subsequent levels" ([Prompt caching, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)), so a per-sibling tool allowlist or an injected timestamp splits one entry into N.
- The shared prefix is a large share of each sibling's input. When each worker also carries a large task-specific payload, the discount applies to a small part of the bill.
- The provider bills cache writes. Anthropic charges 1.25x base input for a 5-minute write. OpenAI charges 1.25x on GPT-5.6 and later, and states that "cache writes have no additional fee on models before the GPT-5.6 family" ([Prompt caching, OpenAI API](https://developers.openai.com/api/docs/guides/prompt-caching)).
- The fan-out can absorb the delay. The last sibling starts N-1 intervals late.

## Why it works

Lumer et al. define prompt caching as the "productized, provider-managed features that reuse KV tensors across API requests when prompts share common prefixes" ([2026 v2, §2.2](https://arxiv.org/abs/2601.06007v2)). That prefix-match requirement is the constraint [prompt caching as architectural discipline](../../context-engineering/prompt-caching-architectural-discipline.md) treats as structural. Creating a cache entry is a side effect of serving a request, so a read can only hit an entry that already exists. That is why Anthropic pins availability to the moment "the first response begins" rather than to request submission ([Prompt caching, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

The size of the win follows from published multipliers, not from a measurement. Anthropic prices a 5-minute cache write at 1.25x base input tokens and a cache read at 0.1x. For N siblings sharing a prefix of P tokens:

| Launch shape | Cost of the shared prefix | N = 8 |
|---|---|---|
| Simultaneous, caching requested | N x 1.25P | 10.0P |
| Simultaneous, no caching | N x 1.0P | 8.0P |
| Staggered | 1.25P + 0.1(N-1)P | 1.95P |

That arithmetic covers the shared prefix only, and neither Anthropic nor the Claude Code changelog publishes a measured saving for the behavior.

## How it differs from queue-contention staggering

[Staggered Agent Launch](staggered-agent-launch.md) prescribes the same physical action for an unrelated reason: de-synchronizing queue reads so each agent claims work before the next one looks. The two motives size the delay differently.

| Question | Queue contention | Cache prefix |
|---|---|---|
| What the delay must cover | One agent reading and reserving work | One request beginning to return tokens |
| Order of magnitude | Seconds | Milliseconds |
| Fails when | Queue-read latency varies | Prefixes diverge or fall below the cache minimum |
| Structural alternative | File-locked task claims | A single warm-up request before the fan-out |

Both can apply to one fan-out. Size the interval from whichever constraint is larger.

## When this backfires

- The prefix falls below the cacheable minimum. No entry is written, no error is raised, and the delay is pure added latency.
- Siblings diverge. Distinct system text or tool definitions give each sibling its own entry at 1.25x, which costs more than a flat uncached fan-out. This is the [mid-session config-cache invalidator](../anti-patterns/mid-session-config-cache-invalidators.md) failure applied across siblings instead of across turns.
- The first sibling errors or is rate-limited before its response begins. Every later sibling misses and the delay bought nothing.
- The fan-out is interactive. A person waiting on results feels N-1 intervals of serialization, which is the latency the fan-out existed to remove.
- Concurrency is very high on one OpenAI cache key. OpenAI advises keeping "the total traffic across all prefixes for each key to approximately 15 requests per minute" ([Prompt caching, OpenAI API](https://developers.openai.com/api/docs/guides/prompt-caching)), so a wide fan-out can miss regardless of timing.
- Caching is applied to the wrong span. Lumer et al. found that "naively enabling full-context caching can paradoxically increase latency, as dynamic tool calls and results may trigger cache writes for content that will not be reused across sessions" ([arXiv:2601.06007v2](https://arxiv.org/abs/2601.06007v2)).

## Example

Claude Code ships the stagger as a default rather than leaving it to the caller. Release 2.1.229 (2026-08-12) records: "Improved workflow fan-outs to stagger same-prefix sibling agents so subsequent agents read the cached prompt prefix instead of re-paying it (`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS=0` disables)" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-229)).

```bash
# Opt out when siblings do not share a prefix and the delay buys nothing
CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS=0 claude
```

The changelog publishes the opt-out but not the default value, so the only supportable statement about the interval is its unit. The `_MS` suffix puts it in milliseconds, which matches a delay sized to a first response rather than to a queue claim. Where a harness does not automate the stagger, the caller applies it, which is what Anthropic's own instruction to "wait for the first response before sending subsequent requests" asks for ([Prompt caching, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

## Key Takeaways

- A cache entry exists only once a request is being served, so simultaneous siblings can never read one another's prefix.
- Size the interval to the first sibling's time to first token, not to its full response, and not to the seconds-scale interval that queue contention needs.
- One warm-up request before the fan-out writes the same entry and lets the siblings then start together, rather than each waiting behind the one before it.
- Check the prefix against the provider's minimum cacheable length before adding any delay; below it the stagger is cost with no benefit.
- Verify that siblings really do send byte-identical prefixes, because divergence converts the discount into a write premium.

## Related

- [Staggered Agent Launch](staggered-agent-launch.md) — the same delay applied to work-queue contention instead of cache reuse
- [Sub-Agents for Fan-Out Research and Context Isolation](sub-agents-fan-out.md) — the fan-out shape this pattern prices
- [Bounded Batch Dispatch](bounded-batch-dispatch.md) — batching as the rate-limit companion to launch timing
- [Mid-Session Config Changes as Invisible Cache Invalidators](../anti-patterns/mid-session-config-cache-invalidators.md) — the same prefix divergence seen across turns
- [Prompt Caching: Architectural Discipline for Agents](../../context-engineering/prompt-caching-architectural-discipline.md) — how to compose context so a shared prefix exists at all
- [Prompt Cache Keepalive for Agent Pauses](../../context-engineering/prompt-cache-keepalive-agent-pauses.md) — keeping an entry resident once it is written
