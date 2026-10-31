---
title: "A Separate Critic Over Completion-Time Self-Checking"
term: "Separate-Critic Verification"
description: "The strongest separate critic design, which also reads the execution trajectory, gained 9.5 points on Terminal-Bench against the strongest completion gate's 6.0, and cost less on both coding benchmarks."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - separate-critic verification
  - independent review layer
  - critic over self-recheck
last_reviewed: 2026-10-28
maturity: emerging
---

# A Separate Critic Over Completion-Time Self-Checking

> The strongest separate critic design, which also reads the execution trajectory, gained 9.5 points on Terminal-Bench against the strongest completion gate's 6.0, and cost less.

Verification compute in an agent harness can go into the agent's own prompt, into reminders during the run, into a gate that reopens the work when the agent tries to finish, or into a second model that reviews the finished deliverable. A comparison of 17 designs across those four layers measured the more favorable accuracy-to-cost trade-off at the second model. Completion gates are the one layer of the four its authors recommend against ([Zhang et al., arXiv:2610.34577v1](https://arxiv.org/abs/2610.34577v1)).

## Conditions the result rests on

The measurement is narrower than the recommendation, so read the conditions before moving budget.

- The critic was cheaper than the agent in most arms. One model, Qwen3.7-Plus, reviewed for all seven coding agents, and the study's output rate for it undercuts six of the seven. The exception is DeepSeek V4-Flash, so an agent that is already the cheap half moves the ratio.
- The sample is small: a 31-task Terminal-Bench 2.1 subset chosen for difficulty spread, a comparably sized SWE-bench Verified subset, and three trials per model and task.
- On SWE-bench Verified the accuracy case is thin. The best critic design gained 6.6 points against the best gate's 6.2, so cost carries that benchmark rather than accuracy.
- Per-model results include flat ones. On Terminal-Bench, claim-guided review of the agent's changes moved DeepSeek V4-Pro and DeepSeek V4-Flash by 0.0 points.

## What each layer bought

Average accuracy change on Terminal-Bench, by layer, across the designs tested in each ([Zhang et al., Table 2](https://arxiv.org/abs/2610.34577v1)):

| Layer | Who checks | Designs | Average change |
|---|---|---|---|
| L0 initial instructions | the agent | 2 | +1.2 to +3.3 pp |
| L1 execution-time reminders | the agent | 3 | +3.5 to +5.4 pp |
| L2 completion gates | the agent | 8 | +0.7 to +6.0 pp |
| L3 independent review | a separate critic | 4 | +5.9 to +9.5 pp (+9.5 with trajectory, +5.9 to +6.9 changes-only) |

Cost is where the layers separate. Independent review ran at 1.13 to 1.25 times baseline on Terminal-Bench and 1.00 to 1.04 times on SWE-bench Verified, counting the critic and the agent's revision. The completion gates that reached the top of their range are the rejection designs, and those cost 1.60 to 1.76 times baseline on Terminal-Bench and 1.48 to 1.56 times on SWE-bench Verified. Rechecking triggered early cost 1.13 and 1.20 times baseline and gained +4.8 and +4.1 points.

The authors' recommendation follows from that gap, and it is a recommendation rather than a measurement: "we recommend avoiding completion-time self-checking, as its gains are limited relative to the additional cost and reopening work does not consistently improve the final artifact".

## Why it works

A self-check can rerun the agent's own blind spot, so reopening the work buys more execution instead of more coverage. On Terminal-Bench, user rejection produced model-level medians of 12 to 19 additional agent steps and file-changing actions in 86 to 96 percent of the runs where it fired, and the authors read the trajectories as showing that "a completion gate creates an opportunity for repair, but the agent must still identify the relevant defect and preserve a valid final artifact". A fresh critic can break the blind spot, though fresh context does not guarantee independent coverage. It "starts in a fresh context" with the task specification and sandbox access, cannot edit the deliverable, and in the logged trajectories tested cases the agent had not tried. On one log-parsing task the critic tested a case with the date appearing before the IP address and exposed a missed match in a regex the agent had already declared done ([Zhang et al., arXiv:2610.34577v1](https://arxiv.org/abs/2610.34577v1)).

The context result splits by benchmark. On Terminal-Bench the two trajectory designs gained +8.4 and +9.5 points against +5.9 and +6.9 for the changes-only designs. On VisualBench, review of the task plus the agent's changes beat review that also received the full execution trajectory on human preference for visual artifacts, 21.2 against 13.2 net points without required visual inspection. Across all three benchmarks the full trajectory did not consistently improve outcomes, and on the two coding benchmarks the trajectory designs incurred 29 to 43 percent higher critic cost, so the authors default to task and changes.

## When this backfires

- A wall clock can expire inside the review round. One GLM-5.2 critic correctly confirmed that asynchronous cleanup was still incomplete, and the run hit its 45-minute limit before the repair finished.
- Scaling depth costs more than scaling width. Two review rounds cost 79.5k mean critic tokens for 65.6 percent accuracy where two critics cost 69.7k for 64.4 percent, and four critics approached four-round accuracy at 19 percent lower total cost.
- The value of any feedback channel is itself contested. Below roughly 7B parameters, discarding a failed program and resampling beats returning the failure for repair at matched budget ([blind resampling over self-repair](../loop-engineering/blind-resampling-over-self-repair.md)).
- A blocking completion gate may be there for a different job. A [pre-completion checklist](pre-completion-checklists.md) stops a premature done signal, which is a correctness floor rather than an accuracy purchase, and this comparison does not price that.
- Rounds accumulate. Repair gains concentrate in the first few rounds and later ones mostly burn tokens ([bounded repair-loop iterations](bounded-repair-loop-iterations.md)).

## Key Takeaways

- Spend first on a separate critic that reads the finished deliverable, runs its own checks, and hands findings back without edit rights.
- Start that critic on the task and the diff, the authors' cost-based default, and add the execution trajectory only if you can measure a gain: it scored highest on Terminal-Bench and trailed changes-only review on VisualBench.
- Add critics in parallel before adding rounds in sequence. Rounds bought slightly more accuracy, critics bought it for less.
- Keep the conditions attached when citing this: a 31-task benchmark subset, one critic model across seven agents, and a 0.4-point margin over the best gate on SWE-bench Verified.

## Related

- [Probing an Agent's Completion Claim in a Disposable Fork](completion-claim-probe.md) — how to run the critic call this page argues for, with fork isolation and execute access
- [Verification Surface: Match the Tool to the Failure](verification-surface-reach-and-cost.md) — the same cost-per-check question applied to the tools an agent checks itself with
- [When a Second Model Helps in LLM Review](cross-model-review-independence.md) — whether the critic should come from a different model family
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md) — the mid-run layer this comparison measures as a modest, model-dependent gain
- [Evaluator-Optimizer Pattern for AI Agent Development](../patterns/agent-design/evaluator-optimizer.md) — the generator-and-critic loop as a general structure
