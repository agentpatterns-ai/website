---
title: "Task List Divergence as Instruction Quality Diagnostic"
description: "Use the gap between an agent's generated task list and your intended steps as a systematic signal for instruction weaknesses in your prompts."
tags:
  - instructions
---

# Task List Divergence as Instruction Quality Diagnostic

> Use the gap between an agent's generated task list and your intended steps as a systematic signal for instruction weaknesses.

## The Diagnostic Principle

When you give an agent a task, it decomposes the work into steps. That decomposition is a mirror of how the agent interpreted your instructions. If the generated task list matches your intended sequence, the instructions communicated clearly. If it diverges, the divergence pattern tells you *what* was unclear and *how* to fix it.

This reframes task lists from an execution artifact into a diagnostic tool. Instead of only checking whether the agent completed the work correctly, you check whether the agent *understood* the work correctly — before execution begins.

## Five Divergence Patterns

Each pattern signals a different instruction problem:

| Divergence | What You See | What It Signals |
|---|---|---|
| **Sequencing** | Agent orders steps B then A when you intended A then B | Dependencies between steps are not explicit in your instructions |
| **Omissions** | Agent skips a step you consider essential (e.g., testing) | The step relies on implicit knowledge you did not state |
| **Additions** | Agent includes steps you did not request (e.g., backup, validation) | Scope boundaries are ambiguous — the agent inferred extra work |
| **Granularity mismatch** | "Update documentation" becomes twelve sub-tasks, or three complex steps collapse into one | Your instructions operate at a different abstraction level than the agent expects |
| **Misinterpretation** | A step describes a different action than you intended | Ambiguous language — the instruction has multiple valid readings |

Sequencing and omission errors indicate structural gaps. Additions and granularity mismatches indicate scope ambiguity. Misinterpretations indicate semantic ambiguity in the instruction text itself.

## Using Divergence to Improve Instructions

The diagnostic loop:

1. **Provide instructions** for a task.
2. **Request a task list** before execution — in Claude Code, use plan mode or ask the agent to generate a task breakdown before implementing.
3. **Compare** the generated list against your intended steps.
4. **Classify** each divergence by pattern.
5. **Revise** instructions to address the specific weakness each pattern reveals.
6. **Re-test** with the same or similar task to verify the fix.

Each pattern has a targeted fix: add explicit dependency markers for sequencing errors; surface implicit knowledge for omissions; tighten scope statements for additions; recalibrate abstraction level for granularity mismatches; replace ambiguous terms with precise ones for misinterpretations.

## Extreme Granularity as a Transparency Strategy

Requesting highly detailed task descriptions — specifying exact file paths, function names, parameter changes — forces the agent to expose its design decisions before execution. A task like "style the navbar" becomes a list of specific CSS property changes with values. You can approve, reject, or redirect individual decisions without waiting for implementation.

This trades compactness for visibility. Use it when the cost of wrong execution is high or when you are calibrating instructions for a new domain [unverified].

## Real-Time Steering

Task lists are not static. When you correct the agent mid-task, the updated task list reflects whether the correction was understood. If you change a requirement ("use green, not blue") and the remaining tasks update accordingly, the correction landed. If tasks remain unchanged, the agent did not integrate the correction — a signal to restate it differently [unverified].

## Tool-Agnostic Application

The diagnostic technique works with any agent that produces task breakdowns — Claude Code's plan mode, GitHub Copilot's plan view, or custom agents using any task management tool. Wherever an agent externalizes its understanding as a step list, that list is available for divergence analysis.

## Example

The following prompt pair shows how to apply the diagnostic loop. First, request a task breakdown before execution begins:

```
You are refactoring the user authentication module. Before writing any code, generate a numbered task list of every step you plan to take.
```

Suppose the agent returns this plan:

```
1. Rename `auth_token` to `access_token` in auth.py
2. Update token validation logic
3. Update API response serialiser
4. Run linter
```

You intended the sequence to be: update the database schema first, then update application code, then run the full test suite. Comparing the lists reveals two divergence patterns:

- **Sequencing** — the database migration step is missing entirely, and the agent would write application code against the old schema
- **Omission** — "run linter" replaces "run the test suite"; testing was implicit knowledge not stated in the instructions

Targeted fixes for each pattern:

```
Before making any code changes, run the database migration in db/migrations/.
After all code changes, run `pytest tests/auth/` and confirm all tests pass before finishing.
```

Re-running the prompt after adding these two sentences produces a plan that matches the intended sequence — catching both errors before any code was written.

## Unverified Claims

- Extreme granularity as a transparency strategy is useful when calibrating instructions for a new domain [unverified]
- Task lists function as a continuous feedback channel, not a one-time plan artifact [unverified]

## Related

- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [Instruction Polarity: Positive Rules Over Negative](../instructions/instruction-polarity.md)
- [Steering Running Agents](../agent-design/steering-running-agents.md)
- [The Implicit Knowledge Problem](../anti-patterns/implicit-knowledge-problem.md) — omissions in task plans often trace to implicit knowledge the agent was never given
