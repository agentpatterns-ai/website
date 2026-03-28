---
title: "The Infinite Context Anti-Pattern in Agent Systems"
description: "Preloading irrelevant context into an agent prompt dilutes attention and degrades output quality — load only the smallest set of high-signal tokens needed."
tags:
  - context-engineering
  - cost-performance
---

# The Infinite Context

> A larger context window does not produce better output — unfocused context dilutes attention and degrades performance.

## The Pattern

Load as much context as possible into the agent's prompt. Include every potentially relevant file, the full conversation history, all documentation, and complete tool results. Assume that more information cannot hurt.

## Why It Fails

Attention is finite even when the context window is not. As total tokens increase, the model's ability to attend to specific tokens degrades. Anthropic's context engineering guide describes this as "context rot" — the model's ability to recall and use information degrades as token count grows.

The symptoms are recognisable: the agent ignores instructions that were followed reliably when the prompt was shorter, produces increasingly generic outputs, or loses track of constraints stated early in the conversation.

Adding irrelevant context does not add capability — it adds noise that competes with the signal for the model's attention. The Anthropic guide recommends identifying "the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" rather than maximising context volume.

## Common Causes

- Preloading entire documentation sites "just in case" an agent needs them
- Including every file in the repository when only two are relevant to the task
- Keeping raw tool results in context after they have been processed
- Accumulating a long conversation history without compaction
- Adding `@workspace` or equivalent full-codebase context to every prompt

## Remediation

Replace volume with precision:

- **Load on-demand**: fetch reference material when the task requires it, not at startup
- **Use skill descriptions**: give the agent metadata about available tools without loading their full content; the content loads only when the agent invokes the skill
- **Compact conversation history**: when context fills, summarise prior turns rather than continuing to accumulate them
- **Isolate with sub-agents**: delegate retrieval-heavy subtasks to isolated context windows; the coordinator receives only the compressed result
- **Prune tool results**: store large tool outputs externally and provide the agent with a summary plus a path to retrieve the full content if needed

LangChain's Deep Agents implements this through tiered compression: offloading large results, truncating older tool calls, and summarising conversation history — applied in sequence as context pressure increases. [unverified]

## Example

A coding agent is tasked with fixing a single failing test in a 200-file repository. The developer pre-loads the entire codebase into context using `@workspace`, attaches all 50 previous conversation turns, and includes the full output of three `git log` commands. Total prompt: 180,000 tokens.

The agent identifies the failing test but then rewrites an unrelated module it “noticed” while scanning earlier files, ignores the test fix constraint stated at turn 1, and produces a diff that touches 12 files. When the developer rolls back and repeats the task with only the failing test file, the two directly imported modules, and a fresh session, the agent fixes the test in one turn.

The fix was not in the extra context — the extra context is why the fix failed.

## Key Takeaways

- More context does not equal better output. Attention degrades with context volume regardless of window size.
- Preloading irrelevant content for convenience is the most common cause of this anti-pattern.
- Fix by loading on-demand, compacting aggressively, and using sub-agents to isolate retrieval from reasoning.

## Related

- [Context Engineering: The Discipline of Designing Agent Context](../context-engineering/context-engineering.md)
- [Retrieval-Augmented Agent Workflows](../context-engineering/retrieval-augmented-agent-workflows.md)
- [Context Compression Strategies: Offloading and Summarisation](../context-engineering/context-compression-strategies.md)
- [Context Poisoning](context-poisoning.md)
- [Objective Drift](objective-drift.md)
- [Distractor Interference](distractor-interference.md)
- [Session Partitioning](session-partitioning.md)
- [Dynamic Tool Fetching and Cache Break](dynamic-tool-fetching-cache-break.md)
- [Context Window Management: The Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Manual Compaction as Dumb Zone Mitigation](../context-engineering/manual-compaction-dumb-zone-mitigation.md)
