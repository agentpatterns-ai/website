---
title: "Retrieval-Augmented Agent Workflows: On-Demand Context"
description: "Pull context into the agent at the moment it is needed rather than preloading it at session start. Context Hub, Semantic Context Loading, JIT Context, RAG"
aliases:
  - Context Hub
  - Semantic Context Loading
  - JIT Context
  - RAG
tags:
  - context-engineering
  - agent-design
  - cost-performance
---

# Retrieval-Augmented Agent Workflows: On-Demand Context

> Pull context into the agent at the moment it is needed rather than preloading it at session start.

!!! info "Also known as"
    Context Hub, Semantic Context Loading, JIT Context, RAG

Retrieval-augmented agent workflows structure context in two layers: a small startup set of instructions and tool descriptions, and an on-demand layer where the agent fetches documentation, file contents, and search results via tool calls only when the current task step requires them. This keeps the context window lean at session start and preserves budget for reasoning.

## The Problem with Preloading

Every token loaded at startup consumes context budget that cannot be used for reasoning, intermediate outputs, or tool results. An agent researching five documentation sites does not need all five loaded before the first message — it needs to know they exist and how to access them.

Loading context speculatively "just in case" produces two failure modes: the agent runs out of context mid-task, or the [U-shaped attention curve](lost-in-the-middle.md) buries the preloaded material where the model rarely attends to it [unverified — specific attention curve effect on preloaded agent context not sourced here].

## On-Demand Retrieval Pattern

Structure agent context in two layers:

| Layer | What goes in | When loaded |
|-------|-------------|-------------|
| Startup | Instructions, conventions, tool descriptions, skill metadata | Session start |
| On-demand | Documentation pages, file contents, search results, API responses | When the task requires them |

The agent starts lean. Tool descriptions tell it what is available. When a task step requires specific knowledge, the agent issues a tool call to retrieve it.

Anthropic notes that teams increasingly augment retrieval systems with ["just in time" context strategies where agents dynamically load data into context at runtime using tools](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## Mechanisms

**MCP servers** expose external data sources as tools. The agent receives tool descriptions at startup and fetches content via tool calls on demand. Nothing enters the prompt until the agent asks for it.

**Web fetch** lets an agent pull a documentation page when researching a specific question rather than pre-embedding pages in the system prompt.

**File search** lets an agent locate relevant code at the point of implementation rather than loading every module upfront — it searches when it needs to understand a dependency.

**Sub-agents** provide isolated context windows for retrieval-heavy tasks. A coordinator delegates a retrieval step to a sub-agent, which fetches, processes, and returns a condensed summary. [LangChain's Deep Agents framework](https://blog.langchain.com/context-management-for-deepagents/) uses a filesystem abstraction that lets agents offload large results and re-read them selectively, rather than keeping everything in active context.

## Trade-offs

On-demand retrieval adds latency. Multi-step retrieval chains (search → read → search again) can slow throughput noticeably. Preloading eliminates that latency at the cost of context budget.

The right balance depends on task structure:

- **Repetitive access** to the same document: preload it.
- **Exploratory tasks** where the relevant subset is unknown upfront: retrieve on-demand.
- **Long-horizon tasks**: combine both — keep instructions preloaded, retrieve reference material as needed, and use compaction or sub-agents when context fills.

Anthropic notes that treating context as ["a precious, finite resource"](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and assembling "the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" produces better results than broad preloading.

## Example

The following Claude MCP configuration demonstrates the two-layer structure: startup context is kept small (tool descriptions only), and document content is never preloaded.

```json
// .claude/mcp_settings.json
{
  "mcpServers": {
    "docs": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace/docs"],
      "description": "Read documentation files on demand"
    },
    "search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "<your-key>" },
      "description": "Search the web for current information"
    }
  }
}
```

At session start the agent receives only tool names and descriptions — no document content. When it needs to consult the API reference, it calls the `docs` tool:

```
Tool call: read_file("docs/api/authentication.md")
→ Returns: 4 KB of authentication docs (now in context)
```

When it needs current information it calls `search`:

```
Tool call: brave_search("stripe webhook signature verification 2024")
→ Returns: top 3 results (now in context)
```

A task requiring only one of five documentation sections consumes context for that section alone. A task requiring none consumes zero documentation tokens. The startup prompt stays under 2 KB regardless of how large the documentation corpus grows.

## Key Takeaways

- Start lean: preload instructions and tool descriptions, not reference content.
- Use tool calls (MCP, web fetch, file search) to pull content when a task step needs it.
- On-demand retrieval preserves context budget for reasoning but adds per-call latency.
- Sub-agents provide isolated context windows for retrieval-heavy subtasks, returning compressed summaries to the coordinator.

## Unverified Claims

- The U-shaped attention curve buries preloaded material where the model rarely attends to it [unverified — specific attention curve effect on preloaded agent context not sourced here]

## Related

- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md)
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md)
- [Context Priming](context-priming.md)
- [Context Compression Strategies: Offloading and Summarisation](context-compression-strategies.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md)
- [Repository Map Pattern: AST + PageRank for Dynamic Code Context](repository-map-pattern.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [Discoverable vs Non-Discoverable Context for Agents](discoverable-vs-nondiscoverable-context.md)
- [Seeding Agent Context: Embedding Breadcrumbs in Code](seeding-agent-context.md)
- [Observation Masking](observation-masking.md)
- [Prompt Compression](prompt-compression.md)
- [The Infinite Context](../anti-patterns/infinite-context.md)
- [Structured Domain Retrieval: Knowledge Graphs and Case-Based Reasoning](structured-domain-retrieval.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
