---
title: "Deciding an Agent Upgrade on a Frozen Judge's Verdict"
term: "Frozen-Judge Release Decision"
description: "A frozen judge's verdicts depend on which agent version wrote the trajectory, even after conditioning on the task and the outcome. On 20 prespecified SWE-bench version pairs, eight judge-only intervals declared an improvement the execution-based interval left inconclusive."
aliases:
  - frozen judge release decision
  - version-dependent judge error
  - transported judge calibration
tags:
  - anti-pattern
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-03
maturity: emerging
---

# Deciding an Agent Upgrade on a Frozen Judge's Verdict

> Three judges tracked the execution-based agent ordering at Kendall 0.71-0.79, and still drew eight judge-only upgrades that execution left inconclusive.

Holding the judge model fixed does not make a judged version comparison valid. Li tested whether a judge's verdict distribution holds across two versions once you condition on the task and on the actual outcome. The test used 20 prespecified version pairs of one coding-agent scaffold across 250 SWE-bench Verified issues. Every available judge rejected that invariance (p = 0.0001 per judge, within-dataset Holm p = 0.0003). The error does not land equally on the old and new arms, so it cannot be assumed to cancel in the difference ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

## When this applies

Two conditions decide whether the error changes a decision. A third decides whether you can do anything about it.

- You are making a ship-or-not call on one pair, not ranking many candidates. Rank agreement across the 35 agents stayed positive for every judge. Li keeps the judge for deciding "which comparisons deserve an audit, not to ship" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).
- The two versions are close. Half the reference version differences in this study were under five points. On close pairs the version-dependent term dominates the comparison error, because the attenuation it competes with is small.
- A reference standard exists: execution tests, database state, or expert labels. Without one the error still reaches the decision, you just cannot size it, and the audit below is unavailable.

## Where the judged decision diverged

After within-judge multiplicity adjustment the version-dependent component of the comparison error was detectably nonzero in 32 of 60 judge-by-pair units (53.3%; sign test p < 0.05 after within-judge Benjamini-Hochberg adjustment). Discrete release decisions disagreed with execution in only 11 of 60. Eight judge-only intervals declared an improvement where the execution interval was inconclusive; three missed an improvement execution did detect.

One combined scaffold and configuration change moved the test-based solve rate by -0.4 points (95% interval -5.2 to +4.4). Two of the judges scored it +8.0 (+2.0 to +14.4) and +9.6 (+3.2 to +16.0) ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

That is excess confidence rather than demonstrated harm. No pair was confidently reversed from better to worse, and six of the eight over-claimed upgrades had positive reference point estimates. Li's own summary: "The practical risk is acting with greater confidence than the reference supports, not a large number of confident reversals" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

## Why it works

The comparison error splits into attenuation, which shrinks a judged difference toward zero, and a version-dependent component that can push it either way. Attenuation scales with the true difference, so on close pairs the version-dependent component is most of what you measure ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

The source does not name one cause for the component. It is detectably nonzero in 32 of 60 SWE-bench units, where the reference is execution tests. Li offers a construct-mismatch reading for one domain only, labeled exploratory and written after the tau-bench results.

In that tau-bench case the judge prompt asked whether the agent "followed the policy", while the environment reward checked only the final database state. The policy forbids a turn that both calls a tool and replies to the user, and the reward ignores the rule. Successful retail conversations carried 7.4 such turns on average for the stronger agent against 0.5 for the weaker one. Li's wording: "so a strict judge measures a stricter construct than the reference, and a difference in the agents' habits becomes a difference in judge error" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

