---
title: "Eval-Driven Development: Write Evals Before Building Agent"
description: "Define evaluation tasks and success criteria before writing agent feature code so that done has an objective, measurable definition from the start."
aliases:
  - Write Evals Before Building
  - Eval-First Development
tags:
  - agent-design
  - testing-verification
  - workflows
---
# Eval-Driven Development: Write Evals Before Building Agent Features

> Define evaluation tasks and success criteria before implementing an agent feature so that "done" has an objective definition before any code is written.

!!! note "Also known as"
    Write Evals Before Building, Eval-First Development. For the specific technique of using input/output pairs as regression tests, see [Golden Query Pairs](../verification/golden-query-pairs-regression.md). For applying this methodology to tool development specifically, see [Eval-Driven Tool Development](eval-driven-tool-development.md).

## Why Write Evals First

Teams that write evals after the fact tend to reverse-engineer success criteria from a live system. This embeds the agent's current behavior — including its bugs — into the definition of correct. The eval suite then validates what the agent already does rather than what it should do.

Writing evals first forces clarity: you must decide what "done" means before building toward it. A low pass rate on a new capability eval is a feature, not a problem — it identifies the gap and makes progress visible as implementation proceeds. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## What to Write Before Building

Before writing any agent feature code:

1. **Define the tasks**: 20-50 representative inputs the agent must handle correctly. Source these from real failure cases, anticipated edge cases, or the specific behaviors that motivated the feature. A small set is enough for early signal; precision matters more than volume. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

2. **Define the success criteria**: What does a correct output look like for each task? This is the hardest part. If the task is ambiguous, domain experts should independently agree on the pass/fail verdict before the task is committed to the suite. Ambiguous task specifications are a source of misleading eval results. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

3. **Choose a grader**: For deterministic outcomes, use automated checks (test pass/fail, schema validation, state comparison). For subjective outcomes, define an LLM rubric with explicit criteria. For complex tasks, consider combining both.

Run the eval suite against a baseline before any development. The baseline failure rate tells you how much the feature actually needs to change agent behavior.

## Converting Existing Work

You likely already have inputs suitable for an eval suite:

- **Manual development checks**: any scenario you tested by hand during development is a candidate eval task
- **Production failures**: incidents and bug reports are high-value eval tasks because they represent real cases the agent actually mishandled — see [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md) for a systematic pipeline
- **Exploratory tests**: ad hoc prompts you ran while figuring out how a feature should behave

Converting these to formal eval tasks avoids duplicating effort and anchors the suite to problems that actually matter. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## Evals as Executable Specifications

Eval tasks function as executable specifications. When a task is well-defined, it answers the question "does this feature work?" with a reproducible, automatable check rather than a manual judgment call.

