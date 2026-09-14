---
title: "Model-Set Parity: Reading Harness Efficiency Claims"
term: "Model-Set Parity"
description: "A published cross-harness efficiency figure measures the harness only when both arms run the same models. Change the model set and the number prices a configuration."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - model-set matching
  - matched-arm harness comparison
  - harness efficiency claim parity
last_reviewed: 2026-09-13
maturity: emerging
---

# Model-Set Parity: Reading Harness Efficiency Claims

> A cross-harness efficiency figure measures the harness only when both arms run the same models.

Model-set parity is the condition a published harness comparison must meet before its cost difference can be attributed to the harness: both arms run the same models, and only the orchestration layer differs. It is a rule for reading someone else's figure, not a study design. Cognition's Fusion announcement shows what fails it. The post calls Fusion "the most efficient frontier harness for Fable and Astra, up to 39% more efficient compared to other model harnesses across major coding benchmarks". Every Fusion arm in its charts and tables runs two models against the comparison's one, which the post states plainly: "When selecting Fusion, you pick two models instead of one" ([Cognition, 2026-09-11](https://cognition.com/blog/local-fusion)).

## When the check is worth applying

Apply it when you plan to carry the saving somewhere the published arm does not reach: you want to build or tune your own harness and expect a comparable gain, you run a different model and assume the figure travels, or you are ranking harnesses as components rather than picking between two products as sold. Each of those needs the harness term separated out, and a bundled figure does not separate it. If you will adopt the bundle exactly as shipped and port nothing, the bundled cost per task at comparable score is the right number and this check adds nothing.

## Three things to read off the claim

1. The model set on each side. Count the models, not the model names. An arm that adds a cheaper execution model has changed two variables at once.
2. The benchmark set behind the headline number. A summary figure is usually one cell rather than an average, and "up to" marks a ceiling.
3. The score printed next to the cost. A cost saving with no paired quality number is a bill, not an efficiency result. [Cost-quality Pareto measurement](../../token-engineering/cost-quality-pareto-measurement.md) keeps both on one plot.

## Why it works

Cost per task is the sum, over every model in the configuration, of tokens consumed multiplied by that model's price. Artificial Analysis computes it that way, with "standard input pricing, discounted cached-input pricing, separate cache-write charges, and output pricing" ([Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents)). Moving work onto a second, cheaper model changes that sum whatever the orchestration layer does. An arm that adds a model has therefore moved two terms, and the result belongs to neither on its own.

