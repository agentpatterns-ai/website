---
title: "Mid-Session Config Changes as Invisible Cache Invalidators"
description: "Switching model, effort, or MCP servers mid-session silently invalidates the prompt cache and re-bills the entire prefix at ~10x the cached rate."
tags:
  - cost-performance
  - context-engineering
  - anti-pattern
  - tool-agnostic
last_reviewed: 2026-05-30
---

# Mid-Session Config Changes as Invisible Cache Invalidators

> Mid-session model, effort, or MCP changes silently invalidate the prompt cache and re-bill the full prefix at ~10x.

The prompt cache is keyed by the exact prefix of each request — system prompt, tool definitions, project context, conversation history — plus the model and effort level ([Claude Code docs](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)). A change at any layer recomputes everything after it, so the next turn reads zero cache and re-bills the full prefix at the standard input rate — roughly 10x the cache-read rate ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)).

## The Invalidator Catalogue

Six actions invalidate part or all of the cache ([Claude Code §Actions that invalidate the cache](https://code.claude.com/docs/en/prompt-caching#actions-that-invalidate-the-cache)):

| Action | What invalidates | User-visible? |
|---|---|---|
| `/model` switch | Entire request — each model has its own cache | Yes, cost is not |
| `/effort` change | Entire request — each effort level has its own cache | Confirmation dialog ([§Changing effort level](https://code.claude.com/docs/en/prompt-caching#changing-effort-level)) |
| MCP server connect/disconnect | System prompt layer (tool definitions) | Often **no** — auto-reconnects happen without user action |
| Bare-name tool deny rule (`Bash`, `WebFetch`, `Bash(*)`) | System prompt layer | No |
| `/compact` | Conversation layer by design | Yes |
| Claude Code upgrade (next launch or resume) | System prompt layer | No — manifests as a slow first turn |

Model and effort are part of the cache key but not the prompt text, so they cannot be diffed by reading the conversation ([§How the cache is organized](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)).

## Why It Works

Prefix matching is exact at the API layer: "a change anywhere in the prefix recomputes everything after it. There is no per-file or per-segment caching" ([§How the cache is organized](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)). The hierarchy is cumulative — `tools → system → messages` — so a tool-definition change invalidates everything below ([Anthropic prompt-caching reference](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Claude Code orders content rarely-changing-first specifically to maximize cached-prefix length.

## The Two Silent Cases

- **MCP auto-reconnect.** Tool definitions sit in the system prompt layer, so the cache invalidates "when the set of MCP tools available to Claude changes between turns. The most common cause is an MCP server connecting or disconnecting mid-session, which can happen without any action on your part: a stdio server's process exits, an HTTP session expires, or a server reconnects automatically after a transient failure" ([§Connecting or disconnecting an MCP server](https://code.claude.com/docs/en/prompt-caching#connecting-or-disconnecting-an-mcp-server)).
- **`opusplan` plan-mode toggle.** The `opusplan` setting "resolves to Opus during plan mode and Sonnet during execution, so each plan-mode toggle is a model switch and starts a fresh cache" ([§Switching models](https://code.claude.com/docs/en/prompt-caching#switching-models)). A permission-mode change is a model switch under the hood.

## When This Backfires

The failure is *invisible cost*, not invalidation per se. Mid-session changes are reasonable when:

- **Short sessions (<5 turns)** — the prefix is too small for a miss to matter.
- **Deliberate mid-task escalation** — switching to a stronger model for one hard step, cost weighed.
- **Subscription users well inside plan cap** — the dollar cost is absorbed; only latency moves ([§Cache lifetime](https://code.claude.com/docs/en/prompt-caching#cache-lifetime)).
- **Local inference without shared KV cache** (Ollama, llama.cpp) — no cross-request cache to invalidate ([Disable Attribution Headers to Preserve KV Cache in Local Inference](../context-engineering/kv-cache-invalidation-local-inference.md)).
- **Gateways or `ANTHROPIC_BASE_URL` deployments where caching is unsupported** — invalidation is moot ([§Where the cache lives](https://code.claude.com/docs/en/prompt-caching#where-the-cache-lives)).

Several changes commonly assumed to invalidate do **not** — over-correcting is also wrong: editing `CLAUDE.md` mid-session ([§Editing CLAUDE.md mid-session](https://code.claude.com/docs/en/prompt-caching#editing-claude-md-mid-session)), changing output style ([§Changing output style](https://code.claude.com/docs/en/prompt-caching#changing-output-style)), switching permission mode without `opusplan` ([§Changing permission mode](https://code.claude.com/docs/en/prompt-caching#changing-permission-mode)), invoking skills or slash commands, running `/recap`, `/rewind`, or spawning a subagent ([§Actions that keep the cache](https://code.claude.com/docs/en/prompt-caching#actions-that-keep-the-cache)).

## Cache-Preserving Alternatives

- `/rewind` truncates to an earlier turn — "the next request hits the earlier cache entry" ([§Rewinding the conversation](https://code.claude.com/docs/en/prompt-caching#rewinding-the-conversation)). Prefer it over `/compact` to abandon a path.
- `/recap` "appends the summary as command output rather than replacing your message history, so the cached prefix stays intact" ([§Running /recap](https://code.claude.com/docs/en/prompt-caching#running-recap)). Prefer it over `/compact` to surface a summary.

The rule of thumb from the primary docs: "Pick your model, effort level, and MCP servers at the top of a session, then save `/compact` for natural breaks between tasks" ([§How the cache is organized](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)).

## Example

**Before — invisible cache miss from mid-task model switch:**

```text
[turn 12 of long debugging session, ~80K cached prefix]
> /model opus
> "Try the harder approach now"
[next turn: 0 cache reads, 80K cache writes at standard input rate ≈ 10x the cost of the prior turn]
```

**After — pick the model at session start, escalate by spawning a subagent:**

```text
[session start]
> /model sonnet
[80K prefix builds up across turns 1-12, fully cached]
> "Spawn a subagent on Opus for the harder approach"
[parent's cache stays warm; subagent builds its own cache from scratch with no parent re-bill]
```

A subagent "starts its own conversation with its own system prompt and tool set, separate from the parent's. It builds its own cache, starting with no cache hits on its first call" ([§Subagents and the cache](https://code.claude.com/docs/en/prompt-caching#subagents-and-the-cache)). The parent's prefix is untouched.

## Key Takeaways

- The cache is keyed by exact prefix plus model and effort — any change to either invalidates everything after.
- Two invalidators are silent: MCP auto-reconnects, and `opusplan` plan-mode toggles (which are model switches).
- Editing `CLAUDE.md`, changing output style, swapping permission modes (without `opusplan`), and invoking skills/commands are all cache-safe — don't over-correct.
- Prefer `/rewind` over `/compact` to abandon a path; `/recap` over `/compact` to surface a summary. Both preserve the prefix.

## Related

- [Dynamic Tool Fetching Breaks KV Cache](dynamic-tool-fetching-cache-break.md) — the tool-list-rebuild variant of the same prefix-invalidation failure.
- [Prompt Cache Economics Across Providers](../context-engineering/prompt-cache-economics.md) — the cost asymmetry (cache reads at ~10% of standard input) that makes invalidation expensive.
- [Structure Prompts with Static Content First to Maximize Cache Hits](../context-engineering/static-content-first-caching.md) — the layering discipline this anti-pattern undermines.
- [Extended Prompt Cache TTL for Long Agent Sessions](../context-engineering/extended-prompt-cache-ttl.md) — when to opt into the 1-hour TTL so the prefix survives idle gaps.
- [Disable Attribution Headers to Preserve KV Cache in Local Inference](../context-engineering/kv-cache-invalidation-local-inference.md) — the local-inference variant where prefix invalidation has a different root cause.
