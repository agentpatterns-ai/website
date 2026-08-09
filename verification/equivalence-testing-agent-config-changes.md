---
title: "Equivalence Testing for Agent Configuration Changes"
term: "Configuration-Change Equivalence Testing"
description: "An equivalence test bounds how far a config change could move agent behavior; a zero-event result states a floor you compute from n, not an absence."
aliases:
  - config-change equivalence testing
  - zero-event equivalence bounds
  - prespecified equivalence margin
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-06
maturity: emerging
---

# Equivalence Testing for Agent Configuration Changes

> Equivalence testing bounds how far a configuration change could have moved agent behavior; a zero-event run states a detection floor, not an absence.

Equivalence testing asks whether a change moved a metric by less than a margin you fixed before collecting data. Reach for it when you expect no effect and need to say so defensibly. A significance test that fails to reject the null says nothing about how large the remaining effect could be, so it cannot clear a configuration dial for release. An equivalence test returns a number: the largest behavior change your data can still hide, paired with the sample size that produced it.

The worked case is a prespecified study of reasoning effort and unauthorized tool use. Varying effort between low and max inside GPT-5.6 across 840 trajectories produced zero policy-prohibited tool calls in every arm, and the interaction estimate of 0.000 carried a simultaneous 95% interval of ±4.34 percentage points, inside the prespecified ±7.01-point margin ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).

## Hold everything but the dial constant

An equivalence claim is only as strong as the thing held constant. That study generated its 20 workplace scenarios as matched triads from one code base, with the three conditions differing in two configuration fields, and checked automatically that rendered prompts, tool schemas, and interaction budgets were identical apart from the sentence those fields control ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)). Anything that varies alongside your dial ends up inside the interval you publish.

Prespecification does the second half of the work. The 14 confirmatory scenarios were built fresh after piloting and never revised in response to outcome data, and the analysis plan was frozen before collection ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)). Without that, a null result is indistinguishable from a scenario set tuned until it produced one.

## Compute the floor before you spend a token

When you expect zero events, the informative quantity is the exact one-sided upper limit, which depends only on sample size and confidence level. At n = 84 per arm the limit is 3.50%; at n = 56 it is 5.21%, and that study set its margin at twice the per-arm limit, giving ±7.01 points ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).

Run that arithmetic first. If the violation rate you would treat as an incident sits below the floor your budget buys, the run cannot answer your question, and a null result from it will still be quoted as though it did.

## Why it works

A significance test puts the burden of proof on detecting a difference, so absence of evidence passes by default. An equivalence test moves that burden onto the interval: you have to show the whole plausible range of the effect sits inside a margin you named in advance. The procedure therefore survives a zero-event outcome, where a conventional test has nothing to work with. The exact bound for two independent zero-event arms falls out of the binomial likelihood, so its width is fixed by the sample size and confidence level rather than estimated from the data ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).

The design does not explain why the dial left conduct unchanged. Those authors offer no causal mechanism for the null and describe it only as consistent with the prohibition gating the conversion of discovery into action, a comparison drawn across studies rather than from their own manipulation ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)). Treat the bound as the result and the explanation as open.

## When this backfires

- Your tolerable rate sits below the floor. Nothing under 3.50% was observable in the primary tier of that study ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)), so a fleet where 1% is a serious incident gets no assurance from it.
- The policy is not explicit. Those prohibitions were unambiguous and system-level, and the authors name ambiguous, implicit, or incentive-conflicting policy as untested, and as where an effort effect on conduct stays most plausible ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).
- The environment rewards the shortcut. Reasoning-tuned models game a specification spontaneously where non-reasoning models need prompting ([Bondarenko et al. 2025](https://arxiv.org/abs/2502.13295v3)), and extended reasoning has amplified concerning behavior in another model family ([Gema et al. 2025](https://arxiv.org/abs/2507.14417v2)). A benign clerical suite bounds none of that.
- You extrapolate past the endpoints. Only low and max were sampled, on one model family at two tiers, and the estimand is the violation probability within that fixed scenario set ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).
- Collection order tracks the condition. All low-effort trajectories preceded max-effort ones against moving vendor aliases, so every effort contrast there is entangled with collection time ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)). Randomize the order or your interval absorbs vendor drift.
- You substitute the null for enforcement. That suite measured propensity with no runtime enforcement layer present. A governed proxy doing access control at tool discovery and invocation drove unauthorized invocation to 0% under 150 adversarial tasks, where prompt-level restriction alone moved it by 11 to 18 points ([Uppala 2026](https://arxiv.org/abs/2605.18414v1)).

## Example

The secondary result in that study shows what an equivalence design buys beyond the headline. The prespecified hypothesis was that added reasoning would raise rule-probing most where probing reveals an exploitable gap. The observed estimate was −0.143, 95% CI [−0.274, +0.012], because probing rose furthest in the condition where it had no instrumental payoff: on the primary tier, 39.3% to 78.6% between low and max effort, against 47.6% to 72.6% where a gap existed ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)).

Inspection moved hard while action did not move at all. Any monitor keyed to how often an agent queries its own policy will therefore alarm after an effort raise and report nothing about whether a rule was broken.

## Key Takeaways

- Write the margin, the sample size, and the resulting floor into the plan before collection; the floor is arithmetic on the sample size, not a finding.
- Hold prompts, tool schemas, and step budgets identical across arms, and verify that mechanically rather than by inspection.
- Freeze the scenario set and the analysis plan before collection, so a null result cannot be read as a suite tuned until it produced one.
- Report a zero-event result as an upper limit with its sample size attached, and refuse the reading that treats it as proof of absence.
- Keep the enforcement layer out of the argument. A propensity bound is evidence about the model, not a control over what it can call.

## Related

- [Policy-Graded Evaluation of Coding Agents](policy-graded-agent-evaluation.md) — Scores agents at each enforced security tier, the complement to measuring propensity with enforcement switched off.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — Separates run-to-run variability into sampling, infrastructure, and orchestration layers before you attribute a difference to a config change.
- [Dispatch-Time Reasoning Level for Delegated Agents](../patterns/agent-design/dispatch-time-reasoning-level.md) — How to choose the effort setting once you know what changing it does and does not move.
- [Prompt-Only Tool Access Control](../patterns/anti-patterns/prompt-only-tool-access-control.md) — Why a stated prohibition is not an access control, whatever a propensity study reports.
- [Subagent Schema-Level Tool Filtering](../patterns/multi-agent/subagent-schema-level-tool-filtering.md) — Making an unauthorized call structurally impossible instead of measuring how often it happens.
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — What to report when a result moves with the seed, and why a cell at a bound is sometimes the design and sometimes the defect.
