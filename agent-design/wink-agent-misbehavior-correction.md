---
title: "Wink: Coding Agent Misbehavior Classification and Correction"
description: "An async trajectory-observer system that classifies coding agent misbehaviors into three categories and injects targeted course-corrections without restarting."
aliases:
  - trajectory observer
  - misbehavior correction
tags:
  - agent-design
  - workflows
---

# Wink: Classifying and Auto-Correcting Coding Agent Misbehaviors

> An async trajectory-observer system that classifies misbehaviors into three categories and injects targeted course-corrections.

## Misbehavior Rate in Production Trajectories

Production coding agent trajectories contain misbehaviors at a rate that makes manual intervention unscalable. Analysis of 10,000+ real trajectories from [arXiv:2602.17037](https://arxiv.org/abs/2602.17037) shows approximately 30% of all agent trajectories contain at least one misbehavior. These are not edge cases — they are normal production behavior requiring a systematic response.

## Three Misbehavior Categories

Wink classifies misbehaviors into three mutually exclusive categories:

**Specification Drift** — the agent departs from its task instructions. The agent continues executing, but its trajectory diverges from the stated goal. Common causes: ambiguous instructions, long-horizon context dilution, or the agent reprioritizing based on intermediate findings.

**Reasoning Problems** — the agent's internal logic fails. Examples: circular reasoning loops, incorrect inferences from tool outputs, and incorrect assumptions about the codebase state. The agent is not ignoring instructions; it is applying them incorrectly.

**Tool Call Failures** — incorrect tool invocations: wrong arguments, non-existent file paths, malformed API calls, or tool sequences that violate execution preconditions.

Each category has distinct correction strategies. Injecting the same generic nudge for all three categories degrades performance; the classifier enables category-specific corrections.

## Async Intervention Architecture

```mermaid
graph TD
    A[Agent trajectory] --> B[Observer]
    B --> C{Misbehavior detected?}
    C -->|No| A
    C -->|Yes| D[Classifier]
    D --> E{Category}
    E -->|Specification Drift| F[Re-anchor to task]
    E -->|Reasoning Problem| G[Inject correction context]
    E -->|Tool Call Failure| H[Inject tool guidance]
    F --> A
    G --> A
    H --> A
```

The observer runs asynchronously — it watches the trajectory without blocking the agent's execution. When it detects a misbehavior signal, it classifies the event and injects a targeted course-correction into the agent's next inference call. The agent continues without a full restart.

This is distinct from synchronous guardrails that block execution. Async intervention preserves trajectory continuity and accumulated context while redirecting the agent.

## Results

From the Wink A/B test on production traffic ([arXiv:2602.17037](https://arxiv.org/abs/2602.17037)):

- **90% resolution rate** for misbehaviors that require a single intervention
- Reduction in tokens per session [unverified] — the agent reaches correct behavior faster without wasted execution
- Reduction in engineer interventions per session [unverified] — most misbehaviors resolve without human involvement

The 10% that require multiple interventions or escalate to human review are typically novel failure modes not covered by the existing classifier's training distribution.

## Implementation Signals

Three observable signals trigger the observer:

1. **Repetition patterns** — the agent calls the same tool with identical or near-identical arguments across multiple turns without progress
2. **Contradiction signals** — the agent's stated reasoning contradicts a tool output it received in the same session
3. **Precondition violations** — a tool call references a resource (file path, API endpoint, variable) that does not exist or has not yet been created

These signals are observable without access to the model's internal state — they are detectable from the tool call log and conversation history.

## Deployment Implication

The 30% misbehavior rate means every production agent deployment needs a trajectory observer. Without one, a third of runs silently degrade.

The minimum viable observer:

- Records each tool call and its arguments
- Detects repetition patterns (same tool + args appearing 3+ times without a successful result) [unverified]
- Detects precondition violations (file read before file creation in the same session)
- Injects a single corrective message when triggered; escalates to human after two failed interventions [unverified]

## Example

**Trigger**: Repetition pattern — the agent calls `read_file` on `src/utils.py` three consecutive turns with no write, move, or delete in between. The observer detects the repeated call with identical arguments and no intervening progress signal.

**Classification**: Tool Call Failure — the agent is stuck in a retrieval loop, not drifting from its goal or reasoning incorrectly.

**Injected correction message** (inserted into the next inference call as a system turn):

> You have read `src/utils.py` three times without acting on its contents. If the file does not contain what you need, state what is missing and proceed to a different approach. Do not read the same file again until you have taken an intermediate action.

**Outcome**: On the next turn, the agent identifies that the function it is looking for is in `src/helpers.py` (which it has not yet read) and proceeds there. No human intervention required.

This illustrates the category-specific correction value: a generic "you seem stuck" nudge would not prompt the agent to look elsewhere; the tool-call-specific correction directs it to change its retrieval strategy.

## Key Takeaways

- 30% of production coding agent trajectories contain misbehaviors — trajectory observation is not optional
- Three categories (Specification Drift, Reasoning Problems, Tool Call Failures) require distinct correction strategies
- Async intervention preserves trajectory continuity; synchronous blocking does not
- 90% of single-intervention misbehaviors resolve without engineer involvement
- Observable signals (repetition, contradiction, precondition violations) detect misbehaviors without model-internal access

## Unverified Claims

- Reduction in tokens per session [unverified]
- Reduction in engineer interventions per session [unverified]
- Repetition detection triggers at same tool + args appearing 3+ times without a successful result [unverified]
- Escalates to human after two failed interventions [unverified]

## Related

- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Loop Detection](../observability/loop-detection.md)
- [Context-Injected Error Recovery](../context-engineering/context-injected-error-recovery.md)
- [Agent Backpressure](agent-backpressure.md)
- [Steering Running Agents](steering-running-agents.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Harness Engineering](harness-engineering.md)
- [Classical SE Patterns as Agent Design Analogues](classical-se-patterns-agent-analogues.md)
- [The Ralph Wiggum Loop](ralph-wiggum-loop.md)
- [Convergence Detection](convergence-detection.md)
- [Agent Self-Review Loop](agent-self-review-loop.md)
- [Rollback-First Design](rollback-first-design.md)
- [Agent Turn Model](agent-turn-model.md)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md)
