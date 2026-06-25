---
title: "Eval-Driven Development: Write Evals Before Building Agent"
term: "Eval-Driven Development"
description: "Define evaluation tasks and success criteria before writing agent feature code so that done has an objective, measurable definition from the start."
aliases:
  - Write Evals Before Building
  - Eval-First Development
tags:
  - agent-design
  - testing-verification
  - workflows
  - tool-agnostic
  - long-form
last_reviewed: 2026-06-12
maturity: established
---

# Eval-Driven Development: Write Evals Before Building Agent Features

> Define evaluation tasks and success criteria before implementing an agent feature so that "done" has an objective definition before any code is written.

**Learn it hands-on:** [Define "Done" First](https://learn.agentpatterns.ai/workflows/define-done-first/) — guided lesson with quizzes.

!!! note "Also known as"
    Write Evals Before Building, Eval-First Development, Eval-Driven Tool Development. For the specific technique of using input/output pairs as regression tests, see [Golden Query Pairs](../verification/golden-query-pairs-regression.md). For applying this methodology to tool building specifically, see [Applying the Loop to Tool Building](#applying-the-loop-to-tool-building) below.

## Why Write Evals First

Teams that write evals after the fact tend to reverse-engineer success criteria from a live system. This embeds the agent's current behavior — including its bugs — into the definition of correct. The eval suite then [grades what the agent already does](../verification/grade-agent-outcomes.md) rather than what it should do.

Writing evals first forces clarity: you must decide what "done" means before building toward it. A low pass rate on a new capability eval is a feature, not a problem — it identifies the gap and makes progress visible as implementation proceeds. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## What to Write Before Building

Before writing any agent feature code:

1. **Define the tasks**: 20-50 representative inputs the agent must handle correctly. Source these from real failure cases, anticipated edge cases, or the specific behaviors that motivated the feature. A small set is enough for early signal; precision matters more than volume. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

2. **Define the success criteria**: What does a correct output look like for each task? This is the hardest part. If the task is ambiguous, domain experts should independently agree on the pass/fail verdict — the same human-spot-check discipline behind [LLM-as-judge evaluation](llm-as-judge-evaluation.md) — before the task is committed to the suite. Ambiguous task specifications are a source of misleading eval results. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

3. **Choose a grader**: For deterministic outcomes, use automated checks (test pass/fail, schema validation, state comparison). For subjective outcomes, define an [LLM rubric](llm-as-judge-evaluation.md) with explicit criteria. For complex tasks, consider combining both.

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

## Applying the Loop to Tool Building

The same methodology applies when the artifact under development is an **agent tool** rather than an agent feature. Agent tools that appear capable during demos often degrade on real tasks — the gap usually lies in untested assumptions: unclear parameter descriptions that cause wrong tool selection, overlapping tool functionality that creates ambiguity, or response formats that waste context budget on irrelevant detail. Without evaluations, debugging is reactive: teams wait for complaints, reproduce issues manually, fix the bug, and hope nothing else regressed. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)] Systematic tool evaluation surfaces these failures before deployment. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

For tools, the eval-first discipline becomes a prototype-evaluate-analyze-iterate loop:

```
Prototype tool → Write evaluation tasks → Run evaluations
       ↑                                          │
       └──── Analyze transcripts ←── Track metrics┘
```

Each cycle produces a concrete change hypothesis grounded in observed failures — not guesswork.

**Write real-world tasks.** Effective tool-evaluation tasks require multiple tool calls and reflect the complexity of actual use; simplified sandbox scenarios mask problems that only appear when tools must coordinate. Source them from real user requests, known failure modes from prior sessions, and edge cases identified during design (pagination boundaries, empty results, permission errors). Pair each task with a verifiable expected outcome, but avoid verifiers so strict they reject valid alternative approaches, and hold out a test set — running the same tasks during development and final evaluation overfits the tool design to that task set. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

**Track multiple metrics per run** to triangulate problems:

| Metric | What It Signals |
|--------|-----------------|
| Accuracy | Whether the outcome is correct |
| Tool call count | Efficiency; unusually high count signals redundant or confusing tools |
| Token consumption | Cost; high consumption may indicate over-verbose tool responses |
| Tool errors | Parameter confusion, schema mismatches |
| Runtime | Latency; useful when tool calls have real I/O costs |

Redundant tool calls often indicate pagination or filtering issues — the agent is compensating for tools that return incomplete data. Parameter errors indicate unclear descriptions. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

