---
title: "Attributed Cache Misses: Reading Why a Prefix Diverged"
term: "Attributed Cache Miss"
description: "Anthropic and OpenAI both return a field naming where your prompt prefix diverged. Read it beside the usage counters, which report whether the cache hit."
aliases:
  - Cache Diagnostics
  - Prompt Cache Diagnostics
tags:
  - context-engineering
  - cost-performance
  - observability
  - tool-agnostic
last_reviewed: 2026-09-28
maturity: emerging
---

# Attributed Cache Misses: Reading Why a Prefix Diverged

> An attributed cache miss names where your request diverged. It does not say whether the cache hit, so read it beside the usage counters.

An attributed cache miss is an opt-in field the provider returns naming where the current request stopped matching a baseline request you nominate. Anthropic returns it as `diagnostics.cache_miss_reason`, opted into with a `diagnostics` object carrying the previous response id ([Anthropic cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)). OpenAI returns it as `prompt_cache_diagnostics.reason`, opted into with `prompt_cache_options.comparison_response_id` ([OpenAI prompt cache diagnostics](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)).

## Read the reason beside the token counts

Anthropic states the scope outright: "The comparison is about request structure, independent of whether the cache actually hit." Its `diagnostics` field reports whether the request changed; `usage.cache_read_input_tokens` reports whether the cache hit. "Combining them tells you where to look." [Source: [Anthropic](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)]

OpenAI draws the same line. Its `cache_hit` verdict means only "no cache miss was detected for the comparison", and it sends you elsewhere for the outcome: "Use `usage.input_tokens_details.cached_tokens` to measure actual cache reuse." [Source: [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)]

The pairing separates two failures that look identical in a cost report. On a turn that passed a real previous message id, Anthropic reads a clean diagnostic with cold reads as "Your requests match but the cache entry was no longer available", answered by shorter turn gaps or the 1-hour TTL. A `*_changed` reason with cold reads gets a blunter verdict: "Your bug. The request changed; fix the cause indicated by `type`." [Source: [Anthropic](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics)]

## What each provider documents

| | Anthropic Claude API | OpenAI Responses API |
|---|---|---|
| Opt-in field | `diagnostics.previous_message_id` | `prompt_cache_options.comparison_response_id` |
| Baseline requirement | Both turns carry the `diagnostics` object: "It stores nothing for requests that omit the object" | "a recent completed response from the same organization" |
| Reason values | Six on `cache_miss_reason.type`, four of them `*_changed` | Nine on `reason`, from `model_changed` to `input_changed` |
| Lost-token estimate | `cache_missed_input_tokens`, on the four `*_changed` types | `cache_missed_tokens`, plus `comparison_reusable_tokens` when present |
| Platform scope | Claude API only: "Not available on Amazon Bedrock or Google Cloud" | "the Responses API for GPT-5.6 and later supported models" |

Sources: [Anthropic cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics), [OpenAI prompt cache diagnostics](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics), both read 2026-09-28.

`unavailable` is where a ported harness misreads a verdict. Both vendors document it as a result with no conclusive comparison. Anthropic lists two causes: a difference in another prompt-affecting parameter, meaning the case where "`model`, `system`, and `tools` match but another prompt-affecting request parameter (`tool_choice`, `thinking`, `context_management`, `output_config`, `output_format`, or the set of active `anthropic-beta` headers) differs", and a conversation where "the divergence is beyond the comparison horizon". OpenAI says its result "does not indicate a hit or miss and is returned if the comparison is not ready".

## Why it works

The comparison runs server-side over the fields that key the provider's own cache, so it sees divergences the client never authored. OpenAI documents three causes a client-side prefix hash cannot see. Its `model_changed` reports that "A different model processed the request", with routing, an A/B test, and fallback given as the examples. Its remedy for `service_tier_changed` is to "Check the returned `service_tier`, which can differ from the requested value". Its `context_compacted` covers the case where "Compaction replaced earlier conversation content". [Source: [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)]

