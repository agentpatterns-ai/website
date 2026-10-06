---
title: "What an Agent's Own Token Cost Estimate Is Good For"
term: "Agent Cost Self-Prediction"
description: "Frontier coding agents predict their own token spend at a correlation of 0.39 at best, and low for every model tested, so it ranks rather than budgets."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - agent token self-estimate
  - self-predicted token cost
  - pre-execution cost self-estimate
last_reviewed: 2026-10-05
maturity: emerging
---

# What an Agent's Own Token Cost Estimate Is Good For

> An agent's estimate of its token cost tops out at 0.39 correlation and runs low for every model tested, so it ranks rather than budgets.

Agent cost self-prediction asks the agent that will run a task to estimate the task's token usage first, with its tools available so it can inspect the repository before answering. The study covers eight frontier models and 500 SWE-bench Verified instances. The strongest correlation between predicted and actual token counts was 0.39, for output tokens with Claude Sonnet 4.5. The authors call the correlations "too modest to support precise, instance-level cost estimates" ([Bai et al., arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). The estimate tells you which tasks are expensive. It will not tell you how expensive.

## Use it to rank, never to price

Four conditions decide whether asking is worth the tokens.

The decision has to be coarse. Flagging a run for approval or picking the cheaper of two tasks survives a correlation near 0.4. Putting a number in front of a customer does not.

The overhead has to be small on the model you run. For most models self-prediction costs less than half a task's own spend. Price and quality still move independently. Sonnet 3.7 and Sonnet 4 "spend more than 2× the task cost on prediction and yet do not achieve the strongest correlations" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). GPT-5.2 "drops prediction overhead below 6% while still hitting moderate correlations" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). Measure that ratio on your own model first.

You have to have nothing better. Given a measured history of similar tasks, [probe-run calibration](probe-run-cost-calibration.md) cuts median prediction error from 161% to 36% ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)), and a hard cap from a pricing table enforces a budget the way an estimate never can. Self-prediction earns its place on a workload you have never run.

Correct the direction before you act. The error is biased rather than scattered: "Models consistently underestimate the tokens they need: most points fall below the diagonal for every model we tested. The bias is especially pronounced for input tokens, whose predictions stay compressed even as real values grow into the millions" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). Treat any self-estimate as a floor.

## Why it works

Input tokens drive agentic coding cost, and at estimation time the agent cannot see what will produce them. Every round carries "the full conversation history, including all previous prompts and completions" forward unchanged, so each file the agent opens is re-billed on every later call. In every phase of a Sonnet 4.5 trajectory, cache reads are "the largest category by a wide margin" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). How many files get opened depends on tool output that does not exist yet. That is why input is the harder half to predict, "reflecting the uncertainty introduced by context construction, retrieval, and tool-driven exploration" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)).

A separate benchmark agrees. BAGEN finds that "all models are optimistically biased", and task success predicts interval hit rate at only r≈0.35. It still calls the signal actionable, because early stopping "saves between 28% and 64% of tokens on failed trajectories" at a cost of 1.6 to 4.2 points of success rate ([arXiv:2606.00198v1](https://arxiv.org/abs/2606.00198v1)).

## When this backfires

- The task is interactive. Self-prediction "carries non-trivial latency and overhead of its own, especially for models that explore extensively before committing to a number" ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)), which the authors call hard to justify in time-sensitive settings.
- An external forecaster is available. TokenCast refreshes a cumulative forecast as the run unfolds with no extra model calls, at 32.8 ms per run, and uses "21.3% fewer tokens on average than a fixed-budget policy at matched trace completion" ([arXiv:2609.35760v2](https://arxiv.org/abs/2609.35760v2)).
- You size by how hard the task looks. Human difficulty ratings track token spend at Kendall tau_b = 0.32, and 6.7% of tasks rated under 15 minutes cost more than the average task rated over an hour ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)).
- You carry the cost breakdown across price schedules. Cache reads dominate dollars here, for one model, at the 5-minute cache-write rate. A study of Kimi K3 found that "output tokens are 2.7% of tokens processed but 51.1% of dollars at a 96.3% cache hit rate" ([arXiv:2608.25399v1](https://arxiv.org/abs/2608.25399v1)). Which side carries the bill depends on your pricing.
- You plan around the 30x headline. Runs of one task differ by up to 30x in the tail, while the per-model average ratio of the most to the least expensive run is about 2x ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). Budget against the tail and you over-provision every ordinary run.
- You generalize past the setup. Eight models, one agent framework, one benchmark, which the authors call "a broad sample by the standards of existing work, but still only a slice of the agentic model landscape".

## Example

A queue of agent jobs with no cost history has three usable gates.

1. Ask the agent, before dispatch, to break the job into stages and estimate input tokens, output tokens, and total cost separately. That is the prompt shape the study benchmarked ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)). Record the estimate and its overhead.
2. Rank the queue by estimate and hold the top decile for approval. This is the decision a 0.39 correlation supports.
3. Multiply the estimate by your observed underestimation factor and set that product as a cap. The cap stops the run; the estimate only decides where to put it.

After about a dozen completed jobs (a rule of thumb from this page, not a figure from the paper) you have the measured history probe-run calibration needs, and step 1 becomes redundant.

## Key Takeaways

- Rank with the estimate and cap with something else. A ceiling of 0.39 Pearson correlation separates expensive tasks from cheap ones and prices neither ([arXiv:2604.22750v3](https://arxiv.org/abs/2604.22750v3)).
- The error has a known direction, so every self-estimate is a floor to scale up.
- Check the overhead before wiring the question in. It runs from under 6% of the task to over 200%, and the expensive end is not the accurate end.
- Input tokens carry agentic coding cost, and input is the half the agent predicts worst.
- Once a dozen comparable tasks are measured, switch to calibration or a hard cap and stop asking.

## Related

- [Probe-Run Calibration for Predicting Agent Token Spend](probe-run-cost-calibration.md) — the measured alternative, once there is a history to calibrate against
- [Per-Run Budget Reservation for Coding Agent Model Calls](../patterns/agent-design/per-run-budget-reservation.md) — the hard cap that enforces a budget an estimate cannot
- [The Four Terms That Decide What an Agent Task Costs](four-term-agent-cost-model.md) — reading a finished bill back to its cause, which is what the estimate is guessing at
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the instrument-attribute-fix-verify loop that builds the history
- [Programming Language Choice as a Token-Cost Lever](language-choice-token-cost.md) — the same study's variance findings applied to a different decision
