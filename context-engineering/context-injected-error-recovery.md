---
title: "Context-Injected Error Recovery for AI Agent Development"
description: "When a tool call fails, inject structured error context — the error message, previous attempts, and targeted recovery suggestions — into the next inference call to prevent retry loops."
aliases:
  - error context injection
  - structured error recovery
tags:
  - agent-design
  - workflows
  - source:opendev-paper
---

# Context-Injected Error Recovery

> When a tool call fails, inject structured error context — the error message, previous attempts, and targeted recovery suggestions — into the next inference call to prevent retry loops before they form.

## The Problem: Blind Retries

When a tool call returns an error, most agent harnesses pass only the raw error message back to the model ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). The model retries with minimal additional information, often repeating the same approach. After several identical failures, the agent enters a retry loop — consuming context window and tokens without progress.

The root cause is information asymmetry: the model lacks the context needed to choose a different strategy on the first retry ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)).

## How Context Injection Works

Instead of forwarding the raw error, the harness constructs a structured error context block containing three components ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)):

1. **Error message** — the original error output, preserved verbatim
2. **Previous attempts** — a record of prior attempts at the same operation within the current session, including what was tried and what failed
3. **Targeted recovery suggestions** — harness-generated hints based on the error type (e.g., "file not found" suggests checking the path; "permission denied" suggests checking credentials or sandbox restrictions)

This block is injected into the next LLM prompt, giving the model a complete picture of the failure situation rather than a single data point.

## Structured Context Format

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

The key property is structure: the model receives not just what went wrong, but what has already been tried and what the viable alternatives are ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)).

## Impact

Context-injected error recovery reduces retry loops by 25–40% compared to passing raw error messages alone ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). The improvement comes from eliminating the first two to three redundant retries that would otherwise occur before the model independently discovers that a different approach is needed.

## Relationship to Loop Detection

Loop detection and error recovery are complementary but operate at different points in the failure lifecycle:

- **Error recovery** acts at the moment of failure — it prevents loops from forming by giving the model better information on the first retry ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344))
- **Loop detection** acts after repeated failures — it detects and interrupts loops that have already formed

Error recovery reduces the workload on loop detection: the 25–40% reduction in retry loops means fewer cases reach the threshold that triggers detection ([Bui, 2026 §2.3.5](https://arxiv.org/abs/2603.05344)). Loop detection remains necessary as a safety net for cases where enriched context is insufficient.

## Implementation Considerations

The harness maintains a per-session log of failed tool calls keyed by operation type and target. On each failure:

1. Look up prior failures for the same operation/target pair
2. Select recovery suggestions from a mapping of error patterns to hints
3. Assemble the structured context block
4. Inject the block into the next prompt, positioned immediately after the error result

Recovery suggestions should be generic enough to avoid prescribing a single fix, but specific enough to exclude approaches already attempted. The suggestion catalog is maintained as a static mapping — no LLM inference is needed to generate suggestions.

This aligns with emerging ReAct-agent reliability guidance: the LangGraph [Production Reliability RFC](https://github.com/langchain-ai/langgraph/issues/6617) proposes classifying errors and surfacing structured reasoning so retries are informed rather than blind.

## When This Backfires

Context injection adds tokens to every retry prompt. Three conditions make this trade-off unfavorable:

1. **Near-context-limit sessions** — injecting prior-attempt history and recovery hints into a prompt that is already large can push the total context past the model's limit, truncating earlier session history and introducing new errors.
2. **High-frequency, low-variance errors** — when errors repeat across many different operations (e.g., a systemic auth failure or a network outage), the recovery suggestion catalog produces the same generic hints on every retry, adding tokens without adding signal.
3. **Static suggestion catalog staleness** — if the hint mappings are not maintained as the tool surface evolves, they can suggest approaches that no longer apply or contradict current tool behavior, actively misleading the model.

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

- Inject structured error context — not just the raw error — into the next inference call after a tool failure
- Include the error message, previous attempts, and targeted recovery suggestions in a single block
- This prevents retry loops at the source, reducing them by 25–40%
- Error recovery complements loop detection: recovery prevents loops, detection catches the ones that still form
- Recovery suggestions are static mappings, not LLM-generated — the harness does the enrichment deterministically

## Related

- [Loop Detection](../observability/loop-detection.md)
- [Circuit Breakers](../observability/circuit-breakers.md)
- [Tool Engineering](../tool-engineering/tool-engineering.md)
- [Machine-Readable Error Responses (RFC 9457)](../tool-engineering/rfc9457-machine-readable-errors.md) — Structured upstream errors that make context injection more precise
- [Error Preservation in Context](error-preservation-in-context.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Agent Harness: Initializer and Coding Agent](../agent-design/agent-harness.md)
- [Exception Handling and Recovery Patterns](../agent-design/exception-handling-recovery-patterns.md) — Broader taxonomy of agent failure modes and recovery strategies
