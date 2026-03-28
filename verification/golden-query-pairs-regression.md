---
title: "Golden Query Pairs as Continuous Regression Tests for Agents"
description: "Maintain a curated set of question-answer pairs with known-good expected outputs, and run them continuously against agent changes using semantic grading rather than string matching."
aliases:
  - Golden Query Pairs
  - Eval Regression Tests
tags:
  - agent-design
  - testing-verification
  - evals
---

# Golden Query Pairs as Continuous Regression Tests for Agents

> Maintain a curated set of question-answer pairs with known-good expected outputs, and run them continuously against agent changes using semantic grading rather than string matching.

!!! note "Also known as"
    Golden Query Pairs, Eval Regression Tests. This is a specific technique within the broader [Eval-Driven Development](../workflows/eval-driven-development.md) methodology. For applying eval-driven development to tool building specifically, see [Eval-Driven Tool Development](../workflows/eval-driven-tool-development.md).

## Evals as Regression Tests

Agent capability can degrade silently as prompts, tools, context, or models change. Without continuous evaluation, regressions surface through user complaints rather than systematic testing.

OpenAI's data agent team treats evals as "unit tests that run continuously during development" and as "canaries in production." The mechanism is a curated set of golden question-answer pairs with known-good expected outputs that run on every agent configuration change. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## What Makes a Good Golden Pair

A golden pair consists of:

- A natural language question representing a pattern the team cares about
- An expected output — the "golden" answer — authored by a domain expert

Good golden pairs:

- Target the patterns the agent is most likely to get wrong
- Cover the edge cases that have caused failures in the past
- Represent the variety of real user inputs, not sanitized demos

Avoid pairs where the expected output has an obvious format that tempts over-rigid grading. The question "what is the total revenue for Q3?" has many correct phrasings and formats for the answer. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Semantic Grading, Not String Matching

Generated output can differ in form while being functionally correct. String matching produces false negatives: a correct answer phrased differently is marked as a failure.

Use an LLM-based grader that produces a score plus explanation for each pair:

1. Present the question, the golden answer, and the generated output
2. Ask the grader to assess whether they are semantically equivalent
3. The grader's explanation surfaces edge cases where the answer is partially correct or correct on a different dimension

For coding agents, grade the execution result in addition to the generated artifact. Different code that produces the same wrong output still fails; different code that produces the correct output passes. [Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Dual Role: Development Guard and Production Canary

Golden pair evals serve two distinct roles:

**Development guard**: run on every change to agent prompts, tools, or configuration to catch regressions before deployment. A degraded score on the eval suite blocks the change.

**Production canary**: run periodically against the live agent to detect drift caused by model updates, provider changes, or context accumulation. The same suite catches regressions in production if something slipped through.

[Source: [Inside Our In-House Data Agent](https://openai.com/index/inside-our-in-house-data-agent/)]

## Building the Suite

Start with 20-50 manually authored pairs covering the most important patterns:

- Real user questions that previously caused failures
- Edge cases identified during development
- High-volume usage scenarios

Grow the suite continuously. Every production failure is a candidate for a new golden pair — fix the failure, then add the question and correct answer to prevent regression. See [Incident-to-Eval Synthesis](incident-to-eval-synthesis.md) for a systematic approach to this pipeline.

Periodically review golden answers that have become outdated as the agent's scope or behavior has legitimately changed.

## For Coding Agents

For agents that generate code rather than query results, golden pairs need adaptation:

- **Question**: a description of the coding task (refactor this function, fix this bug, implement this feature)
- **Golden answer**: the expected behavior or outcome, not necessarily the exact code
- **Grading**: does the generated code pass the tests? Does it meet the acceptance criteria in the task description?

The grader judges functional equivalence, not textual identity.

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
- [Evaluation-Driven Development for Agent Tools](../workflows/eval-driven-tool-development.md)
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Using the Agent to Analyze Its Own Evaluation Transcripts](agent-transcript-analysis.md)
- [Test-Driven Agent Development](tdd-agent-development.md)
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md)
