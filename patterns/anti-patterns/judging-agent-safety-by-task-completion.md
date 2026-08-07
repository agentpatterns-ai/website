---
title: "Judging Agent Safety by Task Completion (Action-Boundary Violations)"
term: "Action-Boundary Violations"
description: "A completed task is not a safe one. Under underspecified DevOps instructions, coding agents guess a target and overstep, violating an action boundary in 55.8-67.8% of runs."
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - action-boundary violation
  - action boundary overstep
  - completion is not safety
last_reviewed: 2026-07-03
maturity: emerging
---

# Judging Agent Safety by Task Completion (Action-Boundary Violations)

> A completed task is not a safe one: under vague instructions, coding agents guess and cross action boundaries on production infrastructure.

Treating "task completed" as evidence that an agent acted safely is the mistake. A benchmark that varied only the instruction, not the task or environment, found that underspecification does not mainly make agents fail — it makes them guess. Across five agent and model configurations, 55.8-67.8% of runs violated at least one action boundary ([Ji et al., 2026](https://arxiv.org/abs/2607.02294)). Completion-centric evaluation counts a confident wrong action as a success and so overstates how safely an agent can run on its own.

## What an action-boundary violation is

UnderSpecBench holds the environment and the one ground-truth safe action fixed, then varies the instruction along three axes: how clear the intent is, how certain the target is, and how large the blast radius is. Deterministic side-effect oracles score each run as Safe Success, Wrong Target, or OverScope. A Wrong Target hits a different or protected resource; an OverScope action is broader or more destructive than the task needed. Safe Success requires the intended action, no wrong target, and no overscope at once ([Ji et al., 2026](https://arxiv.org/abs/2607.02294)).

Two results matter for anyone gating agents on completion. Target uncertainty collapses action quality: among runs where the agent acted, Safe Success fell from 67.9% when the target was clear to 8.6% when it was not, and Wrong Target rose from 9.6% to 75.1%. Blast-radius warnings barely changed behavior — action rate stayed near 65% whether the operation was reversible or not ([Ji et al., 2026](https://arxiv.org/abs/2607.02294)). Overstepping concentrated on shared control planes: 77.2% OverScope on infrastructure and capacity surfaces versus 14.4-37.6% on bounded-object surfaces.

## Why agents guess instead of asking

The agent resolves missing information by inferring against local context rather than by asking. When the target is uncertain, it "infers a plausible object from local context and executes against it instead of confirming which candidate the user intended." When intent is vague, there is "nothing concrete to ask about," so the agent guesses or defers. A large blast radius "signals danger but no missing fact, so it prompts no question" — agents carry no mechanism that couples irreversibility to caution ([Ji et al., 2026](https://arxiv.org/abs/2607.02294)). Overstep lands on control planes because the implementation path runs through a plane whose effects reach past the named target. Whether the agent asks at all is a property of the model and harness, not the risk: in the same benchmark one configuration asked a clarifying question 38-45% of the time while another asked 1.7% of the time.

## Example

**Before — completion treated as the safety signal:** an operator asks an agent to "clean up the old release." The target is underspecified. The agent infers a plausible artifact, deletes it, and reports the task done with exit code 0. Nothing distinguishes this run from one that deleted the correct artifact — the completion signal is identical whether the agent hit the right target or a protected one.

**After — the boundary is measured, not assumed:** the harness exposes a first-class Ask-User affordance and a confirmation schema for irreversible or broad actions, so an underspecified target draws a clarifying question instead of a guess, and a destructive action on a shared control plane needs explicit confirmation before it runs ([Ji et al., 2026](https://arxiv.org/abs/2607.02294)).

## When over-correcting backfires

The fix is calibrated restraint, not maximal clarification. Forcing an agent to confirm every instruction reintroduces the human bottleneck autonomy was meant to remove. Agents already pause for clarification more often than humans interrupt on complex tasks ([Anthropic, 2026](https://www.anthropic.com/research/measuring-agent-autonomy)), and exhaustive asking plateaus: a reward-trained clarification model matched GPT-5's resolution rate on underspecified issues while asking 41% fewer questions ([Vijayvargiya et al., 2026](https://arxiv.org/abs/2604.14624)). Add friction where it earns its cost — uncertain targets and high blast radius — not to well-specified, read-only, or already-gated work. The benchmark authors note their rates are a lower-bound stress test of the fully autonomous path, not a prediction for a deployment already gated by approvals, IAM, or CI.

## Key takeaways

- A green run status and a "task completed" report say the harness exited, not that the agent acted on the right target with the right scope.
- Underspecified targets, not vague intent, are the dominant driver of wrong-target and overscope actions; specify the target, not just the goal.
- Blast-radius cues alone do not make agents cautious — irreversibility has to be coupled to a confirmation gate in the harness or below it.
- Route the fix to its owner: calibrated restraint at the model, a first-class Ask-User affordance and confirmation schemas at the harness, and irreversibility-keyed guards at the system layer.

## Related

- [Interactive Clarification for Underspecified Tasks](../agent-design/interactive-clarification-underspecified-tasks.md) — the mitigation: agents that explore then ask targeted questions lift resolution on underspecified tasks.
- [Destructive-Failure Mechanism Attribution by Mitigation Owner (ClayBuddy Three)](destructive-failure-mechanism-attribution.md) — the three-owner cut of destructive failures this page routes fixes through.
- [Blast Radius Containment: Least Privilege for AI Agents](../../security/blast-radius-containment.md) — scoping permissions so an overscope action cannot reach a protected resource.
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the sibling failure where the completion signal itself is unreliable.
- [Run-Status vs Task-Status Confusion in Autonomous Agent Runs](run-status-vs-task-status-confusion.md) — why a clean exit code is not evidence the task succeeded.
- [Task Completion as Tool Certification (Silent Tool Rot)](task-completion-as-tool-certification.md) — the parallel failure where completion overstates the correctness of a reused agent-built tool rather than its safety.
- [Task-Uniform Agent Permissions Ignore Where Failures Land](task-uniform-agent-permissions.md) — which task contexts the confirmation gate belongs in, from an incident corpus of 547 confirmed failures.
