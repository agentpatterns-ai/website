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

Negative instructions require suppression: the agent must hold the prohibited action in mind while choosing not to take it. Positive instructions require execution: the agent identifies the target behavior and performs it. Token generation favors positive selection — the model chooses what comes next rather than avoiding tokens — so positive instructions boost the probability of desired outputs ([The Pink Elephant Problem](https://eval.16x.engineer/blog/the-pink-elephant-negative-instructions-llms-effectiveness-analysis)), producing higher compliance across equivalent rule sets. Anthropic's prompt engineering guidance reflects this: ["Tell Claude what to do instead of what not to do."](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)

The practical difference is small when instructions are few. It compounds as instruction count grows. Negative rules degrade first under a large instruction set because the suppression signal competes with a growing context of execution targets.

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

In these cases, keep the negative instruction and move it toward the top of the instruction set. LLMs exhibit position-dependent attention — earlier instructions tend to receive stronger weighting, though this can reverse in very long contexts where recency dominates.

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

## When This Backfires

Positive reframing has limits. It fails or is inapplicable when:

- **The acceptable-behavior space is unbounded.** "Use only approved libraries" cannot be made positive without enumerating every approved library — sometimes the negative form is the only practical option.
- **Ambiguity in the positive form creates new errors.** "Push to a feature branch" leaves open which repo, which base branch, and who owns naming. The negative "never push directly to main" is crisper precisely because it is narrower.
- **Context-window pressure is extreme.** Positive instructions are still subject to the lost-in-the-middle effect ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)). Long instruction sets degrade all rule types; positive phrasing mitigates but does not eliminate the problem.
- **Rule count is low.** With fewer than five or six instructions, the compliance gap between positive and negative forms is small enough to be outweighed by other factors such as clarity or brevity.

The pattern is a default, not a universal. Apply it where the compliance benefit is material and the positive form is unambiguous.

## Key Takeaways

- Positive instructions ("use X") outperform negative ones ("avoid Y") — positive forms give the agent an explicit execution target rather than a suppression task
- Reframe prohibitions as requirements: negative rules become positive constraints with explicit targets
- Reserve negative phrasing for absolute prohibitions where the positive form is ambiguous or the acceptable-behavior space is too large to enumerate
- Move critical prohibitions to hooks — instructions ask, hooks require

## Related

- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — the coding-agent-specific refinement where negative constraints outperform positive directives
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](instruction-compliance-ceiling.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](critical-instruction-repetition.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [CLAUDE.md Convention for AI Agent Development](claude-md-convention.md)
- [System Prompt Replacement for Domain-Specific Agent Personas](system-prompt-replacement.md)
- [Layer Agent Instructions by Specificity: Global, Project](layered-instruction-scopes.md)
- [AGENTS.md Design Patterns: Commands, Boundaries, and Personas](agents-md-design-patterns.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md)
