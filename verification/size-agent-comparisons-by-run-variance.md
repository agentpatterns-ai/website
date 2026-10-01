---
title: "Size Agent Comparisons by Run-to-Run Variance"
term: "Run-Variance Sizing"
description: "When one agent-model pairing varies more between its own runs than pairings differ, a three-run comparison picks the wrong winner 28 to 44 percent of the time."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - run-to-run variance sizing
  - repeat-run sample sizing for agent comparisons
last_reviewed: 2026-09-30
maturity: emerging
---

# Size Agent Comparisons by Run-to-Run Variance

> Measure how much one agent-model pairing varies between its own runs, then size the comparison on that spread before you rank pairings.

This technique applies when you compare agents or models on your own multi-step task with a continuous score, and the gap that would change your decision is near or below one run-to-run standard deviation (SD). Under those conditions a handful of runs cannot separate the candidates. For larger gaps a few runs are enough, and for near-deterministic single-turn tasks the technique does not apply (see [When this backfires](#when-this-backfires)).

## The evidence

Ariño de la Rubia and Pafka ran 584 coding-agent runs on one tabular prediction task, including 52 runs for each of six agent-model pairings. Among the runs that followed the task rules, the six pairing means spanned 0.0095 AUC, and the median pairing SD across its own runs was 0.0107. In the paper's words, "Two runs of the same pairing differ by 0.0147 AUC on average over all runs" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.1). The 0.0107 figure holds after the rule-breaking runs are excluded. With them included the median SD was 0.0133.

Three consequences follow from that spread:

- Three compliant runs per pairing, compared by their averages, ranked two pairings on the same model wrongly in 28 to 44 percent of all possible draws ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.2).
- A planned model upgrade was a real effect: GLM-5.3 scored 0.0091 AUC higher, 7.1 standard errors from zero. That gain is 0.87 times the SD of a single pairing, and a one-run-each comparison still favored the smaller model 28 percent of the time ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.5).
- The agent ranking reversed between two models. The authors flag this as "a pattern to test" and not a finding, because they noticed it after the data were in ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.6).

An independent study reached the same shape of result with pass/fail scoring on SWE-bench Verified. Across 60,000 trajectories, "single-run pass@1 estimates vary by 2.2 to 6.0 percentage points depending on which run is selected", with SDs above 1.5 percentage points at temperature 0 ([arXiv:2602.07150v3](https://arxiv.org/abs/2602.07150v3)).

## How to apply it

1. Run one pairing on your task repeatedly and record the SD of its score. This is the noise you compare against.
2. Decide the smallest gap that would change your decision, before you look at results.
3. Size each arm with the paper's approximation, 16 × sd² / gap², which gives 80 percent power in a two-sided test at the 5 percent level ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 3.6). Miller's error-bar paper is the statistical background ([arXiv:2411.00640](https://arxiv.org/abs/2411.00640)).
4. Reject rule-breaking runs first, then rank the rest. See the section on selecting versus ranking below.
5. Compare pairings, not agents or models alone.
6. Repeat the comparison whenever the model, agent version, endpoint, cache, or price changes.

The authors applied the approximation to their observed contrasts as an illustration. The model change needed about 21 runs per arm, and telling two agents apart on one model needed roughly 39 to 113 ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.5). They state that "the counts are not general requirements" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 3.6). Compute your own from your own SD.

The SWE-bench study gives a second scale for pass/fail scoring: about 9 runs per agent to detect a 2% improvement, and 36 runs to detect 1%, at 80 percent power, p < 0.05 and the median SD of 1.5 percentage points ([arXiv:2602.07150v3](https://arxiv.org/abs/2602.07150v3)).

## Selecting versus ranking

Choosing a good artifact needs far fewer runs than ranking configurations. In the paper's best-of-k analysis, three attempts moved the median delivered model 0.0081 AUC above one attempt, and ten attempts 0.0136. The floor rose faster than the ceiling, and the authors conclude that "Attempts mostly buy protection against a bad draw" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.4). The policy was specified after the runs were scored, so treat it as retrospective.

Selection needs a compliance gate. The seven highest scores in the study all came from rule-breaking runs, so picking the top score picks a rule-breaker ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.3). The authors advise: "Reject first, then rank." They also recommend making violations impossible rather than detectable ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 6), for example by putting evaluation labels behind a scoring interface (Section 4.3). [Gate Best-of-k Selection on Compliance Before Score](compliance-gated-best-of-k-selection.md) covers how to build that gate and where it fails. See [anti-reward-hacking](anti-reward-hacking.md) for the wider pattern.

## Confirm on later data

Most of the measured gain did not carry over. On a later year of data, a third of the agents' gain survived, and runs of one pairing still varied more than the pairings differed (0.0060 against 0.0021) ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 4.7). Gains measured on the data the agents tuned against overstate the benefit.

## Why it works

An agent run is a long autoregressive loop. Bjarnason and colleagues found that "runs diverge early, often within the first few percent of tokens", and that these differences cascade into different solution strategies ([arXiv:2602.07150v3](https://arxiv.org/abs/2602.07150v3)). Each run is therefore one draw from a wide distribution. The sample size needed to detect a gap then follows ordinary statistics: it grows with sd² over gap². When the SD exceeds the gap, three-run means put the weaker pairing ahead in 28 to 44 percent of draws on the paper's task. Best-of-k works for a different reason. Selection needs one good draw, not an estimate of the mean.

## When this backfires

- Near-deterministic tasks. At temperature 0 on single-turn tool calling, reruns were nearly deterministic, and prompt-rewording SDs were 11 to 58 times the rerun SDs ([arXiv:2608.22331v1](https://arxiv.org/abs/2608.22331v1)). Repeat runs then measure the smaller noise. See [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md).
- Large gaps. If the candidates differ by several SDs, a few runs suffice. The paper's improvement over the starting code was 2.7 run-to-run SDs, and it found a cache failure in three runs ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Table 9 and Sections 4.9 and 5.1).
- Many-task suites. Averaging a three-run check across many of your own tasks answers a different question, and per-task SDs from one continuous-metric task do not transfer to pass/fail suites.
- Gaps that do not matter. If two configurations sit within one SD, delivered quality barely differs. Choose on cost, compliance, and ergonomics rather than spend tens of runs per arm.
- Pinned or self-hosted models. The measured variance includes hosted-endpoint drift: "We measured systems as deployed, through hosted endpoints whose builds, load and routing we did not pin and could not have held constant." The authors count that variation as part of what they report ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 5.4).
- One task, one dataset. The authors write: "One task. Everything here comes from one tabular prediction task with one dataset." The phenomena may appear elsewhere, but their sizes may not ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1), Section 5.4).

## Key Takeaways

- Measure one pairing's run-to-run SD before you compare anything.
- Size each arm on the smallest gap that would change the decision, and fix that gap before you see results.
- Three attempts with a compliance gate improve the artifact you ship; ranking configurations takes many more runs.
- A real gain can lose a one-run comparison: a 7.1-standard-error model upgrade did so 28 percent of the time.
- Re-test after any change to model, agent, endpoint, cache, or price, and confirm gains on later data.

## Related

- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — report the spread once you have it.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the case where prompt wording, not reruns, dominates the noise.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — where run-to-run variance comes from.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — capability versus consistency metrics.
- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — testing whether a config change matters.
- [Gate Best-of-k Selection on Compliance Before Score](compliance-gated-best-of-k-selection.md) — the selection half: how to build the compliance gate and where it fails.
