---
title: "Cumulative-Best Reporting Hides Repair-Loop Security Regressions"
term: "Cumulative-Best Reporting"
description: "A cumulative-best metric is non-decreasing by construction, so it cannot show a repair loop re-breaking security checks that were already passing — track the per-iteration trajectory instead."
tags:
  - anti-pattern
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - cumulative-best metric blindness
  - per-iteration security trajectory
  - repair-loop security regression
last_reviewed: 2026-08-15
maturity: emerging
---

# Cumulative-Best Reporting Hides Repair-Loop Security Regressions

> A metric defined as the best result across iterations can never fall, so a repair loop that re-breaks passing security checks looks monotone.

Report a generate-validate-repair loop with a cumulative-best metric and you have chosen a number that cannot decrease. Feeding validator errors back for another repair pass sometimes re-breaks a security check that was passing one iteration earlier, and the aggregate absorbs it silently. A study of 5,968 infrastructure-as-code repair timelines found the per-iteration security trajectory had never been examined for this workload, because prior work reported the cumulative-best form ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).

## When this applies

The blind spot exists wherever the aggregate is a maximum, but the fix earns its cost only under three conditions.

- Your loop ships its last iteration rather than the best verified one, so an intermediate regression can reach production. A system that exports a retained checkpoint instead reports that "after the early rounds, the current candidate can lag behind the retained checkpoint" ([Wu et al., 2026](https://arxiv.org/abs/2605.26807v1)).
- Your validator emits a stable per-check pass/fail set of named rules, in the shape Checkov, tfsec, or a policy engine produces. A compiler exit code has no such set to diff.
- The artifact holds several resources the model can restructure while repairing one of them, which is the edit shape the regressions come from.

## The pattern

A team runs an LLM repair loop against a validator, feeds each round of errors back, and reports the outcome as the best pass rate any iteration reached. The loop appears to climb, so the iteration budget gets raised on the assumption that another round can only help.

The per-transition view says otherwise. Across 4,440 iteration transitions carrying Checkov results on both sides, 24.8% of transitions and 13.8% of scenarios showed at least one previously-passing CIS Benchmark check failing afterwards under standard detection ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).

Pin that figure to its detection mode, because the study reports two and they differ by roughly four times. Standard detection counts any check that moves from the passed set into the failed set. Strict detection requires the check to be exclusively passing beforehand and exclusively failing afterwards, removing ambiguous multi-resource cases. Under strict detection the rate falls to 5.2% of transitions and 3.3% of scenarios. The authors call 3.3% "the conservative, defensible rate" and read the gap as evidence that "most apparent regressions are multi-resource measurement artifacts" ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).

## Why it works

The regression follows from a mismatch of scope. Validator feedback names the check that failed, while the model's edit covers the whole resource block it decides to rewrite, so passing properties that went unmentioned become collateral. Resource restructuring accounts for 79.0% of standard-mode regressions and 68.4% of strict-mode ones, ahead of configuration drift at 15.5%. The study describes the shape directly: the model "adds, removes, or renames resource blocks while fixing validation errors, and the restructured code loses security configurations from the prior iteration" ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).

The second half of the mechanism is arithmetic. A cumulative-best aggregate takes a maximum over iterations, and a maximum is non-decreasing whatever the underlying series does, so no property of the reported number separates a loop that improved steadily from one that broke and re-fixed the same check three times. The evidence survives only in the per-transition trajectory, which is why the effect went unmeasured rather than unnoticed.

## What to measure instead

- Diff the per-check result sets between consecutive iterations and report how many checks moved from passing to failing, with the detection mode named.
- Watch check volatility as a cheap online signal. Defined as `|C_new| + |C_removed| + |C_flipped|` across a transition, it averages 11.55 on regression transitions against 2.38 otherwise in strict mode, a 4.9x separation with Cohen's d = 1.49 ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).
- Name regressions in the feedback prompt instead of replaying the whole error list flatly: "Explicitly flagging regressions ('Warning: CKV_AWS_145 was passing but now fails') could prevent the LLM from unknowingly degrading security" ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).
- Instruct minimal edits, since restructuring dominates the root causes. The authors argue models "should be constrained to make minimal modifications during repair rather than regenerating entire resource blocks" ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).
- Retain the best verified artifact instead of the final edit. At revision 3 of a forced-revision study, "16.0% of trajectories have produced a correct patch and subsequently lost it" ([Gao et al., 2026, §5.1](https://arxiv.org/abs/2607.24604v1)).

## When this backfires

- The loop already exports the best verified checkpoint. Cumulative-best then describes the artifact you ship, so per-iteration alarms fire on states that never leave the loop.
- Stopping early to dodge regressions costs pass rate and forfeits self-repair. In the same study 36.6% of standard-mode regressions self-corrected within an average of 1.2 iterations, and the pass-rate maximum sits at iteration 4 (83.4%) rather than iteration 3 (83.1%) ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)). Iteration 3 is a trade-off point, not a safety threshold.
- Single-resource artifacts, where the four-fold gap between the two detection modes means a standard-mode alert is mostly noise.
- Treating the root-cause split as settled. The classification came from automated diff analysis that "was not validated against human labels", and single runs per configuration mean "point estimates may vary ±2–5pp" ([Agyekum and Santos, 2026](https://arxiv.org/abs/2608.13404v1)).

## Example

Before, reporting the cumulative best:

```text
Terraform repair loop — weekly report
- Checks passing (best across 5 iterations): 83.4%
- Conclusion: converging; raise the iteration cap to 8
```

The headline is a maximum over the run, so it rose whatever happened in between.

After, reporting the trajectory alongside it:

```text
Terraform repair loop — weekly report
- Checks passing at final iteration: 82.6%
- Checks passing (best across 5 iterations): 83.4%
- Regressed checks (strict mode): 5.2% of transitions
- Check volatility on regressed transitions: 11.6 vs 2.4 baseline
- Conclusion: final artifact sits below the best one seen; export the
  retained checkpoint and cap the loop nearer iteration 3-4
```

Same run. The gap between the final and the best result is the whole finding, and the first report cannot show it.

## Key Takeaways

- Read any repair-loop report that quotes a best-across-iterations or ever-passed figure as unanswered on safety, and ask for the final-iteration number beside it
- Under standard detection 13.8% of IaC repair scenarios showed at least one security regression, while the defensible strict-mode rate is 3.3%; name the detection mode whenever you cite either
- The cause is scope mismatch: feedback names one failing check while the model rewrites the whole resource block, and restructuring drives 79.0% of standard-mode regressions
- Retaining the best verified artifact removes most of the operational risk without any new metric, so instrument the trajectory when your loop ships its final iteration

## Related

- [Density-Normalized Quality Metrics Mask AI-Driven Code Growth](density-normalized-quality-metric.md) — the adjacent measurement artifact, where the denominator rather than the aggregation function produces the misleading trend
- [State-Bound Evidence and Typed Revision Contracts for Repair Loops](../../verification/state-bound-repair-evidence.md) — the functional-correctness analogue, where a loop finds a correct patch and then destroys it
- [Bounded Repair-Loop Iterations](../../verification/bounded-repair-loop-iterations.md) — the round-budget argument on functional grounds, which this page's stopping guidance sits alongside
- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](../../verification/layered-oracle-iac-security-repair.md) — the within-repair IaC security failure, where a single fix satisfies the scanner without changing the policy
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](../../verification/validity-estimate-stopping-noisy-repair-loops.md) — stopping when the verifier itself is unreliable, a different corruption of the same stop signal
