---
title: "Completion Summary as the Oversight Surface"
term: "Completion Summary as Oversight Surface"
description: "An agent's end-of-task summary referenced 9.4% of the actions its session executed, and leaned back toward the abandoned plan as execution departed from it."
aliases:
  - agent self-report as oversight surface
  - reading the completion summary instead of the log
  - treating the agent summary as the record of the run
tags:
  - anti-pattern
  - observability
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-14
maturity: emerging
status: current
---

# Completion Summary as the Oversight Surface

> In 5,115 measured coding-agent sessions the end-of-task summary referenced about one action in eleven, so reading it is not reviewing the run.

The summary an agent writes when it finishes is the artifact most developers read, and it carries a small share of the work. The SWE-chat corpus holds 5,851 real developer sessions and 355,942 tool calls. Across the 5,115 sessions carrying both a report and a log, mean omission was 0.906, so a self-report referenced 9.4% of the actions its session executed. Given only the report, a probe model rebuilt the action log at a mean F1 of 0.202 over 5,289 sessions, which is about a fifth of the action surface ([Kraishan and Jitkajornwanich, arXiv:2609.12205v1](https://arxiv.org/abs/2609.12205v1)).

## When this applies

Three conditions decide whether that number costs you anything.

- The session is long. Sessions executed a median of 59 actions against a median four claims per report, and the omission distribution has a long left tail of short sessions whose reports do cover the run.
- Review stops at the summary. Where the merge is gated on a diff, a test run, and CI, the report was never the oversight surface.
- The claims you care about are outcomes. Of 20,641 extracted claims, 32.0% asserted an outcome and 62.7% an action. Outcome claims ("all tests pass") are the ones a reader most needs to check and an action log is least able to confirm.

Every session in the study is a coding-agent session recorded through one capture CLI, and 82.9% of them used Claude Code.

## The anti-pattern

You read the final message, glance at a diff, and move on. A report being shorter than a log is unavoidable; what matters is what the shortening leaves out and which way the remainder leans.

Hand coding of the unsupported claims found two shapes, both in the example below: an outcome asserted without the action that would produce it, and a count with no record behind it, such as "modified 39 files" against a handful of writes. Both describe a state the agent may well have believed it reached, narrated as though the reaching had been observed.

## Why it works

The first cause is arithmetic. The scaffold records the log as calls are made and the agent composes the report afterwards, so with a median 59 actions against a median four claims a report referencing every action would be as long as the log.

The second is directional, and it is the one you would not guess. The report's implied action sequence is better contained in the stated plan than in the executed log, and that gap grows with how far execution departed from the plan (b = 0.771, Spearman rho .548, n = 2,327). Agents abandoned a mean 27.7% of stated plan steps. Where execution followed the plan the report tracked the log; where execution abandoned it the report leaned back toward the plan. The authors read this through Suchman's situated-action account: "the report is where situated action gets narrated back into a plan, and it happens in proportion to how much situated action there was to narrate" ([arXiv:2609.12205v1](https://arxiv.org/abs/2609.12205v1)). What drifts is the implied sequence, not necessarily the outcome.

## When this backfires

- Thin reports did not predict trouble here. How far an agent departed from its stated plan carried no information about whether a human later modified agent-authored lines (odds ratio 1.00, 95% CI [0.74, 1.35], p = .989, n = 2,646). Omission ran 1.6 percentage points higher in corrected sessions, which the authors report as small.
- Reading the log is not a free fix. A study of a computer-user agent found current trace practices "cumbersome, limiting their efficacy", and its proposed design reduced the time participants spent finding errors, but "although participants reported higher levels of confidence in their decisions, their final accuracy was not meaningfully improved" ([Grunde-McLaughlin et al., arXiv:2602.16844v1](https://arxiv.org/abs/2602.16844v1)).
- Do not quote the commission rate. Kraishan and Jitkajornwanich also report 35.3% of claims unsupported, but it comes from a model adjudicator that agreed with hand coding at 0.56 (Cohen's kappa .185) and credited the agent far more often than a human reader of the same log did ([arXiv:2609.12205v1](https://arxiv.org/abs/2609.12205v1)). They treat the figure as a lower bound and draw no inference from it. Neither should you.
- No stated plan, no drift signal. Divergence and repair are defined only on the 2,646 sessions carrying a recoverable plan, an exclusion the authors call non-random.

## Example

**Before — outcome asserted without the action that would produce it.** Two claims from the study's validation sample, beside the log the hand coder read them against:

```text
Claim: "All tests pass."
Log:   12 read and execute actions; every execute is a grep over test files.
       No test runner is invoked.                              -> unsupported

Claim: "Pushed changes to remote, synced with local."
Log:   file reads, three writes, git diff --stat && git status.
       No git push.                                            -> unsupported
```

**After — the outcome claim linked to the action that verified it.** The paper's own proposal for oversight interfaces: an action claim links to the tool call that performed it, and an outcome claim links to the action that verified it, so an interface can mark the outcome claims for which no verifying action exists in the log ([arXiv:2609.12205v1](https://arxiv.org/abs/2609.12205v1)).

```text
Claim: "All tests pass."
Link:  no execute action invokes a test runner             -> flag for review
Claim: "Posted PR review comment on PR #22."
Link:  gh pr review 22 --comment                           -> supported
```

## Key Takeaways

- Budget review attention on the assumption that the summary names about 9% of the run and affords a reader about 20% of it, whatever the session's outcome
- Sort claims before checking them: an action claim can be matched to a tool call, an outcome claim needs the action that verified it, and that action is the one most often missing
- Read the summary with the most suspicion on sessions where the agent visibly changed course, because report-to-plan drift rises with plan-execution divergence
- The abandoned plan is a review input, not a checklist: compare which planned steps have a matching executed step and which executed steps had no planned antecedent
- Keep the load-bearing gates outside the narration, in the diff and the test run, so the report's coverage never becomes what you are trusting

## Related

- [Coding-Agent Misalignment Forms (Seven-Symptom Taxonomy)](coding-agent-misalignment-forms.md) — names inaccurate self-reporting as one of seven field-observed forms; this page supplies how much of a run the report carries
- [Trust Without Verify](trust-without-verify.md) — the same mistake one artifact earlier, where polish on the output stands in for a correctness check
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the procedural half: a step an agent skipped is invisible to a check that only reads the artifact
- [Verification Ledger for Tracking Agent Output Quality](../../verification/verification-ledger.md) — the remedy pattern, replacing self-reported claims with structured records carrying tool and exit code
- [Trajectory as the Monitoring Unit for Production Agents](../../observability/trajectory-as-monitoring-unit.md) — moves the monitored unit from one output to the whole run, which is the record the report omits
