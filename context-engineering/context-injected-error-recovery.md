---
title: "Context-Injected Error Recovery for AI Agent Development"
term: "Context-Injected Error Recovery"
description: "When a tool call fails, inject structured error context (the error message, previous attempts, and targeted recovery suggestions) into the next inference call to prevent retry loops."
aliases:
  - error context injection
  - structured error recovery
tags:
  - agent-design
  - workflows
  - source:opendev-paper
  - tool-agnostic
  - context-engineering
last_reviewed: 2026-05-27
maturity: emerging
---

# Context-Injected Error Recovery

> When a tool call fails, inject structured error context (the error, prior attempts, and recovery suggestions) into the next inference call to prevent retry loops.

## The problem: blind retries

When a tool call returns an error, most agent harnesses pass only the raw error message back to the model ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). The model retries with little extra information, and often repeats the same approach. After several identical failures, the agent enters a retry loop that consumes context window and tokens without progress.

The root cause is information asymmetry. The model lacks the context it needs to choose a different strategy on the first retry ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)).

## How context injection works

Instead of forwarding the raw error, the harness builds a structured error context block with three parts ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)):

1. Error message — the original error output, preserved word for word.
2. Previous attempts — a record of prior tries at the same operation within the current session, including what was tried and what failed.
3. Targeted recovery suggestions — harness-generated hints based on the error type. For example, "file not found" suggests checking the path, and "permission denied" suggests checking credentials or sandbox restrictions.

The harness injects this block into the next prompt. The model then sees the full failure situation rather than a single data point.

## Structured context format

A practical error context block follows this shape:

```
[Error Recovery Context]
Operation: edit_file("src/config.ts", ...)
Error: File not found: src/config.ts

Previous attempts (this session):
  1. edit_file("src/config.ts", ...) → File not found
  2. read_file("src/config.ts") → File not found

Recovery suggestions:
  - Verify file path exists (use list_directory or find_file)
  - Check for typos in directory or filename
  - The file may have been moved or renamed earlier in this session
```

The key property is structure: the model receives what went wrong, what has already been tried, and which alternatives are still open ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)).

## Impact

Context-injected error recovery reduces retry loops by 25–40% compared to passing raw error messages alone ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). The improvement comes from removing the first two to three redundant retries that would otherwise happen before the model works out on its own that a different approach is needed.

## Relationship to loop detection

Loop detection and error recovery work together, but act at different points in the failure lifecycle:

- error recovery acts at the moment of failure — it stops loops from forming by giving the model better information on the first retry ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344))
- loop detection acts after repeated failures — it spots and interrupts loops that have already formed

Error recovery lightens the load on loop detection. The 25–40% reduction in retry loops means fewer cases reach the threshold that triggers detection ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). Loop detection is still needed as a safety net when the enriched context is not enough.

## Implementation considerations

The harness keeps a per-session log of failed tool calls, keyed by operation type and target. On each failure, the harness does four things:

1. Look up prior failures for the same operation and target pair.
2. Select recovery suggestions from a mapping of error patterns to hints.
3. Assemble the structured context block.
4. Inject the block into the next prompt, right after the error result.

Recovery suggestions should be general enough to avoid prescribing a single fix, but specific enough to rule out approaches already tried. The harness keeps the suggestion catalog as a static mapping, so no LLM inference is needed to generate suggestions.

This aligns with emerging ReAct-agent reliability guidance: the LangGraph [Production Reliability RFC](https://github.com/langchain-ai/langgraph/issues/6617) proposes classifying errors and surfacing structured reasoning so retries are informed rather than blind.

## When this backfires

Context injection adds tokens to every retry prompt. Three conditions make this trade-off a poor one:

1. Near-context-limit sessions — injecting prior-attempt history and recovery hints into a prompt that is already large can push the total context past the model's limit. This truncates earlier session history and introduces new errors.
2. High-frequency, low-variance errors — when errors repeat across many different operations, such as a systemic auth failure or a network outage, the recovery catalog produces the same generic hints on every retry. This adds tokens without adding signal.
3. Stale suggestion catalog — if the hint mappings are not kept current as the tool surface changes, they can suggest approaches that no longer apply or that contradict current tool behavior, which misleads the model.

## Example

A Python harness that builds and injects error context on each tool failure:

```python
from dataclasses import dataclass, field

RECOVERY_HINTS: dict[str, list[str]] = {
    "FileNotFoundError": [
        "Verify the file path exists using list_directory or find_file",
        "Check for typos in directory or filename",
        "The file may have been moved or renamed earlier in this session",
    ],
    "PermissionError": [
        "Check file permissions or sandbox restrictions",
        "Try reading the file before writing to confirm access",
    ],
    "TimeoutError": [
        "Reduce the scope of the operation",
        "Break the task into smaller steps",
    ],
}

@dataclass
class FailureRecord:
    operation: str
    target: str
    error: str

@dataclass
class ErrorContextBuilder:
    history: list[FailureRecord] = field(default_factory=list)

    def record_failure(self, operation: str, target: str, error: str) -> None:
        self.history.append(FailureRecord(operation, target, error))

    def build_context(self, operation: str, target: str, error: str) -> str:
        self.record_failure(operation, target, error)

        prior = [
            f"  {i}. {r.operation}(\"{r.target}\") → {r.error}"
            for i, r in enumerate(self.history, 1)
            if r.operation == operation and r.target == target
        ]

        error_type = error.split(":")[0].strip()
        hints = RECOVERY_HINTS.get(error_type, ["Try an alternative approach"])

        lines = [
            "[Error Recovery Context]",
            f"Operation: {operation}(\"{target}\")",
            f"Error: {error}",
            "",
            f"Previous attempts (this session): {len(prior)}",
            *prior,
            "",
            "Recovery suggestions:",
            *(f"  - {h}" for h in hints),
        ]
        return "\n".join(lines)
```

The harness calls `build_context` after each tool failure and appends the returned block to the next LLM prompt, immediately after the error result.

## Key Takeaways

- Build the structured context block from the error, prior attempts, and recovery hints, and inject it into the next inference call immediately after the tool failure
- Key the per-session failure log to operation and target, not just error type, so previous-attempt entries surface only for the exact call that is failing again
- The 25–40% reduction comes from removing the first two to three redundant retries that repeat a failed approach, not from later-stage gains
- Loop detection stays required even after adding error recovery — recovery only lightens its load, since enriched context does not catch every case
- Recovery suggestions are static mappings, not LLM-generated — the harness does the enrichment deterministically

## Related

- [Loop Detection](../observability/loop-detection.md)
- [Circuit Breakers](../observability/circuit-breakers.md)
- [Tool Engineering](../tool-engineering/tool-engineering.md)
- [Machine-Readable Error Responses (RFC 9457)](../tool-engineering/rfc9457-machine-readable-errors.md) — Structured upstream errors that make context injection more precise
- [Error Preservation in Context](error-preservation-in-context.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Agent Harness: Initializer and Coding Agent](../patterns/agent-design/agent-harness.md)
- [Exception Handling and Recovery Patterns](../patterns/agent-design/exception-handling-recovery-patterns.md) — Broader taxonomy of agent failure modes and recovery strategies
