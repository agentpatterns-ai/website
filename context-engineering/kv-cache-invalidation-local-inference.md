---
title: "Disable Attribution Headers to Preserve KV Cache in Local Inference"
term: "Disable Attribution Headers to Preserve KV Cache"
description: "When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference"
tags:
  - cost-performance
  - tool-agnostic
  - context-engineering
aliases:
  - KV cache invalidation
  - attribution header cache break
last_reviewed: 2026-05-27
maturity: established
---

# Disable Attribution Headers to Preserve KV Cache in Local Inference

> When Claude Code prepends an attribution header to prompts sent to local models, it invalidates the KV cache on every request and causes ~90% slower inference — disable it via `~/.claude/settings.json`.

## How KV caching works in local inference

Local inference servers like llama.cpp keep a key-value (KV) cache of attention states they have already computed. When a new request shares the same prefix as an earlier one, the server reuses every cached prefix token and processes only the new suffix. This is the same prefix-matching mechanism cloud providers use for [prompt caching](static-content-first-caching.md), applied at the local serving layer.

The cache depends on an exact token-for-token prefix match. Any change to the start of the prompt, even a single inserted token, invalidates the whole cache and forces a full recomputation.

## How the attribution header breaks this

Claude Code prepends an attribution header to every prompt it sends to the inference server. Because the header sits at the start of the prompt, it shifts every token after it. If the header content varies between requests, or differs from what was cached, the KV cache sees a different prefix and discards all cached key-value pairs. Every request then recomputes from scratch, which causes a [~90% inference slowdown](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code).

This is one case of the general prefix-mutation problem described in [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md). Any tool that changes the start of a prompt will break prefix-based caching.

## The fix

Set `CLAUDE_CODE_ATTRIBUTION_HEADER` to `0` in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

The setting must live in `settings.json`. Using `export CLAUDE_CODE_ATTRIBUTION_HEADER=0` in the shell [does not work](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code), because Claude Code reads this value from its own configuration, not from shell environment variables.

## Beyond Claude Code

Any tool or wrapper that injects tokens before the user's prompt causes the same problem on any local inference server that uses KV cache prefix matching. This includes:

- custom proxy layers that prepend metadata or routing headers to prompts
- logging middleware that inserts request IDs or timestamps into the prompt payload
- multi-tenant wrappers that add tenant-specific prefixes

The fix is the same in every case. Keep the prompt prefix identical across requests within a session, or move injected metadata out of the prompt body entirely, for example into HTTP headers or separate API fields.

## Affected servers

The issue is [documented against llama.cpp](https://unsloth.ai/docs/basics/claude-code#fixing-90-slower-inference-in-claude-code) (`llama-server`). Other local serving frameworks that implement KV cache prefix matching show the same invalidation for the same structural reason: a mutated prompt prefix produces a different token hash, which misses the cache entirely. This includes [vLLM's automatic prefix caching](https://docs.vllm.ai/en/latest/features/prefix_caching.html) (enabled with `--enable-prefix-caching`) and Ollama, which uses llama.cpp as its backend and inherits its cache behavior.

## When this backfires

Disabling the attribution header makes sense when KV cache hit rate matters more than request traceability. Leave attribution enabled in three cases:

- multi-tenant or audited environments, where the header identifies which tool or user issued the request; removing it loses that signal for logging and compliance
- debugging tool-level issues, where attribution lets you tell Claude Code or a proxy apart from other callers while you diagnose unexpected behavior
- single-request benchmarks, where the workload is single-shot (no repeated prefix, no session context), so the cache gives no benefit and disabling attribution trades nothing useful

If any of these apply, move attribution data out of the prompt body and into HTTP request headers or a separate metadata field rather than removing it entirely.

## Key Takeaways

- Claude Code's attribution header prepends tokens to every prompt, breaking KV cache prefix matching in local inference servers
- Disable it by setting `CLAUDE_CODE_ATTRIBUTION_HEADER` to `0` in `~/.claude/settings.json` — shell exports do not work
- Any tool that mutates the prompt prefix will cause the same cache invalidation; keep prefixes stable across requests
- The fix is confirmed for llama.cpp; vLLM and Ollama-backed servers will be affected by the same mechanism because all use hash-based prefix matching

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md)
- [Static Content First: Maximizing Prompt Cache Hits](static-content-first-caching.md)
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)
