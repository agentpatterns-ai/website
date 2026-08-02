---
title: "Audit-Budget Allocation for Agent Fleets"
term: "Audit-Budget Allocation"
description: "Screen an agent's self-reported confidence for discrimination before ranking a review queue by it, then allocate the remaining audit budget across correlated agents."
tags:
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - confidence-ranked audit queue
  - oversight budget allocation
  - audit budget for agent fleets
last_reviewed: 2026-08-02
maturity: emerging
status: current
---

# Audit-Budget Allocation for Agent Fleets

> Measure whether an agent's self-reported confidence separates right from wrong on your tasks before you let it order the audit queue.

One person reviewing many agents can inspect only a fraction of the output. Ranking that review queue by stated confidence works only while the score separates correct output from incorrect. Past a threshold it does worse than random, and on five open-weight models tested it carried almost no information ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).

## Screen the signal before you rank on it

Confidence ranking earns its place under two conditions.

The first is discrimination: compute AUROC for the confidence score against observed correctness on your own traffic. Across 20 frontier models from seven families on 524 items, signals passing a validity screen averaged a Type-2 AUROC of .624 against .357 for invalid ones, and the screen explained 47% of AUROC variance ([arXiv:2604.17716](https://arxiv.org/abs/2604.17716v1)). A score near .50 orders nothing.

The second is variance. Under a single-completion prompt at temperature 0, all five open-weight models tested piled confidence at roughly 1.0, with Var(c) at or below 0.016 and AUROC of 0.50 to 0.52 on GSM8K and HotpotQA. The one proprietary model in the set, gpt-4o-mini, reached 0.59 and 0.56 ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)). Do not read this as a rule about open weights. It is a result about small models under one cheap elicitation protocol. Verbalized confidence from RLHF-tuned models such as GPT-4 and Claude beats their own token probabilities, often cutting expected calibration error by a relative 50% ([Tian et al., 2023](https://arxiv.org/abs/2305.14975v2)).

## Two results that invert the intuition

A larger audit budget flips first. The threshold is the fraction of errors whose confidence mimics correct output; past it, ranking loses to random. It sits at 0.93 auditing 2% of the fleet, 0.89 at 5%, 0.84 at 10% and 0.75 at 20%. Tight budgets touch only the extreme low-confidence tail, which stays informative; generous budgets reach the corrupted middle ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).

A second vendor buys less independence than it looks. Once item difficulty is controlled, the extra correlation attributable to shared model lineage was −0.009 (95% CI −0.064 to 0.047) on GSM8K and 0.023 (−0.035 to 0.086) on HotpotQA — both intervals include zero, while raw cross-family correlation ran 0.33 to 0.85 ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)). Shared task difficulty, not ancestry, drives agents to fail together. Note the scope difference from [distillation-induced similarity metrics](distillation-induced-similarity-metrics.md), which finds lineage does shape non-mandatory tool-use behavior.

## Why it works

Ranking by confidence pays off only when the low-confidence tail is enriched in errors, and the mimicry fraction measures how much of that enrichment survives. In the model, errors increasingly draw their confidence from the same high range as correct outputs. More errors then sit above the budget's reach, and the tail the auditor inspects fills with correct-but-diffident output ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)). The blunter mechanism is missing variance, not adversarial mimicry: a near-constant score carries no ordering information, so the queue is random selection with extra machinery. The information exists; the cheap verbal channel does not carry it. On Gemma 3 4B, self-consistency across ten samples scored AUROC2 = 0.999 where single-pass verbal confidence sat near chance ([arXiv:2604.24070](https://arxiv.org/abs/2604.24070v1)). Distilling that signal into a single pass reached AUROC2 = 0.774, but only in a post-hoc rescue after the pre-registered protocol returned a negative result.

## When this backfires

