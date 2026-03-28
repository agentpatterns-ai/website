---
title: "pass@k and pass^k: Capability and Consistency Metrics"
description: "Use pass@k and pass^k together: pass@k shows if an agent can solve a problem at all; pass^k shows if it reliably does. A single pass rate conflates the two."
tags:
  - testing-verification
  - evals
  - cost-performance
---

# Use pass@k and pass^k to Separate Agent Capability from Consistency

> A single pass rate conflates two distinct properties of a non-deterministic agent: whether it *can* solve the problem and whether it *reliably* does. Use pass@k and pass^k together to measure both.

## The Problem with a Single Pass Rate

AI agents are non-deterministic. The same prompt, same task, same environment can produce different results on successive runs. A single pass/fail result tells you what happened once — not what to expect across your workflow.

Reporting a single pass rate from a single trial hides the signal. An agent that solves a benchmark 60% of the time on one run might score anywhere from 40% to 80% depending on sampling temperature and task complexity. Worse, it treats an agent that always scores 6/10 identically to one that randomly scores 0/10 or 10/10.

## The Two Metrics

**pass@k** — the probability the agent produces at least one correct solution across *k* attempts.

As *k* increases, pass@k rises. It measures capability ceiling: given enough chances, can the agent ever get this right? It answers: "Is this problem solvable at all with this agent?"

**pass^k** — the probability *all k* attempts succeed.

As *k* increases, pass^k falls. It measures consistency: does the agent reliably solve this, or does it sometimes succeed and sometimes fail? It answers: "Can I trust this agent to get it right in production?"

[Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## What the Combination Reveals

| pass@k | pass^k | Interpretation |
|--------|--------|----------------|
| High | High | Capable and consistent. Production-ready for this task class. |
| High | Low | Capable but flaky. Human review required; not safe for automation. |
| Low | — | Cannot reliably solve this class of problem at all. |

An agent with high pass@k and low pass^k signals a specific failure mode: it occasionally hits the right answer but cannot be trusted to do so every time. This is the pattern of an agent that is benchmarking well but failing in production.

## Choosing the Right Primary Metric

**Human-in-the-loop workflows**: pass@k is the relevant metric. If a developer reviews every agent output before it takes effect, a single correct answer in three attempts is often sufficient. The agent's job is to surface a good option.

**Automated pipelines**: pass^k is the critical metric. If the agent's output is consumed directly without review — merging code, sending messages, modifying databases — you need high consistency across all attempts, not just occasional success. A 90% pass rate means roughly 1-in-10 automated runs fails.

## How to Run the Measurement

1. Define the task and a deterministic correctness check (test suite pass, schema validation, expected output)
2. Run the agent on the same task *k* times (typically k=3–10 depending on cost tolerance)
3. Compute pass@k: did any run succeed?
4. Compute pass^k: did all runs succeed?
5. Aggregate across the task suite to get rates

Report both numbers. A benchmark that reports only pass@1 is hiding the consistency story. A benchmark that reports only pass^1 is reporting a single data point as if it were stable.

## Practical Guidance

Run at least k=3 for any task that matters. Single-trial evaluation is a sample of size one. Temperature and context variation mean two identical prompts can produce qualitatively different results.

Use pass^k to set deployment thresholds. If your automated pipeline cannot tolerate a failure rate above 5%, require pass^k ≥ 0.95 before promoting a model or prompt change.

Use pass@k during development to identify capability gaps vs. consistency gaps. If pass@k is low, the agent cannot solve the problem. If pass@k is high but pass^k is low, the problem is consistency — address it with better instructions, lower temperature, or added verification steps rather than retraining.

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
- [LLM-as-Judge Context Test Harness](llm-context-test-harness.md)
- [LLM-as-Judge Evaluation with Human Spot-Checking](../workflows/llm-as-judge-evaluation.md)
