---
title: "Instruction Polarity: Positive Rules Over Negative"
description: "Positive directives outperform negative instructions in agent compliance. Reframe prohibitions as explicit requirements; reserve negatives for absolute bans."
tags:
  - instructions
aliases:
  - Negative Space Instructions
  - Instruction Framing
---

# Instruction Polarity: Positive Rules Over Negative

> Positive directives — what to do — outperform negative instructions — what not to do — in agent compliance, especially as instruction count grows.

!!! info "Also known as"
    Negative Space Instructions, Instruction Framing

## The Compliance Asymmetry

Negative instructions require suppression: the agent must hold the prohibited action in mind while choosing not to take it. Positive instructions require execution: the agent identifies the target behavior and performs it. Execution is a cheaper cognitive operation than suppression [unverified — model-architecture dependent], which produces measurably higher compliance rates for positive forms across equivalent rule sets.

The practical difference is small when instructions are few. It compounds as instruction count grows. Negative rules are among the first to fail when attention is under pressure from a large instruction set. [unverified]

## Reframing Common Rules

Most negative rules can be reframed as positive constraints without losing precision:

| Negative | Positive |
|---|---|
| Do not use `var` | Use `const` and `let` only |
| Avoid long functions | Keep functions under 30 lines |
| Don't write vague commit messages | Use conventional commits: `type(scope): description` |
| Never hardcode secrets | Store all secrets in environment variables |
| Don't skip tests | Write a test for every new function |

The positive form states what the agent must do. The negative form states what it must avoid while leaving the correct behavior implicit. Implicit is less reliable.

## When Negative Phrasing Is Justified

Some prohibitions are genuinely clearer in negative form. Use negative phrasing when:

- The space of acceptable alternatives is too large to enumerate: "Do not modify infrastructure files" is cleaner than listing every acceptable file type
- The prohibition is absolute and the positive form would be ambiguous: "Never push directly to main" vs. "Push to feature branches" (which main? which branches?)
- You are naming a specific banned item: "No `console.log` in production code"

In these cases, keep the negative instruction and move it toward the top of the instruction set (primacy bias favors earlier instructions [unverified]).

## Hooks for True Prohibitions

If a prohibition is critical enough that failure is unacceptable, it should not be an instruction at all — it should be a hook. A pre-commit hook that rejects `var` declarations enforces the rule deterministically. An instruction asks; a hook requires.

The heuristic: if you find yourself writing "never" or "must not," ask whether a hook is the right implementation. Instructions are probabilistic; hooks are not.

## Example

A `.claude/CLAUDE.md` instruction file for a TypeScript project, reframed from negative to positive:

**Before — negative-heavy:**

```markdown
## Code Rules

- Do not use `any` type
- Don't leave console.log statements in code
- Avoid nested ternaries
- Never import from `src/internal/*` outside that directory
- Don't write functions longer than 40 lines
```

**After — positive-first with targeted negatives:**

```markdown
## Code Rules

- Type every binding explicitly — use `unknown` when the type is genuinely indeterminate
- Log through the `logger` service; remove all direct `console.*` calls before committing
- Extract complex conditionals into named helper functions
- Keep functions under 40 lines; split at logical boundaries
- Never import from `src/internal/*` outside that directory
```

The last rule stays negative because the set of acceptable imports is too large to enumerate. The others gain an explicit target behavior the agent can execute directly.

## Key Takeaways

- Positive instructions ("use X") outperform negative ones ("avoid Y") because execution is cheaper than suppression
- Reframe prohibitions as requirements: negative rules become positive constraints with explicit targets
- Reserve negative phrasing for absolute prohibitions where the positive form is ambiguous
- Move critical prohibitions to hooks — instructions ask, hooks require

## Unverified Claims

- Execution is a cheaper cognitive operation than suppression for models [unverified — model-architecture dependent]
- Negative rules are among the first to fail when attention is under pressure from a large instruction set [unverified]
- Primacy bias favors earlier instructions [unverified]

## Related

- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](instruction-compliance-ceiling.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](critical-instruction-repetition.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [CLAUDE.md Convention for AI Agent Development](claude-md-convention.md)
- [System Prompt Replacement for Domain-Specific Agent Personas](system-prompt-replacement.md)
- [Layer Agent Instructions by Specificity: Global, Project](layered-instruction-scopes.md)
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md)
