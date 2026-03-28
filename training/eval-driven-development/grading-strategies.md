---
title: "Grading Strategies for Agent Evaluation Suite Design"
description: "Code-based grading, LLM-as-judge evaluation, and human review — when to use each method and how to calibrate them for reliable agent quality measurement."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
---

# Grading Strategies

> The grader determines what "correct" means — choose the wrong grading strategy and your eval suite measures the wrong thing.

---

## Three Grading Methods

Every eval task needs a grader: the mechanism that compares agent output against expected behavior and produces a pass/fail verdict. The three methods form a hierarchy — use the lightest one that covers each case.

| Method | Speed | Reliability | Coverage |
|--------|-------|-------------|----------|
| Code-based | Milliseconds | Deterministic | Limited to verifiable outputs |
| LLM-as-judge | Seconds | Requires calibration | Covers subjective quality |
| Human | Minutes to hours | Gold standard | Covers everything |

---

## Code-Based Grading

Code-based graders are deterministic: same input, same verdict, every time. This eliminates the grader itself as a source of noise in your eval results.

**When to use**: outputs are objectively verifiable — test pass/fail, schema validation, state comparison, regex matching, numeric thresholds.

**Implementation patterns**:

```python
def grade_code_based(output, expected):
    """Grade using deterministic checks."""
    # Test suite passes
    if expected.get("passes_tests"):
        if not run_test_suite(output):
            return "FAIL", "Tests did not pass"

    # Output matches schema
    if expected.get("schema"):
        try:
            jsonschema.validate(output, expected["schema"])
        except ValidationError as e:
            return "FAIL", f"Schema violation: {e.message}"

    # Required content present
    if expected.get("contains"):
        for term in expected["contains"]:
            if term.lower() not in output.lower():
                return "FAIL", f"Missing required content: {term}"

    return "PASS", None
```

**Strengths**: fast, deterministic, no external dependencies, easy to debug. When a code-based grader fails, you know exactly why.

**Weakness**: limited to what can be verified programmatically. Cannot assess style, coherence, factual accuracy of free-form text, or whether an explanation is helpful.

For coding agents, test suites are the most reliable outcome grader — they are objective, fast, and path-agnostic. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

---

## LLM-as-Judge

Using a model to grade another model's output enables evaluation at scale for free-form outputs that resist programmatic checks.

**When to use**: outputs require subjective judgment — factual accuracy, completeness, style compliance, source quality, helpfulness.

**Key design decisions**:

**Score dimensions independently.** Track individual scores for each quality dimension rather than relying solely on a single aggregate. An output can be factually accurate but incomplete, or complete but citing low-quality sources. A single pass/fail hides which dimension failed. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

```python
RUBRIC = """
Score each dimension 1-5:

1. FACTUAL_ACCURACY: Are all claims correct and verifiable?
2. COMPLETENESS: Does the output cover all required topics?
3. SOURCE_QUALITY: Are sources authoritative and current?
4. CONCISENESS: Is the output free of filler and repetition?

For each dimension, provide the score and a one-sentence justification.
Output as JSON: {"factual_accuracy": {"score": N, "reason": "..."}, ...}
"""
```

**Single call outperforms multiple specialized judges.** A single comprehensive prompt with all rubric dimensions produces more consistent scores than routing each dimension to a separate evaluator. [Source: [Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)]

**Calibrate against human reviewers.** Score a sample set with both the judge and human reviewers using the same rubric, then resolve disagreements by refining the rubric or the judge prompt. This is not a one-time step — recalibrate when new query types enter the distribution.

See [LLM-as-Judge Evaluation with Human Spot-Checking](../../workflows/llm-as-judge-evaluation.md) for the full pipeline.

---

## Human Grading

Human grading is the gold standard — it can assess anything. It is also the slowest, most expensive, and least scalable method.

**When to use**:

- Calibrating LLM judges (the bootstrapping step)
- Ambiguous edge cases where neither code nor LLM judges produce reliable verdicts
- Novel failure modes not yet covered by the rubric
- Safety-critical evaluations where automated grading errors are unacceptable

**In practice**: human grading is the calibration layer, not the production layer. Grade a sample with humans, use those grades to calibrate an LLM judge, then use the LLM judge for scale. Periodically re-sample with humans to detect judge drift.

---

## Combining Graders

Most eval suites combine all three methods:

```
Code-based grading  →  catches structural failures (schema, tests, format)
         ↓ passes
LLM-as-judge        →  catches quality failures (accuracy, completeness)
         ↓ passes
Human spot-check    →  catches judge failures (rubric gaps, novel cases)
```

This layering is analogous to [layered accuracy defense](../../verification/layered-accuracy-defense.md) — each layer catches what the previous one misses, and the compounded miss rate is lower than any single layer's.

**Routing logic**: use code-based grading for everything it can assess. Only escalate to LLM-as-judge for dimensions that require subjective judgment. Reserve human grading for calibration and edge cases.

---

## Grader Validation

Graders can have bugs. CORE-Bench penalized correct answers due to grader bugs; fixing the graders pushed scores from 42% to 95%. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

Before trusting a grader:

1. **Test with known-good outputs**: feed outputs you know are correct and verify the grader passes them
2. **Test with known-bad outputs**: feed outputs you know are incorrect and verify the grader fails them
3. **Check for false negatives**: when a task fails, manually inspect whether the output was actually correct but the grader was too strict
4. **Check for false positives**: sample passing tasks and verify the output genuinely meets the criteria

A grader that produces false confidence is worse than no grader at all — it creates a misleading baseline that makes regressions invisible.

---

## Key Takeaways

- Use code-based grading first — it is deterministic and eliminates the grader as a source of noise
- LLM-as-judge enables evaluation of subjective quality at scale; score orthogonal dimensions independently
- Calibrate LLM judges against human reviewers; recalibrate when the query distribution changes
- Layer graders: code-based catches structure, LLM-as-judge catches quality, human catches everything else
- Validate graders before trusting them — grader bugs can mask real quality problems

## Related

- [What Evals Are and Why Agents Need Them](what-evals-are.md) — foundational concepts
- [Writing Your First Eval Suite](writing-first-eval-suite.md) — previous module
- [The Eval-First Development Loop](eval-first-loop.md) — next module
- [LLM-as-Judge Evaluation with Human Spot-Checking](../../workflows/llm-as-judge-evaluation.md)
- [Behavioral Testing for Agents](../../verification/behavioral-testing-agents.md)
- [Hardening Evals for Production](hardening-evals.md) — [anti-reward hacking](../../verification/anti-reward-hacking.md) and grader validation
- [Step-by-Step: Building Your First Eval-Driven Feature](step-by-step-first-feature.md) — hands-on walkthrough applying grading strategies
