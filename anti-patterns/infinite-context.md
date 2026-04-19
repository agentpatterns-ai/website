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

Attention is finite even when the context window is not. Anthropic's context engineering guide calls this "context rot" — recall and use of information degrades as token count grows ([Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Symptoms: the agent ignores instructions that worked at shorter prompt lengths, produces generic outputs, or loses constraints stated early in the conversation.

Irrelevant context adds noise that competes with signal. The Anthropic guide recommends identifying "the smallest possible set of high-signal tokens that maximize the likelihood of your desired outcome" rather than maximising volume ([Anthropic, 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## Common Causes

- Preloading entire documentation sites "just in case" an agent needs them
- Including every file in the repository when only two are relevant to the task
- Keeping raw tool results in context after they have been processed
- Accumulating a long conversation history without compaction
- Adding `@workspace` or equivalent full-codebase context to every prompt

## Remediation

Replace volume with precision:

- **Load on-demand**: fetch reference material when the task requires it, not at startup
- **Use skill descriptions**: expose tool metadata; load full content only when the agent invokes the skill
- **Compact conversation history**: summarise prior turns rather than accumulating them
- **Isolate with sub-agents**: delegate retrieval-heavy subtasks to isolated windows; the coordinator receives only the compressed result
- **Prune tool results**: store large outputs externally and pass the agent a summary plus a retrieval path

LangChain's Deep Agents applies tiered compression — offloading large results, truncating older tool calls, summarising history — in sequence as pressure rises ([LangChain, 2025](https://blog.langchain.com/context-management-for-deepagents/)).

## Mechanism

Transformer attention computes relevance scores between every token in the context. As length grows, the signal-to-noise ratio drops: relevant tokens compete with more irrelevant ones for a fixed attention budget. Models exhibit a "lost in the middle" effect — tokens at the start and end are retrieved reliably, while middle tokens receive less attention ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)). Irrelevant content is not inert; it displaces attention from relevant tokens.

## When This Backfires

Loading more context is not always wrong. The remediation loses to the anti-pattern under specific conditions:

- **Retrieval is unreliable**: when semantic search has poor recall over a large space, loading directly may outperform RAG with high miss rates.
- **Latency budget is tight**: on-demand retrieval adds round-trip overhead. If latency matters more than accuracy, preloading reduces tool calls.
- **Context is truly homogeneous**: a task that genuinely needs every file (e.g., whole-repo rename) has no irrelevant content to exclude.
- **Sub-agent overhead is prohibitive**: isolated windows add orchestration cost and failure modes; for short tasks, a single larger context is cheaper.

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
- [Context Window Management: The Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Manual Compaction as Dumb Zone Mitigation](../context-engineering/manual-compaction-dumb-zone-mitigation.md)
- [Context Poisoning](context-poisoning.md)
- [Distractor Interference](distractor-interference.md)
- [Session Partitioning](session-partitioning.md)
