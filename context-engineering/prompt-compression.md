---
title: "Prompt Compression: Maximizing Signal Per Token"
description: "Write instructions that convey the same guidance in fewer words — shorter, denser instructions improve agent compliance and reduce token cost in Claude Code."
tags:
  - cost-performance
  - context-engineering
---

# Prompt Compression: Maximizing Signal Per Token

> Write instructions that convey the same guidance in fewer words — because shorter, denser instructions improve agent compliance and reduce token cost.

## Why Density Matters

Claude Code's context window fills fast. A debugging session or codebase exploration can consume tens of thousands of tokens. The [Claude Code best practices documentation](https://code.claude.com/docs/en/best-practices) warns that bloated instruction files cause important rules to get lost — instructions near the end of a long context receive less attention than instructions at the start.

The same problem applies to instruction files. The [Claude Code best practices documentation](https://code.claude.com/docs/en/best-practices) explicitly warns: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" A shorter file where every rule applies outperforms a longer file where important rules are buried and skipped.

Prompt compression is not about losing guidance — it is about removing the words that carry no meaning.

## Compression Techniques

### Tables Over Prose

Structured data communicates more information per line than prose. A table of examples communicates the contrast between correct and incorrect behavior with zero explanation overhead.

```markdown
| ✅ Include                          | ❌ Exclude                           |
|------------------------------------|--------------------------------------|
| Bash commands Claude can't guess   | Anything Claude can infer from code  |
| Code style rules that differ from defaults | Standard conventions Claude already knows |
```

The [Claude Code best practices guide](https://code.claude.com/docs/en/best-practices) uses this pattern throughout — tables rather than prose paragraphs for communicating when to do and when to avoid.

### Bullets Over Sentences

One idea per line. No transitional language. Sentences like "It is important that you ensure the code is well-tested before submission" collapse to "Write tests before submitting."

### Rules Over Explanations

State the rule. Do not explain why unless the reason is non-obvious and compliance depends on it.

- **Verbose**: "Try to avoid using unnecessary filler phrases that don't add value to the response."
- **Compressed**: "No filler phrases."

The instruction delivers the same constraint at one-third the length.

### Negative Constraints Are Cheap

"Never X" requires fewer tokens than describing the correct alternative and is harder to misread. Negative constraints define a boundary without specifying every valid option inside it. See [Negative Space Instructions](../instructions/negative-space-instructions.md) for a full treatment of this technique.

### Examples Over Descriptions

Show the pattern instead of describing it. An example collapses the description of a pattern and its application into a single piece of text that the agent can directly imitate.

### Put the Most Important Rules First

Attention degrades across a long context. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) confirms this: important rules in a bloated CLAUDE.md get lost. Front-load the rules that, if broken, cause the most damage.

## The Compression Test

Apply this test to every sentence in an instruction file: "Can I remove a word without losing meaning?" If yes, remove it. Apply the same test at the sentence level: "Can I remove this sentence without losing a constraint?" If yes, remove it.

The [Claude Code skills documentation](https://code.claude.com/docs/en/skills) recommends keeping SKILL.md under 500 lines and moving detailed reference material to separate files loaded on demand. The same principle applies to any instruction file: keep the core short, and reference auxiliary detail only when needed.

## Splitting vs. Compressing

Some content does not compress — it is simply not needed in every context. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) distinguishes between:

- **CLAUDE.md** — always loaded; keep to universal, high-signal rules only
- **Skills** — loaded on demand; domain knowledge that applies to specific tasks

Moving specialized instructions from CLAUDE.md to a skill reduces base context size without losing the guidance. This is structural compression rather than lexical compression.

## Example

A verbose CLAUDE.md testing section before compression:

```markdown
## Testing Requirements

It is very important that you make sure all code changes are thoroughly
tested before submitting them for review. You should always write unit
tests that cover the main logic of any function you add or modify.
Try to ensure that edge cases are handled appropriately in your tests.
Please do not submit code that has not been tested.
```

After applying compression techniques (rules over explanations, bullets over sentences):

```markdown
## Testing

- Write unit tests for every function added or modified
- Cover edge cases
- Do not submit untested code
```

Same constraints. 60% fewer tokens.

## When This Backfires

Compression removes words, not meaning — but the two are not always separable.

- **Edge-case context removed**: A rule like "Write tests before submitting" compresses cleanly, but "Write integration tests when the function touches the database, unit tests otherwise" cannot be compressed further without losing the conditional. Cutting context that disambiguates applies the rule uniformly where it should apply selectively.
- **Implicit reasoning stripped**: Rules without *why* rely on the agent inferring intent correctly. When the agent encounters a case the rule author didn't anticipate, absence of rationale means no basis for generalization. Add rationale only when compliance on unforeseen inputs depends on it.
- **Compression as premature optimization**: Trimming a CLAUDE.md that is already under 20 rules produces marginal gains. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) identifies long, bloated files as the failure mode — not files that are merely imperfect. Compress to remove noise; stop before removing signal.

## Key Takeaways

- Verbose instructions do not improve accuracy — they increase the chance that important rules are skipped.
- Tables, bullets, and direct rules compress more information per token than prose.
- Apply a compression test: remove any word or sentence that does not change agent behavior.
- Front-load the highest-priority rules; attention degrades across long instruction sets.
- Move workflow-specific instructions from always-loaded files (CLAUDE.md) to on-demand skills.

## Related

- [CLAUDE.md Convention](../instructions/claude-md-convention.md) — authoring concise project instruction files; keep to universal, high-signal rules
- [Negative Space Instructions](../instructions/negative-space-instructions.md) — negative constraints that compress guidance without enumerating alternatives
- [Context Compression Strategies](context-compression-strategies.md) — session-level compaction complements lexical compression
- [Semantic Density Optimization](semantic-density-optimization.md) — higher-level packing of meaning per token across context
- [Token-Efficient Code Generation](token-efficient-code-generation.md) — compression patterns applied to generated code output
- [Lost in the Middle](lost-in-the-middle.md) — the attention-degradation effect that motivates front-loading rules
- [Prompt Layering](prompt-layering.md) — structuring instructions across layers so each loads only when needed
- [Layered Context Architecture](layered-context-architecture.md) — structural compression via on-demand loading