That bounds the claim. Hashing your own serialized prefix each turn costs nothing, ports everywhere, and catches every divergence you introduced yourself. The provider surface earns its opt-in on the causes you did not.

## When this backfires

- Your Claude traffic runs through Bedrock or Vertex. Anthropic is explicit: "Not available on Amazon Bedrock or Google Cloud."
- Turns sit far apart. Both vendors expire the diagnostic record after a short period, and Anthropic advises comparing "closely spaced requests". A stale baseline returns a not-found verdict, which Anthropic warns "is not evidence that your request changed". A nightly batch pipeline collects those all day.
- Sibling agents fan out across workspaces. Anthropic requires the baseline to have run in the same organization and workspace, so a cross-workspace comparison fails for a reason unrelated to the prompt. OpenAI names a baseline from the same organization.
- You want the estimate in a cost model. Anthropic derives `cache_missed_input_tokens` "from byte lengths before tokenization, so treat it as a magnitude indicator rather than a billing number", and OpenAI says its diagnostic counts "can differ from usage counts".
- You expect a full causal decomposition. Anthropic "reports the earliest divergence only, so fix it first; later ones may be hidden behind it". OpenAI's are "best effort and may not classify every miss".

One OpenAI code needs separate handling. `prompt_cache_key_changed` "can be reported as a cache miss in response `usage` without a physical cache miss", so it can name an accounting artifact rather than lost reuse. [Source: [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)]

## Key Takeaways

- Log the reason code and the cache-read token count on the same line. Either alone leaves the ambiguity the field exists to remove.
- A clean diagnostic with cold cache reads points at TTL and turn spacing, not at prompt assembly.
- Treat a not-found verdict and `unavailable` alike, as no conclusive comparison rather than a verdict on the prompt. Anthropic's usage matrix excludes both, and its `unavailable` can come from a changed parameter such as `tool_choice` or from a conversation beyond the comparison horizon.
- Keep the lost-token estimate out of cost models. Both vendors say it can disagree with the billed usage figures.
- For your own serialization, a client-side prefix hash needs no opt-in and no provider support. The provider surface pays for itself on model routing and fallback, which both vendors report, and on service tier and server-side compaction, which only OpenAI reports.

## Example

Anthropic documents sending the `diagnostics` object on every turn. Pair it with the usage read:

```python
resp = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    cache_control={"type": "ephemeral"},
    system=SYSTEM,
    tools=TOOLS,
    messages=history,
    diagnostics={"previous_message_id": previous_id},
)

diag = resp.diagnostics
reads = resp.usage.cache_read_input_tokens

if diag is not None and diag.cache_miss_reason is None:
    print("comparison still pending; check the next turn")
elif diag is None:
    if reads == 0:
        print("no divergence, cold reads: shorten the gap or take the 1h TTL")
else:
    print(f"{diag.cache_miss_reason.type}, cache_read_input_tokens={reads}")
```

The middle branch is the point. Without the usage read, an expired entry and a mutated prefix both surface as a cold cache. The first branch exists because a `cache_miss_reason` of `null` means the comparison "was still running when the response was serialized", and the reference says to treat that as inconclusive and check the next turn. Field names and semantics follow [Anthropic's cache diagnostics reference](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) (read 2026-09-28).

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — the discipline, economics, and TTL choice whose results this page reads
- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md) — the same attribute-instead-of-guess move, applied to window growth
- [Prompt Cache Keepalive for Agent Pauses](prompt-cache-keepalive-agent-pauses.md) — what to do when the diagnostic is clean and the entry expired anyway
- [Mask Tools Instead of Removing Them](mask-tools-instead-of-removing.md) — the fix OpenAI suggests for a tools-changed reason
- [Dynamic Tool Fetching Breaks KV Cache](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md) — the harness design that produces a tools-changed reason every turn
