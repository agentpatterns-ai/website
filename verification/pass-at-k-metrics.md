---
title: "pass@k and pass^k: Capability and Consistency Metrics"
description: "Use pass@k and pass^k together: pass@k shows if an agent can solve a problem at all; pass^k shows if it reliably does. A single pass rate conflates the two."
tags:
  - testing-verification
  - evals
  - cost-performance
aliases:
  - "pass at k"
  - "pass power k"
  - "pass@1 pass@k metrics"
---

# Use pass@k and pass^k to Separate Agent Capability from Consistency

> A single pass rate conflates two distinct properties of a non-deterministic agent: whether it *can* solve the problem and whether it *reliably* does. Use pass@k and pass^k together to measure both.

## The Problem with a Single Pass Rate

AI agents are non-deterministic: the same prompt and environment can produce different results across runs. A single pass/fail tells you what happened once, not what to expect across your workflow.

A single pass rate also treats an agent that always scores 6/10 identically to one that randomly scores 0/10 or 10/10. The two have very different production behaviour, and one number cannot distinguish them.

## The Two Metrics

**pass@k** — the probability the agent produces at least one correct solution across *k* attempts. As *k* increases, pass@k rises. It measures the capability ceiling: given enough chances, can the agent ever get this right?

**pass^k** — the probability *all k* attempts succeed. As *k* increases, pass^k falls. It measures consistency: can you trust the agent to get it right every time in production?

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## What the Combination Reveals

| pass@k | pass^k | Interpretation |
|--------|--------|----------------|
| High | High | Capable and consistent. Production-ready for this task class. |
| High | Low | Capable but flaky. Human review required; not safe for automation. |
| Low | — | Cannot reliably solve this class of problem at all. |

An agent with high pass@k and low pass^k signals a specific failure mode: it occasionally hits the right answer but cannot be trusted to do so every time. This is the pattern of an agent that is benchmarking well but failing in production.

## Choosing the Right Primary Metric

**Human-in-the-loop workflows**: pass@k is the relevant metric. If a developer reviews every output, one correct answer in three attempts is often enough — the agent's job is to surface a good option.

**Automated pipelines**: pass^k is critical. If output is consumed directly — merging code, sending messages, modifying databases — you need consistency across all attempts. A 90% pass rate still means roughly 1-in-10 runs fails.

## How to Run the Measurement

1. Define the task and a deterministic correctness check (test suite pass, schema validation, expected output)
2. Run the agent on the same task *k* times (typically k=3–10 depending on cost tolerance)
3. Compute pass@k: did any run succeed?
4. Compute pass^k: did all runs succeed?
5. Aggregate across the task suite to get rates

Report both numbers. A benchmark that reports only pass@1 hides the consistency story; one that reports only pass^1 treats a single data point as if it were stable.

## Practical Guidance

Run at least k=3 for any task that matters — single-trial evaluation is a sample of size one.

Use pass^k to set deployment thresholds. If your automated pipeline cannot tolerate a failure rate above 5%, require pass^k ≥ 0.95 before promoting a model or prompt change.

Use pass@k during development to separate capability gaps from consistency gaps. If pass@k is low, the agent cannot solve the problem. If pass@k is high but pass^k is low, address consistency with better instructions, lower temperature, or added verification steps — not retraining.

## When This Backfires

Both metrics have failure modes worth weighing before treating them as headline results.

