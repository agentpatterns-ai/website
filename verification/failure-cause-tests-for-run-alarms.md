---
title: "Failure-Cause Tests Before Acting on Coding-Agent Alarms"
term: "Failure-Cause Tests"
description: "A coding-agent failure alarm that mostly recognizes hard issues and weak models flags failures a retry is less likely to fix. Three tests on existing runs show which cause it tracks."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - hard issue, weak model, or bad run
  - failure-cause decomposition
  - no-specialization reference
last_reviewed: 2026-11-18
maturity: emerging
---

# Failure-Cause Tests Before Acting on Coding-Agent Alarms

> Test which failure cause an alarm tracks before it triggers a stop, retry, or model switch, because each cause needs a different action.

A coding-agent run fails for one of three reasons, and each needs its own response. "The *issue may be hard*, so that most models fail it; the *model may be weak*, so that it fails many issues; or this particular attempt may have gone wrong, a *bad run*". A hard issue calls for a stop or a human, a weak model for a stronger one, and "only a bad run for retrying" ([Shi and Assunção, arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). On SWE-bench Verified, trajectory-based alarms mostly recognized the first two causes and added nothing measurable about the run. Three tests on logs you may already hold show whether your alarm does the same.

## Conditions for running the tests

The tests need data that single-run production logs do not hold. Check these first.

- Each issue has runs from several models, or several runs from one model. A within-issue comparison has no pairs otherwise.
- You can build a difficulty reference from outcomes on the same issues. The paper used the fail rate of 16 other models, which "serves as a diagnostic rather than a practical predictor" because those outcomes do not exist at deployment ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)).
- You know how far apart the models in the pool are. Model ability explained 2.5% of outcome variance across seven models and about 10% across 23 ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). The paper attributes the larger share to greater differences between models.

The first check, pooled versus within-task AUROC, has its own page: [Random Restart as the Baseline for Agent Early Stopping](../patterns/anti-patterns/random-restart-as-the-stopping-baseline.md).

## Test 1: split within-issue pairs by model ability

Within-issue AUROC removes issue difficulty, but it still rewards a score that guesses which model ran. Label each within-issue pair consistent or an upset. A pair is consistent "if the failed run comes from the overall weaker model and an *upset* otherwise" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Beside your alarm, score a model-identity reference: each model's failure rate on training issues.

A score that tracks the run beats 0.5 on both kinds of pair. A score that tracks model ability beats it on consistent pairs and falls below it on upsets. The paper's TF-IDF predictors never saw the model name, yet "They score 0.68–0.69 on consistent pairs but 0.42 on upsets, and all ten distinct TF-IDF configurations fall below 0.5 on upsets" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Model identity alone reached 0.72 within-issue AUROC against the predictors' 0.60 to 0.61.

Then test what the alarm adds beyond both references. The paper required the 90% interval of the AUROC gain to sit inside ±0.02, and the gain was "equivalent to zero in all 18 configurations" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)).

## Test 2: check the oracle gap against a no-specialization reference

The oracle gap is the share of issues some model solves minus the share the best single model solves. "Model switching is often motivated by" this gap ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). On seven models, "The best single model solves 76.8% of the issues, whereas some model solves 86.8%, an oracle gap of 10.0 pp" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)).

Simulate the gap you would see with no specialization at all. Fit one ability per model and one difficulty per issue with a Rasch or two-parameter logistic model, then sample outcomes "in which every issue ranks the models identically, so that upsets and the gap arise only by chance" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). In the paper's eight comparisons, no observed gap or upset rate sat significantly above its simulated range after Holm correction.

Score any router on held-out runs, never on the runs that chose it. In a repeated-run pilot on two Llama models across 522 issues, choosing each issue's model from its past runs gained 0.09 points on new runs, with a 95% interval of -0.36 to 0.63. Also count the failures nobody can rescue: 448 of 994 failures sat on 64 issues that none of the seven models solved ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)).

## Test 3: compare actions at equal attempts

Judge an alarm by whether its action fixes the failure, against a baseline that spends the same number of attempts. Escalating every failure to one fixed second model gained 6.91 points. "Because this policy makes no issue-specific choice, its gain comes from the second attempt, not from picking a better-suited model" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Choosing the model per issue added only 0.41 points, and the 6.91 assumes a perfect failure detector.

Run the retry arm the same way. Bad runs are common: run-to-run variation explained 42% of outcome variation in the pilot, against 4.6% for model-issue specialization and 53% for issue difficulty. So a retry has failures to fix. An alarm whose score varies mostly between issues sends it to the wrong ones. For the paper's predictors, 64% to 82% of score variance lay between issues, and Fail-Fast's predictor-triggered cold restart "adds only 0.2 pp" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)).

## Map the cause to the action

