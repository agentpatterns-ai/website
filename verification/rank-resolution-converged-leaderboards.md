---
title: "Rank Resolution: Reading a Converged Coding-Agent Leaderboard"
term: "Rank Resolution"
description: "In the SWE-bench Verified top thirty, exact paired tests separate none of the 29 adjacent pairs, because only 164 of 500 instances distinguish the top ten."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - leaderboard rank resolution
  - discordant-instance audit
  - converged benchmark frontier
last_reviewed: 2026-09-16
maturity: emerging
---

# Rank Resolution: Reading a Converged Coding-Agent Leaderboard

> A leaderboard gap orders two systems only while enough instances separate them. At the top of SWE-bench Verified, no adjacent pair separates.

Rank resolution is the count of instances on which two systems actually disagree. An audit of 254 SWE-bench submissions across four splits found that the top ten Verified entries share 285 successes and 51 failures, leaving 164 of 500 instances that distinguish any of their outcomes, and exact paired McNemar tests separated none of the 29 adjacent top-thirty pairs at alpha 0.05 ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). Read those rows as a tier, not as an order.

## The conditions this holds under

This is a claim about a converged frontier, not about benchmarks. Four conditions bound it, and the first one carries the argument.

- The comparison sits at the frontier. On the larger Test split the same paired tests separated 14 of 23 adjacent pairs, and the authors are explicit that SWE-bench "detects many differences across a broader capability range" ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). A 20-point gap needs no audit.
- The benchmark publishes per-instance verdicts. Every step below needs the pass or fail on each instance. SWE-bench publishes them, which is the only reason this audit ran without executing a single model.
- You know which configuration each row evaluated. Within-model scaffold ranges reach 29.8 percentage points, against the 8.8-point spread of the entire top thirty ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). The leaderboard's submission process requires no detailed documentation of the system behind an entry ([Martinez and Franch, 2026](https://arxiv.org/abs/2506.17208v3)), so two adjacent rows may differ by harness rather than by model.
- You are asking whether A beats B, not whether A and B are the same. Non-rejection does not establish equivalence ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).

## What the audit measured

| Quantity | SWE-bench Verified |
|---|---|
| Instances in the split | 500 |
| Resolved by each of the leading two entries | 396 |
| Solved by all of the top ten | 285 |
| Solved by none of the top ten | 51 |
| Instances that distinguish any top-ten outcome | 164 |
| Median nesting of frontier solution sets | 0.935 |
| Score-implied nesting baseline | 0.774 |
| Adjacent top-thirty pairs separated at alpha 0.05 | 0 of 29 |
| Adjacent Test-split pairs separated | 14 of 23 |

A leader-based partition rule turns that top thirty into three descriptive tiers, or two after Holm correction ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).

Two other audits arrive at the same place from different directions. A separate study of SWE-bench's top ten reports that of its 45 pairwise comparisons, "5 are stable under the 2-point practical-margin rule, 1 is target-sensitive, and 39 are underpowered" ([Huang, 2026](https://arxiv.org/abs/2609.07785v1)). The pattern is not specific to coding: a reanalysis of nine models on MMLU lost 3 of its 8 adjacent rank gaps to multiple-comparison correction ([Chandrahas, 2026](https://arxiv.org/abs/2607.04429v1)), which [purpose-built eval suites](purpose-built-eval-suites.md) covers for suites you build yourself.

## The five-step audit

The audit releases its partition and a five-step protocol to go with it ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). Run it over published per-instance verdicts before you quote a rank.

1. Profile. Compute effective size across nested comparison sets to find where resolution collapses.
2. Explain. Compute the nesting coefficient against the score-implied baseline, which says how much of the agreement is structural rather than incidental.
3. Test. Run exact paired McNemar tests on each adjacent pair and report raw alongside Holm-adjusted p-values.
4. Partition. Walk the sorted ranking, compare each entry against its tier leader, and start a new tier when the comparison rejects at p below 0.05.
5. Budget. Invert the paired condition to price the instances that would resolve the comparison you care about.

The budget step is the one that changes plans. For the ten leading adjacent pairs on Verified, excluding two zero-gap pairs, the upper median multiplier is 52 times, or roughly 26,000 instances of the same character. Instances that disagree and also lean one way change the arithmetic: for the reference pair with 54 of 500 discordant instances, an imbalance rate of 0.2 needs about 900 instances rather than 26,000 ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). That ratio, not a task count, is the acceptance test for a candidate instance.

