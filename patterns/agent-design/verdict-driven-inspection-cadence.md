---
title: "Verdict-Driven Inspection Cadence for Agent Monitors (Cadence)"
term: "Verdict-Driven Inspection Cadence"
description: "Set a runtime monitor's next inspection interval from its own last verdict: on SWE-bench Lite a fixed 5-step schedule spent 36.10% more inspections for no resolve-rate gain."
aliases:
  - verdict-driven inspection cadence
  - adaptive inspection scheduling
  - adaptive monitor inspection interval
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - reliability
  - cost-performance
last_reviewed: 2026-10-11
maturity: emerging
status: current
---

# Verdict-Driven Inspection Cadence for Agent Monitors (Cadence)

> A monitor's own verdict sets its next inspection interval: widen after advisory guidance, reset to the base after a discarded step.

Cadence makes a runtime monitor's inspection interval a function of the monitor's own last verdict, so the supervision rate follows the run ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). A fixed interval gives a healthy agent and a failing one the same frequency of checks. That is the design [Wink's trajectory observer](wink-agent-misbehavior-correction.md) uses, where the interval "is statically predetermined and remains indifferent to the agent's real-time execution status" ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). The gain shows up twice. It holds the resolve rate of a fixed 5-step schedule for fewer inspections, and beats a fixed 7-step schedule at nearly the same cost by 9.00 points ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

## When this earns its cost

Four conditions bound the evidence.

- The monitoring budget is constrained. A denser fixed schedule scored 3.33 points higher, not significantly (p=0.24), at 15.00% more tokens ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- Trajectories run long enough to inspect several times. Varying the agent backbone, a GPT-5-mini agent averaging 26.6 steps gained 4.67 percentage points, a Qwen3-Coder-480B-A35B agent averaging 60.0 steps gained 15.00 ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- The monitor can diagnose a root cause. The interval rides on its judgement of execution health, and root-cause misdiagnosis is the largest monitor-attributed failure category at 26.8% ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- The agent's action space resists rule matching. Against LivePlan on Moatless, whose 11 structured tools map cleanly onto predefined phases, the margin fell to 4.33 points at an adjusted p-value of 0.1175 ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

## The rule

The scheduler holds a current interval, a base interval, a fixed growth step, and a ceiling. It inspects once the agent has taken that many steps since the last check. Each inspection sees the issue description, recent guidance, the recent trajectory, and the proposed next action before that action runs, and the verdict moves the interval:

- Advisory. The proposed action executes and the guidance is appended to the trajectory for later steps. The interval grows by the growth step, capped at the ceiling.
- Replacement. The proposed step is discarded, the guidance is injected, and the agent regenerates that step. The interval resets to the base.

The reference setting is a base interval of 5, a growth step of 2, and a ceiling of 20. That ceiling is a safety stop rather than a tuning knob, "with only 1.7% of inspection steps ever reached this limit across all experiments" ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). Cadence runs as "an external monitor supervising its execution", so the coding agent is unmodified ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). Its cost is the monitor's own LLM calls, 5.90 per task in the reference setting ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

## Why it works

The verdict is a health estimate the monitor has already produced, so the scheduler reads it from the intervention module's output. The paper's framing for the scheduler cites Jacobson's 1988 congestion-control paper: grow additively while the signal stays clean, snap back to the floor on a fault ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

Both halves of the design carry the result. Forcing one intervention policy on every inspection, always advisory or always replacement, cost up to 7.33 points with the adaptive schedule left in place ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). The schedule's contribution depends on the comparator: 9.00 points against a fixed 7-step schedule, and 36.10% fewer inspections against a fixed 5-step schedule at the same resolve rate.

## What the adaptation buys

The rows below hold the two-tier verdicts fixed and vary only the schedule, on 300 SWE-bench Lite tasks with mini-swe-agent (Gemini 2.5 Flash) and a GPT-5.2 monitor ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

| Schedule | Resolve rate | Tokens per task | Monitor calls per task |
|---|---|---|---|
| Verdict-driven (base 5, step 2) | 42.33% | 1.028M | 5.90 |
| Fixed, every 3 steps | 45.67% | 1.182M | 12.45 |
| Fixed, every 5 steps | 42.00% | 1.203M | 8.03 |
| Fixed, every 7 steps | 33.33% | 1.025M | 5.07 |

The 7-step row holds the token budget almost constant and keeps a similar inspection frequency (5.07 vs 5.90 calls) and loses 9.00 points, which the paper reads as showing that "strategic inspection timing is crucial when monitoring overhead is held constant" ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

