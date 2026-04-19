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

Developers add tools for coverage: multiple ways to read files, search the codebase, run code. The intent is redundancy; the effect is ambiguity the model resolves on every call.

OpenAI's data agent team found: "We exposed our full tool set to the agent, and quickly ran into problems with overlapping functionality... it's confusing to agents." Consolidating and restricting tool calls — even removing valid options — reduced ambiguity and improved end-to-end reliability. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

Redundancy is a liability, not a safety net. When two tools can accomplish the same task, the model spends reasoning on selection rather than the task itself — and a wrong selection introduces the error before any work is done.

Anthropic's engineering team reaches the same conclusion from the tool-authoring side: "When tools overlap in function or have a vague purpose, agents can get confused about which ones to use," and "Too many tools or overlapping tools can also distract agents from pursuing efficient strategies." [Source: [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Removing Overlapping Tools

The first audit: identify tool pairs that have overlapping functionality. For coding agents, common overlaps:

- Multiple search tools (semantic search, text search, symbol search) with unclear selection criteria
- Multiple file read mechanisms (read full file, read range, search for pattern within file)
- Shell execution plus dedicated command tools for the same operations

For each overlap, decide: consolidate into one tool, or add explicit selection criteria that make the use cases non-overlapping. If the selection criteria are hard to articulate, consolidate. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## The Over-Specification Problem

The complementary mistake: writing detailed step-by-step system prompts that prescribe exactly how the agent should execute the task.

The data agent team found: "rigid instructions often pushed the agent down incorrect paths" when question details varied. Prescriptive prompts anchor the agent to a procedure designed for one variant of the task; when the task shifts slightly, the procedure no longer fits and the agent follows it anyway.

Shifting to higher-level guidance and trusting the model's reasoning to choose execution paths produced more robust outcomes. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## High-Level Prompting in Practice

**Prescriptive (avoid):**
> "First, search for the table name in the schema file. Then find all usages of the table in the query files. Then check the migration files for recent changes to that table. Finally, summarize what you found."

**Goal-oriented (prefer):**
> "Find all places in the codebase that interact with the `users` table, including schema, queries, and migrations. Provide a summary of recent changes and current usage patterns."

The prescriptive version anchors the agent to one search sequence. The goal-oriented version lets the agent start with schema, queries, or migrations based on what it finds.

## For Coding Agent Design

The practical implications:

- Define the outcome and the constraints, not the step-by-step procedure
- Let the model decide whether to read a file, search symbols, or inspect git history — it has information about what it found that the system prompt author didn't have
- Consolidate overlapping tools into the smallest set that covers the task space without redundancy
- Add explicit selection criteria only when use cases are genuinely distinct

## When This Backfires

Minimalism is not a universal rule. Common failure conditions:

- **Multi-system orchestrators.** Agents coordinating distinct systems (ticketing, CRM, deployment) benefit from one tool per system operation. Collapsing into a generic `do_action(system, verb, payload)` moves the selection decision into parameter space and loses per-tool schemas.
- **Consolidation that expands the parameter surface.** A unified `search` tool with `mode={text,semantic,symbol}` only helps if the model picks the mode reliably. If parameter choice is as ambiguous as tool choice, you have traded one ambiguity for another.
- **Compliance-driven work.** Goal-oriented prompts assume a shared definition of "done". For regulated workflows where the procedure itself is the artifact (audit trails), prescriptive steps are safer.
- **Weaker models.** Gains from trusting model reasoning shrink with capability. Smaller models benefit more from procedural scaffolding than open-ended goals.

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
- [Semantic Tool Output](semantic-tool-output.md)
- [MCP Server Design](mcp-server-design.md)
- [Unix CLI Native Tool Interface](unix-cli-native-tool-interface.md)
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md)
- [Tool Calling Schema Standards](../standards/tool-calling-schema-standards.md)
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md)
- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
