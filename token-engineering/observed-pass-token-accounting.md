---
title: "Observed-Pass Token Accounting for Post-Success Agent Spend"
term: "Observed-Pass Token Accounting"
description: "Measure remaining tokens from the first agent-observed pass, or from the first retrospective pass when no pass was observed. Keep these starting points separate."
tags:
  - token-engineering
  - cost-performance
  - testing-verification
  - arxiv
  - tool-agnostic
aliases:
  - observed pass versus retrospective pass
  - post-success token split
last_reviewed: 2026-10-27
maturity: emerging
---

# Observed-Pass Token Accounting for Post-Success Agent Spend

> Post-success agent spend splits two ways: tokens after a pass the agent observed, and tokens after one it never checked for.

Compute that split before you buy a stopping rule, under two conditions: your harness leaves running the check to the model, and that check is the acceptance oracle for the task. Where both hold, the split names which intervention your spend needs. Where either fails, the split either returns nothing or sends you to suppress verification worth keeping.

## What the split showed

[Wu, Anderson and Guha](https://arxiv.org/abs/2607.22807v2) ran five models over Python, Java, Rust and OCaml on MiniLCB, 100 competitive-programming problems with every test visible and a `test.sh` runner supplied. Replaying the suite against every intermediate solution the agent wrote to disk dates the first correct solution independently of whether the agent ever looked. The table gives Gemma-4-26B-A4B medians: tokens, with turns in parentheses, from Tables 8 and 9. The columns use different starting points. Table 8 starts at the first pass the agent observed; Table 9 starts at the retrospectively passing snapshot for trajectories with no observed pass ([Appendix E](https://arxiv.org/abs/2607.22807v2)).

| Language | After first agent-observed pass | After first retrospective pass; no observed pass |
|---|---|---|
| Python | 698 (1), N = 68 | 45,518 (10.5), N = 16 |
| Java | 3,066 (1), N = 81 | 17,970 (3), N = 3 |
| Rust | 743 (1), N = 66 | 24,768 (4.5), N = 20 |
| OCaml | 743 (1), N = 57 | 18,909 (29), N = 5 |

GLM-5.2 in the same harness sits at 66-79 tokens after an observed pass and puts only 7 trajectories in the right-hand column across all four languages ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2), Tables 8 and 9).

The right-hand column is not a population of agents that checked, saw green, and carried on anyway. For Gemma, "43 of 44 (across all four languages) never ran test.sh at all—the agent is not checking repeatedly and failing, it is simply not checking" ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2), Appendix E).

## Why it works

A stop-on-first-pass rule needs an observed pass. Supplying a check makes that observation possible; it does not ensure the agent runs it. MiniLCB's prompt is about as direct as an instruction gets: "To test your program, run exactly: ./test.sh", "These are the only tests I care about", and submit the moment it exits zero ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2), Appendix B). The weaker models substituted their own checking: "over 70% of their snapshot spans into stay are bare solution writes with no preceding test execution. Instead, they frequently challenge their solutions by replaying the sample inputs or constructing their own test cases." ([§4.5](https://arxiv.org/abs/2607.22807v2)).

So the pass exists on disk and nowhere in the agent's context, and a rule keyed to it cannot fire. The authors say so outright: "A simple stop-on-first-pass intervention would not by itself fix this: the agent is not verifying and stopping late, it is not verifying at all." ([Appendix E](https://arxiv.org/abs/2607.22807v2)). For observed-pass spend, test a stopping rule. For never-observed-pass spend, test a harness-run check that supplies its result, such as a [pre-completion gate](../verification/pre-completion-checklists.md). These are proposed interventions; the table does not measure their effects.

## Computing it

Three steps, none of which need the agent's cooperation.

1. Snapshot the solution file on every write, so you hold each intermediate state rather than the final one.
2. Replay the acceptance check against each state offline and date the first full pass.
3. Scan the trajectory for the agent's own invocations of that check, and date the first one that reported a pass.

For trajectories with an observed pass, count remaining tokens from step 3's date. For trajectories without one, count from step 2's date. Keep both timestamps when available; the table does not compare the populations from one common starting point ([Appendix E](https://arxiv.org/abs/2607.22807v2)). Evaluate whether the remaining work is useful before classifying its tokens as waste.

## When this backfires

- Frontier models in the same harness do not show the failure. GPT-5.5 and Sonnet "typically write the solution once, immediately run ./test.sh, and submit if all tests pass" and spend 42-136 median tokens after the first correct solution against Gemma's 3,356-7,312 ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2), Appendix D Table 6 and Table 3). Snapshot replay costs more to build than 42 tokens a run can repay.
- The visible suite is not the acceptance oracle. MiniLCB can declare "These are the only tests I care about"; a real repository's suite rarely can. PatchDiff found that "even more (29.6%) plausible patches induce different behavior than the ground truth patches" on SWE-bench Verified, "because testing is rarely exhaustive" ([arXiv:2503.15223v2](https://arxiv.org/abs/2503.15223v2)). Halting on a partial suite's pass then locks in a plausible-but-wrong patch. Extra checks can seek defects the visible suite misses; this result does not establish their effectiveness.
- A prompt-level decision rule may be enough, and it is far cheaper. Asked to reproduce an issue first and abstain if it is already resolved, GPT-5.4 mini's abstention rose "from 60.5% to 88.5%" and Sonnet 4.6's "from 65.0% to 80.5%", with "no performance degradation" on standard SWE-Bench ([SRI Lab, ETH Zurich](https://www.sri.inf.ethz.ch/blog/fixedcode)). Try that first. It over-fires, though: with a previous incorrect patch in the tree, Sonnet 4.6 submitted 70% empty patches and GPT-5.4 mini 94%, despite the incorrect existing patch ([SRI Lab](https://www.sri.inf.ethz.ch/blog/fixedcode)).
- Your tests are slow or they touch shared state. Replaying them against every snapshot is the entire cost of the diagnostic, and you pay it before learning anything.
- The setting may not reach your work. The authors limit their result to "self-contained competitive-programming problems with visible test cases, solved using a single agent scaffold (mini-swe-agent)", and say it "may therefore not generalize to repository-scale software engineering tasks, or to other agent harnesses" ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2)).

## Key Takeaways

- Record test invocations separately from solution snapshots. A missing invocation calls for a different intervention from continuing after an observed pass.
- A stop-on-first-pass rule needs an observed result. An iteration cap counts turns and can stop either population, but does not establish correctness.
- Validate extra checks before treating their tokens as waste. PatchDiff's 29.6% figure concerns plausible SWE-bench Verified patches; it does not measure whether extra agent checks fix them ([arXiv:2503.15223v2](https://arxiv.org/abs/2503.15223v2)).

## Related

- [Language Choice as an Agent Token-Cost Lever](language-choice-token-cost.md) — the pre-success half of the same study: where the compile-loop tokens go before anything passes
- [Premature Completion: Agents That Declare Success Too Early](../patterns/anti-patterns/premature-completion.md) — the opposite error at the same seam, and why the fixes do not transfer
- [Pre-Completion Checklists for AI Agent Development](../verification/pre-completion-checklists.md) — the harness-run gate this split tells you whether to build
- [Reject on a Failing Check, Never Accept on a Passing One](../verification/asymmetric-check-evidence.md) — why a pass is weaker evidence than a failure, which bounds what any stopping rule can promise
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the instrument-attribute-fix-verify loop this diagnostic slots into
