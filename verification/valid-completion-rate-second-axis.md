---
title: "Valid Completion Rate as a Second Scoring Axis"
term: "Valid Completion Rate"
description: "Score whether a run terminated normally and handed off an evaluable result, then split the non-clean attempts by stage so each routes to a different repair."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - valid completion rate
  - VCR
  - clean run rate
  - operational validity
last_reviewed: 2026-10-27
maturity: emerging
---

# Valid Completion Rate as a Second Scoring Axis

> Valid Completion Rate counts runs that terminate normally and hand off an evaluable result, separately from whether they solved the task.

Valid Completion Rate (VCR) is the share of scheduled attempts that both stop normally and leave a state the evaluator can consume. Zhang and colleagues define it as the measure of "how often attempts terminate normally with valid evaluator handoff, regardless of task correctness", and they keep correctness out of the handoff test in all six of their benchmarks: "In every benchmark, correctness affects the official task outcome but is never part of the valid-handoff condition" ([Zhang et al., arXiv:2610.32483v1](https://arxiv.org/abs/2610.32483v1)).

The two outcomes can diverge. A run can finish cleanly and solve nothing, and a run that died can still earn credit: "a run may complete validly without solving the task, or earn task credit despite abnormal termination" ([Zhang et al., arXiv:2610.32483v1](https://arxiv.org/abs/2610.32483v1)).

## What the second axis adds

VCR helps route repairs and compare execution reliability. It can also change a model-specific choice: Kimi favors OpenCode on Outcome Win Rate and Pi CLI on VCR Win Rate. Qwen favors Codex CLI and OpenCode, respectively ([Zhang et al., §6.1](https://arxiv.org/abs/2610.32483v1)).

The paper's outcome-only Fit ablation preserves the aggregate ordering and each model's Fit ordering. That does not imply that VCR and outcome metrics always select the same harness ([§6.3](https://arxiv.org/abs/2610.32483v1)).

### Your runner records termination and handoff per attempt

The study needed a per-benchmark mapping to decide both: `status=ok` with return code zero and no recorded framework failure on one benchmark, `termination_reason=agent_stop` on another, acceptance of the patch at its application stage on a third ([Zhang et al., §A.3](https://arxiv.org/abs/2610.32483v1)). A final score alone cannot reconstruct these conditions.

## Where each stage sends the repair

Clean completion, pre-normal loss, and post-normal handoff loss sum to 100% of attempts. The right-hand column quotes the paper's routing for each ([Zhang et al., §6.2.2](https://arxiv.org/abs/2610.32483v1)).

| What the attempt did | Stage | Where the paper directs diagnosis |
|---|---|---|
| Stopped abnormally | Pre-normal loss | "interface adherence, timeouts, and recovery" |
| Stopped normally, left nothing the evaluator could read | Post-normal handoff loss | "stopping, finalization, and submission validation" |
| Completed validly, scored low | Clean completion | "planning, action realization, and task-specific support" |

On the study's balanced three-model panel, "DeepAgents loses nearly ten times as many runs before normal termination as at post-normal handoff", while Codex CLI's losses were roughly balanced between the two stages ([Zhang et al., §6.2.2](https://arxiv.org/abs/2610.32483v1)).

## Why it works

The joint score has two factors with different repair paths. The paper gives the arithmetic: where VCR is positive, the joint score equals the completion rate multiplied by the mean task score among the attempts that completed validly, and a second identity "decomposes the official score into contributions from valid completions and other attempts" ([Zhang et al., §4](https://arxiv.org/abs/2610.32483v1)). The score alone does not identify which factor fell.

Across the 72 model-harness-benchmark cells of the paper's three-model panel, "Joint and official scores coincide in 37 of 72 benchmark-level cells; counting credit only from valid completions reduces scores in the other 35" ([Zhang et al., §6.3](https://arxiv.org/abs/2610.32483v1)). One cell swapped order: for MiniMax M3 on SWE-bench-45, DeepAgents scored 31.11 officially and 25.56 once credit was restricted to valid completions, against Codex CLI's 30.56 under both.

## When this backfires

- You expect VCR to reorder the aggregate harness ranking. The outcome-only Fit variant preserved the overall ordering and each model's harness ordering ([Zhang et al., §6.3](https://arxiv.org/abs/2610.32483v1)). Its gain is per-model choice and repair routing.
- You read a high rate as health. On ClawMark with Kimi K2.7, "Codex CLI and Pi CLI achieve 100.00% and 99.25% VCR, yet score only 11.96 and 11.93", and the authors conclude that "High VCR can thus coexist with action-realization gaps" ([Zhang et al., §6.2.3](https://arxiv.org/abs/2610.32483v1)).
- Your completion rate already sits at the top of its range. In the study, "Terminal-Bench 2, LOCA-Bench, and ClawMark mainly expose pre-normal failures, whereas VitaBench is near ceiling" ([Zhang et al., §6.2.2](https://arxiv.org/abs/2610.32483v1)). A measure with no variance routes nothing.
- You cannot separate abnormal termination from invalid handoff. One undifferentiated incomplete-attempt count collapses two buckets that the paper routes to different repairs.
- You reach for token count instead. Low consumption is ambiguous the same way a low score is: "Token Load must be read alongside outcomes: low load can reflect early failure, and high load can include repeated ineffective actions" ([Zhang et al., §6.4](https://arxiv.org/abs/2610.32483v1)).

## Example

ClawMark with Kimi K2.7 used 400 attempts per harness. Codex CLI achieved 100.00% VCR and scored 11.96; Pi CLI achieved 99.25% and scored 11.93. OpenCode scored 70.36 with 88.00% VCR; DeepAgents scored 58.65 with 53.25% VCR ([Table 4](https://arxiv.org/abs/2610.32483v1)).

VCR favors Codex CLI; task score favors OpenCode. Non-clean attempts still contributed 17.43 points to DeepAgents' score. They were not all unreadable ([§6.3](https://arxiv.org/abs/2610.32483v1)).

Their trajectory audit of the same 400-attempt cells found strict action-realization gaps, prospective action intent in reasoning with neither a structured action nor non-whitespace visible text in the same accepted response, in "6.75% of Codex CLI attempts and 40.50% of Pi CLI attempts, with none in OpenCode or DeepAgents" ([Zhang et al., §6.2.3](https://arxiv.org/abs/2610.32483v1)). They bound what that explains: "This pattern coincides with the score split across harnesses, while affected attempts score less than 1.3 points below unaffected attempts within each of Codex and Pi" ([Zhang et al., §6.2.3](https://arxiv.org/abs/2610.32483v1)). The authors conclude that "Trajectory-level diagnostics therefore complement VCR" ([Zhang et al., §6.2.3](https://arxiv.org/abs/2610.32483v1)).

## Key Takeaways

- Log two numbers per attempt, not one: whether it terminated normally, and whether it left an evaluator-consumable state. Correctness belongs to neither.
- Split the non-clean attempts by stage before you change anything. Abnormal termination points at timeouts, interfaces, and recovery; a failed handoff points at stopping and submission validation.
- Instrument this before you need it. The study's status conditions are per-benchmark and per-runner, and a stored score contains neither of them.

## Related

- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — the within-task stage split to run after an attempt completes cleanly and still scores low
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — final-state grading, which the handoff half of valid completion is the precondition for
- [Black-Box Agent Risk Scoring by Domain](black-box-agent-risk-scoring.md) — a scoring method whose authors record crashed runs entering a domain mean as zeros
- [Fleet Harness Attribution: Pinning the Model to Compare Whole Harnesses](../patterns/agent-design/fleet-harness-attribution.md) — the crossed design that attributes an outcome to the harness layer
- [Suspect the Harness Before the Model on a Regression](../patterns/agent-design/suspect-the-harness-not-the-model.md) — which component to look at first when a shipped agent's quality shifts
