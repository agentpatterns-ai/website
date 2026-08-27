---
title: "Match Architecture Spec Format to Model Capability"
term: "Spec Format by Model Tier"
description: "The value of a structured architecture spec runs inverse to model strength: format barely moves a frontier model and decides what a weak one ships."
aliases:
  - architecture spec format by model tier
  - specification format capability equalizer
tags:
  - instructions
  - cost-performance
  - code-generation
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-25
maturity: emerging
---

# Match Architecture Spec Format to Model Capability

> Spec format barely moves a frontier model and decides what a weak one ships. Pick the format from the tier you drive.

The format you write an architecture specification in changes generated code quality in inverse proportion to model strength. A controlled 5x6 experiment covering 90 multi-turn agent trials measured a quality spread across five informationally equivalent formats of 0.17 points on a 10-point scale for Claude Sonnet 4.6, and 1.67 points for Claude Haiku 4.5 in the same vendor family ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Across the two frontier models tested the spread ran 0.17 to 0.92; across the four weaker ones, 0.83 to 2.42 ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)).

## The conditions this depends on

Read the result as an interaction, not as "structure beats prose." It holds for a non-frontier model, on a format close to mainstream software practice, generating a system of moderate size.

The deterministic half of the evidence carries the argument. Of 25 specified API routes, Gemini 2.5 Flash implemented 33% from informal prose and 100% from TypeScript interface contracts, while Sonnet 4.6, Haiku 4.5, and GPT-5 reached 100% from every format ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). The authors report no significance tests, because three trials per cell leaves the quality scores underpowered ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Route coverage is a census count of a fixed list, so it survives that limitation and the score deltas do not.

## Why it works

Prose asks the agent to invent an architecture and then implement it. A TypeScript interface hands over the architecture already in the target shape, because "TypeScript interfaces do not require the agent to translate between a human-readable description and an implementation structure; the specification is the structure" ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Frontier models perform that translation reliably, so deleting the step buys them nothing you can measure. Weaker models lose routes and components while doing it.

## Choosing by tier

| Model tier | Format that pays | Evidence |
|---|---|---|
| Frontier (Sonnet 4.6, GPT-5) | Prose | Spread of 0.17 to 0.92 points; on Sonnet, prose ran 433K tokens against Mermaid-with-constraints' 1,060K for scores of 8.42 and 8.50 |
| Mid (Haiku 4.5, GPT-5-mini, Gemini 2.5 Pro) | OpenAPI or TypeScript contracts, called "the safest choices across vendors" | Spread of 0.83 to 2.42 points; GPT-5-mini drops to 85% route coverage on prose and holds 100% on any structured format |
| Small (Gemini 2.5 Flash) | TypeScript contracts with ArchUnit-style rules | Route coverage 33% on prose, 100% on contracts |

The paper's own guidance reads the same way: prose is "sufficient and most cost-efficient" at the frontier, structured specs give mid-tier models "measurable improvement," and for the smallest model "structured specifications are essential," with TypeScript contracts the only format reaching full route coverage ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)).

The pattern is not uniform across vendors. It holds inside Anthropic's line, Sonnet 0.17 against Haiku 1.67, and breaks inside OpenAI's, GPT-5 0.92 against GPT-5-mini 0.83, which the authors read as format sensitivity plateauing above some capability threshold ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Treat the tier boundary as fuzzy.

## When this backfires

- A better spec does not pay for a cheaper model. Haiku 4.5 burned 735K tokens per trial for a 6.50 score where Sonnet 4.6 spent 640K for 8.42, the extra 15% going into repeated compilation attempts (8.6 per trial against 5.1) ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Downgrading the model and upgrading the spec cost more and delivered less on this system.
- Structure on the output runs the other way. Under a four-level schema gradient, Haiku fell 36.2 percentage points under standard token budgets, largely through truncation, and GPT-4o-mini fell 28.0 points even on extended budgets that ruled truncation out ([arXiv:2606.09410v1](https://arxiv.org/abs/2606.09410v1)). Structuring the input is a different lever from constraining the output.
- Neatness is not the mechanism. Across six rounds spanning 11 models, compact constraint headers cut tokens and produced no statistically significant change in constraint satisfaction, at effect sizes below 0.01 ([arXiv:2604.07192v2](https://arxiv.org/abs/2604.07192v2)). What counts is how much architecture the agent still has to reconstruct, covered in [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md).
- The format has to be one the model has seen. The five tested formats sit close to everyday software practice; UML, SysML v2, AADL, CloudFormation, and Terraform were not tested, and the authors name training-corpus prevalence as the open question ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)).
- The model that most needs the spec is least able to check its own work. Demo run rate fell from 100% on Sonnet to 0% on Gemini Flash ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Verification stays yours.

One system was tested, all six models were proprietary, and one author group wrote all five specs ([arXiv:2608.21747v1](https://arxiv.org/abs/2608.21747v1)). Treat the tier table as a starting hypothesis for your own stack, not a settled ranking.

## Key Takeaways

- Decide the spec format after you decide the model, not before. The same document is worth writing twice over for one tier and barely worth proofreading for another.
- Writing a C4 or TypeScript-contract spec for a frontier model is authoring cost for a difference inside the noise.
- Trust the route-coverage numbers over the quality scores; three trials per cell buys no significance test.
- The cheap-model trade did not work here: 15% more tokens, 1.9 points less quality.
- A weak model given a strong spec still will not validate its own output, so keep the tests and the demo run on your side.

## Related

- [The Specification as Prompt](specification-as-prompt.md) — Use types, schemas, and API definitions as instructions rather than prose descriptions.
- [Multi-Layer Specification Redundancy](multi-layer-specification-redundancy.md) — Independent spec layers absorb prompt noise that prose repetition does not.
- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — Reformatting constraints changes tokens, not compliance.
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — Accuracy falls as simultaneous constraint count rises.
- [Utility Model Split](../patterns/agent-design/utility-model-split.md) — Where routing work to a cheaper tier does pay off.
