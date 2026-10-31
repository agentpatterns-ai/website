---
title: "Edit-Request Steering Trigger: One Plan Before the First Source Edit"
term: "Edit-Request Steering Trigger"
description: "Fire a single planning intervention when a repair agent first asks to write a source file, using a trigger readable from the action type and target path, with no monitor and no checkpoint search."
aliases:
  - pre-edit steering trigger
  - first source-code edit intervention
  - search-free steering trigger
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - reliability
  - cost-performance
last_reviewed: 2026-10-26
maturity: emerging
status: current
---

# Edit-Request Steering Trigger: One Plan Before the First Source Edit

> A coding agent's first editor request to change a source file provides a steering trigger detectable from the action type and target path.

The harness must expose an edit request before it executes. Whether an intervention helps depends on the guidance the planner supplies. The evidence covers single-attempt bug repair; transfer to multi-stage builds needs validation. In the evaluated method, one planning intervention replaces periodic review or anomaly monitoring.

## What the trigger is

A source-code edit here means a file-editor request whose target path sits inside the repository's source set, with that set fixed before the run. Detecting it needs the action type and the path and nothing else: "The predicate can be evaluated before the requested edit executes, using only the action type and target path" ([PAUSE, arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The paper calls that property search-free, because locating the moment needs no learned monitor, no checkpoint search, and no extra model call.

The moment also arrives late. Across 500 recorded Qwen3-coder runs on SWE-bench Verified, 476 contained such a request, and "its median position is 60.0% of action progress, and 80.5% occur after the midpoint" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The planner can use the investigation recorded by then, before the requested editor change executes. Earlier shell commands may already have changed source files.

## Why it works

The trigger reads an event in the agent's own action stream rather than inferring the agent's state. Firing it needs no model call. It also lands where two conditions hold together, "when accumulated evidence is available to inform the repair and the proposed change remains open to revision", which the authors frame as a trade-off between cuts: "an earlier intervention gives the Planner too little of the investigation to ground a plan, whereas a later one arrives after the agent has committed to and built on its own changes, which the plan must then overturn" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).

Controlled continuation arms separate the plan's contribution from the value of another turn. On 223 eligible Qwen3-coder failures resumed in OpenHands on SWE-bench Verified, with all three arms retaining "the same checkpoint, conversation history, workspace, and remaining Executor budget", "Unaided continuation recovers 9 of 223 failures (4.0%)", a self-reconsideration cue recovers 13 (5.8%), and a plan from GPT-5.6 Sol recovers 79 (35.4%) ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The arms share the restored state and the remaining budget, so what separates them is the guidance.

## What the evidence covers

Every figure here comes from the authors' own evaluation of the method they propose, so read the boundary before the deltas. Online gains are measured against each harness's unmodified executor, with Qwen3-Coder-30B-A3B-Instruct executing and GPT-5.6 Sol planning, on all 500 SWE-bench Verified tasks: "PAUSE improves resolution in all three harnesses, by 14.8 percentage points in SWE-agent, 6.0 in Pi, and 16.8 in OpenHands" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The main comparisons use one attempt per task.

