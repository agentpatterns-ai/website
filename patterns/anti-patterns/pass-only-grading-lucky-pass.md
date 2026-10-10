---
title: "Pass-Only Grading Treats Luck and Judgment the Same"
term: "Lucky Pass"
description: "10.7% of 1,136 passing OpenHands trajectories on SWE-bench Verified reached a correct patch through a weak process; process ranking reordered all eight backends."
aliases:
  - lucky pass
  - process-aware trajectory scoring
  - outcome-only trajectory evaluation
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-07
maturity: emerging
---

# Pass-Only Grading Treats Luck and Judgment the Same

> Pass-only grading gave 1,136 agent runs one label, and a process score separated 122 of them as weak successes.

A Lucky Pass is a run that produces a correct patch through a weak process. One study scored 1,136 passing OpenHands trajectories on SWE-bench Verified, each against a reference merged from other passing runs of the same task. The fixed thresholds yield "229 Ideal trajectories (20.2%), 785 Solid trajectories (69.1%), and 122 Lucky trajectories (10.7%)" ([Sahoo et al., 2026, §5.1](https://arxiv.org/abs/2605.12925v4)). A pass-only gate hands all 1,136 the same label, so the split sits outside what it can report.

## Read the process only under these conditions

- The task has two or more passing runs on record. The reference merges several known-good solutions, a requirement "satisfied by 47 of the 60 tasks" here ([Sahoo et al., §4](https://arxiv.org/abs/2605.12925v4)).
- The score stays a second reading rather than the gate. The authors draw that line: "process scores should be treated as complementary diagnostics rather than replacements for functional correctness, security review, or human judgment" ([Sahoo et al., §A.3](https://arxiv.org/abs/2605.12925v4)).
- The log is detailed enough to rebuild each step as a state carrying "the tool, target file, affected line range, content hash, trajectory position, and an intent-stage label" ([Sahoo et al., §3.1](https://arxiv.org/abs/2605.12925v4)). Coarser logs cannot be scored.

## What the pass rate hides

- Which model to pick. Ranking eight backends by process quality rather than pass rate disagreed on every one, "with some models moving by as many as five rank positions" ([Sahoo et al., §1](https://arxiv.org/abs/2605.12925v4)). Opus 4.6's "77.3% pass rate hides an 18.7% Lucky rate", against a 0.5% to 23.2% spread across models ([Sahoo et al., §5.2](https://arxiv.org/abs/2605.12925v4)). One direction of that reshuffle carries the authors' own caution: GPT-4o's rise "may partly reflect which tasks it solves rather than a model-wide advantage".
- What a pass costs. Mean token spend across the weak classes runs 34,032 to 1,377,226, "with one trajectory consuming 2.62M tokens for a one-line fix" ([Sahoo et al., Appendix F](https://arxiv.org/abs/2605.12925v4)). Forty-fold apart, identical binary credit. Those means compare weak classes against each other, not against all passing runs.
- Which runs to keep as demonstrations. Trajectory datasets "commonly filter on pass rate, treating every successful trajectory as equally valuable supervision" ([Sahoo et al., §1](https://arxiv.org/abs/2605.12925v4)).

## The five classes, and where each fix sits

| Class | n | Share | Behavior | Where the fix sits |
|---|---|---|---|---|
| Minimal and unverified | 19 | 15.6% | Short fix, verification skipped | Agent: run tests after an edit |
| Brute-force convergence | 42 | 34.4% | Retries until one attempt holds | Agent: planning and termination |
| Incomplete implementation | 41 | 33.6% | Partial fix the suite misses | The test suite |
| Excessive exploration | 5 | 4.1% | Long, unfocused search | Agent: termination |
| Divergent but valid | 15 | 12.3% | A different correct route | Nothing; a scorer false positive |

Counts and shares come from Table 1. Brute-force convergence is the paper's C2 and incomplete implementation its C3, and "C2 and C3 account for 68.0% of Lucky Passes" ([Sahoo et al., §5.2](https://arxiv.org/abs/2605.12925v4)).

Incomplete implementation is the awkward class. Its cause is not the agent: "It passes because the test suite does not cover the missing aspects of the full solution" ([Sahoo et al., §D.2](https://arxiv.org/abs/2605.12925v4)). A process score reports that third of the problem and repairs none of it.

## Why it works

A pass/fail label is a function of the final patch alone, so two runs differing only in route receive the same label by construction. Whether a test ran, how many retries happened, and how many tokens burned are all outside its domain. Merging several passing runs into one reference restores that variance while still accepting branches those runs took, because "divergent but successful strategies form branches" and each root-to-terminal path is one known-good solution ([Sahoo et al., §3.2](https://arxiv.org/abs/2605.12925v4)).

A second group measured the same drift while training against a unit-test reward: "the uncorrected verifier pass rate can increase even when a growing fraction of successful trajectories rely on monitored shortcut behaviors". Averaged over three SWE-bench variants, adding a trajectory-level monitor took their hacked-resolved rate "from 28.57% to 0.56%" and clean resolutions, a metric that "treats hacked solutions as incorrect", "from 40.22% to 60.53%" ([Wang et al., 2026, §2.3](https://arxiv.org/abs/2606.26300v2)). Their monitor audits for leakage patterns such as retrieving the original pull request, so it corroborates that the route carries signal without measuring process quality.

## When this backfires

- Incomplete implementation dominates your corpus. The score names the gap and a stronger test suite closes it, so the process tooling is a detour.
- The reference set is small. At low merge counts a compact reference "may penalize valid strategies absent from the reference" ([Sahoo et al., §6](https://arxiv.org/abs/2605.12925v4)), and 12.3% of these Lucky Passes are already that false positive.
- Anyone optimizes against the score. Policies trained on AIME problems against a process reward model reached rewards above 0.9 "while ground-truth accuracy remains low (below 4%), with 43% of reward gains attributable to stylistic shortcuts" ([Tiwari et al., 2026](https://arxiv.org/abs/2603.06621v1)). The paper reports this from standard RL, "without adversarial intent". That lands on promoting process quality to a training reward, not on reading it post hoc.
- You grade against one reference trace. A single-reference paradigm is "inadequate for assessing the rich space of valid agent execution paths" ([Shi et al., 2026](https://arxiv.org/abs/2609.14637v3)), the objection that keeps [outcome grading](../../verification/grade-agent-outcomes.md) the right default for the gate.
- Your suite carries few tasks. Weak passes concentrate, and "the top 10 tasks account for 77 of the 122 Lucky Passes (63.1%)" ([Sahoo et al., §D.5](https://arxiv.org/abs/2605.12925v4)), so a small suite's rate describes its task mix.

## Key Takeaways

- Keep the pass/fail gate. Add process quality beside it for model choice, cost, and demonstration filtering.
- Build the reference from several passing runs per task. Thirteen of 60 tasks here never qualified for one.
- Only three of the five weak-pass classes point at the agent. One points at the test suite and one at the scorer.
- Log token spend per run and read it beside the verdict. Token counts are usually already in the trajectory log.
- Do not promote the score to a training target without an anti-hacking check.

## Related

- [Grade Agent Outcomes, Not Execution Paths](../../verification/grade-agent-outcomes.md) — the rule this page qualifies: outcome grading stays correct for the gate, and process quality is a second signal beside it
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](../../verification/trajectory-decomposition-diagnosis.md) — the same artifact read on failing runs, scored for stage precision against a reference patch
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the per-run form, where the skipped step is a mandate in the agent's own skill rather than a benchmark's blind spot
- [Trajectory-Aware Benchmark Subset Selection for Agents](../../verification/trajectory-aware-benchmark-subset-selection.md) — what noise in the pass label costs when that label is the key a subset is grouped by
- [Assertion-Free Test Theater](assertion-free-test-theater.md) — the test-suite half of the incomplete-implementation class, where a present test asserts nothing
