---
title: "Coverage Ceilings: Score Generated Eval Suites Per Cell"
term: "Coverage Ceiling"
description: "A defect reaching b passing scenarios moves an N-scenario suite by at most b/N on its own. Publish that ceiling and score generated eval suites per cell."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - per-cell suite scoring
  - scoped defect detection
  - generated suite coverage ceiling
last_reviewed: 2026-11-21
maturity: emerging
---

# Coverage Ceilings: Score Generated Eval Suites Per Cell

> A defect reaching b passing scenarios contributes at most b/N to a generated suite's pass-rate drop, so publish that ceiling and score its covered cells.

This applies when each generated scenario records the requirement or tool it exercises. A coverage ceiling is the most a defect can itself move a suite's pass rate. If b of the scenarios it reaches pass at baseline, its contribution over a suite of N is at most b/N, and you can compute that from baseline results before the defect exists ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)). When the ceiling sits at or below your detection threshold, the defect's own effect cannot push the suite mean past it. Scoring the covered cells alone recovered a tool-removal defect the mean missed. It did not recover a behavioral defect, forced escalation, which only the whole suite detected.

## The study behind the ceiling

Yadav injected 7 controlled defects into a τ²-bench airline agent and replicated two of them in the retail domain. The generator read the domain policy and emitted a fully covered grid of 90 scenarios: 30 requirements times three scenario kinds, with 8 personas driving the conversations. One model played agent, user simulator, and judge. A suite detected a defect when the pass rate dropped by more than 0.10 and a 2,000-sample paired bootstrap interval excluded zero ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

Under that rule the generated suite detected 1 of 7 airline defects and the hand-authored suite 0 of 7. Of the 5 airline defects with a traceable footprint, 4 had a ceiling at or below the 0.10 threshold on both suites. The paper calls 0.10 "a convention, not a quantity derived from the data". At 0.05 only one defect stays ceiling-bound ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

## A total breakage that reads as an improvement

Removing one tool (`cancel_reservation` on airline, `exchange_delivered_order_items` on retail) failed every hand-authored task that required it and had passed at baseline: 3 of 3 on airline and 6 of 6 on retail. The hand-authored suite's pass rate still rose, from 25 to 27 of 50 tasks on airline and from 20 to 21 of 48 on retail, because "off-target drift exceeds what the defect destroyed." The author's reading: "averaging over the archive does not merely dilute the signal, it inverts it." ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1))

A high ceiling does not rescue the mean either. Truncating the policy to its first 40% touched 51 of 90 scenarios, a ceiling of 0.49, and was still not detected ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

A production ordering agent shows the same masking with no generator involved: six injected local regressions moved the aggregate pass rate by 1.7 to 5.9 points while the matching slice fell 25 to 91 points. Its authors note the slice reaction "is partly by construction" ([Layer-Isolated Evaluation, arXiv:2606.11686v1](https://arxiv.org/abs/2606.11686v1)).

## Two regimes, two units of scoring

| Regime | Footprint | Right unit | Evidence |
|---|---|---|---|
| Trace-aligned | A requirement or a tool the generator's descriptors name | The covered cells | Tool removal: scoped drop of +0.43 and +0.67 on airline, +0.43 on retail, every interval excluding zero |
| Trace-orthogonal | A behavior, with no descriptor for it | The whole suite | Forced escalation: transfers rose from 36% to 84% of airline hand-authored conversations; the airline scoped interval touched zero on both suites |

Source: [Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1).

Per-cell scoring also tells a regression from an accidental fix. Deleting the 24-hour cancellation clause made the agent better on the 13 tasks it touched, a significant scoped improvement, because the baseline agent had over-applied that clause. In the paper's words, "A suite-level difference sums regressions and accidental fixes; per-cell scoring separates them." It is not automatic: inverting a policy condition never reached the threshold under scoped scoring ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

The regime also picks the grader. Under programmatic end-state checks, forced escalation scored no worse, because "where the expected end state is reachable by inaction an end-state check cannot tell doing nothing from doing the right thing; the transcript judge sees it in both domains" ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

## What to publish with a generated suite

1. Record each scenario's requirement, persona, and kind, plus the tools its grading names.
2. For each element a change can touch, list the covered scenarios, count the b that pass at baseline, and report b/N beside the threshold. A ceiling of zero is a coverage hole the suite can name about itself.
3. Score the covered cells with the same paired test as the whole suite, and keep the whole-suite score for behavioral defects.
4. Keep scenario kinds mixed. At 30 scenarios, a happy-path-only airline suite detected none of the 7 defects, while kind-diverse suites detected forced escalation in 5 of 20 draws. The author calls this "positive, though exploratory" ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

The paper also proposes behavioral cells, such as "does this conversation escalate, does it call this tool", computed from baseline transcripts. It adds: "We have not evaluated either construction here." ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1))

