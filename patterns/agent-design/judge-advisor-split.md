---
title: "Splitting the Drift Judge from the Advisor (LivePlan)"
term: "Judge-Advisor Split"
description: "Separate the component that decides whether an agent has drifted from the component that decides what to do about it, so the always-on half runs without an LLM call."
aliases:
  - judge-advisor split
  - LivePlan
  - deterministic monitor with LLM advisor
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - reliability
  - observability
last_reviewed: 2026-08-10
maturity: emerging
---

# Splitting the Drift Judge from the Advisor (LivePlan)

> A deterministic monitor decides whether an agent drifted; an advisor model decides what to do, and only sees trajectories the monitor flagged.

Runtime supervision of a long-running coding agent asks two questions: has this trajectory gone wrong, and what should happen next. LivePlan answers them in separate components, with a rule-based monitor gating the advisor LLM ([Liu et al., 2026 — arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).

## When the split earns its cost

Evidence for this architecture sits on one scaffold and one task shape, so treat it as conditional. Build the split when all four hold:

- The task has a phase sequence a state machine can check. LivePlan's monitor is defined against navigate, reproduce, patch, validate, and its blocking rules exist only because that order does ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).
- Trajectories are long. The published thresholds fire after seven consecutive steps in one phase, with a five-step cooldown between advisor calls, so a run finishing in a dozen steps rarely trips them.
- The executor is not already near its ceiling. Reported gains on SWE-bench Pro run from +15.24 pp on the weakest executor tested down to +5.45 pp on the strongest ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).
- The executor follows mid-run correction. The paper attributes nearly all of its resolved-to-unresolved regressions to "the executor's inability to follow correct guidance" ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).

## The two halves

The monitor builds two views of the trajectory as it runs: an action graph enriched with thought nodes, and a phase-sequence abstraction. It checks both against fixed algorithms and sorts findings into two classes. Blocking drifts stop execution: plan violation, premature patching, skipping the patch, skipping validation, thought and action oscillation. Non-blocking drifts let execution continue with advice attached: long stagnation in one phase, prolonged phase duration, a repeated action appearing as a back-edge in the graph. No model call is involved, and the reported overhead is "a few milliseconds" ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)).

The advisor runs only after the monitor fires and the cooldown has elapsed. It receives the issue text, the trajectory slice since the last advice, the previous advice, and a canned message for the detected drift class. It returns "a next-step recommendation, rather than a long-horizon plan" ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). Advisor spend came to $0.01–$0.06 per instance across the three executors tested.

## Why it works

The stated reason is about incentive rather than cost: "an advisor prompted to diagnose and provide corrective advice is incentivized to find a problem," so a model asked both questions at once invents defects on healthy runs ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). Gating on a rule removes the opportunity: the model is never consulted about a trajectory the rules call clean, which changes its question from "is anything wrong here" (to which it will answer yes) into "given this specific drift, what next". This is separation of concerns applied to supervision, and the paper's own re-planning baseline shows the cost of skipping it. That baseline redirected an agent toward a file that did not exist, and it landed below the vanilla agent on two of three executors, by 2.97 pp and 2.12 pp ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). The near-zero monitor cost is a consequence of that design, not its motivation.

## When this backfires

Cheap detection is not well-timed detection. Across 9,429 incident-grounded code-agent trajectories, a rule-based guardrail carrying 847 rules reached 86% recall while its intervention timing came out "statistically indistinguishable from random," because more than three-quarters of its alerts fired on benign prefix code before any violation happened ([StepShield, 2026 — arXiv:2601.22136v2](https://arxiv.org/abs/2601.22136v2)). High recall bought nothing: the alerts arrived before there was anything to correct.

A conflated judge and advisor also works in production, which weakens the case for building two components. Wink runs an LLM observer that classifies and corrects in one pass over 10,000+ real trajectories, and reports 90% resolution for misbehaviors needing a single intervention ([arXiv:2602.17037v2](https://arxiv.org/abs/2602.17037v2); see [Wink](wink-agent-misbehavior-correction.md)). If your drift modes are semantic rather than structural, rules will not see them at all.

Thresholds do not travel. The published constants were tuned on SWE-bench under one scaffold at temperature zero, so carrying them elsewhere imports somebody else's false-positive rate. Deterministic detectors are not reliably net-positive: across 220 instrumented agent runs, only half of twelve automated loop interventions reduced the signal they targeted, and one produced 13 times more signal than it suppressed ([boucle2026, 2026](https://dev.to/boucle2026/how-to-tell-if-your-ai-agent-is-stuck-with-real-data-from-220-loops-4d4h); see [loop detection](../../observability/loop-detection.md)).

The intervention also does not close the gap. Blocking drifts fell from 55.63% of trajectories to 34.37% on SWE-bench Pro ([arXiv:2608.06701v1](https://arxiv.org/abs/2608.06701v1)). A third of runs still drifted with the monitor watching.

## Example

An agent working a repository issue has spent nine consecutive steps reading files without reproducing the reported failure.

A conflated observer reads the trajectory and is asked whether anything is wrong. Because it is prompted to diagnose, it produces a diagnosis: the agent is looking in the wrong module and should try `src/adapters/`. If that module is irrelevant, the agent has now been sent somewhere worse than where it was.

Under the split, the monitor evaluates one rule. Steps in the current phase exceed the stagnation threshold and the phase is still navigation, which is a non-blocking drift. Only then is the advisor called, and its prompt already carries the finding, so it answers a narrower question: the agent has been navigating for nine steps without reproducing, so what is the next step. The advisor recommends writing a minimal reproducer from the issue text before reading further.

On a trajectory where the agent had reproduced the failure at step three and was legitimately reading widely, no rule fires and no model is called at all, which is the case the split exists to protect.

## Key Takeaways

- Separate the component that judges whether a trajectory drifted from the one that advises what to do next
- A model asked to diagnose will find something, which is why the always-on half should not be a model
- The deterministic half only exists if the task has a checkable phase structure; without one there is nothing to gate on
- Gains shrink as the executor gets stronger, from +15.24 pp to +5.45 pp across the executors tested
- High recall does not mean useful timing, since a rule set can flag every failure and still intervene at random

## Related

- [Classifying and Auto-Correcting Coding Agent Misbehaviors (Wink)](wink-agent-misbehavior-correction.md) — the opposite architecture, where one LLM observer both classifies and corrects
- [Plan Compliance in Agents](plan-compliance-in-agents.md) — measuring whether the instructed phases run, which is the signal this pattern acts on
- [The Advisor Strategy](advisor-strategy.md) — a frontier advisor gated by task difficulty rather than by detected drift
- [Loop Detection for AI Agents](../../observability/loop-detection.md) — deterministic detection with a canned nudge and no advisor
- [Steering Running Agents](steering-running-agents.md) — the human-issued version of the same mid-run correction