- Your model's confidence has been measured as informative. gpt-4o-mini sat below its flip threshold with positive tail-precision lift, so dropping confidence ranking there discards real precision ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- Your audit budget is very tight. At 2% coverage the flip needs 93% of errors to mimic correct output, so the warning matters least exactly where oversight is thinnest ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- You rotate or fine-tune models often. The paper's correlation-aware alternative relies on error shocks persisting between rounds and collapses when persistence goes to zero ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- Your audits are themselves noisy. In the paper's model an audit returns the agent's true error status flipped with probability ε. At correlation 0.5 the correlation-aware policy loses to confidence ranking once ε reaches 0.2, and it resists that noise only at correlation 0.8 ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- Your agents process disjoint inputs. The reported correlations come from agents answering aligned items, an upper bound for fleets whose agents see different work ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).

The evidence is a modeled inspection setting with replay on recorded traces; the fleet experiment used 15 agents and the authors call it preliminary ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).

## Example

The paper's own measurements, as a reference table for the screening step:

| Model | GSM8K AUROC | HotpotQA AUROC | Usable for ranking |
|---|---|---|---|
| Qwen3-0.6B | 0.50 | 0.50 | No |
| Qwen3-4B | 0.50 | 0.51 | No |
| Qwen3-8B | 0.50 | 0.50 | No |
| Mistral-7B-Instruct-v0.3 | 0.51 | 0.52 | No |
| Phi-4-mini-instruct | 0.51 | 0.50 | No |
| gpt-4o-mini | 0.59 | 0.56 | Yes |

Source: [arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1), 500-item manifests per dataset, temperature 0, one locked single-completion prompt eliciting an answer and a 0 to 100 confidence.

Reproduce this table on your own traffic first: sample outputs, label each correct or incorrect, and compute AUROC of the stated confidence against that label. At 0.50, round-robin sampling gives the same coverage with less machinery.

## Key Takeaways

- Treat confidence-ranked auditing as a claim to verify, not a default. Measure AUROC of stated confidence against observed correctness on your own tasks first.
- Five small open-weight models produced near-constant confidence (Var(c) at or below 0.016, AUROC 0.50 to 0.52), so a queue ordered by it is random selection in disguise ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- A larger audit budget flips to worse-than-random sooner: the threshold falls from 0.93 at 2% coverage to 0.75 at 20% ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- Shared item difficulty dominates model lineage in correlated errors, so a second vendor's model is weaker independent verification than it appears ([arXiv:2607.28317](https://arxiv.org/abs/2607.28317v1)).
- The collapse is partly an elicitation artifact. Self-consistency across samples discriminates far better than single-pass verbal confidence on the same items ([arXiv:2604.24070](https://arxiv.org/abs/2604.24070v1)).

## Related

- [Model Confidence as Security Verification (Security Calibration Gap)](../patterns/anti-patterns/model-confidence-as-security-verification.md) — endorses confidence as a triage signal; this page makes that triage use conditional on measured discrimination
- [Distillation-Induced Similarity Metrics for Tool-Use Agents](distillation-induced-similarity-metrics.md) — the behavioral side of correlated failure, and a scope contrast on how much model lineage explains
- [Risk-Score Threshold Calibration for Auto-Approval](../code-review/risk-score-threshold-calibration.md) — the same allocation problem solved with a learned diff-risk score instead of the model's own confidence
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md) — what to do with the audit budget the screening step frees up
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md) — the human-side framing of the scarce review capacity this page allocates

## Sources

- [arXiv:2607.28317v1](https://arxiv.org/abs/2607.28317v1) — Zavattari, Tommasi and Prencipe (2026): "One Human, N Agents: Audit-Budget Allocation for LLM Agent Fleets under Miscalibrated, Correlated Confidence"
- [arXiv:2604.17716v1](https://arxiv.org/abs/2604.17716v1) — Cacioli (2026): validity screen for LLM confidence signals under selective prediction
- [arXiv:2604.24070v1](https://arxiv.org/abs/2604.24070v1) — Cacioli (2026): distilling self-consistency into verbal confidence on Gemma 3 4B
- [arXiv:2305.14975v2](https://arxiv.org/abs/2305.14975v2) — Tian et al. (2023): "Just Ask for Calibration"
