---
title: "Agent Time Estimates Are Not Schedules"
description: "A coding agent's duration estimate reproduces the human timeline in its training data. Use it to rank scope, bound the run with turn and tool-call caps, and measure wall-clock on comparable past runs instead."
aliases:
  - "coding agent time estimate"
  - "agent duration estimate"
tags:
  - human-factors
  - claude
last_reviewed: 2026-08-29
maturity: emerging
status: current
---

# Agent Time Estimates Are Not Schedules

> Agent duration estimates reproduce the human timeline in the training data, so read them as a scope signal and bound the run separately.

Ask Claude Code how long a task will take and you get generated text, not a measurement. The model holds no clock, no record of its last comparable run, and no advance count of the tool calls the work needs. Eivind Kjosbakken puts the cause in the training distribution: "Claude has essentially been trained on human estimates of time" ([Kjosbakken, 2026-08-28](https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/)). His worked case is a feature Claude scoped at "3-4 weeks of work" for a single engineer that "will typically be done within a single day, especially if you set up Claude in the correct way."

Note the direction. The one practitioner report describes over-estimation by roughly an order of magnitude, because the model returns the human reference class for work an agent will execute. Teams brace for the overrun; the documented failure is the idle window.

## What the estimate is good for

The number carries weak ranking signal. Across 16 software projects, zero-shot LLM story-point predictions beat supervised models trained on 80% of the same projects' history ([Shetty et al., arXiv 2603.06276v2](https://arxiv.org/abs/2603.06276v2)). DeepSeek reached an average Pearson correlation of 0.3816 against a 0.3175 supervised baseline, and Kimi a rank correlation of 0.4111 against 0.3133. Correlations in that band order tasks by relative effort. They do not commit a calendar.

Compare it across tasks to decide what to hand the agent first, and read it as a report on how the agent scoped the work. When the number surprises you, the disagreement is about scope, not speed.

## Why it works

Two causes stack, and they fail differently. The first is calibration: the estimate is text conditioned on a task description, fit to a distribution of human timelines ([Kjosbakken, 2026-08-28](https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/)). That part is fixable with grounding: five scale-aware examples from the same project raised DeepSeek's average correlation from 0.3816 to 0.4532 ([Shetty et al., arXiv 2603.06276v2](https://arxiv.org/abs/2603.06276v2)).

The second is not fixable by calibration at all. Toby Ord fits agent performance on METR's task suite with "a constant rate of failing during each minute a human would take to do the task" ([Ord, arXiv 2505.05115v1](https://arxiv.org/abs/2505.05115v1)). That produces a success rate declining exponentially with task length, and gives each agent a characteristic half-life. A run either converges or spends its remaining time in a retry tail. That is why METR reports capability as a 50%-task-completion time horizon, the time humans take on tasks the model completes with 50% success, not an expected duration ([Kwa et al., arXiv 2503.14499v4](https://arxiv.org/abs/2503.14499v4)). A point estimate is the wrong object for a heavy-tailed outcome no matter who produces it.

Bounding sidesteps the problem it cannot solve. A turn cap, a tool-call cap, and a mid-run checkpoint need only that the tail exists, never how long it is.

## What to measure instead

