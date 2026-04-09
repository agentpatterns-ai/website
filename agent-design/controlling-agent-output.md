---
title: "Controlling Agent Output: Concise Answers, Not Essays"
description: "Matching the agent's response format to what you actually need reduces noise and preserves context budget. Set output mode once in system instructions."
tags:
  - instructions
---

# Controlling Agent Output: Concise Answers, Not Essays

> Matching the agent's response format to what you actually need reduces noise and preserves context budget.

## The Default Problem

Agents default to verbose, explanatory output. Ask for a function and receive the function plus several paragraphs of context, rationale, and caveats. For experienced developers, this is friction: you already know the context. The explanation consumes tokens that could be used for more work.

Output control is not about suppressing capability — it's about directing the response format to match the task.

## Output Modes

Different tasks call for different formats:

| Mode | When to Use |
|---|---|
| Code only | Implementation tasks where you'll review the diff |
| Concise | Quick questions, status checks, short answers |
| Structured (JSON/table) | Reviewable data: audits, test results, comparisons |
| Diff only | Refactoring where context is already loaded |
| Verbose | Debugging, architecture decisions, unfamiliar domains |

## System-Level Instructions

Output mode preferences belong in system instructions, not per-prompt requests. Setting them once removes the need to repeat them:

```
Be concise. Provide code without explanation unless asked.
For review tasks, return structured JSON: {verdict, issues, notes}.
```

The instruction "just do it" — implementing without narrating — is effective for experienced developers who treat the agent as a capable peer rather than a teaching assistant.

## Structured Output

For tasks requiring human review, structured output outperforms prose. A review result as JSON:

```json
{
  "verdict": "FAIL",
  "issues": [
    {"severity": "high", "file": "auth.ts", "description": "...", "fix": "..."}
  ]
}
```

...is faster to parse and easier to feed to downstream steps than free-form paragraphs. Defining the schema in a skill or system instruction ensures consistent structure across invocations.

## Context Cost

Verbose output is not free. Each paragraph of explanation the agent writes is context that cannot be used for analysis, tool calls, or follow-up reasoning. In long-running sessions or multi-agent pipelines, output verbosity compounds: one agent's lengthy response becomes another's bloated input [unverified].

## Templates in Skills

Placing output format templates in skills constrains verbosity structurally. An agent loading a skill that defines a fixed output schema will produce output in that shape without needing a per-prompt instruction. This is more reliable than relying on natural language instructions to hold format across a long session [unverified].

## The Anti-Pattern

The anti-pattern is the three-act response: the agent explains what it's about to do, does it, then explains what it did. This triples the token cost of any action [unverified]. A system instruction like "act without announcing your actions" eliminates it.

## Example

A system prompt that enforces concise output for an implementation agent:

```
You are a coding assistant. Be concise.
- For implementation tasks: return code only, no explanation.
- For review tasks: return structured JSON — { verdict, issues, notes }.
- Do not announce what you are about to do. Act, then stop.
```

Verbose equivalent (anti-pattern):

```
I'll now implement the function you requested. Here's how I'll approach it:
[3 paragraphs of rationale]

[code]

I've implemented the function above. It handles the edge cases by...
[2 paragraphs of explanation]
```

The concise version cuts token cost by roughly two-thirds for the same deliverable [unverified].

## Key Takeaways

- Set output mode in system instructions once, not per prompt
- Prefer structured output (JSON, tables) over prose for any result that needs review or downstream processing
- Verbose output consumes [context budget](../context-engineering/context-budget-allocation.md); in agentic pipelines this compounds across steps
- Use output templates in skills to enforce format structurally rather than through natural language instructions

## Unverified Claims

- In multi-agent pipelines, output verbosity compounds: one agent's lengthy response becomes another's bloated input [unverified]
- Output format templates in skills are more reliable than natural language instructions for holding format across a long session [unverified]

## Related

- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [Negative Space Instructions: What NOT to Do](../instructions/negative-space-instructions.md)
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](../instructions/instruction-compliance-ceiling.md)
- [Evaluator-Optimizer](evaluator-optimizer.md)
- [Agent Turn Model](agent-turn-model.md)
- [Think Tool](think-tool.md)
- [Agent Memory Patterns](agent-memory-patterns.md)
- [Agent-First Software Design](agent-first-software-design.md)
- [Prompt Engineering](../training/foundations/prompt-engineering.md)
- [Progressive Disclosure for Layered Agent Definitions](progressive-disclosure-agents.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Harness Engineering](harness-engineering.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
