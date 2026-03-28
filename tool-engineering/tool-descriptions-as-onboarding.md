---
title: "Write Tool Descriptions as Agent Onboarding Documents"
description: "Write tool descriptions assuming the agent has never seen the system — include implicit context, query syntax, domain terms, and resource relationships."
tags:
  - agent-design
  - instructions
aliases:
  - Tool Engineering
  - Mistake-Proofing
  - Poka-Yoke
---

# Write Tool Descriptions Like Onboarding Docs

> Write tool descriptions assuming the agent has never seen the underlying system — include implicit context, query formats, domain terminology, and resource relationships that an experienced user would take for granted.

!!! info "Also known as"
    Tool Engineering, Mistake-Proofing / Poka-Yoke

## The New Hire Analogy

A terse, accurate API reference is sufficient for a developer who already knows the system. An agent integrating with your system for the first time has no background knowledge. It cannot infer what "user" means in your domain, whether a date parameter expects ISO 8601 or a timestamp, or how resource A relates to resource B.

The effective framing is: write as if training a competent new hire on their first day. Not a tutorial — they can already read code and understand systems — but explicit about the things the documentation omits because experienced users know them.

Per [Anthropic's writing tools for agents post](https://www.anthropic.com/engineering/writing-tools-for-agents), minor description refinements routinely yield dramatic accuracy improvements. The gap between accurate-but-minimal and accurate-with-context is the primary source of agent tool misuse [unverified].

## What Implicit Context Looks Like

Systems accumulate implicit knowledge over time:

- Specialized query syntax (e.g., `status:open assignee:me` in a search API)
- Domain terminology (e.g., "sprint" vs "iteration" — which term does the API use?)
- Resource relationships (e.g., projects contain issues, issues belong to sprints — what order do you need to traverse?)
- Encoding conventions (e.g., IDs are strings, not integers; dates are UTC, not local)

None of this is typically documented in terse API references. All of it is necessary for an agent to use the tool correctly without trial and error.

## Unambiguous Parameter Names

Parameter names are the first point of failure. A parameter named `user` is ambiguous: is it a user ID, a username, an email, a display name? The agent will guess — and guess wrong at a rate proportional to the ambiguity.

Fix: `user_id` (integer), `username` (string, lowercase), `email` (string, RFC 5322). The name communicates the type and format; the description confirms it.

This applies to all parameters:

- `date` → `start_date`, `end_date`
- `id` → `project_id`, `task_id`, `user_id`
- `type` → `event_type`, `resource_type`

## Steering Behavior Through Error Messages

Error messages are part of the tool description in practice — they are what the agent reads when a call fails. Treat them as guidance, not just diagnostics:

- Instead of "Query too broad, returned 0 results" → "Query too broad. Consider narrowing by date range or adding a status filter. Use `status:open` to filter active items."
- Instead of "Invalid parameter" → "Invalid `user_id` format. Expected integer, received string. User IDs are numeric identifiers found in the users index."

An error message that tells the agent what to try next reduces retry failures and context waste.

## Iterating on Descriptions

Description quality degrades silently. As the underlying system changes, descriptions that were accurate become stale. As agents encounter new use cases, gaps in descriptions emerge. Treat description iteration the same as code maintenance:

- Review descriptions when the underlying API changes
- Log agent failures that trace to tool misuse and identify the description gap
- Update descriptions based on observed failure patterns, not anticipated ones

## Example

The following pair shows a Jira MCP tool description before and after applying the new-hire framing. The terse version describes the interface; the onboarding version provides the context an agent needs to use it correctly.

```python
# Before: accurate but opaque — agent must guess date format, ID type, and query syntax
{
    "name": "get_sprint_issues",
    "description": "Get issues for a sprint.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "string"},
            "status": {"type": "string"}
        },
        "required": ["sprint_id"]
    }
}
```

```python
# After: written as onboarding — includes domain conventions, ID format, filter values, and traversal order
{
    "name": "get_sprint_issues",
    "description": (
        "Retrieve all issues assigned to a Jira sprint. "
        "sprint_id is a numeric string (e.g. '42'), not the sprint name. "
        "To find a sprint_id, first call list_sprints with the board_id. "
        "status filters to a single status; accepted values are: 'To Do', 'In Progress', 'Done'. "
        "Omit status to return issues in all statuses. "
        "Returns a list of objects with keys: id (string), summary, status, assignee (username string), story_points."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "sprint_id": {
                "type": "string",
                "description": "Numeric sprint ID (not name). Obtain from list_sprints."
            },
            "status": {
                "type": "string",
                "description": "Optional. One of: 'To Do', 'In Progress', 'Done'."
            }
        },
        "required": ["sprint_id"]
    }
}
```

The improved description makes explicit three things a new hire would learn on day one: sprint IDs are numeric strings, you must call `list_sprints` first to get one, and `status` only accepts the exact strings shown. None of this is in the terse version, so an agent using that version will guess — and fail — on each point.

## Key Takeaways

- Write as if training a new hire: explicit about implicit context, domain conventions, and resource relationships
- Use unambiguous parameter names that include type and context (`user_id`, `start_date`, not `user`, `date`)
- Treat error messages as guidance — tell the agent what to try next, not just what went wrong
- Minor description refinements produce dramatic accuracy improvements — iterate on descriptions the same way you would on code
- Keep descriptions current as the underlying system evolves; stale descriptions are a silent failure source

## Unverified Claims

- The gap between accurate-but-minimal and accurate-with-context descriptions is the primary source of agent tool misuse [unverified]

## Related

- [Tool Description Quality](tool-description-quality.md)
- [Tool Engineering](tool-engineering.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — mistake-proofing tools so agents cannot call them incorrectly
- [Agent-Computer Interface](agent-computer-interface.md) — tool design as UX discipline for agents
- [Consolidate Agent Tools](consolidate-agent-tools.md)
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md) — structured errors that guide agents to the correct next action
- [Semantic Tool Output](semantic-tool-output.md) — designing tool output for agent readability
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md) — enforcing correct tool inputs through schema design
- [Token-Efficient Tool Design](token-efficient-tool-design.md) — designing tools that minimize context consumption
- [The Implicit Knowledge Problem](../anti-patterns/implicit-knowledge-problem.md) — why implicit context that agents cannot find causes silent failures