For online steering the authors compare against two alternatives. [LivePlan](https://arxiv.org/abs/2608.06701) invokes an advisor when rule-based checks detect trouble, and the [SICA](https://arxiv.org/abs/2504.15228) overseer reviews the trajectory on a schedule.

Against both, the result is weaker than the headline. On Verified in SWE-agent, the margin over LivePlan is "a gain of 3.2 percentage points that is not statistically significant (p=0.11)", and SICA scores higher: "SICA achieves the highest aggregate resolution at 67.6%, 2.6 percentage points and 13 tasks above PAUSE's 65.0%; this difference is not statistically significant (p=0.18)" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The measured advantage is lower planner cost; the non-significant differences do not establish equal resolution: it "stays within a non-significant margin of SICA at about 11% of its Planner cost" on Verified, and about 15% on Multilingual. The paper is a preprint submitted in October 2026, and every comparison above is the authors' own.

## When this backfires

- The agent edits source through the shell. "Trajectories without such a request receive no intervention, limiting coverage in workflows whose source changes use other editing interfaces, such as shell commands" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). The authors offer this as one likely contributor to the Pi harness gaining least, and say they did not measure how often it happens.
- The chosen planner supplies weak guidance. Using the executor's own model as a separate planner recovered 12 of those 223 failures (5.4%), against 9 (4.0%) for no plan at all. Offline resume with Qwen3-30B-Thinking planning reached 43.4% on the 500 Verified tasks, below the unmodified executor's 45.6%, and across the 178 originally solved tasks evaluated under both planners its plans produced 26 regressions against the no-plan control's 10 ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).
- One plan goes stale. The framework "supplies a single repair plan and does not refresh its guidance as new observations arrive" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)), so a contradicting test result later in the run is the agent's problem to reconcile.
- The investigation missed the evidence. The planner reads the issue and the pre-edit transcript and "cannot independently inspect the workspace or execute commands" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).
- The stack sits outside the measured set. On SWE-bench Multilingual, "Rust is the only language in which PAUSE falls below the unmodified Executor, resolving 16 of 43 tasks against 19" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)). LivePlan and SICA also fell below baseline on Rust. All three measured guidance methods share the drop.
- The work is not bug repair. Transfer "to substantially different repositories or longer, multi-stage development workflows remains unexamined", and the authors note that under broader path rules "the detected event need not represent the same stage of investigation in every repository" ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).

## Example

The paper walks one scikit-learn case through the trigger. The executor's source reads and scratch reproduction show two things. Successive evaluations using the same cross-validation generator obtain two folds and then zero folds. Candidate scoring in the sequential feature selector repeatedly passes the original `cv` object through validation and splitter normalization. The first source-code edit is blocked. The planner, reading only that transcript, returns a plan to normalize CV once per fit and propagate the reusable splitter to each candidate. The same executor resumes with its context and workspace preserved, edits the sequential feature selector, and checks that both evaluations retain two folds ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).

The fold-count evidence exists because the agent had already run its reproduction, and the wrong edit had not yet been written. The trigger fires exactly where both of those are true.

## Key Takeaways

- Read the trigger from the action type and target path, before the edit executes. That is what removes the monitor and the extra model call.
- Budget the planner, not the monitor. Planner cost stayed between $0.037 and $0.052 per task across the three harnesses tested with Qwen3-coder and GPT-5.6 Sol, under 2% of executor tokens ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).
- Compare cost and resolution on your workload. On Verified, SICA's planner spend was 8.9 times PAUSE's for a resolution difference that was not statistically significant ([arXiv:2610.29870v1](https://arxiv.org/abs/2610.29870v1)).
- Audit how your agents actually write files first. A source edit issued through a shell command does not fire the trigger. A trajectory that never issues an editor request gets no intervention at all.
- Measure the planner choice rather than assuming it. Recovery on the same 223 failures ranged from 12 to 79 tasks across the four planners tested.

## Related

- [Verdict-Driven Inspection Cadence for Agent Monitors (Cadence)](verdict-driven-inspection-cadence.md) — the alternative when you keep a monitor and tune how often it looks
- [Comparison-Only Advisor: Steering a Large Actor With a Tiny Comparator](comparison-only-advisor.md) — advice on every action instead of once per run
- [Critic Agent Pattern: Dual-Model Plan Review](critic-agent-plan-review.md) — plan review before execution begins, rather than after investigation
- [Agent Failure Trajectories and the Recovery Window](failure-trajectory-recovery-window.md) — the same timing question framed by failure onset instead of an observable action
- [Planning Stage Preconditions: Budget Headroom and Task Text](planning-stage-preconditions.md) — whether a planning stage earns its tokens at all
