---
title: "Agent Pushback Protocol for Managing Disagreements"
description: "Agents evaluate requests at both implementation and requirements level, surface concerns, and wait for explicit confirmation before executing."
tags:
  - agent-design
  - instructions
---

# Agent Pushback Protocol

> Agents evaluate requests at both implementation and requirements level before executing, surfacing concerns and waiting for explicit confirmation — the solution pattern for the [yes-man agent](../anti-patterns/yes-man-agent.md).

## Two Categories of Pushback

Most agent instructions focus on the happy path: receive task, execute task, return result — this is the same optimization pressure behind [happy path bias](../anti-patterns/happy-path-bias.md) in generated code. A pushback protocol adds evaluation before execution, split into two distinct categories.

**Implementation concerns** (code quality): the request introduces tech debt, duplication, or unnecessary complexity. A simpler approach exists. The scope is too large or vague for one pass.

**Requirements concerns** (product correctness): the feature conflicts with existing behavior. The request solves symptom X but the real problem is Y. Edge cases produce surprising or dangerous behavior. Burke Holland's [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) calls these "the expensive kind" — requirements-level mistakes caught after shipping cost orders of magnitude more than implementation-level mistakes caught during development.

## Structured Format

The Anvil agent implements pushback as a structured callout with interactive confirmation ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)):

1. **Callout** — a visible warning block identifying the concern
2. **Explanation** — what the problem is and why it matters
3. **Choices** — "Proceed as requested" / "Do it the agent's way" / "Let me rethink this"

The agent does NOT implement until you respond. This is the critical constraint: evaluation without a gate is advisory, and advisory feedback gets ignored.

### Implementation Example

> "You asked for a new `DateFormatter` helper, but `Utilities/Formatting.swift` already has `formatRelativeDate()` which does exactly this. Adding a second one creates divergence. Recommend extending the existing function with a `style` parameter."

The agent searched the codebase, found existing code, and surfaced it before writing new code.

### Requirements Example

> "This adds a 'delete all conversations' button with no confirmation dialog and no undo — the Firestore delete is permanent. Users who fat-finger this lose everything. Recommend adding a confirmation step, or a soft-delete with 30-day recovery."

The agent evaluated the request against user impact, not just code correctness.

## Instruction Design That Elicits Pushback

Framing matters. An agent instructed "you are a helpful assistant" optimizes for compliance. An agent instructed "you are a senior engineer with opinions" optimizes for correctness. The Anvil agent uses: "You are a senior engineer, not an order taker. You have opinions and you voice them — about the code AND the requirements" ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)).

Concrete trigger conditions work better than vague instructions to "push back when appropriate":

- The request will introduce duplication or unnecessary complexity
- There is a simpler approach you have not considered
- The scope is too large or vague to execute well in one pass
- Edge cases would produce dangerous behavior for end users
- The change makes an implicit assumption about system usage that may be wrong

## Distinct from Human-in-the-Loop Gates

[Human-in-the-loop confirmation gates](../security/human-in-the-loop-confirmation-gates.md) fire on action type: "confirm before deleting files," "approve before pushing to main." They gate on *what* the agent does.

Pushback protocols gate on *request quality*: "this request is a bad idea, here's why." The trigger is the agent's evaluation of the task, not the category of tool being invoked. Both patterns complement each other — gates prevent dangerous actions while pushback prevents misguided ones.

## When This Backfires

The pattern degrades in three conditions:

**High-frequency, low-stakes edits.** When a developer iterates quickly on minor changes — renaming a variable, reordering output fields — a gate on every request adds more interruption than it saves. SOC alert-fatigue research documents the same dynamic: at high volume, analysts disable, ignore, or offload alerts rather than triage each one ([Tariq et al., 2025](https://dl.acm.org/doi/10.1145/3723158)). Reserve pushback for genuinely risky or ambiguous requests.

**Poorly calibrated trigger conditions.** Vague triggers ("push back when something seems off") cause agents to flag too many routine requests, which trains developers to dismiss concerns reflexively. When the real risky request arrives, the gate gets bypassed on habit. Concrete, enumerated conditions (as in the Anvil agent) solve this, but require upfront calibration per project context.

**Over-reliance on agent judgment for domain correctness.** The pattern assumes the agent can reliably detect requirements-level mistakes. For novel domains, proprietary systems, or under-documented codebases, the agent lacks sufficient context to distinguish "this edge case is dangerous" from "I'm uncertain." A pushback gate backed by shallow context can produce false confidence — the check ran, so the request must have been validated. Pairing the protocol with explicit context-injection (system prompt with architecture docs, domain constraints) reduces this risk.

## Key Takeaways

- Split pushback into implementation concerns (code quality) and requirements concerns (product correctness)
- Use a structured format: callout, explanation, choices — with a hard gate that blocks execution until you respond
- Frame agents as senior engineers with opinions, not order-takers — instruction framing shapes evaluation depth
- Define concrete trigger conditions rather than vague "push back when appropriate" instructions
- Pushback gates on request quality; human-in-the-loop gates on action type — use both
- Reserve pushback for genuinely ambiguous or risky requests — overuse creates automation fatigue and causes developers to dismiss valid concerns

## Related

- [The Yes-Man Agent](../anti-patterns/yes-man-agent.md)
- [Human-in-the-Loop](../workflows/human-in-the-loop.md)
- [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md)
- [Agent Backpressure](agent-backpressure.md)
- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md)
- [Steering Running Agents](steering-running-agents.md)
- [Grill Me Technique](grill-me-technique.md)
