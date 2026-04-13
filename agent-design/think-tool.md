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

The mechanism: separating observation from action-selection forces implicit state into the context as text. A model that must immediately emit the next tool call carries unverified interpretations of the previous output without examining them. The think call makes those interpretations explicit, allowing the model to correct them before committing to a path.

This explains the [τ-bench](https://arxiv.org/abs/2406.12045) gains: airline tasks require checking specific policies against specific account states — exactly the class of problem where unexamined intermediate state causes downstream errors.

## Token Budget

The cost is the tokens consumed by each thought. The practical optimization is to make the tool available but not mandatory — the model self-selects when to use it. On tasks requiring frequent reflection, the accuracy gain typically justifies the cost; on tasks where reflection is rarely needed, the incidental overhead is low.

## System Prompt Requirements

The think tool alone is not sufficient. [Anthropic's post](https://www.anthropic.com/engineering/claude-think-tool) notes that the tool alone improved results, but adding domain-specific examples produced the largest gains. A generic instruction yields modest gains; a system prompt with explicit examples of what good mid-stream reasoning looks like in your domain yields large gains.

Monitor what the model writes in think calls and refine the system prompt based on quality gaps.

## Why It Works

In a standard tool-call chain, the model carries its interpretation of each tool result implicitly — encoded in the residual stream rather than as retrievable text. When the next action requires reconciling multiple constraints against a fresh observation, that implicit encoding is prone to drop or distort details.

By materializing reasoning as token text, the think tool converts implicit state into explicit context the model can attend to directly. Anthropic's research notes the tool is most effective when tool output carries *new* unanticipated information — the think call creates an explicit integration point between observation and decision. Because the model decides when to invoke it, the scratchpad only appears when the step is complex enough to warrant it.

## When This Backfires

The think tool adds cost without benefit in several conditions:

- **Low-constraint sequential tasks**: The 54% gain is specific to high-constraint, multi-branch domains — on τ-Bench's retail domain, the gain was only 3.7%. When each tool output has an obvious follow-up, the model invoking think adds latency with no accuracy benefit.
- **Well-defined decision trees**: When the system prompt already encodes the decision tree precisely, the think step can cause the model to re-examine resolved choices and introduce unnecessary caveats.
- **Strong default behaviour**: Per [Anthropic's post](https://www.anthropic.com/engineering/claude-think-tool), "when there are not many constraints to which Claude needs to adhere, and its default behaviour is good enough, there are unlikely to be gains."
- **Sub-second latency pipelines**: Each think call adds output tokens and increases p99 latency; the overhead may outweigh accuracy gains on time-sensitive pipelines.

## When This Backfires

Anthropic [now recommends extended thinking](https://www.anthropic.com/engineering/claude-think-tool) over a dedicated think tool in most cases — extended thinking provides more comprehensive reasoning and is better integrated into current Claude models. Use the think tool when you cannot enable extended thinking (budget constraints, API tier, model version).

Conditions that reduce or eliminate the value:

1. **Native reasoning enabled** — extended thinking or adaptive thinking subsumes what the think tool provides.
2. **Parallel or independent tool calls** — no accumulated context to reflect on between unrelated calls.
3. **Simple, predictable tasks** — when the next step is obvious, forced reflection wastes tokens.
4. **No domain-specific prompting** — without concrete examples, the model invokes the tool infrequently and gains are modest.

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

## Why It Works

Serializing reasoning into an explicit scratchpad forces the model to commit intermediate state to tokens rather than encoding it implicitly in the residual stream between generation steps. Once a plan or observation is written out, subsequent tokens attend to it directly — making it harder to silently abandon a constraint or forget a key fact from earlier in the tool chain. This is the same mechanism behind chain-of-thought prompting ([Wei et al., 2022](https://arxiv.org/abs/2201.11903)), applied at the inter-tool boundary rather than within a single prompt.

For sequential tool chains, each tool call introduces new facts that may invalidate earlier assumptions. The think call gives the model a structured moment to reconcile new evidence with its prior plan before acting — a form of explicit belief revision that the default autoregressive generation step does not guarantee.

## When This Backfires

The think tool adds overhead and is not universally beneficial:

- **Independent parallel tool calls**: When tool calls do not depend on each other's outputs, there is no information to reconcile between them. A think call here burns tokens without changing the decision.
- **High-frequency, low-stakes steps**: In tight loops where each iteration is routine (e.g., processing identical file chunks), the model will invoke the think tool rarely on its own — but if prompting forces it, the fixed overhead per step adds up quickly.
- **Overly permissive system prompts**: Without concrete examples of what good mid-stream reasoning looks like in your domain, the think tool can produce verbose but vacuous thoughts that consume context without improving accuracy. The τ-bench results required domain-specific prompting; [Anthropic notes](https://www.anthropic.com/engineering/claude-think-tool) that generic "reason carefully" instructions yield modest gains.
- **Models already producing cautious outputs**: On tasks where the model already hedges extensively before acting, an additional scratchpad step can amplify over-hedging, leading to refusals or conservative actions that under-deliver.

## Key Takeaways

- The think tool is mid-stream reasoning after tool output — distinct from extended thinking (pre-generation)
- Adding the think tool plus domain-specific prompting produced a 54% relative improvement on τ-Bench airline tasks; the mechanism is explicit state materialization between observation and decision
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
