---
title: "Re-Run an Agent's Speed-Up Claim Before Merging"
term: "Speed-Up Re-Run"
description: "Acceptance of an agent's performance fix tracks the repository's history with that agent, not the evidence attached, so re-run the claim yourself to learn whether it delivers."
tags:
  - workflows
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - performance claim re-execution
  - re-executing an agent benchmark
  - speed-up delivery check
last_reviewed: 2026-09-30
maturity: emerging
status: current
---

# Re-Run an Agent's Speed-Up Claim Before Merging

> Re-executing 30 merged agent fixes found nine with no significant gain, or a regression, at the primary workload.

A speed-up re-run is a bounded re-execution of the improvement an agent's pull request claims, timed on the base tree and the head tree in one container at more than one workload size, with a behavior diff over the changed lines. The merge button answers a different question from the one the claim raises, and the two get read as one answer.

## Why the merge tells you nothing about the speed-up

Acceptance tracks the repository's history with the agent and the shape of the patch. Qi and colleagues coded 1,262 agent performance fixes across 582 repositories from AIDev v4, 1,105 of them closed. Acceptance runs at 33% where the repository had merged at most 40% of its decided agent pull requests when the fix opened, 57% in the middle band, and 84% where it had merged over 90% (n = 165, 521, and 255). Moving that pre-opening merge rate from 0 to 1 multiplies the odds of acceptance by 13.7 (95% CI 6.3 to 30.0) ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

Delivery is a property of the code. A rejection thread rarely shows whether anyone checked the claimed improvement. Only 3% of the 480 rejection threads ask for a measurement, and 61% state no reason at all. Of 30 merged fixes the authors re-executed, 18 met their delivery criterion at the primary workload, 3 improved but fell short of the claim, and 9 showed no significant gain or regressed ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

Attaching a benchmark does not buy you a merge, which inverts the usual advice. Acceptance sits at 51% for fixes carrying a performance test, 54% with functional tests only, 60% with adaptation only, and 58% with no test at all (p = 0.53) ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). Run the measurement because it tells you something, not because the reviewer will weigh it.

## Three verification layers

Each layer is cheaper than the next and disqualifies a different class of claim. Run them in order; stop at the first failure.

### Layer 1: Base-tree replay

Check out the base commit, apply only the pull request's test files, and run them. In 17 of the 28 merged fixes where the tests ran on the base tree, they passed there unchanged, and only 2 of the 30 failed on the base for a performance reason ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). A test that passes with and without the fix is not evidence about this fix.

Read the bound as well. In web-infra-dev/rsbuild PR 6060, Copilot added a test requiring `getCommonParentPath` to handle 100 paths within 100 ms. The base costs about 41 microseconds per call, so "the bound sits more than 2,000 times above the cost it is meant to guard" ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

### Layer 2: Sized re-execution

Time base and head in the same container at three workload sizes: the size the pull request's own test uses, a size one to two orders of magnitude larger, and the size of the pull request's claim. Across the three sizes the authors ran, 8 of the 30 fixes were slower than the base at one of them, and 5 of the 18 that delivered gained only at the larger sizes. In jdereg/java-util PR 127, a binary search over a compact map's keys ran 9% slower than the linear scan at the four keys the pull request itself used, and 4.8 times faster on 600 ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

Budget for it. The authors timed each merged fix as 12 interleaved forks per version at each of the three sizes, which the paper calls a more intensive protocol than its single-workload pilot ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

### Layer 3: Behavior diff

A reproduced speed-up is not a correct fix. Generated tests over the changed lines found the head behaving differently from the base in 24 of the 30 merged fixes. In 14 the fix introduced a functional change its description never mentions, and in 10 of those the head failed or returned a different result on inputs inside the changed function's intended use ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). None of those inputs appeared in the pull request's own tests.

## Triggers and constraints

Tie the three layers to the pull request event. What bounds the agent doing the timing:

| Driver | When it fires | Bound on the runner |
|---|---|---|
| Pull request opened or synchronized | Layers 1 and 2, in CI | Fixed container image, no network, wall-clock cap per fix |
| Reviewer request | Layer 3, on demand | Read-only on the repository; writes a report, never the fix |
| Merge gate | Layer 1 result only | Blocks when the added test passes on base |

Gate a merge on Layer 1 only. Layer 2 reports rather than blocks, because shared hardware moves the number: Laaber et al. (2019) found a 10% slowdown detectable only when test and control ran on the same instance in randomized order, as reported in [Qi et al. (2026)](https://arxiv.org/abs/2609.37985v1) section 2.1.

The artifact worth keeping is a performance test that fails on base and passes on head. Any performance test is uncommon: only 11% of the 1,259 fixes carry one, and of the 140 that do, 66 use a sized workload against 49 a toy one. Among the 28 merged fixes whose tests ran on the base tree, 17 passed there unchanged ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).

