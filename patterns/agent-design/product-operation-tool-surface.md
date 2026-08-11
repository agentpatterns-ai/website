---
title: "Product-Operation Tool Surfaces for In-Product Agents"
term: "Product-Operation Tool Surface"
description: "An agent living inside a product enumerates each action as its own shallow tool, then scopes the live catalog per thread so tool selection holds up."
tags:
  - agent-design
  - tool-engineering
  - tool-agnostic
aliases:
  - shallow product tools
  - product-operation tools
  - in-product agent tool surface
last_reviewed: 2026-08-11
maturity: emerging
---

# Product-Operation Tool Surfaces for In-Product Agents

> A product-operation tool surface enumerates each product action as its own shallow tool, then scopes the live catalog per conversation thread.

A product-operation tool surface gives an agent one tool per product action instead of a few general primitives it composes. Linear built its in-product agent from "a large number of comparatively shallow tools, each tied to a specific product operation like creating an issue or modifying a document," where coding agents rely on "a small set of deep tools, like `read_file`, `write_file`, and `run_command`" ([Linear](https://linear.app/now/how-we-built-linear-agent)). The inversion pays off under three conditions and costs you elsewhere.

## When this applies

Adopt the shallow-tool surface only when all three hold. Handing the agent an SDK and a sandbox is the better design when any of them fails.

| Condition | Why it is load-bearing |
|-----------|------------------------|
| The product's actions are enumerable | Once the general API is withheld, a request outside the enumerated set has no path to completion. Linear names the symptom as "long-tail requests where…the agent may attempt to solve the task through increasingly speculative actions" ([Linear](https://linear.app/now/how-we-built-linear-agent)). |
| The harness can scope the live catalog per thread | Retrieval over a tool index more than triples selection accuracy against a flat catalog, 43.13% versus 13.62% ([RAG-MCP, arXiv:2505.03275v1](https://arxiv.org/abs/2505.03275v1)). |
| Predictability is worth more than breadth | Linear declined to expose "the Linear SDK and a coding environment, a CLI, or the GraphQL API" because it would "increase the surface area for mistakes" ([Linear](https://linear.app/now/how-we-built-linear-agent)). |

## How it works

The pattern is two halves, and running only the first is what makes it fail.

Enumerate the action space. Each product feature ships tools for reading and changing its data, an explanation of how that data is structured, and principles for using the feature well ([Linear](https://linear.app/now/how-we-built-linear-agent)). Operations the surface never defines are unreachable, so the agent cannot improvise an invalid product state against a raw API.

Scope the live catalog. Bundle related tools so only the relevant slice enters context. Linear calls its bundle a system skill, holding "some basic metadata, a fragment of the system prompt, and a set of tools," loaded "either before the agent begins working on a task or on-demand as the task unfolds" ([Linear](https://linear.app/now/how-we-built-linear-agent)). GitHub reached the same shape independently, grouping its MCP server's operations into named toolsets and stating the reason plainly: "Enabling only the toolsets that you need can help the LLM with tool choice and reduce the context size" ([github/github-mcp-server](https://github.com/github/github-mcp-server)).

Watch the cache when tools load mid-conversation. Tool definitions sit first in the prompt-cache prefix, and Anthropic's caching documentation is explicit: "Modifying tool definitions (names, descriptions, parameters) invalidates the entire cache" ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Linear built dynamic injection specifically to "preserve the provider's prefix cache, which isn't the case if implemented naively, because reprocessing existing context can drive up costs" ([Linear](https://linear.app/now/how-we-built-linear-agent)).

Enumeration also buys per-operation approval. Linear's agent "can delete something it created during the current conversation without asking, while still requiring confirmation before deleting an existing issue" ([Linear](https://linear.app/now/how-we-built-linear-agent)), a rule expressible only because deletion is an operation the product team defined.

## Why it works

Enumeration moves error prevention from the prompt to the interface. An operation the surface never defines cannot be called, so the agent has no route to an invalid state regardless of what it infers. That is the same [poka-yoke](../../tool-engineering/poka-yoke-agent-tools.md) logic applied at the product boundary rather than the argument schema. The cost is catalog size, and catalog size degrades selection: Anthropic measured Opus 4 at 49% against large tool sets, rising to 74% once tool search kept the visible set small ([Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)). Scoped loading is the half that makes enumeration survivable, not an optimization added afterward.

That also resolves an apparent contradiction with the standing advice to [consolidate agent tools](../../tool-engineering/consolidate-agent-tools.md). The two rules govern different axes: consolidation bounds the live catalog the model reads on a turn, enumeration bounds the action space the agent can reach at all. A product agent runs a large total catalog and a small per-thread catalog at once.

## When this backfires

- Requests routinely fall outside the enumerated operations. The withheld escape hatch turns an unusual request into a dead end, and the agent burns turns on speculative alternatives ([Linear](https://linear.app/now/how-we-built-linear-agent)).
- The harness has no per-thread scoping. Every enumerated tool then competes for attention on every turn, which is the flat-catalog baseline the second condition above measures ([RAG-MCP, arXiv:2505.03275v1](https://arxiv.org/abs/2505.03275v1)).
- Dynamic injection is implemented naively. Tools head the cache prefix, so mid-conversation injection invalidates the whole cache and the scoping machinery costs more than the flat catalog it replaced ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- The routing that picks bundles is weak. A weak retrieval scorer expands an adaptive shortlist to roughly 80 tools out of a 100-tool registry, so the loading machinery is paid for and the targeting benefit never arrives ([Repantis et al., 2026, arXiv:2605.24660v2](https://arxiv.org/abs/2605.24660v2)).
- A sandbox is cheap for your deployment. Anthropic reports a Drive-to-Salesforce task falling "from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%" when MCP servers are presented as code APIs, at the price of "a secure execution environment with appropriate sandboxing, resource limits, and monitoring" ([Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)). An internal agent already inside that boundary should take the code route.
- The product ships features faster than the tool layer. Every feature needs its tools, its data-model explanation, and its best-practice principles ([Linear](https://linear.app/now/how-we-built-linear-agent)), so a fast-moving surface leaves the agent behind the product it serves.

## Example

The GitHub MCP server is a product-operation tool surface you can inspect. It exposes GitHub's operations as tools rather than wrapping the REST or GraphQL API in one call, and it groups them into roughly twenty named toolsets — `actions`, `code_quality`, and the rest — with two more available only on the remote server, `copilot_spaces` and `github_support_docs_search` ([GitHub MCP remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)).

The scoping half shows up in how those toolsets are selected. Each is "provided as a distinct URL so you can mix and match to create the perfect combination of tools for your use-case" ([GitHub MCP remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)), and the reason for narrowing the selection is the tool-choice and context-size argument quoted above.

Run one toolset and the agent sees a handful of GitHub operations. Run them all and it sees the whole product, which is the configuration the project's own guidance steers you away from. The alternative surface — one `execute_code` tool with the GitHub API reachable from inside a sandbox — buys every operation at once and gives up the bound. Anthropic puts that trade at a 98.7% saving on its own example, against a sandbox someone has to run ([Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)).

## Key Takeaways

- Enumerating product actions as shallow tools bounds what an agent can do to what the product team defined, and withholding the SDK or API is what makes that bound real.
- Enumeration alone degrades tool selection; per-thread scoping through skills, toolsets, or tool search is the half that keeps it usable.
- Consolidation advice and shallow-tool advice govern different axes, one the live catalog and the other the reachable action space.
- Dynamic tool loading must preserve the prompt-cache prefix, since tool definitions sit at its head and any change invalidates the whole cache.
- Where an execution sandbox is already acceptable, the code-surface alternative is cheaper on tokens and broader in reach, so choose the shallow surface only when the bounded action space is the point.

## Related

- [Consolidate Agent Tools](../../tool-engineering/consolidate-agent-tools.md) — the live-catalog half of the same problem, and the rule this pattern reconciles with
- [Advanced Tool Use](../../tool-engineering/advanced-tool-use.md) — the API-level features that implement per-thread scoping
- [Poka-Yoke for Agent Tools](../../tool-engineering/poka-yoke-agent-tools.md) — the same error-prevention logic applied inside a single tool's schema
- [Progressive Disclosure for Layered Agent Definitions](progressive-disclosure-agents.md) — on-demand loading of knowledge rather than tools
- [Issue-Tracker as Agent Dispatch Surface](../../workflows/issue-tracker-agent-dispatch-surface.md) — the view from the team wiring an agent to a tracker, rather than the team building the agent inside it
