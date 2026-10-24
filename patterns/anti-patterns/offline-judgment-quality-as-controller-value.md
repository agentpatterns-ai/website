---
title: "Treating Offline Judgment Quality as In-Loop Controller Value"
term: "Judgment-to-Intervention Gap"
description: "A decision model that ranked an agent's finish requests at AUROC 0.78 still raised cost per attempt 19% at an unchanged 73.0% pass rate, because its argmax fired below the base rate."
tags:
  - anti-pattern
  - cost-performance
  - loop-engineering
  - tool-agnostic
  - arxiv
aliases:
  - judgment-to-intervention gap
  - decision-model controller cost
  - AUROC as controller evidence
last_reviewed: 2026-10-21
maturity: emerging
---

# Treating Offline Judgment Quality as In-Loop Controller Value

> A controller that ranks its decisions best can still raise cost per attempt 19% at an unchanged pass rate, because the action policy decides value.

Ranking skill does not make a controller worth wiring in. A pre-specified study on Terminal-Bench 2.1 held one Claude Sonnet 5.5 terminal loop fixed and varied only the controller across five arms. The typed decision model Jev 1.13 ranked finish requests better than every alternative and still cost more for nothing: "On 21 held-out tasks (315 trials), Jev raised cost per attempt by 19% (geometric-mean ratio 1.19, 95% CI 1.02-1.36) at an identical pass rate (73.0% vs. 73.0%)" ([Vats, arXiv:2610.24649v1](https://arxiv.org/abs/2610.24649v1)).

## The four conditions behind the null result

The null result is a verdict on one policy, not on in-loop controllers. Check all four against your own setup first.

- The controller's actions are advisory nudges on an event that already succeeds. 87% of the unaided loop's finish requests passed the grader.
- The policy acts on the argmax instead of a cutoff derived from that base rate. Jev "therefore chose verify for 29 of 53 finish requests, and its argmax accuracy (0.55) fell below the base rate (0.87)" ([Vats, arXiv:2610.24649v1](https://arxiv.org/abs/2610.24649v1)).
- The controller holds no stopping action it will actually use. "No controller chose abandon in any of the 315 trials."
- The evaluation has no placebo arm, so you credit the cost to the act of intervening rather than to the content of the advice. Without one, "the comparison against native alone would suggest only that Jev is somewhat expensive" ([Vats, arXiv:2610.24649v1](https://arxiv.org/abs/2610.24649v1)).

## Why it works

A controller moves cost only through the reasoning model's subsequent trajectory. Its own calls are a rounding error: "Controller calls were negligible: Jev averaged 0.52 s per decision and 0.11% of spend" ([Vats, arXiv:2610.24649v1](https://arxiv.org/abs/2610.24649v1)). Every advisory message it appends buys more steps on the expensive model, and "Cost rose with how often a controller asked the agent to verify" in the same order across the four controller arms. Jev also ran longer trajectories throughout, 16.0 steps per attempt against 13.3.

The base rate of the event under review sets whether those steps are worth buying, and an AUROC figure does not report it. Jev's probabilities sat far below that rate, so argmax turned good ordering into frequent low-value interventions: "the agent's own finish requests were usually right (87% of native finish requests passed), so a verification round is mostly spent re-checking correct work." Even the runs it doubted most were mostly fine, since "even Jev's least confident group passed 79% of the time." The paper names the gap: "The gap between an informative signal and a useful intervention is the policy in between."

The placebo arm licenses that attribution. Choices sampled at random from Jev's own frequencies at the same trigger moments cost no more than the unaided loop, at a 0.98 ratio: "Random guidance at the same moments matched every informed controller's pass rate without their cost."

## When this backfires

Reading this as "keep cheap models out of the loop" overshoots the evidence.

- A calibrated stopping action does save money. BAGEN reports that "Early stop saves 28-64% tokens on failed trajectories, and SFT+RL strengthens early stop and alert behavior" ([BAGEN, arXiv:2606.00198v1](https://arxiv.org/abs/2606.00198v1)). Jev's cost-saving action went unused, not tested and found wanting.
- Controller quality varies and is measurable. LoopArena puts the best full-task Strict Success Rate at 36.25%, "leaving substantial room for improvement in long-horizon loop control" ([Wang et al., arXiv:2608.28281v2](https://arxiv.org/abs/2608.28281v2)).
- The pass-rate half is weak either way. The author says "pass-rate intervals are wide" on a held-out set of 21 tasks, about ±11 to 13 percentage points. That leaves the no-harm guardrail at the limit of what the design resolves.
- Runs ending at a timeout or a budget cap raise no finish request, so a verify-only controller has nothing to second-guess. Jev's three clear cost reductions were hard tasks of exactly that shape.
- Your harness may be mismeasuring verification. A naive feature asking whether the agent verified "misses agents that check work by running their own programs."

## Example

The before case is the comparison the study warns against. The after case is the arm set it ran.

**Before — a controller chosen on the AUROC column:**

```text
offline Q-finish quality, 53 logged states
              AUROC    ECE   accuracy
base rate      0.50   0.00       0.87
rules          0.62   0.55       0.45
small LLM      0.60   0.70       0.30
Jev 1.13       0.78   0.37       0.55
```

**After — the same controller measured end to end against rules and a placebo:**

```text
arm         pass %   USD/attempt   verify msgs/attempt
native       73.0       0.177            -
rules        73.0       0.191           0.92
small LLM    76.2       0.213           1.30
Jev          73.0       0.206           0.51
placebo      71.4       0.156           0.33
```

The AUROC column ranks Jev first, and the accuracy column already puts it 32 points under the base rate. End to end it comes fourth of five on cost, below a placebo that samples its own choice frequencies at random ([Vats, arXiv:2610.24649v1](https://arxiv.org/abs/2610.24649v1)).

## Key Takeaways

- Bill the controller's advice to the reasoning model, not to the controller's own invoice line. Jev's calls were 0.11% of spend and the small LLM's 0.47%, so neither shows up in the budget it moves.
- Derive the action cutoff from the base rate of the event you are gating. An argmax accuracy of 0.55 against an 0.87 base rate means the controller chose verify on 29 of 53 finish requests when 87% of them passed unaided.
- Run a placebo arm that fires at the same trigger moments with shuffled choices. Without it you cannot tell advice from interruption, and here the placebo was the cheapest arm in the study.
- Give the controller a stopping action and check whether it ever fires. Across 315 trials the only cost-saving action available was never chosen once.
- Report cost per attempt and cost per solved task together. Jev's USD per solved task was 0.283 against 0.243 for the unaided loop, so the pass-rate tie hid no compensating gain.

## Related

- [Calibrated Deciders for In-Loop Agent Decisions](../agent-design/calibrated-deciders-in-loop-decisions.md) — the ranking test a decider has to clear first, which this page shows is necessary and not sufficient.
- [Calibrated Early Termination and Warm Restart for Agent Runs (FailFast-RestartSmart)](../../loop-engineering/early-termination-and-warm-restart.md) — the stopping action Jev never used, with the false-positive budget that makes it pay.
- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](cheaper-per-token-costlier-per-task.md) — the same sticker-price error one layer down, where the cheap model generates instead of advising.
- [Decision Unbundling: What Moves Into the Orchestrator](../agent-design/decision-unbundling-orchestrator-load.md) — what your code picks up when a decision leaves the driver model, including the threshold this page says to derive.
- [Premature Completion](premature-completion.md) — the opposite failure, where an agent stops early and the loop has no check at all.
