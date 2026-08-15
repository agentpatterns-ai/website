---
title: "Loop Engineering: Designing Agent Loops That Converge"
description: "The cross-cutting discipline of designing, controlling, and terminating the iterative loops agents run in — so they converge on the goal instead of spinning, stalling, or burning budget."
tags:
  - loop-engineering
  - index
last_reviewed: 2026-06-29
---

# Loop Engineering

> Loop engineering designs, controls, and terminates the iterative loops agents run in, so they converge on the goal instead of spinning or burning budget.

The loop is the defining structure of agentic coding — tool loops, plan/act loops, verification loops, improvement flywheels, long-running autonomous loops. But coverage of *how to engineer loops well* is scattered. Loop engineering is the name for that cluster: the deliberate design of loops that terminate correctly and earn their cost.

It cuts across the site. The canonical treatment of each loop pattern still lives in its home discipline — [agent design](../patterns/agent-design/index.md), [workflows](../workflows/index.md), [verification](../verification/index.md), [observability](../observability/index.md). This section owns the pages whose primary subject *is* the loop, and crosswalks the rest under one frame, built on the three-loops spine, so you can navigate "how do I design a loop that terminates correctly and earns its cost?" as a single topic.

## What loop engineering is — and isn't

- It is the design discipline over the iterative structure: which loop type fits the work, how each turn is bounded, and when the loop stops.
- It is not all of [agent design](../patterns/agent-design/index.md). Agent design covers composition, memory, delegation, and harness; loop engineering is the lens on the *iteration* specifically.
- It is not [workflows](../workflows/index.md). A workflow is a composed pipeline of agents and gates; loop engineering is about the loop *inside* a single agent's run (though improvement workflows are loops too — they crosswalk here).
- Termination and cost are the crux. Convergence detection, go/no-go gates, and runaway guardrails are what separate an engineered loop from a runaway — they are foregrounded below.

## The crosswalk

The spine is the three-loops diagnostic — name the loop, then the symptom tells you the intervention.

- [The Three Loops of Agentic Coding: A Diagnostic Vocabulary](three-loops-agentic-coding.md) — tool, verification, and convergence loops; the vocabulary the rest of this section hangs on
- [Loop Engineering: Stacking Outer Loops Around the Agent](loop-engineering.md) — the loopcraft / four-loop-stack framing: stacking verification, event-driven, and hill-climbing loops around the agent so the human stops being the throughput ceiling

### Loop strategy and autonomy

How much context each iteration carries, and how much the loop runs on its own.

- [Loop Strategy Spectrum: Accumulated vs Fresh Context](loop-strategy-spectrum.md) — accumulated, compressed, or fresh context per iteration, chosen by workload
- [The Ralph Wiggum Loop: Fresh-Context Iteration Pattern](ralph-wiggum-loop.md) — each iteration runs in a fresh window, state persisted to disk
- [Blind Resampling Over Self-Repair in Small Code Models](blind-resampling-over-self-repair.md) — below 7B, discard the failed program and resample rather than feed it back for repair
- [Goal-Driven Autonomous Loop with Budget Cap](goal-driven-autonomous-loop.md) — an objective-bound loop that stops on goal-done or budget exhaustion
- [Long-Running Agents](../patterns/agent-design/long-running-agents.md) — making progress across many sessions by moving state into durable artifacts
- [Agentless vs Autonomous](../patterns/agent-design/agentless-vs-autonomous.md) — when a fixed pipeline beats a model-controlled loop
- [Continuous Autonomous Task Loop](../workflows/continuous-autonomous-task-loop.md) — a self-directed loop that reads a backlog and executes each item

### Loop structure and orchestration

The shape of a single iteration and what guarantees run inside it.

- [Agent Loop Middleware — Safety Nets and Message Injection](agent-loop-middleware.md) — wrap the loop from outside so critical steps always run
- [CoALA Decision-Making Loop](../patterns/agent-design/coala-decision-making-loop.md) — propose/evaluate/select/act as a vocabulary for where tactics intervene
- [ReAct Pattern](../patterns/agent-design/react-pattern.md) — interleave thought, tool call, and observation each step
- [Plan-First Loop](../workflows/plan-first-loop.md) — design a written plan before code, then loop on it

### Termination, convergence, and cost gates

The crux — what stops a loop and what justifies running one at all.

- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — mechanical stopping criteria from change velocity, output size, and similarity
- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md) — the four-condition gate before you build a loop at all
- [Loop Trigger Selection: Pairing the Start with the Stop](loop-trigger-selection.md) — goal-bounded, scheduled, and event-driven triggers, and the terminal state each one commits you to
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](loop-budgeting.md) — pick the budget primitive (iteration / token / wall-clock) and choose front-loaded vs even-split per-turn allocation
- [Within-Task Model Cascade: Designing the Escalation Gate](within-task-model-cascade.md) — retry the same step on a cheap model first and escalate on gate failure; the gate's false-accept rate sets both the saving and the quality floor
- [Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)](early-termination-and-warm-restart.md) — predict failure from the trajectory prefix against a false-positive budget, then restart with the killed attempt's diff as an optional git overlay

### Runaway guardrails

Detecting and breaking loops that spin without converging.

- [Loop Detection](../observability/loop-detection.md) — catch repetition and stuck states before they burn budget
- [Stuck-Loop Recovery: Detecting and Escaping Non-Converging Agent Loops](stuck-loop-recovery.md) — the recovery playbook once detection fires: nudge, replan, escalate, reset, hand off, abort
- [Observability Feedback Loop](../observability/observability-feedback-loop.md) — close the loop from telemetry back into agent behavior

### Improvement and flywheel loops

Loops that make future agent work better, not just finish the current task.

- [Agentic Flywheel](../patterns/agent-design/agentic-flywheel.md) — agents analyze their own operational data and generate harness improvements
- [Self-Reporting Loops](../patterns/agent-design/self-reporting-loops.md) — out-of-scope observations filed so signal survives the session
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — a standing loop that upgrades the agent setup over time
- [Closed-Loop Agent Training](../workflows/closed-loop-agent-training.md) — feed run outcomes back into training
- [Skill Library Refinement Loops](../workflows/skill-library-refinement-loops.md) — iteratively refine a skill library from usage
- [Humans and Agents Development Loops](../workflows/humans-agents-development-loops.md) — interleave human and agent turns as one loop

### Review loops

Iterative review as a loop structure.

- [Agent Self-Review Loop](../code-review/agent-self-review-loop.md) — the agent critiques and revises its own output
- [Review-Then-Implement Loop](../code-review/review-then-implement-loop.md) — review before implementing, then iterate
- [Human-in-the-Loop](../workflows/human-in-the-loop.md) — workflow-boundary HITL: where to place approval gates around an agent pipeline
- [Human-in-the-Loop Checkpoints as Loop Control](human-in-the-loop-checkpoints.md) — the loop-internal counterpart: HITL as a four-verb suspend that bounds or redirects the iteration
- [Failure-Driven Iteration](../workflows/failure-driven-iteration.md) — let failures drive the next iteration

## Related

- [Concept Map](../concepts.md) — all site content grouped by theme
- [Agent Design](../patterns/agent-design/index.md) — the canonical home for loop patterns
- [Workflows](../workflows/index.md) — composed pipelines that wrap these loops
- [Verification](../verification/index.md) — the verification loop's home discipline
