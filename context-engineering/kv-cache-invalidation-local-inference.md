---
title: "Disable Attribution Headers to Preserve KV Cache in Local Inference"
description: "When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference"
tags:
  - cost-performance
aliases:
  - KV cache invalidation
  - attribution header cache break
---

# Disable Attribution Headers to Preserve KV Cache in Local Inference

> When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference — disable it via `~/.claude/settings.json`.

## How KV Caching Works in Local Inference

Local inference servers like llama.cpp maintain a key-value (KV) cache of previously computed attention states. When a new request shares the same prefix as a previous one, the server skips recomputation for all cached prefix tokens and processes only the new suffix. This is the same prefix-matching mechanism that cloud providers use for [prompt caching](static-content-first-caching.md), but applied at the local serving layer.

The cache depends on an exact token-for-token prefix match. Any change to the beginning of the prompt — even a single inserted token — invalidates the entire cache and forces full recomputation.

## How the Attribution Header Breaks This

Claude Code prepends an attribution header to every prompt sent to the inference server. Because this header is added at the start of the prompt, it shifts all subsequent tokens. If the header content varies between requests (or differs from what was cached), the KV cache sees a different prefix and discards all cached key-value pairs. The result is a [~90% inference slowdown](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code) because every request recomputes from scratch.

This is a specific instance of the general prefix mutation problem described in [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md) — any tool that modifies the beginning of a prompt will break prefix-based caching.

## The Fix

Set `CLAUDE_CODE_ATTRIBUTION_HEADER` to `0` in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

The setting must be in `settings.json`. Using `export CLAUDE_CODE_ATTRIBUTION_HEADER=0` in the shell [does not work](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code) — Claude Code reads this value from its own configuration, not from shell environment variables.

## Beyond Claude Code

Any tool or wrapper that injects tokens before the user's prompt will cause the same problem on any local inference server that uses KV cache prefix matching. This includes:

- **Custom proxy layers** that prepend metadata or routing headers to prompts
- **Logging middleware** that inserts request IDs or timestamps into the prompt payload
- **Multi-tenant wrappers** that add tenant-specific prefixes

The mitigation is the same in every case: ensure the prompt prefix remains identical across requests within a session, or move injected metadata out of the prompt body entirely (e.g., into HTTP headers or separate API fields).

## Affected Servers

The issue is [documented against llama.cpp](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code) (`llama-server`). Other local serving frameworks that implement KV cache prefix matching — such as vLLM and Ollama — are likely affected by the same mechanism [unverified].

## Key Takeaways

- Claude Code's attribution header prepends tokens to every prompt, breaking KV cache prefix matching in local inference servers
- Disable it by setting `CLAUDE_CODE_ATTRIBUTION_HEADER` to `0` in `~/.claude/settings.json` — shell exports do not work
- Any tool that mutates the prompt prefix will cause the same cache invalidation; keep prefixes stable across requests
- The fix is confirmed for llama.cpp; other local servers using prefix-based KV caching are likely affected

## Unverified Claims

- vLLM and Ollama are likely affected by the same KV cache invalidation mechanism [unverified]

## Related

- [Prompt Cache Economics Across Providers](prompt-cache-economics.md)
- [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md)
- [Stateless Agent Loop for Prompt Caching and Zero Data Retention](prompt-caching-architectural-discipline.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)
