---
title: "Reading a Vendor-Computed AI Coding ROI Dashboard"
description: "A first-party ROI panel meters the cost side of the ratio and models the value side — trust the metered cost figure and override the throughput figure with a locally-derived one."
aliases:
  - "Copilot impact dashboard ROI section"
  - "vendor-computed ROI for AI coding tools"
tags:
  - copilot
  - human-factors
  - cost-performance
last_reviewed: 2026-08-08
maturity: emerging
status: current
---

# Reading a Vendor-Computed AI Coding ROI Dashboard

> A vendor-computed ROI dashboard meters the cost side of the ratio and models the value side; trust the first, override the second.

The return-on-investment section of the Copilot impact dashboard reports three numbers per adoption cohort: cost per developer per month "derived from actual AI credit consumption", that cost as a percentage of developer compensation, and pull requests per developer per month ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)). One of the three is measured. Read the panel by splitting it along that line.

## What the panel reports

The cards are keyed to the same `ai_adoption_phase` cohorts as the Copilot usage metrics API, computed over a rolling 28-day window ([GitHub Changelog, 2026-07-22](https://github.blog/changelog/2026-07-22-new-copilot-usage-metrics-impact-dashboard/)). The section sets an early-adoption cohort beside an agent-first cohort, and a salary selector picks the compensation band the cost figures recalculate against. No division happens on screen: the reader supplies the ratio and the theory of what a merged pull request is worth.

## The measured half and the modeled half

Cost per developer per month comes from metered credit consumption, so it answers a question buyers previously had to estimate: what this costs per person in the cohorts that use it hardest. GitHub still asks readers to "treat these metrics as directional" ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)).

The value half did not improve. Pull requests per developer per month is the same activity proxy it always was, and the salary selector is "a modeling input rather than actual payroll data" ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)). Two properties weaken the throughput figure further:

- The comparison is cross-sectional. Cohort membership is self-selected along the same axis as the outcome: at Microsoft, retention of CLI coding agents tracked baseline coding activity rather than demographics ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). The agent-first cohort was the higher-throughput cohort before it became agent-first.
- Task mix moves the number independently of the tool. Across 7,156 agent pull requests, documentation tasks were accepted at 82.1% against 66.1% for new features, a gap wider than the variance between agents ([Pinna et al., arXiv:2602.08915v2](https://arxiv.org/abs/2602.08915v2)).

## When the vendor figure settles the question

Use the panel unmodified when the decision turns on cost:

- Renewal and budget scale. When metered spend lands at a low single-digit percentage of payroll, error in the throughput term cannot flip the renewal.
- Spend shape. Which cohorts burn credits, and how steeply cost climbs with adoption depth, are now observations instead of guesses.
- Checking a local model. A hand-built ROI spreadsheet whose cost term disagrees with metered consumption has a bug in the spreadsheet.

The direction of the gap holds up independently. Across tens of thousands of Microsoft engineers, adopters merged roughly 24% more pull requests than they would have otherwise, persisting over four months ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). That is a counterfactual estimate rather than a cohort mean; [Rolling Out CLI Coding Agents at Organization Scale](org-scale-cli-agent-rollout.md) covers what it licenses.

## When to override the throughput half

Replace the pull-request term with a locally derived value term whenever the decision turns on value: team-level staffing, per-team budget allocation, or any argument that adoption depth caused the gap. [Human-Equivalent Hours](human-equivalent-hours-agent-productivity.md) is the buyer-side construction of the same ratio, converting agent output into the hours finance already uses. Pair either figure with a downstream signal such as review time or revert rate before reading a gap as value.

## Why it works

The panel collapses uncertainty on exactly one side of the ratio and leaves the other side untouched. GitHub bills the credits, so cost per developer is an observation; the compensation band stays an input the buyer chose, and the pull-request count stays a proxy the field already distrusts ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)). That asymmetry predicts which decisions the panel can close: anything dominated by cost uncertainty is answerable from metered data, and anything dominated by value uncertainty sits where it sat before the section shipped.

