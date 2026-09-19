---
title: "Reading Copilot Feature Engagement by Its Threshold"
description: "The Copilot impact dashboard counts users who touched each feature on at least two days in 28. That is a floor on repeat use, not evidence of a habit."
aliases:
  - copilot_feature_engagement
  - users_in_phase_28d
  - Copilot feature engagement breakdown
tags:
  - copilot
  - human-factors
  - observability
last_reviewed: 2026-09-18
maturity: emerging
status: current
---

# Reading Copilot Feature Engagement by Its Threshold

> The Copilot feature engagement count reports repeat use at a two-day threshold, so read each figure as a floor rather than a habit.

On 17 September 2026 the Copilot impact dashboard began reporting how many active users "engaged with each included feature on at least two days during the 28-day period" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)). The threshold carries the new information. A seat count says a license exists, a request count says a surface was touched, and this counter says it was touched again.

## Three conditions before the number means anything

The panel is readable under three constraints, all of them stated by GitHub.

- Two days in 28 is 7% of the window, so treat the panel as a trial detector. The one field study that tested a recurrence bar defines retention as activity "on at least 5 of the 14 days beginning with their first use", a threshold "designed to separate 'tried and stayed' from 'tried and abandoned'" ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). Its model fits at a looser 3-of-14 too, and 3 of 14 is 21% of calendar days, three times GitHub's bar.
- The counts overlap. "A user can be counted under more than one feature" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)), so a ranking by share double-counts the multi-surface developers it claims to describe.
- Missing is not zero, in two places. `users_in_phase_28d` "is omitted when the phase population was not measured. A value of `0` means the phase was measured and had no users", and the `copilot_feature_engagement` object "can be absent or null when the calculation is unavailable" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)).

## What the breakdown enumerates

`totals_by_feature` splits engagement across seven features: code completion, agent edit, passive Copilot code review, active Copilot code review, Copilot cloud agent, Copilot CLI, and the Copilot app ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)). In the same entry, active code review "means a user manually requested a Copilot review or applied a Copilot review suggestion", while passive code review means Copilot "was automatically assigned to review the user's pull request without the user actively engaging with the review". The passive counter therefore fires without any act by the user it counts.

The same release added `users_in_phase_28d`, which reports "the full rolling 28-day population classified into each AI adoption phase as of that day", where the existing `total_engaged_users` "continues to only report users in the phase who were active that day" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)). That is the denominator an engagement rate per [adoption phase](cohort-segmentation-copilot-usage-metrics.md) needs. All of it is "not added to user-level reports", so enablement can target a lagging organization, never a lagging person.

## Why it works

First use and sustained use are separate phenomena, and their predictors can run in opposite directions. At Microsoft, prior IDE Copilot use raised the odds of trying Copilot CLI from 49% up to 83%, rising with days of prior use. Across those same groups the retention markers ran negative, between -12% and -15% ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). A counter that cannot tell a first touch from a second one answers the wrong half of that pair, and the enablement budget asks the other half. A day-count threshold is the cheapest instrument that separates them, and that study's robustness check shows the separation holds anywhere between 3 and 7 days of 14. GitHub's two-day bar performs it weakly.

## When this backfires

- Reading "engaged" as habitual. GitHub's own framing is that a feature is "becoming part of developers' regular workflows" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-copilot-impact-dashboard-now-shows-feature-engagement)). The threshold does not carry that.
- Running an enablement push across all seven surfaces at once. The one measured cross-surface result points the other way: heavier prior use of one surface predicted worse retention on another ([Murphy-Hill et al., arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). That association is not causal, and it is still the only evidence on the question.
- Treating one window as a level. Adoption at one 300-engineer deployment ran "4% engagement in month 1 to 83% peak usage by month 6, stabilizing at 60% active engagement" ([Kumar et al., arXiv:2509.19708v1](https://arxiv.org/abs/2509.19708v1)). One 28-day reading sits somewhere on that curve and cannot say where.
- Reading recurrence as benefit. Among 415 practitioners, frequent users reported faster completion and higher output, and those gains "were offset by increased code review burden, persistent cognitive load from output verification, and unchanged collaboration patterns" ([Afroz et al., arXiv:2510.24265v2](https://arxiv.org/abs/2510.24265v2)). The panel has no field for the offset.
- Using it as the only instrument. A survey drawing 2,989 developer responses exposed "conflicting perspectives on AI tool usefulness", and the paired interviews elicited factors including technical expertise and ownership of work ([Chen et al., arXiv:2602.03593v1](https://arxiv.org/abs/2602.03593v1)). No engagement counter carries those.
- Publishing the number as a target. Active code review counts a manually requested review, which a developer can request on two days without reading either result.

## Example

The field names and the arithmetic are real; the counts below are constructed to show the two readings.

**Before** — ranking the surfaces by share:

```text
agent edit               612 users   38%
code completion          540 users   34%
passive code review      410 users   26%   <- shares sum past 100%
active code review       180 users   11%
Copilot CLI               95 users    6%
```

**After** — rates against the phase population, with the overlap named:

```text
users_in_phase_28d                     1,600

agent edit               612 / 1,600 = 38% returned on a 2nd day
code completion          540 / 1,600 = 34%
active code review       180 / 1,600 = 11%
Copilot CLI               95 / 1,600 =  6%  <- weakest floor, enablement target
passive code review      410 / 1,600 = auto-assignment, not a user act

rows overlap: a user may appear under several features
```

The first form invents a share-of-usage split the overlapping counts cannot support, and promotes an administrator's auto-assignment setting into third place. The second reads each row as its own floor and names the weakest surface.

## Key Takeaways

- Query `totals_by_feature` for near-zero rows first. A surface almost nobody returned to is the one finding the two-day bar supports on its own.
- Divide by `users_in_phase_28d`, never by `total_engaged_users`, which counts only users active that day and moves independently of the numerator.
- Keep the passive code review row in its own column and label it a configuration signal.
- Map a null `copilot_feature_engagement` to unknown rather than 0, or a reporting gap renders as a decline.

## Related

- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — the `ai_adoption_phase` classification that `users_in_phase_28d` now supplies a full population for
- [Per-Agent-App Attribution in the Copilot Usage Metrics API](per-agent-app-attribution-copilot-metrics.md) — the other non-partitioning array in this API, where the residual comes from unidentified agents rather than from users counted twice
- [Reading a Vendor-Computed AI Coding ROI Dashboard](vendor-computed-roi-copilot-impact-dashboard.md) — the return-on-investment section of the same dashboard, and which half of its ratio is measured
- [Rolling Out CLI Coding Agents at Organization Scale](org-scale-cli-agent-rollout.md) — why a rollout tracks trials and sustained use as two numbers rather than one
- [Intervention Rate as a Diagnostic North Star, Not a Target](intervention-rate-diagnostic-north-star.md) — the general case of a diagnostic signal that breaks once it becomes a target
