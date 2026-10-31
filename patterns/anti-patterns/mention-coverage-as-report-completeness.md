---
title: "Mention Coverage as Report Completeness"
term: "Mention Coverage as Completeness"
description: "Most of the task state an agent's reports left unrecovered was mentioned in them, and adding a mention measured -.002, so a coverage audit misses most of the gap."
tags:
  - anti-pattern
  - human-factors
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - mention coverage as completeness
  - mentioned but insufficient reports
  - auditing an agent report for named events
last_reviewed: 2026-10-15
maturity: emerging
status: current
---

# Mention Coverage as Report Completeness

> Two annotators scored states mentioned without enough detail as most of what an agent's reports left unrecovered, so counting mentions cannot measure completeness.

A mention-only audit checks whether a report names an event. It does not check whether the report answers a later question about that event.

CTXGAP compares accumulated reports with full execution context from 37 coding-agent trajectories on SWE-bench Verified Python issues. Across 4,799 probes, reports supported 52.0% recovery against 92.7% from full context, a 40.7-point gap. The agent answered 93.6% when queried at an isolated checkpoint fork ([arXiv:2610.20003v2](https://arxiv.org/abs/2610.20003v2)).

## The anti-pattern

On 195 stratified gap atoms, two annotators assigned 55.4% and 59.2% of weighted gap mass to states mentioned without sufficient detail. Unmentioned states accounted for 42.1% and 33.7%; sufficient-yet-unrecovered states accounted for 2.5% and 3.7%. Agreement was Cohen's kappa .632 for mention and .638 for sufficiency. The authors conclude: "Mention-based coverage can therefore overstate answer support" ([source](https://arxiv.org/abs/2610.20003v2)).

Adding a mention did not solve this. Across 99 human-screened candidates, mention-only additions changed recovery by -.002, with a 95% confidence interval of [-.027, +.025] ([source](https://arxiv.org/abs/2610.20003v2)).

## Why it works

Recovery measures whether the reader can answer a specific question. Naming the activity does not supply its particulars. The gap persists after successful repairs. At the final checkpoint of 30 hidden-test-verified fixes, reports trailed full context by 34.8 points [28.2, 41.3]. The gap was positive in 28 tasks ([source](https://arxiv.org/abs/2610.20003v2)).

## When this backfires

- Better reporting instructions are a partial lever. Rewrites at matched total length gained about eight points but used complete execution context to create both rewrites, "not an autonomous reporting effect". Targeted summaries beat natural ones at matched added length (+2.39 [+1.05, +3.57]) ([source](https://arxiv.org/abs/2610.20003v2)).
- More visible history helps only partly. Full terminal scrollback recovered 73.6%, leaving a 19.1-point gap. This measures available history, not what a person necessarily reads or remembers ([source](https://arxiv.org/abs/2610.20003v2)).
- More confidence can accompany unchanged accuracy. In a controlled study of one redesigned trace interface for a Computer User Agent, the interface reduced error-finding time without meaningfully improving final accuracy. It "did increase confidence when participants were incorrect" ([Grunde-McLaughlin et al.](https://arxiv.org/abs/2602.16844v1)).
- The instrument may favor exact identifiers. The authors' literal-detail check "supports the existence of a gap among LLM-assessed non-literal probes, not a quantitative decomposition of the headline 40.7-point gap" ([source](https://arxiv.org/abs/2610.20003v2)).
- Generalization is limited. The non-random 37-task Python cohort underrepresents difficult issues from a 76-task inventory. Two models, rather than people, judged supervisory relevance ([source](https://arxiv.org/abs/2610.20003v2)).

## Example

A Django checkpoint from the study, where a coverage audit scores a hit and a reader recovers nothing:

```text
Execution context  two end-to-end scripts
                   fake_psql.py  captures subprocess environment variables
                   e2e_check.py  exercises the database-shell path under
                                 empty and password-bearing configurations
Report             mentions "a fake psql test"
Probe              which scripts were created, and what did each do?
                   full-context observer   3 of 3 samples correct
                   report-only observer    0 of 3
```

Both annotators classified that report as mentioned but insufficiently supported ([arXiv:2610.20003v2](https://arxiv.org/abs/2610.20003v2)). The test was named, so the checklist clears.

## Key Takeaways

- Score a report by what a reader can answer from it. On 195 stratified gap atoms, 55.4% and 59.2% of weighted gap mass (by annotator) sat in states the report already mentioned.
- Treat a mention-only remedy as unsupported until someone measures it. The direct test came back at -.002 with a confidence interval spanning zero.
- Put the specific question to the agent at the checkpoint instead of relying on its accumulated report. It answered 93.6% of the same probes at an isolated fork. The supervisor must already know which question to ask, because an agent may omit the states that would prompt one.
- Budget scrollback access as a partial substitute, worth 73.6% against 92.7% from full context, and expect the residual to stay.
- Keep a verified fix and a legible report as separate claims. The gap measured 34.8 points after a hidden-test-verified repair.

## Related

- [Completion Summary as the Oversight Surface](completion-summary-as-oversight-surface.md) — the same channel measured from the omission side, where the summary referenced about one action in eleven
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the procedural twin, where a check that reads only the output cannot see a step the agent skipped
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the claim a thin report is most likely to carry unsupported
- [Verification Ledger for Tracking Agent Output Quality](../../verification/verification-ledger.md) — replacing narrated claims with records that carry the tool and exit code
- [Transcript-Measured Review Coverage](../../verification/transcript-measured-review-coverage.md) — the measured version of one such claim, checking whether a review touched the files it says it did
