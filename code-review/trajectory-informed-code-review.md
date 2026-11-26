---
title: "Trajectory-Informed Code Review From the Author Agent's Run"
term: "Trajectory-Informed Code Review"
description: "A reviewer takes leads from the coding agent's run, then checks the code. One study saw higher mean recall on synthetic labels, precision unmeasured."
tags:
  - code-review
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - trajectory-informed review
  - reviewing with the author agent's trajectory
last_reviewed: 2026-11-26
maturity: emerging
---

# Trajectory-Informed Code Review From the Author Agent's Run

> Trajectory-informed code review lets an independent reviewer take leads from the author agent's run, then test them against the code.

Trajectory-informed code review gives an independent review agent the coding agent's development trajectory beside the final diff and repository. A trajectory records the run that wrote the code: the user request, the agent's messages, its tool calls and their output, and its completion message ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

## Why the run can help

The final patch does not preserve the full process that produced it. In the authors' words, "A discarded approach may expose a compatibility constraint, while a failed test and its subsequent repair may suggest related scenarios that remain unchecked". The record also carries assumptions that may be wrong ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

## What the study measured

The study used 113 DeepSWE tasks from 91 repositories: 339 implementations from three coding configurations, with 882 synthetic reference comments. Codex CLI and GitHub Copilot CLI reviewed them in `/review` mode, both with GPT-5.6 Sol, for six coding-review configurations. The table gives mean recall, the share of reference comments matched ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

| What the reviewer gets, beyond patch and repository | Mean recall |
|---|---|
| Nothing (diff-only) | 23.03% |
| Full raw trajectory | 25.87% |
| Code first, then the trajectory to challenge that assessment | 27.08% |
| Full trajectory, with the reviewer selecting its own signals before reading code | 27.83% |
| Messages only | 29.03% |
| Evidence-linked map | 30.35% |

The raw trajectory raised recall in only four of six configurations, falling on GPT-5.6 Sol-authored code under both harnesses. In that condition, reviewers' trajectory-reading calls returned only about 10% of its text. The four alternative methods (the last four rows) each gained 4.05 to 7.32 points over diff-only on average ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

## What limits the result

- The comparison is confounded. "Diff-only review receives neither a development trajectory nor a separate task description", while trajectory conditions carry the original user request ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)). Part of the gain may come from knowing the task (inference).
- Precision was not measured, so extra comments may be wrong ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- GPT-5.6 Sol wrote the synthetic reference comments, comparing each implementation with a held-out reference patch, and also did the matching. "Synthetic labels may be incorrect, duplicated, or incomplete", and a reference patch can embody one valid design ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- Recall stays low: about 30% for the best mean and 38.31% for the best single configuration ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- Repeat runs cover one configuration, GPT-5.5 code under Copilot CLI. There the map and Messages tied at 36.71% against 27.14% for diff-only ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- Gains are uneven. On GPT-5.6 Sol-authored code the map added 2.70 and 1.62 points, and under Copilot CLI Messages beat it, 21.62% to 18.38% ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

## Build an evidence-linked map

The map had the highest mean recall. Its procedure ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)):

1. Before inspecting code, extract the requirements from the user request and build one map from the full trajectory.
2. Make each fact and question cite its source events, and keep observations apart from interpretations.
3. For each prioritized question, connect the evidence to a code location, a plausible counterexample, and a focused check.
4. Fix the map before investigating. Delegated workers return code evidence without changing it.
5. Check the leads against the patch, callers, consumers, and tests, with a limit of ten focused probes. Discourage broad suites and repeated checks.
6. Supplement the map's leads with an independent code-driven pass.

## Or pass only the messages

Messages keeps all user and agent text in chronological, role-labeled order, and omits tool calls and their output. The reviewer checks that account against the patch and repository ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)). With tool output gone, the reviewer cannot compare the author's claims with what its commands returned (inference). Those claims can be wrong, which is why [work reports get checked against the record](../verification/check-agent-work-reports-against-records.md).

## What it costs

Time and cost are ranges of per-configuration medians for the whole review session, without the coding run. Cost is estimated at API prices archived on 2026-09-26. Recall is the six-configuration mean ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

| Measure | Diff-only | Messages | Evidence-linked map |
|---|---|---|---|
| Review time, minutes | 1.85 to 2.42 | 1.88 to 2.90 | 3.22 to 7.12 |
| Estimated API cost per review, USD | 0.36 to 0.56 | 0.45 to 0.60 | 1.13 to 2.06 |
| Recall, critical failure-linked comments | 22.90% | 30.81% | 40.40% |
| Recall, other comments | 22.79% | 28.59% | 29.73% |