**Analyze transcripts to explain the metrics.** Raw metrics identify that a problem exists; transcripts explain why. Watch for what the agent says it cannot do (capability gaps), what it omits (silence about a capability can mean it doesn't know the tool exists), its tool-selection reasoning, and where it backtracks (repeated attempts at one step signal tool-response confusion). Agents can be used to analyze their own evaluation transcripts at scale, surface patterns, and propose specific improvements to tool descriptions. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

**Iterate on targeted changes.** Common changes triggered by analysis: rewrite an unclear tool description with explicit usage criteria and what the tool is NOT for; consolidate overlapping tools (redundancy inflates tool-call count — the example below averaged 9.4 calls per task); strip fields the agent never uses from response formats; add pagination/filtering parameters so the agent narrows results rather than fetching everything. After each change, re-run the suite to confirm the targeted failure is resolved and no regressions were introduced. Diminishing returns set in when further transcript analysis produces no new change hypotheses — at that point run the held-out [golden query pairs](../verification/golden-query-pairs-regression.md) to measure generalization. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

### Tool-Building Worked Example

One iteration of the loop applied to a `search_issues` tool. The initial definition has a broad description and no filtering parameters:

```python
{
    "name": "search_issues",
    "description": "Search GitHub issues.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}
```

Running 15 multi-step tasks produces per-run metrics:

```
task                        accuracy  tool_calls  tokens  errors
find-open-auth-bugs         FAIL      11          4820    0
list-stale-issues           PASS      7           3100    0
count-issues-by-label       FAIL      14          6200    2
...
avg accuracy: 53%   avg tool_calls: 9.4   avg tokens: 4100
```

High tool-call counts on `find-open-auth-bugs` and `count-issues-by-label` signal the agent is fetching everything and discarding most of it. Transcript inspection confirms it is paginating through all issues because no `state` or `label` filter exists. The targeted change adds those filters:

```python
{
    "name": "search_issues",
    "description": "Search GitHub issues. Use 'state' to limit to open or closed issues. Use 'labels' to filter by label names. Only omit filters when you genuinely need all issues.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query":  {"type": "string"},
            "state":  {"type": "string", "enum": ["open", "closed", "all"]},
            "labels": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["query"]
    }
}
```

Re-running the same tasks after v2 shows accuracy rising to 80% and average tool calls dropping from 9.4 to 4.1 — one targeted change, measurable improvement, no regressions on previously passing tasks.

Eval-driven tool development carries its own when-this-backfires cases beyond the feature-level ones below: skip the harness for a narrow, stable tool (a thin wrapper over a well-understood API rarely justifies it — ship it and monitor real calls per the [prototype-before-optimizing](prototype-before-optimizing.md) default); treat a fixed task suite as a known floor rather than a ceiling when the eval distribution drifts from production [Source: [Eval-Driven Development of LLM Agents](https://arxiv.org/html/2411.13768v3)]; rotate tasks and weight production telemetry to avoid the suite becoming a benchmark to game [Source: [The Vulnerability of Language Model Benchmarks](https://arxiv.org/abs/2412.03597)]; and for tools already deployed behind an observable agent, real traffic often surfaces failures more cheaply than a synthetic suite.

## Common Pitfalls

**Overfitting the eval to the implementation**: if you write tasks while building the feature, you may unconsciously write tasks that match what the agent already does rather than what it should do. Write tasks based on expected behavior, not observed behavior.

**Ambiguous pass/fail criteria**: tasks where 2 experts disagree on the correct answer produce misleading aggregate pass rates. Get agreement before committing a task.

**Graders that are too strict**: exact-match verifiers reject valid alternative solutions. Use outcome-based graders (state checks, test suites) or semantic equivalence graders rather than string matching.

**Too few tasks**: 5 tasks is enough to start, but not enough to detect regression reliably. Grow the suite as edge cases are discovered.

## When This Backfires

Eval-driven development is not the right default for every situation. Write evals first when you have enough of a problem shape to define "done"; skip or defer it in these cases:

- **Early exploration of a novel problem space**: when the team genuinely does not yet know what correct behaviour looks like, committing to pass/fail criteria upfront anchors the project to metrics that may prove irrelevant. Quick manual iteration builds the understanding needed to write meaningful evals later.
- **Short-lived prototypes and spikes**: a throwaway script explored over a single afternoon does not pay back the cost of a 20-50 task suite. The eval harness is heavier than the artifact it evaluates.
- **Highly subjective outputs with shifting preferences**: when success hinges on evolving aesthetic or stylistic judgment (e.g., creative copy, UX tone) that changes faster than the eval set can be updated, the suite misleads more than it informs — tasks pass while real users dislike the output.
- **Unstable upstream dependencies**: if the tools, APIs, or data sources the agent depends on churn weekly, the eval set breaks faster than it yields signal — the same drift that destabilises [tool-building evals](#applying-the-loop-to-tool-building). Defer formal evals until the environment stabilises.

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

- [Grade Agent Outcomes, Not Execution Paths](../verification/grade-agent-outcomes.md)
- [Use the Agent Itself to Analyze Evaluation Transcripts](../verification/agent-transcript-analysis.md)
- [Eval-Driven Development: Golden Query Pairs as Regression Tests](../verification/golden-query-pairs-regression.md)
- [Test-Driven Agent Development](../verification/tdd-agent-development.md)
- [LLM-as-Judge Evaluation with Human Spot-Check Review](llm-as-judge-evaluation.md)
- [Simulation and Replay Testing for Agent Verification](simulation-replay-testing.md)
- [Failure-Driven Iteration for Improving Agent Workflows](failure-driven-iteration.md)
- [The Eval-First Development Loop](../training/eval-driven-development/eval-first-loop.md) — training module with step-by-step loop walkthrough
  - long-form
