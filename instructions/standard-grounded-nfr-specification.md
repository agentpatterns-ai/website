---
title: "Standard-Grounded NFR Specs: Quality Up, Correctness Flat"
term: "Standard-Grounded NFR Specification"
description: "Grounding a non-functional requirement in a published quality model cuts static defect density and prompt-wording variance, but leaves functional correctness flat."
aliases:
  - ISO-Grounded NFR Specification
  - Quality-Model-Grounded Requirements
tags:
  - instructions
  - code-generation
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-17
maturity: emerging
---

# Standard-Grounded NFR Specs: Quality Up, Correctness Flat

> Grounding a non-functional requirement in a published quality model lowers static defect density and stabilizes output across rewordings. Correctness stays flat; error handling regresses.

A standard-grounded NFR specification replaces a one-line quality phrase such as "make it performant" with a paragraph or object that names the ISO/IEC 25010 characteristic and spells out intent, constraints, and acceptance criteria. In a controlled comparison on HumanEval, that enrichment cut unreadability density across all four requirement types tested and shrank the spread of results across ten rewordings of the same requirement. Pass rates held steady everywhere except error handling, where they fell ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)). Treat it as a trade you make deliberately.

## What was measured

The baseline is not free either: stating a non-functional requirement at all cut Pass@1 by up to 39% and raised standard deviation from 0.48 to 2.48 against a function-only prompt ([Lin et al., 2025](https://arxiv.org/abs/2503.22851v2)).

The study compared three ways of stating the same requirement on HumanEval's 164 tasks with the HumanEval-ET extended oracles, using gpt-5.4-2026-03-05 at temperature 0: a terse one-line phrase in the RobuNFR style, an ISO/IEC 25010:2023-grounded paragraph, and the identical ISO content serialized as a JSON object carrying the same five fields (attribute, intent, ISO mapping, constraints, acceptance criteria). Four requirement types (performance, error handling, code smell, readability) each ran with ten wording variations per condition, analyzed with paired Wilcoxon signed-rank tests and Holm–Bonferroni correction ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

| Measure | One-line phrase | ISO-grounded prose | Change |
|---|---|---|---|
| Unreadability density, performance | 0.88 | 0.69 | −22% |
| Unreadability density, error handling | 0.57 | 0.42 | −26% |
| Pass@1 standard deviation across wordings, performance (descriptive) | 0.0158 | 0.0057 | −64% |
| Extended-test pass rate, error handling | 81.0% | 76.0% | −5 points |

Unreadability density counts Pylint convention findings per ten lines, a static maintainability proxy rather than something a reviewer feels. The third row is descriptive only: on per-problem Pass@1 standard deviation the paired test does not survive Holm correction (performance p=0.044). Unreadability standard deviation is the stability result that does, falling for every intervention–baseline pair at p_Holm<0.05. The last row is the one that hurts: for error handling the enriched specification also dropped Pass@1 from 95.1% to 92.3% ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

## Serialization is not the lever

Hold the ISO content constant and prose versus JSON differ by at most 0.023 in effect size on correctness ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)). Choose the format your tooling already parses. It extends the [constraint encoding compliance gap](constraint-encoding-compliance-gap.md) result for constraint blocks: reformatting moves nothing, so effort belongs in what the requirement says.

## Why it works

The enrichment constrains interpretation without touching functional synthesis. ISO-grounded specifications add constraints and acceptance criteria that stay attribute-specific, limiting nesting depth for readability being the paper's own example, and never reference test passage. That steers generation toward implementations with fewer Pylint convention findings while leaving the synthesis of correct behavior alone ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

The stability comes from the same anchoring. Fixed template text acts as a semantic anchor, so the model converges on similar static patterns whatever the surface phrasing. The enriched prompts had lower lexical diversity than the baseline (Jaccard 0.10 to 0.13 against 0.44 to 0.59) yet produced lower quality variance, so the lower variance is not explained by more varied prompt text alone. The authors do not eliminate that confound: part of the diversity gap is shared ISO template boilerplate, and the Jaccard measure itself mixes surface variation with fixed template text ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

For error handling the mechanism inverts. Explicit fault-tolerance criteria elicit defensive try/except structures that satisfy the static criteria and violate exact-output oracles; exception density rose from 0.99 to 1.18 as the extended-test pass rate fell ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

## When this backfires

- Fault-tolerance requirements judged by exact-output tests. Both pass rates fell, and the authors warn that the extra exception statements may be broad try/except blocks with no genuine fault tolerance ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).
- Smaller or older models. Serialization neutrality was measured on one frontier model at temperature 0; prompt template alone moved GPT-3.5-turbo code translation by up to 40%, while GPT-4 held steadier ([He et al., 2024](https://arxiv.org/abs/2411.10541v1)).
- Teams with no quality model to draw on. The authors scope the payoff to organizations already maintaining quality models, architecture portals, or model-driven pipelines, and say one-line requirements may suffice for one-off scripts ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).
- Task descriptions that are already rich. Under-specification mutations that degrade HumanEval have near-zero net effect on the structurally richer LiveCodeBench, because redundancy across descriptions, constraints, examples, and I/O conventions already absorbs them ([Akli et al., 2026](https://arxiv.org/abs/2604.24712v1)).
- Anything above a single function. The findings are bounded to function-level static quality and prompt sensitivity, and HumanEval's exact-output oracles are only weakly sensitive to system-level quality characteristics ([Pereira and Garcia, 2026](https://arxiv.org/abs/2608.13742v1)).

## Key Takeaways

- Ground the requirement in a published quality model when you want fewer static maintainability findings and repeatable output across rewordings, and accept that pass rates will not improve.
- Do not spend time choosing between JSON and prose. With content held constant the two are indistinguishable on correctness.
- Exempt error handling from the enrichment when exact-output tests are your oracle, or review the generated exception structures against project-specific tests instead.
- The improved metric is Pylint output, so a linter in CI enforces it deterministically and for free. Reach for the enriched prompt when you also want the variance reduction, which a linter cannot give you.
- The evidence covers one model, one benchmark, and single-function tasks, so verify on your own workload before rolling it across a codebase.

## Related

- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — the same format-is-not-the-lever result for constraint blocks, with the token-budget case for compact encoding
- [Constraint Degradation in AI Code Generation](constraint-degradation-code-generation.md) — what happens when the enriched requirement pushes total constraint count past the ceiling
- [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) — why an already-redundant specification absorbs wording noise on its own
- [Standards as Agent Instructions](standards-as-agent-instructions.md) — pointing agents at a precise standards document rather than paraphrasing it into a prompt
- [The Specification as Prompt](specification-as-prompt.md) — the general case for reusing an existing formal artifact instead of describing it in prose
