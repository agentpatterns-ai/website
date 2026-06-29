---
title: "Observation Masking: Filter Tool Outputs from Context"
term: "Observation Masking"
description: "Observation masking removes processed tool outputs from conversation history to keep the context window lean, replacing each output with a one-line summary."
aliases:
  - Tool Output Masking
  - Context Masking
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: adopted
---

# Observation Masking: Filter Tool Outputs from Context

> Strip intermediate tool results from conversation history once they have served their purpose to keep active context lean without losing the work product.

Learn it hands-on with [Masking the Tail](https://learn.agentpatterns.ai/context-engineering/observation-masking/), a guided lesson with quizzes.

## The problem

Tool calls are a primary source of context growth in agent workflows. Every tool output injects tokens into the context window: a file read, a search result, test runner output, a lint report. In software engineering agent benchmarks, observation tokens account for roughly 84% of trajectory content. The agent consumes most of them once during synthesis and never references them again ([arXiv 2508.21433](https://arxiv.org/abs/2508.21433)). They stay in context, consuming budget and diluting attention.

The useful artifact of a tool call is usually what the agent produced from it: the code written, the decision made, the summary. The raw tool output that informed it is not.

## How observation masking works

Observation masking removes processed tool outputs from conversation history before the next inference call. The agent synthesizes a result from the tool output. Once synthesis is complete, the raw output is replaced with a [compact summary](context-compression-strategies.md) or dropped entirely.

The retention decision turns on whether the agent will need to reference the tool output again:

| Tool output type | Retain or mask? |
|-----------------|----------------|
| File content (read once, then edited) | Mask after edit |
| Search results (synthesized into plan) | Mask after synthesis |
| Test output (failure mode identified) | Mask after fix is applied |
| Schema definition (queried throughout task) | Retain |
| API response (used in one step) | Mask after use |
| Reference documentation (checked repeatedly) | Retain |

The heuristic is simple. Once the agent has extracted what it needs from the tool output and expressed it as a decision or artifact, the raw output is no longer needed.

## Implementation considerations

Apply observation masking at the conversation history management layer. Post-process the message list before each inference call, not after:

1. Track which tool outputs the agent has referenced in its outputs.
2. After an agent turn that references a tool output, flag the output as processed.
3. Before the next inference call, remove flagged tool outputs from the history.
4. Optionally replace them with a one-line summary, such as "read `src/auth.ts`, identified session validation pattern".

The one-line replacement preserves traceability, so the agent can see what it consulted, without the full token cost of the original output.

## Why it works

Retaining stale tool outputs degrades inference quality two ways. First, transformer attention is quadratic: adding tokens raises the cost of every later call and spreads attention thinner across all token pairs ([context rot research, Chroma 2025](https://www.trychroma.com/research/context-rot)). Second, outdated content that still looks relevant acts as a distractor. A file read that has since been edited is one example. Models attend to it even when it no longer reflects the current state, which skews generation toward stale assumptions. Removing processed outputs cuts both the cost and the distraction, and it keeps the synthesized result that the agent actually needs.

## What masking does not address

Observation masking reduces context growth from intermediate tool results. It does not address:

- System prompt size
- Conversation history from prior reasoning turns
- Tool outputs the agent needs to retain for repeated reference

For those cases, combine masking with context compression (tiered summarization and offloading) and on-demand retrieval for content the agent needs to consult several times.

## When this backfires

Masking is a heuristic, not a guarantee. It degrades quality in four cases.

Reference outputs are masked too early. Schema definitions, API contracts, or documentation the agent consults repeatedly are not single-use. Masking them forces the agent to re-read or hallucinate their contents on later turns. Keep such content available through [on-demand retrieval](retrieval-augmented-agent-workflows.md) instead.

Synthesis is not yet complete. Masking a test failure output before the agent has produced and verified a fix removes the ground truth mid-task. Confirm the retention decision, do not assume it.

Models use extended reasoning. Benchmarks show that masking reduces solve rate by about 10% for models with extended thinking enabled, where the model benefits from inspecting its full observation history during long chains of thought ([arXiv 2508.21433](https://arxiv.org/abs/2508.21433)). Prefer LLM-based summarization over hard masking in those configurations.

Domain differs from software engineering. The efficiency advantage of masking assumes observation tokens dominate context, about 84% in SE benchmarks. In domains where observations are brief and reasoning turns are long, the gain is smaller and the risk of over-masking is higher.

## Example

An agent is asked to refactor `src/auth/session.ts`. It reads the file, makes the edit, then runs the test suite. Without masking, all three tool outputs stay in the conversation history.

Before masking, the conversation history after three tool calls:

```
[tool: read_file] → 312 lines of session.ts content
[tool: edit_file] → diff output confirming the change
[tool: run_tests] → 847 lines of pytest output, 1 failure
```

All three outputs stay in context for the next inference call, even though the file content is now stale after the edit and the passing test lines give no further signal.

After masking, the conversation history before the next inference call:

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

- Most tool outputs are referenced once and then abandoned — they account for roughly 84% of trajectory content in SE benchmarks — so masking them prevents unnecessary context accumulation.
- Retain tool outputs when the agent will query them repeatedly; mask them after single-use synthesis.
- Apply masking at the conversation history management layer, before each inference call.
- Replace masked outputs with a brief summary line to preserve traceability without the full token cost.

## Related

- [Context Engineering: The Practice of Shaping Agent Context](context-engineering.md)
- [Context Compression Strategies: Offloading and Summarisation](context-compression-strategies.md)
- [Error Preservation in Context for AI Agent Development](error-preservation-in-context.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md)
- [Filter, Aggregate, and Execution Environment](filter-aggregate-execution-env.md)
- [Context Budget Allocation: Every Token Has a Cost](context-budget-allocation.md)
- [The Infinite Context](../anti-patterns/infinite-context.md)
