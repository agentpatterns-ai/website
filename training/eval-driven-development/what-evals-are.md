---
title: "What Evals Are and Why AI Agents Need Them for Quality"
description: "How agent evaluations differ from traditional software tests, why non-determinism breaks conventional QA, and the metrics that measure agent reliability."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - agent evals
  - LLM evaluations
  - agent evaluation
---

# What Evals Are and Why Agents Need Them

> Evals measure agent quality across runs and over time — they answer "is the agent getting better or worse?" in a way that traditional tests cannot.

---

## The Non-Determinism Problem

Traditional software tests assert that a specific input produces a specific output. Run the test today, run it tomorrow — same result (assuming no code changes). This determinism is what makes test suites trustworthy as deployment gates.

Agents break this assumption. The same prompt, same task, same environment can produce different results on successive runs. Temperature settings, context window contents, model updates, and even the order of tool results introduce variance that no amount of test design eliminates. A test suite that passes today may fail tomorrow without any change to your code.

This is not a bug in agents — it is a fundamental property of systems built on language models. The testing discipline must adapt to it, not pretend it does not exist.

---

## Evals Are Not Tests

The distinction is structural, not semantic:

| Property | Traditional test | Agent eval |
|----------|-----------------|------------|
| Result | Binary: pass or fail | Statistical: pass rate across N runs |
| Determinism | Same input → same output | Same input → distribution of outputs |
| Failure meaning | Bug in the code | Signal about reliability at this quality bar |
| When to run | After code changes | After code changes, prompt changes, model updates, and periodically |
| What it gates | Deployment | Deployment, model adoption, prompt changes |

A test that passes 95% of the time is broken. An eval that passes 95% of the time is measuring a 95% reliable agent — and that number is the information you need.

Evals serve two roles that tests do not: during development they function like unit tests that catch regressions continuously, and in production they act as canaries that detect drift caused by model updates or context accumulation. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

---

## Measuring Reliability: pass@k and pass^k

A single pass/fail result from one trial is a sample of size one. Two metrics separate capability from consistency:

**pass@k** measures whether the agent produces at least one correct solution across *k* attempts — the capability ceiling. If the agent solves the task in 1 out of 5 runs, pass@5 = 100%. This answers: "can the agent do this at all?"

**pass^k** measures whether *all k* attempts succeed — the consistency floor. If the agent solves the task in 4 out of 5 runs, pass^5 = 0% (because one run failed). This answers: "can the agent do this reliably?"

High pass@k with low pass^k means the agent can solve the problem but cannot be trusted to do so without supervision. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

The choice of primary metric depends on deployment context:

- **Human-in-the-loop** (developer reviews every output): pass@k matters — a single correct answer in three attempts is sufficient
- **Automated pipelines** (outputs consumed directly): pass^k is critical — a 90% pass rate means roughly 1-in-10 automated runs fails

See [pass@k and pass^k Metrics](../../verification/pass-at-k-metrics.md) for measurement methodology and worked examples.

---

## Why Traditional QA Fails for Agents

Teams that try to apply traditional QA practices to agents encounter three failure modes:

**Snapshot testing locks in bugs.** Recording "golden" outputs from the current agent and comparing future outputs against them embeds the agent's current behavior — including its bugs — into the definition of correct. Any improvement that changes the output format will fail the snapshot test.

**Path-based assertions penalize creativity.** Asserting that the agent called tool X before tool Y rejects valid alternative solutions the test author did not anticipate. An agent that finds a better path fails a test designed around the only path the author considered. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

**One-shot runs hide reliability problems.** Running each test once and reporting pass/fail gives a misleading confidence level. An agent that passes 70% of the time will produce a passing test run often enough to seem reliable — until production traffic reveals the true failure rate.

---

## What Evals Actually Measure

Good evals measure outcomes, not paths. For a coding agent, the outcome grader is often a test suite: did the code pass the tests? For a research agent, the grader checks factual accuracy and source quality. For a summarization agent, the grader checks completeness and faithfulness to the source.

The grader itself is a design decision with trade-offs covered in [Grading Strategies](grading-strategies.md). The key insight at this stage: the eval measures the *what* (did the agent produce the right result?) not the *how* (did the agent follow the expected sequence of actions?).

See [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md) for the full argument.

---

## When to Run Evals

Evals are not just a CI step. Run them:

- **Before development**: establish a baseline pass rate before writing any feature code
- **During development**: measure progress against the baseline as you iterate
- **Before deployment**: gate releases on pass rate thresholds
- **After model updates**: a model upgrade can silently degrade quality — evals catch this before users do
- **Periodically**: context drift, data changes, and upstream API changes can degrade quality even without code changes

Teams with eval suites in place can adopt new model releases in days; those without face weeks of manual regression testing per upgrade. See [Model Upgrade Testing](eval-first-loop.md#model-upgrade-testing) for the workflow. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

---

## Example

A coding agent that generates unit tests from function signatures. A traditional test and an eval for the same task:

**Traditional test** — asserts one expected output:

```python
def test_generate_tests():
    result = agent.generate_tests("def add(a, b): return a + b")
    assert "def test_add" in result
    assert "assert add(1, 2) == 3" in result  # locks in exact phrasing
```

This fails whenever the agent produces a valid but differently worded test — `assert add(2, 3) == 5` would fail even though it is correct.

**Eval** — measures outcomes across multiple runs:

```python
def eval_generate_tests(runs=5):
    results = []
    for _ in range(runs):
        output = agent.generate_tests("def add(a, b): return a + b")
        # Grade the outcome: does the generated test actually pass?
        passed = run_generated_test(output)
        results.append("PASS" if passed else "FAIL")

    pass_rate = results.count("PASS") / len(results)
    print(f"pass@{runs}: {1.0 if 'PASS' in results else 0.0}")
    print(f"pass^{runs}: {1.0 if all(r == 'PASS' for r in results) else 0.0}")
```

The eval does not care *how* the agent wrote the test. It checks whether the generated test runs and passes — the outcome, not the path. Running it five times reveals reliability: pass@5 = 100% means the agent can do it; pass^5 = 60% means it fails 2 out of 5 times.

---

## Key Takeaways

- Agents are non-deterministic — traditional pass/fail tests give a false sense of reliability
- Evals measure a distribution (pass rate across N runs), not a binary outcome
- pass@k measures capability (can the agent ever solve this?); pass^k measures consistency (does it reliably solve this?)
- Grade outcomes (final state), not execution paths (tool call sequences)
- Run evals at every change point: code, prompts, models, and periodically for drift

## Related

- [pass@k and pass^k Metrics](../../verification/pass-at-k-metrics.md)
- [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md)
- [Eval Engineering](../foundations/eval-engineering.md) — complementary module with broader scope
- [Writing Your First Eval Suite](writing-first-eval-suite.md) — next module in this pathway
- [Hardening Evals for Production](hardening-evals.md) — making eval suites resistant to gaming and drift
- [Step-by-Step: Building Your First Eval-Driven Feature](step-by-step-first-feature.md) — hands-on walkthrough applying the eval-first loop
