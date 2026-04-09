---
title: "Subagent Schema-Level Tool Filtering for AI Agents"
description: "Restrict subagent capabilities by filtering their tool schemas — making unauthorized tool use structurally impossible rather than relying on prompt"
tags:
  - agent-design
  - source:opendev-paper
aliases:
  - Tool Calling Schema Standards
  - Tool Minimalism
  - Tool Schema Design
---
# Subagent Schema-Level Tool Filtering

> Restrict subagent capabilities by filtering their tool schemas — making unauthorized tool use structurally impossible rather than relying on prompt instructions.

!!! info "Also known as"
    Tool Calling Schema Standards, Tool Minimalism, Tool Schema Design

## Schema Filtering vs. Runtime Checks

Runtime checks reject forbidden tool calls after the model has already planned to use them. Schema filtering removes tools from the subagent's schema entirely, so the model cannot form the intent to call tools it has never seen ([Bui, 2025 §2.2.2](https://arxiv.org/abs/2603.05344)).

This distinction matters. A runtime rejection wastes an inference cycle and creates a failure the model must recover from [unverified]. Schema filtering eliminates the failure mode at the structural level — the model selects only from tools it can see.

## Filtered Tool Sets by Role

The OPENDEV agent defines built-in subagent types, each receiving a filtered subset of the shared tool registry ([Bui, 2025 §2.2.7, App G](https://arxiv.org/abs/2603.05344)):

| Subagent | Tool Access |
|----------|-------------|
| Strategic Planner | Read-only tools plus extended reasoning — no write operations |
| Code Explorer | Read-only codebase navigation tools |

Additional specialized subagents are registered in the subagent capability matrix (Appendix G). Each subagent's schema is the minimum set required for its role. Tools outside the allowlist do not appear in the schema sent to the model.

## Prompt + Schema Dual Constraint

Schema filtering pairs with prompt specialization. Subagent prompts inherit the base system prompt plus role-specific sections that emphasize constraints and responsibilities ([Bui, 2025 §2.2.7](https://arxiv.org/abs/2603.05344)).

The prompt tells the model what to do; the schema prevents it from doing anything else. Neither mechanism alone is sufficient — prompts can be overridden by strong context, and schema filtering does not guide the model toward the *right* tool among those available. Together, they create a dual constraint that is harder to violate than either alone.

## Declarative Subagent Specs

The design evolved from inline subagent code to a declarative SubAgentSpec registry ([Bui, 2025 §2.2.1](https://arxiv.org/abs/2603.05344)). Each spec declares:

- Role description and specialized prompt sections
- Tool allowlist (schema filter)
- Execution constraints (e.g., read-only, no network)

Compilation (SubAgentSpec → CompiledSubAgent) shares the tool registry for cheap construction while isolating runtime state through filtered schemas and fresh message history.

## Parallel Execution

Multiple subagents with filtered schemas can run concurrently for independent exploration tasks ([Bui, 2025 §2.2.7](https://arxiv.org/abs/2603.05344)). Schema filtering makes this safe — each subagent operates within its structural capability boundary regardless of what other subagents are doing.

## Example

The following shows a declarative SubAgentSpec for a read-only Code Explorer subagent, demonstrating how the tool allowlist is the schema filter — the model receives only these tools in its schema and cannot form intent to call anything else.

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

Both subagents can run concurrently — their filtered schemas ensure neither can touch files the other is reading, and neither can perform write operations regardless of what appears in their prompts.

## Key Takeaways

- Schema filtering is stronger than runtime rejection — the model cannot call tools absent from its schema
- Define filtered tool sets per subagent role: minimum tools required, nothing more
- Combine schema filtering with prompt specialization for a dual constraint
- Use declarative specs (SubAgentSpec) to define tool allowlists alongside role prompts
- Filtered schemas enable safe parallel subagent execution

## Related

- [Agent Composition Patterns](../agent-design/agent-composition-patterns.md)
- [Specialized Agent Roles](../agent-design/specialized-agent-roles.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Tool Minimalism and High-Level Prompting](../tool-engineering/tool-minimalism.md)
- [Orchestrator-Worker Pattern](orchestrator-worker.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](sub-agents-fan-out.md)
- [Declarative Multi-Agent Composition](declarative-multi-agent-composition.md)
- [Multi-Agent SE Design Patterns: A Taxonomy Across 94 Papers](multi-agent-se-design-patterns.md)
- [Emergent Behavior Sensitivity](emergent-behavior-sensitivity.md)
- [Tool Calling Schema Standards](../standards/tool-calling-schema-standards.md)
