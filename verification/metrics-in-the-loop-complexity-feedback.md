---
title: "Metrics-in-the-Loop: Complexity Feedback for Coding Agents"
term: "Metrics-in-the-Loop"
description: "A short complexity report injected after each code-changing turn lowered erosion in four models on two benchmarks; no per-model correctness change was detectable."
aliases:
  - MITL
  - in-run complexity feedback
  - complexity feedback loop
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-23
maturity: emerging
---

# Metrics-in-the-Loop: Complexity Feedback for Coding Agents

> A short complexity report after each code-changing turn lowered erosion in agent-written code, and the study found no detectable change in held-out correctness.

Metrics-in-the-loop (MITL) measures the code an agent has just changed and puts a short report into the agent's context before its next turn. The complexity report names changed functions whose cyclomatic complexity exceeds a limit. The coverage report names changed lines that the agent's own tests skip. The agent can then refactor or add tests before it builds on the weak code. The method needs no training, no reference solution and no access to held-out tests ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

## How the loop works

After each turn that changes a file, the study's harness saves a snapshot, measures the changed functions, and appends one message before the next model call ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

- The complexity report lists changed functions with cyclomatic complexity above 6, highest first, and asks the agent to bring them under the limit.
- The coverage report comes from rerunning the agent's own tests. It lists changed functions with added or edited lines that no test executes. The target is zero uncovered changed lines.
- Complexity comes from [lizard](https://github.com/terryyin/lizard) and is cached by file content, so a turn re-parses only the files it changed.

Every arm that received a message got the same feedback instructions: simplify nested control flow, extract named helpers, and keep the tests passing. A reminder arm (R) got those instructions with no measurements. That control separates the effect of the numbers from the effect of being told to tidy up ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

## What the study found

Four models (DeepSeek V4.1 Flash, GLM-5.3 Flash, Claude Haiku 5.5, GPT-6 Luna) ran three long-horizon Python benchmarks: Commit0, SlopCodeBench and SWE-EVO. The headline metric is erosion, the share of complexity mass in functions with cyclomatic complexity above 10 ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

Complexity feedback, alone (C) or with coverage feedback (CT), lowered final erosion against the reminder arm for all four models on Commit0 and SlopCodeBench, with every interval excluding zero. On SWE-EVO every estimate was lower, but only two of four models' intervals excluded zero under project clustering. Values below are erosion under the reminder arm and the paired change for CT.

| Model | Commit0: reminder | Commit0: CT minus R | SlopCodeBench: reminder | SlopCodeBench: CT minus R |
|---|---|---|---|---|
| DeepSeek | 0.251 | -0.070 | 0.430 | -0.433 |
| GLM | 0.231 | -0.096 | 0.530 | -0.504 |
| Haiku | 0.122 | -0.054 | 0.046 | -0.045 |
| Luna | 0.311 | -0.261 | 0.696 | -0.687 |

The paper notes that absolute effects on SlopCodeBench differ fifteenfold across models, yet every model "removes nearly all erosion present under the reminder arm" ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)). Its pooled estimates are post hoc.

Correctness showed no detectable change. Every per-model interval for CT minus R on held-out correctness includes zero. On Commit0 the change runs from -2.3 points (Haiku) to +4.7 (GLM), and the pooled change is +3.1 [-0.1, +6.3]. On SlopCodeBench it runs from -5.8 (Haiku) to 0.0 (GLM), and the pooled change is -1.7 [-3.6, +0.1].

A joint mixed model gives an odds ratio of 0.82 [0.70, 0.96] on SlopCodeBench, so "a small cost of the combined arm on SlopCodeBench cannot be ruled out." Each benchmark also has per-model intervals compatible with losses of 6 percentage points or more ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

Agents act on the report. Under complexity feedback they re-edited 54 to 88% of flagged functions on Commit0 and 87 to 94% on SlopCodeBench, and by the end of the run 46 to 94% and 94 to 97% met the limit. Under the reminder, agents edited 20 to 60% of over-limit functions, and only 1 to 18% ended under the limit. Agents saw at least 98.2% of offered messages ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

## Read the effect with its confounds

