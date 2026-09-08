---
title: "Compound Prompt Constraints Degrade More Than Their Parts Predict"
term: "Compound Prompt Constraints"
description: "Prompt constraints that each test clean can combine into a super-additive accuracy loss, and whether they do depends on the model family rather than on model size."
tags:
  - anti-pattern
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - super-additive constraint degradation
  - compound constraint interaction
  - single-factor prompt validation
last_reviewed: 2026-09-05
maturity: emerging
---

# Compound Prompt Constraints Degrade More Than Their Parts Predict

> On the GPT-4o family, stacking JSON output, a persona, and urgency cost up to 12.2 points of pass@1 beyond what the single constraints predict.

Constraint effects do not add, and how far they miss is a property of the model rather than of the constraints. Jadhav and colleagues crossed output format (none, JSON, XML), persona (none, generic developer, senior expert), and urgency (none, moderate, extreme emergency) over all 164 HumanEval+ problems and five OpenAI models, for 22,140 greedy-decoding evaluations in a 3x3x3 design ([Jadhav et al., arXiv:2609.03156v1](https://arxiv.org/abs/2609.03156v1)). Each compound condition carries an additive prediction from its own single-factor measurements, and the residual against that prediction is the finding.

## Where this applies

Check your model family before reading further, because the GPT-4.1 family barely moves. Average three-way interaction, from Table I ([arXiv:2609.03156v1](https://arxiv.org/abs/2609.03156v1)):

| Model | Baseline pass@1 | Average 3-way interaction | Super-additive conditions |
|---|---|---|---|
| GPT-4o-mini | 73.8% | -7.6 pp | 8 of 8 |
| GPT-4o | 79.3% | -4.2 pp | 5 of 8 |
| GPT-4.1-mini | 87.2% | +1.7 pp | 0 of 8 |
| GPT-4.1 | 89.6% | +1.3 pp | 2 of 8 |

On GPT-4.1-mini "no pairwise comparison reached significance (p>0.05 for all)", which the authors put down to the GPT-4.1 family having been "explicitly optimized for instruction-following fidelity". The fifth model, o3-mini, runs the other way: its unconstrained baseline was 59.8% and "performance increased dramatically with any structured output constraint (JSON: 88.6%, XML: 88.1%), an improvement of approximately 11 pp". The two figures use different reference points: 59.8% is the all-none cell, while the 11 pp is the marginal effect of adding a format. Size does not predict who is affected, since GPT-4o-mini and GPT-4.1-mini sit at the same parameter scale and land on opposite sides.

## The pattern

The trap is that the individual measurements look fine or better than fine. For GPT-4o-mini, XML alone moved pass@1 from 78.1% to 82.0% and extreme urgency alone moved it from 76.6% to 80.2%; persona cost at most 1.7 points, falling from 79.5% with none to 77.8% with the expert framing ([arXiv:2609.03156v1](https://arxiv.org/abs/2609.03156v1), Table II). Two of the three constraints helped when measured alone, and the third barely registered.

Combined, they did not. JSON plus expert persona plus moderate urgency was predicted at 85.4% pass@1 and measured at 73.2%, a residual of -12.2 pp and the largest interaction in the study. Format choice shifted the size of that residual: JSON combinations averaged -10.7 pp against XML's -4.6 pp.

A team that A/B tests each constraint on its own, ships the union, and never measures the union has validated a prompt it does not run.

## Why it works

The paper does not settle the mechanism and says so, listing "mechanistic analysis of why certain architectures resist compound constraints while others do not" as future work. Its hypothesis is format-specific overhead: JSON escape sequences and brace matching cost more than XML tag wrapping, and that cost "compounds more heavily with concurrent persona and urgency processing" ([arXiv:2609.03156v1](https://arxiv.org/abs/2609.03156v1)).

Better evidence sits in an adjacent study. Fan isolated two causes of format-induced loss, truncation and capacity competition, and found both are capacity effects rather than format effects. Raising Claude Haiku 4.5's token budget from 2048 to 8192 took its JSON accuracy from 52.5% to 84.0%, and "even with extended budgets eliminating truncation, GPT-4o-mini drops 28.0pp", which Fan reads as "pure capacity competition independent of token exhaustion" ([Fan, arXiv:2606.09410v1](https://arxiv.org/abs/2606.09410v1)). Fan's summary: "the same JSON schema is absorbed without cost by capable models while severely degrading weaker ones". Finite generation capacity predicts both observations here, because constraints draw on one pool and the headroom differs by model.

## When this backfires

Auditing compound prompts is not free, and several conditions make it a waste.

- Your model already resists, or inverts. Moving from GPT-4o-mini to GPT-4.1 recovers 15.8 points of baseline accuracy, larger than the worst interaction in the study and cheaper than a factorial sweep. Going the other way, stripping the format constraint from o3-mini gives back the roughly 11 points structure bought it. [Pressured Prompt Framing](pressured-prompt-framing.md) reaches the same conclusion from a different study: settle model choice before touching wording.
- The prompt carries one constraint. There is no second factor and nothing to interact.
- Length is confounded with constraint count, and the authors concede it: "prompt token length is confounded with constraint intensity". They call the confound inherent, since real compound prompts are longer precisely for holding more constraints. Your A/B may be measuring tokens.
- Your harness has no format-aware extraction. The study needed a four-stage fallback and specific handling for double-escaped newlines, which "cause near-zero pass rates if left uncorrected". Without it you grade your parser and call the number reasoning.
- Token budget is the real cause. Haiku's 36.2 pp JSON drop was "largely due to truncation", and raising max tokens alone "recovers most of the JSON penalty" ([arXiv:2606.09410v1](https://arxiv.org/abs/2606.09410v1)). Check that first.

The individual axes are contested too. Tam and colleagues found format restrictions lower reasoning accuracy across models ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)), while Deaconu and colleagues measured urgency framing lowering correctness on five open-weight models, the opposite sign to the urgency result here ([arXiv:2608.11513v1](https://arxiv.org/abs/2608.11513v1)).

## Example

**Before — three separately validated constraints assembled into one prompt:**

```text
You are a senior developer with 15 years of experience.
This is moderately important, please be careful.
Return your answer as JSON: {"code": "<your solution>"}

<HumanEval+ problem>
```

The three lines render the study's expert-persona, moderate-urgency and JSON-format levels rather than quoting its prompt text. Each passed its own check. That combination measured 73.2% pass@1 on GPT-4o-mini against an additive prediction of 85.4% ([arXiv:2609.03156v1](https://arxiv.org/abs/2609.03156v1)).

**After — the format constraint moved out of the generation step:**

```text
<HumanEval+ problem>

Solve it. Explain your reasoning first, then give the final function.
```

A second call or a parser applies the JSON wrapper, so the prompt that has to reason no longer carries it. Fan reports this ordering recovering 80-87% of the lost accuracy on capacity-limited models ([arXiv:2606.09410v1](https://arxiv.org/abs/2606.09410v1)).

## Key Takeaways

- Run one A/B on the assembled prompt against a stripped variant. That single comparison is what the 27-cell factorial buys you, and it is the measurement most teams are missing.
- Re-run that A/B on every model swap. The residual is a property of the model family, so a migration invalidates the result rather than inheriting it.
- Move the format wrapper to a second call or a parser when the A/B comes back negative, before you start rewording the persona or the urgency line.
- Prefer XML to JSON for any format constraint that has to stay in the reasoning prompt.
- Raise the token budget and build format-aware extraction first. Both produce interaction-shaped numbers that are not interactions.

## Related

- [Constraint Degradation in AI Code Generation](../../instructions/constraint-degradation-code-generation.md) — the count-based sibling, where accuracy falls as simultaneous constraints grow; its model is additive and cannot express the negative residual this page measures
- [Pressured Prompt Framing](pressured-prompt-framing.md) — the urgency axis on its own, measured on open-weight models with the opposite sign
- [Cross-Component Interference in Agent Scaffolds](cross-component-interference.md) — the same composition failure one layer up, over planning, memory, retrieval and reflection instead of prompt text
- [Agent Extension Conflicts](agent-extension-conflicts.md) — the same failure at the extension boundary, where per-extension evals miss the combination
- [The Instruction Compliance Ceiling](../../instructions/instruction-compliance-ceiling.md) — what happens to rule following as instruction count rises, the behavioral counterpart to this page
