---
title: "Skill Utility Depends on Model and Harness Configuration"
term: "Configuration-Specific Skill Utility"
description: "A skill's pass-rate gain belongs to one model and harness pair. Rerun the paired with-and-without test on your own pair when the task is narrow, high-stakes, or the model is weak."
aliases:
  - skill utility configuration dependence
  - per-configuration skill testing
  - model-harness skill transfer
tags:
  - testing-verification
  - evals
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-09
maturity: emerging
---

# Skill Utility Depends on Model and Harness Configuration

> A skill's downstream utility is its pass-rate gain over no skill, and that gain belongs to one model and harness pair.

Test a skill on your own model and harness when it targets a narrow or high-stakes task, when you run a weaker or non-default model, or when you change either half of the pair. A published gain is an average over many tasks and does not say whether the skill helps on yours.

## What the study found

An empirical study ran 87 SkillsBench tasks with their 232 supplied skills across three models and three harnesses. That gave nine configurations, with three runs per task per condition ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). The authors define utility as the task pass-rate difference between a skill condition and the no-skill condition, "evaluated on the same tasks under the same model–harness configuration" ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

In aggregate the skills helped everywhere: "Benchmark Skills improve the overall pass rate in all nine configurations, with gains of 4.60–19.54 percentage points over No-Skill." ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). The smallest was Qwen on Codex (2.30% to 6.90%), the largest GPT on OpenCode (24.14% to 43.68%).

Per task, the picture differed. The same skills "can yield gains on a task in one configuration and losses in another", and the study shows this on 32 of the 87 tasks (36.78%) ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). The model with the higher no-skill pass rate, GPT, also gained more than Qwen under all three harnesses. Under OpenCode that widened their gap from 10.73 to 19.16 points ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

Treat the 36.78% as a noisy estimate. The authors warn that with three repetitions, task-level pass rates "remain sensitive to execution randomness" ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). SkillsBench, across 18 configurations of the same 87-task benchmark, reports 13 of 87 tasks with negative skill deltas, a different measure from sign flips between configurations ([SkillsBench, arXiv:2602.12670v4](https://arxiv.org/abs/2602.12670v4)).

## Why it works

A skill prescribes a method, and a configuration that cannot carry the method out gets stuck inside it. The study states the finding directly: skill utility "depends on the fit between supplied procedures and the target model–harness configuration's ability to execute and adapt them" ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

The exam-block-sequencing task shows it. DeepSeek on Codex "passes all three No-Skill runs but times out in all three Benchmark-Skill runs" ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). The skills prioritize integer programming, DeepSeek mis-specifies the program and debugs until the timeout, and it does not switch to the heuristic method the task allows. GPT on the same harness hits a solver failure, switches to an allowed heuristic, and passes all three runs ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

The harness adds its own effect. SkillsBench finds that the harness's discovery, prompting, execution, and tool-use loop mediate realized benefit ([SkillsBench, arXiv:2602.12670v4](https://arxiv.org/abs/2602.12670v4)). The 2610 study's mechanism comes from case trajectories, not a controlled ablation.

## The recipe

1. Pin the model and harness version, and name the pair the result applies to.
2. Pick representative tasks that have a deterministic verifier.
3. Run every task at least three times per condition, with and without the skill, in a fresh environment each time.
4. Compare per-task deltas, not only the mean. A task that loses with the skill is a review target.
5. Record the tasks and the configuration. The authors say this "would further help users judge whether reported gains apply to their setting and decide what to retest before deployment" ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

## When this backfires

The test costs compute and engineer time. Under these conditions it buys a number you cannot use:

- No deterministic verifier. On judgement-graded work, a paired run cannot separate a skill effect from variance.
- Too few tasks or runs. On 23 tasks, one task moving from 0 of 3 to 3 of 3 shifts the average by 4.35 points. That equals the low end of the study's operation-support reranking gain (4.35 to 5.80 points), which the authors say needs evaluation on independent tasks ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)). Single-run pass@1 alone swings 2.2 to 6.0 points ([arXiv:2602.07150v3](https://arxiv.org/abs/2602.07150v3)).
- A configuration that changes faster than the test runs. You rerun on every model or harness change, or you carry a result that no longer describes the current pair.
- Work where the average is what counts. All nine aggregate gains were positive, so trusting the published gain would have been right.
- Floor pass rates. At 6.90% with skills, the paired delta rests on a handful of runs.

Vendor guidance agrees on the per-model part: "Test your Skill with all the models you plan to use it with." ([Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## Key Takeaways

- Aggregate gains held in 9 of 9 configurations while individual tasks flipped sign, so a positive average does not predict your task.
- The 36.78% flip rate comes from three-run cells, which the authors say stay sensitive to execution randomness.
- The failure mechanism is a procedure the configuration cannot execute or abandon, as DeepSeek on Codex showed.
- Run the paired test for narrow, high-stakes, weak-model, or changed-configuration cases. Skip it as a ritual.
- Write down the model and harness a result applies to, or the result expires unnoticed.

## Related

- [Skill Evals](skill-evals.md) — the paired with-skill and baseline runner this recipe depends on.
- [Skill Lift: Measuring What a Skill Adds at Runtime](skill-lift.md) — the paired delta and its limits.
- [Skill-Use Gates: Trigger, Compliance and Boundary](skill-use-gate-decomposition.md) — harness differences in trigger and compliance.
- [Skill Over-Trust](../patterns/anti-patterns/skill-over-trust.md) — relevance ranking is a weak proxy for utility.
- [Size Agent Comparisons by Run-to-Run Variance](size-agent-comparisons-by-run-variance.md) — how many runs a small delta needs.
