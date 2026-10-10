---
title: "Agent PR Intake Checklist: Visible Ownership Before Review"
term: "Agent PR Intake Checklist"
description: "An intake checklist for agent-authored pull requests, drawn from a 239-reviewer survey: what reviewers ask for before spending effort, and when to skip it."
tags:
  - code-review
  - human-factors
  - arxiv
  - tool-agnostic
aliases:
  - AI-Authored PR Intake
  - Stewardship Trace
  - Reviewability Debt
last_reviewed: 2026-10-09
maturity: emerging
---

# Agent PR Intake Checklist: Visible Ownership Before Review

> Reviewers in one survey spent effort on agent PRs that arrived with visible ownership, and an intake checklist makes that expectation explicit.

## The checklist, and where it applies

An agent PR intake checklist asks the submitter to show, before review starts, what the change is, why it fits the project, how it was validated beyond CI, and who will maintain it. The checklist rests on a survey of 239 practitioners from 31 countries ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). Treat it as something to pilot, not as established practice, for the reasons in the next section.

The survey authors found that AI authorship was not a categorical rejection signal. Respondents described review effort as conditional on whether the PR arrived as an accountable contribution with five properties:

- bounded scope
- project-grounded rationale
- validation beyond CI
- contributor responsiveness
- identifiable post-merge ownership

## How strong the evidence is

The sample is purposive and non-probabilistic. Repository-based recruitment favors practitioners visible in mature open-source projects, and professional-network recruitment adds self-selection ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). Every percentage below comes from that sample.

The data are self-reported ratings of written scenarios, not observed review behavior. The study used questionnaire items rather than established psychometric scales, and it was cross-sectional. It was designed to characterize reviewer judgments, not to establish a causal effect of AI authorship on review behavior ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). The paper reports no test of whether any gate improves merge outcomes, defect rates, or reviewer time.

Authorship still mattered in the scenarios. With CI passing, willingness to accept a change without extra human explanation fell for agent PRs in every change type:

| Change type | Human-authored | Agent-authored | Drop |
|-------------|----------------|----------------|------|
| Cleanup | 86.2% | 73.6% | 12.6 points |
| Documentation | 85.4% | 66.9% | 18.4 points |
| Test additions | 79.5% | 61.5% | 18.0 points |
| Refactor, no behavior change | 52.3% | 19.7% | 32.6 points |

The agent item asked about additional human explanation, and it always followed the human item. The authors therefore call these gaps upper bounds on the effect of authorship alone ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

## What reviewers asked for

CI came first. Among entry requirements, 66.5% of respondents wanted passing CI or tests, and 56.9% wanted a clear PR description or intent. Ownership gates were a minority position: 41.8% required evidence that a known human would maintain the code, and 32.2% checked for an explicit ownership statement. Only 19.2% applied the same criteria regardless of authorship ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

Respondents deferred agent PRs most often for three reasons: vague or generic descriptions (64.9%), very large PRs without clear decomposition (51.0%), and missing tests despite behavior changes (51.0%) ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

Volume raises the stakes. Since agent PRs became common, 77.8% of respondents saw more PRs needing review, and 57.7% called the increase moderate or significant ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) covers the merge-rate side of that pressure.

## Building the checklist

Each item maps to a survey finding. Use the items as PR template fields, and pilot them before you enforce them.

1. Scope. State what the change does and what it leaves alone. Decompose a large PR before submitting it.
2. Rationale. Explain why the change fits this project. A generic description is the top deferral trigger.
3. Evidence matched to the change. Respondents asked teams to replace generic test requirements with evidence such as explain plans, migration dry-run notes, UI screenshots, or performance benchmarks. This was the second most common theme among 171 coded proposals ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).
4. Responsiveness. The author commits to answering review comments and CI or bot failures.
5. Ownership. Name who maintains the change after merge.

The authors call the combination a stewardship trace: a visible chain from generated output to human judgment that shows what was generated, what was manually revised, what validation ran, what assumptions remain open, and who will maintain the change. They write that disclosure alone is too weak ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

### Scale the checklist to risk

The authors advise against one-size-fits-all AI rules. Routine generated changes may need lightweight checks, while refactors, migrations, security, performance, accessibility, and user-facing changes need stronger evidence and ownership ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). For docs and typo fixes, a short description may be the whole checklist. For a refactor that claims no behavior change, ask for the evidence that supports the claim.

### Newcomer handling

