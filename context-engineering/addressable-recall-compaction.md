---
title: "Addressable Recall Compaction: Compact to Citations, Not Summaries"
term: "Addressable Recall Compaction"
description: "Store every tool observation verbatim under a stable ID, show a short citation once context fills, and let the agent dereference the exact record instead of a summary or a similarity match."
aliases:
  - addressable recall compaction
  - citation stub compaction
  - address-based context recall
tags:
  - context-engineering
  - tool-agnostic
  - pattern
  - arxiv
last_reviewed: 2026-07-30
maturity: emerging
---

# Addressable Recall Compaction: Compact to Citations, Not Summaries

> Compaction replaces older tool observations with short citations the agent can dereference by ID, so the exact bytes stay recoverable without re-running the tool.

Reach for addressable recall when your agent loses specific details it already saw. Keep every tool observation verbatim in an append-only store keyed by a stable identifier. When the window fills, swap the observation in the transcript for a compact citation and let the agent ask for the record back by ID. [Summarization and masking](context-compression-strategies.md) make the loss permanent; addressing makes it reversible.

Addressable Recall Compaction (ARC), the named form of this pattern, backs a narrow claim: it scored 99.00% exact-answer accuracy on a needle-in-a-haystack task against 79.57% for a similarity-retrieval baseline, running Qwen3-8B at a 16k window. On the LongBench-v2 hard subset, which needs synthesis rather than lookup, that same 8B setup scored 27.47% against 25.83% ([Dang et al., arxiv 2607.25066](https://arxiv.org/abs/2607.25066v1)). Treat the Qwen3 figures as the shape of the effect, not a claim about frontier models — the authors scope their evaluation to that family.

## What the citation carries

A citation is a pointer plus enough surface for the agent to decide whether to follow it. ARC computes the identifier as a hash of the action signature and the observation, then stores the record without ever overwriting or deleting it ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066)).

| Element | Purpose |
|---------|---------|
| Stable identifier | Resolves to exactly one record, so recovery skips ranking |
| Head and tail preview | Lets the agent answer from the stub when the preview is enough |
| Length and type metadata | Signals what a recall would cost before paying for it |
| Recall hint | Names the action that fetches the full record |

Because recall is not free, ARC bounds it deliberately: it caps recalls per step, caps the total materialized recall budget, caps each recall's length, and evicts least-recently-used recalled bodies back to stubs when a budget is exceeded ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066)).

## Why it works

Compaction loss is a presentation problem that harnesses treat as a storage problem. The observation is only missing from the transcript, so an external store makes the loss reversible. Manus states the reason plainly: an agent "must predict the next action based on all prior state—and you can't reliably predict which observation might become critical ten steps later. From a logical standpoint, any irreversible compression carries risk" ([Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)).

The second half is exactness. An identifier resolves to one record, so recovery never passes through an embedding ranker that can push the needed record below the cut. That is what the 19-point needle-in-a-haystack gap over similarity retrieval measures ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066)). Anthropic describes the same idea as holding "lightweight identifiers (file paths, stored queries, web links, etc.)" and loading data through them at runtime ([Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## When this backfires

- Reasoning-bound tasks. The margin falls from 19 points on verbatim recall to under 2 points on LongBench-v2 hard, because perfect recall still permits faulty reasoning ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066)).
- Tight recall budgets. At the smallest ablated budget ARC scored 26.05% against a structured-state baseline's 27.01% on Qwen3-8B — stub overhead consumed the budget it was meant to protect ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066v1)).
- Models that never call recall. StructMemEval found agents handle structured memory reliably only when explicitly instructed, and "do not always recognize the memory structure when not prompted to do so" ([arxiv 2602.11243](https://arxiv.org/abs/2602.11243)). Unprompted, the store becomes write-only.
- Latency-sensitive loops. Every dereference is another turn and another inference. Anthropic notes that just-in-time loading is slower than pre-processing data up front ([Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Dialogue-shaped history. Similarity retrieval sometimes wins there, and the ARC authors describe explicit and implicit recall as complementary rather than competing ([arxiv 2607.25066](https://arxiv.org/abs/2607.25066)).

The case against the pattern is worth holding onto: if your agent fails through attention dilution rather than detail loss, a summary fixes that and a citation does not, while the stubs, the extra turns, and the storage backend all still cost you.

## Example

The Strands Agents SDK ships this pattern as its `ContextOffloader` plugin. Any tool result over `max_result_tokens` (default 2,500) is stored externally and replaced in the conversation with a preview, a per-block reference, and a hint naming the retrieval tool ([Strands Agents documentation](https://strandsagents.com/docs/user-guide/concepts/plugins/context-offloader/)):

```text
[Offloaded: 1 blocks, ~10,000 tokens]
Tool result was offloaded to external storage due to size.
Use the preview below if it answers your question.
If you need more detail, use retrieve_offloaded_content with a reference and:
  - pattern: regex or keyword to find matching lines with context
  - line_range: { start, end } to read a specific span of lines
Retrieve full content (omit pattern/line_range) as a last resort.

{"users":[{"id":1,"name":"Alice","role":"admin"},{"id":2,"name":"Bob",...

[Stored references:]
  mem_1_tool-123_0 (json, 42,000 bytes)
```

Two details differ from the paper, and both are deliberate. Strands supports partial dereference by regex pattern or line range, so the agent pulls a slice instead of the whole record. It also evicts offloaded entries after 20 idle agent loop cycles by default, and evicted content is gone — append-only retention is a setting you choose, not what you get ([Strands Agents documentation](https://strandsagents.com/docs/user-guide/concepts/plugins/context-offloader/)).

## Key Takeaways

- Choose addressable recall when compaction is losing details your agent later needs, not when the transcript is merely long.
- Its advantage is exact recovery, so it beats similarity retrieval on lookup and barely moves reasoning-bound tasks.
- Budget the recall channel deliberately — caps per step, per recall, and in total — or stub overhead eats the space compaction freed.
- Prompt the recall action explicitly; agents do not reliably invoke memory tools on their own.
- Decide your eviction policy on purpose. Production implementations default to deleting idle records, not keeping them forever.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the tiered offload-then-summarize baseline this pattern extends with exact addressing
- [Observation Masking](observation-masking.md) — the lossy alternative that drops processed tool outputs instead of citing them
- [Selective Rewind Summarization](selective-rewind-summarization.md) — choosing a cut point when summarization is the right tool
- [Agent-Initiated Rubric-Gated Self-Compaction](agent-initiated-self-compaction.md) — deciding when compaction fires, orthogonal to what it leaves behind
- [Event Sourcing for Agents](../observability/event-sourcing-for-agents.md) — the append-only event log as a general agent-state substrate
