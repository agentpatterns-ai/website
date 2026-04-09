---
title: "Negative Space Instructions: What NOT to Do in Agent Prompts"
description: "Exclusions and constraints eliminate entire classes of mistakes more efficiently than equivalent positive guidance. Instruction Polarity, Positive Rules Over"
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

Negative constraints are cheap in tokens, unambiguous in intent, and verifiable programmatically. A grep for banned phrases confirms compliance without human review. Equivalent positive guidance ("write in a direct, information-dense style") requires judgment to evaluate [unverified].

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

## Key Takeaways

- Negative constraints are binary, cheap, and verifiable — prefer them for eliminating known failure modes
- Design constraints to be greppable: if you cannot check compliance automatically, reconsider the form
- Pair negative constraints with positive guidance: state the goal, then close off the wrong paths
- For must-never-fail constraints, use hooks rather than instructions

## Unverified Claims

- Equivalent positive guidance requires judgment to evaluate [unverified]

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
