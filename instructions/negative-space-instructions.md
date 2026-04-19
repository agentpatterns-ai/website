---
title: "Negative Space Instructions: What NOT to Do in Agent Prompts"
description: "Use negative constraints — banned phrases, scope exclusions, tool restrictions — to eliminate known failure modes in agent prompts with binary, greppable rules."
tags:
  - instructions
aliases:
  - Instruction Polarity
  - Positive Rules Over Negative
  - Instruction Framing
---

# Negative Space Instructions: What NOT to Do

> Exclusions and constraints eliminate entire classes of mistakes more efficiently than equivalent positive guidance.

!!! info "Also known as"
    Instruction Polarity, Positive Rules Over Negative, Instruction Framing

## Why Negative Constraints Work

"Write concise content" is vague — concise to whom, in what context? "No filler phrases: no 'in this guide', no 'let's explore', no 'as you may know'" is precise and binary. The agent either produced the phrase or it didn't. There is no interpretation required.

Negative constraints are cheap in tokens, unambiguous in intent, and verifiable programmatically. A grep for banned phrases confirms compliance without human review. Equivalent positive guidance ("write in a direct, information-dense style") requires a human or second model to evaluate — there is no deterministic check.

## Types of Negative Constraints

**Banned phrases** eliminate verbal tics and filler that survive positive tone guidance:
```
No filler: "in this guide", "let's explore", "it's worth noting", "as you may know"
```

**Scope exclusions** prevent agents from drifting into adjacent work:
```
Do not modify files outside docs/
Do not touch .github/, mkdocs.yml, or CI configuration
```

**Tool restrictions** are simpler than explaining when each tool is appropriate:
```
Do not use the web search tool unless explicitly asked
```

**Format exclusions** enforce structure without requiring explanation:
```
No paragraphs longer than 3 sentences
No inline comments in production code unless the logic is non-obvious
```

## Pairing with Positive Guidance

Negative constraints are most effective when paired with a positive directive that states the goal. The positive rule gives the agent direction; the negative constraint closes off the most common wrong interpretations:

```
Be direct and information-dense. No filler phrases ("in this guide", "let's explore").
```

Relying entirely on positive guidance leaves edge cases open. Relying entirely on negative constraints produces agents that know what not to do but lack direction. Both together cover the space efficiently.

## Greppability as a Design Criterion

A well-formed negative constraint is one you can verify automatically. If the constraint cannot be expressed as a grep pattern or a deterministic check, it may belong in positive guidance instead. This also makes negative constraints audit-friendly: a CI step can flag violations before human review.

## Why It Works

The effectiveness of negative constraints comes from reducing the interpretation surface. A constraint like "no filler phrases" collapses to a binary outcome — the phrase either appears or it doesn't. The agent cannot partially comply; the output is deterministically checkable. Positive guidance like "write concisely" leaves the interpretation open: the agent must model what "concise" means in context, and that model can drift.

Mechanically, negative constraints eliminate entire token sequences from consideration during generation, which has a discrete and binary effect rather than a soft preference. Positive guidance ("be concise") narrows the output distribution without hard-cutting regions, so it must compete against other objectives in the model's output distribution. Negative constraints behave more like hard constraints in optimization: they create a feasibility boundary rather than a preference gradient.

Palantir's prompt engineering guidance documents this directly: banning specific undesired outputs is more reliable than describing desired characteristics, because banned patterns can be verified while quality attributes require judgment ([Palantir AIP prompt engineering best practices](https://www.palantir.com/docs/foundry/aip/best-practices-prompt-engineering)).

This specificity advantage also applies at enforcement time. A CI step can grep for banned phrases and block a commit; it cannot evaluate whether prose is "information-dense." The constraint is only as strong as your ability to verify it.

## What Negative Constraints Cannot Do

Negative constraints eliminate known failure modes. They do not handle unknown ones. If an agent finds a new way to violate the spirit of an instruction, a negative constraint won't catch it. Keep a list of negative constraints short and targeted; don't try to enumerate every possible mistake.

For constraints that must never fail, hooks are more reliable than instructions — negative or positive. A pre-commit hook blocking commits to main is more reliable than "never commit directly to main."

## Example

A CLAUDE.md section using negative constraints paired with positive guidance:

```markdown
## Code Style

Write clear, self-documenting code.

- No abbreviations in variable or function names
- No single-letter variables outside loop counters
- No commented-out code in committed files
- No TODO comments without a linked issue number

## Agent Behavior

Complete the task in a single session. Be thorough.

- Do not modify files outside the assigned directory
- Do not install new dependencies without explicit approval
- Do not run destructive commands (rm -rf, git reset --hard, DROP TABLE)
- Do not skip tests to make CI pass
```

Each positive directive ("Write clear, self-documenting code") sets the goal. The negative constraints close off the most common violations — and every one is verifiable with a grep or a git diff.

## When This Backfires

Negative constraints fail in predictable ways:

- **Negation comprehension**: Models do not always interpret negation reliably. A "Pink Elephant" or "white bear" effect occurs when the prohibited concept becomes a stronger prior in the model and the rate of prohibited output goes *up*, not down. [Negation: A Pink Elephant in the Large Language Models' Room? (Truhn et al., arxiv:2503.22395, 2025)](https://arxiv.org/abs/2503.22395) finds that negation handling varies substantially across model sizes and languages, and is not a solved capability. [Do not think about pink elephant! (Liu et al., arxiv:2404.15154, CVPR 2024 Responsible GenAI Workshop)](https://arxiv.org/abs/2404.15154) shows the same pattern in generative models and that prompt-based defenses can mitigate but not eliminate it. Reframing as a positive instruction often outperforms a literal "do not" — see [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md) for the trade-off.
- **Unknown failure modes**: A constraint list only covers mistakes the author anticipated. When an agent finds a new way to violate the spirit of an instruction, no existing negative constraint catches it — the list must be updated reactively.
- **Superficial compliance**: An agent can satisfy the letter of a negative constraint while preserving the underlying problem. Banning "in this guide" doesn't prevent wordy preambles; it just changes the wording.
- **Constraint explosion**: As edge cases accumulate, the constraint list grows until it dominates the prompt. Long constraint lists are harder to reason about and more likely to conflict internally.
- **Missing context**: Scope exclusions ("do not modify files outside docs/") assume the agent correctly identifies what counts as "outside docs/". Ambiguous boundaries produce false compliance.

For must-never-fail constraints, rely on enforced mechanisms — hooks, CI checks, schema validation — rather than instruction text alone.

## Key Takeaways

- Negative constraints are binary, cheap, and verifiable — prefer them for eliminating known failure modes
- Design constraints to be greppable: if you cannot check compliance automatically, reconsider the form
- Pair negative constraints with positive guidance: state the goal, then close off the wrong paths
- For must-never-fail constraints, use hooks rather than instructions

## Related

- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [The Mega-Prompt (Anti-Pattern)](instruction-compliance-ceiling.md)
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md)
- [Content Exclusion Gap in Agent Systems](content-exclusion-gap.md)
- [WRAP Framework for Agent Instructions](wrap-framework-agent-instructions.md)
- [Critical Instruction Repetition via Primacy and Recency](critical-instruction-repetition.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md)
- [Guardrails Beat Guidance for Coding Agents](guardrails-beat-guidance-coding-agents.md)
