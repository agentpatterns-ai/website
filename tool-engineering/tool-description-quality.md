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

Agents do not browse a tool catalog before acting. They select tools by reasoning about which available tool best matches their current intent. A poorly described tool is invisible for use cases its description fails to communicate — even if the implementation would handle them correctly.

Per [Anthropic's multi-agent research system post](https://www.anthropic.com/engineering/multi-agent-research-system), improving tool ergonomics — including descriptions — reduced task completion time by 40% for agents using the updated tools.

The mechanism: tool descriptions are embedded into the agent's context at the reasoning step. Richer, distinctive descriptions create stronger semantic signals that align agent intent with the correct tool. Research on [tool-level retrieval for multi-agent systems](https://arxiv.org/abs/2511.01854) confirms this: coarse descriptions cluster functionally different tools together in embedding space, making correct selection unreliable.

## Instruct Agents to Examine Tools First

When a tool set includes both generic and specialized tools, agents tend to match on the first plausible tool — often a generic one. Making the preference explicit in the system prompt counters this: "Before acting, review your available tools and select the one that best matches the task. Prefer specialized over generic tools." An agent that defaults to a generic search tool when a specialized domain-specific tool is available produces lower-quality results.

## MCP Server Tool Descriptions

MCP servers expose many tools at once. Unclear descriptions at this scale cause systematic misuse: every agent makes the same wrong selection decision, compounding across all invocations. For MCP tools:

- Each tool description must be independently self-contained — agents may not have context from adjacent tools
- Do not assume agents read related tools before selecting the current one
- Include domain context in each description, not just in a top-level server description

## Testing Tool Selection

Tool selection failures are often invisible during development — an agent calling the wrong tool with a plausible-looking result won't surface the error until compared against ground truth. To test selection:

- Instrument agent traces and log which tool was selected for each task type
- Compare selected tools against ground truth for a representative set of test cases
- Refine descriptions based on observed misselection patterns, not intuition about what descriptions should say

## Iterating on Descriptions

Description iteration follows the pattern of prompt iteration: observe, identify failures, change, measure. The most common failure mode: a description accurate enough to describe what the tool does but not specific enough to tell the agent when to prefer it over alternatives.

The fix is positive selection signals: "Use this tool when X" and "Prefer this over [other tool] when Y." These are instructions to the agent, not documentation of the interface.

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

## When This Backfires

Each description adds tokens on every invocation. Three conditions where this matters:

- **Large MCP servers** (50+ tools): verbose descriptions push tool context above 10k tokens. Use retrieval-based selection (embedding search to select a subset) over in-context enumeration.
- **High-frequency loops**: verbose descriptions add cost with diminishing returns after selection stabilizes.
- **Genuinely similar tools**: description quality cannot resolve near-identical tools — consolidate or differentiate at the implementation level. See [Consolidate Agent Tools](consolidate-agent-tools.md).

## Key Takeaways

- Tool description quality is a direct performance lever — improving tool ergonomics (including descriptions) reduced task completion time by 40% in one case
- Prompt agents explicitly to prefer specialized over generic tools; make this instruction explicit in the system prompt
- MCP server tools require self-contained descriptions; do not assume agents read adjacent tool docs
- Test tool selection explicitly by logging which tools are selected for which tasks
- Add positive selection signals ("use this when...") not just capability descriptions
- At large tool set sizes (50+ tools), prefer retrieval-based selection over in-context enumeration to manage token cost

## Related

- [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md)
- [Tool Engineering](tool-engineering.md)
- [Agent-Computer Interface](agent-computer-interface.md)
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Poka-Yoke Agent Tools](poka-yoke-agent-tools.md)
- [MCP Server Design](mcp-server-design.md)
- [Token-Efficient Tool Design](token-efficient-tool-design.md)
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md)
- [Filesystem Tool Discovery](filesystem-tool-discovery.md)
- [Semantic Tool Output](semantic-tool-output.md)
- [Self-Healing Tool Routing](self-healing-tool-routing.md)
- [Advanced Tool Use](advanced-tool-use.md)
- [Tool Minimalism](tool-minimalism.md)