This has a compounding benefit during model upgrades: teams with evals in place can adopt new model releases in days; teams without them face weeks of manual regression testing per upgrade. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)] A broader reference architecture places evaluation as a continuous governing function across both offline (development-time) and online (runtime) stages rather than a terminal checkpoint. [Source: [Evaluation-Driven Development and Operations of LLM Agents (arxiv 2411.13768)](https://arxiv.org/abs/2411.13768)]

## Common Pitfalls

**Overfitting the eval to the implementation**: if you write tasks while building the feature, you may unconsciously write tasks that match what the agent already does rather than what it should do. Write tasks based on expected behavior, not observed behavior.

**Ambiguous pass/fail criteria**: tasks where two experts disagree on the correct answer produce misleading aggregate pass rates. Get agreement before committing a task.

**Graders that are too strict**: exact-match verifiers reject valid alternative solutions. Use outcome-based graders (state checks, test suites) or semantic equivalence graders rather than string matching.

**Too few tasks**: 5 tasks is enough to start, but not enough to detect regression reliably. Grow the suite as edge cases are discovered.

## When This Backfires

Eval-driven development is not the right default for every situation. Write evals first when you have enough of a problem shape to define "done"; skip or defer it in these cases:

- **Early exploration of a novel problem space**: when the team genuinely does not yet know what correct behaviour looks like, committing to pass/fail criteria upfront anchors the project to metrics that may prove irrelevant. Quick manual iteration builds the understanding needed to write meaningful evals later.
- **Short-lived prototypes and spikes**: a throwaway script explored over a single afternoon does not pay back the cost of a 20-50 task suite. The eval harness is heavier than the artifact it evaluates.
- **Highly subjective outputs with shifting preferences**: when success hinges on evolving aesthetic or stylistic judgment (e.g., creative copy, UX tone) that changes faster than the eval set can be updated, the suite misleads more than it informs — tasks pass while real users dislike the output.
- **Unstable upstream dependencies**: if the tools, APIs, or data sources the agent depends on churn weekly, the eval set breaks faster than it yields signal. Defer formal evals until the environment stabilises.

A practical heuristic: if you cannot get two reviewers to agree on pass/fail for 20 representative tasks, the problem is not yet eval-ready — do targeted manual iteration first, then convert the resulting observations into an eval suite.

## Example

The following shows the eval-first workflow applied to a new "summarise PR diff" agent feature. Tasks and graders are written before any implementation code exists.

**`evals/summarise-pr/tasks.yaml`** — defined before writing the feature

```yaml
- id: single-file-rename
  input:
    diff: |
      diff --git a/src/utils.py b/src/helpers.py
      similarity index 100%
      rename from src/utils.py
      rename to src/helpers.py
  expected_topics:
    - file renamed
    - no logic changes

- id: breaking-api-change
  input:
    diff: "@@ -12,7 +12,7 @@ def fetch(url, timeout=30):\n-def fetch(url, timeout=30):\n+def fetch(url, *, timeout=30):"
  expected_topics:
    - keyword-only argument
    - breaking change
```

**`evals/summarise-pr/run.py`** — grader using Claude as judge

```python
import anthropic, yaml, json

client = anthropic.Anthropic()
tasks = yaml.safe_load(open("evals/summarise-pr/tasks.yaml"))

for task in tasks:
    result = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        system="Summarise the following git diff in 2-3 sentences.",
        messages=[{"role": "user", "content": task["input"]["diff"]}],
    )
    summary = result.content[0].text
    verdict = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=64,
        system="Reply with PASS or FAIL only.",
        messages=[{
            "role": "user",
            "content": f"Does this summary mention all of {task['expected_topics']}?\n\n{summary}"
        }],
    )
    print(task["id"], verdict.content[0].text.strip())
```

Running this suite against a baseline before any feature code is written produces a clear failure rate — the gap the implementation must close, not a post-hoc rubber stamp.

## Key Takeaways

- Writing evals after the fact embeds current bugs into the definition of correct; write them before development instead
- Start with 20-50 tasks sourced from real failures and anticipated edge cases — small sets still show clear signal
- Low initial pass rates on new capability evals are a feature: they define the improvement surface
- Ambiguous task specifications are a source of misleading eval results — get expert agreement first
- Teams with eval suites can adopt model upgrades in days; teams without them face weeks of manual regression testing per release

## Related

- [Evaluation-Driven Development for Agent Tools](eval-driven-tool-development.md)
- [Grade Agent Outcomes, Not Execution Paths](../verification/grade-agent-outcomes.md)
- [Eval-Driven Development: Golden Query Pairs as Regression Tests](../verification/golden-query-pairs-regression.md)
- [Test-Driven Agent Development](../verification/tdd-agent-development.md)
- [LLM-as-Judge Evaluation with Human Spot-Check Review](llm-as-judge-evaluation.md)
- [Simulation and Replay Testing for Agent Verification](simulation-replay-testing.md)
- [Failure-Driven Iteration for Improving Agent Workflows](failure-driven-iteration.md)
- [Spec-Driven Development: Build with a Persistent Spec](spec-driven-development.md)
- [Verification-Centric Development for AI-Generated Code](verification-centric-development.md)
- [The Eval-First Development Loop](../training/eval-driven-development/eval-first-loop.md) — training module with step-by-step loop walkthrough
