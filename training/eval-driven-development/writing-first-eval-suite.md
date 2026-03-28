---
title: "Writing Your First Agent Evaluation Suite from Scratch"
description: "Step-by-step guide to building an agent evaluation suite — from defining 20 tasks and success criteria to choosing graders and running baselines."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
---

# Writing Your First Eval Suite

> Start with 20–50 tasks, clear success criteria, and a simple grader — then grow the suite as you learn what fails.

---

## The Starting Point: 20 Tasks

The most common mistake is waiting until you have a comprehensive suite. Start with 20–50 tasks. This is enough to detect large effect sizes (e.g., a 30% to 80% improvement from a prompt change) without a large dataset upfront. Precision matters more than volume. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

Where to source tasks:

- **Real failure cases**: scenarios where the agent actually failed in testing or production — these are the highest-signal tasks because they represent proven failure modes
- **Anticipated edge cases**: inputs that are likely to expose weaknesses based on the feature's design
- **Manual checks you already run**: any scenario you test by hand during development is a candidate eval task — formalizing it prevents the check from being forgotten

Avoid inventing synthetic tasks that do not correspond to real usage patterns. Synthetic tasks produce pass rates that do not predict production reliability.

---

## Defining Success Criteria

For each task, define what a correct output looks like. This is the hardest step and the one most teams rush through.

**Binary outcomes** (the output is either right or wrong): test pass/fail, schema validation, state comparison. A coding agent either produces code that passes the test suite or it does not.

**Subjective outcomes** (correctness requires judgment): completeness, factual accuracy, style compliance, source quality. A summarization agent's output requires a rubric to evaluate.

**The agreement test**: two domain experts should independently agree on the pass/fail verdict for every task before the task is committed to the suite. If they disagree, the task specification is ambiguous — and ambiguous task specifications are a leading source of misleading eval results. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

---

## Choosing a Grader

Use the lightest grader that covers each task:

| Method | Best for | Trade-off |
|--------|----------|-----------|
| **Code-based** | Deterministic outputs: test pass/fail, schema validation, regex, state comparison | Fastest, most reliable, but limited to verifiable outputs |
| **LLM-as-judge** | Open-ended outputs: style, completeness, factual accuracy, source quality | Scalable, but requires calibration against human judgment |
| **Human** | Ambiguous edge cases, novel failure modes, calibrating LLM judges | Most flexible, but slowest and most expensive |

Code-based grading first, LLM-as-judge for what code cannot assess, human grading as a last resort. Cost scales with grader complexity: code-based grading is essentially free, while LLM-as-judge incurs API costs per task per run — with 50 tasks at 3 runs each, costs compound quickly. For a deep dive on each method, see [Grading Strategies](grading-strategies.md).

For your first suite, start with code-based grading wherever possible. It eliminates the grader itself as a source of uncertainty — which is one fewer variable when you are still learning what your eval suite is telling you.

---

## Structuring the Suite

A minimal eval suite has three components:

**1. Task definitions** — the inputs and expected outputs:

```yaml
# evals/feature-name/tasks.yaml
- id: descriptive-case-name
  input:
    prompt: "The input the agent receives"
    context: "Any additional context provided"
  expected:
    contains: ["keyword1", "keyword2"]
    passes_test: true
    max_length: 500

- id: edge-case-empty-input
  input:
    prompt: ""
  expected:
    error_type: "validation_error"
```

**2. Runner** — executes the agent against each task:

```python
# evals/feature-name/run.py
import yaml, json

tasks = yaml.safe_load(open("evals/feature-name/tasks.yaml"))

for task in tasks:
    result = run_agent(task["input"])  # your agent invocation
    verdict = grade(result, task["expected"])  # your grading logic
    print(json.dumps({
        "id": task["id"],
        "verdict": verdict,
        "output": result[:200]  # truncate for readability
    }))
```

**3. Grader** — compares agent output against expected:

```python
def grade(result, expected):
    if "contains" in expected:
        for keyword in expected["contains"]:
            if keyword.lower() not in result.lower():
                return "FAIL"
    if "passes_test" in expected:
        if not run_tests():
            return "FAIL"
    return "PASS"
```

Keep the structure simple. You will iterate on it. Premature abstraction in eval infrastructure is as costly as premature abstraction anywhere else.

---

## Running the Baseline

Before writing any feature code, run the suite against the current agent state. This baseline tells you:

- **Current pass rate**: how much the feature actually needs to change agent behavior
- **Which tasks already pass**: surprising passes reveal that the agent already handles some cases — you may not need to build what you thought
- **Which tasks fail**: the improvement surface your implementation must address

A low initial pass rate on a new capability eval is a feature, not a problem — it defines the gap and makes progress visible as implementation proceeds. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

Record the baseline results. Every subsequent run compares against this anchor.

---

## Growing the Suite

After the initial 20 tasks, grow the suite from two sources:

**Production incidents**: every failure report is a candidate eval task. See [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md) for the systematic pipeline from incident to eval case.

**Edge cases discovered during development**: as you build the feature, you will encounter inputs that expose unexpected behavior. Add these immediately — they are the cases you will forget to test manually later.

Do not add tasks to pad the count. Every task should represent a genuinely distinct scenario. Duplicate tasks inflate the pass rate without improving coverage.

---

## Common First-Suite Mistakes

**Writing tasks after implementation**: this embeds the agent's current behavior into the definition of correct. Write tasks based on what the agent *should* do, not what it *currently* does.

**Graders that are too strict**: exact-match verifiers reject valid alternative solutions. Use outcome-based graders (state checks, test suites) or semantic equivalence rather than string matching.

**No baseline run**: skipping the baseline means you cannot measure progress. A pass rate of 85% is meaningless without knowing the starting point.

**Single-run evaluation**: running each task once gives a misleading confidence level. Run at least 3 times per task to detect variance. If variance is high (pass rate swings more than 20% between runs), you need more runs or tighter task specifications.

**Too few runs for small effects**: a suite of 20–50 tasks at 3 runs each can detect large improvements (30% → 80%) but not small ones (85% → 90%). As changes become incremental, increase task count or run count to maintain the ability to distinguish real improvements from noise.

---

## Key Takeaways

- Start with 20 tasks sourced from real failures and anticipated edge cases — do not wait for comprehensive coverage
- Define success criteria before writing code; get expert agreement on ambiguous tasks
- Use code-based grading first, LLM-as-judge where code cannot assess, human grading as last resort
- Run the baseline before any development — low initial pass rates are a feature, not a problem
- Grow the suite from production incidents and edge cases discovered during development

## Related

- [What Evals Are and Why Agents Need Them](what-evals-are.md) — previous module
- [Grading Strategies](grading-strategies.md) — next module: deep dive on grader design
- [The Eval-First Development Loop](eval-first-loop.md) — eval-driven workflow from write-evals to ship
- [Hardening Evals for Production](hardening-evals.md) — anti-reward hacking, grader validation, and production-grade reliability
- [Step-by-Step: Building Your First Eval-Driven Feature](step-by-step-first-feature.md) — hands-on walkthrough building a PR description generator
- [Eval-Driven Development](../../workflows/eval-driven-development.md) — reference page on the eval-first workflow
- [Incident-to-Eval Synthesis](../../verification/incident-to-eval-synthesis.md) — systematic pipeline from incidents to eval tasks
