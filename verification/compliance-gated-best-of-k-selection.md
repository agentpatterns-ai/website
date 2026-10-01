---
title: "Gate Best-of-k Selection on Compliance Before Score"
term: "Compliance-Gated Selection"
description: "Reject rule-breaking attempts before ranking on score. Across 312 agent runs the ten violators held the seven highest scores, so the top pick was a violator."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - reject first then rank
  - compliance-gated best-of-k
  - compliance gate before selection
last_reviewed: 2026-09-30
maturity: emerging
---

# Gate Best-of-k Selection on Compliance Before Score

> Run every attempt through a pass/fail compliance check, then rank only the attempts that passed.

A compliance gate is a check that every attempt passes or fails before any score comparison runs. Failing attempts leave the candidate pool, so the selection takes the maximum over the survivors rather than over all k.

Ariño de la Rubia and Pafka ran 312 fixed-configuration agent runs on one tabular prediction task. Ten broke a data rule: five trained on the labeled evaluation file, five computed features from the batch they were scoring. "The seven highest scores in the study are all among these ten, and removing them takes the best score from 0.8293 to 0.7695" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.3). Their conclusion, in the same section: "Because they sit at the top of the ranking, the run one would pick on score alone is the run most likely to have broken a rule."

With the gate in place, three attempts beat one. The measured policy selects among compliant attempts on the evaluation set and reports the holdout score of the one it keeps. "Three attempts move the median delivered model 0.0081 AUC above one attempt, and ten attempts 0.0136" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.4). Its Table 6 puts the chance that three attempts return a compliant artifact at "at least 99.88%". The policy was specified after the runs were scored, so read it as retrospective.

## Where the gate applies

The paper's gate checks two rules: "no evaluation label reaches a model fit, other than as the early-stopping set the rules permit, and no feature or statistic is computed from the frame handed to the prediction function" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 3.5).

For ranking configurations against each other, excluding the violations "leaves the spread between pairing means and the best-of-k medians almost unchanged" (Section 4.3). Sizing that comparison is a separate job, covered in [Size Agent Comparisons by Run-to-Run Variance](size-agent-comparisons-by-run-variance.md).

## Declare what k counts

Two policies share the name: "Note also what k counts: attempts, not compliant attempts" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.4). The paper measured the fixed-attempt version, and says the alternative "costs more and never fails to deliver". Say which one you run. The fixed-k version can fail to deliver a compliant artifact.

Report the violation rate beside the quality figures. The paper's own recommendation is that "Agents and models should be evaluated as pairings, over repeated attempts, with compliance reported beside quality" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), abstract).

## Prefer prevention to detection

Two designs remove a violation rather than catch it: "putting evaluation labels behind a scoring interface makes unauthorised training impossible, and testing whether a row's prediction changes when the batch around it changes catches batch-dependent features without reading code" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.3). The first makes one class of violation unreachable; the second is a behavioral probe that reads no code.

## When this backfires

- A proxy heuristic stands in for the real check. The paper published a screen flagging any run whose best evaluation score beats its holdout score by more than 0.03, then did not use it. It compares a run's best experiment with the program it delivered, which need not be the same, and "on these runs it would have excluded two compliant runs and missed two that trained on evaluation labels" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 3.5).
- The gate's coverage gets read as the rule set. Two traces covered the two violation classes, and "Seven hits were cleared on reading" (Section 3.5).

## Key Takeaways

- Check every attempt against your rules, then compare scores. Reversing the order makes the top pick the run most likely to have broken a rule.
- On 312 runs, ten violators held the seven top scores, and excluding them moved the best score from 0.8293 to 0.7695.
- Say whether k counts attempts or compliant attempts. The two policies differ in cost and in whether they can return nothing.
- Report the violation rate next to the quality figures.
- A gate catches the classes you wrote checks for. The authors write that prevention is better than detection.

## Related

- [Size Agent Comparisons by Run-to-Run Variance](size-agent-comparisons-by-run-variance.md) — how many runs a ranking needs, from the same study.
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — designing the score so fewer violations pay off.
- [Protecting the Test Oracle From the Agent](../patterns/agent-design/protect-the-oracle-from-the-agent.md) — the permission-level version: deny the agent write access to what decides correctness.
- [Reliability of an Automatically Selected Agent Harness](../patterns/agent-design/harness-selection-reliability.md) — what a pick from a noisy search is worth in the unlucky case.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — what repeated attempts measure when the outcome is pass or fail.