## Why it works

A defect can only change a scenario it reaches. If b covered scenarios pass at baseline, the worst it can do on its own is flip all b, which moves an N-scenario suite by b/N. With small b and large N that change cannot cross a fixed threshold, and drift in the scenarios it does not reach can match or reverse it. Scoring only the covered cells sets the denominator to the covered count and removes the dilution ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1), §3.3). The bound holds only where the trace finds every affected scenario. A renamed tool parameter that no grading criterion names escaped the trace, and noise or behavioral effects can push an observed drop past the ceiling.

## When this backfires

- Scenarios with no record of the requirement or tool they exercise. Without that trace you cannot compute coverage or a ceiling.
- Behavioral defects. No requirement cell holds the footprint. On the airline generated suite, scoping to the 9 scenarios that name escalation lost the detection the whole suite made.
- Many small cells tested without correction. Each cell is a separate hypothesis, and "A naive testing procedure that does not adjust for multiplicity could surface a large number of spurious failure modes simply by chance (Type I error)" ([Context-Aware Testing, arXiv:2410.24005v1](https://arxiv.org/abs/2410.24005v1)). Correction in turn tightens the per-test threshold, and one covered cell in this study held 3 scenarios ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).
- Single-run baselines. Three reruns of each covered airline hand-authored task for the tool-removal defect found that two of three baseline passes did not recur, shrinking the scoped drop to 0.14 ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).
- Generalizing from this study. It used two domains of one benchmark and one model as agent, simulator, and judge. Hand-authored intervals ran about ±0.15 wide, and the scoped scores and ablations are post hoc ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)).

## Example

The tool-removal defect on the airline generated suite, from Table 1 of the paper ([Yadav, arXiv:2611.17632v1](https://arxiv.org/abs/2611.17632v1)):

| Measure | Value | Detected at 0.10 |
|---|---|---|
| Covered scenarios | 12 of 90 | n/a |
| Ceiling | 0.09 | n/a |
| Whole-suite drop | +0.08 [+0.00, +0.17] | No |
| Scoped drop over the 12 covered | +0.67 [+0.42, +0.92] | Yes |

The ceiling of 0.09 said, before the defect existed, that the suite mean could not reach 0.10 from this defect alone. The deleted cancellation clause had zero covered scenarios on the same suite: "a requirement-traced suite can report that about itself; a hand-authored suite cannot."

## Key Takeaways

- Compute b/N for each element you expect to change before you run the defect. A ceiling at or below the threshold means the defect's own effect cannot carry the suite mean past it.
- A suite mean can report a total tool breakage as a small improvement, as the hand-authored suites did in both domains of the study.
- Score tool and requirement defects at the covered cells. Score behavioral defects on the whole suite with a transcript judge.
- Correct for the number of cells you test, and rerun small cells before acting on them.

## Related

- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — the bound to state when a config change shows no effect at all.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the noise a per-cell drop has to clear on small cells.
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the seeded-fault method this study applies to agent configurations.
- [Measuring Synthetic Eval Data Quality (SynAE)](synae-synthetic-eval-quality.md) — scoring a synthetic suite's diversity and fidelity before it gates anything.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — other gaps that come from how you measure.
