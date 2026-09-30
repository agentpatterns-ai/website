---
title: "Requirement Smells: No Category Signal, Density Unconfirmed"
term: "Requirement Smell Density"
description: "Pass rates fell in some model and application pairings as injected requirement defects accumulated, but no defect category did consistently more damage and no density correlation survived multiple-comparison correction."
aliases:
  - requirement smell category triage
  - requirement quality in code-generation prompts
tags:
  - instructions
  - code-generation
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-29
maturity: emerging
---

# Requirement Smells: No Category Signal, Density Unconfirmed

> Pass rates fell in some pairings as defective requirements accumulated, but no category did consistently more damage and no density correlation survived multiple-comparison correction.

A requirement smell is a quality defect in the requirement sentence itself: a weak verb or a passive construction that drops the actor. A controlled experiment injected these into otherwise clean requirements at five increasing densities and scored the generated Java against requirement-level unit tests. Correctness fell in several model and application pairings as density rose, and no defect category did consistently more damage than the others, though the study had limited power to detect a difference ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).

## What was measured

Seventy-four functional requirements across four Java game applications, with a fixed prompt template, a fixed code skeleton, and requirement-level JUnit tests. Two models, GPT-4o and DeepSeek-V3, at temperature 0, five runs per configuration. The authors injected smells by hand from a published taxonomy, and a second author independently reviewed each variant to confirm it carried the intended defect and no other ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).

| Application | Model | Clean baseline | Highest density |
|---|---|---|---|
| Snake | DeepSeek-V3 | 64.3% | 52.9% |
| Dice | DeepSeek-V3 | 88.0% | 77.6% |
| Scopa | GPT-4o | 72.5% | 57.5% |
| Snake | GPT-4o | 71.4% | 67.1% |

Arkanoid is not in that table. "For Arkanoid, both LLMs maintained comparatively high performance across all density levels: GPT-4o remained above 88%, while DeepSeek-V3 remained above 90%" ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).

## The study found no category triage signal

Chi-square tests across three categories and two models found no significant aggregate associations and weak effect sizes. The smallest uncorrected p-value was lexical smells with DeepSeek-V3 on Snake, at p=0.0098 and Cramér's V=0.577. It still did not clear the corrected threshold of roughly 0.0021 ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)). The authors conclude that "no category produced a consistently larger decrease in test-suite-based functional correctness."

So this study gives no basis for a repair queue sorted by defect type. Higher density was generally associated with lower correctness, but the magnitude and consistency varied across applications and LLMs, and no density correlation survived correction either.

## What the example shows

The paper's own example shows the kind of edit involved. The weak-verb variant "replaces a precise numerical threshold with the vague expression 'sufficient to win', increasing interpretive flexibility while preserving grammatical correctness" ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)). The number is gone from the sentence.

Independent specification layers absorb the same class of degradation, which is why identical mutations that hurt on a single-docstring benchmark are near-flat on a layered one ([Akli et al., 2026](https://arxiv.org/abs/2604.24712v1)). See [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) for how to build those layers.

## When this backfires

- Another specification layer already carries the value. Where a prompt layers description, constraints, examples, and I/O format, the under-specification mutations that cost 11.8% of Pass@1 on a single-docstring benchmark produce near-zero net effect ([Akli et al., 2026](https://arxiv.org/abs/2604.24712v1)). Find what else pins the value before you rewrite the sentence.
- Expecting every application to decline. Arkanoid held above 88% at every density level, and the descriptive decreases were more evident for Snake and Scopa. The authors offer interconnected behavior as one possible explanation for those two and call it a hypothesis for future work ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).
- Treating a clean requirement as a correctness guarantee. On clean Scopa requirements GPT-4o averaged 72.5% with a standard deviation of 15.0 percentage points across five runs, and the authors state that "clean requirements alone do not guarantee complete functional correctness" ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).
- Reading the declines as an effect size. No correlation survived correction for multiple comparisons. The authors are explicit that power was limited and that "non-significant results should not be interpreted as evidence of the absence of an effect" ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).
- Generalizing past the setting. The paper covers four game applications with "relatively short and well-scoped functional requirements". It tests two models, one proprietary and one open-weight, and the authors say this limits generalizability. The defects were injected deliberately, not collected from a real requirements process ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)).

## Example

Requirement 12 of the Dice application, in both the clean and the injected form used in the experiment ([Villamizar et al., 2026](https://arxiv.org/abs/2609.29208v1)):

**Before** — clean:

```
If a player's points get above 11, his point color shall turn purple.
```

**After** — weak-verb smell injected:

```
If a player's points are sufficient to win, his point color shall turn purple.
```

The injected version replaces the numeric threshold with the vague expression "sufficient to win" and stays grammatical.

## Key Takeaways

- Do not sort a repair queue by defect type on this evidence. The experiment found no category that consistently did more damage, and its density pattern is descriptive only.
- Check whether a test, type, or schema already pins the value before rewriting a vague requirement.
- Budget for failures on clean input. One model averaged 72.5% on defect-free requirements with a 15.0-point standard deviation across identical runs.
- Cite this evidence as a direction of effect. Nothing in it survived correction for multiple comparisons, and the authors say so themselves.
- The paper's weak-verb example replaces a number with a phrase and leaves the sentence grammatical.

## Related

- [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) — why a layered specification absorbs the same defect that hurts a single-sentence one
- [Ambiguity Stability as a Model-Selection Criterion](../verification/ambiguity-stability-model-selection.md) — ranking models on their drop between clear and ambiguous requirements, once the requirements you can repair are repaired
- [Standard-Grounded NFR Specs: Quality Up, Correctness Flat](standard-grounded-nfr-specification.md) — the same question for non-functional requirements, with a different answer on correctness
- [The Specification as Prompt](specification-as-prompt.md) — pointing at the type or schema instead of describing it, which removes the sentence that could carry a smell
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — the opposite failure, where adding constraints rather than losing detail is what breaks compliance
