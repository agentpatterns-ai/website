---
title: "Require the Metric the Optimization Should Move"
term: "Expected-Metric Gate"
description: "Half of performance PRs reporting validation carry no extractable number, and only 34.5% report a metric the applied optimization is expected to improve, so name the metric and its traded resource before accepting."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - expected-metric gate
  - performance claim metric correspondence
  - trade-off metric requirement
last_reviewed: 2026-10-06
maturity: emerging
status: current
---

# Require the Metric the Optimization Should Move

> Half of performance PRs that claim validation report no metric at all, so require the one the optimization is supposed to move.

An expected-metric gate names two numbers a performance change must report before anyone accepts it: the metric the applied optimization is expected to improve, and the resource that optimization usually spends to get it. Asking instead whether the author validated the change sorts almost nothing, because nearly everyone says yes.

Apply the gate where the change trades one resource for another and the effect cannot be read off the diff. Caching, buffering, request batching, lazy loading, and data-structure swaps all qualify. A dead-code deletion does not.

## What validation presence hides

Validation evidence appears at the same rate whatever wrote the change. In a 1:1 balanced sample of performance pull requests, week-stratified over December 2024 to June 2026 in repositories with at least 100 GitHub stars, "Validation evidence is reported in 929 of 1,129 agentic PRs (82.3%) and 910 of 1,129 human-authored PRs (80.6%)", with no significant association to author type at p=0.330 ([Peng et al., arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).

The form of that evidence decides whether a number exists at all. Among the 1,684 PRs with a resolved evidence type, "the pipeline identifies at least one metric in 79.8% of benchmark-based PRs, 30.8% of profiling-based PRs, 21.6% of static-reasoning-based PRs, and 18.2% of anecdotal ones" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)). Agents lean on the form that carries no number. Among the 1,819 PRs with reported validation evidence and a resolved evidence type (918 agentic and 901 human-authored), static reasoning is the primary evidence in 51.4% of agentic PRs against 39.3% of human-authored ones.

That author-type difference is closing, so do not build the gate on it. Benchmark use among agentic PRs rises at an odds ratio of 3.63 per year (p=0.012) against 0.98 for humans (p=0.950). Among PRs with a resolved evidence type, the benchmark share by 2026-Q2 is 60.1% agentic and 58.7% human ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)). What is left to gate on is what the evidence measures, and both groups show that gap.

## The two numbers to name

First, the metric the optimization is expected to improve. The study maps each of 59 catalog optimization patterns to the performance dimensions it should move, then checks whether the PR reports one of them. Among 1,699 PRs with validation evidence, 34.5% report at least one expected metric against a 23.7% permutation baseline (p=0.002). Better than chance, and still two PRs in three reporting nothing from that expected set. Reporting is thin before correspondence even comes up: "half of the PRs with reported validation contain no extractable quantitative performance metric, and a majority of those that report a metric report only one" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).

Second, the resource the change spends. The authors restricted this test to caching and buffering, where the exchange of memory for time is well established. Of the 96 such PRs with benchmark or profiling evidence that report a runtime-side gain, "fewer than one in five caching or buffering PRs that report a runtime-side improvement also report an adverse memory effect" — 17.7%, split 18.2% agentic and 17.1% human ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).

Agentic PRs show no significant difference by change type. Human authors report both validation and a metric for 25.2% of code-smell refactorings against 45.8% of other performance changes. The agentic figures are 37.8% and 42.3%, and none of the three agentic contrasts reaches significance, at q≥0.33 ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)). An agent applies one reporting habit to a dead-code deletion and to a cache, so the gate has to supply the discrimination the author did not.

## Why it works

Performance is not a property you can read from a diff. The paper states the premise its recommendation rests on: "a functionally correct change may yield no improvement, regress on other workloads, or appear beneficial because of measurement noise or experimental conditions" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).

Naming the expected metric and the traded resource replaces a question whose answer carries no information with one that has a checkable answer. The authors reach the same conclusion: "The assurance target should therefore be the appropriateness and completeness of evidence, not merely the presence of validation or a benchmark", because "even benchmark-based evidence can verify an intended gain while leaving relevant costs unobserved" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).