Retiring the instances everyone solves is the tempting alternative, and it buys nothing. Rescoring the top thirty on the 209 instances non-degenerate for the top twenty widens the visible spread from 8.8 to 18.7 percentage points and reorders three adjacent pairs, yet separable pairs stay at 0 of 29, because a paired test already discards instances both systems agree on ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).

## What to report instead of a rank

Publish comparison-set-specific resolution and model-scaffold provenance rather than treat a small aggregate gap as an established rank difference ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). Four things belong beside each score: per-subset resolution, the model-and-harness pair in machine-readable form, the effective sample size, and descriptive tiers in place of a strict ordering. The independent audit asks for the same disclosure, adding the uncertainty unit and the practical margin ([Huang, 2026](https://arxiv.org/abs/2609.07785v1)).

## Why it works

A paired test on binary per-instance verdicts draws all of its information from discordant instances: the ones where exactly one of the two systems succeeds. Convergence makes those scarce by construction. Frontier solution sets nest at a median 0.935 against a score-implied baseline of 0.774, so the better system solves close to a superset of what the worse one solves, and the leftover disagreement is both small and nearly one-directional ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). With 164 discriminating instances shared across ten entries, an adjacent pair has almost no sample to argue from. That is why zero of 29 Verified pairs separate while 14 of 23 do on the less converged Test split.

The underlying problem is minimum detectable effect, and it predates coding agents by a benchmark generation. Card et al. found that "typical test sets of 2000 sentences have approximately 75% power to detect differences of 1 BLEU point" in machine translation, and that several GLUE tasks have test sets small enough to leave most attempted comparisons against state of the art underpowered ([Card et al., 2020](https://arxiv.org/abs/2010.06595v1)). Saturation walks a benchmark into that regime from the top down.

## When this backfires

- The benchmark reports only aggregate scores. Nesting, discordance counts, and paired tests all need per-instance verdicts, and without them resolution is unknown rather than absent.
- The systems are far apart. Fourteen of 23 adjacent Test-split pairs separate cleanly, so running the audit on a gap that size answers a settled question.
- You read a null as parity. A non-significant McNemar result bounds nothing. If the claim you need is that two configurations behave the same, run [equivalence testing against a prespecified margin](equivalence-testing-agent-config-changes.md) instead.
- You treat the harness finding as causal. Six of nine cell-mean interaction tests survive Holm correction, but the factorial design is observational, it confounds team effort with co-optimization, and 54% of submissions cannot be placed in it at all ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).
- Every entry ran once. Between-system differences cannot be separated from run-to-run variance, and the audit's intervals resample instances while omitting execution variability ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).
- Contamination may be doing part of the work. Verified overlaps pretraining data: given only the issue text, models identify the buggy file at 76% accuracy on Verified against 53% on unseen repositories, and the audit's own age-based test detects no effect while treating age as a proxy only ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)). Treat [benchmark contamination](benchmark-contamination-eval-risk.md) as a separate question this audit does not settle.
- You generalize the protocol. It was validated on the SWE-bench family only ([Liu et al., 2026](https://arxiv.org/abs/2609.17394v1)).

## Key Takeaways

- Count discordant instances before quoting a gap. The count, not the score difference, is what a paired test has to work with.
- Convergence is a property of the frontier, not of the benchmark. The same tests separate 14 of 23 adjacent pairs on the larger Test split.
- Record the model-and-harness pair for any row you compare. Within-model harness ranges of 29.8 points dwarf the 8.8-point spread of the top thirty.
- Price the fix before asking for a bigger benchmark. Retiring easy instances widens the spread and resolves nothing.
- A failed separation test is not an equivalence claim, and shortlisting three candidates from thirty remains a defensible use of a converged leaderboard.

## Related

- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — the same power problem on a suite you build yourself, and how to size one to the decision.
- [Equivalence Testing for Agent Configuration Changes](equivalence-testing-agent-config-changes.md) — what to run when the claim you need is parity rather than superiority.
- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the variance floor a gap has to clear, measured across reruns and rewordings.
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — why shared successes at the frontier may track training-data overlap.
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — reporting capability and consistency as two numbers instead of one rank.
