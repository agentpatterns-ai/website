---
title: "When to Use Examples vs Rules in Agent Instructions"
description: "Rules generalize; examples anchor — knowing when to use each determines whether agents interpret your intent or invent their own."
aliases:
  - Hints Over Code Samples
  - Example-Based Instructions
tags:
  - instructions
  - context-engineering
  - tool-agnostic
---

# Example-Driven vs Rule-Driven Instructions

> Rules generalize; examples anchor — knowing when to use each determines whether agents interpret your intent or invent their own.

!!! info "Also known as"

    Hints Over Code Samples, Example-Based Instructions

## The Trade-off

Rules are compact and context-efficient. "Use kebab-case filenames" costs five tokens and applies universally. Examples are concrete and unambiguous. `progressive-disclosure.md, not ProgressiveDisclosure.md` leaves no room for creative interpretation. Each has failure modes:

- **Rules** can be misread. "Write concisely" means different things to different agents.
- **Examples** can be over-fitted. An agent shown one example may copy its structure verbatim rather than abstracting the pattern.

The choice between them is not stylistic — it's a function of what kind of failure you're trying to prevent.

## When to Use Rules

Use rules for behavioral constraints where the expected output space is large and you want to eliminate a class of behavior:

- `Never commit directly to main`
- `Keep functions under 30 lines`
- `Use const and let only — never var`

Rules work well when the constraint is binary (either compliant or not) and when the agent's interpretation of the rule will produce acceptable variation. If any interpretation is fine, a rule is cheaper than an example.

## When to Use Examples

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

## Combining Rules and Examples

The most reliable pattern: state the rule, then show one example. This gives the agent a generalization to apply and a concrete reference to check against.

```
File names must be kebab-case and match the concept name.

Example: progressive-disclosure.md (not ProgressiveDisclosure.md, not prog-disc.md)
```

One example is usually enough. Multiple examples risk teaching the agent to interpolate between them rather than follow the rule [unverified]. For constraint rules, a single well-chosen example suffices.

## Pointing at Existing Code (Hints Over Code Samples)

For format and style constraints in a codebase, pointing at existing code outperforms providing an inline example. A hint is a reference, not a reproduction:

| Code sample | Hint equivalent |
|-------------|-----------------|
| `export class UserRepo extends BaseRepo<User> {...}` (30 lines) | "Follow the repository pattern in `src/repos/UserRepo.ts`" |
| Full example middleware function | "Use the existing middleware in `src/middleware/auth.ts` as the pattern" |
| Example test setup | "Tests follow the pattern in `src/__tests__/user.test.ts`" |

Hints carry two advantages over inline samples:

**Hints stay current.** Code samples are frozen. The real implementation changes — function signatures, dependencies, patterns — while the agent follows the stale example. A hint points to the current file and requires no maintenance.

**Hints are cheaper.** A 30-line example loaded every session consumes context budget for every task, including unrelated ones. A hint costs one line. For instruction files loaded at session start, this compounds across every interaction.

The one case where a code sample is justified: a genuinely novel pattern with no existing example in the codebase. Once any file implements the pattern, replace the sample with a hint to that file.

## Placement

Critical format constraints belong in the main instruction file. Reference examples and templates belong in supporting files (skills, referenced documents) loaded on demand. Putting every example inline bloats the system prompt and pushes rules past the reliable attention range.

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
- [The Instruction Compliance Ceiling: Why More Rules Mean More Ignored Rules](instruction-compliance-ceiling.md)
- [Prompt Compression: Maximizing Signal Per Token](../context-engineering/prompt-compression.md)
- [Context Priming for AI Agent Development](../context-engineering/context-priming.md)
