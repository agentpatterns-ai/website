---
title: "Evaluation-Driven Development for Building Agent Tools"
description: "Build agent tools through a prototype-evaluate-analyze-iterate loop using real-world tasks, metrics, and transcript analysis to drive targeted improvements."
aliases:
  - Eval-Driven Tool Development
tags:
  - agent-design
  - testing-verification
  - workflows
---
# Evaluation-Driven Development for Agent Tools

> Build agent tools in a prototype-evaluate-analyze-iterate loop rather than optimizing in the dark.

!!! note "Also known as"
    Eval-Driven Tool Development. This applies the broader [Eval-Driven Development](eval-driven-development.md) methodology specifically to tool building. For using golden query pairs as regression tests within this workflow, see [Golden Query Pairs](../verification/golden-query-pairs-regression.md).

## The Problem

Agent tools that appear capable during demos often degrade on real tasks. The gap usually lies in untested assumptions: unclear parameter descriptions that cause wrong tool selection, overlapping tool functionality that creates ambiguity, or response formats that waste context budget on irrelevant detail.

Without evaluations, debugging is reactive: teams wait for complaints, reproduce issues manually, fix the bug, and hope nothing else regressed. [Source: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)] Systematic tool evaluation surfaces these failures before deployment. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## The Loop

```
Prototype tool → Write evaluation tasks → Run evaluations
       ↑                                          │
       └──── Analyze transcripts ←── Track metrics┘
```

Each cycle produces a concrete change hypothesis grounded in observed failures — not guesswork.

## Step 1: Write Real-World Evaluation Tasks

Effective evaluation tasks require multiple tool calls and reflect the complexity of actual use. Simplified sandbox scenarios mask problems that only appear when tools must coordinate.

Sources for good tasks:

- Real user requests the agent will face
- Known failure modes from prior sessions
- Edge cases identified during design (pagination boundaries, empty results, permission errors)

Pair each task with a verifiable expected outcome, but avoid verifiers so strict they reject valid alternative approaches. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

Hold out a test set. Running the same tasks during development and final evaluation overfits the tool design to that specific task set and masks generalization failures. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Step 2: Define Metrics Before Running

Track multiple metrics per evaluation run to triangulate problems:

| Metric | What It Signals |
|--------|-----------------|
| Accuracy | Whether the outcome is correct |
| Tool call count | Efficiency; unusually high count signals redundant or confusing tools |
| Token consumption | Cost; high consumption may indicate over-verbose tool responses |
| Tool errors | Parameter confusion, schema mismatches |
| Runtime | Latency; useful when tool calls have real I/O costs |

Redundant tool calls often indicate pagination or filtering issues — the agent is compensating for tools that return incomplete data. Parameter errors indicate unclear descriptions. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Step 3: Analyze Transcripts

Raw metrics identify that a problem exists; transcripts explain why.

When reading transcripts, pay attention to:

- What the agent says it cannot do — often reveals capability gaps
- What the agent omits — silence about a capability can indicate it doesn't know the tool exists
- Tool selection reasoning — why did the agent pick the wrong tool?
- Where the agent backtracks — repeated attempts at the same step indicate tool response confusion

Agents can be used to analyze their own evaluation transcripts at scale, surface patterns, and propose specific improvements to tool descriptions. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Step 4: Iterate on Targeted Changes

Common changes triggered by evaluation analysis:

**Unclear tool description** → Rewrite with explicit usage criteria, list what the tool is NOT for, add an example call.

**Overlapping tools** → Consolidate or add hard constraints that distinguish when each is appropriate. Redundancy is a liability: the model must resolve the ambiguity on every call.

**Poor response format** → Strip fields the agent never uses; restructure so the most decision-relevant information appears first.

**Pagination/filtering** → Add parameters that let the agent narrow results rather than fetching everything and discarding most of it.

After each change, re-run the evaluation suite to confirm the targeted failure is resolved and no regressions were introduced. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## When to Stop

Diminishing returns set in when further transcript analysis produces no new change hypotheses. Remaining failures often reveal the evaluation task itself is ambiguous or the underlying capability is out of scope for the current tool design.

At that point, run the held-out test set to measure generalization. Significant degradation on held-out tasks compared to development tasks indicates overfitting — the tool is optimized for the specific tasks you've been evaluating rather than the general capability.

## Example

The following illustrates one iteration of the prototype-evaluate-analyze-iterate loop applied to a `search_issues` tool. Metrics are captured per run; transcripts are analysed to form the next change hypothesis.

**Initial tool definition (v1)** — broad description, no filtering parameters

```python
{
    "name": "search_issues",
    "description": "Search GitHub issues.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}
```

**Evaluation run output** — metrics after running 15 multi-step tasks

```
task                        accuracy  tool_calls  tokens  errors
find-open-auth-bugs         FAIL      11          4820    0
list-stale-issues           PASS      7           3100    0
count-issues-by-label       FAIL      14          6200    2
...
avg accuracy: 53%   avg tool_calls: 9.4   avg tokens: 4100
```

High tool call counts on `find-open-auth-bugs` and `count-issues-by-label` signal the agent is fetching everything and discarding most of it. Transcript inspection confirms it is paginating through all issues because no `state` or `label` filter exists.

**Targeted change (v2)** — add filters grounded in the transcript analysis

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

## Key Takeaways

- Build evaluation tasks before optimizing tools — real-world multi-step tasks, not simplified demos
- Track accuracy, tool call count, token consumption, errors, and runtime per evaluation run
- Transcripts explain why metrics are bad; agent-assisted transcript analysis scales this step
- Each iteration targets one specific failure with a grounded hypothesis, not a broad rewrite
- Hold out a test set and only evaluate against it after development is complete

## Related

- [Eval-Driven Development: Write Evals Before Building Agent Features](eval-driven-development.md)
- [Failure-Driven Iteration](failure-driven-iteration.md)
- [LLM-as-Judge Evaluation](llm-as-judge-evaluation.md)
- [Golden Query Pairs as Continuous Regression Tests](../verification/golden-query-pairs-regression.md)
- [Grade Agent Outcomes, Not Execution Paths](../verification/grade-agent-outcomes.md)
- [Use the Agent Itself to Analyze Evaluation Transcripts](../verification/agent-transcript-analysis.md)
- [Test-Driven Agent Development](../verification/tdd-agent-development.md)
- [Verification-Centric Development](verification-centric-development.md)
- [Simulation and Replay Testing for Agent Workflows](simulation-replay-testing.md)
