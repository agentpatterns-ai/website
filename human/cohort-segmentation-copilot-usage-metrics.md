---
title: "Cohort Segmentation in the Copilot Usage Metrics API"
description: "The May 2026 Copilot Usage Metrics API exposes four AI-adoption phases per user — a diagnostic primitive that recovers the conditional distribution behind a misleading aggregate, and maps directly onto adoption interventions."
aliases:
  - copilot ai adoption phases
  - totals_by_ai_adoption_phase
  - copilot cohort metrics
tags:
  - copilot
  - human-factors
last_reviewed: 2026-05-30
status: current
---

# Cohort Segmentation in the Copilot Usage Metrics API

> The Copilot Usage Metrics API now sorts each engaged user into one of four AI-adoption phases, recovering the segmented shape aggregate utilization hides.

On 29 May 2026 the Copilot Usage Metrics API gained `ai_adoption_phase` (user-level) and `totals_by_ai_adoption_phase` (enterprise/org-level), keyed to a four-phase classification over a rolling 28-day window ([GitHub Changelog, 2026-05-29](https://github.blog/changelog/2026-05-29-copilot-usage-metrics-api-adds-cohorts-for-ai-adoption)).

## The Four Phases

| Phase | Name | Definition |
|---|---|---|
| 0 | No cohort | Did not meet engagement criteria in the 28-day window |
| 1 | Code-first | Code completion and/or IDE agent mode |
| 2 | Agent-first | A single GitHub-based agent surface |
| 3 | Multi-agent | Two or more agent surfaces, or the new Copilot app |

Each entry carries a `version` field (starts at `v1`) so logic can evolve without breaking history. `totals_by_ai_adoption_phase` reports averages *per user inside the phase* — engaged users, interactions, completion/acceptance activity, lines added/deleted, PRs created/merged/reviewed, median time-to-merge ([GitHub Changelog, 2026-05-29](https://github.blog/changelog/2026-05-29-copilot-usage-metrics-api-adds-cohorts-for-ai-adoption)). Averages, not sums — otherwise phase size dominates phase intensity.

## When This Applies

The cohort layer is only diagnostic at meaningful scale:

- **~25+ engaged users per phase.** Below that, one developer adopting Copilot Workspace can flip an org-level "Multi-agent growth" headline.
- **≥60 days since rollout.** Earlier, cohort transitions are onboarding artefacts (Phase 0 → 1 → 2 happens mechanically in month one) — not attributable to interventions.
- **Outcome telemetry wired alongside.** Pass rate, revision rate, cost per merged PR decide whether a phase shift mattered. Without them the dashboard is a [vanity surface](../anti-patterns/agent-headcount-vanity-metric.md).

## Mapping Phases to Interventions

Each phase has a different intervention surface — the reason to break adoption out:

| Phase | Likely cause of stall | Intervention |
|---|---|---|
| 0 | Dormant licence, policy block, refusal | Triage before reclaiming — causes diverge ([AI Adoption Footprint](ai-adoption-footprint.md)) |
| 1 | Has not crossed the agent-supervision skill gate | Pair sessions, agent-mode demos, low-stakes first tasks |
| 2 | Single surface is enough for current work | Multi-surface onboarding only if work requires it |
| 3 | Power user — retention question | Instrument outcomes, protect from churn, mine for patterns |

Phase 0 does **not** equal "dormant." It is "did not meet engagement criteria in 28 days," which mixes non-users, policy-blocked users, vacationers, and users whose work happened to skip tracked surfaces.

## Why It Works

Aggregate utilization — "60% active this month" — is a mean over a distribution that is almost always bimodal in engineering orgs: a small power-user mode, a long middle, a dormant tail ([Userpilot 2026](https://userpilot.com/blog/user-adoption-metrics/), [AI Adoption Footprint](ai-adoption-footprint.md)). Means over bimodal distributions hide the modes, and the modes are where interventions land. A 60% headline is consistent with a 20%-power / 40%-dormant org and with a uniform-60%-medium-use org — same number, opposite playbooks.

Cohort segmentation recovers the conditional `P(activity | phase)` instead of the marginal `P(activity)` — the *actionable* shape ([Zigpoll 2026](https://www.zigpoll.com/content/9-ways-optimize-cohort-analysis-techniques-developertools)). The API's depth-of-surface framing aligns with the capability-layering mechanism in [AI Adoption Footprint](ai-adoption-footprint.md): each phase boundary is a skill gate (autocomplete → agent supervision → multi-agent), so per-phase averages reveal *which* gate is choking adoption.

## When This Backfires

- **Small teams or fresh rollouts.** The 28-day window plus small per-phase samples produce noise that reads as trend. Below the thresholds above, ignore the split.
- **Phase 3 treated as a goal.** Grade enablement on "% in Phase 3" and teams Goodhart: open Workspace once, install the app, touch two surfaces — Phase 3 climbs while throughput stays flat. The [Agent Headcount Vanity Metric](../anti-patterns/agent-headcount-vanity-metric.md) shape on a different axis.
- **Single-surface shops by policy.** Regulated environments that disable agent surfaces have a structural Phase 1 ceiling. Reading the distribution as adoption maturity there is a category error.
- **Replacement for outcome telemetry.** Cohort distribution decides *where* to invest; outcome metrics decide *whether* it worked. Reporting Phase 3 growth alone repeats the DORA-as-vanity drift ([Larridin: Why DORA Metrics Break in the AI Era](https://larridin.com/developer-productivity-hub/why-dora-metrics-break-ai-era)).
- **Depth confused with productivity.** Time savings plateaued around four hours per week even as adoption climbed from ~50% to 91% in DX 2025 ([Rob Bowley on DX 2025](https://blog.robbowley.net/2025/11/05/findings-from-dxs-2025-report-ai-wont-save-you-from-your-engineering-culture/)). A higher Phase 3 share is not a higher-productivity org.

Cohort segmentation is the right diagnostic primitive for adoption *shape*; it is the wrong target for adoption *success*.

## Example

A 200-engineer org sees `weekly_active_users / engaged_users = 0.62` and reports "62% weekly active." After enabling the cohort fields, the same month's `totals_by_ai_adoption_phase` resolves to:

```text
Phase 0:  48 users   (24%)   — needs refusal / policy / dormancy triage
Phase 1: 110 users   (55%)   — completion + IDE agent only
Phase 2:  30 users   (15%)   — one agent surface
Phase 3:  12 users    (6%)   — multi-agent / Copilot app
```

The 62% headline is consistent with this org and with a uniform-60%-medium-use org, but the intervention reads diverge sharply: this org needs Phase 0 triage (24% is too large to be vacationers) and a Phase 1 → 2 skill-gate programme (the chat-tool middle from [AI Adoption Footprint](ai-adoption-footprint.md) is 55% of the population). Phase 3 growth is not the lever; the Phase 1 boundary is.

## Key Takeaways

- The Copilot API now exposes `ai_adoption_phase` (user) and `totals_by_ai_adoption_phase` (org/enterprise) over a 28-day window, with four phases keyed to surface depth.
- Cohort segmentation is a diagnostic primitive: it recovers the conditional `P(activity | phase)` that an aggregate "% active" headline averages away.
- Each phase maps to a distinct intervention; Phase 3 is a descriptor, not a target.
- Apply at scale only: ~25+ users per phase, ≥60 days post-rollout, outcome telemetry wired alongside.
- Without outcome metrics, cohort dashboards degenerate into the same vanity surface that headcount and aggregate utilization already produce.

## Related

- [AI Adoption Footprint: The Segmented Shape of Engineering Orgs](ai-adoption-footprint.md) — the underlying segmented-distribution mechanism cohort segmentation operationalises.
- [Agent Headcount as a Vanity Metric](../anti-patterns/agent-headcount-vanity-metric.md) — the Goodhart failure mode Phase 3 will exhibit if treated as a target.
- [The Productivity-Experience Paradox in AI-Assisted Development](productivity-experience-paradox.md) — why depth-of-use can rise while developer experience and outcomes diverge.
- [Copilot vs Claude Billing Semantics](copilot-vs-claude-billing-semantics.md) — the other side of Copilot-specific instrumentation; cost telemetry that pairs with the cohort distribution.
