---
title: "Agent Bug Findings Are Not the Maintainer Backlog"
term: "Finding List as Backlog"
description: "The best of ten frontier models recovered 20.8% of the bugs maintainers actually fixed, no configuration passed 8.1% precision, and the bug-type mix diverged."
aliases:
  - finding list as bug backlog
  - agent bug report as priority order
  - bug-hunt output as maintainer backlog
tags:
  - anti-pattern
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
  - benchmarks
last_reviewed: 2026-10-29
maturity: emerging
---

# Agent Bug Findings Are Not the Maintainer Backlog

> Agents and maintainers draw bugs from different distributions, so a finding list in the agent's order is not a priority order.

## The pattern

A team runs a repository-wide bug hunt, gets back a list of findings, and works it top to bottom as if maintainers had written it. PROBE measures what that list is. Across ten frontier models auditing 20 repositories against 2,457 bugs that maintainers fixed over the following 18 months, the best configuration recovered 20.8% of those bugs, and no configuration exceeded 8.1% precision ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).

Low precision here is mostly not noise. An LLM judge panel, validating 100 findings from each of nine models and agreeing with a human grader on 93% of the 131 conclusive cases, confirmed 84% of the sampled findings that missed the reference set as real bugs. Validity was not uniform across models: "Three of the four models with the lowest precision (Claude Sonnet 5, Gemini 3.5 Flash and Muse Spark 1.3) also have significantly lower validity (64–73% vs. 89–95%)" ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).

Real, then, and still not the backlog. Extrapolating the agents' roughly 7% precision to the authors' estimate of every snapshot bug fixed within ten years, "more than two-thirds of the valid bugs agents report would thus remain unfixed for at least a decade at the maintainers' current pace" ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).

## Why it works

Agents read code; maintainers run it. PROBE categorized what each bug needs in order to surface. Maintainer-fixed bugs more often require a specific environment (10.8% against 4.7% of agent findings) or a person inspecting the output (3.8% against 0.7%), while agent findings usually need only a specific input (83.9% against 74.3%). The bug types follow that split: agents over-report wrong arithmetic or comparison expressions, 18.5% of their findings against 9.9% of maintainer fixes, and under-report a missing branch for a supported input variant, 7.7% against 18.0% ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).

The authors offer the causal reading as a hypothesis, not a result: humans more often find "a mismatch between described and implemented behavior or observable failures when running the code or using its public API", agents "logical bugs that cause subtly incorrect behavior". The agreement between runs is what makes the gap structural rather than model-specific. Across the 28 bug types with at least ten findings on each side, repeated GPT-5.6 Luna runs overlapped with each other a median of 6.3 times more than with the maintainer set ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).

## When this backfires

Reading the list as a backlog is the error. Discarding the list is a different error.

- A human filter changes the economics. Daniel Diniz's Claude Code campaign across 44 Python C extensions reported "575+ confirmed bugs (~10-15% false positive rate after review, ~140 reproduced from Python) and fixes already merged in 14 projects" ([LWN, 2026](https://lwn.net/Articles/1067234/)), with every finding reviewed and given a pure-Python reproducer where possible.
- The reference set is partial. Estimating how many snapshot bugs maintainers would fix within 5 to 10 years "caps precision at 26–47%", and the authors note that even the tightest of those ceilings is three times the best precision they measured ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).
- Scope bounds the numbers: 20 repositories, three memory-safe languages, none over 200k lines. Memory-safety bugs cannot appear at all.
- Rank by repeat count instead of the agent's order. On average only 57% to 63% of one run's findings reappear in another run of the same model, and "findings with a higher report probability are more likely to match human findings". Intersecting all ten GPT-5.6 Luna runs reached 10.5% precision and taking the union of all five Muse Spark 1.3 runs reached 26.7% recall, both above the best single run ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).
- Do not pick the model by finding count. Recall was "mostly determined by the total number of findings", at a Pearson r of 0.94, while "precision is much more consistent" across models ([Paina et al., 2026](https://arxiv.org/abs/2610.35987v1)).
- Expect the objection Maurycy Pawłowski-Wieroński raised after trying the same tool on CPython: "Unless the issue is critical (even if perfectly reproducible), many fixes are just distracting. Maintainers have their own projects, plans, schedules etc." ([LWN, 2026](https://lwn.net/Articles/1067234/)).

## Key Takeaways

- Report a bug hunt as a candidate pool with a repeat count per finding, never as an ordered queue. Repeat count is the ranking signal PROBE measured as tracking maintainer interest.
- Budget for the filter before the hunt. The best-recall configuration produced 8,285 findings across 20 repositories, and the campaign that landed merged fixes spent a human pass on every one.
- Coverage is the claim to refuse. Under 21% recall against bugs maintainers did fix means a clean report is silent about most of them, and the under-found classes are the API and input-handling gaps.

## Related

- [Agent-Laundered Bug Reports](agent-laundered-bug-reports.md) — what happens to the bug report itself when an LLM writes it up.
- [Unstated-Contract Bugs: Sort Tickets by Information Gap](../../verification/unstated-contract-bug-triage.md) — the other axis for ordering a bug queue.
- [Treating a Detector's Benchmark Score as Deployment Evidence](detector-benchmark-score-as-deployment-evidence.md) — the same gap between a benchmark number and a deployment decision.
- [Passing Tests Are Not Evidence a Patch Is Fast](passing-tests-as-performance-evidence.md) — a gate that answers a narrower question than the one being asked of it.
