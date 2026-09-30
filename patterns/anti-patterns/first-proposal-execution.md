---
title: "First-Proposal Execution in Agent Loops"
term: "First-Proposal Execution"
description: "An agent loop that runs whatever action it proposed first spends its budget on optional work. Offering the loop three candidates and picking one closed most of the gap in a synthetic benchmark; the governance layer on top bought tokens, not success."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - first-candidate execution
  - executing the first proposed action
last_reviewed: 2026-09-29
maturity: emerging
---

# First-Proposal Execution in Agent Loops

> An agent loop that executes whatever it proposed first spends its budget on optional work; choosing among three candidates recovered nearly all the lost success.

Give the loop more than one candidate action per cycle and make it choose. In a synthetic 24,000-episode benchmark under a shared 40,000-token ceiling, a loop that executed its first proposal reached the hard goal 67.42% of the time; the same loop choosing among three pre-generated candidates reached 96.53% ([Xiao et al., 2026, §9.1](https://arxiv.org/abs/2609.30662v1)). No live model was run: the authors call their benchmark "a mechanism-isolation testbed, not a prevalence estimator for real models", and note that "live-model validation remains necessary".

## What the benchmark isolates

Every policy ran the same stream: "the simulator pre-generates candidate sets and execution random draws from a common seed" ([§8.3](https://arxiv.org/abs/2609.30662v1)). The candidate opportunities and stochastic outcomes stayed fixed across policies, so the differences between the policies are what the comparison isolates.

| Policy | Hard-goal success | Mean tokens | Pre-completion goal drift |
|---|---|---|---|
| Execute the first candidate | 67.42% | 32,058 | 0.2721 |
| Budget-only: skip a candidate that will not fit the remaining budget | 67.85% | 32,170 | 0.2718 |
| Choose among three candidates | 96.53% | 19,782 | 0.1290 |
| Full governance architecture | 96.57% | 12,574 | 0.0000 |

The selecting policy added no external adjudicator: it "selects using only the generator's own declared action-to-goal links (preferring a declared link to an unmet governed criterion, with lower token cost as a tie-breaker)" ([§8.3](https://arxiv.org/abs/2609.30662v1)). The full governance architecture on top of that added 0.04 points of success and cut mean tokens by 36.4%. It bought a token saving, not a higher success rate. Its zero drift is an artifact of its own gate: "zero pre-completion GDR is likewise substantially enforced by the default independent scope gate" ([§9.1](https://arxiv.org/abs/2609.30662v1)).

## Why it works

The candidate stream carries 28% optional proposals ([§8.4](https://arxiv.org/abs/2609.30662v1)). A loop that takes the first one executes them at close to that rate (its pre-completion drift is 0.2721) until the ceiling runs out with hard criteria still open. Selection redirects the identical opportunities toward required work. The paper's §9.1 concludes that "access to multiple candidate opportunities explains most of the success gain" ([§9.1](https://arxiv.org/abs/2609.30662v1)).

## When this backfires

- Candidates are free in the benchmark and not in your loop. Every policy pays the same "120 planning tokens plus the selected action cost" per cycle ([§8.4](https://arxiv.org/abs/2609.30662v1)), so seeing three proposals costs no more than seeing one. "Real agents, however, often generate candidates adaptively from their evolving state" ([§11.3](https://arxiv.org/abs/2609.30662v1)), and generation is the cost this benchmark never charges.
- Adjudication inverts the result at a modest price. Charging 500 synthetic governance tokens per cycle drops the full architecture to 89.88% success at 23,251 mean tokens ([§9.5](https://arxiv.org/abs/2609.30662v1)), behind the plain three-candidate policy on both numbers. The paper runs that sweep against the first-candidate baseline only; setting it beside the three-candidate policy is arithmetic over its own two tables.
- The selection signal is a proxy, and proxies get optimized against. Reward hacking "can arise through parameter updates, selection among generated outputs, or revisions to persistent prompts" ([Wahi, 2026](https://arxiv.org/abs/2609.25848v1)). The selector here reads the generator's self-declared link, and Xiao et al. state that "the generator's self-declared link is not authoritative" ([§5.2](https://arxiv.org/abs/2609.30662v1)).
- Removing the no-progress breaker "slightly improved synthetic efficiency", which the authors record as "an important negative result" ([§9.3](https://arxiv.org/abs/2609.30662v1)). A component can be sensible and still fail its own ablation.
- The baseline is built to lose. Once it believes the work is done it notices "with probability 0.12 per cycle" ([§8.4](https://arxiv.org/abs/2609.30662v1)), and that rate is a benchmark parameter: "baseline stopping propensity are stress-test parameters, not fitted estimates of a named LLM" ([§11.1](https://arxiv.org/abs/2609.30662v1)). The 29-point gap the selection policy closes is partly a property of that setting.

## Key Takeaways

- Treat the first proposal as one option. Selection among three candidates carried nearly the whole success gain in this benchmark.
- A token ceiling is an accounting limit rather than a decision rule ([§10.8](https://arxiv.org/abs/2609.30662v1)). Every policy already shared a 40,000-token ceiling, and adding a remaining-budget feasibility gate on top of it moved success from 67.42% to 67.85% ([§9.1](https://arxiv.org/abs/2609.30662v1)).
- Price the layer before you add it. At 500 governance tokens per cycle the architecture falls behind the plain three-candidate policy on both success and tokens.
- Read the zero in the drift column as a gate invariant the implementation enforces, not an effect it measured.
- None of this has run against a live model, and the authors say live validation is still required.

## Related

- [Minimum-Sufficient Control Ladder: Escalate by Failure Mode](../agent-design/minimum-sufficient-control-ladder.md) — the ordering rule this result argues for, applied to agent controls generally
- [Prompt-Only Baseline Before a Specialized Agent Subsystem](../agent-design/prompt-only-baseline-before-specialized-subsystem.md) — the same measurement discipline for memory and self-improvement harnesses
- [Adaptive Generate-Rank-Verify Under Costly Verification](../agent-design/adaptive-generate-rank-verify.md) — how to spend an expensive verifier once candidate generation is cheap
- [Objective Drift: When Agents Lose Sight of the Goal](objective-drift.md) — the failure the drift column here is measuring
- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — why a token saving is not automatically a cost saving
