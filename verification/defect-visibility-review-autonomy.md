---
title: "Defect Visibility as the Unsupervised Review Boundary"
term: "Defect-Visibility Review Routing"
description: "Diff-visible defects carried 2.6x the adjusted detection odds in CRBugBench while repository size carried none, so route unsupervised agent review by whether the evidence sits inside the diff."
aliases:
  - diff-visible defect routing
  - lights-off review scoping
  - defect visibility routing
tags:
  - testing-verification
  - code-review
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-13
maturity: emerging
---

# Defect Visibility as the Unsupervised Review Boundary

> Diff-visible defects carried 2.6x the adjusted detection odds of ones needing outside context in one review benchmark; repository size showed none.

Send a change to unsupervised agent review when it is narrowly scoped and low-consequence and the defect it would have to find is decidable from the diff. Send it to a human when confirming the defect needs project knowledge, a cross-file check, or a run, when the change is consequential, or when the concern is maintainability or project values. Repository size is not the dividing line. CRBugBench measured it as a covariate and found no significant effect once diff size was adjusted ([arXiv:2610.13668v1](https://arxiv.org/abs/2610.13668v1) §4.4).

## Conditions this rests on

Four limits decide whether the rule below applies to you.

- The authors scope unsupervised operation by consequence, which the regression does not recover (agents detect severe bugs better, OR=1.906): "The present evidence therefore supports 'lights-off' operation only for narrowly scoped, low-consequence PRs" (§5.1). Treat that as a second condition on the rule below.
- The benchmark scores recovery of known bugs and nothing else: "Our benchmark only measures review agents' bug detection capabilities. Our results should therefore be interpreted as recovery of known bugs rather than as overall review usefulness" (§4.2). No precision or developer-trust figure comes from this work.
- The effect sizes are associations: "Our observational regressions estimate adjusted associations, not causal effects" (same section). Matching is done by LLM judges, "which may be unreliable", mitigated with a three-model panel.
- The evidence is one benchmark in two portions, "1,000 review tasks across 98 open-source GitHub repositories, and 800 additional tasks from proprietary industry repositories at one large company". Results "may differ for smaller or younger projects, uncommon languages, generated or configuration-heavy code, and other review practices" (§4.2).

## What the regression found

Yang and colleagues modeled the probability that a review detected a bug using multivariable logistic regression over repository, pull request, and bug features. Significance markers follow the paper: `***` is p<0.001, `**` is p<0.01, `*` is p<0.05.

| Property of the change or bug | Adjusted odds ratio |
|---|---|
| Defect directly visible in the diff | 2.621 `***` |
| More severe bug | 1.906 `**` |
| More heterogeneous diff (several kinds of change) | 0.795 `*` |
| Larger diff | 0.591 `***` |
| Bug-fixing pull request | 0.521 `***` |
| Usability bug | 0.454 `***` |
| Portability bug | 0.523 (p=0.07) |
| Repository size, adjusted for diff size | none observed |
| Pull request language | none observed |

Agents "succeed more with bugs that are directly visible in the diff (OR=2.621, \*\*\*), compared to bugs that need additional project knowledge, cross-files check beyond the diff, or run-time checks" (§4.4).

That reading survives the industry result, which is easy to mistake for a repository-size effect. Detection fell by "up to 25.5%" (§4.3) on the proprietary portion, where the task population differs: internal pull requests "contain far fewer locally visible bugs (22.8% vs. 46.1% in GitHub tasks), but contain many more bugs that require project context understanding". Those percentages are shares of each task population, not detection rates. The authors find that "adjusting for bug visibility alone explains 20% of the performance gap" (§4.4), so distribution accounts for part of the drop and not all of it.

## Routing rule

- Estimate visibility forward from the change, because you cannot know the defect in advance. A small, single-purpose diff whose correctness is decidable from the lines it touches is the unsupervised case.
- Send breadth to a human. Large diffs, diffs mixing source with tests and config, and bug-fixing pull requests all carried lower detection odds after adjustment.
- Spend compute, not supervision, where the change is wide but local: "Small, homogeneous changes may be reviewed with a cheaper configuration, whereas large, heterogeneous PRs warrant stronger models, higher reasoning effort, comprehensive prompts, and careful human review" (§5.2).
- Keep a human on maintainability and project values. The paper reports a significant interaction between bug impact and reviewer identity, where "humans are much better (OR=2.702, \*) at catching maintainability issues than agent reviewers". The same comparison runs the other way on severity, where "humans are also worse at identifying more severe bugs (OR=0.450, \*) and reliability issues (OR=0.591, \*)", so this is a split of responsibility and not a human floor under every non-functional property. The paper reports no visibility-by-reviewer interaction.

## Why it works

Detection fails at diagnosis rather than retrieval, and diagnosis needs evidence the diff does not carry. The funnel is measured: "95.6% of agent executions inspect the file with defects, but only 80.2% produce a finding for that file, and 56.2% actually hit the bugs" (§4.5). Agents reach the defective file and then do not call the bug. They also stay inside a reading loop, where "reading and searching account for 75% of all turn mass (39% Read, 36% Probe), while running code accounts only for 8%". A defect whose confirmation needs a run has little path through that loop. The authors give the practitioner form: agents "struggle more when a correct judgment depends on project-specific knowledge, surrounding source files, or runtime evidence" (§5.2).

## When this backfires

- Your problem is comment volume. This benchmark measures no precision, so it says nothing about a team that already skips the agent's comments.
- Few of your defects are diff-visible. At 22.8% locally visible bugs, a visibility rule on the proprietary portion routes nearly everything to a human.
- You cannot estimate visibility before the review. The paper's labels were assigned against a bug already known, and a forward proxy built from change characteristics fails silently when it is wrong.
- The change argues its own correctness. In one Selenium task "all models endorsed the buggy condition because both the in-code comment and the PR description asserted the intended behavior that the code failed to implement" (§4.5).
- Your repositories sit outside the sample the authors describe.

## Key Takeaways

- Route unsupervised review on whether the defect's evidence sits inside the diff. Repository size showed no observed significant effect on detection once diff size was adjusted.
- Diff-visible defects carried an adjusted odds ratio of 2.621; usability bugs carried 0.454.
- Bug visibility alone explains 20% of the gap between the open-source and proprietary portions, so it is part of the up-to-25.5% drop rather than the whole of it.
- CRBugBench scores recovery of known bugs only. Take no precision or trust claim from it.

## Related

- [Scoring a Code Review Agent on an Open Benchmark Suite](open-code-review-benchmarks.md) — why an aggregate benchmark score does not predict misses in your own codebase
- [Risk-Based Task Sizing for Agent Verification Depth](risk-based-task-sizing.md) — the static file-risk alternative to routing on a property of the change
- [Task Category as the Security Review Routing Key](task-category-security-review-routing.md) — the same routing shape applied to security review depth
- [Review-Comment-Derived Benchmarks for Code Review Agents](review-comment-derived-benchmarks.md) — building the repository-specific evidence these authors recommend calibrating on
- [Transcript-Measured Review Coverage](transcript-measured-review-coverage.md) — deriving what a review actually inspected from the tool-call trace
