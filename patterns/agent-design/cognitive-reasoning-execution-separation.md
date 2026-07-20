---
title: "Cognitive Reasoning vs Execution: A Two-Layer Agent"
term: "Cognitive Reasoning vs Execution"
description: "Separate the agent layer that decides what to do from the layer that acts — typed tool interfaces enforce the boundary and make each independently testable."
tags:
  - agent-design
  - multi-agent
  - cost-performance
  - tool-agnostic
aliases:
  - reasoning-execution separation
  - two-layer agent architecture
  - cognitive-execution split
last_reviewed: 2026-06-12
maturity: adopted
---

# Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture

> Separate the agent layer that decides from the layer that acts — typed tool interfaces enforce the boundary and make each independently testable.

## The split

Production LLM agents mix two concerns that should be separate. This is the same cut as [separation of knowledge and execution](separation-of-knowledge-and-execution.md):

- Reasoning layer: decides which tools to call, in what order, and how to interpret results. It holds no execution logic.
- Execution layer: receives typed tool calls and acts on them. It holds no decision logic.

The [arXiv:2602.10479 survey of production agent architectures](https://arxiv.org/abs/2602.10479) identifies this split as the foundational pattern for scaling agentic systems. When you conflate the layers, the reasoning layer fills with implementation details that obscure intent, and the execution layer gathers decision branches you cannot test in isolation.

## Typed tool interfaces as the seam

The contract between layers is a JSON schema parameter definition. Each tool the reasoning layer can invoke has a name, a purpose, and typed inputs. The reasoning layer picks which tool to call from the schema description. The execution layer validates the call against the schema before acting.

[Anthropic's advanced tool use research](https://www.anthropic.com/engineering/advanced-tool-use) describes how to route tool results programmatically instead of always returning them to the model's context window. A code execution environment processes intermediate results, and only the final filtered result reaches the reasoning layer's context.

## How Claude Code models this

Claude Code's [sub-agent architecture](https://code.claude.com/docs/en/sub-agents) makes the split concrete. Sub-agents get scoped tool permissions rather than broad access. An exploration sub-agent holds read-only tools with no write permissions. An orchestrating sub-agent holds decision and delegation tools. The runtime enforces the constraint at the tool permission level, not by instruction. Sub-agent definitions specify an explicit `tools` allowlist and a `permissionMode` that the runtime enforces regardless of what the system prompt says.

## Dynamic tool discovery

Loading every tool definition into the reasoning layer's context at startup is wasteful. [Anthropic's context engineering patterns](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) recommend keeping context lean by loading only what is needed. The same principle applies to tool registries: surface tool schemas to the reasoning layer on demand rather than pre-loading the full set.

Execution-layer tools stay available without pre-occupying reasoning context.

## Workload-specialized model routing

The separation enables [model routing by layer](../../token-engineering/cost-aware-agent-design.md). Reasoning tasks need instruction-following depth and long-context coherence, which suits larger frontier models. Execution tasks are often deterministic, short-context, and high-frequency, which suits fast, low-cost models.

Running execution on cheaper models while reserving frontier capacity for reasoning cuts per-task cost. This routing is one of the main cost levers the layer separation enables.

```mermaid
graph TD
    R[Reasoning Layer<br>Frontier Model] -->|typed tool call| T[Tool Interface<br>JSON Schema]
    T -->|validated call| E[Execution Layer<br>Fast/Cheap Model]
    E -->|structured result| T
    T -->|filtered result| R
```

## Why it works

Layer separation removes two categories of failure that compound in monolithic agents. First, when a reasoning model must also manage implementation details — file handles, retry loops, API pagination — those details compete with planning content in the context window and degrade decision quality. Keeping execution logic out of the reasoning context preserves the signal-to-noise ratio for the reasoning model, the core discipline of [context engineering](../../context-engineering/context-engineering.md). Second, execution failures become isolated and attributable. You can retry or rerun a failed tool call on its own without re-invoking the reasoning layer. Side effects such as writes and API calls stay in the execution layer, where you can audit or roll them back without touching reasoning state.

## When this backfires

The split adds overhead that is not always justified:

- Short-lived single-turn tasks: for tasks that finish in one or two tool calls, the typed-interface seam adds schema validation and context-passing overhead with no testability benefit. A simple function call is often clearer.
- High-latency layer seams: if the execution layer is a remote service — an [orchestrator-worker](../multi-agent/orchestrator-worker.md) split across processes — every reasoning-to-execution round-trip adds network latency. Tight feedback loops such as reactive agents and streaming responses may need collocated logic instead.
- Schema versioning churn: typed interfaces become a maintenance burden when tool signatures change often. You must version the schema contract and keep both layers in sync, which offsets the testing advantages in fast-iteration codebases.

## Independent testability

Each layer can be validated without the other:

- Reasoning layer: given a known task and known tool schemas, does the agent produce the correct tool call sequence? Feed it canned execution responses to verify.
- Execution layer: given a valid typed tool call (a validated `BaseModel`), does the execution produce the expected side effect and return value? No reasoning layer required.

Without a schema contract, testing requires running the full system.

## Example

A minimal Python sketch showing the boundary between layers. The reasoning layer emits a typed call. The execution layer validates it against the schema before acting.

```python
from pydantic import BaseModel

# Tool interface — the schema contract between layers
class WriteFileCall(BaseModel):
    path: str
    content: str

# Execution layer: validates the typed call, then acts
def execute_write_file(call: WriteFileCall) -> dict:
    with open(call.path, "w") as f:
        f.write(call.content)
    return {"status": "ok", "path": call.path}

# Reasoning layer: decides what to call (LLM output parsed into typed model)
raw_tool_call = {"path": "output.txt", "content": "hello"}
validated_call = WriteFileCall(**raw_tool_call)   # schema validation at the seam
result = execute_write_file(validated_call)        # execution layer receives only typed input
```

The reasoning layer never opens files. The execution layer never decides what to write. The `WriteFileCall` schema is the enforced boundary.

## Key Takeaways

- The reasoning layer decides; the execution layer acts — no cross-layer logic belongs in either.
- Typed tool interfaces (JSON schema) are the enforced contract between layers.
- Programmatic tool calling routes intermediate execution results away from the reasoning context window.
- Claude Code sub-agents instantiate this pattern via tool permission scoping, not just by instruction.
- The split enables workload-appropriate model routing: large models for reasoning, fast models for execution.

## Related

- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Three Reasoning Spaces](three-reasoning-spaces.md)
- [Orchestrator-Worker Pattern](../multi-agent/orchestrator-worker.md)
- [Execution-First Delegation](execution-first-delegation.md)
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md)
- [Dynamic Tool Fetching Breaks KV Cache](../anti-patterns/dynamic-tool-fetching-cache-break.md)
- [Context Engineering](../../context-engineering/context-engineering.md)
- [Permission-Gated Custom Commands](../../security/permission-gated-commands.md)
- [LLM-as-Code Agentic Programming for Agent Harnesses](llm-as-code-agentic-programming.md) — Pushes the layer boundary one step further: orchestration itself moves into the program, with the LLM as a callable component
