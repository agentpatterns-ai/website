---
title: "Using the Agent to Analyze Its Own Evaluation Transcripts"
description: "Feed evaluation transcripts back to the agent and have it identify tool design issues, propose description improvements, and surface failure patterns that manual review misses at scale."
tags:
  - agent-design
  - testing-verification
  - workflows
  - observability
---
# Using the Agent to Analyze Its Own Evaluation Transcripts

> Agent transcript analysis uses the agent itself to review its own evaluation transcripts — identifying tool selection errors, description ambiguities, and cross-transcript failure patterns that manual review misses at scale.

## The Manual Review Problem

After running evaluation tasks, someone must read the transcripts and identify what went wrong. Manual review is slow and inconsistent — humans miss patterns that span dozens of transcripts and tend to focus on the most recent failure rather than the most common one.

The same agent you are building tools for can perform this analysis at scale. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## What the Agent Is Good at Here

Agents analyzing transcripts tend to surface:

- Tool selection errors and their apparent causes
- Redundant or overlapping tool calls indicating ambiguity in tool descriptions
- Response format problems — fields that are never used, or structured data that forces unnecessary parsing
- Patterns of confusion repeated across multiple tasks that look different on the surface

Agents are also effective at making consistent changes across multiple tool definitions at once — something humans do unevenly when editing several related descriptions in one pass. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

The mechanism: when all transcripts and tool definitions sit in a single context window, the agent applies one criterion uniformly across every instance — without the recency bias and inconsistent framing that accumulate when a human reads transcripts sequentially.

## Setup

**What to provide:**

- A batch of evaluation transcripts (5-20 is useful; more can be summarized first)
- The current tool definitions (name, description, parameters)
- A description of what the agent was trying to accomplish in each task

**What to ask for:**

- Patterns of failure across transcripts
- Specific tool descriptions that appear to have caused confusion
- Concrete proposed rewrites, not just observations
- Whether any tools should be consolidated, split, or removed

**Instruction to trigger deeper analysis:**
Ask the agent to output its reasoning before each proposed change. Anthropic's tool guidance recommends reasoning blocks before tool calls — the same principle here separates diagnosis from prescription. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Interpreting the Output

Treat proposed changes as hypotheses, not conclusions — the agent is good at pattern recognition but may fix the observed failure while introducing a new one.

Before applying a proposed change:

1. Verify it addresses the root cause identified in the transcript, not just the symptom
2. Consider whether it could break correctly-functioning cases
3. Prefer targeted edits over broad rewrites — smaller diffs are easier to evaluate

After applying changes, re-run the eval suite to confirm the targeted failure is resolved and no regressions appear.

## Combined Human and Agent Review

Neither approach alone is enough. Human reviewers catch issues that require domain context and judgment about intended behavior; agents apply consistent criteria across large transcript volumes without attention fatigue. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

A practical split: run agent analysis first to identify the top 3-5 issue classes, then focus human review on root causes and whether the agent's proposed fixes are sound.

## Avoiding Overfitting

After agent-assisted refinement, run a held-out test set before declaring the tool improved. Changes that fix development-task transcripts can overfit to those inputs; a held-out set reveals whether improvements generalize. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Example

The following prompt feeds a batch of evaluation transcripts and the current tool definitions to an agent, asking for structured analysis before any proposed changes.

```python
import anthropic
import json

client = anthropic.Anthropic()

transcripts = open("eval_transcripts.json").read()
tool_definitions = open("tools.json").read()

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    system=(
        "You are a tool design analyst. When reviewing transcripts, "
        "output your reasoning before each proposed change."
    ),
    messages=[{
        "role": "user",
        "content": (
            f"Here are 12 evaluation transcripts:\n\n{transcripts}\n\n"
            f"Here are the current tool definitions:\n\n{tool_definitions}\n\n"
            "Identify patterns of failure across transcripts. "
            "For each pattern: (1) cite the transcript IDs where it appears, "
            "(2) identify the specific tool description causing confusion, "
            "(3) reason through the root cause, then "
            "(4) propose a concrete rewrite of the description."
        )
    }]
)

print(response.content[0].text)
```

The key instruction is to reason through the root cause before proposing a rewrite. This separates diagnosis from prescription and makes it easier to evaluate whether the proposed change actually addresses the underlying issue. After applying any changes, re-run the eval suite against a held-out test set before treating the tool as improved.

## Key Takeaways

- Agents can analyze their own evaluation transcripts and surface tool design issues at scale
- Ask for reasoning before each proposed change to trigger deeper analysis
- Use agent analysis to identify issue classes; use human review to validate root cause and proposed fixes
- Apply changes as targeted hypotheses, then re-run evaluations to confirm resolution and check for regressions
- Validate improvements against a held-out test set to avoid overfitting to development transcripts

## When This Backfires

Agents miss by omission as much as by commission — the Anthropic engineering team notes that "what agents omit in their feedback and responses can often be more important than what they include." An agent that confidently lists five issue classes may silently skip a sixth that is harder to articulate.

Agent-proposed fixes can overfit to the surface of a failure rather than its root cause. A description rewrite may resolve the visible symptom while introducing a subtler ambiguity that only surfaces on task types not covered by your eval set — which is why re-running a held-out test set after changes is not optional.

When the same model both generates and reviews, self-preference bias compounds the problem: judges mark their own outputs as satisfying rubrics up to 50% more often than a neutral evaluator would, even on objectively verifiable criteria. [Source: [Self-Preference Bias in Rubric-Based Evaluation](https://arxiv.org/abs/2604.06996)] Cross-check proposed fixes with a different model family.

Do not rely on agent analysis as the sole quality gate. Use it to narrow the search space for human review, not to replace the judgment needed to validate fixes.

## Related

- [Evaluation-Driven Development for Agent Tools](../workflows/eval-driven-tool-development.md)
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Test-Driven Agent Development: Tests as Spec and Guardrail](tdd-agent-development.md)
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md)
- [Introspective Skill Generation](../workflows/introspective-skill-generation.md)
- [Incident-to-Eval Synthesis: Converting Production Failures into Regression Evals](incident-to-eval-synthesis.md)
- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md)
- [Trajectory-Opaque Evaluation Gap: Why Final-Output Grading Misses Safety Violations](trajectory-opaque-evaluation-gap.md)
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
