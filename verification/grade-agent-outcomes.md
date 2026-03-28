---
title: "Grade Agent Outcomes, Not Execution Paths"
description: "Evaluate agents by the final state they produce, not the sequence of steps they took to get there. Path-based evals penalize valid alternative solutions."
tags:
  - agent-design
  - testing-verification
  - evals
---

# Grade Agent Outcomes, Not Execution Paths

> Evaluate agents by the final state they produce, not the sequence of steps they took to get there.

## The Problem with Path-Based Grading

Path-based evals check that an agent called tool X before tool Y, or edited file A before file B. This approach penalizes agents that find valid alternative solutions — a refactored approach, a different API call order, a more efficient sequence the eval author didn't anticipate.

Frontier models regularly discover solutions their authors didn't expect. Checking for a specific path marks these as failures and produces misleading results, making agents appear worse than they are. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)] [unverified]

## Outcome Grading

Outcome grading asks: "Is the system in the correct state?" rather than "Did the agent follow the expected procedure?"

For coding agents, the most reliable outcome graders are deterministic tests — they are objective, fast, and path-agnostic. A passing test suite is a correct outcome regardless of whether the agent took two steps or twenty.

Examples of outcome-based checks:

- Unit tests pass after the agent's code changes
- The database schema matches the expected state
- The API response contains the expected fields
- The file was created with the correct content

## Handling Subjective Outcomes

Not all outcomes are deterministic. When correctness involves code quality, readability, or style, combine outcome checks with LLM rubric graders. Specify the criteria (e.g., "follows team conventions," "avoids global state") and have a model evaluate the result against them — rather than prescribing the steps the agent must take to achieve it. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## Common Grading Bugs

Over-specification causes false negatives. Common examples:

- Exact string matching on numeric output that can legitimately be formatted different ways
- Checking for a specific function name when any functionally equivalent name is correct
- Asserting a particular import order or comment placement
- Requiring one file to be modified when the agent correctly refactored across multiple files

These bugs embed the eval author's implementation assumptions into the definition of correct, which narrows the agent's effective solution space and distorts evaluation results. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

## Example

The contrast below shows a path-based grader that produces false negatives versus an outcome-based grader that accepts any correct solution. Both evaluate an agent tasked with writing a function that returns unique sorted values from a list.

**Path-based grader (fragile — fails valid solutions)**

```python
def grade_path_based(agent_trace: list[dict]) -> bool:
    """Fails if the agent didn't call the tools in the expected order."""
    tool_calls = [step["tool"] for step in agent_trace if "tool" in step]
    # Assumes the agent must: read file → write function → run tests
    expected_sequence = ["read_file", "write_file", "bash"]
    return tool_calls == expected_sequence
```

This grader rejects an agent that reads multiple files first, or that runs the tests before finalising the file, even if the final result is correct.

**Outcome-based grader (robust — accepts any correct implementation)**

```python
import subprocess, textwrap

def grade_outcome(repo_path: str) -> dict:
    """Run the test suite; pass if all tests pass regardless of how the agent got there."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_unique_sorted.py", "-q"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    passed = result.returncode == 0
    return {"passed": passed, "output": result.stdout + result.stderr}

# For subjective quality, add an LLM rubric grader alongside the test result:
def grade_code_quality(file_contents: str) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": (
                f"Rate this Python function on a scale of 1-5 for readability "
                f"and adherence to PEP 8. Respond with JSON: {{\"score\": <int>, \"reason\": \"<str>\"}}.\n\n"
                f"```python\n{file_contents}\n```"
            ),
        }],
    )
    return response.content[0].text
```

`grade_outcome` passes as long as the test suite is green — the agent may have taken two tool calls or twenty. The optional `grade_code_quality` function uses an LLM rubric to handle the subjective dimension without prescribing implementation steps.

## Key Takeaways

- Grade the final environment state or test results, not the sequence of tool calls
- Deterministic unit tests are the most reliable outcome graders for coding agents
- Combine outcome checks with LLM rubric graders for subjective quality criteria
- Exact-match verifiers for format-sensitive fields are a common source of false negatives
- Path-based grading discourages valid alternative solutions and produces misleading metrics

## Unverified Claims

- Frontier models regularly discover solutions their eval authors didn't expect, making path-based grading misleading [unverified]

## Related

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md)
- [Use the Agent Itself to Analyze Evaluation Transcripts](agent-transcript-analysis.md)
- [Incremental Verification](incremental-verification.md)