## When this backfires

- The direction is visible in the diff. Code smells and structural simplification is the category with the lowest metric reporting in the study, and human authors already hold it to a lower bar. Requiring a benchmark to delete unreachable code spends CI minutes and returns nothing.
- The benchmark runs in isolation, or on a shared runner. A JMH-compliant microbenchmark can still mislead: a badly designed one "may cause the JVM to collect an unrealistic profile, resulting in aggressive, yet misleading, optimizations, that would not occur in a real application" ([Schiavio et al., arXiv:2605.23570v1](https://arxiv.org/abs/2605.23570v1)). A gate that accepts any number accepts that one.
- The PR volume is agentic scale. A per-PR benchmark requirement is the thing that does not scale: "Existing CI-based benchmarking, designed for human workflows, is unlikely to scale to agent-driven workloads" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).
- Nobody re-runs the number. The gate reads a PR description, and the authors warn that agents "may also learn to reproduce the form of human validation reports, including plausible benchmark claims, without a corresponding improvement in measurement practice or evidential reliability" ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)). A gate on the reported figure is a shallower fix than re-timing base against head yourself, so pair it with a [speed-up re-run](../workflows/rerun-agent-speedup-claims.md) wherever the change matters enough.

The case against the gate runs on incentives. Test kind does not move acceptance: across the 1,105 closed agent performance fixes in a separate study, "acceptance is 51% with a performance test, 54% with functional tests only, 60% with adaptation only and 58% with no test (p = 0.53)" ([Qi et al., arXiv:2609.37985v1](https://arxiv.org/abs/2609.37985v1)). An attached measurement is slightly more common among rejected fixes (20% versus 15%, p = 0.024), and "the measurement's coefficient is not significant once the agent is held fixed (M4)". Acceptance does not track the test kind, so a reviewer who starts requiring a metric imposes a real cost on authors and collects no faster merge for it. The gate buys information. The study is observational and "identifies associations rather than causal effects of agentic authorship".

## Example

This example is illustrative, not drawn from the studies.

A caching PR description that fails the gate: "Added an LRU cache to the lookup path. Tested locally and it feels faster."

A caching PR description that passes: "Added an LRU cache to the lookup path. Expected metric: p95 lookup latency, measured on base and head with the same benchmark. Traded resource: peak resident memory, measured on the same runs. Cache size is capped at 10,000 entries."

The first names no metric and no cost. The second names both, so a reviewer can check them.

## Key Takeaways

- Stop asking whether a performance change was validated. The answer is yes at 82.3% for agentic PRs and 80.6% for human-authored ones, p=0.330 ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).
- Ask instead for the metric the optimization should move, because two thirds of validated PRs report none: 34.5% correspondence against a 23.7% baseline ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).
- Ask for the resource it spends too. Among 96 caching and buffering PRs claiming a runtime gain, 17.7% also report an adverse memory effect ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).
- Justify the gate on evidence, not on authorship. Agentic benchmark use overtook the human rate by 2026-Q2, at 60.1% against 58.7% among PRs with a resolved evidence type ([arXiv:2610.03969v1](https://arxiv.org/abs/2610.03969v1)).
- Expect no faster merges from it. Acceptance was statistically flat across test kinds over 1,105 closed agent performance fixes, p = 0.53 ([Qi et al., arXiv:2609.37985v1](https://arxiv.org/abs/2609.37985v1)).

## Related

- [Re-Run an Agent's Speed-Up Claim Before Merging](../workflows/rerun-agent-speedup-claims.md) — the complement: this page sets what the PR must report, that one re-executes the claim on base and head
- [Profiler-Guided Optimization Loops for Coding Agents](profiler-guided-optimization-loop.md) — give the agent the profile before it writes the patch, so the expected metric is the one it targets
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](evidence-bundled-agent-prs.md) — what else to attach so a reviewer can pick a depth per change
- [Name the Check That Passed Before Accepting AI Code](named-check-over-evaluation-confidence.md) — the same move applied to correctness, where a named check replaces a confidence statement
- [Reject on a Failing Check, Never Accept on a Passing One](asymmetric-check-evidence.md) — how much a passing check is worth once you have one
