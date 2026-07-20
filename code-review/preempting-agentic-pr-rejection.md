---
title: "Preempting Agentic PR Rejection by Failure-Mode Category"
term: "Preempting Agentic PR Rejection"
description: "A 14-reason taxonomy of why agent-authored fix PRs get rejected — and which preemption practices actually move which categories of failure."
tags:
  - code-review
  - arxiv
  - tool-agnostic
aliases:
  - Agentic Fix Rejection Taxonomy
  - Why Agent Fix PRs Get Rejected
last_reviewed: 2026-06-14
maturity: emerging
---

# Preempting Agentic PR Rejection by Failure-Mode Category

> A 14-reason rejection taxonomy explains why 46% of agentic fix PRs fail, and only implementation and CI categories respond to preemption prompts.

## The rejection taxonomy

Across 3,225 fix pull requests from Copilot, Devin, Cursor, and Claude in the AIDev dataset, 46.41% were rejected. A qualitative two-rater study of a representative 306-PR sample (95% CI, Cohen's κ = 0.605) sorts the reasons into four categories and 14 specific causes ([arXiv:2606.13468](https://arxiv.org/abs/2606.13468)).

| Category | Share of sample | Specific reasons (share of sample) |
|----------|-----------------|------------------------------------|
| Relevance of Fix | 24.2% | Inactivity 17.3%, Superseded 5.9%, Low priority 1.0%, Architecture change 0.3%, Test PR 0.3% |
| Implementation Issues | 10.1% | Incorrect fix 5.6%, Wrong approach 2.6%, Ambiguity 0.7%, Insufficient 0.7%, Wrong repo 0.7% |
| Provider-Related | 8.5% | Agent failure 7.5%, Rate limit 1.0% |
| Technical Issues | 7.2% | CI failure 6.9%, Breaking change 0.3% |
| Unclassified | 49.3% | No explicit reviewer rationale in the PR thread |

The unclassified bucket is large because rejected agent-authored PRs often lack reviewer feedback. A companion study of 654 rejected PRs across five agents finds that 67.9% of rejections carry no explicit reviewer comment ([arXiv:2602.04226](https://arxiv.org/abs/2602.04226)).

## What the categories mean for preemption

The four categories have different causal roots, so preemption prompts only move some of them. The paper recommends three practices, each targeting a specific bucket ([arXiv:2606.13468](https://arxiv.org/abs/2606.13468)):

1. Approach hints and do-not constraints in the agent instruction file (for example, `.github/copilot-instructions.md`, `AGENTS.md`) encode the team's implicit conventions that reviewers would otherwise enforce. This targets Implementation Issues.
2. CI validation instructions tell the agent how to run tests and confirm the fix without introducing breaking changes. This targets Technical Issues.
3. Task prioritization before dispatch filters out low-priority, superseded, or stale-on-arrival issues. This targets the Low-priority and Superseded sub-reasons under Relevance of Fix.

Inactivity (17.3% of the sample, the single largest cause) is a workflow-attention failure, not a fix-content failure, so no prompt change reduces it. Provider-Related rejections (agent failure 7.5%, rate limit 1.0%) are infrastructure failures, and no prompt addresses them.

## Why it works

Reviewers reject implementation-bucket fixes because the agent ignored unwritten team conventions that it could not infer from the issue text alone: style rules, architectural choices, "we don't use library X here," and test expectations. Encoding those conventions in the instruction file gives the agent the same implicit knowledge a new human contributor would learn from a senior engineer's pre-PR review. The paper names this mechanism in its Implications section: developers should "provide guidance on how to perform the fix or provide guidance on what approaches are not acceptable in the agent instruction file" ([arXiv:2606.13468](https://arxiv.org/abs/2606.13468)). The mechanism matches the [Implicit Knowledge Problem](../patterns/anti-patterns/implicit-knowledge-problem.md) anti-pattern: agents fail when the team's conventions are nowhere in the artifacts the agent reads.

## When this backfires

Preemption prompts target only the Implementation and Technical-Issue buckets, roughly 17 percentage points of the rejection rate. The remaining 30 or so points either resist prompt intervention or need workflow-side changes:

- Greenfield or single-purpose repos without an established convention set: the instruction file has nothing to encode beyond generic advice, and authoring it costs more than the rejections it prevents.
- Silent-reject reviewers: 67.9% of rejected PRs carry no reviewer feedback ([arXiv:2602.04226](https://arxiv.org/abs/2602.04226)), so instructions cannot address rejection reasons the reviewer never states.
- Inactivity rejections (17.3% of the sample): reviewer attention and triage cadence drive these, not PR content, so preemption shifts only the workflow side.
- Provider-side rejections (agent failure 7.5%, rate limit 1.0%): no prompt can stop the agent from going down or running out of quota.
- Low-priority and Superseded fixes: a task-routing problem, not a fix-quality problem. A better fix does not change the outcome, because the issue should not have gone to an agent at all. See [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) for the productivity-paradox framing.
- Different sampling, different headline: a separate empirical study of fix-related PRs measures a 65% merge rate (Codex 81.6%, Copilot 42.4%, Devin 42.9%) on a different sample ([arXiv:2602.00164](https://arxiv.org/pdf/2602.00164)). The 46.41% rejection figure is specific to AIDev's fix-PR slice, so treat the headline as a calibration target, not a universal constant.

The paper measures rejection causes, not the causal effect of any preemption intervention. No study yet measures how much adding `.github/copilot-instructions.md` reduces the rejection rate. The taxonomy motivates the practice well, but an A/B comparison has not validated it.

## Example

The paper's three preemption practices translate to a concrete artifact layout. GitHub Copilot's [repository custom instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) file (`.github/copilot-instructions.md`) is the documented surface for the first practice, and the paper recommends it by name ([arXiv:2606.13468](https://arxiv.org/abs/2606.13468)).

A preemption-shaped instruction file carries three load-bearing sections.

```markdown
## Approach hints

- Prefer minimal-diff fixes; do not refactor adjacent code in the same PR.
- Address the underlying cause, not the symptom.

## Approaches to avoid

- Do not add new dependencies without an issue thread approving them.
- Do not modify CI configuration to make tests pass.

## Validation before opening a PR

- Run `<project test command>` and confirm the previously failing test now passes.
- Run `<project lint command>` and confirm no new warnings.
```

The Approach-hints and Approaches-to-avoid blocks target Implementation Issues; the Validation block targets Technical Issues. Nothing in the file addresses Inactivity, Superseded, or Provider-Related failures — those need workflow-side or infrastructure changes.

## Key Takeaways

- 46.41% of agent-authored fix PRs in the AIDev sample are rejected; the reasons cluster into 14 specific causes across four categories.
- Implementation Issues (10.1%) and Technical Issues (7.2%) are the buckets that respond to preemption prompts — roughly 17 percentage points of the rejection rate.
- Inactivity (17.3%) is the single largest sub-reason and is a workflow-attention failure, not a content failure.
- 67.9% of rejected PRs lack explicit reviewer feedback, so the prescription set is grounded on a minority of cases.
- Preemption practices — approach hints, CI validation instructions, pre-dispatch prioritization — target specific buckets; treat them as partial mitigations, not universal merge-rate boosters.

## Related

- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — the productivity-paradox framing and AIDev merge-rate gap that motivates the rejection-cause study
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — reviewer-composition effect on merge outcomes, the complementary axis to the rejection-reason taxonomy
- [PR Description Style as a Lever](pr-description-style-lever.md) — how PR description structure affects merge outcomes, an adjacent preemption lever
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — reviewer engagement as the strongest merge predictor, the back-end counterpart to preemption
- [Implicit Knowledge Problem](../patterns/anti-patterns/implicit-knowledge-problem.md) — the underlying anti-pattern preemption prompts target

## Sources

- [arXiv:2606.13468](https://arxiv.org/abs/2606.13468) — Abujadallah, Arabat, Sayagh (2026): "Understanding the Rejection of Fixes Generated by Agentic Pull Requests — Insights from the AIDev Dataset" (MSR '26)
- [arXiv:2602.04226](https://arxiv.org/abs/2602.04226) — companion study of 654 rejected PRs across five agents: 67.9% lack reviewer feedback; seven rejection modes occur only in agent-authored PRs
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — AIDev dataset paper, the upstream source for both studies
- [arXiv:2602.00164](https://arxiv.org/pdf/2602.00164) — companion empirical study with a 65% merge rate on a different sample, illustrating the sample-dependence of the headline figure
