---
title: "Gateway Session Affinity: Read the Pin, Not the Cache Rate"
term: "Gateway Session Affinity"
description: "Gateways pin a session to the provider holding its prompt cache. Defaults, session identity, and precedence over your provider order differ, so read the recorded outcome."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - model-routing
aliases:
  - sticky routing for prompt caches
  - provider pinning per session
  - session affinity outcome
last_reviewed: 2026-10-19
maturity: adopted
---

# Gateway Session Affinity: Read the Pin, Not the Cache Rate

> Gateways pin a session to the provider holding its prompt cache, and disagree on the defaults, so read the outcome each one records.

Gateway session affinity routes each turn of one conversation to the provider instance that served the turn before it, so that provider still holds most of the prompt in cache. Vercel AI Gateway, OpenRouter, LiteLLM, and Portkey all ship it. They disagree on whether it runs by default, on what identifies a session, and on whether the pin overrides a provider order you declared. Read what the gateway recorded for the request rather than assuming the route held.

## Three conditions before the signal means anything

Pin at provider or deployment granularity for cache locality. LiteLLM keeps two separate pins, and only the second concerns cache locality: "A tier with several deployments behind it also needs `deployment_affinity` and the `prompt_caching` pre-call check in `router_settings`, so continuing turns return to the deployment holding the cache" ([LiteLLM, Prompt Caching](https://docs.litellm.ai/docs/auto_router/prompt_caching)).

Send the session identity yourself. Vercel checks six sources in priority order and falls back to a SHA-256 fingerprint of the first system message, the first non-system message, and the tool set. Unrelated runs then collide: "Two conversations that open with the same system prompt, tools, and first user message share a fingerprint. A script that starts every run with a templated message such as \"Begin the task.\" does this" ([Vercel, AI Gateway Session Affinity](https://vercel.com/docs/ai-gateway/models-and-providers/session-affinity)). Claude Code gets an identity free at priority five, where "Claude Code sends it automatically" via `x-claude-code-session-id` (same page).

The prompt must be cacheable. For a session the gateway named itself, it "skips pinning when the prompt is below that minimum" — 1,024 tokens for most OpenAI and Google models (same page).

## What the gateway records

Vercel returns the decision on every response under `providerMetadata.gateway.routing`: the session ID, whether it was `explicit`, `agent`, or `fingerprint`, the outcome, the pinned provider, and the provider the pin displaced. The outcome is one of nine values, three of which mean the pin never existed rather than failed: `no_pin`, `skipped_below_min_prefix`, and `not_cache_capable`. One reports a conflict with your own configuration, since `skipped_not_in_plan` means "Your routing settings removed the pinned provider from this request". Write the reader to tolerate additions, since the gateway "can add values over time, so handle unknown values as \"no change\"".

One value is worth alerting on by itself. `pin_expired` means "The session had a pin for this model, but it expired. The provider's cache is likely cold" ([Vercel, AI Gateway Session Affinity](https://vercel.com/docs/ai-gateway/models-and-providers/session-affinity)). An expired pin signals a likely cold cache; it does not prove a cache miss.

The per-session view arrived on 18 October 2026: "Open a session to see its cache hit rate, duration, and path. The path lists each turn with its model and timing, and names the provider serving the session along with any earlier ones" ([Vercel changelog, 2026-10-18](https://vercel.com/changelog/ai-gateway-logs-now-show-session-affinity)). OpenRouter answers from the usage object rather than an enum: "`usage.prompt_tokens_details.cached_tokens` shows how many tokens were read from cache. If it's greater than zero, the request hit the cache" ([OpenRouter, Prompt Caching and Sticky Routing](https://openrouter.ai/blog/tutorials/prompt-caching-sticky-routing/)).

## Precedence over your provider order is not portable

Write the policy against one gateway and it is wrong on the next. On Vercel, "The pinned provider goes first, ahead of your order. Set `sessionAffinity: false` to keep your order exactly" ([Vercel, AI Gateway Session Affinity](https://vercel.com/docs/ai-gateway/models-and-providers/session-affinity)). On OpenRouter the precedence inverts: "One catch: if you set `provider.order` yourself, your order wins over sticky routing" ([OpenRouter](https://openrouter.ai/blog/tutorials/prompt-caching-sticky-routing/)). Portkey ships it off until you set `sticky.enabled`, keyed on fields you nominate in `hash_fields` ([Portkey, Load Balancing](https://portkey.ai/docs/product/ai-gateway-streamline-llm-integrations/load-balancing)).

Pin lifetime follows the cache, not the conversation. Vercel "starts from a default lifetime for each provider, then subtracts 15 seconds so a pin never outlives the cache": 5 minutes for Anthropic, Bedrock, and Google, 10 for OpenAI and Azure, 1 hour for DeepSeek. The ceiling is fixed at 1 hour, because "A pin never lasts longer than 1 hour, even when the cache does" (same page).

## Why it works

A provider prompt cache is local to the account and instance that wrote it, so the cache-read discount depends on where the next request lands rather than on what it contains: "A provider's prompt cache lives on the provider account that served your request. When the next request in a conversation goes somewhere else, that cache is cold and you pay full price for the prompt again" ([Vercel, AI Gateway Session Affinity](https://vercel.com/docs/ai-gateway/models-and-providers/session-affinity)). OpenRouter states the same chain from the client side: "A warm cache only helps if the next request lands on the provider endpoint that holds it" ([OpenRouter](https://openrouter.ai/blog/tutorials/prompt-caching-sticky-routing/)). Affinity loops over that locality: name the session, record which provider served it, promote that provider next time, expire the record before the cache. Every stage can decline, which is why the gateway reports which one ran.

## When this backfires

- Pinning the model to protect the cache. Across "4,684 real switch-backs" on live traffic LiteLLM reports that "97.4% found the cache warm at a 5-minute TTL", and ships `session_affinity` off "and that is the right setting for most routers. The numbers above show it is not needed for the cache, and pinning forfeits the savings from routing later turns down a tier" ([LiteLLM, Prompt Caching](https://docs.litellm.ai/docs/auto_router/prompt_caching)). The same source recommends pinning when provider-specific history or visible model consistency requires it.
- A replicated gateway with no shared pin store. Portkey: "Sticky sessions require Redis for persistence across gateway instances. Without Redis, sticky sessions will only work within a single gateway instance's memory" ([Portkey, Load Balancing](https://portkey.ai/docs/product/ai-gateway-streamline-llm-integrations/load-balancing)).
- Affinity bookkeeping at scale. Li and colleagues measured it as the largest single per-request cost in their gateway: "Session Management—session-affinity lookup and routing—dominates the cost, contributing 3.45 ms on average (75% of mean RT)", rising to a "P99 growing from 4.07 ms to 37.55 ms" across four instances, where "The increase comes mainly from session data misses" ([Li et al., arXiv:2607.15593v1 §6.4](https://arxiv.org/abs/2607.15593v1)). Their affinity holds a stateful backend session rather than a prompt cache, so read it as the price of the bookkeeping.
- Long human pauses. A pause longer than the pin lifetime can expire the pin. Check cached-token usage before concluding that the provider rewrote the prefix.
- Request types with nothing to keep warm. "Session affinity doesn't apply to other request types, such as embeddings, images, or realtime sessions. They have no prompt cache to keep warm" ([Vercel, AI Gateway Session Affinity](https://vercel.com/docs/ai-gateway/models-and-providers/session-affinity)).
- Reading the header as a promise. Vercel's caveat: "The header doesn't guarantee a cache hit" ([Vercel, Automatic Prompt Caching](https://vercel.com/docs/ai-gateway/models-and-providers/automatic-caching)).

## Key Takeaways

- Send an explicit session ID per agent run. A fingerprint derived from the conversation opening groups templated runs together, and the fix costs one header.
- Alert on `pin_expired` and on `skipped_not_in_plan`, not on the session cache-hit rate. The rate tells you something was cold; those two say which stage declined.
- Treat `no_pin` as "no pin for this model yet". Check prompt size for `skipped_below_min_prefix` and caching support for `not_cache_capable`.
- Check the precedence rule before writing a provider order, because Vercel's pin overrides your order and OpenRouter's order overrides the pin.
- Pin at deployment or provider granularity. LiteLLM leaves model pinning off for most routers, but it can preserve provider-specific history and visible model consistency.
- Budget for shared pin state before replicating the gateway. Portkey's sticky sessions work only within one instance without Redis. One tool-access gateway that holds backend sessions (not prompt caches) saw session-lookup P99 grow from 4.07 ms to 37.55 ms across four instances.

## Related

- [Cache-Safe Routing Boundaries: Where a Router May Act](cache-safe-routing-boundaries.md) — the companion question of when a router may change model at all, with the cache-read and cache-write arithmetic this page assumes
- [Gateway Hint Headers for Routing and Budgeting Agent Calls](gateway-hint-headers.md) — the client declares what it wants in headers; affinity outcomes record what the gateway did with it
- [Gateway Model Routing](gateway-model-routing.md) — treating the gateway as both inference target and model catalog
- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the cost model a pinned route feeds into
- [Persistent-Connection Agent Transport](persistent-connection-agent-transport.md) — the transport-level analogue of keeping one session on one backend