The 3-step row is the counter-case, and it is the highest resolve rate in the ablation. The paper reports that gap as not significant: "this minor improvement is not statistically significant according to McNemar's test (p=0.24)", at 15.00% more tokens. The 5-step row reads the same way, spending 36.10% more inspections and 17.03% more tokens for a 0.33-point difference ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

So the adoption decision is a budget decision. The headline number measures having a monitor at all: against an unmonitored mini-swe-agent the gain is 25.33 percentage points, against the strongest guidance-only Fixed-Interval baseline (k=5) in that comparison 8.33 ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

## When this backfires

- Short runs can finish before the first inspection. "Inspection Timing Failure accounts for 8.1% of cases, where short execution tasks finish before the first inspection triggers", and it occurred only on Moatless, which "executes multiple tool calls in a single turn" ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). The paper's own remedy is to "incorporate tool invocation counts alongside step bounds when determining inspection timing for agents that bundle multiple actions per turn" ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- A growth step set too wide gives the gain back. Holding the base interval at 5 and raising the growth step from 2 to 6 drops the resolve rate from 42.33% to 34.00% ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)). The interval then outruns the health signal.
- A weak monitor is penalized twice. An advisory verdict both releases the proposed action and widens the next interval, so one misdiagnosis buys less supervision as well as a bad step. The monitor was the primary cause of 57.7% of 284 analyzed failures ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).
- An interval is not the only trigger available. Where you can reduce executions to symbolic states and you hold traces to learn from, ProbGuard instead learns a discrete-time Markov chain and intervenes when predicted safety probability crosses a threshold ([arXiv:2508.00500](https://arxiv.org/abs/2508.00500)), on autonomous driving and embodied household agents rather than coding.
- Scope is narrow. The evaluation "focuses on bug fixing and feature implementation tasks in Python", and the authors name other benchmarks as future work ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

## Example

On the SWE-bench Lite task `django__django-11179`, the goal was to make deleting a model instance without dependencies clear its primary key. Django implements deletion through a standard path and a fast path, and instances without dependencies take the fast path. The agent added the clearing logic to the standard path. The monitor inspected the proposed submission, blocked it, and issued guidance to implement the logic in the fast path instead; the agent regenerated that step and resolved the task, where the baseline agent submitted an invalid patch ([arXiv:2610.12269v1](https://arxiv.org/abs/2610.12269v1)).

This is the replacement branch: the verdict stopped the step rather than advising around it. Under the rule above, a replacement verdict also pulls the interval back to its base.

## Key Takeaways

- Key the interval on the verdict the monitor already returns, so the health signal costs nothing extra to collect.
- Compare against a token-matched fixed schedule before adopting. The margin over the best guidance-only Fixed-Interval baseline (k=5) was 8.33 points, against 25.33 over no monitor at all. With the two-tier verdicts kept, a fixed 3-step schedule scored 3.33 points higher, not significantly.
- Tune the growth step first and keep it small. A step of 2 held 42.33%; a step of 6 dropped to 34.00%.
- Count tool invocations alongside steps where the agent bundles several calls per turn, or the first inspection can arrive after the run has ended.
- Keep both halves. Dropping the two-tier verdicts cost 7.33 or 4.33 points; dropping the adaptive schedule cost tokens at equal or better resolve rate, except at a 7-step interval, which lost 9.00 points.

## Related

- [Splitting the Drift Judge from the Advisor (LivePlan)](judge-advisor-split.md) — the rule-based monitor this pattern is benchmarked against, which gates the advisor call instead of scheduling it
- [Wink: Classifying and Auto-Correcting Coding Agent Misbehaviors](wink-agent-misbehavior-correction.md) — the fixed-interval async observer whose synchronous form is the Fixed-Interval baseline here
- [Minimum-Sufficient Control Ladder: Escalate by Failure Mode](minimum-sufficient-control-ladder.md) — which control to add before the run, where this pattern sets how often to look during it
- [Effective Feedback Compute (EFC) for Harness Comparison](effective-feedback-compute.md) — counting only the feedback that moves the agent, the same placement-over-volume argument at trace level
- [Watcher Side Agents: Give the Second Agent a Trigger It Did Not Pick](watcher-side-agents.md) — the operator-addressed version, where the trigger decides whether the note is worth reading
- [Loop Detection for AI Agents](../../observability/loop-detection.md) — deterministic repetition detection, the cheapest trigger in this family