- The reminder does part of the work. For Haiku on SlopCodeBench, the reminder alone cut erosion by 0.383 against no message, and complexity feedback cut a further 0.045 ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).
- Coverage feedback alone did not lower erosion. On SlopCodeBench it raised erosion for DeepSeek (+0.067 [+0.030, +0.104]), GLM and Luna against the reminder arm.
- Splitting functions explains part of the drop. After inlining every eligible single-use function in both arms, 3 to 46% of the erosion difference remained on Commit0 and 8 to 18% on SlopCodeBench (DeepSeek, GLM and Luna). The authors say this does not isolate extraction's causal effect. Total branching fell 14 to 21% on SlopCodeBench for those three models, but changed by under 4% for DeepSeek and GLM on Commit0.
- The report bundles several changes. It combines limits and measurements, so target, content and timing effects are confounded. The estimated effects also include a changed message header and a task-prompt paragraph defining each metric.

## What it costs

The paper measured overhead on its DeepSeek and GLM runs ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1)).

- Median message size ran from 1.2 kB (reminder) to 2.1 kB (both reports). Injected feedback was a median 0.4 to 1.1% of processed tokens per cell.
- Coverage needs a full rerun of the agent's test suite after each measured turn. On Commit0 that took a median 0.4 to 0.5 s per turn (0.5 to 0.7% of model time per cell). On SlopCodeBench it took 9.6 to 16.9 s per measured turn, a median 33 to 44% of model time per cell.
- Snapshotting and complexity measurement were not timed.

## When this backfires

- Slow test suites make the coverage half expensive. Agent-written suites can be slow enough that coverage measurement costs a median 33 to 44% of model time, as on SlopCodeBench.
- A correctness cost is not ruled out. The SlopCodeBench mixed-model result above is the evidence.
- The long-term benefit is unproven. The authors expect simpler code to pay off over longer maintenance, but their benchmarks cannot show it. Pass rates are near saturation on SlopCodeBench, and both it and Commit0 are public and subject to contamination.
- The conditions are narrow. The study covers Python, one harness (Oh-My-Pi), four models and one budget per benchmark, with a single complexity limit.

## Applying it

The mechanism needs three parts: a trigger after a code-changing turn, a measurement scoped to changed functions, and a short message appended to the agent's context. The study ran only in the Oh-My-Pi harness, not in Claude Code, so treat the mapping below as untested.

In Claude Code, a `PostToolUse` hook can return `additionalContext`, which is added to the context alongside the tool result. A `PostToolBatch` hook injects its context once before the next model call ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). The study sent one message per code-changing turn, which is closer to the batch event than to a per-edit hook. [PostToolUse hooks for formatting and linting](../tools/claude/posttooluse-auto-formatting.md) covers the per-edit form.

If you add reminder text alongside the numbers, keep a reminder-only baseline. Without one you cannot tell whether the measurements or the instruction moved the code.

## Example

The complexity message the paper reproduces from a Commit0 run, with its closing feedback instructions omitted ([arXiv:2611.23817v1](https://arxiv.org/abs/2611.23817v1), Appendix A.1):

```text
[Measurement, turn 1] Cyclomatic complexity estimates how many independent
execution paths a function contains. Higher complexity usually means the
function is harder to understand, test, and modify safely. The target is 6
or lower for every function.
Functions above the limit, highest first:
src/attr/_make.py:60 attrib cyclomatic complexity 18 (limit 6); new this turn
At or under the limit: 0 functions.
```

## Key Takeaways

- Report only the functions the last turn changed, and name each one with its score and the limit.
- In the study, complexity feedback lowered erosion for all four models on Commit0 and SlopCodeBench, and for two of four on SWE-EVO under project clustering.
- Held-out correctness showed no detectable per-model change, but a small cost on SlopCodeBench is not ruled out.
- Part of the effect comes from the reminder text and from splitting functions, so run a reminder-only control.
- Coverage feedback alone did not lower erosion. Its cost depends on how long the agent's own test suite takes to run.

## Related

- [Diff-Coverage Gating for Agent-Authored Pull Requests](diff-coverage-gate-agent-prs.md) — the merge-time version of the changed-line coverage measure.
- [Over-Compliant Refactoring: Agents That Keep Editing Clean Code](../patterns/anti-patterns/over-compliant-refactoring-loop.md) — why a refactoring request needs a stopping criterion such as a complexity limit.
- [In-Loop Interception](../loop-engineering/in-loop-interception.md) — where custom logic can run between model call and tool call.
- [Pre-Generation Complexity Scoring](pre-generation-complexity-scoring.md) — complexity scored from the prompt instead of the output.
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md) — the per-edit hook that feedback delivery builds on.
