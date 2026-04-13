---
title: "Tool Minimalism and High-Level Prompting"
description: "Expose fewer, non-overlapping tools and use goal-oriented instructions — counter-intuitive decisions that production data shows improve reliability."
aliases:
  - Tool Schema Design
tags:
  - agent-design
  - instructions
---

# Tool Minimalism and High-Level Prompting

> Expose fewer, non-overlapping tools and provide goal-oriented instructions rather than step-by-step procedures — both counter-intuitive decisions that production data shows improve reliability.

!!! info "Also known as"
    Tool Calling Schema Standards, Subagent Schema-Level Tool Filtering, Tool Schema Design

## The Over-Tooling Problem

Developers instinctively add more tools for coverage: multiple ways to read files, search the codebase, run code. The intent is to ensure the agent always has something that works. The effect is ambiguity the model must resolve on every call.

OpenAI's data agent team found: "We exposed our full tool set to the agent, and quickly ran into problems with overlapping functionality... it's confusing to agents." Consolidating and restricting tool calls — even removing valid options — reduced ambiguity and improved end-to-end reliability. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

Redundancy is a liability, not a safety net. When two tools can both accomplish a task, the model spends reasoning on the selection decision rather than on the task itself. When it selects the wrong one, the error is introduced before any work has been done.

## Removing Overlapping Tools

The first audit: identify tool pairs that have overlapping functionality. For coding agents, common overlaps:

- Multiple search tools (semantic search, text search, symbol search) with unclear selection criteria
- Multiple file read mechanisms (read full file, read range, search for pattern within file)
- Shell execution plus dedicated command tools for the same operations

For each overlap, decide: consolidate into one tool, or add explicit selection criteria that make the use cases non-overlapping. If the selection criteria are hard to articulate, consolidate. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## The Over-Specification Problem

The complementary mistake: writing detailed step-by-step system prompts that prescribe exactly how the agent should execute the task.

The data agent team found: "rigid instructions often pushed the agent down incorrect paths" when question details varied. Highly prescriptive prompts anchor the agent to a procedure that was designed for one variant of the task; when the task varies slightly, the procedure doesn't fit and the agent follows it anyway.

Shifting to higher-level guidance and trusting the model's own reasoning to choose execution paths produced more robust outcomes. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## High-Level Prompting in Practice

**Prescriptive (avoid):**
> "First, search for the table name in the schema file. Then find all usages of the table in the query files. Then check the migration files for recent changes to that table. Finally, summarize what you found."

**Goal-oriented (prefer):**
> "Find all places in the codebase that interact with the `users` table, including schema, queries, and migrations. Provide a summary of recent changes and current usage patterns."

The prescriptive version anchors the agent to one search sequence. The goal-oriented version lets the agent choose whether to start with schema, queries, or migrations based on what it finds — which is often the right decision.

## For Coding Agent Design

The practical implications:

- Define the outcome and the constraints, not the step-by-step procedure
- Let the model decide whether to read a file, search symbols, or inspect git history — it has information about what it found that the system prompt author didn't have
- Consolidate overlapping tools into the smallest set that covers the task space without redundancy
- Add explicit selection criteria only when use cases are genuinely distinct

## Key Takeaways

- Overlapping tools create ambiguity the model resolves on every call — redundancy is a liability, not a safety net
- Consolidating and restricting tool calls improves reliability, even when it removes valid options
- Prescriptive step-by-step prompts produce rigid behavior that fails when task details vary
- Goal-oriented instructions with outcome definitions outperform procedure specifications
- Trust the model's execution path reasoning; constrain the goal and the boundaries, not the steps

## Example

A coding agent starts with six file-interaction tools:

| Tool | Purpose |
|------|---------|
| `read_file` | Read entire file |
| `read_lines` | Read line range |
| `grep_file` | Search within a single file |
| `grep_codebase` | Search across all files |
| `semantic_search` | Embedding-based search |
| `find_symbol` | Find function/class definitions |

The agent frequently calls `grep_file` when `grep_codebase` would have been correct, and hesitates between `semantic_search` and `find_symbol` for locating functions.

After consolidation:

| Tool | Purpose |
|------|---------|
| `read_file` | Read file (supports optional line range) |
| `search` | Text or regex search across files (supports path filter) |
| `find_symbol` | Find definitions by name (distinct use case: structured symbol lookup) |

Three tools, no overlapping functionality. `read_file` absorbed `read_lines` via an optional parameter. `search` absorbed `grep_file`, `grep_codebase`, and `semantic_search` — the model no longer decides which search variant to use. `find_symbol` remains because its use case (structured symbol lookup) is clearly distinct from text search.

## Related

- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Tool Selection Guidance](tool-description-quality.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Tool Calling Schema Standards](../standards/tool-calling-schema-standards.md)
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md)
- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
