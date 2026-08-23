---
title: "Mutation Testing for LLM Judges: Scoring an Evaluator on Injected Defects"
term: "Judge Mutation Testing"
description: "When a task has no unique ground truth, inject defects you named into known-good inputs and score your LLM judge on how many it reports — a screening proxy for judge rankings, not a replacement for measuring precision."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - judge mutation testing
  - kill ratio for LLM judges
  - mutation testing for semantic evaluators
last_reviewed: 2026-08-17
maturity: emerging
---

# Mutation Testing for LLM Judges: Scoring an Evaluator on Injected Defects

> Inject defects you named into inputs your judge should catch, then score kill ratio when the task has no ground truth to score against.

You cannot score a judge on correctness when the task has no correct answer. Mutation testing sidesteps that by manufacturing the label: take a pair a human already accepted, apply an operator that breaks it in a way you can name, and ask whether the judge reports that specific defect. Kill ratio is the share of injected defects the judge caught, and it ranks judge configurations without any new human labeling.

## When this applies

Four conditions have to hold before the number means anything.

- The task genuinely lacks a checkable ground truth. If compilation, tests, or a schema can settle it, score against the real answer instead.
- You have inputs already judged acceptable. The method assumes the transformation degrades a good artifact, which the authors list as a threat to validity ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- You are screening candidates, not picking a winner. Kill ratio reproduced the manual ordering of judge configurations on 11 of 15 pairs, an agreement rate of 73.3%; against manual precision it correlates at Pearson r = 0.624 ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- A precision measure runs alongside it. Kill ratio is recall on defects you invented, so nothing in it sees a false positive.

## How the harness works

Three pieces, each built once per task.

- An operator set. The study defines 11 operators for comparing a domain class diagram against a textual description: five applied automatically (remove a class, remove an attribute, remove a relationship, add an irrelevant association, reverse a non-symmetrical relationship) and six applied with LLM assistance, which add implementation-oriented elements, implicit domain elements, or elements from unrelated domains ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- A mutant corpus. Those operators over two datasets of 5 and 45 model-description pairs, less three non-applicable operator-model combinations, left 547 mutants and 3,282 mutant judgments across six judge configurations ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- A kill detector. Judges report issues in prose, so something has to decide whether a reported issue is the injected one. The study matched them by semantic similarity above a threshold of 0.55 and reports the detector at F1 = 0.90, precision 0.86, recall 0.95 ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).

## Why it works

The operator converts an unlabelable judgment task into a labeled detection task. No one can say whether a judge's critique of a diagram is right, because the task admits many valid answers. Remove a named class from an accepted diagram and one statement about it becomes true by construction, so "did the judge report the missing class?" has a decidable answer that cost nothing to produce. What survives the conversion is the ranking: kill ratio and expensive manual annotation put the same configurations on top, which is why the authors call the two "complementary instruments" rather than substitutes ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)). The same perturb-then-score design appears independently in [AXIOM, which builds a code-judge benchmark by applying predefined perturbation rules to high-quality programs](https://arxiv.org/abs/2512.20159v1).

## When this backfires

- Easy operators saturate the metric. Adding elements from unrelated domains was killed 95.8% and 97.8% of the time, against 62.3% for removing an attribute ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)). Report per operator, because an aggregate hides which ones still discriminate.
- Kill ratio cannot see over-flagging. A judge that reports everything kills every mutant. Kill ratio separated the two GPT configurations by half a point (87.1% against 86.6%) where manual precision separated them by 28 points (63.7% against 35.5%) ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- Near-ties flip. Roughly one configuration pair in four was ordered differently by kill ratio than by manual assessment ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- The reference standard is adjudicated, not clean. Annotators on the manual baseline reached Krippendorff's α = 0.32 "before adjudication", after which an additional annotator settled every disagreement to produce the labels the precision analysis actually uses. The authors keep the residual caveat: adjudication "resolves disagreements for analysis purposes, but does not eliminate the underlying ambiguity of the task" ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- One defect per mutant is not one defect per artifact. The authors call the single-defect design "limited regarding the complexity of real-world models, which often contain multiple interacting inconsistencies" ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)).
- A single run is not a measurement. Haldar and Hockenmaier report [low intra-rater reliability in LLM judges, whose variance "makes their ratings inconsistent, almost arbitrary in the worst case"](https://arxiv.org/abs/2510.27106v1), and a kill ratio is produced by judge runs.
- The proxy is context-dependent. A replicability study of mutation score on LLM-generated test suites found that [where the code under test may already be buggy, coverage and mutation scores "no longer serve as reliable indicators"](https://arxiv.org/abs/2607.22880v1). Injecting into accepted inputs is the assumed-clean case, so the result says less about judging artifacts that were already wrong.

## Example

The study screened six judge configurations: three models crossed with two prompts. The prompt comparison is where the proxy earned its keep. Detailed-guidance prompt P2 scored 87.0% kill ratio against 77.7% for the basic prompt P1, and manual precision moved the same direction, 48.6% against 26.9% ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)). Two independent metrics ranking the prompts the same way is a decision you can act on without annotating anything.

The model comparison is where it did not. Kill ratio ordered the models GPT-5.3-codex 87.1%, GPT-5-mini 86.6%, Gemma4:e4b 73.4%. Manual precision ordered them 63.7%, 35.5%, 31.6% ([arxiv.org/abs/2608.14315v1](https://arxiv.org/abs/2608.14315v1)). Both agree Gemma is worst, so the harness correctly drops one candidate. Neither kill ratio tells you that only 35.5% of what GPT-5-mini reports holds up. That is the split to expect: use the harness to cut the field, then spend annotation budget on the survivors.

## Key Takeaways

- Injecting a defect you named turns an unscoreable judgment task into a scoreable detection task, at zero labeling cost
- Kill ratio is a recall measure and is blind to over-flagging, so pair it with a precision measure before acting on a result
- Report kill ratio per operator, because easy operators saturate near 100% and stop separating candidates
- Treat the output as a screen that narrows a field of judge configurations, not as the verdict on the survivors
- Budget for a kill detector and a calibration of its matching threshold; deciding whether a reported issue is the injected one is its own measurement problem

## Related

- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the same operator machinery aimed one level down, at whether a test suite notices a regression
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — the human-labeled alternative this method substitutes for when labels are the cost you cannot pay
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — inject a known defect to test the instrumentation rather than the evaluator
- [Comparative Judging for Agent Configuration Ranking](comparative-judging-config-ranking.md) — another way to rank configurations when absolute scores are too noisy to average
- [Measuring Synthetic Eval Data Quality (SynAE)](synae-synthetic-eval-quality.md) — scoring the synthetic data itself rather than the judge that reads it