| Cause | Signature in the tests | Action that pays |
|---|---|---|
| Hard issue | High difficulty reference; most models fail | Stop, or hand to a human |
| Weak model | Model-identity reference ranks it; consistent pairs | Escalate to a fixed stronger model |
| Bad run | Same model solves the issue in other runs | Retry the same model |

## Why it works

AUROC counts the failed-successful pairs a score ranks correctly, and the pair mix decides what the count rewards. Of 494,109 such pairs in the paper's test folds, 99.66% compared different issues, so a score that knows only which issues are hard ranks most pairs right ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Every pair left inside an issue sets two models against each other. Model identity scores 1 on consistent pairs and 0 on upsets, so its 0.72 within-issue AUROC means most such pairs were consistent. A score that infers the model from the transcript inherits that ranking. The decomposition follows item response theory, "which explains each outcome by the difficulty of the item and the ability of the respondent". The oracle gap moves by the same logic. A second attempt from any model raises the chance of at least one success whether models specialize or not. In the paper's toy example, two models at 0.7 and 0.6 jointly solve 0.88 of issues, while running the stronger one twice reaches 0.91.

## When this backfires

- Your logs hold one attempt per issue. Single-run benchmark data cannot separate a bad run from a hard issue or a weak model, and the paper says so of public leaderboards ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Collect a repeated-run sample first.
- The cheap model is much weaker than the target. Atropos migrates predicted failures from small open-weight models to a more capable target model and reports "Hotswapping LLMs for such inferences can convert up to 27.57% of them to be successful" ([Kim and Yoo, arXiv:2604.15075v1](https://arxiv.org/abs/2604.15075v1)). The abstract states no equal-attempt control.
- You built a feature for run-level drift. A Toolathlon analysis estimates an 8.8-percentage-point success gain from restarting the bottom tercile by adherence at 75% of trajectory completion. This counterfactual assumes restarted runs reach the adherence of successful runs of the same model on the same task. The restart benefit still needs experimental validation ([Lee, sections 7.2 and 7.3](https://arxiv.org/html/2602.19008v1#S7.SS2)). The null result covers TF-IDF and small fine-tuned predictors on one benchmark and scaffold, not every trajectory feature.
- Your sample is small. The authors "have not yet measured how much specialization the no-specialization reference can detect, so non-rejection does not prove that specialization is absent" ([arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1)). Recurring upsets did show up in the pilot, on about 15 of 522 issues.
- Model failures are correlated. Under stochastic decoding, the oracle premium that per-model success rates identify spans an interval whose lower bound is zero ([arXiv:2607.03436v3](https://arxiv.org/abs/2607.03436v3)). Read any oracle gap, observed or simulated, as conditional on how failures couple.

## Example

**Before** — a failure alarm reported on its pooled score:

```text
alarm                     pooled AUROC
TF-IDF, full prefix       0.630
verdict                   wire it to an auto-retry
```

**After** — the same alarm beside run-blind references, at step 20 on 2,840 runs:

```text
score                     pooled   within   consistent   upset
issue difficulty          0.924    0.500    0.500        0.500
model identity            0.567    0.724    1.000        0.000
length + model identity   0.607    0.648    0.756        0.373
TF-IDF, full prefix       0.630    0.610    0.687        0.416
verdict                   tracks issue and model; retry arm untested
```

Figures are Table I of [arXiv:2611.08285v1](https://arxiv.org/abs/2611.08285v1). The alarm sits under 0.5 on upsets, the signature of a score following model ability. Its pooled score is not significantly above length plus model identity.

## Key Takeaways

- An alarm below 0.5 on upset pairs is ranking models, not runs. The paper's predictors scored 0.42 there.
- A 10-point oracle gap fell inside the range a no-specialization simulation produced. Test it before you fund a per-issue router.
- Price escalation against a same-budget second attempt. Escalation to one fixed model gained 6.91 points, while a per-issue model choice on one attempt gained 0.41.
- A retry pays only on bad runs. Run-to-run variation was 42% of outcome variation, so the failures exist, but an alarm driven by issue-level score variance points away from them.

## Related

- [Random Restart as the Baseline for Agent Early Stopping](../patterns/anti-patterns/random-restart-as-the-stopping-baseline.md) — the pooled-versus-within-task AUROC split this page builds on, with continuation as the stop baseline.
- [Static Difficulty Estimation for Agent Issue Triage](static-difficulty-estimation-issue-triage.md) — a difficulty score available before the run, the deployable form of the issue-difficulty reference.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — where run-to-run variation comes from, the cause a retry can fix.
- [Judge a Technique Against a Budget-Matched Best-of-n Baseline](budget-matched-best-of-n-baseline.md) — the equal-attempt comparison applied to techniques in general.
- [Router-Imposed Quality Ceiling: Committing Before Output](../patterns/agent-design/router-imposed-quality-ceiling.md) — the router-to-oracle gap from the routing side.
