---
title: "pass@k and pass^k: Capability and Consistency Metrics"
term: "pass@k and pass^k"
description: "Use pass@k and pass^k together: pass@k shows if an agent can solve a problem at all; pass^k shows if it reliably does. A single pass rate conflates the two."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - "pass at k"
  - "pass power k"
  - "pass@1 pass@k metrics"
last_reviewed: 2026-06-12
maturity: established
---

# pass@k and pass^k: Capability and Consistency Metrics

> A single pass rate conflates two agent properties: whether it *can* solve a problem and whether it *reliably* does. pass@k and pass^k separate them.

## The problem with a single pass rate

AI agents are non-deterministic: the same prompt and environment can produce different results across runs. A single pass or fail tells you what happened once, not what to expect across your workflow.

A single pass rate also treats an agent that always scores 6/10 the same as one that randomly scores 0/10 or 10/10. The two behave very differently in production, and one number cannot tell them apart.

## The two metrics

pass@k is the probability the agent produces at least one correct solution across k attempts [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]. As k increases, pass@k rises. It measures the capability ceiling: given enough chances, can the agent ever get this right?

pass^k is the probability all k attempts succeed [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]. As k increases, pass^k falls. It measures consistency: can you trust the agent to get it right every time in production?

## What the combination reveals

| pass@k | pass^k | Interpretation |
|--------|--------|----------------|
| High | High | Capable and consistent. Production-ready for this task class. |
| High | Low | Capable but flaky. [Human review required](../workflows/human-in-the-loop.md); not safe for automation. |
| Low | — | Cannot reliably solve this class of problem at all. |

An agent with high pass@k and low pass^k signals a specific failure mode: it occasionally hits the right answer but cannot be trusted to do so every time. This is the pattern of an agent that benchmarks well but fails in production.

## Choosing the right primary metric

In [human-in-the-loop](../workflows/human-in-the-loop.md) workflows, pass@k is the relevant metric. If a developer reviews every output, one correct answer in three attempts is often enough. The agent's job is to surface a good option.

In automated pipelines, pass^k is the relevant metric. If output is consumed directly (merging code, sending messages, modifying databases), you need consistency across all attempts. A 90% pass rate still means roughly 1 in 10 runs fails.

## How to run the measurement

1. Define the task and a deterministic correctness check (test suite pass, schema validation, expected output).
2. Run the agent on the same task k times, typically 3 to 10 depending on cost tolerance.
3. Compute pass@k: did any run succeed?
4. Compute pass^k: did all runs succeed?
5. Aggregate across the task suite to get rates.

Report both numbers. A benchmark that reports only pass@1 hides the consistency story. One that reports only pass^1 treats a single data point as if it were stable.

## Practical guidance

Run at least k=3 for any task that matters — single-trial evaluation is a sample of size one.

Use pass^k to set deployment thresholds. If your automated pipeline cannot tolerate a failure rate above 5%, require pass^k ≥ 0.95 before promoting a model or prompt change.

Use pass@k during development to separate capability gaps from consistency gaps. If pass@k is low, the agent cannot solve the problem. If pass@k is high but pass^k is low, address consistency with better instructions, lower temperature, or added verification steps — not retraining.

## When this backfires

Both metrics have failure modes worth weighing before you treat them as headline results.

- pass@k is "exponentially forgiving" at larger k. As k grows, almost any non-zero-capability agent eventually hits the right answer, so pass@k can rank a lucky agent above a more reliable one. Users rarely judge a tool by its best of ten attempts [Source: [Brooker, *Pass@k is Mostly Bunk*](https://brooker.co.za/blog/2026/01/21/pass-k.html)].
- Small-suite, small-k estimates are statistically unstable. With a handful of tasks and k=3, both metrics have wide confidence intervals that most reports omit. Bayesian posterior estimates give more honest uncertainty [Source: [Hariri et al., *Don't Pass@k: A Bayesian Framework for LLM Evaluation*](https://arxiv.org/abs/2510.04265)].
- pass^k is dominated by the flakiest test. A single noisy oracle (a timing-race integration test, an LLM-as-judge with temperature above 0) can collapse pass^k even when the agent is correct. Check the oracle is deterministic before you use pass^k as a deployment gate.
- pass@k assumes independent attempts. If your harness shares context, seeds, or cached state across the k runs, the samples are correlated and the metric no longer measures what its definition claims.

When these conditions apply, pair the point estimates with posterior intervals rather than reporting them alone.

## Example

An agent runs against a suite of 5 code-generation tasks. Each task runs k=3 times, and the project's test suite checks each output. Results:

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

- "Add null check" and "Add rate-limit header": pass@3 = 1.0, pass^3 = 1.0. Safe to automate; no human review required.
- "Refactor auth middleware" and "Generate OpenAPI schema stub": pass@3 = 1.0, pass^3 = 0.0. The agent can produce a correct answer but does not reliably do so. Send these tasks through human-in-the-loop workflows only, and flag them for review, not auto-merging.
- "Fix off-by-one in paginator": pass@3 = 0.0. The agent cannot solve this class of problem at all. This is a capability gap, not a consistency gap, so address it with better task decomposition or more context, not lower temperature.

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
- [Markov-Chain Reliability for LLM Agents](markov-chain-agent-reliability.md) — Treats pass@k and pass^k as projections of one underlying success first-passage distribution
- [Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)](sampling-state-agent-variability-layers.md) — Pass@k/pass^k summarises the aggregate spread; this technique attributes the spread to the layer that should be mitigated
- [LLM-as-Judge Evaluation with Human Spot-Checking](../workflows/llm-as-judge-evaluation.md)
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md)
