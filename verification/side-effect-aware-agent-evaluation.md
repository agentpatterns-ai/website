---
title: "Side-Effect-Aware Evaluation: Score Authorization Too"
term: "Side-Effect-Aware Evaluation"
description: "Score task completion and writes outside the authorization set separately with a deterministic trace oracle. A run can pass one check and fail the other."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - collateral damage evaluation
  - authorization compliance axis
  - SABench
  - two-axis agent evaluation
last_reviewed: 2026-10-31
maturity: emerging
---

# Side-Effect-Aware Evaluation: Score Authorization Too

> Side-effect-aware evaluation scores each run twice, once for task completion and once for writes outside the task's authorization set.

A side-effect-aware eval declares, per task, which state changes the user authorized. It then checks the agent's trace for any successful write outside that set, and reports that count beside the goal result. Huang and colleagues call such a write collateral damage (CD). They measure it on SABench, a benchmark of 201 email, calendar, and ticket tasks ([Huang et al., arXiv:2610.34167v1](https://arxiv.org/abs/2610.34167v1)). Across 2,211 model-task pairs, 12.8% of the runs that reached the goal still wrote outside the boundary. An eval that scores only the goal counts those runs as passes.

## What the paper builds

Each task has an initial state, an authorization boundary, and goal conditions. The oracle is deterministic and "uses no LLM-based or natural-language judgment at any stage". It takes each successful state-changing tool call from the trace, ignores reads, failed calls, and idempotent calls, and replays the writes on the initial state. It then reports goal satisfaction and CD as two separate results ([Huang et al., §4](https://arxiv.org/abs/2610.34167v1)).

CD is the set of realized writes minus the explicit authorization set and a small allowance for bookkeeping writes. On a task whose request is ambiguous, the explicit set is empty, so any write before a clarifying question counts. The paper states that CD "measures authorization noncompliance, not realized harm" ([Huang et al., §2](https://arxiv.org/abs/2610.34167v1)).

The corpus crosses four state structures (independent, dependent, externally reachable, cross-tool) with four trap families: ambiguity, mis-targeting, cascade harm, and overreach ([Huang et al., §3](https://arxiv.org/abs/2610.34167v1)). The authors ran 11 models once per task at temperature 0.

## What the second axis found

| Result | Figure |
|---|---|
| Runs with CD, all 2,211 pairs | 15.2% |
| Goal reached and CD present, share of all runs | 11.4% |
| Goal-satisfied runs with CD | 12.8% |
| CD on ambiguity tasks | 38.8% |
| CD in dependent and cross-tool state | 22.1%, 21.0% |
| CD in externally reachable and independent state | 11.0%, 9.4% |

Source for the table: [Huang et al., §6 and A.3](https://arxiv.org/abs/2610.34167v1). The paper calls the state-structure gap an association, not a causal effect ([§6.3](https://arxiv.org/abs/2610.34167v1)).

The 11.4% figure is the share of all runs in which the goal is reached and CD is present. The 12.8% figure includes ambiguity tasks, where the goal condition is empty and so passes automatically. Restricted to the 156 non-ambiguous tasks, 4.1% of goal-satisfied runs still had CD, with a 95% interval of 2.2 to 6.4 ([§6.1](https://arxiv.org/abs/2610.34167v1)).

DeepSeek V3.2 and GPT-5.4 reached goal rates of 87.6% and 88.1%. Their CD rates were 23.9% and 7.5%, a 16.4-point gap. Across all 11 models, CD varied 4.7 times at comparable goal rates ([Huang et al., §6.2](https://arxiv.org/abs/2610.34167v1)). A leaderboard sorted by goal rate hides that gap.

## The confirmation trade

The authors tested a prompt-level confirmation policy on 115 tasks: the 45 ambiguity tasks and the 70 non-ambiguous dependent or cross-tool tasks. The policy tells the agent to stop and ask before an external write or a write to an unnamed target. Only the system prompt changed ([Huang et al., A.10](https://arxiv.org/abs/2610.34167v1)).

| Model | Goal, baseline to confirmation | CD, baseline to confirmation |
|---|---|---|
| GPT-5.4 | 95.7% to 79.1% | 18.3% to 5.2% |
| Kimi K2.5 | 93.9% to 80.0% | 25.2% to 12.2% |
| Qwen 3.5 Plus | 97.4% to 84.3% | 24.3% to 7.0% |

The paper reports a 52 to 71% cut in CD at a cost of 13 to 17 goal points, and 5 to 12% CD remains. Both halves matter. A goal-only eval sees a 13 to 17 point loss and rejects the policy. A CD-only eval sees the cut and accepts it. Only the pair lets you decide.

## Where it transfers

The authors limit their claim: "The reported CD rates and model rankings are specific to this setting and should not be extrapolated to other domains". They also name what transfers: "the reusable part is the evaluation design, which checks goal satisfaction and authorization compliance separately over realized writes" ([Huang et al., §9](https://arxiv.org/abs/2610.34167v1)). Use the design, not the percentages.

For coding agents the paper lists three missing pieces. A coding version "would require path- and file-scoped authorization contracts, diff-based write extraction, and semantic goal checks", and the authors leave it to future work ([§9](https://arxiv.org/abs/2610.34167v1)). The paper reports no coding-task results. The [overeager-behavior diagnostic](overeager-behavior-elicitation-scope-trap-fragments.md) already scores out-of-scope tool calls in coding agents, so build on it before writing a new oracle.

Two limits apply:

- Each pair ran once. The paper's intervals "capture template composition rather than sampling variability" ([§9](https://arxiv.org/abs/2610.34167v1)), so repeat runs before you rank two close models.
- An always-ask agent avoids CD. The paper reports an unnecessary-clarification guard metric beside goal and CD for that reason ([§9](https://arxiv.org/abs/2610.34167v1)).

## Key Takeaways

- Report goal and authorization compliance as two results per run. The cell that matters is goal reached and CD present: 11.4% of all runs in SABench.
- Write the authorization set before the run and compare it to the trace. A deterministic oracle needs no judge model, and it only works when the set is explicit.
- Seed tasks with ambiguity, linked state, and external recipients. Those strata held most of the CD, and the safe action in an ambiguous task is a question.
- Do not extrapolate the percentages. They come from office workflows run once per model, with no coding tasks.
- Test every mitigation on both axes. Confirmation cut CD by 52 to 71% and cost 13 to 17 goal points.

## Related

- [Overeager-Behavior Elicitation](overeager-behavior-elicitation-scope-trap-fragments.md) — Scores out-of-scope tool calls in coding agents with a filesystem-delta oracle; the closest sibling.
- [Valid Completion Rate as a Second Scoring Axis](valid-completion-rate-second-axis.md) — Another second axis, for run validity instead of authorization.
- [Recovery as a Separate Eval Axis](recovery-as-separate-eval-axis.md) — A third axis, scored over faulted runs.
- [Request Rate and Commit Rate Are Different Safety Numbers](request-vs-commit-safety-readouts.md) — Splits what the model asks for from what the tool commits.
- [Permission Framework Choice Outweighs Model Choice](../security/permission-framework-over-model.md) — The runtime control to pair with this measurement.
