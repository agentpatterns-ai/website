---
title: "Background Shell Handoff Before Subagent Cache Expiry"
term: "Background Shell Handoff Before Cache Expiry"
description: "Claude Code moves long shell commands in background subagents to the background after three minutes. Track command completion separately from cache reuse."
tags:
  - context-engineering
  - cost-performance
  - claude
applies_to: "claude-code@2.1.318"
last_reviewed: 2026-11-06
maturity: emerging
---

# Background Shell Handoff Before Subagent Cache Expiry

> Background subagents hand long shell commands back to the runtime before the default cache expires, while command completion remains pending.

Claude Code 2.1.318 moves a shell command to the background after three minutes when it runs inside a background subagent. The release note applies this change across providers and gives prompt-cache preservation as its purpose ([changelog](https://code.claude.com/docs/en/changelog#2-1-318)). It describes a command handoff, not a three-minute command timeout or a rule for every foreground agent.

## Keep the two clocks separate

The cache timer measures inactivity between matching requests. A cache hit refreshes it. Subagents normally use a five-minute cache lifetime, even when the main subscription conversation uses an hour; explicit settings can change that lifetime ([cache lifetime](https://code.claude.com/docs/en/prompt-caching#cache-lifetime)).

The command timer concerns the running process. A background subagent can leave a background shell command running beyond its turn, and Claude Code notifies it when that command ends ([background results](https://code.claude.com/docs/en/sub-agents#tools-permissions-and-results-of-background-subagents)). Returning control therefore must not be interpreted as a successful build or test.

For a completion contract, require the command's exit status and relevant result artifact. Keep dependent work pending until that evidence arrives. This is a workflow implication of the separate lifecycles, not a new runtime guarantee.

## Measure the affected cache

Inspect `cache_read_input_tokens` and `cache_creation_input_tokens` for the worker's requests. The `/usage` prompt-cache summary explicitly describes the main conversation, so it cannot by itself establish a worker's hit rate ([cache diagnostics](https://code.claude.com/docs/en/prompt-caching#check-cache-performance)).

Compare a representative long command before and after a runtime upgrade with the same model and context. Record elapsed time, completion status, and cache creation. A cache-friendly handoff does not guarantee a hit if the next request changes the prefix or arrives after expiry.

Avoid splitting a job into fresh workers solely to shorten shell waits. A non-fork subagent starts its own cache; a resumed worker can reuse a still-valid prefix ([subagents and caching](https://code.claude.com/docs/en/prompt-caching#subagents-and-the-cache)). Split when task independence justifies it, then measure the added context cost.

## Key Takeaways

- Distinguish shell completion from the handoff at three minutes.
- Use worker request counters when evaluating worker cache savings.
- Compare continuation with fresh dispatch before redesigning a long job.

## Related

- [Prompt Cache Keepalive for Agent Pauses](prompt-cache-keepalive-agent-pauses.md) — explicit refresh requests and their cost
- [Prompt Caching Architectural Discipline](prompt-caching-architectural-discipline.md) — prefix stability and cache lifetime
- [Cache-Safe Routing Boundaries](../patterns/agent-design/cache-safe-routing-boundaries.md) — model changes and cache reuse