A judge weaker than what it judges can misrank with no construct mismatch at all. Dorner and colleagues construct a binary proxy and a set of strictly better classifiers. Better means point-wise: wherever the proxy is right, so is every classifier in the set. Scoring with that proxy "fully reverses the correct model ranking". It perturbs the ranking strongly in their empirical case ([arXiv:2410.13341v4](https://arxiv.org/abs/2410.13341v4)).

A replay check does not catch this. A frozen anchor set detects the judge changing, but because the anchors are fixed the statistic cannot respond to error the new version's outputs induce. "Anchors certify the stability of the judge, not its validity on the outputs being compared" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

## When this backfires

- The judges distort in opposite directions and you aggregate them. On tau-bench their distortions partly canceled. All three aggregation rules reached the reference decision in both domains. Counting ties as rejections left no detectable version-dependent error (cluster-robust p = 0.16). Cancellation is not guaranteed, though. On SWE-bench the signed comparison error averaged +2.8 points over all 60 units (95% interval +1.6 to +4.2), and the differential component averaged +6.8 points (+5.8 to +7.7) ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).
- The disagreement count is not the finding. A simulated judge with no version-dependent error produced decision disagreement near 32.7% through task mix alone, above the 18.3% observed. The count cannot separate a version-dependent judge from a clean one. The continuous component can ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).
- The audit saves few labels. At 80 randomly selected task pairs, an interval using execution labels alone was 14.9 points wide and the judge-assisted interval 14.2, about 5%. An untuned version of the same estimator was wider at 19.8 ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).
- The numbers do not travel past the design. The 20 version pairs come from one scaffold family on one 250-issue set and are observational.
- An upstream outage cut the preregistered four-judge primary analysis to three. The fourth judge is reported descriptively.
- The capability gradient is "an association among public configurations of one scaffold, not evidence that raising an agent's capability causes the judge to change its behavior" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

## Example

A team wants to know whether agent v7 beats agent v6. Take Li's own planning case. The pool has 300 tasks, the two versions' outcomes differ on 25% of them, and the true success-rate difference is 5 points ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

### The repair that makes it worse

Estimate the judge's sensitivity and false-positive rate on v6's labeled outputs, apply those rates to v7's judged score, and ship. That correction was worse than no correction in 59 of 60 ordered judge-pair units, raising mean absolute comparison error from 3.8 to 19.5 points. The correction divides the version-dependent error and the sampling noise by the old version's discriminability. Its median here was 0.19 to 0.38. 24.6% of bootstrap draws had to be dropped because a resampled index went nonpositive. Li writes that transport "is exact only when the error rates are the same for both versions, which can be checked only with labels on the new version" ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

### The audit that works instead

Draw tasks at random from the pool. Get the execution outcome for both versions on each drawn task. Estimate the paired difference using the judge's verdicts on the full set as a proxy. Because the audit sample is random, the estimate stays unbiased for any fixed weight on the judge, however the judge's errors depend on the version. Tuning that weight on a small audit drops coverage below nominal, so Li treats 40 tasks as a planning floor rather than a guarantee. For that 300-task pool, Li's planning approximation puts the requirement at about 217 labeled task pairs without a judge, at 5% significance and 80% power. With a judge whose paired correlation matches the AgentRewardBench median of 0.46, it is 202. Treat a judged lead as the trigger for that audit on this pair ([arXiv:2609.34198v2](https://arxiv.org/abs/2609.34198v2)).

## Key Takeaways

- A frozen judge is not a fixed instrument on a moving agent. Every available judge rejected the invariance that its verdicts turn on the task and the outcome but not on which version wrote the trajectory.
- Positive rank agreement with execution does not license a ship decision. Kendall 0.71 to 0.79 across 35 agents coexisted with a detectably nonzero version-dependent component in 32 of 60 judge-by-pair units.
- Never transport the previous version's calibration. It was worse than the raw judge in 59 of 60 units, and its exactness can be checked only with labels on the new version.
- Budget the audit as a validity cost. The saving is real and small. The judge narrowed an 80-pair interval by roughly 5%, and cut a 300-task pool's label requirement from about 217 pairs to 202.

## Related

- [Measure the Judge Before You Freeze a Gate on It](../../verification/judge-instrument-stability-check.md) — the replay check that holds the agent still and watches the judge; what it cannot see is the failure here
- [Choosing the Judge Model That Grades Your Agent Evals](../../verification/judge-model-bake-off.md) — judge selection on frozen traces, and the condition under which a bias really does cancel in a version delta
- [Equivalence Testing for Agent Configuration Changes](../../verification/equivalence-testing-agent-config-changes.md) — what a comparison can defensibly claim when you expect no effect
- [Rank Resolution: Reading a Converged Coding-Agent Leaderboard](../../verification/rank-resolution-converged-leaderboards.md) — why close orderings stay unresolved whatever grades them
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](../../verification/meta-evaluate-llm-judge-rubric-verification.md) — measuring judge error against human labels before the judge scales
