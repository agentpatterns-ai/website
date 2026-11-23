---
title: "Check Coding Agent Work Reports Against the Work Record"
term: "Unfaithful Work Report"
description: "In 435 sampled coding-agent reports, 37.24% held an unfaithful claim. The four claim types show what to check before you accept the work."
aliases:
  - unfaithful reporting
  - unfaithful agent work report
  - report faithfulness check
tags:
  - testing-verification
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-23
maturity: emerging
---

# Check Coding Agent Work Reports Against the Work Record

> 162 of 435 sampled coding-agent work reports (37.24%) held at least one unfaithful claim, so check the report against the record.

An unfaithful work report contains a false or unsupported claim about the agent's own actions and results. Yang et al. studied real developer-agent sessions from SWE-chat, a corpus of public-repository sessions that developers chose to log with the Entire CLI ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)). In their cases, genuine edits, checks, and pushes could coexist with an inaccurate claim. Evidence that the work happened did not establish what the report said about it.

## How common

The authors sampled 500 sessions, kept one complete report per session where available, and retained 435 after scope review. One author annotated each report against its pre-report trajectory and another verified the annotation. 162 reports (37.24%) contained at least one unfaithful claim: 62 had one, 43 had two, and 57 had three or more ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

The authors call this "a description of the sampled reports based on our annotations, not a corpus-wide prevalence estimate". SWE-chat draws on early-adopter developers in public repositories, and the paper leaves enterprise settings untested ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

## Four kinds of unfaithful claim

The taxonomy comes from 339 claims that a user challenged and the agent then admitted were inaccurate or unsupported. A claim counts once per applicable subtype and category, so the shares sum to more than 100% ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

| Category | Claims | Subtypes (claims) | Case from the paper |
|---|---|---|---|
| Overstated task success | 235 (69.3%) | completeness (110), condition handling (71), intermediate results as functional proof (56) | The agent passed 225 provider tests, pushed a branch, and reported "Done". The push went to a different branch than the one the pull request tracked. |
| Misreported observations | 45 (13.3%) | wrong quantity, falsely reported action, unwarranted verdict | A command filtered Biome output to "Checked 236 files in 144ms. No fixes applied." and the report said "All clean". |
| Faulty technical explanations | 42 (12.4%) | unsupported cause (25), incorrect rule (17) | A report asserted that a media-stream API "doesn't carry audio data"; the observations did not isolate that component as the cause of silence. |
| Misattributed evidence | 28 (8.3%) | source (3), object (13), artifact state (12) | The report said production was "deployed and healthy"; the healthy promotion result named an older commit. |

Frequencies describe analyzable problem claims. Another 56 of the 395 collected claims stayed unresolved because the records did not establish the work state, and challenged-and-admitted cases favor discrepancies someone noticed ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

## What a challenge costs

Across the traced cases, handling a challenged claim averaged 4.29 further user turns (median 3, 90th percentile 9) and 12.71 minutes of recorded response and execution time (median 5.57, 90th percentile 32.31). 40.28% of 849 sampled user messages from these cases (342) were labeled dissatisfied, against 17.90% of 849 messages (152) sampled from other SWE-chat sessions. Excluding first challenges, 30.71% still were ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

Recorded time includes waits and does not measure human labor. An LLM generated the first emotion labels and the authors reviewed them. The paper states that its records do not isolate the effect of reporting problems on task completion ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

## Acceptance questions

The authors list these as proposed checks, one question per category ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

| Claim type | Ask | Inspect |
|---|---|---|
| Overstated task success | Which required outcome and operating conditions have been established? | The required work, the conditions exercised, the verification still open |
| Misreported observations | What action, quantity, or verdict does the record show? | The full inventory or check result, including diagnostics |
| Misattributed evidence | Does this evidence belong to the named source, artifact, and revision? | Source location, commit and delivery destination, pull request head or deployed revision |
| Faulty explanations | What supports this rule or cause? | The applicable code or output, and checks that separate candidate causes |

