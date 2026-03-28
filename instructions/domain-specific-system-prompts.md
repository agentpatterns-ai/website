---
title: "Domain-Specific System Prompts with Concrete Examples"
description: "Domain-Specific Personas, Domain-Specific System Prompts. For replacing the default system prompt entirely with a domain-specific identity, see System Prompt"
aliases:
  - Domain-Specific Personas
  - Domain-Specific System Prompts
tags:
  - agent-design
  - instructions
---

# Domain-Specific System Prompts with Concrete Examples

> Generic instructions produce mediocre reasoning. Domain-specific system prompts with worked examples produce consistent, high-quality agent behavior in your specific context.

!!! note "Also known as"
    Domain-Specific Personas, Domain-Specific System Prompts. For replacing the default system prompt entirely with a domain-specific identity, see [System Prompt Replacement](system-prompt-replacement.md).

## The Gap Between Generic and Domain-Specific

A generic instruction like "reason carefully before acting" gives the model no information about what good reasoning looks like in your domain. It has no worked examples, no domain vocabulary, and no model of what edge cases matter. The result is reasoning that looks thoughtful but misses the specific failures you care about.

[Anthropic's think tool post](https://www.anthropic.com/engineering/claude-think-tool) documents this gap quantitatively: on the τ-Bench airline domain, switching from a baseline prompt to one with detailed domain-specific guidance and examples produced a **54% relative improvement** in task pass rate. The model and tools were identical; only the prompt changed.

## What "Domain-Specific" Means

A domain-specific system prompt includes:

- **Domain vocabulary** — the specific terms, resource types, and relationships that exist in your system, not generic descriptions
- **Worked examples of reasoning** — concrete sequences showing what good thinking looks like for cases the agent handles, including edge cases
- **Explicit edge case guidance** — what to do when inputs are ambiguous, when resources are missing, when multiple valid paths exist
- **Success and failure definitions** — what a correct outcome looks like, stated specifically enough that the agent can self-check

Abstract rules ("be careful with edge cases") are harder to apply than concrete examples ("when the requested flight is full, check for connecting routes before returning no availability").

## Where Examples Belong

Complex guidance belongs in the system prompt, not in tool descriptions. Tool descriptions answer "what does this tool do?"; the system prompt answers "how should you reason about this domain?". The model integrates system prompt content more broadly — it applies across all reasoning steps, not just at tool selection time.

Per [Anthropic's post](https://www.anthropic.com/engineering/claude-think-tool), complex guidance in tool descriptions is fragmented; the same content in the system prompt produces more consistent application.

## Writing Effective Examples

Effective examples in a system prompt:

1. Describe a scenario that represents a real edge case — not the happy path the agent already handles
2. Show the reasoning chain explicitly — what the agent should consider, in what order
3. Show the correct action at the end — grounded in the reasoning shown

The examples should come from your actual domain. Invented examples based on imagined cases miss the real failure patterns. Instrument your agent in production, observe where reasoning fails, and write examples for those cases.

## Iterative Refinement

[Prompt engineering](../training/foundations/prompt-engineering.md) for domain-specific reasoning is iterative:

1. Deploy the agent and log the think-tool output (or reasoning trace)
2. Identify cases where reasoning quality is low or reasoning reaches wrong conclusions
3. Write examples that demonstrate correct reasoning for those cases
4. Add examples to the system prompt
5. Measure improvement via benchmark or targeted eval
6. Repeat

This is not a one-time effort. As the agent encounters new cases and as the domain evolves, the example set needs maintenance.

## Example

The following shows the difference between a generic instruction and a domain-specific example for a support agent handling subscription billing. The generic version gives the model no information about what correct reasoning looks like; the domain-specific version shows the exact reasoning chain for a real edge case.

**Generic (before):**

```text
You are a helpful customer support agent. Reason carefully before taking action.
If a customer asks about their subscription, check the relevant account details.
```

**Domain-specific (after):**

```text
You are a billing support agent for Acme SaaS. You handle subscription changes,
refund requests, and payment failures.

When a customer reports a failed payment:
1. Check `get_subscription_status` first — if status is `past_due`, the payment
   processor has already retried at least once. Do NOT tell the customer "we'll
   retry soon"; retry attempts are exhausted at this point.
2. Check `get_payment_method` — if the card is expired, direct the customer to
   update it via the billing portal before taking any other action.
3. If the card is valid but the charge failed, call `get_payment_failure_reason`.
   A `insufficient_funds` reason requires a different script than `do_not_honor`.
4. Only offer a manual retry via `retry_payment` after confirming the card is
   current and the failure reason is transient (not `card_permanently_declined`).

Incorrect action: offering a retry when the card is expired wastes the customer's
time and creates a second failure event in the payment processor logs.
```

The after version encodes the tool call sequence, the conditions that gate each step, and why the wrong path causes a real problem. This is the pattern that produced a 54% relative improvement on τ-Bench: not a smarter model, but a prompt that shows the model what correct domain reasoning looks like.

## Key Takeaways

- Domain-specific system prompts with worked examples produce a 54% relative improvement over generic baselines on complex tasks — with no model or tool changes
- Examples should represent real edge cases from your domain, not imagined happy paths
- Complex guidance belongs in the system prompt, not in tool descriptions — broader integration, more consistent application
- Write examples by observing real reasoning failures; instrument production before writing prompts
- The example set requires ongoing maintenance as the domain and failure modes evolve

## Related

- [The Think Tool](../agent-design/think-tool.md)
- [Reasoning Budget Allocation](../agent-design/reasoning-budget-allocation.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [System Prompt Altitude](system-prompt-altitude.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
- [Event-Driven System Reminders](event-driven-system-reminders.md)
- [Instruction Polarity](instruction-polarity.md)
- [Production System Prompt Architecture](production-system-prompt-architecture.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Negative Space Instructions](negative-space-instructions.md)
- [Prompt File Libraries](prompt-file-libraries.md)
- [Prompt Governance via PR](prompt-governance-via-pr.md)
- [Tool Descriptions as Onboarding](../tool-engineering/tool-descriptions-as-onboarding.md) — writing tool descriptions with implicit context agents need
