---
title: "Agent Pushback Protocol for Managing Disagreements"
term: "Agent Pushback Protocol"
description: "Agents evaluate requests at both implementation and requirements level, surface concerns, and wait for explicit confirmation before executing."
tags:
  - agent-design
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: adopted
---

# Agent Pushback Protocol

> A pushback protocol makes agents evaluate requests, surface concerns, and wait for explicit confirmation before executing — the cure for the [yes-man agent](../anti-patterns/yes-man-agent.md).

## Two categories of pushback

Most agent instructions focus on the happy path: receive task, execute task, return result — the same pressure behind [happy path bias](../anti-patterns/happy-path-bias.md). A pushback protocol adds evaluation before execution, in two categories.

Implementation concerns cover code quality. The request introduces tech debt, duplication, or unnecessary complexity. A simpler approach exists. The scope is too large or vague for one pass (a trigger for [interactive clarification](interactive-clarification-underspecified-tasks.md)).

Requirements concerns cover product correctness. The feature conflicts with existing behavior. The request solves symptom X but the real problem is Y. Edge cases produce dangerous behavior — the class [human-in-the-loop confirmation gates](../security/human-in-the-loop-confirmation-gates.md) guard. Burke Holland's [Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md) calls these "the expensive kind", consistent with [Boehm and Basili's (2001)](https://dl.acm.org/doi/10.1109/2.962984) finding that requirements defects cost roughly 100× more to fix after delivery than during design.

## Structured format

The Anvil agent structures pushback as a callout with interactive confirmation ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)):

1. Callout: a visible warning block that names the concern.
2. Explanation: what the problem is and why it matters.
3. Choices: "Proceed as requested" / "Do it the agent's way" / "Let me rethink this".

The agent does not implement until you respond. This gate is the point. Evaluation without it is advisory, and advisory feedback gets ignored — the [yes-man agent](../anti-patterns/yes-man-agent.md) failure mode.

### Implementation example

> "You asked for a new `DateFormatter` helper, but `Utilities/Formatting.swift` already has `formatRelativeDate()` which does exactly this. Adding a second one creates divergence. Recommend extending the existing function with a `style` parameter."

The agent searched the codebase and surfaced existing code before writing new.

### Requirements example

> "This adds a 'delete all conversations' button with no confirmation dialog and no undo — the Firestore delete is permanent. Users who fat-finger this lose everything. Recommend adding a confirmation step, or a soft-delete with 30-day recovery."

The agent weighed user impact, not just code correctness.

## Instruction design that elicits pushback

Framing matters. An agent told "you are a helpful assistant" optimizes for compliance. One told "you are a senior engineer with opinions" optimizes for correctness — [persona framing](persona-as-code.md) shapes how it evaluates. The Anvil agent uses: "You are a senior engineer, not an order taker. You have opinions and you voice them — about the code AND the requirements" ([Anvil agent](https://github.com/burkeholland/anvil/blob/main/agents/anvil.agent.md)).

Concrete trigger conditions beat vague instructions to "push back when appropriate":

- The request will introduce duplication or unnecessary complexity
- A simpler approach exists that you have not considered
- The scope is too large or vague for one pass
- Edge cases would produce dangerous behavior for end users
- The change assumes something about system usage that may be wrong

## Distinct from human-in-the-loop gates

[Human-in-the-loop confirmation gates](../security/human-in-the-loop-confirmation-gates.md) fire on action type: "confirm before deleting files," "approve before pushing to main." They gate on what the agent does.

Pushback protocols gate on request quality: "this request is a bad idea, here's why." The trigger is the agent's evaluation, not the tool category. The two complement each other — gates prevent dangerous actions, pushback prevents misguided ones.

## When this backfires

The pattern degrades in three conditions.

The first is high-frequency, low-stakes edits. When a developer iterates quickly — renaming a variable, reordering fields — a gate on every request interrupts more than it saves. SOC alert-fatigue research shows the same dynamic: at high volume, analysts disable, ignore, or offload alerts rather than triage each one ([Tariq et al., 2025](https://dl.acm.org/doi/10.1145/3723158)). Reserve pushback for genuinely risky or ambiguous requests.

The second is poorly calibrated trigger conditions. Vague triggers ("push back when something seems off") make agents flag routine requests, training developers to dismiss concerns reflexively. When the real risk arrives, the gate gets bypassed on habit — the same alert-fatigue dynamic ([Tariq et al., 2025](https://dl.acm.org/doi/10.1145/3723158)). Concrete, enumerated conditions (as in the Anvil agent) solve this, but need upfront calibration per project.

The third is over-reliance on agent judgment for domain correctness. The pattern assumes the agent can detect requirements-level mistakes — the roughly 100×-cost defects from Boehm and Basili above. For novel domains, proprietary systems, or thin docs, the agent cannot tell "this edge case is dangerous" from "I'm uncertain." A gate on shallow context produces false confidence: the check ran, so the request looks validated. Pairing it with explicit context injection (architecture docs and domain constraints) reduces this risk.

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
