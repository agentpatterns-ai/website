---
title: "Mask Tools Instead of Removing Them"
term: "Tool Masking"
description: "Restrict which tools an agent may call through a per-request field rather than by editing the tools array, so a changing action space costs no cache write, and the conditions under which removing them is still cheaper."
aliases:
  - mask don't remove
  - tool availability masking
  - allowed_tools gating
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-23
maturity: emerging
---

# Mask Tools Instead of Removing Them

> Masking which tools an agent may call leaves the declared tool definitions untouched, so the cached prefix survives a change in the action space.

Two separate levers control what an agent can do. The `tools` array declares which tools exist, and a per-request control decides which of them the model may call on this turn. Only the first one is part of the cached prefix. Move the variation onto the second lever and an agent whose available tools change every turn pays no cache write for the change.

Varying the first lever is the reflex, and it is the expensive one. Manus calls a dynamic action space "a natural reaction", tried it, and settled on the opposite rule: "unless absolutely necessary, avoid dynamically adding or removing tools mid-iteration" ([Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)).

## When masking is the right lever

Masking pays when three things hold at once:

- The declared set is small enough to keep resident every turn. Anthropic puts the threshold for reaching for deferred loading at "tool definitions consuming >10K tokens" ([Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).
- Availability changes often, per turn or per model state rather than once or twice a session.
- Your provider exposes a callability control that is not part of the prompt.

Miss the first two and removal is the better trade. An agent with three phases and a large library crosses two boundaries a session, so it writes the cache twice and carries a short, clean tool list through every turn in between. That beats carrying every phase's tools through all of them.

## Why it works

The cached unit is the rendered prefix as bytes, and tool definitions render near the front of it. OpenAI states both halves of that: "Cache reuse requires the entire rendered prefix to match. If content or a relevant setting changes before a breakpoint, the prefix after that change cannot match the existing cache entry", and its table of cache-affecting settings attributes invalidation to `tools` for "tool names, descriptions, schemas, ordering, or tool-specific instructions" ([OpenAI prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)). Manus reached the same conclusion from its own experiments: "In most LLMs, tool definitions live near the front of the context after serialization, typically before or after the system prompt. So any change will invalidate the KV-cache for all subsequent actions and observations" ([Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)).

Callability is enforced somewhere else entirely: in a per-request field the provider reads, or in a logit mask applied while decoding. Neither renders into the prompt. That same OpenAI settings table is the evidence by omission. It names `model`, `tools`, `parallel_tool_calls`, `text.format`, `reasoning.effort`, `text.verbosity` and `context_management`, and neither `tool_choice` nor `allowed_tools` appears in it.

A second reason has nothing to do with cost. Removing a tool does not remove the calls to it already sitting in the conversation. Manus reports that when "previous actions and observations still refer to tools that are no longer defined in the current context, the model gets confused", and that without constrained decoding this "often leads to schema violations or hallucinated actions".

## The controls

OpenAI's prompt caching guide groups three of these under "Manage tools with append-only updates":

| Goal | Control | What stays fixed |
|---|---|---|
| No tool use this turn | `tool_choice: "none"` | The whole `tools` array |
| Only a subset callable | `allowed_tools` | The supplied `tools` list |
| Add capability mid-thread | Tool search with `defer_loading: true` | Everything before the append point |

The guide presents the first two as substitutes for editing the array: set `tool_choice` to `"none"` "instead of removing the tool definitions", and use `allowed_tools` "to restrict which tools are callable while keeping the supplied `tools` list stable". Cache preservation is the stated reason `allowed_tools` exists, for when "you want to make only a subset of tools available across model requests, but not modify the list of tools you pass in, so you can maximize savings from prompt caching" ([Function calling](https://developers.openai.com/api/docs/guides/function-calling)). The third row covers what masking does not, since deferred tools get appended at the end of context rather than inserted at the front.

Self-hosted stacks get finer resolution. Manus prefills the assistant turn up to a chosen point so the model must begin its reply inside a named group, and gives related tools a shared name prefix so `browser_` or `shell_` selects a group "without using stateful logits processors".

## When this backfires

Masking preserves the cache and preserves the distractor load. Every definition you mask is still rendered, still attended to, and still billed on every turn.

- Large libraries. Anthropic measured a 50-plus MCP tool configuration at roughly 72K tokens of definitions loaded upfront, against about 8.7K of total context once the same library is discovered on demand, and reports that "Opus 4 improved from 49% to 74%, and Opus 4.5 improved from 79.5% to 88.1% with Tool Search Tool enabled" ([Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)). Masking locks in the worse number on both counts.
- Crowded shortlists, even small ones. Over-presentation costs choice accuracy on its own: "When the gold tool is present, Claude selects it 93.1±0.5% of the time under BoR (K=2.2) but only 87.1% under FK=5, a gap of 6 percentage points" ([arXiv:2605.24660v2](https://arxiv.org/abs/2605.24660v2)).
- Phase-shaped availability. Two cache writes a session is a small bill. Paying every phase's definition tokens on every turn of every phase is not.
- Single-turn or cold-start traffic. No accumulated prefix exists to protect, so declaring tools you will not allow buys nothing.
- No per-request control. If the framework's only lever is the `tools` array, masking is unavailable, and the prefill route needs control over decoding that a hosted API does not hand you.
- Access control. A mask constrains sampling, and a schema-violating completion can still name a tool the mask was meant to rule out. A tool that must be unreachable should not be declared at all (see [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md)).

Manus concedes the first two in the same section that recommends masking: "your heavily armed agent gets dumber."

## Example

The anti-pattern rebuilds the array, so the front of the prompt changes and everything after it misses:

```python
# BAD: the declared set changes per phase, so the prefix changes too
tools = PLANNING_TOOLS if phase == "plan" else EXECUTION_TOOLS
response = client.responses.create(
    model="gpt-6",
    tools=tools,            # names, order and schemas all move -> cache write
    input=history,
)
```

The fix declares everything once and gates callability per request:

```python
ALL_TOOLS = load_all_tools()          # identical bytes on every call
PHASE_TOOLS = {
    "plan": ["read_file", "search_repo"],
    "execute": ["read_file", "write_file", "run_tests"],
}

response = client.responses.create(
    model="gpt-6",
    tools=ALL_TOOLS,                  # never changes -> prefix keeps matching
    tool_choice={
        "type": "allowed_tools",
        "mode": "auto",
        "tools": [{"type": "function", "name": n} for n in PHASE_TOOLS[phase]],
    },
    input=history,
)
```

Check the result rather than trusting the change. Cached-token reporting should stay high across a phase boundary; a read that collapses on the turn the phase changes means something in the declaration moved after all, and non-deterministic JSON key ordering is the usual culprit.

## Key Takeaways

- Declaration and availability are different layers. Put session-varying behavior on the availability layer, where the provider reads it as a field instead of rendering it into the prompt.
- Confirm your chosen control is absent from the provider's list of cache-affecting settings before relying on it. OpenAI's list names `tools` and omits `tool_choice` and `allowed_tools`; a provider that folds availability into the prompt gives you no saving.
- Masking buys back the cache write and nothing else. The definitions still cost tokens every turn and still compete for the model's attention, which is a 6-point accuracy gap in one measurement and 25 points in another.
- Count how often availability actually changes. Per-turn variation favors masking; two phase boundaries a session favors removing the tools and paying the two writes.
- Never use a mask where you mean a permission. It constrains sampling, not access.

## Related

- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — the prefix rules this technique works within, and the cross-provider cache economics
- [Dynamic Tool Fetching Destroys KV Cache Performance](../patterns/anti-patterns/dynamic-tool-fetching-cache-break.md) — the failure this avoids, and deferred loading as the other remedy
- [Advanced Tool Use: Scaling Agent Tool Libraries](../tool-engineering/advanced-tool-use.md) — the deferred-loading route to take when the library is too large to keep resident
- [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md) — why a sampling-time constraint is not a permission boundary
- [Structure Prompts with Static Content First to Maximize Cache Hits](static-content-first-caching.md) — the prefix layout this depends on
