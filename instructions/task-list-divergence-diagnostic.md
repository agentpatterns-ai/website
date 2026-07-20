---
title: "Task List Divergence as Instruction Quality Diagnostic"
description: "Use the gap between an agent's generated task list and your intended steps as a systematic signal for instruction weaknesses in your prompts."
term: "Task List Divergence"
tags:
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# Task List Divergence as Instruction Quality Diagnostic

> Use the gap between an agent's generated task list and your intended steps as a systematic signal for instruction weaknesses.

## The diagnostic principle

When an agent breaks a task into steps, that breakdown mirrors how it read your instructions. If the generated task list matches your intended sequence, the instructions communicated clearly. If it diverges, the divergence pattern tells you what was unclear and how to fix it.

This reframes the task list from an execution artifact to a diagnostic tool. It extends the [plan-first loop](../workflows/plan-first-loop.md): check whether the agent understood the work before execution begins, not only whether it finished correctly after.

## Five divergence patterns

Each pattern signals a different instruction problem:

| Divergence | What You See | What It Signals |
|---|---|---|
| Sequencing | Agent orders steps B then A when you intended A then B | Dependencies between steps are not explicit in your instructions |
| Omissions | Agent skips a step you consider essential (e.g., testing) | The step relies on implicit knowledge you did not state |
| Additions | Agent includes steps you did not request (e.g., backup, validation) | Scope boundaries are ambiguous — the agent inferred extra work |
| Granularity mismatch | "Update documentation" becomes 12 sub-tasks, or 3 complex steps collapse into one | Your instructions operate at a different abstraction level than the agent expects |
| Misinterpretation | A step describes a different action than you intended | Ambiguous language — the instruction has multiple valid readings |

Sequencing and omission errors indicate structural gaps. Additions and granularity mismatches indicate scope ambiguity. Misinterpretations indicate semantic ambiguity in the text itself.

## Using divergence to improve instructions

Run the diagnostic loop:

1. Provide instructions for a task.
2. Request a task list before execution. Use plan mode or ask the agent to generate a task breakdown before implementing. Anthropic recommends this "explore, then plan, then code" separation to avoid solving the wrong problem ([Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)).
3. Compare the generated list against your intended steps.
4. Classify each divergence by pattern.
5. Revise the instructions to address the weakness each pattern reveals.
6. Re-test with the same or a similar task to [verify the fix](../verification/pre-completion-checklists.md).

Targeted fixes: add dependency markers for sequencing; surface implicit knowledge for omissions; tighten scope for additions; recalibrate abstraction for granularity; replace ambiguous terms for misinterpretations.

## Extreme granularity as a transparency strategy

Asking for highly detailed task descriptions — exact file paths, function names, parameter changes — forces the agent to expose design decisions before execution. "Style the navbar" becomes a list of specific CSS property changes with values. You can approve, reject, or redirect each one without waiting for the implementation.

This trades compactness for visibility. Use it when the cost of wrong execution is high, or when [calibrating instruction altitude](system-prompt-altitude.md) for a new domain.

## Real-time steering

Task lists are not static. When you [correct the agent mid-task](../patterns/agent-design/steering-running-agents.md), the updated list shows whether the correction landed. Say you change a requirement to "use green, not blue". If the remaining tasks update to match, the correction landed. If the tasks stay the same, the agent did not take it in, so restate it differently.

## Why it works

LLMs break tasks down by propagating explicit prompt constraints into the subtask structure. When constraints are absent or underspecified, the model fills the gaps with training priors. The result is a plan that reflects how similar tasks usually look rather than what you specified. That gap is the diagnostic signal: plan steps driven by prior knowledge show you exactly what you left implicit. Recent work that builds decomposition around a task's stated constraints reports that this constraint-aware decomposition outperforms prior planning methods ([Decompose, Plan in Parallel, and Merge, arXiv 2506.02683](https://arxiv.org/abs/2506.02683)).

## When this backfires

- Simple, well-specified tasks: a breakdown adds a round-trip with little diagnostic return when the task has a single unambiguous action.
- Exploratory tasks: divergence comparison needs a known intended sequence. Open-ended tasks with no correct approach have no baseline.
- Non-deterministic planners: agents that produce different plans across repeated prompts need multiple comparisons — a [trajectory-decomposition](../verification/trajectory-decomposition-diagnosis.md) concern — to separate instruction-driven variation from noise.
- Agents without plan-before-execute modes: the technique needs the agent to externalize the plan before acting. Silent execution exposes no signal.

## Tool-agnostic application

The technique works with any agent that produces task breakdowns — Claude Code's plan mode, GitHub Copilot's plan view, or custom agents with any task tool. Wherever an agent externalizes its understanding as a step list, that list is available for divergence analysis.

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

- Sequencing — the database migration step is missing entirely, so the agent would write application code against the old schema
- Omission — `Run linter` (step 4 above) replaces the `pytest tests/auth/` run added in the fix below; testing was implicit knowledge not stated in the instructions

Targeted fixes for each pattern:

```
Before making any code changes, run the database migration in db/migrations/.
After all code changes, run `pytest tests/auth/` and confirm all tests pass before finishing.
```

Re-running the prompt after adding these two sentences produces a plan that matches the intended sequence — catching both errors before any code was written.

## Key Takeaways

- Treat the agent's generated task list as a diagnostic artifact, not just an execution plan — the divergence from your intended steps reveals exactly where instructions failed.
- Classify divergences by pattern (sequencing, omission, addition, granularity, misinterpretation); each pattern maps to a different fix in your prompt.
- Request the plan before execution begins via [plan mode](../workflows/plan-first-loop.md) or an explicit "list every step you plan to take" prompt — silent execution exposes no signal.
- The technique only pays off when you have a known intended sequence; skip it for exploratory work or single-action tasks where comparison has no baseline.
- Extreme granularity is a transparency strategy: force the agent to expose design decisions in the plan when the cost of wrong execution is high.

## Related

- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Steering Running Agents](../patterns/agent-design/steering-running-agents.md)
- [The Implicit Knowledge Problem](../patterns/anti-patterns/implicit-knowledge-problem.md) — omissions in task plans often trace to implicit knowledge the agent was never given
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md) — structured verification before task completion, complementary to pre-execution plan review
- [Trajectory Decomposition Diagnosis](../verification/trajectory-decomposition-diagnosis.md) — diagnosing agent failures by decomposing execution traces
- [Completion Failure Taxonomy](../verification/completion-failure-taxonomy.md) — classifying the ways agents fail to complete tasks
