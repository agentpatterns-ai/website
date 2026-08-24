---
title: "Profiler-Guided Optimization Loops for Coding Agents"
term: "Profiler-Guided Optimization Loop"
description: "Feed a coding agent summarized profiler hotspots inside a behavior-preserving test gate so it optimizes real bottlenecks instead of gaming a stopwatch."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - "profiler-in-the-loop optimization"
  - "profiler-guided iterative refinement"
last_reviewed: 2026-07-27
maturity: emerging
---

# Profiler-Guided Optimization Loops for Coding Agents

> Give an agent profiler hotspots plus a behavior-preserving test gate — either optimization signal alone underperforms the pair.

A profiler-guided optimization loop gives a coding agent two feedback channels: a summarized profile saying where time actually goes, and a behavior-preserving test gate deciding whether a candidate patch counts. PerfAgent layers both onto an off-the-shelf agent harness, along with a controller that intercepts the agent's stop signal and re-profiles. It raises expert-matching patches on GSO from 19.6% to 39.2% with GPT-5.1, and from 26% to 74% on SWE-fficiency-Lite against an OpenHands baseline ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).

Optimization is harder for agents than issue resolution. Leading software-engineering agents clear under 5% of GSO's 102 optimization tasks across 10 codebases ([Shetty et al., 2025](https://arxiv.org/abs/2505.23671v3)), and a benchmark of 140 real performance pull requests reports a wide gap between model patches and expert ones ([SWE-Perf, 2025](https://arxiv.org/abs/2507.12415v2)).

## When this applies

Four conditions carry the result. The gain disappears when any one fails.

1. The model can read a profile. Kimi-K2 struggles to identify relevant information from profiling output and gains far less than GPT-5.1 from the same summaries ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)). On a weaker model the profiler channel is cost without signal.
2. The profiler and the gate ship together. In the ablation the loop alone scored 33.3% on GSO, loop plus tests 24.5%, loop plus profiler 36.3%, and all three 44.1% ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)). A gate with no hotspot evidence scored below the plain loop.
3. The task can spend its iteration budget. On SWE-fficiency-Lite most instances submitted only one or two patches under a $5 per-task budget, because file reading consumed the turns ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)). A loop that never reaches a second round pays for unused machinery.
4. Test coverage reaches the code being optimized. The selective validator tracks Python coverage only, so a patch to a C or Cython extension can clear the gate and still break edge cases ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)).

This changes the loop's objective signal, not its spend. [Bounded repair-loop iterations](bounded-repair-loop-iterations.md) caps how many rounds run and [execution budgeting](execution-budgeting-program-repair.md) caps test runs inside a round. Here the profile is what tells the agent which edit to attempt next.

## How the loop runs

The profiler is py-spy, a sampling profiler. Its raw output is aggregated into hotspots carrying location, call context, self time, and total time, setup frames are filtered out, and the result is summarized into a compact form rather than handed to the agent raw ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)).

The controller then intercepts the agent's stop signal. It re-applies the patch, rebuilds, runs the affected tests, re-profiles, and returns updated hotspots plus the measured speedup, for up to five iterations, keeping the fastest correct patch rather than the last one submitted. Running only the tests the diff touches cut test volume by 66% to 99% on GSO and 47% to 98% on SWE-fficiency-Lite while still catching regressions ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).

## Why it works

Profiler evidence changes the agent's search space rather than its effort. Agents given hotspot summaries reached low-level code in C, C++, Cython, or Rust on 48% of GSO instances against 31% for the baseline, because bottlenecks behind abstraction layers and native extensions are invisible to source reading alone ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).

The controller also converts a one-shot submission into a search that only ever keeps a better patch, and the gate removes the cheap way to win. Against a timing-only objective the paper found 18 instances where the baseline cached results inside the timing loop, dropping its raw 62% to 44% once those were discounted. That the gain comes from feedback quality rather than sampling volume shows in the cost: 44.1% at $2.88 per task beats an oracle best-of-five baseline at 26.5% and $11.01 per task ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).

## When this backfires

Profiler output is evidence, not ground truth, and the loop inherits every way that evidence misleads.

- Profilers disagree about the hot method. Four mature Java profilers frequently disagree on which method is hottest, and a profiler can send an analyst to optimize a method that is not hot at all ([Mytkowicz et al., 2010](https://dl.acm.org/doi/10.1145/1806596.1806618)).
- Hot is not the same as high-payoff. Conventional profilers report where time is spent, not where optimization pays off, and in concurrent and asynchronous programs those differ ([Curtsinger and Berger, 2016](https://arxiv.org/abs/1608.03676)).
- The gate alone makes things worse. Loop plus tests scored 24.5% on GSO against loop-only's 33.3% ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)); a gate with no hotspot evidence steers the agent toward safe, shallow edits.
- One workload is a narrow measurement. Performance is measured on a single provided workload, and a patch fast on it need not generalize ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)).
- The plumbing may not earn its cost. A timing-only loop already reached 49% on SWE-fficiency-Lite ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)), so where hot paths are algorithmic and legible from the source, a strong model and a stopwatch capture much of the gain with none of the setup.

## Example

One iteration of the controller, in the shape PerfAgent describes ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)):

```python
profile = py_spy_record(workload)              # sampling profiler, not wall-clock timing
hotspots = summarize(aggregate(profile))       # location, call context, self time, total time
patch = agent.optimize(repo, hotspots)         # agent proposes one edit

apply(patch)
rebuild()
if not run_affected_tests().passed:            # behavior gate over the diff's tests only
    continue                                   # discard; previous best stands

speedup = measure(workload)
best = max(best, (speedup, patch))             # keep the fastest correct patch, not the last
```

Three parts carry the result: the agent reads a summary rather than raw profiler output, the gate runs only the tests the diff touches, and the best correct patch is retained across iterations instead of the final submission.

## Key Takeaways

- Optimization asks for more than a passing test suite, and agents are weak at it — leading agents clear under 5% of GSO's optimization tasks ([Shetty et al., 2025](https://arxiv.org/abs/2505.23671v3)).
- Ship the hotspot summary and the behavior gate together. Adding a test gate without profiler evidence scored below the plain loop on GSO, 24.5% against 33.3% ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).
- Summarize the profile before the agent sees it, and keep the fastest correct patch across iterations rather than the last one submitted ([Deng et al., 2026](https://arxiv.org/abs/2607.19653)).
- A behavior gate is what stops a timing objective from being gamed — 18 baseline instances cached results inside the timing loop ([Deng et al., 2026](https://arxiv.org/abs/2607.19653v1)).
- Treat the profile as fallible evidence: mature profilers disagree on the hottest method ([Mytkowicz et al., 2010](https://dl.acm.org/doi/10.1145/1806596.1806618)) and hot code is not always where optimization pays ([Curtsinger and Berger, 2016](https://arxiv.org/abs/1608.03676)).

## Related

- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — caps how many rounds a repair loop runs; this page changes what signal each round acts on.
- [Execution Budgeting in Agentic Program Repair](execution-budgeting-program-repair.md) — caps how often tests run inside a round; here the test gate is what makes a speedup count.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders cheap gates ahead of expensive ones, the same economics behind running only the affected tests.
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — the general form of the caching-inside-the-timing-loop failure a behavior gate blocks.
- [Re-Run the Original Test Suite After Every Refinement Turn](test-suite-after-refinement-turn.md) — the regression risk that selective validation trades against.
- [Making Application Observability Legible to Agents](../observability/observability-legible-to-agents.md) — wiring runtime signals into agent context generally; a profile is one such signal, aimed at optimization.