Gorinova et al. give the general form of the error. A coding agent "is not a model: it is a system harness — a composite of models, harnesses, contexts, environments, and feedback signals, any one of which can move the benchmark score by margins comparable to those between adjacent model generations", so "comparing two such numbers is comparing two systems, not two models" ([arXiv:2606.17799v2](https://arxiv.org/abs/2606.17799v2)). Their remedy states parity as a reporting rule: declare "what model, agent harness version, environment hash, and dataset version were used", and include "at least one ablation across a non-model axis against a fixed baseline".

The lever itself is real once the arms match. Holding Claude Opus 4.6 fixed on Terminal-Bench, "differences of 20 percentage points or more appear across harnesses" ([Gorinova et al.](https://arxiv.org/abs/2606.17799v2)). Parity is what lets you tell that result apart from a model-set change wearing the same headline.

## Example

Cognition published per-benchmark figures for both model pairs, evaluated with Artificial Analysis and Vals AI. Each cell is score followed by cost per task ([Cognition](https://cognition.com/blog/local-fusion)):

| Benchmark | Fable 5.1 | Fusion (Fable 5.1 + SWE-2) | Astra | Fusion (Astra + SWE-2) |
|---|---|---|---|---|
| DeepSWE 1.1 | 64.3 / $14.63 | 63.1 / $7.88 (−46%) | 67.6 / $7.88 | 67.3 / $4.69 (−40%) |
| Terminal-Bench 4 | 57.6 / $17.46 | 56.1 / $13.37 (−23%) | 55.6 / $10.08 | 50.0 / $6.06 (−40%) |
| SWE-Atlas QnA | 64.8 / $7.57 | 65.9 / $5.00 (−34%) | 61.8 / $5.72 | 59.4 / $3.59 (−37%) |
| Vals Code Migration | 54.6 / $70.97 | 57.3 / $42.00 (−41%) | 67.7 / $44.36 | 61.3 / $35.51 (−20%) |
| FrontierCode 1.1 (Extended) | 63.6 / $2.68 | 63.5 / $1.67 (−38%) | 63.1 / $2.62 | 63.4 / $2.34 (−11%) |

Read it against the three checks. Every Fusion column adds SWE-2, so no row is model-set matched. The savings run from 11% to 46% and no row equals the headline, which comes instead from one Artificial Analysis Coding Agent Index cell where Codex on Astra costs $7.47 and Fusion on Astra plus SWE-2 costs $4.54. Score falls in seven of the ten cells, and the two largest drops sit on the Astra pair: 5.6 points on Terminal-Bench 4 and 6.4 points on Vals Code Migration. The index supplying the headline does not isolate the harness either. Its published unit is the agent variant, because "model choice, settings, and execution configuration can materially change outcomes", and its harness comparison section reads "Coming soon" ([Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents)).

None of that makes the result wrong. Cognition argues the coupling is the finding rather than a confound, since "the models' cost and intelligence are coupled" and what matters is "how efficiently the pair completes work together" ([Cognition](https://cognition.com/blog/local-fusion)). The figure supports "this configuration costs less than that one". It does not reach "this harness is more efficient".

## When this backfires

- Architecturally multi-model harnesses. Fusion needs a lead and a sidekick by construction, so a model-set-matched arm is a configuration nobody ships. Demanding one leaves you with no measurement rather than a better one.
- Subscription billing. Artificial Analysis prices per token and says so itself: "Many users will access coding agent harnesses through subscription plan offerings rather than pay-per-token" ([Artificial Analysis](https://artificialanalysis.ai/agents/coding-agents)). Under a seat price, neither shape of comparison predicts your invoice.
- Benchmark sensitivity wider than the gap. The spread above is 11% to 46% across five benchmarks. A matched figure drawn from a benchmark set unlike your work transfers no better than a bundled one.
- Portability you cannot buy either way. Scaffold effectiveness "is not an inherent property of the scaffold" and emerges from how it integrates with the base model, with model swaps moving resolve rate 2 to 3x at a fixed scaffold ([Gorinova et al.](https://arxiv.org/abs/2606.17799v2), reporting Fan et al., 2025). A matched result can still die on a model swap, which is why [running your own attribution](fleet-harness-attribution.md) beats reading anyone's headline.

## Key Takeaways

- An arm that adds a cheaper execution model moves the bill on its own, so a figure comparing it to a single-model arm cannot be attributed to the harness.
- "Up to" marks a ceiling from one cell. Cognition's five-benchmark table spreads from 11% to 46%, and no row equals the 39% headline.
- A cost figure with no paired score hides trades like Terminal-Bench 4 falling from 55.6 to 50.0 for a 40% saving.
- The bundled number is the correct one when you will buy the bundle as shipped. The parity check earns its cost only when you plan to port the saving.

## Related

- [Fleet Harness Attribution](fleet-harness-attribution.md) — the method for producing a matched comparison yourself across a model fleet.
- [Harness-Controlled Token Economics](../../token-engineering/harness-token-economics.md) — what the harness lever is worth once the model is genuinely held fixed.
- [Isometric Harness Ablation](isometric-harness-ablation.md) — pinning the model and removing one subsystem at a time to rank investment.
- [Cost-Quality Pareto Measurement](../../token-engineering/cost-quality-pareto-measurement.md) — keeping score and cost on one plot so a quality trade stays visible.
- [Pricier Per Token, Cheaper Per Task](../../token-engineering/pricier-per-token-cheaper-per-task.md) — the lead-model result inside the same Fusion architecture.
