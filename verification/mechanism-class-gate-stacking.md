---
title: "Choose Agent Gate Layers by Mechanism Class, Then Measure"
term: "Mechanism-Class Gate Selection"
description: "Two LLM judges stacked over 560 agent actions labeled block composed to 1.2 to 1.4 independent layers; a regex layer plus one judge reached 1.9 to 2.1."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - mechanism-class gate selection
  - multiplication-equivalent layers
  - gate stack independence
last_reviewed: 2026-10-07
maturity: emerging
---

# Choose Agent Gate Layers by Mechanism Class, Then Measure

> Two LLM judges over 560 block-labeled agent actions composed to 1.2 to 1.4 independent layers. A rule layer plus one judge reached 1.9 to 2.1.

Stacked runtime gates for agent tool calls multiply their error rates only when their layers fail on different properties of the input. Four LLM judges reading the same action text do not, so a second judge behind the first cuts the joint leak by much less than multiplication predicts. A rule layer paired with one judge came close to the prediction on the same cases. Both readings come from 1,119 labeled agent actions across three corpora, 560 labeled block, with no adaptive adversary ([Yang, 2026, arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).

## The conditions that bound the rule

Three conditions carry the rule, and the measurement says nothing outside them.

- Both layers are competent on the traffic you gate. The same rule layer missed 46 of 87 block cases on the held-out cloud, identity and CI corpus, and the paper discards the independence it measured there: "independence at a 53% marginal miss rate buys nothing" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).
- No attacker is adapting to your rules. "An attacker who knows the rules can write an action that none of them matches," and the numbers "bound nothing about an attacker who targets the joint miss set" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)). Tuned adaptive attacks bypassed 12 recent defenses "with attack success rate above 90% for most" ([Nasr et al., 2025, arXiv:2510.09023v1](https://arxiv.org/abs/2510.09023v1)).
- You read the null as a null. The pre-registered equivalence tests failed, and the authors declined to substitute one that passed: "no coupling was detected and the point estimates sit at zero. Independence was not established" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).

## What the measurement showed

| Two-layer stack | Multiplication-equivalent layers (STRICT) | Floor under perfect coupling |
|---|---|---|
| Two LLM judges | 1.22 to 1.44 | 1.02 to 1.17 |
| Rule layer plus one judge | 1.86 to 2.09 | 1.01 to 1.09 |

Source: [arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1), Table IV, 560 block cases. Two layers whose errors multiply read 2.

Pairwise miss correlation splits the same way. Under the same strict definition, judge pairs sit at a median phi of +0.430 with 6 of 6 significant, and rule-by-judge pairs at +0.014 with 0 of 4 (Fisher's exact test, Holm corrected over ten pairs). The separation is narrower than that sounds, because the intervals separate on pooled data only. Per corpus, the point estimates split and the intervals overlap.

## Solo accuracy is the wrong number to read

A cloud rule pack cut the rule layer's solo miss rate from 0.139 to 0.111, a 20% relative improvement, and added nothing to a three-judge stack. Summed over the four three-judge baselines, the rule layer's new coverage was 86 cases under STRICT before and after the pack (31 under PRIMARY), "identical case for case" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)). The pack caught only rule misses the judges already caught.

The error runs in the other direction too. A 50-pattern blocklist that missed 85.7% of block cases on its own still caught 9 cases the three-judge baselines leaked. Report what a candidate layer adds to the stack you already run, and treat its solo number as an answer to a different question.

## Why it works

