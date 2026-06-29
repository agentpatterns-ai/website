---
title: "Dynamic Tool Fetching Destroys KV Cache Performance"
description: "Loading tool definitions dynamically per step seems like good context management but destroys the most impactful cost optimization available: prompt caching."
tags:
  - cost-performance
  - context-engineering
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-05-27
maturity: established
---

# Dynamic Tool Fetching Breaks KV Cache

> Loading tool definitions dynamically per step seems like good context management but destroys the single most impactful cost optimization available: prompt caching.

## The intuition trap

Fewer tools means fewer tokens, so fetching only the needed tools per step seems best. It is not. The savings from removing tools are far smaller than the cost of breaking prompt cache continuity.

## Why it fails

Tool definitions sit at the top of the cache hierarchy. The model computes the prefix in order: `tools` → `system` → `messages`. Any change to tool definitions invalidates every level below it.

```mermaid
graph LR
    A["tools (top)"] --> B["system"] --> C["messages"]
    style A fill:#d32f2f,color:#fff
    style B fill:#f57c00,color:#fff
    style C fill:#fbc02d,color:#000
```

Cached tokens cost 10 times less than uncached. Claude Sonnet 4's cache-read rate is $0.30/MTok against a $3/MTok base input ([Anthropic prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). A single cache break per turn erases all savings from fewer tools.

| Approach | Tools in context | Cache hit rate | Effective cost |
|---|---|---|---|
| Stable tool set (30 tools) | 30 every turn | High | Low |
| Dynamic RAG per step | 5-15, varying | Near zero | High |
| Deferred loading (stable prefix) | 8-10 core + search | High | Lowest |

## The subtle variant: non-deterministic serialization

Languages like Swift and Go randomize dictionary key ordering during JSON serialization. So the cache sees a different byte sequence even when the tools are identical. This triggers the same anti-pattern by accident.

Fix: sort the keys deterministically before serialization.

## The correct alternative: deferred tool loading

Anthropic's [Tool Search Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) reaches the same goal without breaking the cache prefix. Tools marked `defer_loading: true` stay out of the prompt, and the agent discovers them on demand.

Anthropic's [evaluations](https://www.anthropic.com/engineering/advanced-tool-use):

| Metric | All tools loaded | Deferred + search |
|---|---|---|
| Token usage | ~55K | ~8.7K |
| Accuracy (Opus) | 49% | 74% |

The cache prefix stays identical across turns. Deferred tools load into message history, so they invalidate nothing.

## Recommended tool architecture

Anthropic's [advanced tool use guidance](https://www.anthropic.com/engineering/advanced-tool-use) recommends grouping tools by how often you use them:

| Level | Contents | Cache impact |
|---|---|---|
| Core tools (3–5) | Most-used, always loaded | Cached prefix, never changes |
| General utilities | bash, code execution | Part of stable prefix |
| Specialized tools | Domain-specific, MCP servers | Deferred; loaded via search on demand |

## When this backfires

Deferred loading adds a tool search round-trip for each undiscovered tool. It gives no benefit when:

- Tool library is small (under 10 tools): upfront loading costs less than the repeated search overhead.
- All tools are needed every request: deferring tools you always use forces a search penalty with no savings.
- Latency is the main constraint: real-time pipelines may not tolerate extra inference passes for tool discovery.
- Tool search accuracy is low: poor search hits miss tools, and that hurts task completion more than cache breaks cost.

## When this does not apply

Stable tool sets are the right default for multi-turn agents. In a few cases, dynamic selection is fine:

- Single-turn, cold-start requests: when every call is a fresh session with no prior cache, there is no accumulated prefix to protect. Cache continuity only pays off across turns.
- Local inference without a shared KV cache: some self-hosted backends, for example llama.cpp and Ollama, do not reuse the KV cache across requests. The 10-times cost gap disappears.
- Very small tool sets (under 5 tools, under 500 tokens total): when tool definitions are tiny next to the message history, the savings from cache hits may not justify a deferred-loading architecture.

In all other cases — multi-turn agents, API-hosted models, or any setup with repeated context — the cost gap dominates and dynamic per-step fetching works against you.

## Key Takeaways

- Any change to tool definitions invalidates the entire KV cache — continuity matters more than minimizing tool count.
- Prefer deferred loading with a stable core set over dynamic RAG on tool definitions.
- Audit JSON serialization for non-deterministic key ordering — an accidental cache-breaker.

## Example

Anti-pattern — tool definitions change each turn, breaking the cache:

```python
# BAD: tool list rebuilt per step — cache prefix changes every call
for step in plan:
    tools = fetch_tools_for_step(step)          # different subset each time
    response = client.messages.create(
        model="claude-sonnet-4-5",
        tools=tools,                             # cache invalidated every turn
        messages=history,
    )
```

Fix — stable core tools, deferred discovery via Tool Search:

```python
# GOOD: stable prefix; agent discovers specialized tools on demand
CORE_TOOLS = load_core_tools()                  # same every call

response = client.messages.create(
    model="claude-sonnet-4-5",
    tools=CORE_TOOLS,                           # never changes → cache hits
    messages=history,
)
# Specialized tools are fetched inside message history via Tool Search Tool,
# invalidating nothing above the messages layer.
```

Sorting tool keys deterministically also prevents accidental cache breaks in languages with non-deterministic dict ordering:

```python
import json

def stable_tool_schema(tool: dict) -> dict:
    return json.loads(json.dumps(tool, sort_keys=True))

CORE_TOOLS = [stable_tool_schema(t) for t in load_core_tools()]
```

## Related

- [Prompt Caching as Architectural Discipline](../context-engineering/prompt-caching-architectural-discipline.md)
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md)
- [Tool Minimalism](../tool-engineering/tool-minimalism.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](../tool-engineering/advanced-tool-use.md) — full documentation of deferred tool loading and the Tool Search Tool
- [Infinite Context Anti-Pattern](infinite-context.md)
- [Token Preservation Backfire](token-preservation-backfire.md)
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Context Engineering](../context-engineering/context-engineering.md)
- [Static Content First: Maximizing Prompt Cache Hits](../context-engineering/static-content-first-caching.md)
- [Disable Attribution Headers to Preserve KV Cache in Local Inference](../context-engineering/kv-cache-invalidation-local-inference.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
- [Filesystem-Based Tool Discovery](../tool-engineering/filesystem-tool-discovery.md)
