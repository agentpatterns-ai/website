---
title: "Passing Tests Are Not Evidence a Patch Is Fast"
term: "Correctness-Only Patch Acceptance"
description: "Correct patches for the same issue differed by more than twice in runtime in one measured case, and the test gate that accepted both never asked about cost."
aliases:
  - correctness-only patch acceptance
  - patch performance blind spot
  - test-pass as patch quality verdict
tags:
  - anti-pattern
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-13
maturity: emerging
---

# Passing Tests Are Not Evidence a Patch Is Fast

> Two patches passed the same tests and ran 3.97 and 9.15 seconds in one measured case, and the tests reported neither figure.

Correctness-only patch acceptance is reading a green test run as a verdict on an agent's fix. The gate answers one question, whether the issue is repaired, and says nothing about what the repair costs to execute. One study measured that cost on 262 Python repository issues, each carrying two or more distinct correct patches, drawn from the verified splits of SWE-bench and SWE-bench-Live. It found statistically distinguishable runtime differences between those patches in 41.98% of cases on instruction count and 34.73% on wall-clock time ([Peng et al., arXiv:2610.13563v1](https://arxiv.org/abs/2610.13563v1)). The patches came from four frontier models under one agent framework, plus the developer's own fix.

## Read the runtime only under these conditions

The measurement earns its cost on a minority of fixes, and three conditions decide which.

