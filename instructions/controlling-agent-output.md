---
title: "Controlling Agent Output: Concise Answers, Not Essays"
term: "Controlling Agent Output"
description: "Matching the agent's response format to what you actually need reduces noise and preserves context budget. Set output mode once in system instructions."
tags:
  - instructions
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# Controlling Agent Output: Concise Answers, Not Essays

> Matching the agent's response format to what you actually need reduces noise and preserves context budget.

## The default problem

Agents default to verbose, explanatory output. Ask for a function and you get the function plus several paragraphs of context, rationale, and caveats. For experienced developers, this is friction: you already know the context. The explanation spends tokens you could put toward more work — a direct draw on the [context budget](../context-engineering/context-budget-allocation.md).

Output control does not suppress capability. It directs the response format to match the task.

## Output modes

Different tasks call for different formats:

| Mode | When to use |
|---|---|
| Code only | Implementation tasks where you'll review the diff |
| Concise | Quick questions, status checks, short answers |
| Structured (JSON/table) | Reviewable data: audits, test results, comparisons |
| Diff only | Refactoring where context is already loaded |
| Verbose | Debugging, architecture decisions, unfamiliar domains |

## System-level instructions

Output mode preferences belong in system instructions, not per-prompt requests. Set them once and you do not have to repeat them:

```
Be concise. Provide code without explanation unless asked.
For review tasks, return structured JSON: {verdict, issues, notes}.
```

The instruction "just do it" — implement without narrating — works well for experienced developers who treat the agent as a capable peer rather than a teaching assistant.

## Structured output

For tasks that need human review, structured output beats prose. A review result as JSON:

```json
{
  "verdict": "FAIL",
  "issues": [
    {"severity": "high", "file": "auth.ts", "description": "...", "fix": "..."}
  ]
}
```

...is faster to parse and easier to feed to downstream steps than free-form paragraphs. A schema defined in a skill or system instruction keeps the structure consistent across invocations.

## Context cost

Verbose output is not free. Each paragraph of explanation the agent writes is context you cannot use for analysis, tool calls, or follow-up reasoning. The cost is multiplicative: LLM APIs bill for the entire conversation history on every call, so in a multi-step agent loop, context accumulates at O(N²) — a 20-step loop where each step generates 1,000 tokens produces roughly 210,000 cumulative input tokens rather than the 20,000 a per-step estimate would suggest ([Augment Code, 2025](https://www.augmentcode.com/guides/ai-agent-loop-token-cost-context-constraints)). In multi-agent pipelines, verbosity compounds further: one agent's long response becomes every downstream agent's bloated input.

## Templates in skills

Output format templates in skills constrain verbosity structurally. An agent that loads a skill defining a fixed output schema produces output in that shape without a per-prompt instruction. Provider-level structured output support (available in Anthropic, OpenAI, and Gemini APIs) enforces schema compliance at the API level — production experience shows natural language format instructions break when models update and silently rename fields like `status` to `current_state`, while schema-enforced outputs stay consistent across invocations ([agenta.ai, 2025](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)).

## The anti-pattern

The anti-pattern is the three-act response: the agent explains what it is about to do, does it, then explains what it did. This triples the token cost of any action. A system instruction like "act without announcing your actions" removes it.

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

The concise version cuts token cost by roughly two-thirds for the same deliverable.

## When this backfires

Concise-output mode is wrong in three situations:

- Debugging unfamiliar failures: verbose chain-of-thought traces are the main diagnostic surface. Suppress them and the agent silently makes wrong decisions without leaving reasoning evidence.
- Architecture and design decisions: when the problem is underspecified, the agent's narrative explanation surfaces hidden assumptions — the same signal [interactive clarification](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) elicits by asking. Asking for code-only output removes the only signal that the agent misunderstood the requirement.
- First pass in new domains: a practitioner expert in Python but new to Rust needs the caveats. Concise mode assumes shared context that does not yet exist.

Set output mode per task category in system instructions, not as a global default.

## Key Takeaways

- Set output mode in system instructions once, not per prompt
- Prefer structured output (JSON, tables) over prose for any result that needs review or downstream processing
- Verbose output consumes [context budget](../context-engineering/context-budget-allocation.md); in agentic pipelines this compounds at O(N²) across steps
- Use output templates in skills to enforce format structurally — provider-level structured output support is more reliable than natural language instructions

## Related

- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](instruction-compliance-ceiling.md)
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Agent Turn Model](../patterns/agent-design/agent-turn-model.md)
- [Think Tool](../patterns/agent-design/think-tool.md)
- [Progressive Disclosure for Layered Agent Definitions](../patterns/agent-design/progressive-disclosure-agents.md)
- [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md)
