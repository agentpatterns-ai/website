---
title: "Cross-Framework Signal Semantics: Re-Measure Borrowed Trajectory Rules"
term: "Cross-Framework Signal Semantics"
description: "The same trajectory-shape signal can predict opposite outcomes across agent frameworks. Re-measure borrowed behavioral rules in your own harness before adopting them."
tags:
  - testing-verification
  - agent-design
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-12
maturity: emerging
---

# Cross-Framework Signal Semantics

> Cross-framework signal semantics: a behavioral signal that predicts success in one framework can predict failure in another. Re-measure borrowed signals in your own harness.

Cross-framework signal semantics is the property that operational rules extracted from one agent framework — "test step follows code modification", "short error cascades", "compact trajectories" — often carry different or opposite meaning in another. A 64,380-run analysis across 126 agent configurations spanning 43 frameworks found that on error rate, 47 configurations resolve more issues when the rate is lower while 48 resolve more when it is higher ([Ma et al., 2026](https://arxiv.org/abs/2605.18332)). Five other continuous features and three of seven binary patterns from prior software-engineering agent literature showed the same directional disagreement.

## The 47-vs-48 result

The main finding is a coin flip on direction:

- Error rate: 47 configurations succeed more often when their error rate is low; 48 succeed more often when it is high ([Ma et al., 2026](https://arxiv.org/abs/2605.18332))
- Framework over LLM choice: framework explains 64% of the between-configuration variance for mean turns; LLM choice explains 10% ([Ma et al., 2026](https://arxiv.org/abs/2605.18332))
- Wide scope of disagreement: five other continuous features and three of seven binary patterns from prior software-engineering agent literature show the same directional split ([Ma et al., 2026](https://arxiv.org/abs/2605.18332))

A behavioral rule mined from one framework's runs is not a finding about agents in general. It is a finding about that framework, set by its scaffolding, tools, and error-handling.

## Why it works

Framework choices — which tools are exposed, how observations are formatted, how the agent-computer interface scaffolds turns — shape the trajectory more than the backing LLM does ([Ma et al., 2026](https://arxiv.org/abs/2605.18332)). "Short error cascades correlate with success" emerges because in framework A the harness short-circuits errors and only successful runs reach the cascade-length metric, while in framework B the harness lets errors compound and successful runs accumulate longer cascades. Identical signal, opposite data-generating process. The 64% framework versus 10% LLM variance for mean turns measures this mechanism directly ([Ma et al., 2026](https://arxiv.org/abs/2605.18332)). The SWE-agent paper named the same effect from the design side: "the design of the ACI can impact agents' behavior and performance" ([Yang et al., 2024](https://arxiv.org/abs/2405.15793)).

## How to apply it

Treat any borrowed behavioral rule as a hypothesis until you re-measure it locally:

1. Tag the rule with its origin framework. "Short error cascades predict success" means nothing without "...in SWE-agent v1.2 on SWE-bench Verified" attached. Without that origin, you cannot validate a rule.
2. Re-measure on your harness. Compute the same statistic on your own trajectories before you adopt it as an eval signal or routing heuristic.
3. Prefer mechanism-grounded checks. Signals tied to a falsifiable mechanism ("did the agent run the test command between edit and submission?") transfer better than statistical correlates ("mean turn count"), the same principle behind [behavioral testing for agents](behavioral-testing-agents.md). The mechanism holds across frameworks; the correlate does not.
4. Treat split-direction signals as warnings, not features. When a signal points opposite ways in different harnesses, do not pick a side. Drop the signal from cross-framework comparisons and look for a mechanism-grounded substitute.

This complements [isometric harness ablation](../agent-design/isometric-harness-ablation.md): ablation tells you which of your own subsystems carries weight; signal-semantics validation tells you which of someone else's rules survive the move into your stack.

## When this backfires

Cross-framework validation is overhead, and that overhead is wasted in a few narrow conditions:

- Single-framework teams with no transfer ambition: a team that runs one harness and tunes its eval suite to that harness can ignore generalization, because the question never arises.
- Mechanism-grounded signals: when a signal is tied to a falsifiable behavior ("did the agent run its own tests before claiming done?"), framework variance shrinks, so gating it on cross-framework re-measurement is ceremony.
- Configuration-tweaking inside one framework: comparing two prompt variants in the same harness is not a cross-framework comparison, so applying the warning there freezes routine experimentation.
- Benchmark-quality contamination: the SWE-bench dataset itself has solution leakage and inadequate test cases; resolution rate for SWE-agent+GPT-4 drops from 12.47% to 3.97% under stricter filtering ([Aleithan et al., 2024](https://arxiv.org/abs/2410.06992)). If borrowed signals are contaminated upstream, re-measurement on your harness inherits the same noise, and only mechanism-grounded checks survive it.

## Key Takeaways

- A 64,380-run cross-framework study split 47-vs-48 on whether lower error rate predicts higher resolution; same signal, opposite direction.
- Framework identity explains roughly 6x more between-configuration variance than LLM choice for mean turns.
- Borrowed trajectory rules are hypotheses about your harness, not facts. Re-measure before adopting.
- Prefer mechanism-grounded checks (verify-before-edit, test-runs-before-submit) over statistical correlates (turn count, error rate magnitude) when designing rules meant to transfer.

## Related

- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md)
- [Trajectory-Opaque Evaluation Gap](eval-blind-spots.md)
- [Behavioral Testing for Agents](behavioral-testing-agents.md)
- [Isometric Harness Ablation](../agent-design/isometric-harness-ablation.md)
- [Per-Model Harness Tuning](../agent-design/per-model-harness-tuning.md)