- The gap is large enough to matter. Across all 262 cases the between-solution spread had a median of 0.21% on instruction count and 0.59% on wall time, with "a clear heavy tail" reaching 132.68% ([arXiv:2610.13563v1, §4.1](https://arxiv.org/abs/2610.13563v1)). The typical fix is indistinguishable; the tail is where the cost sits.
- The failing test is a single CPU-bound unit. The authors dropped 368 of the two benchmarks' 1,000 instances for listing more than one failing test, 206 for performing I/O, and 87 for breaking under repeated in-process execution, keeping 339 ([arXiv:2610.13563v1, §2.2.3](https://arxiv.org/abs/2610.13563v1)). Two thirds of the instances are out of reach of this instrument.
- The patch swaps a dependency or a parser. That is the class the paper's own case study lands in, where each admissible fix sends the same call through a different library ([arXiv:2610.13563v1, §4.3](https://arxiv.org/abs/2610.13563v1)).

## What the green gate hides

Which model to trust for this work. On the 339-instance measurable corpus, resolution rate ran Claude (87.32%), Qwen (83.19%), GPT (82.01%), DeepSeek (81.42%). Instruction-count speedup against the developer patch ran GPT (97.53%), DeepSeek (97.89%), Claude (98.42%), Qwen (101.68%), where smaller is faster. Those four figures come from the 90 cases all four models solved and the test distinguished. The authors put it plainly: "the runtime performance of generated patches is independent of the issue resolution rate of LLMs, with nearly reversed model rankings" ([arXiv:2610.13563v1](https://arxiv.org/abs/2610.13563v1)).

Counting cases instead of aggregating ratios keeps the same two models on top: "DeepSeek produces the fastest patches in most cases on both instruction count and wall-clock time, whereas Claude produces the fewest on both" ([arXiv:2610.13563v1, §4.2.2](https://arxiv.org/abs/2610.13563v1)). The correctness leader came last by that count, on either metric.

Whether the developer's own patch is the fast one. Three of the four models ran faster than the ground truth on their own resolved cases, and only Qwen was consistently slower, so "the developer ground-truth patches show no systematic performance advantage over model-generated patches" ([arXiv:2610.13563v1](https://arxiv.org/abs/2610.13563v1)). Reviewing an agent patch against the human fix tells you how far it diverged, not which one is cheaper to run.

## Why it works

The gate and the property measure different things, and nothing links them. A repository-level issue is marked resolved when its failing tests pass and the regression suite stays green, so the criterion is behavioral: "The evaluation criterion only requires that the issue be fixed, not the specific implementation used to achieve it. So multiple genuinely different patches may pass the same F2P tests" ([arXiv:2610.13563v1, §2.1](https://arxiv.org/abs/2610.13563v1)). Every admissible implementation satisfies the same assertions, and an assertion reads a return value rather than the work behind it. What the gate does hand you is the workload: the failing test already drives the changed code path, so nobody has to design a benchmark to exercise it. The harness around that workload is the part that costs money, and the conditions above say when to pay for it.

## Example

In `astropy__astropy-7671` the repository had deliberately dropped the heavy `pkg_resources` parser for the lighter `LooseVersion`, then had to restore a version sanitizer the same pull request had removed ([arXiv:2610.13563v1, §4.3](https://arxiv.org/abs/2610.13563v1)). Five sources produced three repair strategies. The developer patch and DeepSeek restored the sanitizer and stayed on `LooseVersion`. GPT and Qwen switched back to `pkg_resources` unconditionally. Claude kept `LooseVersion` and fell back to `pkg_resources` on error.

All three passed the same test. Measured, "the three strategies cost 48.8/103.4/64.9 billion instructions and 3.97/9.15/5.49 seconds, respectively" ([arXiv:2610.13563v1, §4.3](https://arxiv.org/abs/2610.13563v1)). Two of the three silently reintroduced the dependency the maintainers had spent a pull request removing: "The correctness tests cannot detect this architectural regression, which our performance analysis successfully reveals" ([arXiv:2610.13563v1, §4.3](https://arxiv.org/abs/2610.13563v1)).

## When this backfires

- Your fixes are cold-path one-liners. The 0.21% median gap was measured on a rig with cores reserved for the Docker daemon and the OS, cgroup cpuset partitions the host scheduler cannot touch, idled hyperthread siblings, and NUMA-bound memory ([arXiv:2610.13563v1, §3.3](https://arxiv.org/abs/2610.13563v1)). A shared runner has none of that, so budget for the rig or skip the reading.
- The code under test touches disk or network. I/O variance drowns the CPU signal, which is why this one rule alone cost the study 206 instances ([arXiv:2610.13563v1, §2.2.3](https://arxiv.org/abs/2610.13563v1)).
- The test leaves state behind. The repeatability rule dropped 87 instances across three classes, and the strictest one fails because "each test invocation mutates state that outlives it" as inserted database rows, accumulated caches, filesystem artifacts, or server threads ([arXiv:2610.13563v1, §2.2.3](https://arxiv.org/abs/2610.13563v1)). Later invocations then collide with the residue instead of redoing the work.
- You trust a spread statistic alone. The authors switched from relative standard deviation to Welch ANOVA because the former "is likely to overlook genuine runtime differences and retain cases without meaningful distinctions" ([arXiv:2610.13563v1, §4.1](https://arxiv.org/abs/2610.13563v1)). Two teams measuring the same patches with different criteria get different verdict sets.
- You are not on Python, or not on this agent scaffold. Both benchmarks "draw from Python repositories" and "all solutions come from a single SWE-agent framework" ([arXiv:2610.13563v1, §5](https://arxiv.org/abs/2610.13563v1)), so neither the divergence rate nor the speedup ordering transfers unexamined.
- A dependency-aware diff review would catch it. The case above is visible to a reviewer who knows the repository dropped `pkg_resources` on purpose, and that review costs no harness at all.

## Key Takeaways

- A passing test gate reports repair, not cost. Treat it as one of two readings, not the verdict.
- Spend the measurement on dependency and parser swaps. Skip it on cold-path edits.
- Rank models on both axes before standardizing on one. A leaderboard row carries the correctness axis only.
- The developer patch is not a performance reference. Three of the four models ran faster than it on their own resolved cases.
- Reuse the failing test as the workload before building a benchmark. It already exercises the changed path.

## Related

- [Pass-Only Grading Treats Luck and Judgment the Same](pass-only-grading-lucky-pass.md) — the same gate hiding a different dimension, the route the agent took rather than the cost of what it produced
- [Require the Metric the Optimization Should Move](../../verification/expected-metric-gate-performance-prs.md) — the mirror case, where a patch claims a performance gain and the claim carries no number
- [Model Rankings Reverse Across Agent Harnesses](../agent-design/model-rankings-reverse-across-harnesses.md) — ranking reversal driven by the scaffold instead of by the axis you measure on
- [Profiler-Guided Optimization Loops for Coding Agents](../../verification/profiler-guided-optimization-loop.md) — what to give an agent when runtime cost is the goal rather than a side effect
- [CodeSlop: Search-Trajectory Residue in Agent Patches](codeslop-trajectory-minimization.md) — the other patch property a green suite accepts without comment, removable code the tests never observe
