---
title: "Tool Description Quality for Effective Agent Guidance"
description: "Tool descriptions determine whether agents select the right tool. Treating descriptions as prompt engineering surfaces directly multiplies task success rate."
tags:
  - agent-design
  - cost-performance
aliases:
  - Tool Selection Guidance
  - Selection Signals
---

# Tool Description Quality

> Tool descriptions — not just tool implementations — determine whether agents select the right tool for a task. Treating descriptions as prompt engineering surfaces is a direct multiplier on task success rate.

!!! info "Also known as"
    Tool Selection Guidance, Selection Signals

## Selection as a Reasoning Step

Agents do not browse a tool catalog before acting. They select tools by reasoning about which available tool best matches their current intent. A poorly described tool is effectively invisible for use cases its description fails to communicate — even if the implementation would handle them correctly.

Per [Anthropic's multi-agent research system post](https://www.anthropic.com/engineering/multi-agent-research-system), improving tool ergonomics — including descriptions — reduced task completion time by 40% for agents using the updated tools.

## Instruct Agents to Examine Tools First

Agents prompted to examine all available tools before matching tool selection to user intent perform better than agents that select tools based on the first match that seems plausible. This behavior should be explicit in the system prompt: "Before acting, review your available tools and select the one that best matches the task." [unverified]

This is especially important when the tool set includes both generic and specialized tools. Specialized tools should be preferred; the preference should be stated explicitly. An agent that defaults to a generic search tool when a specialized domain-specific tool is available will produce lower-quality results. [unverified]

## MCP Server Tool Descriptions

MCP servers expose many tools at once. Unclear descriptions at this scale cause systematic misuse: every agent using the server makes the same wrong selection decision, compounding the effect across all invocations. For MCP tools:

- Each tool description must be independently self-contained — agents may not have context from adjacent tools
- Do not assume agents read related tools before selecting the current one
- Include the domain context in each description, not just in a top-level server description

## Testing Tool Selection

Tool selection failures are often invisible during development. An agent that calls the wrong tool and gets a plausible-looking result may not surface the error until results are compared against ground truth. To test selection:

- Instrument agent traces and log which tool was selected for each task type
- Compare selected tools against ground truth for a representative set of test cases
- Refine descriptions based on observed misselection patterns — not based on intuition about what descriptions should say

## Iterating on Descriptions

Description iteration follows the same pattern as prompt iteration: observe behavior, identify failures, make specific changes, measure. The most common failure mode is a description accurate enough to describe what the tool does but not specific enough to tell the agent when to prefer it over alternatives.

The improvement is to add positive selection signals: "Use this tool when X" and "Prefer this over [other tool] when Y." These are instructions to the agent, not documentation of the interface.

## Example

The following pair shows the same MCP tool with a weak description and an improved one. The weak version is accurate but leaves selection decisions to the agent.

```python
# Before: accurate but minimal — agent must guess when to use it
{
    "name": "search_issues",
    "description": "Search for issues in the project tracker.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}
```

```python
# After: includes query syntax, return shape, and when to prefer it over alternatives
{
    "name": "search_issues",
    "description": (
        "Search for issues in the project tracker. "
        "Returns a list of issues matching the query, each with id, title, status, and assignee. "
        "Supports field filters: status:open, status:closed, assignee:<username>, label:<name>. "
        "Use this tool to find issues by keyword or filter. "
        "Prefer this over list_issues when you have a search term or filter criteria. "
        "Use list_issues instead when you need all issues in a project without filtering."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search keywords and/or field filters. Example: 'login page status:open assignee:alice'"
            }
        },
        "required": ["query"]
    }
}
```

The improved description answers all three questions the page identifies: what the tool does, what it returns, and when to use it instead of `list_issues`. The query syntax example eliminates trial-and-error on filter format.

## Key Takeaways

- Tool description quality is a direct performance lever — improving tool ergonomics (including descriptions) reduced task completion time by 40% in one case
- Prompt agents explicitly to examine all tools and prefer specialized over generic
- MCP server tools require self-contained descriptions; do not assume agents read adjacent tool docs
- Test tool selection explicitly by logging which tools are selected for which tasks
- Add positive selection signals ("use this when...") not just capability descriptions

## Unverified Claims

- Agents prompted to examine all available tools before matching tool selection to user intent perform better than agents that select based on the first plausible match [unverified]

## Related

- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md)
- [Tool Engineering](tool-engineering.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Poka-Yoke Agent Tools](poka-yoke-agent-tools.md)
- [MCP Server Design](mcp-server-design.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Filesystem Tool Discovery](filesystem-tool-discovery.md)
- [Semantic Tool Output](semantic-tool-output.md)
- [Self-Healing Tool Routing](self-healing-tool-routing.md)
- [Advanced Tool Use](advanced-tool-use.md)
- [Tool Minimalism](tool-minimalism.md)
