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

The think tool fires between tool calls — after the agent receives a tool's output, before it decides what to do next. It gives the agent an explicit space to reflect without immediately acting.

This is distinct from extended thinking, which reasons before the first generation token. Extended thinking is pre-action; the think tool is mid-stream, firing after the agent has observed new information from the environment.

Per [Anthropic's think tool post](https://www.anthropic.com/engineering/claude-think-tool), on the [τ-Bench](https://arxiv.org/abs/2406.12045) airline domain benchmark, adding the think tool plus optimized prompting produced a **54% relative improvement** over baseline. This is a large effect for a structural change that adds no new capabilities.

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

## Why It Works

Separating observation from action-selection forces implicit state into the context as text. A model that must immediately emit the next tool call carries unverified interpretations of the previous output in the residual stream. The think call materialises those interpretations as tokens so the model can check policy constraints and evaluate candidate next steps before committing — the same mechanism as chain-of-thought prompting ([Wei et al., 2022](https://arxiv.org/abs/2201.11903)), applied at the inter-tool boundary. That is why [τ-Bench](https://arxiv.org/abs/2406.12045) airline tasks gained 54% while its retail domain — with lighter constraints — gained only 3.7%.

## Token Budget

The cost is the tokens consumed by each thought. The practical optimization is to make the tool available but not mandatory — the model self-selects when to use it. On tasks requiring frequent reflection, the accuracy gain typically justifies the cost; on tasks where reflection is rarely needed, the incidental overhead is low.

## System Prompt Requirements

The think tool alone is not sufficient. [Anthropic's post](https://www.anthropic.com/engineering/claude-think-tool) notes that the tool alone improved results, but adding domain-specific examples produced the largest gains. A generic instruction yields modest gains; a system prompt with explicit examples of what good mid-stream reasoning looks like in your domain yields large gains.

Monitor what the model writes in think calls and refine the system prompt based on quality gaps.

## Prefer Extended Thinking on Modern Claude Models

Anthropic [now recommends extended thinking](https://www.anthropic.com/engineering/claude-think-tool) over a dedicated think tool in most cases. On Claude Sonnet and Opus 4.x, adaptive thinking scales reasoning depth to the difficulty of each step and further supersedes the pattern. Reach for the think tool when extended thinking is unavailable — older model versions, API tiers without access, or deployments where mid-stream checkpoints must be inspectable as discrete tool calls rather than hidden reasoning tokens.

## When This Backfires

The think tool adds cost without benefit in several conditions:

- **Modern Claude models with native reasoning**: extended thinking and adaptive thinking subsume the think tool; a custom implementation on these models is redundant.
- **Parallel or independent tool calls**: with no accumulated context to reconcile, a think call burns tokens without changing the decision.
- **Low-constraint sequential tasks**: the 54% gain is specific to high-constraint, multi-branch domains; on τ-Bench's retail domain the gain was only 3.7%.
- **Well-defined decision trees**: when the system prompt already encodes the path, a think step can cause the model to re-examine resolved choices and inject unnecessary caveats.
- **No domain-specific prompting**: without concrete examples of good mid-stream reasoning in your domain, think output is verbose but vacuous.
- **High-frequency loops**: per-step token overhead accumulates fast and can outweigh accuracy gains on latency- or cost-sensitive pipelines.

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
- Adding the think tool plus domain-specific prompting produced a 54% relative improvement on τ-Bench airline tasks; the mechanism is explicit state materialization between observation and decision
- Anthropic now recommends extended thinking (and adaptive thinking on Claude 4.x) over the dedicated think tool in most cases; the custom tool is most useful when native reasoning is unavailable
- The tool is only invoked when the model judges reflection is needed; token cost scales with actual usage
- It adds value in sequential workflows with interdependent steps; not in independent parallel tool calls
- Domain-specific examples in the system prompt are required to realize the full performance gain
- Avoid it on simple sequential tasks, well-defined decision trees, or sub-second latency pipelines where the cost outweighs the benefit

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
