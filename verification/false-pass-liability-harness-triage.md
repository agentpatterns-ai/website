---
title: "False-Pass Liability Decides the Next Harness Component"
term: "False-Pass Liability"
description: "Price an erroneous accept before choosing a planner or a completion check — the two flip order as that liability rises, and the check only withholds work."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - liability per false pass
  - erroneous acceptance cost
  - harness component triage
last_reviewed: 2026-09-18
maturity: emerging
---

# False-Pass Liability Decides the Next Harness Component

> Price an erroneous accept first. That liability, not a benchmark score, decides whether you build the planner or the completion check.

False-pass liability is what your system loses when it accepts work that is wrong. It is the input that ranks harness components against each other, because a planner and a completion check pay out on different terms. A component ablation in τ²-bench found that a prewritten task-specific plan raised oracle-verified success by 7.17 percentage points over a word-count-matched sham control, across 265 matched cells, while a read-only terminal verifier cut the false-pass rate from 57.21% to 20.96%, with nearly all of that reduction coming from its rejection flag rather than from different agent behavior ([Zhang et al., arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1)). A success rate and a rejection rate do not compare on their own. The price you put on a wrong accept is what makes them comparable.

## The condition that flips the order

The paper values each component against a minimal harness on matched samples, under a liability weight `L` in USD per false pass. In the high-risk Retail stratum at `L = 2`, the fixed planner returns the most (mean net value 1.9748) and the standalone verifier 1.5275. At `L = 200` the order reverses: the verifier returns 97.3133 against the planner's 35.1299 ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), Table 7). Two grid points is a bracket, not a threshold, so the usable rule is directional. Where a wrong accept is cheap to catch and undo downstream, fund the planner. Where it reaches a customer, a ledger, or a production branch, fund the check.

Read the scope before you transfer the numbers. These are tool-using service agents in Retail and Airline task environments, not coding agents. The pooled rates in the table below are unbalanced and unpaired, and the scenario values above rest on matched-pair counts that differ by configuration: 217 for the planner, 214 for the verifier, 135 for the full stack ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), Tables 6 and 7).

## Why it works

The completion check never repairs anything. It runs on the executor's own model after the episode ends and after oracle scoring, reads at most the last eight messages truncated to 300 characters each, gets no database access, and raises one rejection flag when its 200-token reply contains `INCOMPLETE` ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), §4.4). The paper decomposes the 37.34-point false-pass gap against the minimal harness: 36.24 points come from the rejection flags and 1.09 from differences in what the agents actually did (§6.1). Withholding is the entire product.

The self-correction literature lands on the same distinction from the other side. Stechly et al. measured a performance collapse under self-critique and gains under sound external verification, and reported that re-prompting with a sound verifier can "maintain most, if not all, of the gains shown by our previous, more complicated, more expensive setups" ([arXiv:2402.08115v2](https://arxiv.org/abs/2402.08115v2)). Cost follows the same shape. One extra call on a truncated transcript added 0.0079 USD per episode, while the full planning-plus-verification stack avoided 49.82 points of false pass against the standalone verifier's 48.38 and charged twelve times the incremental cost ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), §7.3).

## When this backfires

- Reversals are cheap. At `L = 2` the planner wins on mean net value, and a check that withholds correct work to block a mistake you would have caught downstream is the worse buy.
- You wire verification as a repair loop. The evaluator-plus-repair arm moved false pass from 0.5830 to 0.5702 against the minimal harness, roughly doubled mean cost (0.0136 to 0.0268 USD), and lowered verified success ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), Table 6).
- Your domain withholds more correct work. Retail withheld 16 of 92 correct episodes (17%) and the Airline pilot withheld 7 of 17 (41%), on 17 episodes ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), §6.1 and §6.3).
- The failure never reaches the transcript. A check reading eight truncated messages with no database access cannot reject a silent state corruption.
- Rejected work has nowhere to go. The paper leaves plan authoring, integration, maintenance, human review, and the opportunity cost of withholding correct outcomes outside its cost model, and states that following rejected cases through repair, escalation, or abandonment has not been measured ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), §7.5 and §8.2).
- You expect the check to be sound. It still admitted 54 of 137 invalid Retail episodes ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), §6.1). Intrinsic self-correction without external feedback can degrade performance outright ([Huang et al., arXiv:2310.01798v2](https://arxiv.org/abs/2310.01798v2)).

## Example

The pooled Retail configuration table makes the two currencies visible side by side ([arXiv:2609.20474v1](https://arxiv.org/abs/2609.20474v1), Table 6):

| Configuration | Verified success | False pass | Mean cost (USD) |
|---|---|---|---|
| Minimal | 0.3787 | 0.5830 | 0.0136 |
| Planner, fixed plan | 0.4810 | 0.5021 | 0.0135 |
| Evaluator plus repair | 0.3617 | 0.5702 | 0.0268 |
| Terminal verifier only | 0.4017 | 0.2096 | 0.0164 |

Rank these on verified success and the planner wins outright, at no extra pooled cost. On false pass, the terminal verifier cuts 37 points, against 8 for the fixed plan. The evaluator arm bought about one point of false-pass reduction for double the cost, which is the case against treating "add verification" as the finding. Samples are unbalanced across rows, so read the table as direction rather than as a paired estimate.

## Key Takeaways

- Start from the price of one erroneous accept. Without it you are holding a success rate next to a rejection rate, and nothing puts the two in order.
- Budget the correct work a check withholds, not only the tokens it burns. That line is absent from the paper's own cost model, and it is the one your users feel.
- Decide whether you are buying a terminal reject flag or a repair loop before you cost the work. The two arms priced out a factor of two apart, and the repair loop moved the false-pass rate by about one point.
- Reach for the full stack only after the cheap check disappoints you, because the standalone version already took almost all of the avoided false pass at a twelfth of the incremental cost.
- Re-measure before porting the ordering. The share of correct work withheld more than doubled between two task environments inside one paper.

## Related

- [Verify-Gated Completion as Admission Control](../patterns/multi-agent/verify-gated-completion-admission-control.md) — how to build the read-only gate once you have decided to fund one.
- [Verification Surface: Match the Tool to the Failure](verification-surface-reach-and-cost.md) — picking the checking tool whose reach covers how your application actually fails.
- [Verification Capacity as the Agent Quality Ceiling](verification-capacity-quality-ceiling.md) — what happens when generation outruns the throughput of the gate.
- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — why the repair half of verification pays back over so few rounds.
- [Validity-Estimate Stopping for Noisy Verify-Repair Loops (VRR-Stop)](validity-estimate-stopping-noisy-repair-loops.md) — what a noisy verifier does to acceptance once repair starts damaging correct work.