- **pass@k is "exponentially forgiving" at larger k.** As *k* grows, almost any non-zero-capability agent eventually hits the right answer, so pass@k can rank a lucky agent above a more reliable one — users rarely judge a tool by its best of ten attempts [Source: [Brooker, *Pass@k is Mostly Bunk*](https://brooker.co.za/blog/2026/01/21/pass-k.html)].
- **Small-suite, small-k estimates are statistically unstable.** With a handful of tasks and *k*=3, both metrics have wide confidence intervals that most reports omit; Bayesian posterior estimates give more honest uncertainty [Source: [Hariri et al., *Don't Pass@k: A Bayesian Framework for LLM Evaluation*](https://arxiv.org/abs/2510.04265)].
- **pass^k is dominated by the flakiest test.** A single noisy oracle — a timing-race integration test, an LLM-as-judge with temperature > 0 — can collapse pass^k even when the agent is correct. Verify the check is itself deterministic before using pass^k as a deployment gate.
- **pass@k assumes independent attempts.** If your harness shares context, seeds, or cached state across the *k* runs, samples are correlated and the metric no longer measures what its definition claims.

When these conditions apply, pair the point estimates with posterior intervals rather than reporting them alone.

## Example

An agent is evaluated on a suite of 5 code-generation tasks. Each task is run k=3 times and the output is checked by running the project's test suite. Results:

```
Task                          Run 1   Run 2   Run 3   pass@3  pass^3
──────────────────────────────────────────────────────────────────────
Add null check to parser       PASS    PASS    PASS     1.0     1.0
Refactor auth middleware        PASS    FAIL    PASS     1.0     0.0
Generate OpenAPI schema stub    FAIL    PASS    FAIL     1.0     0.0
Fix off-by-one in paginator     FAIL    FAIL    FAIL     0.0     0.0
Add rate-limit header           PASS    PASS    PASS     1.0     1.0
──────────────────────────────────────────────────────────────────────
Suite average                                           0.8     0.4
```

The suite pass@3 is 0.8 — the agent can produce at least one correct solution for 4 out of 5 tasks. The suite pass^3 is 0.4 — it is fully consistent on only 2 of 5 tasks.

Reading the combination:

- **"Add null check"** and **"Add rate-limit header"**: pass@3 = 1.0, pass^3 = 1.0. Production-safe for automation; no human review required.
- **"Refactor auth middleware"** and **"Generate OpenAPI schema stub"**: pass@3 = 1.0, pass^3 = 0.0. The agent can produce a correct answer but does not reliably do so. These tasks are appropriate for human-in-the-loop workflows only — flag them for review rather than auto-merging.
- **"Fix off-by-one in paginator"**: pass@3 = 0.0. The agent cannot solve this class of problem at all. It is a capability gap, not a consistency gap — address it with better task decomposition or additional context, not lower temperature.

To compute these numbers in Python from a results matrix:

```python
import numpy as np

# results[i][j] = 1 if task i, run j passed
results = np.array([
    [1, 1, 1],  # Add null check
    [1, 0, 1],  # Refactor auth middleware
    [0, 1, 0],  # Generate OpenAPI schema stub
    [0, 0, 0],  # Fix off-by-one
    [1, 1, 1],  # Add rate-limit header
])

pass_at_k = (results.sum(axis=1) >= 1).mean()   # 0.8
pass_pow_k = (results.sum(axis=1) == 3).mean()  # 0.4

print(f"pass@3: {pass_at_k:.2f}")   # pass@3: 0.80
print(f"pass^3: {pass_pow_k:.2f}")  # pass^3: 0.40
```

## Key Takeaways

- pass@k (at least one success) measures capability; pass^k (all successes) measures consistency
- High pass@k with low pass^k means the agent is flaky — capable but not production-safe for automation
- For human-review workflows, optimize for pass@k; for automated pipelines, optimize for pass^k
- Single-trial evaluation is a sample of size one — run multiple trials and report both metrics

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Golden Query Pairs as Regression Tests](golden-query-pairs-regression.md)
- [Behavioral Testing for Non-Deterministic AI Agents](behavioral-testing-agents.md) — Design tests that account for agent non-determinism across multiple trials
- [PASS@(k,T): Evaluate RL for Agents Along Sampling and Interaction Depth](pass-at-k-t-agentic-rl-eval.md) — Extends pass@k by also varying interaction depth *T* for tool-use agents
- [LLM-as-Judge Context Test Harness](llm-context-test-harness.md)
- [LLM-as-Judge Evaluation with Human Spot-Checking](../workflows/llm-as-judge-evaluation.md)
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md)
