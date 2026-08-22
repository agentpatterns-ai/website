---
title: "Multi-Run, Shuffled-Order Evaluation for Self-Improving Agents"
term: "Shuffled-Order Evaluation"
description: "Memory-based agents that learn across a task stream need several runs and randomized task orders before a reported gain means anything, because the loop amplifies variance and the default order hides a curriculum."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - shuffled task order evaluation
  - multi-run agent evaluation protocol
  - task-order stress testing for agent memory
last_reviewed: 2026-08-19
maturity: emerging
---

# Multi-Run, Shuffled-Order Evaluation for Self-Improving Agents

> A self-improving agent's reported gain is only believable after several runs under shuffled task orders, with the spread reported next to the mean.

## When this applies

The protocol has purchase under one condition: the agent writes something back between tasks and reads it on later tasks. Textual memory banks, distilled workflow libraries, and any harness that appends to an instruction file mid-stream all qualify. A stateless agent that starts each task from a fixed prompt cannot be affected by task order, and the extra runs buy nothing there beyond the sampling spread that [seed-variance reporting](seed-variance-reporting.md) already covers.

Two further conditions decide whether it is worth the budget: the effect under test is small enough that noise could explain it, and the suite is large enough for a spread to mean something. Ye et al. report that "when using GPT-5-mini as the backbone model, a single run over all 812 WebArena tasks costs around $25", an estimate they base on the no-memory baselines, with memory-based methods adding extra cost the authors expect to be minimal ([2026](https://arxiv.org/abs/2608.18066v1)). On that backbone and that baseline, three runs under each of three orders is near $225 of compute before any variants — a floor, not a budget.

## The protocol

1. Run the full suite at least three times under the default order and record each run separately. Ye et al. used three identical runs per configuration.
2. Report the best-worst gap alongside the mean, for the baseline and the memory-equipped agent both. The comparison that matters is whether the loop widened the gap.
3. Re-run the suite under at least one random shuffle of the task order, with the same number of repeats.
4. Apply a significance test to the mean difference and publish the result even when it is unflattering. The headline gain in the re-evaluation was 1.5% over baseline at p=0.23 by unpaired t-test over three runs ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)).
5. Treat any sign change between the default and shuffled conditions as the finding, not as an outlier to be explained away.

Step 5 is where the re-evaluation landed. That same 1.5% gain under WebArena's shipped order became a 4.5% degradation once the task order was randomized ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)).

## Why it works

A memory bank turns an evaluation into a feedback loop rather than a set of independent trials. Each task's outcome is distilled into memory that conditions every later task, so an early deviation propagates into what the agent retrieves next instead of averaging out. Ye et al. observed the consequence directly: "In 17 of the 24 cases, we see an increase in variances", and "in 11 cases the relative increase exceeds 50%" ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)). A mechanism that stabilized behavior would move that number the other way.

Task order acts through the same channel in a different direction, because the order decides what enters memory first. The authors identify "environment and task underspecification during memory generation as potential drivers" of the variance, with memory entries recommending API calls that the browser environment cannot execute ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)). Seeded with easy successes, memory accumulates executable patterns; seeded with hard failures, it accumulates plausible strategies that misdirect everything downstream.

Benchmark task IDs are not neutral here. The default ordering "may be an artifact of the benchmark construction process, whereby annotators begin with simpler tasks and progressively introduce more challenging ones", and the moving-average pass curves for the no-memory baseline agent "begin with high pass rates (around 75%), which subsequently decline to below 40% once the task ID exceeds 150" ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)).

## When this backfires

- The agent carries no state across tasks. Shuffling a stateless suite measures the same distribution twice at triple the cost. Reach for [pass@k and pass^k](pass-at-k-metrics.md) instead.
- Production order is genuinely fixed and easy-to-hard. Onboarding streams and staged migrations really do escalate, and curriculum ordering is a documented lever in RL post-training rather than only a measurement artifact: an easy-to-hard curriculum "significantly improves the reasoning ability of small LLMs (1.5B to 3B), which otherwise struggle when trained with vanilla RL alone" ([Parashar et al., 2025](https://arxiv.org/abs/2506.06632v3)). Shuffling then reports a number for a stream you will never serve.
- The suite is small and the budget is thin. Three runs across several orders on a 50-task suite widens the error bar without resolving anything. A reproducibility study of reasoning benchmarks finds that "Bootstrapping over 30 runs substantially stabilizes Pass@1 estimates and should be considered a minimal standard for reliable evaluation" ([Hochlehnert et al., 2025](https://arxiv.org/abs/2504.07086v2)), which also bounds what three runs establish in the re-evaluation itself.
- The effect is already obvious. A change that moves success by 20 points needs no significance test; this protocol earns its cost in the one-to-three-point band where p=0.23 lives.

Fixing the underlying fragility is harder than detecting it. Adding evaluation rubrics, environment feedback, and a prompt that discourages unsupported actions recovered part of the shuffled-order loss, "a 2.9% improvement over the original RBank method (49.8% → 52.7%)", still short of the 54.8% baseline ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)).

## Example

WebArena's GitLab domain shows the reportable shape. Across three baseline runs the best and worst differed by 4.4%; with ReasoningBank attached the gap widened to 7.8% ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)). A single-run report shows one number from inside that band and credits its position to the memory bank.

Under the protocol the same comparison reads: baseline 54.8% mean over three WebArena runs; memory-equipped 1.5% higher at p=0.23; variance widened in 17 of 24 cases; 49.8% under one random shuffle ([Ye et al., 2026](https://arxiv.org/abs/2608.18066v1)). That supports a decision. The 1.5% headline does not.

## Key Takeaways

- Run at least three repeats and one shuffled task order before accepting that a memory-based agent improved.
- Report the best-worst gap next to the mean; a self-improvement loop that widens the gap has bought instability along with any gain.
- A sign change between the default and shuffled orders means the benchmark's ordering was doing the work.
- Skip the protocol entirely when no state crosses task boundaries, and check the per-run cost before committing to a multi-order design.

## Related

- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — the same discipline on the sampling axis, for results that do not accumulate state.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — where orchestration-state variance sits relative to token sampling.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — the metric pair for stateless suites.
- [Weakest Consistent Learning: What Agent Loops Should Persist](../patterns/agent-design/weakest-consistent-learning.md) — what to write into memory once the loop is measurable.
- [Agentic Flywheel: Self-Improving Agent Systems](../patterns/agent-design/agentic-flywheel.md) — the loop shape this protocol is meant to keep honest.