Respondents did not favor automatic closure. 80.8% selected at least one special-handling strategy, and the most common was requiring the contributor to demonstrate understanding before review (55.6%) ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). [Explain-the-Change Review Gate](../workflows/explain-the-change-review-gate.md) describes that one gate in detail.

Profile signals counted for little. An active GitHub profile was rated highly or extremely influential by 23.4%, against 82.4% for a professional response to initial feedback and 81.2% for testing evidence beyond "it works for me" ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

## Why it works

Generative AI has made old signals of contributor effort cheap. The authors write that a fluent description no longer shows the contributor understood the change, and that responding well to feedback is hard to do without understanding it. CI shows that checks passed, but not whether a generated refactor preserved behavior or whether an accountable human understood a security-sensitive change ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)). A checklist moves that reasoning cost to the submitter before review starts. The paper's term for the gap is reviewability debt: the cost transferred to reviewers when a PR looks complete but leaves intent, scope, validation, or ownership unresolved.

This mechanism is the authors' post hoc interpretation of self-reports, and the paper calls for vignette experiments that manipulate the signals directly. Reviewability debt is also an interpretive concept, not a measured quantity of reviewer time or defects ([arXiv:2610.11179v1](https://arxiv.org/abs/2610.11179v1)).

## When this backfires

- Small internal teams. When every author is a known colleague, the ownership gates are already met and a template adds ceremony.
- Authorship you cannot see. A gate keyed to AI authorship is skipped by contributors who do not disclose and burdens those who do. Apply one authorship-blind standard instead. Every gate in the survey is a reasonable gate for human PRs too.
- Newcomer-heavy projects. Issue-first discussion and a stricter bar raise the cost of a first contribution. The paper's fairness discussion warns that intake should preserve newcomer access.
- Fluent template answers. An agent can fill a checkbox as fluently as it writes a description. The field must ask for change-specific evidence, or it becomes another cheap signal.
- Low-risk changes. Full evidence bundles on docs or typo PRs waste the author's time, and reviewers learn to rubber-stamp the gate.
- Provenance objections. Gentoo forbids content created with NLP AI tools ([Gentoo AI policy](https://wiki.gentoo.org/wiki/Project:Council/AI_policy)), NetBSD presumes LLM output tainted ([NetBSD commit guidelines](https://www.netbsd.org/developers/commit-guidelines.html)), and QEMU declines contributions believed to derive from AI-generated content ([QEMU code provenance](https://www.qemu.org/docs/master/devel/code-provenance.html)). These bans rest on copyright, ethical, quality, and licensing concerns, so a stewardship trace does not answer them.
- Observed behavior may differ from stated intent. A behavioral study of Claude Code PRs found 83.8% accepted against 91.0% for human PRs, with rejections driven by project context such as alternative solutions or PR size rather than AI code flaws ([arXiv:2509.14745v3](https://arxiv.org/abs/2509.14745v3)). Reviewers may already handle agent PRs inside normal review, so the survey's willingness gaps may overstate the practical cost.

## Key Takeaways

- The survey names five conditions for review effort: bounded scope, project-grounded rationale, validation beyond CI, responsiveness, and post-merge ownership.
- CI-first (66.5%) and a clear description (56.9%) led the entry gates. Named ownership was a minority gate (41.8% and 32.2%).
- Authorship still cost 18 points on CI-passing docs and tests, so the finding does not say authorship stopped mattering.
- The evidence is self-reported scenario ratings from a non-probabilistic sample, with no outcome data. Pilot the checklist and measure reviewer time yourself.
- Match evidence to change type, and ask for specifics an agent cannot fill from a template.

## Related

- [Reviewer's Playbook for Agent-Authored PRs](reviewers-playbook-agent-authored-prs.md)
- [Explain-the-Change Review Gate](../workflows/explain-the-change-review-gate.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md)
- [Preempting Agentic PR Rejection by Failure-Mode Category](preempting-agentic-pr-rejection.md)

## Sources

- [Who Pays the Review Cost? (arXiv:2610.11179v1)](https://arxiv.org/abs/2610.11179v1)
- [On the Use of Agentic Coding: An Empirical Study of Pull Requests on GitHub (arXiv:2509.14745v3)](https://arxiv.org/abs/2509.14745v3)
- [Gentoo Council AI policy](https://wiki.gentoo.org/wiki/Project:Council/AI_policy)
- [NetBSD commit guidelines](https://www.netbsd.org/developers/commit-guidelines.html)
- [QEMU code provenance](https://www.qemu.org/docs/master/devel/code-provenance.html)
