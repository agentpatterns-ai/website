---
title: "Decision-Fork Replay: Grading an Agent's Mid-Run Choices"
term: "Decision-Fork Replay"
description: "Grade an agent's mid-run choices by replaying the branch points in recorded runs, with everything after the fork hidden from the evaluated model."
tags:
  - agent-design
  - tool-agnostic
  - evals
  - arxiv
aliases:
  - decision fork mining
  - taste benchmark
  - hindsight-labeled fork questions
last_reviewed: 2026-09-28
maturity: emerging
---

# Decision-Fork Replay: Grading an Agent's Mid-Run Choices

> Decision-fork replay grades the choice an agent made at a branch point in a recorded run, and the best of 14 models scored 59.7%.

Decision-fork replay turns recorded agent runs into a test of mid-run judgment. Find a step where the run could have gone two ways and the record shows which way worked. Keep the prefix up to that step, describe both directions, and ask a model to choose. The recorded outcomes are the answer key, so nobody grades anything by hand. Pan and colleagues built Taste-Bench this way, 502 questions in which "we freeze the trajectory at the fork, hide all later work, and ask a model to choose between the two directions" ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).

## What you need before the method pays

Each question is cheap. The rollouts behind it are not.

- Volume. The engineering pool held 2,677 graded rollouts over 517 SWE-bench Pro tasks and the research pool 1,132 runs over 47 tasks. From both together the generator proposed 4,657 candidate forks, of which 10.8% passed all filters ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)). One attempt per ticket rules out the parallel construction and leaves only detours.
- Grading you trust. The label is whichever branch finished better, so a flaky suite credits luck as judgment. Only the last of three stages guards the label: "Of the 4,657 mined candidate forks, 1,809 pass the generator rubric, 729 survive the trivial filter, and 502 questions remain in the release". The undecidable filter drops questions whose "recorded outcome is not clearly consistent with the label", 227 of the 729 that reach it ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).
- A reason to want a decision-level number. Across 11 models the score correlates with SWE-bench Verified at r=+0.63, and "the correlation on the engineering subset is only r=+0.37", with a 95% interval of [-0.30,+0.79] there ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)). It measures something a pass rate does not, on too few models to say how much.

## Two ways a fork shows up in your logs

Parallel attempts give the first kind. Two runs of one task share a prefix, split, and one passes. The split is the fork and the passing branch is the answer.

Detours give the second. Inside a single run an agent commits to a direction, hits a failure, and recovers, so the abandoned direction and the recovery become the candidates. That asks whether a model spots the mistake sooner than the acting agent did, and it is harder. Averaged over the 14 models, parallel engineering scores 58.1% and detour engineering 35.9%, while in research the two constructions score 50.9% and 50.8% ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).

Score every question in both candidate orders. Position bias is large enough that "a question counts as correct only when both orders are answered correctly, so an answer that flips with the order does not count as taste", which puts the chance baseline at 25% ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).

## Why it works

Grading a mid-run choice is hard because execution and environment shape the outcome too. One run cannot say whether the decision or the follow-through decided it. Parallel attempts remove that confound by accident. The branches "share an equivalent prefix before the fork and sampling randomness assigns the judgments to the branches", so "the outcomes of the branches differ mainly because of the judgments at the fork" ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)). Retries you already paid for become a randomized comparison.

The score then tracks how much of the future the prefix reveals. A judge model annotates every fork with how far ahead the deciding evidence sits, and the mean over the 14 models "falls from 62.3% at the in-prefix level to 21.0% at the more-work level, near the 25% score of random guessing" ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)). Thinking longer does not manufacture absent evidence. Across three reasoning-effort settings on two GPT-5.6-family models, accuracy moved by −0.2 and +2.2 points, and both spent their longest reasoning where they scored worst ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).

## Reusing the forks as advice

The same forks can go back into a run as notes: the situation, the direction to avoid, the direction to take. On 41 held-out SWE-bench Pro tasks with a Qwen3.6-27B executor, notes from a distilled student model raised the success rate from 14.6% to 33.7%, against 39.0% when every note named the right direction ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).

Read the scope before copying it. Those notes are headed "Task-specific pitfall notes (from prior runs on this exact task)", so the gain lands on a re-run of a ticket somebody already attempted, not on new work. The no-advice condition also lacks the mandatory verification instruction both advice conditions carry, so the margin over it is not judgment quality alone. The 33.7% against the 39.0% ceiling is the clean comparison.

## When this backfires

- You run each task once. Detours still give you forks, in both domains. Detour engineering is the hardest cell, averaging 35.9% against parallel engineering's 58.1%, while detour research averages 50.8%, level with parallel research at 50.9% ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).
- Your outcome signal is noisy or subjective. The label inherits every flake in the suite. Only the last filter stage guards against this: it removed 227 of 729 questions whose "recorded outcome is not clearly consistent with the label" ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)).
- A ranking is what you want from it. One model returned 459 unparsable responses out of 1,004 presentations and scored 15.7%, and three of the 14 were dropped from the SWE-bench Verified comparison for unparsable rates above 9% ([arXiv:2609.25804v2](https://arxiv.org/abs/2609.25804v2)). A low score can be a formatting failure.
- You generalize the reasoning-effort result. The ablation covers two models of one family under a single token budget. Across seven benchmarks and up to 12 frontier models, a controlled study found instead that "larger token budgets substantially improve performance on benchmarks across multiple domains" and concluded that "benchmark scores are protocol-dependent" ([arXiv:2606.17930v3](https://arxiv.org/abs/2606.17930v3)).
- Outcome-derived labels look settled to you. Assigning credit to one step from how a trajectory ended is an open problem. Work on hindsight-modulated process rewards names "delayed propagation in sparse outcome rewards" as one of the two weaknesses it targets ([arXiv:2603.18683v1](https://arxiv.org/abs/2603.18683v1)).

## Key Takeaways

- Count your rollouts before anything else. 3,809 recorded runs yielded 502 usable questions, and without repeated attempts at one task only the detour construction is open to you.
- Report the number against 25%, not 50%, and score an answer that flips with candidate order as wrong.
- Expect detour engineering forks to score lowest. Detour engineering averaged 35.9% against parallel engineering's 58.1%, so a weak number there is partly the construction. Detour research averaged 50.8%, level with parallel research at 50.9%.
- Do not spend the finding on a reasoning-effort decision. It rests on two models of one family, and one independent study points the other way.
- Keep the fork notes for re-runs of tickets you have already attempted. That is the only setting the end-to-end gain was measured in.

## Related

- [Dispatch-Time Reasoning Level for Delegated Agents](dispatch-time-reasoning-level.md) — choosing effort at hand-off, the control this benchmark found unresponsive.
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — where extra thinking does buy something.
- [Agent Failure Trajectories and the Recovery Window](failure-trajectory-recovery-window.md) — the detour shape, seen from the recovery side.
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](../../verification/trajectory-decomposition-diagnosis.md) — stage-level precision and recall over the same kind of recorded run.
- [Cut-Point Replay: Test a Fix Against a Recorded Agent Run](../../verification/cut-point-replay-agent-regression-tests.md) — replaying a record for a regression test rather than for a judgment score.
