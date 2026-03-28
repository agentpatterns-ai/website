---
title: "The Think Tool: Mid-Stream Reasoning for AI Agents"
description: "Give agents a dedicated mid-stream reasoning step after receiving tool outputs so they can re-evaluate their plan before taking the next action."
tags:
  - agent-design
  - workflows
aliases:
  - reasoning checkpoint
  - mid-stream reasoning
---

# The Think Tool

> The think tool is a mid-stream reasoning checkpoint that fires between tool calls, giving agents an explicit space to reflect on tool output before deciding the next action.

## What the Think Tool Does

The think tool is a structured reasoning checkpoint that fires between tool calls — after the agent receives a tool's output, before the agent decides what to do next. It gives the agent an explicit space to reflect without immediately acting.

This is distinct from extended thinking, which reasons before the first generation token. Extended thinking is pre-action; the think tool is mid-stream, occurring after the agent has observed new information from the environment.

Per [Anthropic's think tool post](https://www.anthropic.com/engineering/claude-think-tool), on the τ-Bench airline domain benchmark, adding the think tool plus optimized prompting produced a **54% relative improvement** over baseline. This is a large effect for a structural change that adds no new capabilities.

## When It Helps

The think tool adds value specifically in sequential workflows where each step depends on the output of the previous one:

- After receiving tool output that may change the plan (e.g., discovering a file doesn't exist, or a test fails for an unexpected reason)
- Before a branching decision where different tool outputs require different next steps
- When policy compliance needs explicit checking against what the tool returned
- When multiple constraints must be reconciled before acting

It does not help when tool calls are independent and parallel — there is nothing to reflect on between independent calls. See the anti-pattern on reasoning overuse.

## How It Works

The think tool is invoked by the agent as a regular tool call. The agent writes out its reasoning as the "thought" — it is not shown to the user, but it is included in the model's context. The model can then use that reasoning when formulating the next action.

Critically, the tool only fires when the model chooses to use it. If the task is simple or the next step is obvious from the tool output, the model skips it. Token overhead is proportional to how often the model judges reflection is needed.

## Token Budget

The think tool's cost is the tokens consumed by the thought text. For tasks where reflection is needed frequently, this can be substantial. The practical optimization is to make sure the tool is available but not mandatory — the model self-selects when to use it. For tasks where nearly every step requires careful reflection, the 54% improvement in accuracy may justify the token cost; for tasks where reflection is rarely needed, the incidental cost is low.

## System Prompt Requirements

The think tool alone is not sufficient. [Anthropic's post](https://www.anthropic.com/engineering/claude-think-tool) notes that domain-specific prompting with concrete examples significantly improves results. The think tool alone improved results even without prompting, but adding domain-specific examples produced the largest gains. A generic "use the think tool to reason carefully" instruction yields modest gains; a system prompt with explicit examples of what good mid-stream reasoning looks like in your domain yields large gains.

The reasoning the agent produces should be monitored in production: observe what the model actually writes in think calls and refine the system prompt based on quality gaps.

## Example

The following tool definition adds the think tool to a Claude API request alongside a domain-specific Bash tool. The system prompt instructs the agent to use it at the right moment.

```python
tools = [
    {
        "name": "think",
        "description": (
            "Use this tool to reason about what you just observed before deciding "
            "your next action. Call it after receiving unexpected tool output, "
            "before choosing between multiple possible next steps, or when you need "
            "to check whether a policy constraint applies to the current situation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Your reasoning about the current situation."
                }
            },
            "required": ["thought"]
        }
    },
    {
        "name": "bash",
        "description": "Run a shell command and return stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"]
        }
    }
]
```

The system prompt pairs with the tool to guide when reflection is valuable:

```
After each bash result, call the think tool if:
- the output differs from what you expected
- you need to choose between two or more possible next commands
- you must verify a constraint before proceeding (e.g., confirming no destructive operation)
```

Without this prompt guidance, the model may invoke `think` too rarely on novel outputs. The tool definition and the system prompt together reproduce the conditions under which Anthropic observed the 54% benchmark improvement.

## Key Takeaways

- The think tool is mid-stream reasoning after tool output — distinct from extended thinking (pre-generation)
- Adding the think tool plus domain-specific prompting produced a 54% relative improvement on τ-Bench airline tasks
- The tool is only invoked when the model judges reflection is needed; token cost scales with actual usage
- It adds value in sequential workflows with interdependent steps; not in independent parallel tool calls
- Domain-specific examples in the system prompt are required to realize the full performance gain

## Related

- [Reasoning Budget Allocation](reasoning-budget-allocation.md)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md)
- [Domain-Specific System Prompts](../instructions/domain-specific-system-prompts.md)
- [Know When Not to Add Structured Reasoning](../anti-patterns/reasoning-overuse.md)
- [The Plan-First Loop: Design Before Code](../workflows/plan-first-loop.md)
- [Three Reasoning Spaces](three-reasoning-spaces.md)
- [Cognitive Reasoning vs Execution](cognitive-reasoning-execution-separation.md)
- [Controlling Agent Output](controlling-agent-output.md)
- [Rollback-First Design](rollback-first-design.md)
