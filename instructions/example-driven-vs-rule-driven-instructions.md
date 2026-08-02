---
title: "Example-Driven vs Rule-Driven Instructions"
term: "When to Use Examples vs Rules"
description: "Rules generalize; examples anchor — knowing when to use each determines whether agents interpret your intent or invent their own."
aliases:
  - Hints Over Code Samples
  - Example-Based Instructions
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-13
maturity: emerging
---

# Example-Driven vs Rule-Driven Instructions

> Rules generalize and examples anchor — choosing between these instructions determines whether agents interpret your intent or invent their own.

Learn it hands-on with the [Rules or Examples](https://learn.agentpatterns.ai/prompt-engineering/rules-or-examples/) guided lesson, which includes quizzes.

!!! info "Also known as"

    [Hints Over Code Samples](hints-over-code-samples.md), Example-Based Instructions

## The trade-off

Rules are compact and context-efficient. "Use kebab-case filenames" costs five tokens and applies everywhere. Examples are concrete and unambiguous. `progressive-disclosure.md, not ProgressiveDisclosure.md` leaves no room for creative interpretation. Each has failure modes:

- Rules can be misread. "Write concisely" means different things to different agents.
- Examples can be over-fitted. An agent shown one example may copy its structure verbatim rather than abstracting the pattern — the few-shot brittleness that [hints over code samples](hints-over-code-samples.md) also has to manage.

The choice is not stylistic. It depends on what kind of failure you want to prevent.

## When to use rules

Use rules for behavioral constraints where the expected output space is large and you want to eliminate a class of behavior:

- `Never commit directly to main`
- `Keep functions under 30 lines`
- `Use const and let only — never var`

Rules work well when the constraint is binary (either compliant or not) and when the agent's reading of the rule produces acceptable variation. If any reading is fine, a rule is cheaper than an example.

## When to use examples

Use examples when the format or structure matters precisely and a misinterpretation would produce clearly wrong output. File naming, commit message structure, and output schemas are good candidates:

```
Commit message format:
  docs(patterns): add context priming pattern

Not:
  Added context priming pattern to patterns
  update docs
  docs: context priming
```

Examples are also effective for anti-patterns. Pairing "don't do this" with a concrete instance is more reliable than describing the prohibited behavior abstractly.

## Combining rules and examples

The most reliable pattern: state the rule, then show one example. This gives the agent a generalization to apply and a concrete reference to check against.

```
File names must be kebab-case and match the concept name.

Example: progressive-disclosure.md (not ProgressiveDisclosure.md, not prog-disc.md)
```

One example is usually enough. Multiple examples can shift agent focus from the rule to the pattern of the examples themselves, producing outputs that interpolate between cases rather than apply the constraint uniformly — the brittleness [system prompt altitude](system-prompt-altitude.md) warns against. For constraint rules, a single well-chosen example suffices.

## Pointing at existing code (hints over code samples)

For format and style constraints in a codebase, pointing at existing code outperforms providing an inline example. A hint is a reference, not a reproduction:

| Code sample | Hint equivalent |
|-------------|-----------------|
| `export class UserRepo extends BaseRepo<User> {...}` (30 lines) | "Follow the repository pattern in `src/repos/UserRepo.ts`" |
| Full example middleware function | "Use the existing middleware in `src/middleware/auth.ts` as the pattern" |
| Example test setup | "Tests follow the pattern in `src/__tests__/user.test.ts`" |

Hints carry two advantages over inline samples:

Hints stay current. Code samples are frozen. The real implementation changes — function signatures, dependencies, patterns — while the agent follows the stale example. A hint points to the current file and needs no maintenance.

Hints are cheaper. A 30-line example loaded every session consumes context budget for every task, including unrelated ones. A hint costs one line. For instruction files loaded at session start, this draw on the [context budget](../context-engineering/context-budget-allocation.md) compounds across every interaction.

The one case where a code sample is justified: a genuinely novel pattern with no existing example in the codebase. Once any file implements the pattern, replace the sample with a hint to that file.

## Placement

Critical format constraints belong in the main instruction file. Reference examples and templates belong in supporting files (skills, referenced documents) loaded on demand. Putting every example inline bloats the system prompt and pushes rules past the reliable attention range.

## Why it works

Rules and examples engage different mechanisms in how transformers process instructions. GPT-3 established that large language models can infer tasks from text demonstrations alone, without fine-tuning or explicit rules ([Brown et al., 2020](https://arxiv.org/abs/2005.14165)). Mechanistic interpretability research traces in-context learning to induction heads, pairs of attention heads that find an earlier occurrence of the current token and copy what followed it, matching and extending prior patterns ([Olsson et al., "In-context Learning and Induction Heads," 2022](https://arxiv.org/abs/2209.11895)). An example gives the model a concrete template to replicate rather than a constraint to interpret, the effect [domain-specific system prompts](domain-specific-system-prompts.md) exploit with worked reasoning traces. Rules require the model to derive the intended output space through inference; examples supply it directly. This is why rules tolerate ambiguity when acceptable variation is wide, and examples are necessary when the output space is tightly constrained. The combination — state the rule, provide one anchor example — engages both: the rule limits the interpretation space, the example collapses residual ambiguity to a specific format.

## Key Takeaways

- Rules constrain behavior space; examples constrain interpretation — choose based on what failure you're preventing
- Combine them: state the rule, show one example, stop
- Negative examples ("don't do this") paired with a concrete instance outperform abstract prohibitions
- For format precision, point at existing code rather than reproducing it inline — hints stay current and cost far fewer tokens
- Too many examples teaches interpolation; too few leaves rules open to creative misreading
- When no existing example exists, a code sample is the specification; replace it with a hint once the pattern is in the codebase

## Related

- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — empirical evidence on negative-vs-positive rule polarity for coding agents
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](instruction-compliance-ceiling.md)
- [Hints Over Code Samples in Agent Prompts](hints-over-code-samples.md) — detailed treatment of when and how to use path references instead of inline code samples
- [System Prompt Altitude](system-prompt-altitude.md) — balancing specificity and brittleness in instruction design
- [Prompt Compression: Maximizing Signal Per Token](../context-engineering/prompt-compression.md)