Two gates fail together when one property of the input defeats both. Chat judges reading the same action share a pre-training distribution and a semantic read of risk, the same coupling the judge-panel literature reports without reference to gates. Nine frontier judges from seven model families "effectively provide only about 2 independent votes' worth of information" ([Kohli, 2026, arXiv:2605.29800v1](https://arxiv.org/abs/2605.29800v1)), and across "over 350 LLMs overall", "larger and more accurate models have highly correlated errors, even with distinct architectures and providers" ([Kim et al., 2025, arXiv:2506.07962v1](https://arxiv.org/abs/2506.07962v1)). A regular-expression matcher consumes no model output and fails on a different question: whether a literal pattern appears.

Half of the mechanism is open. Stratifying judge pairs by case difficulty leaves the share of coupling that difficulty explains between 31.8% and 61.8%, so the residual "cannot be read as evidence that a shared mechanism exists" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)). Whether the within-judge coupling is shared difficulty or shared mechanism is unresolved.

## When this backfires

Three habits make the rule mislead you instead of help.

- Your metric credits escalation to a human as a catch. One judge returned a review verdict on 47 of 560 block cases against 2 to 17 for the others, and that accounting rule reversed five conclusions, each time flattering the judge that deferred. "In a stack with no human layer to absorb the escalation, that layer contributes nothing" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).
- You improve a layer rather than adding a different one. Gains along a layer's own mechanism axis land on cases the other layers already catch, which leaves the stack unchanged and moves the layer toward the coupled band ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).
- You stretch either result past its evidence. The zero-added-coverage finding covers one pack and 17 newly caught cases under STRICT (19 under PRIMARY), all but two on the external corpus, and mechanism distance is sampled at two points: "Two configurations do not make a gradient, and none is claimed" ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).

## Example

The instrument is arithmetic over counts you already log: the multiplication-equivalent layer count is the log of the joint miss rate divided by the log of the geometric mean of the per-layer miss rates ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)).

```python
import math

def n_mult(per_layer_miss_rates, joint_miss_rate):
    """Read a joint miss rate as a number of independent layers."""
    logs = [math.log(p) for p in per_layer_miss_rates]
    geometric_mean = math.exp(sum(logs) / len(logs))
    return math.log(joint_miss_rate) / math.log(geometric_mean)

# Two judges, each missing 10.5% of block cases alone, missing 5.2% together.
n_mult([0.105, 0.105], 0.052)   # 1.31

# Rule layer at 13.4% and one judge at 10.5%, missing 1.3% together.
n_mult([0.134, 0.105], 0.013)   # 2.04
```

Both calls use the study's own counts under its primary miss definition ([arXiv:2610.07359v1](https://arxiv.org/abs/2610.07359v1)). Record the floor beside the number: under perfect coupling the value is 1 only when the layers' miss rates are equal, and it rises as they spread apart, reaching 1.54 to 1.73 on the corpus where the rule layer missed half the cases.

## Key Takeaways

- Count a stack's layers by mechanism class, not by how many boxes the diagram has. Two chat judges over the same action text were worth about 1.3 layers.
- Measure what a candidate layer adds to the stack you already run. A 20% relative gain in solo miss rate bought zero new coverage, and the worst solo layer in the study still caught 9 leaked cases.
- Fix the accounting rule for escalation before reading any stack number. Counting a hand-off to a human as a catch reversed five conclusions in one study, every time in favor of the layer that deferred most.
- Independence measured on a fixed corpus is not protection against an attacker aiming at the joint miss set. Nothing here was collected against one.

## Related

- [Per-Layer Suppression Accounting in Acceptance Gates](per-layer-suppression-accounting.md) — attributes work inside one gate, where this page measures correlation between two; its deterministic layer suppressed nothing, which is the same lesson read from the other end
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the general case for hard checks around agent output, of which the rule layer measured here is one instance
- [Layered Accuracy Defense for Reliable Agent Outputs](layered-accuracy-defense.md) — assumes each layer catches what the previous one missed; this measurement says when that assumption survives
- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — the within-class half in its own right, including why scaling a judge panel does not fix correlated errors
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](../security/hybrid-deterministic-semantic-tool-authorization.md) — asserts that the two mechanism classes cover orthogonal attack surfaces; this is the measurement of that claim on labeled actions
