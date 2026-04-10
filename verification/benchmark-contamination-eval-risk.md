---
title: "Benchmark Contamination as Eval Risk"
description: "Static benchmarks inflate model scores as training data overlaps with test sets — decontaminated evaluation pipelines use temporal filtering and continuous fresh task sourcing to restore honest measurement."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - decontaminated evaluation
  - benchmark data leakage
---

# Benchmark Contamination as Eval Risk

> Static benchmarks become unreliable as models train on their data. Decontaminated pipelines use temporal filtering and continuous fresh task sourcing to measure real capability.

## The Contamination Problem

Models trained on large internet corpora inevitably encounter benchmark data. When a model has seen the test set during training, its benchmark score reflects memorization, not generalization.

SWE-rebench quantified this for coding agents: DeepSeek-V3 scores 39.7% on SWE-bench Verified but only 21.3% on decontaminated fresh tasks — an 18.4 percentage point gap attributable to contamination. GPT-4.1 shows a similar pattern: 31.1% on older tasks versus 26.7% on newer ones. [Source: [SWE-rebench](https://arxiv.org/abs/2505.20411)]

The problem extends beyond SWE-bench. LessLeak-Bench audited 83 software engineering benchmarks and found leakage ratios ranging from under 1% to 100%. StarCoder-7b achieved Pass@1 4.9x higher on leaked samples than on non-leaked samples in the APPS benchmark. [Source: [LessLeak-Bench](https://arxiv.org/abs/2502.06215)]

Teams that rely on published benchmark scores for model upgrade decisions risk selecting models that memorized the test set over models that generalize better to real-world tasks.

## Decontamination Mechanisms

Three mechanisms restore honest measurement:

### Temporal Filtering

Track the creation date of every eval task (the issue, the PR, the test) against the model's training data cutoff. Tasks created after the cutoff cannot appear in training data. SWE-rebench explicitly flags evaluations where tasks predate a model's release date, marking them as potentially contaminated on the leaderboard. [Source: [SWE-rebench leaderboard methodology](https://swe-rebench.com/about)]

### Continuous Fresh Task Sourcing

Rather than curating a fixed benchmark once, extract tasks continuously from recent real-world activity. SWE-rebench mines merged PRs linked to resolved GitHub issues, yielding 21,336 tasks from 3,468 repositories. The pipeline runs four stages: repository filtering, LLM-driven environment setup, execution validation in isolated containers, and quality assessment. [Source: [SWE-rebench](https://arxiv.org/abs/2505.20411)]

The same principle applies at team scale: periodically add eval tasks sourced from recent internal work to keep your suite ahead of potential contamination.

### Standardized Scaffolding

Contamination is not the only confounding variable. Differences in prompts, tools, and test-time computation inflate or deflate scores independently of model capability. SWE-rebench isolates model quality by fixing the scaffolding: identical ReAct-style prompts, 128K context window, default hyperparameters, and five runs per model with standard error reported. [Source: [SWE-rebench leaderboard methodology](https://swe-rebench.com/about)]

## Team-Level Defenses

You do not need to build a 21,000-task pipeline. Three practices protect against contamination at team scale:

1. **Maintain a private eval suite.** Tasks drawn from your own codebase and real production incidents are unlikely to appear in any model's training data. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

2. **Refresh continuously.** Add eval tasks from recent work — last month's merged PRs, last week's incidents. Tasks that postdate the model's training cutoff are inherently decontaminated.

3. **Treat public benchmarks as upper bounds.** Use them for directional comparison, not absolute measurement. When two models score within a few points of each other on a public benchmark, the difference may be contamination rather than capability.

## Example

SWE-rebench's own leaderboard demonstrates the pattern. DeepSeek-V3 leads on SWE-bench Verified at 39.7%, but drops to 21.3% on decontaminated tasks — a gap nearly as large as its reported score. Meanwhile, models with lower Verified scores show smaller drops, suggesting their original scores were less inflated by contamination. [Source: [SWE-rebench](https://arxiv.org/abs/2505.20411)]

A team using SWE-bench Verified scores alone to choose between models would rank DeepSeek-V3 highest. A team running the same models against fresh, post-cutoff tasks drawn from their own repositories would get a different ranking — one that reflects generalization to the work the team actually needs done.

## Key Takeaways

- Static benchmarks inflate scores as models train on their data — the measured gap can exceed 18 percentage points
- Temporal filtering (using only post-cutoff tasks) is the primary decontamination mechanism
- Continuous fresh task sourcing from real-world activity prevents benchmark stagnation
- Private eval suites sourced from your own codebase provide inherent contamination resistance
- Treat published benchmark scores as upper bounds, not ground truth, when making model selection decisions

## Related

- [Hardening Evals for Production](../training/eval-driven-development/hardening-evals.md) — benchmark contamination defenses within a broader hardening framework
- [The Eval-First Development Loop](../training/eval-driven-development/eval-first-loop.md) — model upgrade testing with eval suites
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — using realistic benchmarks for tool evaluation
- [Golden Query Pairs as Regression Tests](golden-query-pairs-regression.md) — private regression suites as contamination-resistant measurement
- [Incident-to-Eval Synthesis](incident-to-eval-synthesis.md) — converting production incidents into fresh eval tasks
