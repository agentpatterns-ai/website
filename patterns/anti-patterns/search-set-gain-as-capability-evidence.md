---
title: "Search-Set Harness Gain as Capability Evidence"
term: "Unattributed Harness Gain"
description: "A harness gain measured where you tuned can reflect overfitting, extra inference compute, or capability. Two control arms separate them; the score alone cannot."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - unattributed harness gain
  - harness-delta attribution
  - search-set gain attribution
last_reviewed: 2026-10-19
maturity: emerging
---

# Search-Set Harness Gain as Capability Evidence

> A search-set harness gain has three possible sources, so split it before calling any of it capability.

An unattributed harness gain is a tuned harness's improvement read as capability before separating its causes. Harness-Delta Attribution separates overfitting, gains a compute-matched baseline reproduces without tuning, and a residual ([Ding et al., 2026](https://arxiv.org/abs/2610.22466v1)). Across 21 significant search-set gains, overfitting averaged 54% and test-time scaling 14%. Their combined share exceeded half in 14 settings.

## Test the gain before attributing it

Run a paired bootstrap significance test on baseline and tuned scores. The paper says "we report it as within noise and do not assign an attribution" when the difference fails that gate. Four of its 25 settings received no attribution ([§3](https://arxiv.org/abs/2610.22466v1)).

For a significant gain, run two controls:

- Raise the original harness's inference budget to the tuned harness's measured spend. Aggregate samples using a task-appropriate rule, such as majority vote or pass@10. The recovered gain estimates test-time scaling without harness evolution.
- Disable each detected shortcut through "the smallest intervention that disables the shortcut", leaving unrelated evolved components in place. The score drop estimates overfitting ([§3](https://arxiv.org/abs/2610.22466v1)).

If the tuned harness spends no more compute, the protocol sets the compute arm equal to baseline and its scaling share to zero. Attribution percentages divide by the observed gain. Overfitting is capped at 100%, scaling at the remaining share, and the residual receives the rest.

## Why it works

Selection rewards whichever candidate scores highest on the search set, including candidates that exploit benchmark artifacts. Compute matching tests whether additional sampling explains the gain. Shortcut neutralization tests the contribution of a detected artifact.

These estimates have opposite limits. Overfitting is "a lower-bound estimate of overfitting, since implicit or entangled mechanisms may remain". The residual is "an upper bound on generalizable improvement rather than evidence of transfer" ([§3](https://arxiv.org/abs/2610.22466v1)).

## When this backfires

- An insignificant gain has no attribution under this protocol.
- An undetected or inseparable shortcut remains in the residual. A low overfitting estimate cannot establish absence.
- Held-out tasks preserve an artifact shared across splits. They can confirm a shortcut rather than transfer.
- Validation selection leaves a gap. Across 16 Meta-Harness settings, it improved held-out scores in 10 and reduced them in 6. In 14, the validation-selected held-out gain remained below the search-selected search-set gain ([§5](https://arxiv.org/abs/2610.22466v1)).
- Prevention is a separate option. HarnessCompass restricts changes to task-agnostic modifications and reports transfer to held-out tasks and other models ([Zhang et al., 2026](https://arxiv.org/abs/2608.01918v1), abstract). That result does not validate another search procedure's winner.

## Example

The study's controls expose different explanations for a winning score ([Ding et al., 2026](https://arxiv.org/abs/2610.22466v1)):

| Setting | Observation | What the headline misses |
|---|---|---|
| Meta-Harness, CREATE | The compute arm recovered 49% of Haiku 4.5's gain and exceeded the tuned Qwen3.6-35B-A3B harness | Extra sampling explains part or all of those gains |
| One Meta-Harness ALFWorld run | A 0.8B executor's harness grew from 66 to 503 non-blank, non-comment lines and reached 100% search-set success with no LLM calls | The controller hard-coded benchmark priors |
| LiveMath | A meta-option was correct in all 21 search questions containing it, out of 35 questions; all three frameworks found it | The artifact appeared across search, validation, and test splits |
| Two Meta-Harness SWE-bench rows | Attribution was 0/0/100, yet held-out scores regressed | A 100% residual does not demonstrate transfer |

For one LiveMath executor, test accuracy was 53/53 on questions containing the meta-option and 22/71 elsewhere. Across ALFWorld settings, overfitting averaged 89% of search-set gain despite strong held-out gains ([§5 and Appendix G](https://arxiv.org/abs/2610.22466v1)).

## Key Takeaways

- Establish a significant gain before running attribution.
- Compare against a compute-matched baseline and a shortcut-neutralized harness.
- Report the residual as a ceiling on generalizable improvement.
- Test protocol artifacts as well as held-out task content.

## Related

- [Held-Out Tasks as a Harness Shortcut Defense](held-out-tasks-as-shortcut-defense.md) — why resampling the questions leaves a protocol-level shortcut in place, the defense this page measures around
- [Fleet Harness Attribution](../agent-design/fleet-harness-attribution.md) — the prior question of whether the harness or the model owns an outcome, settled by pinning the model
- [Isometric Harness Ablation](../agent-design/isometric-harness-ablation.md) — removing one subsystem at a time to rank investment, the same one-variable discipline applied to harness structure
- [Harness Hill-Climbing](../agent-design/harness-hill-climbing.md) — the eval-driven tuning loop whose selection rule creates the pressure described here
- [Measure Agent Experience Against a Bare Baseline](../../verification/ax-bare-baseline-lift-drag.md) — reporting task cost beside quality, which is what makes a compute-matched comparison possible
