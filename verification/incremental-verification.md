---
title: "Incremental Verification: Check at Each Step, Not at the End"
description: "Verify agent output at each logical step to catch errors close to their source before they propagate — cheap checkpoints prevent expensive cascading failures."
tags:
  - testing-verification
---

# Incremental Verification: Check at Each Step, Not at the End

> Verify agent output at each logical step to catch errors close to their source, before they propagate.

## The Pattern

An agent that generates 500 lines of code before any verification may have made a wrong assumption at line 10. Everything after that point is built on a mistake. Unwinding the cascade is expensive — each dependent decision must be re-evaluated.

Incremental verification inserts checkpoints between stages. After each meaningful unit of work, you verify before proceeding. The cost of a checkpoint is low; the cost of debugging downstream consequences is high.

## Why This Works

Error cost grows with distance from the error. A type mismatch caught at the point of introduction is a one-line fix. The same mismatch discovered after 10 functions have been written against the wrong type requires auditing every callsite.

This is the same principle as fail-fast in software design: surface problems immediately, in the location where they occurred, with full context still available.

## Checkpoint Patterns

### Code: Build → Test → Iterate

Implement one function, run the test suite, fix failures, move to the next function. Do not write multiple functions before running tests — the second function may build on a broken assumption in the first.

Type checking is continuous verification: compile after each change, not after a batch. Type errors at the function boundary are simpler to fix than type errors across a module.

### Documents: Claim-by-Claim Verification

Check each source as it is cited, not after the whole document is written. A hallucinated citation in paragraph 2 invalidates every argument that builds on it. Verifying at the end means re-reading against sources retroactively, which is harder than checking forward.

### Agent Workflows: Stage Gates

Agent pipelines should include explicit verification steps between stages, not just at the end of the pipeline. A research → draft → review pipeline with no verification between research and draft means the draft may be built on unverified claims.

```mermaid
graph TD
    A[Research] --> B{Verify Sources}
    B -->|Pass| C[Draft]
    B -->|Fail| A
    C --> D{Check Claims}
    D -->|Pass| E[Review]
    D -->|Fail| C
    E --> F[Publish]
```

### Checkpoint-Save Pattern

Before making a batch of changes: save a known-good state (commit, checkpoint, snapshot). Make changes. Verify. If verification fails, restore to the known-good state and retry. This contains the [blast radius](../security/blast-radius-containment.md) of errors to one checkpoint interval.

## Anti-Patterns

- **Write everything, then review** — errors compound through the entire artifact before detection
- **Batch verification** — running tests only at the end of a session, not between logical units
- **No automated checkpoints** — relying on human review as the only verification layer

## Key Takeaways

- Error cost grows with distance from the error source — catch failures close to where they occur
- Automated checkpoints (type checks, tests, linters) are cheap; manual review of cascaded errors is expensive
- Structure agent pipelines with verification gates between stages, not only at the end
- Save known-good state before each batch of changes to bound recovery cost
- The anti-pattern is "write the whole thing then we'll review it"

## Related

- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Test-Driven Agent Development: Tests as Spec and Guardrail](tdd-agent-development.md)
- [Pre-Completion Checklists for AI Agent Development](pre-completion-checklists.md)
- [Layered Accuracy Defense for Reliable Agent Outputs](layered-accuracy-defense.md)
- [Red-Green-Refactor with Agents: Letting Tests Drive Dev](red-green-refactor-agents.md)
- [Defense Patterns](index.md)
