---
title: "Subagent Schema-Level Tool Filtering for AI Agents"
term: "Subagent Schema-Level Tool Filtering"
description: "Restrict subagent capabilities by filtering their tool schemas, making unauthorized tool use structurally impossible rather than relying on prompt instructions."
tags:
  - agent-design
  - source:opendev-paper
  - tool-agnostic
  - multi-agent
aliases:
  - Tool Calling Schema Standards
  - Tool Minimalism
  - Tool Schema Design
last_reviewed: 2026-06-13
maturity: adopted
---

# Subagent Schema-Level Tool Filtering

> Restrict subagent capabilities by filtering their tool schemas — making unauthorized tool use structurally impossible rather than relying on prompt instructions.

!!! info "Also known as"
    Tool Calling Schema Standards, Tool Minimalism, Tool Schema Design

## Schema filtering versus runtime checks

Runtime checks reject forbidden tool calls after the model has already planned to use them. Schema filtering removes tools from the subagent's schema entirely. The model cannot form the intent to call tools it has never seen ([Bui, 2026 §2.2.2](https://arxiv.org/abs/2603.05344)).

This distinction matters. A runtime rejection happens after the model has already spent tokens planning the call, and recovery needs another inference turn. Schema filtering removes the failure mode at the structural level. The model selects only from tools it can see.

## Filtered tool sets by role

The OPENDEV agent defines built-in subagent types. Each one receives a filtered subset of the shared tool registry ([Bui, 2026 §2.2.7, App G](https://arxiv.org/abs/2603.05344)):

| Subagent | Tool access |
|----------|-------------|
| Strategic Planner | Read-only tools plus extended reasoning — no write operations |
| Code Explorer | Read-only codebase navigation tools |

Other specialized subagents are registered in the subagent capability matrix (Appendix G). Each subagent's schema is the minimum set its role needs. Tools outside the allowlist do not appear in the schema sent to the model.

## Prompt and schema dual constraint

Schema filtering pairs with prompt specialization. Subagent prompts inherit the base system prompt plus role-specific sections that stress constraints and responsibilities ([Bui, 2026 §2.2.7](https://arxiv.org/abs/2603.05344)). Anthropic's guidance on writing effective agent tools makes the same point: giving an agent only the tools relevant to its task reduces ambiguity and improves selection accuracy ([Anthropic Engineering, 2025](https://www.anthropic.com/engineering/writing-tools-for-agents)).

The prompt tells the model what to do. The schema stops it from doing anything else. Neither mechanism is enough alone. Strong context can override prompts, and schema filtering does not guide the model toward the right tool among those available. Together they create a dual constraint that is harder to violate than either alone.

## Declarative subagent specs

The design moved from inline subagent code to a declarative SubAgentSpec registry ([Bui, 2026 §2.2.1](https://arxiv.org/abs/2603.05344)). Each spec declares:

- Role description and specialized prompt sections
- Tool allowlist (schema filter)
- Execution constraints (for example, read-only, no network)

Compilation (SubAgentSpec → CompiledSubAgent) shares the tool registry for cheap construction. It isolates runtime state through filtered schemas and fresh message history.

## Parallel execution

Multiple subagents with filtered schemas can run at the same time for independent exploration tasks ([Bui, 2026 §2.2.7](https://arxiv.org/abs/2603.05344)). Schema filtering makes this safe. Each subagent works within its structural capability boundary, whatever other subagents are doing.

## Example

The example below shows a declarative SubAgentSpec for a read-only Code Explorer subagent. The tool allowlist is the schema filter: the model receives only these tools in its schema and cannot form intent to call anything else.

```python
from opendev import SubAgentSpec, ToolRegistry

code_explorer_spec = SubAgentSpec(
    name="code_explorer",
    role_description="Navigates and reads the codebase to answer questions about structure and logic.",
    system_prompt_sections=[
        "You are a read-only code analyst. Do not modify, create, or delete files.",
        "Summarize findings concisely — return extracted facts, not raw file contents.",
    ],
    tool_allowlist=[
        ToolRegistry.get("read_file"),
        ToolRegistry.get("list_directory"),
        ToolRegistry.get("search_code"),
        ToolRegistry.get("get_symbol_definition"),
    ],
    # write tools (write_file, run_command, etc.) are absent — not in schema
)

# Compilation shares the shared registry but filters at construction time
explorer = code_explorer_spec.compile(shared_registry=ToolRegistry)
```

The Strategic Planner receives a different filtered set — read-only tools plus an extended reasoning tool, still no write operations:

```python
strategic_planner_spec = SubAgentSpec(
    name="strategic_planner",
    role_description="Produces implementation plans using extended reasoning. No writes.",
    tool_allowlist=[
        ToolRegistry.get("read_file"),
        ToolRegistry.get("search_code"),
        ToolRegistry.get("extended_thinking"),
    ],
)
```

Both subagents can run at the same time. Their filtered schemas mean neither can touch files the other is reading, and neither can perform write operations whatever appears in their prompts.

## When this backfires

Schema filtering adds structural rigidity. When it fails to match the actual workload, the costs outweigh the safety benefit:

- Over-scoped allowlists: a subagent given too broad a tool allowlist gives false safety assurance while it can still cause harm within its scope. Allowlists need ongoing maintenance as the tool registry changes.
- Allowlist maintenance lag: adding a new tool to the [shared registry](../standards/tool-calling-schema-standards.md) does not grant it to existing subagents. Removing a tool from a spec that still references it causes compilation errors. The SubAgentSpec layer must stay in sync with the live tool registry.
- Misuse within the allowlist: schema filtering stops calls to absent tools but does not stop misuse of present ones. A Code Explorer subagent with `search_code` can still run excessive queries or leak discovered content, so prompt specialization must handle safety within the allowlist.
- Parallel execution overhead: spawning multiple filtered subagents adds orchestration overhead (compilation, context initialization, result aggregation). For simple linear tasks, a single agent with a broad schema is cheaper.
- "Structurally impossible" is a ceiling, not a guarantee: schema filtering narrows intent to the visible tool set, but tools inside the allowlist still expose indirect pathways. [CVE-2026-22708](https://github.com/cursor/cursor/security/advisories/GHSA-82wg-qcm4-fp2w) showed that Cursor Agent's terminal allowlist could be bypassed through shell built-ins and environment-variable manipulation. Poisoning the environment of allowed commands produced effects the allowlist never sanctioned. The same pattern recurs whenever an allowlisted tool (shell, package manager, HTTP client) can be steered into unintended behavior through its inputs. Treat schema filtering as one layer of defense in depth, not as a boundary the model cannot reason around.

## Key Takeaways

- Schema filtering is stronger than runtime rejection — the model cannot call tools absent from its schema
- Define filtered tool sets per subagent role: minimum tools required, nothing more
- Combine schema filtering with prompt specialization for a dual constraint
- Use declarative specs (SubAgentSpec) to define tool allowlists alongside role prompts
- Filtered schemas enable safe parallel subagent execution

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Specialized Agent Roles](../agent-design/specialized-agent-roles.md)
- [Agent Composition Patterns](../agent-design/agent-composition-patterns.md)
- [Declarative Multi-Agent Composition](declarative-multi-agent-composition.md)
- [Typed Schemas at Agent Boundaries](typed-schemas-at-agent-boundaries.md)
- [Tool Calling Schema Standards](../standards/tool-calling-schema-standards.md)
- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md)
