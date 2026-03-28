---
title: "Observation Masking: Filter Tool Outputs from Context"
description: "Observation masking removes processed tool outputs from conversation history to keep the context window lean, replacing each output with a one-line summary."
tags:
  - context-engineering
  - cost-performance
---

# Observation Masking: Filter Tool Outputs from Context

> Strip intermediate tool results from conversation history once they have served their purpose to keep active context lean without losing the work product.

## The Problem

Tool calls are a primary source of context growth in agent workflows. Every tool output — a file read, a search result, test runner output, a lint report — injects tokens into the context window. Most of those tokens are consumed once during synthesis and never referenced again [unverified]. They remain in context, consuming budget and diluting attention.

The useful artifact of a tool call is typically what the agent produced from it (the code written, the decision made, the summary), not the raw tool output that informed it.

## How Observation Masking Works

Observation masking removes processed tool outputs from conversation history before the next inference call. The agent synthesises a result from the tool output; once synthesis is complete, the raw output is dropped from context [unverified].

The retention decision is based on whether the agent will need to reference the tool output again:

| Tool output type | Retain or mask? |
|-----------------|----------------|
| File content (read once, then edited) | Mask after edit |
| Search results (synthesised into plan) | Mask after synthesis |
| Test output (failure mode identified) | Mask after fix is applied |
| Schema definition (queried throughout task) | Retain |
| API response (used in one step) | Mask after use |
| Reference documentation (checked repeatedly) | Retain |

The heuristic: if the agent has extracted what it needs from the tool output and expressed it as a decision or artifact, the raw output is no longer needed.

## Implementation Considerations

Observation masking is applied at the conversation history management layer — post-processing the message list before each inference call, not after:

1. Track which tool outputs have been referenced in agent outputs
2. After an agent turn that references a tool output, flag the output as processed
3. Before the next inference call, remove flagged tool outputs from the history
4. Optionally replace them with a one-line summary ("read `src/auth.ts`, identified session validation pattern")

The one-line replacement preserves agent traceability (the agent can see what it consulted) without the full token cost of the original output.

## What Masking Does Not Address

Observation masking reduces context growth from intermediate tool results — it does not address:

- System prompt size
- Conversation history from prior reasoning turns
- Tool outputs the agent needs to retain for repeated reference

For those cases, combine masking with context compression (tiered summarisation and offloading) and on-demand retrieval for content the agent needs to consult multiple times.

## Example

An agent is asked to refactor `src/auth/session.ts`. It reads the file, makes the edit, then runs the test suite. Without masking, all three tool outputs remain in the conversation history:

**Before masking — conversation history after three tool calls:**

```
[tool: read_file] → 312 lines of session.ts content
[tool: edit_file] → diff output confirming the change
[tool: run_tests] → 847 lines of pytest output, 1 failure
```

All three outputs stay in context for the next inference call, even though the file content is now stale (it has been edited) and the passing test lines provide no further signal.

**After masking — conversation history before the next inference call:**

```
[masked: read_file src/auth/session.ts — read 312 lines, identified validateSession return type]
[masked: edit_file src/auth/session.ts — applied refactor, 14 lines changed]
[tool: run_tests] → 847 lines of pytest output, 1 failure  ← retained: agent still needs this
```

The masking layer replaces the completed `read_file` and `edit_file` outputs with one-line summaries. The `run_tests` output is retained because the agent must still interpret the failure and act on it. Once the failure is fixed and tests pass, that output is also replaced with a summary line.

The masking logic applied here:

```python
def should_mask(tool_name: str, tool_output: str, agent_turn_after: str) -> bool:
    # Mask file reads once the agent has produced an edit referencing the file
    if tool_name == "read_file" and "edit_file" in agent_turn_after:
        return True
    # Mask edit confirmations once the agent has moved past them
    if tool_name == "edit_file" and "run_tests" in agent_turn_after:
        return True
    # Retain test output until the agent has produced a fix
    if tool_name == "run_tests":
        return False
    return False

def summarise(tool_name: str, tool_output: str) -> str:
    # Return a one-line summary replacing the full output
    ...
```

The token saving from masking `read_file` and `edit_file` in this example is roughly 1,100 tokens — the cost of re-including stale content in every subsequent inference call for the remainder of the session.

## Key Takeaways

- Most tool outputs are referenced once and then abandoned — masking them prevents unnecessary context accumulation.
- Retain tool outputs when the agent will query them repeatedly; mask them after single-use synthesis.
- Apply masking at the conversation history management layer, before each inference call.
- Replace masked outputs with a brief summary line to preserve traceability without the full token cost.

## Unverified Claims

- Most tokens from tool outputs are consumed once and never referenced again [unverified]
- Once synthesis is complete, the raw tool output is dropped from context [unverified]

## Related

- [Context Engineering: The Practice of Shaping Agent Context](context-engineering.md)
- [Context Compression Strategies: Offloading and Summarisation](context-compression-strategies.md)
- [Prompt Caching as Architectural Discipline](prompt-caching-architectural-discipline.md)
- [Context-Injected Error Recovery for AI Agent Development](context-injected-error-recovery.md)
- [Context Window Management: The Dumb Zone](context-window-dumb-zone.md)
- [Error Preservation in Context for AI Agent Development](error-preservation-in-context.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [The Infinite Context](../anti-patterns/infinite-context.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](../agent-design/agent-turn-model.md)
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md)
- [Filter, Aggregate, and Execution Environment](filter-aggregate-execution-env.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [Lost in the Middle: The U-Shaped Attention Curve](lost-in-the-middle.md)
