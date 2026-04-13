---
title: "Consolidate Agent Tools to Reduce Cognitive Overhead"
description: "Fewer, higher-level tools reduce selection ambiguity and context cost compared to many narrow tools that mirror API endpoint boundaries."
tags:
  - agent-design
  - cost-performance
---

# Consolidate Agent Tools

> Prefer fewer, higher-level tools that match how agents reason about tasks over many narrow tools that mirror API endpoint boundaries.

## The Problem with API-Shaped Tool Sets

Developers building tool-augmented agents often mirror the underlying API: one tool per endpoint, one tool per operation. This produces a large tool set where agents must chain multiple calls to complete a single logical action — finding a calendar slot and booking it requires two separate tools, two decisions, two opportunities for error.

Agents select tools based on intent. A large set of overlapping or fine-grained tools creates ambiguity at the selection step: the agent must reason about which combination of tools achieves the goal, rather than selecting the tool that directly matches its intent. Per [Anthropic's writing tools for agents post](https://www.anthropic.com/engineering/writing-tools-for-agents), more tools do not improve agent outcomes — thoughtful selection beats abundance.

## Consolidation Principle

Each tool should map to a distinct, human-understandable sub-task. If two tools are always called together, they should be one tool. If a tool's output always feeds into another specific tool, merge them.

Example: Instead of `list_calendar_events` + `create_calendar_event`, define a single `schedule_event` tool that finds availability and books in one call. The agent expresses intent ("schedule a meeting") and the tool handles the mechanics.

## Overlapping Functions

Overlapping tool functions produce two failure modes:

1. **Redundant calls** — the agent calls both tools when one would have been sufficient
2. **Wrong tool selection** — the agent selects the less appropriate tool because the distinction is unclear

Eliminate overlap by defining mutually exclusive responsibilities for each tool. If you cannot state in one sentence what each tool does that no other tool does, the tool set has overlap.

## Namespace Grouping

When multiple related tools are necessary, group them under a common namespace prefix. For example: `asana_search`, `asana_projects_search`, `asana_task_create`. The prefix signals to the agent that these tools operate on the same system and reduces confusion when selecting between them.

This is preferable to flat naming (`search`, `project_search`, `create_task`) where the relationship between tools is implicit.

## Why It Works

LLMs select tools by attending to their descriptions in the context window. When descriptions for ten narrow tools compete for attention, the model must reason about which subset achieves the goal — a multi-step inference problem layered on top of the actual task. Fewer, well-scoped tools reduce the selection decision to a direct mapping: intent → tool, rather than intent → combination of tools.

The mechanism is not merely ergonomic. [LongFuncEval (2025)](https://arxiv.org/abs/2505.10570) found that expanding a tool catalog caused accuracy drops of 7–85% depending on the model, with a pronounced ["lost-in-the-middle"](https://arxiv.org/abs/2307.03172) effect (Liu et al., 2023): the correct tool becomes harder to locate among distractors. Consolidation removes distractors at the source rather than relying on the model to filter them.

## Context Window Impact

Each tool definition consumes context tokens. A large tool set with many narrow tools consumes context on definitions the agent may never use in a given task. Consolidating tools reduces context footprint proportionally — fewer tools means more context available for task data and reasoning.

This matters most in long-running tasks where context pressure accumulates. A tool set designed for minimal context footprint is a latent performance advantage in complex multi-step workflows.

## When Not to Consolidate

Consolidation has limits and backfires in specific conditions. Do not merge tools that:

- Serve genuinely distinct sub-tasks that are not always performed together — forcing the agent to call a merged tool when it only needs one sub-operation wastes tokens and obscures intent
- Have significantly different permission requirements — combining them grants excess access to every caller regardless of which sub-task they need
- Have output schemas so different that a merged interface becomes incoherent — the agent can't reliably pattern-match on the response

**Drawbacks of over-consolidation:** A merged tool that handles too much becomes a black box. When it fails, the agent can't reason about which step failed. A merged `find_and_book_flight` that silently fails at the hold step looks identical to one that fails at confirmation. Narrow tools preserve failure granularity; merged tools trade it away for call-count efficiency.

**The test:** Does the merged tool still map to a single, clear human-understandable action? If it requires a paragraph to describe, it has been over-consolidated. If two sub-tasks are *sometimes* called together but not always, keep them separate and let the agent compose them.

## Example

A travel-booking agent starts with five tools mirroring the REST API:

```yaml
tools:
  - name: search_flights
    description: Search available flights by route and date
  - name: get_flight_details
    description: Get seat map and baggage policy for a flight
  - name: hold_flight
    description: Place a temporary hold on a flight
  - name: create_booking
    description: Book a held flight with passenger details
  - name: send_confirmation
    description: Email booking confirmation to the passenger
```

The agent must chain all five in the correct order, deciding at each step which tool comes next. In practice `get_flight_details` is always called after `search_flights`, `hold_flight` always precedes `create_booking`, and `send_confirmation` always follows `create_booking`.

After consolidation:

```yaml
tools:
  - name: find_flights
    description: Search flights and return options with full details (seat map, baggage)
  - name: book_flight
    description: Hold, book, and send confirmation for a selected flight
```

Two tools, two clear intents. `find_flights` merges search and detail retrieval — they were always called together. `book_flight` merges the hold-book-confirm chain — the agent never holds without booking or books without confirming. The agent now selects between "find" and "book" instead of reasoning about a five-step pipeline.

## Key Takeaways

- More tools do not improve agent outcomes — fewer, well-scoped tools reduce selection ambiguity
- Each tool should map to one distinct sub-task; tools always called together should be one tool
- Eliminate overlapping functions to prevent redundant calls and wrong tool selection
- Use namespace prefixes to group related tools and signal system relationships
- Consolidation also reduces context window consumption — a structural performance benefit

## Related

- [Tool Engineering](tool-engineering.md)
- [Tool Description Quality](tool-description-quality.md)
- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md)
- [Advanced Tool Use](advanced-tool-use.md)
- [Poka-Yoke Agent Tools](poka-yoke-agent-tools.md)
- [Semantic Tool Output](semantic-tool-output.md)