- Wall-clock on comparable past runs. Claude Code exports `claude_code.active_time.total` in seconds, incremented during user interaction and during CLI processing such as tool execution, with a `type` attribute of `user` or `cli` ([Anthropic](https://code.claude.com/docs/en/monitoring-usage)).
- Turn and tool-call budgets rather than minutes. See [loop budgeting](../loop-engineering/loop-budgeting.md) for allocating them across turns.
- Checkpoints that report progress mid-run, so an overrun is visible before the window closes.
- Past durations for comparable tasks, held in a skill file the agent reads. Kjosbakken proposes exactly this: "make your coding agent store data on how long something takes to implement" ([Kjosbakken, 2026-08-28](https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/)). The five-example effect size above was measured on story points, not run durations, so treat the transfer as untested.

## When this backfires

- One wall-clock cap over a heterogeneous task mix. A timeout sized for a lint fix kills a dependency migration mid-edit, and the partial state costs more than the overrun.
- No reference class. Greenfield work, a first run against an unfamiliar repository, or a new model version has no comparable history, so measuring past runs has nothing to read.
- Budgets count work, not progress. A run that burns its whole allocation on retries is indistinguishable from a productive one in `claude_code.active_time.total`, which "is incremented during user interactions, such as typing and reading responses, and during CLI processing, such as tool execution and AI response generation" ([Anthropic](https://code.claude.com/docs/en/monitoring-usage)). No term in that definition refers to whether the work succeeded.
- Small samples sit inside the variance. The constant-hazard model gives a wide spread ([Ord, arXiv 2505.05115v1](https://arxiv.org/abs/2505.05115v1)), so a handful of runs per month cannot separate a trend from noise.
- Substituting human intuition. In METR's randomized controlled trial, 16 experienced developers forecast AI would cut completion time by 24%; the measured effect was a 19% increase ([Becker et al., arXiv 2507.09089v2](https://arxiv.org/abs/2507.09089v2)). Swapping the agent's number for the team's gut swaps one miscalibrated forecast for another.

## Example

**Before** — the estimate read as a schedule, from Kjosbakken's reported case:

```text
Claude, scoping a feature:  "For a single engineer, this might be
                             3-4 weeks of work."
What happened:              "will typically be done within a single day,
                             especially if you set up Claude in the
                             correct way."
```

**After** — the same run bounded and instrumented, using documented Claude Code surfaces:

```text
claude -p --max-turns 40 "<task>"
   # --max-turns: "Limit the number of agentic turns (print mode only).
   #  Exits with an error when the limit is reached."

# Read the run's cost afterward, not before it:
claude_code.active_time.total{type="cli"}   # seconds, exported over OTel
```

The turn cap holds whether the true duration is a day or three weeks, which is the point: it needs no forecast ([Anthropic, CLI reference](https://code.claude.com/docs/en/cli-reference)). The estimate still contributed. It said the feature was larger than a rename, which is why the cap is 40 turns and not 10.

## Key Takeaways

- The estimate has no clock behind it. It reproduces the human timeline in the training data, and the documented error is over-estimation, not the underrun teams brace for ([Kjosbakken, 2026-08-28](https://towardsdatascience.com/why-claude-code-time-estimates-are-poor/)).
- Correlations of roughly 0.38 to 0.45 mean the number ranks relative effort; it does not commit a calendar ([Shetty et al., arXiv 2603.06276v2](https://arxiv.org/abs/2603.06276v2)).
- Grounding has a measurement behind it; prompting does not. Five project-specific examples lifted correlation from 0.3816 to 0.4532 ([Shetty et al., arXiv 2603.06276v2](https://arxiv.org/abs/2603.06276v2)). Kjosbakken's other suggestion, telling the model to estimate for an LLM rather than a human, is offered without one.
- Bound rather than predict. `--max-turns` and a mid-run checkpoint need only that a retry tail exists, not its length ([Anthropic, CLI reference](https://code.claude.com/docs/en/cli-reference)).
- Do not swap in human intuition as the fix. METR's developers forecast 24% faster and measured 19% slower ([Becker et al., arXiv 2507.09089v2](https://arxiv.org/abs/2507.09089v2)).
- A few runs a month sits inside the spread the constant-hazard model implies ([Ord, arXiv 2505.05115v1](https://arxiv.org/abs/2505.05115v1)). Keep the caps and skip the dashboard until the sample supports it.

## Related

- [Human-Equivalent Hours for Autonomous Coding Agent Productivity](human-equivalent-hours-agent-productivity.md) — the backward-looking counterpart: estimating human hours for output already produced, rather than duration for work not yet started
- [The Productivity-Experience Paradox in AI-Assisted Development](productivity-experience-paradox.md) — why the human forecast that replaces the agent's is also miscalibrated
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](../loop-engineering/loop-budgeting.md) — how to size the turn and tool-call caps this page recommends
- [Agent Loop Go/No-Go: When Looping Earns Its Cost](../loop-engineering/agent-loop-go-no-go-gate.md) — the decision that comes before the budget
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md) — the checkpoint trail that makes a mid-run overrun visible
