---
title: "Constraint Preambles and the Gain Your Scanner Misses"
term: "Constraint Preamble"
description: "A fixed list of output constraints before every generation cut named defect classes in all five models tested, and the biggest wins are ones no scanner sees."
aliases:
  - Specification Frame
  - Fixed Constraint Preamble
tags:
  - instructions
  - code-generation
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-22
maturity: emerging
---

# Constraint Preambles and the Gain Your Scanner Misses

> A fixed constraint preamble moved named defect classes in all five models tested, and your scanner cannot see most of the gain.

A constraint preamble is a short fixed block of text stating what must be true of the generated code, prepended unchanged to every generation prompt. Money is not a float. Timestamps carry a zone. A retryable handler checks an idempotency key. It says nothing about how the team works. That is what separates it from repository context files, where "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average" ([arXiv:2602.11988v2](https://arxiv.org/abs/2602.11988v2)).

## The conditions this depends on

Four conditions bound the result to a narrow floor rather than a quality control.

Generation is single-turn. The evidence covers one stateless call per prompt, no tools and no retrieval ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)). In a long agent session the picture inverts for the prohibition-shaped rules. On Mistral Large 3, "omission compliance falls from 73% at turn 5 to 33% at turn 16 while commission compliance holds at 100%" ([arXiv:2604.20911v1](https://arxiv.org/abs/2604.20911v1)).

The defect classes are named in advance. Nine checkers reading the abstract syntax tree scored nine classes, and correctness was never scored, so a module can clear all nine and still be wrong ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

The task does not already carry the constraint. The two tasks whose own prompt text named a time zone produced zero findings in every model and in both arms ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

The model has weak defaults here. Effect size ordered monotonically against bare-arm weakness: 0.16 findings per task for the cleanest baseline, against 0.70 and 0.68 for the two weakest ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

## What was measured

Fifty regulated-backend tasks ran through five models from five vendor lineages, each task twice, bare and behind a 267-word preamble, for 500 one-shot generations. Hypotheses, refuters, checkers and analysis code were pre-registered on 18 August 2026 under a rule forbidding regeneration of any output ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

| Domain | Bare findings | Preamble findings |
|---|---|---|
| Money | 66 | 8 |
| Idempotency | 32 | 2 |
| Date and time (DA tasks) | 31 | 5 |
| Authentication and access | 19 | 8 |

Every model showed a positive mean paired difference, a bootstrap confidence interval excluding zero, and a significant Holm-adjusted sign test. It also tied 150 of the 250 pairs, and of the 100 that differed the preamble arm won 95 ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

## Why it works

The preamble supplies a constraint the model's unprompted default does not carry, in proportion to how much is missing. Two findings argue against the simpler story that any 267 words buy more deliberation. The checkers score behavior such as `Decimal` arithmetic and aware datetimes, which a model has no reason to adopt from extra thinking alone. And the timezone null above is "what a content account predicts and a deliberation account does not" ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)). The confound is not closed: no length-matched neutral preamble and no reason-first arm was run.

## Measure it with checkers, not a scanner

Money arithmetic and idempotency accounted for 88 of the 125 findings the preamble removed, and idempotency "has no CWE and lies outside the rule sets of security scanners such as Bandit, which is one reason tooling has not caught it" ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)). Judge this intervention on scanner output and you are reading the one instrument that cannot see most of the effect. Bandit did register the rest, falling from 53 medium-or-high findings to 11, which is why it works as corroboration and not as the primary measure ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)). Write a few syntax-tree checks for your own domain rules and run them beside the scanner.

## When this backfires

- Long agent loops. The constraint text drifts back through the context window and the prohibition-shaped rules decay first ([arXiv:2604.20911v1](https://arxiv.org/abs/2604.20911v1)). Re-inject before the depth where compliance drops, or write the rules in requirement form.
- A model that already has the habit. The cleanest model's 0.16 came with the only marginal p value in the set, 0.021 ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)). Measure your own baseline before paying 267 tokens on every call.
- Classes a generic constraint cannot reach. Authentication and access moved least, 19 findings to 8, and the study names open redirects and path traversal as "the kind that a generic constraint may not fully reach" ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).
- Treating it as a security control. Explicit security instructions have moved a formally verified vulnerability rate "by only 4 points" against a 55.8% baseline ([arXiv:2604.05292v2](https://arxiv.org/abs/2604.05292v2)). This is a floor on named classes, not a gate.
- Silent functional regression. No functional tests were run. A post hoc byte-compile check found 236 of 236 complete preamble-arm outputs compile, which says nothing about what they do ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

One caveat on provenance. The author wrote the book that introduced this preamble and designed the nine checkers, and discloses both. The instrument-blind scanner and the 500 raw outputs under a DOI are the mitigations, so the result is re-derivable without trusting him ([arXiv:2609.23270v1](https://arxiv.org/abs/2609.23270v1)).

## Key Takeaways

- State what must be true of the output, not how the team writes code. The artifact class is the whole difference between this result and the instruction-file null.
- Expect nothing on most tasks. Sixty percent of pairs tied, and the value sits in the tail where a model would otherwise ship float money.
- Your scanner will under-read the gain, because the two classes that moved most have no CWE between them.
- The weaker the model behind your tooling, the more this buys. Vendors rotate models under fixed product names, so the floor is the part you own.
- Nothing here licenses skipping tests or review, and functional correctness was not measured at all.

## Related

- [The Specification as Prompt](specification-as-prompt.md) — Point the agent at a formal artifact that already exists, instead of writing the constraints in prose.
- [Match Architecture Spec Format to Model Capability](spec-format-by-model-tier.md) — The same inverse-capability shape, measured on architecture spec format rather than a fixed preamble.
- [Standard-Grounded NFR Specs: Quality Up, Correctness Flat](standard-grounded-nfr-specification.md) — Per-requirement enrichment that cuts static defect density and leaves correctness flat.
- [Evaluating AGENTS.md Context Files](evaluating-agents-md-context-files.md) — The instruction-file null this result is answering.
- [Prompt as Security Knob](../patterns/anti-patterns/prompt-as-security-knob.md) — Why none of this makes the prompt a security guarantee.
