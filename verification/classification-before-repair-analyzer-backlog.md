---
title: "Classification Before Repair in an Analyzer Backlog"
term: "Classification Before Repair"
description: "When an agent works a static-analysis backlog instead of a failing test, its expensive errors sit in deciding whether each finding is real. Gate the queue on classification and read the finding count as fixed-or-silenced."
tags:
  - testing-verification
  - copilot
  - code-review
  - arxiv
aliases:
  - analyzer backlog triage for agents
  - true-positive gating before agent repair
last_reviewed: 2026-09-10
maturity: emerging
---

# Classification Before Repair in an Analyzer Backlog

> On an analyzer backlog an agent's costly mistake is deciding a finding is real, not writing the patch.

Split the queue before you assign it. A backlog finding has three correct outcomes — a code change, a suppression, or a rule change — and an agent picks between the first two on its own, with no oracle to check it. The patch itself is the cheap half, because the analyzer that raised the finding can be re-run against any tree state.

## When this applies

Check all four before handing over a queue.

- The input is a standing default-branch backlog, not a failing test or a pull request diff. GitHub shipped this shape on 2026-09-09: "You can select up to 25 standard findings on a page and assign the whole set to Copilot in one action" ([GitHub Changelog](https://github.blog/changelog/2026-09-09-remediate-code-quality-findings-with-agentic-autofix)). Standard findings are the deterministic CodeQL set, listed separately from the AI findings dashboard ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/maintain-quality-code/explore-code-quality)).
- The findings are local. Across 1,000 SonarQube warnings in 106 Java projects, 99.4% of single-line fixes were plausible, against 95.5% for multi-line and 75.0% for multi-file ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).
- You can re-run the analyzer per finding on demand, against the pre-fix and post-fix tree.
- The flagged files carry tests. GitHub warns that the model "may suggest fixes that are syntactically valid but change the semantics of the program" ([GitHub Docs](https://docs.github.com/en/code-security/responsible-use/security-and-quality-ai-features)).

Cross-module findings fail the second condition badly enough to skip the technique. On 65 hard-severity architectural smells in scikit-learn, expert validation found 63.1% were false positives, the best of 11 agent configurations resolved 47.7%, and the most aggressive agent introduced 140 new smells ([Dinu et al., 2026](https://arxiv.org/abs/2605.07001v2)).

## Where the errors concentrate

CodeCureAgent classifies each warning true or false positive before acting, then repairs or suppresses it. On its 1,000-warning benchmark it labeled 69.6% true positive and 30.4% false positive. Manual inspection of 291 distinct-rule cases put classification accuracy at 91.8% and the end-to-end correct-fix rate at 86.3%, and the authors report that "most errors arise in the classification phase (8.2%), rather than in the subsequent repair" ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).

The split inside that number should drive the gate. Classification was 97.4% accurate on true positives and 81.0% on false positives, and the authors read the residual errors as a direction rather than a rate: "CodeCureAgent tends toward missed repairs rather than unwanted changes, since suppression does not alter program behavior beyond silencing the warning" ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).

## Three outcomes, one metric

Resolving a false positive means writing a suppression comment, and 95.1% of those fixes were single-line, "as FPs can usually be suppressed by adding a NOSONAR comment to the warning line" ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)). Nothing about program behavior changes. Retiring a rule that fires on nothing actionable is unreachable for an agent working finding by finding, so it arrives as many suppressions instead of one config edit.

The dashboard will not tell you which one happened. GitHub's trend graph "tracks the total count of open findings, not individual findings being opened or fixed," and the total includes findings "fixed in the code or dismissed by users" ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/maintain-quality-code/explore-code-quality)). Bulk dismissal, added in the April preview, moves the same line as bulk repair ([GitHub Changelog, 2026-04-14](https://github.blog/changelog/2026-04-14-github-code-quality-improvements-to-standard-findings-in-public-preview/)).

## Why it works

Gating on classification pays off because the repair half is already cheap to check and the classification half has no automated check at all. A CodeQL or SonarQube rule evaluates against any tree state on demand, so the agent gets the pre-fix and post-fix contrast that repair agents usually lack. Across 3,730 validation events, 46.0% of positive comparable events carried "no bug-discriminating information" ([Xu and Wu, 2026](https://arxiv.org/abs/2607.28871v1)); see [bug-discriminating validation evidence](bug-discriminating-validation-evidence.md) for the replay method.

Ablating CodeCureAgent's change approver prices the remaining gates against each other, counting patches that the full three-check approver would have rejected. Dropping the test suite admitted 9 of them. Dropping the static-analysis re-run admitted 123 ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).

Nothing comparable exists for "is this finding worth acting on." That question gets answered once, by the agent, and every downstream gate then measures something else. A suppression passes the build, clears the rule, and keeps the suite green, which makes it the correct action on a real false positive and an invisible one on a misjudged true positive.

## When this backfires

- Architectural and cross-module findings. The SmellBench numbers above make agent triage net-negative there.
- Files the suite does not cover. The regression gate is inert, and the analyzer re-run cannot see a semantics change that leaves the rule satisfied.
- Backlogs dominated by one noisy rule. Tuning the ruleset is cheaper, and an agent handed the queue scatters suppressions through the source instead.
- Review that exists on paper. Batching 25 findings puts them behind a single review, and across 33,596 agent-authored pull requests in GitHub repositories with at least 100 stars, 61.38% received no recorded review activity ([Duma et al., 2026](https://arxiv.org/abs/2605.02273v1)).
- Fixes that touch dependencies. GitHub warns the system "may suggest fabricated dependencies published under statistically probable names" ([GitHub Docs](https://docs.github.com/en/code-security/responsible-use/security-and-quality-ai-features)).

The strongest case against the technique is that triage is the wrong response to a backlog running a 30% to 63% false-positive rate. Fix the rules first, and the residue is small enough to read yourself.

## Example

Nullability checkers produce exactly the mixed queue this technique is for. Residual errors surviving annotation inference are "typically a mix of real bugs and false positives," and NullRepair resolves 63% of the 1,119 that remain across 12 Java projects, with all unit tests passing in 10 of 12 ([Karimipour et al., 2026](https://arxiv.org/abs/2507.20674v2)).

Applied to GitHub's flow, that means not selecting 25 findings in dashboard order. Select findings whose rule you have already judged actionable, whose fix is single-file, and whose file has tests. Assign that set, then read the resulting pull request for its suppressions before its diffs. A suppression is the agent's classification made visible, and it is the only part of the change no later gate re-examines.

## Key Takeaways

- Repair accuracy is not the binding constraint on a backlog. CodeCureAgent reached a 96.8% plausible-fix rate and an 86.3% correct-fix rate, with most of the loss in classification ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).
- Gate the queue on the judgment you can make without the agent: the rule is actionable, the fix is single-file, the file is covered.
- Re-running the analyzer is the load-bearing automated gate on this input, worth roughly 13 times the test suite measured by false accepts admitted ([Joos et al., 2026](https://arxiv.org/abs/2509.11787v5)).
- Read a falling finding count as fixed-or-silenced. GitHub's trend graph counts a repair, a suppression, and a bulk dismissal identically ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/maintain-quality-code/explore-code-quality)).
- Treat a detector whose findings are 63.1% false positive on expert review as a ruleset defect rather than a remediation queue ([Dinu et al., 2026](https://arxiv.org/abs/2605.07001v2)).

## Related

- [Layered Oracle Stack for Agent IaC Security Repair (TerraProbe)](layered-oracle-iac-security-repair.md) — What to do after a finding is classified real: stack behavioral oracles, because clearing the scanner rule is not the same as fixing the policy.
- [Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)](bug-discriminating-validation-evidence.md) — The pre-fix replay this technique assumes, measured on repair agents that have no on-demand oracle.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — Cost-ascending gate ordering for the repair half, where a target test exists to constrain intent.
- [Closed-Loop CI Failure Remediation with Cloud Coding Agents](../workflows/closed-loop-ci-failure-remediation.md) — The same delegation with a failing test as input, which removes the classification question.
- [Explained Feedback for LLM Vulnerability Repair](explained-feedback-vulnerability-repair.md) — How much of the scanner diagnostic to pass back once a finding is queued for repair.
- [Per-Layer Suppression Accounting in Acceptance Gates](per-layer-suppression-accounting.md) — Which layer of a stacked gate actually discards a finding, measured rather than assumed.
