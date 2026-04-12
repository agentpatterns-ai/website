---
title: "Filesystem-Based Tool Discovery for AI Agent Development"
description: "Store MCP tools as files in a directory tree so agents load only the definitions they need, reducing token overhead by up to 98% versus upfront registration."
tags:
  - context-engineering
  - agent-design
  - cost-performance
  - claude
  - source:opendev-paper
aliases:
  - "lazy tool loading"
  - "on-demand tool loading"
---

# Filesystem-Based Tool Discovery

> Structure MCP tools as files in a directory tree and let the agent load only the definitions it needs, reducing token overhead by up to 98% compared to registering all tools upfront.

## The Problem With Upfront Tool Registration

The standard MCP pattern registers every tool definition at session start. As tool collections grow — hundreds of tools across dozens of servers — this becomes a significant context cost. [Anthropic's MCP code execution research](https://www.anthropic.com/engineering/code-execution-with-mcp) reports that large tool collections can consume 150,000+ tokens on tool definitions alone before any task work begins.

Loading all definitions regardless of relevance is the MCP equivalent of reading the entire standard library before writing a function.

## The Pattern

Instead of registering tools as live function definitions, store each tool as a file in a directory tree:

```
servers/
  google-drive/
    getDocument.ts
    listFiles.ts
    uploadFile.ts
  github/
    createPR.ts
    listIssues.ts
    mergePR.ts
  slack/
    postMessage.ts
    readChannel.ts
```

The agent starts each session with access to:

1. A directory listing of available server categories
2. A search tool that locates relevant tool files by keyword or category
3. A read tool to load individual tool definitions on demand

When the agent determines it needs to fetch a Google Drive document, it reads `servers/google-drive/getDocument.ts` — loading one definition instead of every definition across every server.

[Anthropic's MCP code execution research](https://www.anthropic.com/engineering/code-execution-with-mcp) reports a 98.7% token reduction using this approach (150,000 tokens → ~2,000 tokens).

## Why It Works

Models handle filesystem navigation natively — reading directories, searching by name, loading files. No special orchestration is required; the agent applies the same exploration skills it uses for codebases.

## Implementation Notes

**Directory structure matters.** Group tools by service or functional domain so the agent can navigate by category before searching by keyword. A flat directory of 500 tool files is harder to navigate than five directories of 100 files each.

**Include a manifest.** A top-level `README.md` or `manifest.json` listing available server categories and their purposes helps the agent orient without reading every subdirectory.

**Search over listing.** Provide keyword or embedding-based search so the agent locates tools without exhaustive listing. Return file paths, not full definitions.

**File content format.** Each tool file should contain the minimum: function signature, brief description, and parameters. The purpose is selective loading, not documentation.

## Tradeoffs

| Upfront registration | Filesystem discovery |
|---------------------|---------------------|
| All tools available immediately | Agent must search before calling |
| O(all tools) context cost per session | O(used tools) context cost per session |
| Simpler [agent harness](../agent-design/agent-harness.md) | Requires directory + search infrastructure |
| Breaks at large tool counts | Scales with tool count |

Filesystem discovery adds a navigation step before each new tool type is used — a one-time cost for repeated tool sets, per-tool-type for exploratory workflows.

## Keyword-Scored MCP Discovery

The OPENDEV paper describes a complementary approach: a `search_tools` tool that uses keyword matching to discover MCP tools, loading them lazily on first invocation rather than registering all definitions at startup ([Bui, 2025 §2.4.7](https://arxiv.org/abs/2603.05344)). The initial approach loaded all MCP tools into the schema upfront, causing [prompt bloat](../anti-patterns/prompt-tinkerer.md) and context budget exhaustion. Lazy loading trades a one-time lookup cost for a significant reduction in initial prompt size ([Bui, 2025 §2.4.7](https://arxiv.org/abs/2603.05344)).

The principle is identical — on-demand loading — but the mechanism differs. Filesystem discovery uses directory navigation (98.7% reduction); keyword-scored discovery uses search queries against a tool index. The approaches complement each other: filesystem structure for category browsing, keyword scoring for cross-category lookup.

## Key Takeaways

- Registering all MCP tool definitions upfront is a fixed context cost that scales with tool count, not task complexity.
- Filesystem-based discovery loads only the definitions needed for the current task.
- Anthropic reports a 98.7% token reduction using this pattern for large tool collections.
- Models navigate directory trees natively — no special orchestration is required.
- Group tools by service or domain to make category-level navigation practical.
- Keyword-scored lazy MCP loading achieves significant initial prompt reduction as a complementary discovery mechanism.

## Example

An agent task requires reading a GitHub issue and posting a Slack message. Without filesystem discovery the system loads all tool definitions at startup. With filesystem discovery:

```
# Agent receives task: "Read GitHub issue #42 and summarize it in #engineering"

# Step 1 — list available server categories
list_dir("servers/")
# → github/, slack/, google-drive/

# Step 2 — load only the needed tool definitions
read_file("servers/github/getIssue.ts")
# → { name: "getIssue", params: { owner, repo, issue_number }, ... }

read_file("servers/slack/postMessage.ts")
# → { name: "postMessage", params: { channel, text }, ... }

# Step 3 — invoke tools with loaded definitions
getIssue(owner="acme", repo="api", issue_number=42)
postMessage(channel="#engineering", text="Issue #42: ...")
```

Total tokens loaded: ~400 (2 tool definitions). Upfront registration of all 120 tools across 3 servers would have consumed ~12,000 tokens before the first API call.

## Related

- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [MCP Client-Server Architecture](mcp-client-server-architecture.md)
- [Filter and Aggregate in the Execution Environment](../context-engineering/filter-aggregate-execution-env.md)
- [Context Engineering](../context-engineering/context-engineering.md)
- [Progressive Disclosure Agents](../agent-design/progressive-disclosure-agents.md)
- [MCP Client Design](mcp-client-design.md)
- [MCP Server Design](mcp-server-design.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
- [Tool Description Quality](tool-description-quality.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Self-Healing Tool Routing](self-healing-tool-routing.md)
