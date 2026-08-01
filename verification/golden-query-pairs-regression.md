---
title: "Golden Query Pairs as Continuous Regression Tests for Agents"
term: "Golden Query Pairs as Continuous Regression Tests"
description: "Maintain a curated set of question-answer pairs with known-good expected outputs, and run them continuously against agent changes using semantic grading rather than string matching."
aliases:
  - Golden Query Pairs
  - Eval Regression Tests
tags:
  - agent-design
  - testing-verification
  - evals
  - tool-agnostic
last_reviewed: 2026-08-02
maturity: established
---

# Golden Query Pairs as Continuous Regression Tests for Agents

> Maintain a curated set of question-answer pairs with known-good expected outputs, and run them continuously against agent changes using semantic grading rather than string matching.

!!! note "Also known as"
    Golden Query Pairs, Eval Regression Tests. A specific technique within [Eval-Driven Development](../workflows/eval-driven-development.md); see also [applying the loop to tool building](../workflows/eval-driven-development.md#applying-the-loop-to-tool-building).

## Evals as regression tests

Agent capability degrades silently as prompts, tools, context, or models change. Without continuous evaluation, you find out about regressions through user complaints. This class of failure has a name — *prompt regression*, where small prompt or instruction edits quietly break behavior with no error raised ([Towards Data Science — Prompt Engineering Fails Quietly](https://towardsdatascience.com/prompt-engineering-fails-quietly-prompt-regression-is-why/)).

OpenAI's data agent team treats evals as "unit tests that run continuously during development" and "canaries in production" — golden question-answer pairs run on every agent configuration change. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## What makes a good golden pair

A golden pair consists of:

- A natural language question representing a pattern the team cares about
- An expected output — the "golden" answer — authored by a domain expert

Good pairs target patterns the agent is most likely to get wrong, cover edge cases that have caused past failures, and represent real user inputs rather than sanitized demos.

Avoid pairs where the expected output has an obvious format that tempts over-rigid grading — "what is the total revenue for Q3?" has many correct phrasings. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Semantic grading, not string matching

Generated output can differ in form while still being correct. String matching marks correct-but-reworded answers as failures.

Use an LLM-based grader that produces a score plus explanation for each pair:

1. Present the question, the golden answer, and the generated output.
2. Ask the grader whether they are semantically equivalent.
3. Use the grader's explanation to surface partial or dimension-shifted answers.

For coding agents, grade the execution result alongside the artifact — different code producing the same wrong output still fails. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Dual role: development guard and production canary

- Development guard: run it on every change to prompts, tools, or configuration. A degraded score blocks the change.
- Production canary: run it periodically against the live agent to detect drift from model, provider, or context changes.

[Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Building the suite

We recommend starting with 20 to 50 manually authored pairs covering failures, edge cases, and high-volume scenarios. That range is our own starting point rather than a published finding: it is small enough that a domain expert can author and review every pair by hand. Grow the suite continuously — every production failure is a candidate pair (see [Incident-to-Eval Synthesis](incident-to-eval-synthesis.md)). Review goldens for drift periodically. A stale suite hides regressions behind [benchmark-contamination](benchmark-contamination-eval-risk.md) and [reward-hacking](anti-reward-hacking.md) dynamics.

## For coding agents

For code-generating agents:

- Question: a coding task description (refactor, fix, implement)
- Golden answer: the expected behavior or outcome, not exact code
- Grading: does the generated code pass tests or meet acceptance criteria?

The grader judges functional equivalence, not textual identity.

## When this backfires

The approach assumes the suite represents the target distribution and that the grader's judgments are stable. Both break under specific conditions:

- Overfitting to the eval set. If the suite is small and authored by the same team tuning prompts, scores improve without improving real-user behavior — benchmarks lose discriminative power once they become the optimization target. [Source: [Categorizing Variants of Goodhart's Law](https://arxiv.org/abs/1803.04585)]
- Grader bias contaminates the signal. LLM judges show position, verbosity, and self-enhancement biases. A "regression" may be grader drift rather than agent drift, especially when the judge model is updated. [Source: [Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge](https://arxiv.org/abs/2410.02736)]
- Stale goldens mark correct answers wrong. Golden answers erode as the agent's tools, data, or scope legitimately change. Without periodic re-review, passing the suite stops meaning the agent is correct. [Source: [Golden Datasets for GenAI Testing](https://www.techment.com/blogs/golden-datasets-for-genai-testing/)]
- Cost and latency break continuity. A large suite graded by a strong judge adds minutes and dollars per CI run, pushing teams to sample or skip the check.

A smaller bank of deterministic assertions (schema checks, known-answer lookups, tool-call shape) plus periodic human spot-review complements the suite when these conditions dominate.

## Example

The following shows a minimal golden pair eval runner using the Anthropic SDK. It runs each pair through the agent under test, then sends the question, golden answer, and generated output to a grader model that returns a pass/fail score with explanation.

```python
import anthropic
import json

client = anthropic.Anthropic()

GOLDEN_PAIRS = [
    {
        "question": "What was the total revenue for Q3 2024?",
        "golden": "Total Q3 2024 revenue was $4.2M, up 18% quarter-over-quarter.",
    },
    {
        "question": "Which product line had the highest return rate last month?",
        "golden": "The Accessories line had the highest return rate at 6.3% in October 2024.",
    },
]

GRADER_PROMPT = """You are an eval grader.
Question: {question}
Golden answer: {golden}
Generated output: {generated}

Is the generated output semantically equivalent to the golden answer?
Reply with JSON: {{"pass": true/false, "explanation": "..."}}"""

def run_agent(question: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text

def grade(question: str, golden: str, generated: str) -> dict:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": GRADER_PROMPT.format(
                question=question, golden=golden, generated=generated
            ),
        }],
    )
    return json.loads(response.content[0].text)

results = []
for pair in GOLDEN_PAIRS:
    generated = run_agent(pair["question"])
    verdict = grade(pair["question"], pair["golden"], generated)
    results.append({"question": pair["question"], **verdict})
    print(f"{'PASS' if verdict['pass'] else 'FAIL'}: {verdict['explanation']}")

pass_rate = sum(r["pass"] for r in results) / len(results)
print(f"\nPass rate: {pass_rate:.0%} ({len(results)} pairs)")
```

The grader outputs a structured verdict for each pair, making it straightforward to fail CI when `pass_rate` drops below a threshold.

## Key Takeaways

- Curated golden question-answer pairs run continuously serve as regression guards and production canaries
- Use LLM-based semantic graders that produce scores plus explanations — string matching produces false negatives
- Grade both the generated artifact and its execution result; different code can produce the same wrong output
- Grow the suite by converting production failures into golden pairs after fixing them
- Review golden answers periodically — some will become outdated as agent capabilities legitimately evolve

## Related

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md)
- [Benchmark Contamination as an Eval Risk](benchmark-contamination-eval-risk.md)
- [Anti Reward Hacking](anti-reward-hacking.md)
- [Evaluator Templates: Portable Primitives](evaluator-templates.md)
- [Eval Awareness: Designing Evals Agents Cannot Recognize](eval-awareness.md)
