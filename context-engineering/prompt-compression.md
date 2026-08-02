---
title: "Prompt Compression: Maximizing Signal Per Token"
term: "Prompt Compression"
description: "Write instructions that convey the same guidance in fewer words — shorter, denser instructions improve agent compliance and reduce token cost in Claude Code."
tags:
  - cost-performance
  - context-engineering
  - tool-agnostic
last_reviewed: 2026-07-15
maturity: established
---

# Prompt Compression: Maximizing Signal Per Token

> Write instructions that convey the same guidance in fewer words — because shorter, denser instructions improve agent compliance and reduce token cost.

Learn it hands-on with the [Signal Per Token guided lesson](https://learn.agentpatterns.ai/context-engineering/signal-per-token/), which includes quizzes.

## Why density matters

Claude Code's context window fills fast. A debugging session or codebase exploration can consume tens of thousands of tokens. Instructions near the end of a long context receive less attention than those at the start. The [Claude Code best practices documentation](https://code.claude.com/docs/en/best-practices) is blunt about the consequence: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" A shorter file where every rule applies works better than a longer file where important rules are buried and skipped.

Prompt compression is not about losing guidance — it is about removing the words that carry no meaning.

## Compression techniques

### Tables over prose

Structured data carries more information per line than prose. A table shows the contrast between correct and incorrect behavior with no explanation overhead.

```markdown
| ✅ Include                          | ❌ Exclude                           |
|------------------------------------|--------------------------------------|
| Bash commands Claude can't guess   | Anything Claude can infer from code  |
| Code style rules that differ from defaults | Standard conventions Claude already knows |
```

The [Claude Code best practices guide](https://code.claude.com/docs/en/best-practices) uses this pattern throughout — tables rather than prose paragraphs to show what to do and what to avoid.

### Bullets over sentences

One idea per line. No transitional language. Sentences like "It is important that you ensure the code is well-tested before submission" collapse to `Write tests before submitting`.

### Rules over explanations

State the rule. Do not explain why unless the reason is non-obvious and compliance depends on it.

- Verbose: "Try to avoid using unnecessary filler phrases that don't add value to the response."
- Compressed: `No filler phrases.`

The instruction delivers the same constraint at one-third the length.

### Negative constraints are cheap

"Never X" needs fewer tokens than describing the correct alternative, and it is harder to misread. Negative constraints define a boundary without naming every valid option inside it. See [Negative Space Instructions](../instructions/negative-space-instructions.md) for a full treatment of this technique.

### Examples over descriptions

Show the pattern instead of describing it. An example collapses a pattern and its application into a single piece of text the agent can copy directly.

### Name concepts instead of defining them

A canonical name carries its full definition. The model already knows what semantic versioning, Conventional Commits, or exponential backoff mean. `Version bumps follow semver` delivers the whole constraint in four words, where a paragraph re-deriving the major/minor/patch rules adds tokens without adding meaning. The [Claude Code best practices guide](https://code.claude.com/docs/en/best-practices) draws exactly this boundary in its include/exclude table, which excludes "standard conventions Claude already knows", and [Microsoft's skill-authoring guidance](https://developer.microsoft.com/blog/stop-overloading-your-skills) states the sizing rule directly: include only the delta of knowledge the model lacks; omit standard SDK and API patterns. This cuts only when local usage matches the standard meaning — see [When this backfires](#when-this-backfires).

### Put the most important rules first

Attention degrades across a long context. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) confirms this: important rules in a bloated CLAUDE.md get lost. Front-load the rules that, if broken, cause the most damage.

## The compression test

Apply this test to every sentence in an instruction file: "Can I remove a word without losing meaning?" If yes, remove it. Apply the same test at the sentence level: "Can I remove this sentence without losing a constraint?" If yes, remove it.

The [Claude Code skills documentation](https://code.claude.com/docs/en/skills) recommends keeping SKILL.md under 500 lines and moving detailed reference material to separate files loaded on demand. The same principle applies to any instruction file: keep the core short, and reference auxiliary detail only when needed.

## Splitting versus compressing

Some content does not compress — it is simply not needed in every context. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) distinguishes between two homes for instructions:

- CLAUDE.md — always loaded, so keep it to universal, high-priority rules only
- Skills — loaded on demand, for domain knowledge that applies to specific tasks

Moving specialized instructions from CLAUDE.md to a skill cuts base context size without losing the guidance. This is structural compression rather than lexical compression.

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

## When this backfires

Compression removes words, not meaning — but the two are not always separable.

- Edge-case context removed: a rule like "Write tests before submitting" compresses cleanly, but `Write integration tests when the function touches the database, unit tests otherwise` cannot be compressed further without losing the conditional. Cutting context that disambiguates applies the rule uniformly where it should apply selectively.
- Local redefinitions cut as "known concepts": naming a concept replaces its definition only when the standard meaning is exactly the rule. A project that redefines a term — "a *release* here means the gate passed **and** the tag pushed **and** the shelf mirrored" — is stating a constraint, not ceremony; cutting the local definition silently substitutes the standard behavior for the intended one. The same applies to genuinely ambiguous or obscure names the model may not resolve reliably.
- Implicit reasoning stripped: rules stripped of [their rationale](semantic-density-optimization.md) rely on the agent inferring intent correctly. When the agent meets a case the rule author did not anticipate, the missing rationale leaves no basis for generalization. Add rationale only when compliance on unforeseen inputs depends on it.
- Compression as premature optimization: trimming a CLAUDE.md that is already under 20 rules produces marginal gains. The [Claude Code documentation](https://code.claude.com/docs/en/best-practices) identifies long, bloated files as the failure mode — not files that are merely imperfect. Compress to remove noise; stop before removing signal.
- The compliance U-curve: shorter is not always better. A benchmark study of instruction-following under compression — [Separating Constraint Compliance from Semantic Accuracy (arXiv:2512.17920)](https://arxiv.org/abs/2512.17920) — found constraint violations peak at medium compression, with compliance recovering at both the verbose and the extreme-compression ends. Half-compressing a rule (paraphrasing it tighter without committing to a terse, unambiguous form) can hurt compliance more than leaving it verbose. Compress decisively to a crisp rule; a partially-trimmed instruction is the worst of both worlds.

## Key Takeaways

- Verbose instructions do not improve accuracy — they increase the chance that important rules are skipped.
- Tables, bullets, and direct rules compress more information per token than prose.
- Apply a compression test: remove any word or sentence that does not change agent behavior.
- Name known concepts (semver, Conventional Commits) instead of re-defining them; keep local definitions that differ from the standard meaning.
- Front-load the highest-priority rules; [attention degrades across long instruction sets](lost-in-the-middle.md).
- Move workflow-specific instructions from always-loaded files (CLAUDE.md) to on-demand skills.

## Related

- [CLAUDE.md Convention](../instructions/claude-md-convention.md) — authoring concise project instruction files; keep to universal, high-signal rules
- [Negative Space Instructions](../instructions/negative-space-instructions.md) — negative constraints that compress guidance without enumerating alternatives
- [Context Compression Strategies](context-compression-strategies.md) — session-level compaction complements lexical compression
- [Semantic Density Optimization](semantic-density-optimization.md) — higher-level packing of meaning per token across context
- [Token-Efficient Code Generation](../token-engineering/token-efficient-code-generation.md) — compression patterns applied to generated code output
- [Lost in the Middle](lost-in-the-middle.md) — the attention-degradation effect that motivates front-loading rules
- [Prompt Layering](prompt-layering.md) — structuring instructions across layers so each loads only when needed
- [Layered Context Architecture](layered-context-architecture.md) — structural compression via on-demand loading