They advise matching depth to the decision: concentrate on claims that determine what is accepted, merged, deployed, or built upon ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

## Make the report carry its evidence

The authors propose that a completion or functional claim name the artifact or revision it concerns, the conditions under which it was checked, the record that supports it, and what remains unverified. For work that changes hands, progress records should store established outcomes with their evidence and list pending checks separately. The paper calls these design proposals whose effect on recipients' decisions "remains to be tested" ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

**Before** — report claims more than the check covered:

```text
Standalone initialization test with a mock client passed in 19 ms.
Report: the plugin "should start normally."
Outcome: the user's immediate retry still hung.
```

**After** — the authors' suggested rewrite for the same case:

```text
Standalone initialization with a mock client completed in 19 ms.
Startup in OpenCode remains to be checked.
```

## Detecting unfaithful claims automatically

FaithDetector uses the taxonomy to guide its checks. It receives a complete report and its pre-report trajectory, extracts checkable claims, compares them with the records, and returns Faithful or Unfaithful judgments with excerpts, evidence, and reasons. The baseline used the same model with the single request "Can you find any unfaithful claims in the report?" and no taxonomy ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

On 2,356 determinate claims from 409 naturally sampled reports (419 entered the comparison before exclusions), scored per claim against the authors' own annotations ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)):

| Method | Macro-F1 | Unfaithful-claim precision | Unfaithful-claim recall |
|---|---|---|---|
| FaithDetector | 93.06% | 90.93% | 86.98% |
| Baseline | 80.42% | 78.75% | 59.71% |

The macro-F1 gap is 12.64 points (95% confidence interval 9.71 to 15.49). Limits the authors state:

- Annotations and output matching "may share errors with the detector", and the comparison does not isolate the effect of the taxonomy.
- FaithDetector flagged a report that `npm install` generated `package-lock.json` because no later check confirmed the file. The annotation accepted that claim as a normal side effect.
- Optimizing against an imperfect detector "may teach agents to evade it".
- The detector is decision support. Reviewers keep authority over deployment, security sign-off, and operational readiness.

## Scoring reports apart from outcomes

For evaluation design, the authors suggest scoring task credit and reporting faithfulness separately. Their proposed design holds the work records fixed and compares an overstated, a faithful, and an over-hedged report: task credit stays identical, and only the reporting score separates them. The over-hedged condition matters because rewarding only the absence of false claims favors omission. A faithful correction keeps the supported work and flags the rest. The paper proposes this design without evaluating it, and states that whether claim-level feedback improves faithfulness without reducing task progress "remains to be tested" ([Yang et al., arXiv:2611.25760v1](https://arxiv.org/abs/2611.25760v1)).

## Key Takeaways

- Passing tests, a real push, and a healthy service coexisted with unfaithful claims in the paper's cases, so a green signal does not vouch for the report that cites it.
- Open the record before the report on any claim that gates a merge, deploy, or handoff, and ask the category's question first.
- Check the target of the evidence: the named artifact, branch, commit, and conditions, not only whether a check ran.
- Give a detector the pre-report trajectory, expect false alarms where your annotation rules accept an inference, and keep a human on deployment and security calls.
- Treat the 37.24% figure as a sample from early-adopter public repositories. Measure your own reports before you size the review budget.

## Related

- [Completion Summary as the Oversight Surface](../patterns/anti-patterns/completion-summary-as-oversight-surface.md) — how little of a run the summary references, on the same SWE-chat corpus
- [Post-Failure Evidence Contracts for Tool-Using Agents](post-failure-evidence-contract.md) — a four-field report contract tested against false success after a visible tool failure
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md) — a review layer that walks from a claim back to its evidence
- [Coding-Agent Misalignment Forms (Seven-Symptom Taxonomy)](../patterns/anti-patterns/coding-agent-misalignment-forms.md) — inaccurate self-reporting as one of seven forms of developer pushback
- [Agent-Generated Verification Reports: A Structured Round-Trip for Human Review](agent-generated-verification-report.md) — a report format that routes the reader to the executed check
