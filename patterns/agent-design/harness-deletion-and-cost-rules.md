---
title: "Deletion and Cost Rules for an Evolving Agent Harness"
term: "Harness Deletion Rule"
description: "Score-only acceptance never removes anything from a self-improving agent harness. Add a deletion rule for components that stopped earning and a price for the ones that did."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - harness pruning rule
  - regularized harness evolution
  - cost-gated harness acceptance
last_reviewed: 2026-09-25
maturity: emerging
---

# Deletion and Cost Rules for an Evolving Agent Harness

> Score-only acceptance never deletes anything, so a self-improving harness accumulates cost while its transfer stalls.

Add a deletion rule and a cost rule to the acceptance step of any loop where a search, not a person, proposes harness edits. Score-only acceptance runs one way. A candidate is admitted on its measured score, and no rule ever re-examines a component the loop accepted four rounds ago.

## The three conditions

All three have to hold. Miss one and these rules are machinery with nothing to constrain.

- A search proposes the edits. [Harness hill-climbing](harness-hill-climbing.md) run by hand already gives you attribution and a reviewer.
- You deploy somewhere other than the split you evolve against. These rules trade in-distribution score for transfer, so a narrow task family you own is the case where they cost more than they return.
- Each edit is attributable to a named harness component. Without that, the deletion rule has nothing to compute against.

## The cost column is the finding

One ablation on an agentic-workspace instance compares four arms. Read the token column next to the transfer column ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2), Table 2):

| Harness | Evolve set | Out-of-distribution average | Tokens per trial |
|---|---|---|---|
| Unevolved base | 89.4 | 39.7 | 1.56M |
| Unregularized evolution | 92.8 | 40.3 | 3.80M |
| Acceptance rules removed | 91.5 | 41.0 | 3.59M |
| Full method | 90.5 | 43.6 | 2.42M |

Unregularized evolution bought 3.4 evolve-set points and 2.4 times the token cost for 0.6 points of transfer, which left it "within a point of the unevolved harness" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Row three is the one this page is about, because it isolates the acceptance side. Dropping those rules alone cost 2.6 points of transfer and pushed tokens up by half, "showing that an unconstrained selection rule spends most of its accepted edits on noise and on context rather than on mechanism" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)).

The paper splits its constraints by where they act: proposal-side steers what the search drafts, acceptance-side decides what survives. Removing either group "raises the evolve-set score and lowers transfer" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Both rules below are acceptance-side, and the proposal-side edit cap they depend on is in the next section.

## The two rules

Delete what stopped earning. Mark a component unproductive when it "has been exercised but has produced no strictly positive measured gain in the recent pruning window", then hand it to the proposer as a deletion target ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). The published window is 4 rounds for the coding and agentic-workspace instances and 5 for engineering design.

Price every accepted edit. Require that "additional inference cost must be justified by measurable performance improvement" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Two settings carry it: a flat allowance that "sets the cost increase tolerated for a negligible score gain", and a second that "controls how much additional cost is allowed as the measured improvement increases".

Both rules need a noise band underneath them. The method estimates one "from repeated evaluations of the unchanged base harness", then requires every candidate to clear the best score so far minus that band ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). The calibrated bands are narrow: on the coding instance the band "corresponds to 3 passes out of 89×k=178 trials".

## Why it works

Deletion depends on attribution, and a cap on edits per candidate is what supplies it. A candidate bundling many edits has "high effective capacity: they can fit more idiosyncrasies of the current feedback, and any measured change is difficult to attribute to a particular mechanism" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Anneal the cap toward one edit and each measured delta maps to a named component. The pruning evidence "becomes more attributable as the edit budget anneals toward one" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Only then can the loop ask whether a specific component earned anything recently. The paper names the asymmetry these rules correct. A mechanism persists "simply because score-only evolution has no incentive to remove it" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)).

## When this backfires

- The loop may not be worth constraining. Under comparable feedback and inference budgets on Terminal-Bench 2.1, "automatic harness evolution does not consistently outperform simple test-time scaling methods and exhibits limited generalization" ([arXiv:2607.12227v2](https://arxiv.org/abs/2607.12227v2)). Without unit tests, parallel sampling averaged 72.3 against harness evolution's 67.4. Price a parallel-sampling arm before arguing about acceptance rules.
- The defect may be the edits, not the acceptance rule. On held-out tasks the same study measured the evolved harness improving "Claude Opus 4.6 by a mere 1.2 points", and GPT-5.4 not at all. Its diagnosis: "most edits memorize fixes rather than distilling strategies" ([arXiv:2607.12227v2](https://arxiv.org/abs/2607.12227v2)). Deletion removes dead machinery. It does not turn a memorized fix into a strategy.
- Set them too tight and the loop returns nothing. In one counterfactual harness search, every second-round candidate violated an ε=0.05 constraint "despite released gains as high as 15.31%", and the method fell back to the original harness ([arXiv:2609.18366v1](https://arxiv.org/abs/2609.18366v1)).
- Your footprint is not policy tokens. The cost rule uses "policy-token cost as a common measurable proxy" for the harness footprint ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). Where the cost that hurts is wall-clock, tool-call side effects, or human review, the rule binds on nothing.
- The thresholds are fitted where the risk is. The authors select every hyperparameter "using only the evolve environment", and state that "held-out and OOD benchmarks are not used for tuning" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)). That is the right discipline, and it means the band defending against evolve-set overfitting is calibrated on the evolve set.

Scope: frozen backbone models only, and the authors state that "broader validation is needed to determine how well the method generalizes to substantially different agent architectures, tool ecosystems, and longer-running self-improvement processes" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2)).

## Example

One coding round produced two similar candidates. Both added verification and long-running-work guidance. The first was accepted at "+3.93 points on the evolve set". Its sibling was "Rejected by cost rule: +1.69 points, +26.1% cost" ([arXiv:2609.24972v2](https://arxiv.org/abs/2609.24972v2), Table 6). A later round cut cost by 13.6% and was rejected too, because its score dropped 2.81 points, which put it under the noise-adjusted floor. Cheaper does not buy admission, and neither does a positive delta on its own.

## Key Takeaways

- An automated harness loop needs a rule that removes things. Score-only acceptance has none, so the harness grows every round.
- Read the token column beside the transfer column. Unregularized evolution spent 2.4 times the tokens for 0.6 points of out-of-distribution gain.
- Expect the constrained harness to score lower on the split it tuned against. That is the trade, not a defect.
- Calibrate your harness's run-to-run noise band before you accept any edit, by rerunning the unchanged base harness.
- Cap edits per candidate first. You cannot delete a component whose contribution you never measured on its own.
- Measure a parallel-sampling arm at the same budget before committing to the loop at all.

## Related

- [Harness Hill-Climbing](harness-hill-climbing.md) — the hand-run version of the same loop, whose overfitting defenses are all measurement-side
- [Reliability of an Automatically Selected Agent Harness](harness-selection-reliability.md) — constrains what the optimizer may edit to shrink run-to-run selection variance, and reports what the pick is worth
- [Agentic Flywheel](agentic-flywheel.md) — the loop where agents propose their own harness changes against an eval gate
- [Observability-Driven Harness Evolution](observability-driven-harness-evolution.md) — pairs each edit with a prediction, an attribution route the cost rule does not supply
- [Isometric Harness Ablation](isometric-harness-ablation.md) — measuring one subsystem's contribution at a fixed model, which is what a deletion rule needs each round