Measurement frameworks pair outcome-oriented north-star metrics with diagnostic submetrics rather than promoting a submetric to the headline ([Houck et al., arXiv:2605.04259](https://arxiv.org/abs/2605.04259)). A cohort card is a diagnostic submetric rendered where a north star belongs.

## When this backfires

- Small per-cohort populations. Cards report per-user averages inside a phase over a rolling 28-day window ([GitHub Changelog, 2026-07-22](https://github.blog/changelog/2026-07-22-new-copilot-usage-metrics-impact-dashboard/)). With a handful of engineers in a phase, one person's sprint moves the mean and a month-over-month delta is noise.
- Organizations already saturated on AI IDEs. A staggered difference-in-differences study with matched controls found large velocity gains only where agents were the first AI tool in a project; repositories with prior AI IDE use saw "minimal or short-lived throughput increases" ([Agarwal et al., arXiv:2601.13597v2](https://arxiv.org/abs/2601.13597v2)). The card still renders a gap.
- Quality cost carrying the decision. The same study measured static-analysis warnings up about 18% and cognitive complexity about 39%, persisting after the velocity advantage faded ([Agarwal et al., arXiv:2601.13597v2](https://arxiv.org/abs/2601.13597v2)). The panel has no field for that debit.
- Policy-constrained organizations. Where agent surfaces are disabled by policy, phase membership records what compliance permits, so the gap measures the policy rather than the tool.
- Promotion of the figure to a target. Pull requests per developer per month rises when work is sliced more finely, and agent tooling makes slicing cheap. [Cohort segmentation](cohort-segmentation-copilot-usage-metrics.md) flags the same trap for adoption phases, and [stakeholder-trust evals](../workflows/stakeholder-trust-evals-observability.md) flags it for composite quality scores.

## Example

A 300-engineer organization opens the ROI section during renewal planning. The card figures below are illustrative rather than GitHub-published numbers. Two ways to read the same two cards:

**Before** — treating the card as a ratio:

```text
Code-first cohort:    $41/dev/mo    0.4% payroll    4.1 PRs/dev/mo
Agent-first cohort:  $138/dev/mo    1.3% payroll    5.6 PRs/dev/mo

Read:     "agent-first ships 37% more PRs for 0.9% more payroll"
Decision: move every team to agent-first, fund it from open headcount
```

**After** — splitting the card along the measured line:

```text
Trust as measured:
  $138/dev/mo in the agent-first cohort, 1.3% of payroll
  -> renewal is not close; fund it

Do not trust as causal:
  the 1.5 PR/dev/mo gap is a cross-sectional cohort difference
  -> do not restaff teams on it

Override with a local value term:
  human-equivalent hours on PR-gated sessions,
  paired with review time and revert rate
```

Reading the card as a ratio moves headcount on a number the vendor itself labels directional. Splitting it closes the renewal with the metered half and sends the staffing question to a figure built from the organization's own outcomes.

## Key Takeaways

- The ROI section reports cost per developer per month from metered credit consumption, that cost against a chosen compensation band, and pull requests per developer per month ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)). It does not divide them for you.
- The cost half is measured. The value half is the same activity proxy as before, and the salary selector is a modeling input rather than payroll data.
- Cohort cards compare self-selected groups. Retention tracked baseline coding activity, so the agent-first cohort was already the higher-throughput cohort ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)).
- Use the panel unmodified for renewal-scale and spend-shape decisions. Override the throughput term for team-level staffing or any causal claim.
- The costs it cannot see are real: static-analysis warnings up about 18% and cognitive complexity about 39% after agent adoption, persisting after velocity gains fade ([Agarwal et al., arXiv:2601.13597v2](https://arxiv.org/abs/2601.13597v2)).

## Related

- [Human-Equivalent Hours for Autonomous Coding Agent Productivity](human-equivalent-hours-agent-productivity.md) — the buyer-side construction of this same ratio, and the value term to substitute when the vendor's proxy will not carry the decision
- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — the adoption-phase classification the ROI cards are keyed to, and why a phase is a descriptor rather than a target
- [Rolling Out CLI Coding Agents at Organization Scale](org-scale-cli-agent-rollout.md) — the Microsoft rollout evidence behind the throughput lift, and the conditions that make it observational
- [Copilot vs Claude Billing Semantics for Enterprise Teams](copilot-vs-claude-billing-semantics.md) — the credit-billing mechanics the panel's metered cost figure is drawn from
- [Stakeholder Trust Through Evals and Observability](../workflows/stakeholder-trust-evals-observability.md) — the Goodhart failure a single stakeholder-facing score invites once it becomes a target
