---
title: "Using the Agent to Analyze Its Own Evaluation Transcripts"
description: "Feed evaluation transcripts back to the agent and have it identify tool design issues, propose description improvements, and surface failure patterns that manual review misses at scale."
term: "Agent Transcript Analysis"
tags:
  - agent-design
  - testing-verification
  - workflows
  - observability
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: adopted
---

# Using the Agent to Analyze Its Own Evaluation Transcripts

> Feeding evaluation transcripts back to the agent surfaces tool-selection errors, description ambiguities, and cross-transcript failure patterns that manual review misses at scale.

Learn it hands-on with [Gates That Catch Regressions](https://learn.agentpatterns.ai/observability/gates-that-catch-regressions/), a guided lesson with quizzes.

## The manual review problem

Manual transcript review is slow and inconsistent. After running evaluation tasks, someone has to read the transcripts and work out what went wrong. People miss patterns that span dozens of transcripts. They also tend to focus on the most recent failure rather than the most common one.

The same agent you are building tools for can do this analysis at scale. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## What the agent is good at here

Agents analyzing transcripts tend to surface:

- Tool selection errors and their apparent causes
- Redundant or overlapping tool calls indicating ambiguity in tool descriptions
- Response format problems — fields that are never used, or structured data that forces unnecessary parsing
- Patterns of confusion repeated across multiple tasks that look different on the surface

Agents are also good at making consistent changes across many tool definitions at once. People do this unevenly when they edit several related descriptions in one pass. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

Here is why it works. When all the transcripts and tool definitions sit in a single context window, the agent applies one criterion to every instance. It avoids the recency bias and inconsistent framing that build up when a person reads transcripts one after another.

## Setup

What to provide:

- A batch of evaluation transcripts (5 to 20 is useful; summarize more first)
- The current tool definitions (name, description, parameters)
- A description of what the agent was trying to do in each task

What to ask for:

- Patterns of failure across transcripts
- Specific tool descriptions that appear to have caused confusion
- Concrete proposed rewrites, not just observations
- Whether any tools should be merged, split, or removed

What to ask for to trigger deeper analysis: tell the agent to output its reasoning before each proposed change. Anthropic's tool guidance recommends reasoning blocks before tool calls, and the same principle here separates diagnosis from prescription. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

## Interpreting the output

Treat proposed changes as hypotheses, not conclusions. The agent is good at pattern recognition, but it may fix the observed failure while introducing a new one.

Before you apply a proposed change:

1. Verify it addresses the root cause identified in the transcript, not just the symptom.
2. Consider whether it could break cases that work correctly today.
3. Prefer targeted edits over broad rewrites, because smaller diffs are easier to evaluate.

After you apply changes, re-run the eval suite. Confirm the targeted failure is resolved and no regressions appear.

## Combined human and agent review

Neither approach alone is enough. Human reviewers catch issues that need domain context and judgment about intended behavior. Agents apply consistent criteria across large transcript volumes without attention fatigue. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

A practical split works well. Run agent analysis first to find the top 3 to 5 issue classes. Then focus human review on root causes and on whether the agent's proposed fixes are sound.

## Avoiding overfitting

Run a held-out test set before you declare the tool improved. Changes that fix development-task transcripts can overfit to those inputs. A held-out set shows whether the improvements generalize. [Source: [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)]

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

The key instruction is to reason through the root cause before proposing a rewrite. This separates diagnosis from prescription. It also makes it easier to judge whether the proposed change addresses the underlying issue. After you apply any changes, re-run the eval suite against a [held-out test set](eval-blind-spots.md) before you treat the tool as improved.

## Key Takeaways

- Agents can analyze their own evaluation transcripts and surface tool design issues at scale
- Ask for reasoning before each proposed change to trigger deeper analysis
- Use agent analysis to identify issue classes; use human review to validate root cause and proposed fixes
- Apply changes as targeted hypotheses, then re-run evaluations to confirm resolution and check for regressions
- Validate improvements against a held-out test set to avoid overfitting to development transcripts

## When this backfires

Agents miss by omission as much as by commission. The Anthropic engineering team notes that "what agents omit in their feedback and responses can often be more important than what they include." An agent that confidently lists five issue classes may quietly skip a sixth that is harder to put into words.

Agent-proposed fixes can overfit to the surface of a failure rather than its root cause. A description rewrite may resolve the visible symptom while introducing a subtler ambiguity. That ambiguity only surfaces on task types your eval set does not cover. This is why re-running a [held-out test set after changes](eval-blind-spots.md) is not optional.

When the same model both generates and reviews, self-preference bias makes the problem worse. Judges mark their own outputs as satisfying rubrics up to 50% more often than a neutral evaluator would, even on objectively verifiable criteria. [Source: [Self-Preference Bias in Rubric-Based Evaluation](https://arxiv.org/abs/2604.06996v3)] Cross-check proposed fixes with a different model family.

Do not rely on agent analysis as the only quality gate. Use it to narrow the search space for human review, not to replace the judgment needed to validate fixes.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Introspective Skill Generation](../workflows/introspective-skill-generation.md)
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md)
- [Trajectory-Opaque Evaluation Gap: Why Final-Output Grading Misses Safety Violations](eval-blind-spots.md)
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