The map's median input tokens were 2.81 to 6.18 times diff-only's, and its output tokens 2.39 to 3.45 times. Critical failure-linked means GPT-6 Astra judged that the comment directly explains a DeepSWE verifier failure. Only 51 comments qualify, against 829 others ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).

## When this backfires

- You replace diff-only review. In every configuration it matched comments the map missed ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- You treat the trajectory as proof. "The trajectory guides what to investigate, while the review probe and final code establish whether the suspected problem remains" ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- You share trajectories freely. The authors say production deployments should keep repository permissions and least privilege on trajectories and derived artifacts such as maps, and filter restricted content before a reviewer sees it. For sensitive repositories, "secret scanning and sanitization should precede analysis, dataset construction, or sharing", covering both ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)).
- The author read untrusted text. Tool output can carry it to the reviewer, so limit the reviewer's write and network access (inference).

## How it differs from nearby patterns

- [Diff-based review](diff-based-review.md) sets the review boundary at the delta. The delta stays under review here, and the run adds leads.
- [Per-reviewer context views](per-reviewer-context-views.md) build input from the diff and repository structure, not the history of the run.
- In an [agent self-review loop](agent-self-review-loop.md) the author checks its own work. Here an independent reviewer reads the author's record.
- A [committee review](committee-review-pattern.md) splits reviewers by lens. This study compared no panels.
- [Context reset or model diversity](../patterns/multi-agent/context-reset-vs-model-diversity.md) asks how a reviewer differs from the author. The trajectory is material the author already saw, so new evidence has to come from the reviewer's checks (inference).
- [Role-declared context mode](../patterns/multi-agent/role-declared-context-mode.md) keeps a verifier from inheriting the supervisor's reasoning. Here the reviewer gets the author's reasoning on purpose, as claims to test. The net recall gain does not show how often it steered a reviewer off a defect (inference).

A [separate-critic comparison](../verification/separate-critic-over-self-recheck.md) gave critics the task and changes, with or without the trajectory, and scored outcomes after the author revised. Across three benchmarks the full trajectory did not consistently improve outcomes, although trajectory designs scored higher on Terminal-Bench ([Zhang et al., arXiv:2610.34577v1](https://arxiv.org/abs/2610.34577v1)).

## Example

The study's FastAPI task adds settings for automatic HEAD and OPTIONS responses. While building them, the coding agent hit a test failure about which setting takes precedence, repaired it, and then passed all 11 tests in its targeted suite. The map turned that history into a question ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)):

```text
Evidence        inclusion copies routes and resolves route/include/router/self,
                with a later correction to precedence logic.
Question        Does repeated/nested inclusion preserve nearest non-omitted
                precedence after routes have already been materialized?
Surface         include_router.
Counterexample  same child router included through two parents with opposite
                include-level settings.
Probe           nested two-parent inclusion matrix for both HEAD and OPTIONS.
```

The reviewer tested the same rule in a simpler nested setup, with OPTIONS unset at the two inner levels and enabled only at the outer inclusion. The app returned HTTP 405 where the outer setting should have enabled the response ([Luo et al., arXiv:2611.31316v1](https://arxiv.org/abs/2611.31316v1)):

```text
PROBE2 nested omitted then outer include override
405 {"detail":"Method Not Allowed"} materialized flags [False]
```

At the first inclusion, `default=False` had turned "unspecified" into an explicit disable. That stored value then took priority over the outer `True`.

## Key Takeaways

- Do not stop at attaching the raw log. Its gain was inconsistent in this study, and all four alternative methods averaged higher.
- If you add a trajectory-informed pass, keep your diff-only one. In every configuration, diff-only and the map each matched reference comments the other missed. The study ran no combined condition.
- Try Messages when review minutes or spend are tight, and the evidence-linked map when higher recall is worth more of both.
- Before you adopt it, give your diff-only baseline the task description and count wrong comments in both arms. The study did neither.

## Related

- [Diff-Based Review Over Output Review](diff-based-review.md)
- [Per-Reviewer Context Views for Code Review Agents](per-reviewer-context-views.md)
- [Reproduce-Before-Report Verification Gate](reproduce-before-report-verification-gate.md) — a verifier that reports only findings it can reproduce
- [Check Coding Agent Work Reports Against the Work Record](../verification/check-agent-work-reports-against-records.md) — why the author's account needs checking
- [A Separate Critic Over Completion-Time Self-Checking](../verification/separate-critic-over-self-recheck.md) — critics compared with and without the execution trajectory
