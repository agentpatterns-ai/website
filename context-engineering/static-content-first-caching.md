---
title: "Structure Prompts with Static Content First to Maximize Cache Hits"
description: "Place static prompt content first and variable content last to maximize prompt cache hits and reduce inference costs in agent loops."
aliases:
  - "prompt prefix caching"
  - "cache-friendly prompt ordering"
tags:
  - context-engineering
  - cost-performance
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# Structure Prompts with Static Content First to Maximize Cache Hits

> Place static content (instructions, tool definitions) at the prompt's start and variable content last to maximize cache hits and keep inference cost linear.

## Why Prompt Structure Affects Cost

Without prompt caching, the cost of running an agent loop is quadratic: each new inference call re-sends the entire accumulated context. An agent that makes 50 tool calls in a session sends the entire history 50 times — each call includes all preceding content.

Prompt caching addresses this by reusing cached prefixes from previous calls. [OpenAI's Codex CLI](https://openai.com/index/unrolling-the-codex-agent-loop/) structures its prompt explicitly to exploit this: static content (model instructions, sandbox configuration, tool definitions) forms an exact prefix that never changes during a conversation. Only the dynamic suffix (user messages, tool results) changes per call.

When the static prefix is an exact match to a cached prefix, the provider recomputes only the dynamic suffix — reducing sampling cost to linear in the number of new tokens per call, not linear in total context size.

## What Goes Where

| Content Type | Position | Why |
|--------------|----------|-----|
| System instructions | Start of prompt | Static, changes rarely |
| Tool schemas and definitions | After instructions | Static per session |
| Examples or few-shot samples | After tool schemas | Static per session |
| User messages | After static section | Variable per call |
| Tool results | After user messages | Variable per call |
| New agent turn | End of prompt | Variable per call |

## What Breaks Cache Hits

Prompt caching requires exact prefix matches. Common cache-busting mistakes include:

**Non-deterministic tool enumeration**: [OpenAI identified a bug in Codex](https://openai.com/index/unrolling-the-codex-agent-loop/) where [MCP](../standards/mcp-protocol.md) tools were listed in non-deterministic order, causing a cache miss on every call because the tool list prefix was never the same twice. Tool definitions must be enumerated in a consistent, deterministic order.

**Model switching**: Codex injects model-specific instructions early in the prompt. Changing the target model mid-conversation busts the cache because the injected instructions are different. If you need to switch models, treat it as a context boundary.

**Prefix mutation**: Any change to content earlier in the prompt than the current turn [invalidates the cache](kv-cache-invalidation-local-inference.md) for everything after it. Even reordering two static sections that produce identical content will bust the cache if the character sequences differ.

**Stateless vs stateful**: Some implementations send the full conversation history on every call rather than referencing a conversation ID. Full resend keeps all content available for caching but incurs quadratic network traffic. Referencing a `previous_response_id` reduces network traffic but loses the caching opportunity for historical content.

## Tradeoffs

Optimizing for cache hits requires discipline in prompt construction:

- Tool definitions must be locked into a deterministic order and not mutated during a session
- System instructions cannot be personalized per-call (any change busts the prefix cache)
- The split between static and dynamic sections must be maintained as the harness evolves

For short agent sessions (5–10 tool calls), the cache optimization may not be worth the engineering overhead. For long-running sessions or high-volume production loops, [cache reads cost 10% of base input token price](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), and empirical studies on agentic workloads report 41–80% total cost reductions across providers ([Don't Break the Cache, 2026](https://arxiv.org/abs/2601.06007)).

Static-first ordering is necessary but not sufficient. The same study finds that naive full-context caching — caching everything, including volatile tool results — can *paradoxically increase latency*; strategic cache-block control that excludes dynamic tool results and places variable content deliberately delivers more consistent gains ([Don't Break the Cache, 2026](https://arxiv.org/abs/2601.06007)). Order the prefix static-first, then be selective about which dynamic blocks you cache at all.

## Implementation Checklist

- [ ] System instructions and tool schemas are assembled before any user or agent content
- [ ] Tool definitions are enumerated in a deterministic, consistent order
- [ ] No model-specific content is injected mid-conversation
- [ ] Static content sections are never mutated within a session
- [ ] Cache hit rates are monitored in production to detect regressions

## Example

A minimal [agent harness](../agent-design/agent-harness.md) in Python illustrating static-first prompt assembly. The system prompt and tool definitions are built once and reused across every turn; only the conversation history grows.

**Before** — tool list rebuilt on every call (cache miss every turn):

```python
def call_model(conversation_history, user_message):
    tools = load_tools_from_registry()  # re-fetched each call, order varies
    system = build_system_prompt(user=current_user)  # personalized, busts cache

    return client.messages.create(
        model="claude-opus-4-5",
        system=system,
        tools=tools,
        messages=conversation_history + [{"role": "user", "content": user_message}],
    )
```

**After** — static prefix fixed at session start, variable suffix appended:

```python
# Built once per session — stable cache prefix
TOOLS = sorted(load_tools_from_registry(), key=lambda t: t["name"])
SYSTEM = build_system_prompt()  # no per-user injection

def call_model(conversation_history, user_message):
    return client.messages.create(
        model="claude-opus-4-5",
        system=SYSTEM,          # identical bytes every call → cache hit
        tools=TOOLS,            # deterministic order → cache hit
        messages=conversation_history + [{"role": "user", "content": user_message}],
    )
```

The key changes: tools sorted by name (deterministic order), system prompt built without per-call personalization, and both constructed once outside the call loop so the prefix bytes are identical across turns.

## Key Takeaways

- Static content first, variable content last — exact prefix matches are required for cache hits.
- Non-deterministic tool ordering is a common cache-busting bug; sort tool definitions consistently.
- Switching models mid-session busts the cache because model-specific instructions are injected early.
- Any change to a prefix segment invalidates the cache for all content after it, so [prefix discipline](prompt-caching-architectural-discipline.md) must hold across the session.
- For high-volume or long-running agents, this optimization can reduce inference costs from quadratic to linear.

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md)
- [KV Cache Invalidation in Local Inference](kv-cache-invalidation-local-inference.md)
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md)
- [Context Compression Strategies](context-compression-strategies.md)
- [Stateful Iteration State-Carry](stateful-iteration-state-carry.md) — the application-tier complement: when loops are long and observations large, lifting state out of the transcript beats caching on its own
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
