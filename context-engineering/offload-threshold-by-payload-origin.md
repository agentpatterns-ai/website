---
title: "Offload Thresholds by Payload Origin (Tool Output and Pasted Input)"
term: "Payload-Origin Offload Threshold"
description: "Deep Agents documents separate offload thresholds for tool results and human messages. Neither its post nor the related coding study tests that split."
aliases:
  - provenance-split offload threshold
  - per-origin offload threshold
  - offload threshold by payload type
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-28
maturity: emerging
status: current
---

# Offload Thresholds by Payload Origin (Tool Output and Pasted Input)

> Payload-origin offload thresholds decide when tool results and human messages become file references; Deep Agents documents different limits without testing the split.

## Documented offload behavior

LangChain's October 14, 2026 [Deep Agents post](https://www.langchain.com/blog/context-engineering-deep-agents-remember) describes an offload policy keyed to who supplied the payload:

| Payload origin | Documented threshold | Storage path |
|---|---|---|
| Tool result | Roughly 20,000 tokens | `/large_tool_results/{tool_call_id}` |
| Human message | 50,000 tokens | `/conversation_history/` |

The harness saves the full content before it enters the conversation. The model receives the opening and closing lines plus a file path. It can retrieve further detail with `read_file`. These are the post's documented settings; the post reports no comparison of alternative thresholds ([LangChain](https://www.langchain.com/blog/context-engineering-deep-agents-remember)).

This admission policy differs from [summarizing accumulated conversation history](context-compression-strategies.md) and [retaining content by semantic type](per-type-retention-under-compaction.md). Origin determines when a payload becomes a preview. It does not classify which statements within the payload matter.

## What the coding study supports

Lewis evaluates a different mechanism: older tool results shrink as the context fills, while task text and other conversation messages stay unchanged. The treatment also includes stall detection, interventions, and command safeguards ([study, sections 2–3](https://arxiv.org/html/2608.26218v1)).

On 169 SWE-bench Verified tasks, the study uses a 20,480-token window and a fixed 480-second attempt endpoint. Mean per-task fail-to-pass fraction rises from 28% to 49%; complete solutions rise from 43 to 72. These results belong to the combined treatment. The experiment does not isolate any component's effect ([Lewis, abstract and section 3.1](https://arxiv.org/html/2608.26218v1)).

That evidence cannot validate the Deep Agents thresholds or establish a benefit from treating human messages differently. See [half-life truncation](half-life-tool-result-truncation.md) for the age-based policy and its evaluation limits.

## Reading an offload trace

A missing file read alone does not establish a wrong answer. LangChain describes retrieval as necessary when the agent needs more detail; the preview remains available ([documented retrieval behavior](https://www.langchain.com/blog/context-engineering-deep-agents-remember)). The implication for review is to check whether the answer requires information absent from that preview. A read count alone cannot answer that question.

The sources above provide no tested recipe for choosing your own pair of thresholds. Treat threshold tuning as a separate evaluation question, with task correctness as an outcome.

## Key Takeaways

- Record payload origin when examining an offload trace; the documented admission rules differ for tools and human messages.
- Separate evidence for a combined harness change from evidence for a particular threshold.
- Review the information needed for the answer before classifying an unread offloaded file as a failure.

## Related

- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md) — the broader compression pipeline
- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](half-life-tool-result-truncation.md) — an age-based working-view policy
- [Addressable Recall Compaction: Compact to Citations, Not Summaries](addressable-recall-compaction.md) — references that preserve access to full observations
- [Per-Type Retention Policy for Agent Compaction (Knowledge Triage)](per-type-retention-under-compaction.md) — retention by content type during compaction