## Multi-tool coverage

Tool-agnostic. The layers act on a pull request and two trees, so nothing differs between Claude Code, Copilot, and Cursor. Who holds the merge button does differ. Where the operator opens the pull request through their own account and merges it, 209 of the 306 self-merged operator fixes were merged within an hour and 97% of those fast merges carry no human text ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). Under that account model the re-run lives in CI or nowhere.

## Why it works

Acceptance tracks the repository's history with the agent, and the coded content of the fix does not separate merged from rejected fixes. A passing functional test says nothing about speed, and a measurement worth reading needs repetition and control that a pull request thread rarely shows. Georges et al. (2007) found that reporting the best or the mean of a few runs of a Java benchmark can reverse a comparison, and Mytkowicz et al. (2009) found that link order and the size of the process environment alone shift run time enough to reverse the sign of a claimed speed-up, both as reported in [Qi et al. (2026)](https://arxiv.org/abs/2609.37985v1) section 2.1.

The study finds the same pattern in its acceptance model. Adding the block that holds author association and the repository's history with agent pull requests lifts the pseudo R-squared from 0.145 to 0.232. The authors summarize the other terms this way: "The repository's history with agent PRs and the deleted-line share of the fix distinguish merged from rejected fixes, while the coded content of the fix, its description, its tests and its attached measurements do not" ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). These are associations in observational data, and the authors say so; whether changing a fix's shape would change its outcome is untested.

## When this backfires

- One- to five-line micro-optimizations. Eight of the 10 fully covered fixes failed the delivery criterion against 4 of the 20 partly covered ones (p = 0.004), because the fully covered fixes are mostly micro-optimizations whose gain disappears under the JIT or inside untouched work. The authors note that diff size confounds that comparison ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- Repositories that have not yet merged an agent pull request. The study records an agent's account as NONE until the repository merges one of its pull requests, and NONE fixes are rejected 94% of the time ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- One benchmark read as a verdict. The discipline that catches a bad claim produces a bad one when it runs at one size on one shared machine.

The case for skipping the re-run is real. Eighteen of the 30 re-executed merged fixes did deliver, and the median base-to-head cost ratio across all 30 was 1.8 ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). A prior built from twenty merged pull requests is cheap, and it does track something: acceptance runs at 37% where the repository had never seen the agent and 70% after 20 or more merged pull requests from it ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)). A maintainer who waves through a small deleting patch from an agent with a long record in the repository is making a defensible trade.

Measurement does change what the agent produces, even though it does not change what the maintainer decides. On PerfBench's 81 .NET performance tasks, a baseline OpenHands agent reached "only a ~3% success rate"; the same harness with performance-aware tooling and instructions reached "a ~20% success rate" ([Garg et al., 2025](https://arxiv.org/abs/2509.24091v3)). Give the agent the benchmark before it writes the patch, then re-run the claim after.

## Key Takeaways

- Acceptance and delivery are separate questions. The repository's pre-opening merge rate on other agent pull requests moves the odds of acceptance by a factor of 13.7 from 0 to 1, while the fix's tests and attached measurements do not separate the outcomes ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- Layer 1 pays for itself. In 17 of 28 fixes the pull request's tests passed on the base tree, so they could not have told a delivered fix from a missing one ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- One size certifies nothing. Over the authors' three sizes, 8 of the 30 fixes were slower than the base at one of them ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- Diff the behavior too. Fourteen of the 30 merged fixes changed behavior their description never mentions ([Qi et al., 2026](https://arxiv.org/abs/2609.37985v1)).
- The weakness generalizes past performance work. A differential analysis of 1,210 merged agent bug-fix pull requests concludes that "merge success does not reliably reflect post-merge code quality" ([Beyond Bug Fixes, 2026](https://arxiv.org/abs/2601.20109v1)).

## Related

- [Effective Feedback Compute (EFC) for Harness Comparison](../patterns/agent-design/effective-feedback-compute.md) — the single-agent building block: which feedback an agent actually acts on
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](../verification/evidence-bundled-agent-prs.md) — what to attach so a reviewer can pick a depth per change
- [Post-Merge Fix Signals for Agent Merges](../verification/post-merge-fix-signals-agent-merges.md) — the follow-up-fix rate after an agent merge, and what predicts it
- [Profiler-Guided Optimization Loops for Coding Agents](../verification/profiler-guided-optimization-loop.md) — give the agent a profile and a behavior gate before it writes the patch
- [Measuring the Verification Tax on Agent Output](verification-tax.md) — what checking agent work costs relative to producing it
- [Require the Metric the Optimization Should Move](../verification/expected-metric-gate-performance-prs.md) — what the PR has to report before you re-run anything
