---
title: "Retrieval-Augmented Agent Workflows: On-Demand Context"
term: "Retrieval-Augmented Agent Workflows"
description: "Pull context into the agent at the moment it is needed rather than preloading it at session start, keeping the context window lean and the budget free for reasoning."
aliases:
  - Context Hub
  - Semantic Context Loading
  - JIT Context
  - RAG
tags:
  - context-engineering
  - agent-design
  - cost-performance
  - tool-agnostic
  - rag
last_reviewed: 2026-06-13
maturity: established
---

# Retrieval-Augmented Agent Workflows: On-Demand Context

> Pull context into the agent at the moment it is needed rather than preloading it at session start.

Learn it hands-on with the [Just-in-Time Retrieval guided lesson](https://learn.agentpatterns.ai/context-engineering/just-in-time-retrieval/), which includes quizzes.

!!! info "Also known as"
    Context Hub, Semantic Context Loading, JIT Context, RAG

Retrieval-augmented agent workflows structure context in two layers: a small startup set of instructions and tool descriptions, and an on-demand layer where the agent fetches documentation, file contents, and search results via tool calls only when the current task step requires them. This keeps the context window lean at session start and preserves budget for reasoning.

## The problem with preloading

Every token loaded at startup consumes budget that cannot be used for reasoning, intermediate outputs, or tool results. An agent researching five documentation sites does not need all five loaded before the first message — it needs to know they exist and how to access them.

Loading context speculatively "just in case" produces two failure modes: the agent runs out of context mid-task, or the [U-shaped attention curve](lost-in-the-middle.md) leaves the preloaded material in the middle of the window, where [models attend less reliably than they do to content near the start or end](https://arxiv.org/abs/2307.03172).

## On-demand retrieval pattern

Structure agent context in two layers:

| Layer | What goes in | When loaded |
|-------|-------------|-------------|
| Startup | Instructions, conventions, tool descriptions, skill metadata | Session start |
| On-demand | Documentation pages, file contents, search results, API responses | When the task requires them |

The agent starts lean. Tool descriptions tell it what is available. When a task step requires specific knowledge, the agent issues a tool call to retrieve it.

Anthropic notes that teams increasingly augment retrieval systems with ["just in time" context strategies where agents dynamically load data into context at runtime using tools](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## Mechanisms

MCP servers expose external data sources as tools. The agent receives tool descriptions at startup and fetches content on demand. Nothing enters the prompt until the agent asks for it.

Web fetch lets an agent pull a documentation page when researching a specific question rather than pre-embedding pages in the system prompt.

File search lets an agent [locate relevant code](repository-level-retrieval-code-generation.md) at the point of implementation rather than loading every module upfront.

Sub-agents provide isolated context windows for retrieval-heavy tasks. A coordinator delegates a retrieval step to a sub-agent, which fetches, processes, and returns a condensed summary. [LangChain's Deep Agents framework](https://blog.langchain.com/context-management-for-deepagents/) uses a filesystem abstraction that lets agents offload large results and re-read them selectively, rather than keeping everything in active context.

## Trade-offs

On-demand retrieval adds latency. Multi-step retrieval chains (search → read → search again) can slow throughput. Preloading eliminates that latency at the cost of [context budget](context-budget-allocation.md).

Latency is not the only downside. Retrieval quality is a second failure mode: when the retriever surfaces irrelevant chunks, accuracy drops rather than improves — one study saw accuracy fall [from 75% to below 40% as a corpus grew from 54 to 1,128 documents](https://arxiv.org/abs/2606.11350) because dense similarity search returned semantically similar but contextually wrong results. On-demand retrieval only preserves budget for reasoning when what it returns is correct; a noisy retriever spends budget on distractors and degrades the very reasoning it was meant to protect.

The right balance depends on task structure:

- Repetitive access to the same document: preload it.
- Exploratory tasks where the relevant subset is unknown upfront: retrieve on demand.
- Long-horizon tasks: combine both — keep instructions preloaded, retrieve reference material as needed, and use compaction or [sub-agents](../patterns/multi-agent/sub-agents-fan-out.md) when context fills.

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

## FAQ

**When should you preload context instead of retrieving it on demand?**

Preload when a document is accessed repeatedly throughout a task, since re-fetching it on demand at every step adds redundant latency. Retrieve on demand for exploratory tasks where the relevant subset of documents is unknown upfront. For long-horizon tasks, combine both: keep instructions preloaded, retrieve reference material as needed, and lean on compaction or sub-agents once context fills.

**Why can on-demand retrieval hurt accuracy instead of improving it?**

Retrieval quality is a separate failure mode from latency: when a retriever surfaces irrelevant chunks, accuracy drops rather than improves. One study found accuracy fell [from 75% to below 40% as a corpus grew from 54 to 1,128 documents](https://arxiv.org/abs/2606.11350), because dense similarity search returned semantically similar but contextually wrong results. On-demand retrieval only helps when what it returns is actually correct.

**Why does preloading large amounts of context hurt reasoning quality?**

Preloaded material often lands in the middle of the context window, where the [U-shaped attention curve](lost-in-the-middle.md) means [models attend less reliably than to content near the start or end](https://arxiv.org/abs/2307.03172). That, combined with running out of context mid-task, is one of two failure modes that speculative just-in-case loading produces, which is why lean startup context plus on-demand retrieval is preferred.

**How does MCP support on-demand retrieval?**

MCP servers expose external data sources, such as documentation, files, and search, as tools the agent receives descriptions for at startup. Nothing enters the prompt until the agent calls the tool; a `docs` server, for example, returns file contents only when the agent issues a `read_file` call for a specific page it currently needs, keeping the startup prompt near 2 KB.

## Key Takeaways

- Start lean: preload instructions and tool descriptions, not reference content.
- Use tool calls (MCP, web fetch, file search) to pull content when a task step needs it.
- On-demand retrieval preserves context budget for reasoning but adds per-call latency.
- Sub-agents provide isolated context windows for retrieval-heavy subtasks, returning compressed summaries to the coordinator.

## Related

- [Compositional Skill Routing for Large Skill Libraries](compositional-skill-routing.md)
- [Context Hub: On-Demand Versioned API Docs for Coding Agents](context-hub.md)
- [Semantic Context Loading: Language Server Plugins for Agents](semantic-context-loading.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [Context Engineering: The Discipline of Designing Agent Context](context-engineering.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
