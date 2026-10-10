---
title: "Reading a Client-Version Metric Dip as Lost Adoption"
description: "A step-shaped fall in Copilot agent metrics can come from an IDE release, not developer behavior. GitHub cannot backfill the lost data, so check client versions before you act."
term: "Client-Version Metric Dip"
aliases:
  - client-version measurement artifact
  - telemetry attribution break
  - adoption dip misread
tags:
  - anti-pattern
  - human-factors
  - observability
  - copilot
last_reviewed: 2026-10-09
maturity: emerging
---

# Reading a Client-Version Metric Dip as Lost Adoption

> A Copilot agent metric dip can come from a client release that changed what the IDE reports, and GitHub cannot recover the data.

Read a falling Copilot agent curve as a measurement question first when three conditions hold: the drop is a step, it lines up with an IDE or extension release, and it shows in client-only fields while server-side active-user counts hold steady. Under those conditions, the cause may be telemetry attribution and not developer behavior. A gradual decline across every IDE version fits disengagement better, and the measurement explanation would delay the real response.

## The incident

In October 2026 GitHub reported that several IDEs had moved Copilot agent sessions to the Copilot SDK. Those sessions "didn't identify which IDE they came from, so usage metrics couldn't attribute them correctly." Most of that activity was left out of reports, and some was counted as Copilot CLI activity ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)).

Teams saw agent activity and agent lines of code fall while Copilot usage kept growing. Only IDE versions that use the SDK for agent mode are affected, so developers on earlier versions were still counted (same source).

## What the error looks like

The error has two signs in the reports:

- Affected IDEs undercount agent interactions and agent lines of code, for example `loc_added_sum` and `loc_deleted_sum` for `agent_edit`. This applies to enterprise, organization, and user reports, on both 1-day and 28-day windows.
- Copilot CLI metrics may be inflated, because some activity from other SDK-based clients was counted as CLI activity.

Billing is not affected. The issue changed how agent activity was attributed in usage metrics, not what GitHub charged (same source).

## The loss is permanent

GitHub states: "We can't backfill missing data." Activity from affected versions carries no IDE identifier, so no later join can attribute it. Earlier CLI metrics cannot be corrected either, because that activity cannot be separated from real CLI use. GitHub expects a gradual recovery as developers update, "rather than a single jump" (same source).

Knowing the dip is an artifact explains the gap but does not fill it. A trend-based return-on-investment case that spans the affected window stays wrong.

## How to check

Most detailed usage metrics (feature, language, model, and lines-of-code breakdowns) come from telemetry that each IDE sends. GitHub also records server-side data, which "reliably shows who was active, but it can't see what happens in the editor" (same source). The usage metrics documentation confirms that most metrics come from client-side IDE telemetry ([GitHub Docs](https://docs.github.com/en/copilot/concepts/billing-and-usage/copilot-usage-metrics/copilot-metrics#which-usage-is-included)).

When the two sources disagree, GitHub says the gap is usually on the client side: telemetry turned off, a proxy or firewall blocking the endpoint, an out-of-date IDE or extension, a client that changed how it sends telemetry, or a client that sends none (same source).

Run the check in this order:

1. Compare the dip with server-side active users. A client-only drop with steady active users points at measurement.
2. In per-user reports, read `last_known_ide_version` and `last_known_plugin_version` under `totals_by_ide`.
3. Group users by those versions and compare the dip cohort with the rest.
4. Check whether the drop starts at an IDE release date.

## Fixed versions

GitHub's table, as published on 2026-10-06 and sure to go stale:

| IDE | Fixed version | Status on 2026-10-06 |
|---|---|---|
| Visual Studio Code | 1.139.0 and later | Available |
| Visual Studio | 18.12 | Expected in October 2026 |
| JetBrains IDEs | Next plugin release | Expected by late October 2026 |
| Eclipse | Next plugin release | Expected by November 2026 |
| Xcode | Next plugin release | Expected by November 2026 |

If you manage IDE versions centrally, GitHub suggests moving developers directly to the fixed versions, because activity on an affected version "can't be recovered later" (same source).

## Why it works

The attribution key, which IDE sent the session, lives in the client payload. When a client release changed the transport without that key, the server could not place the events, so they dropped out or landed under CLI. Because nobody recorded the key, nothing can restore it afterward ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)). Recovery follows the IDE update rollout, not a server deployment.

Twyman's law supplies the prior: surprising movements in data are more often measurement errors than real changes of the same size ([Wikipedia](https://en.wikipedia.org/wiki/Twyman%27s_law)).

Measurement changes also move numbers up. In June 2026 GitHub began counting any active user it could confirm server-side who client telemetry had missed, which raised daily active user coverage with no change in behavior ([GitHub Changelog, 2026-06-15](https://github.blog/changelog/2026-06-15-copilot-usage-metrics-now-include-more-of-your-active-users/)). Check step changes in either direction.

## When this backfires

- The dip is gradual and spreads across all IDE versions, or it also appears in server-side active-user counts. The measurement explanation does not fit, and defaulting to it delays a real response. Sentiment can fall: the 2025 Stack Overflow survey reports positive sentiment toward AI tools at 60%, down from more than 70% in 2023 and 2024 ([Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/ai)). That figure measures sentiment, not usage.
- The affected cohort is pinned to older IDE versions. GitHub says developers on earlier versions "are still counted", so this bug does not explain their dip.
- Most agent work runs in Copilot CLI. CLI numbers in the window may be inflated, so the growth signal on that surface is also suspect.
- The team is small, with no version control over IDEs. A noisy curve cannot show a step change, so the shape cannot test the hypothesis.
- Measurement-first becomes a standing excuse. A team that blames telemetry for every dip stops seeing real disengagement. Run the version check and talk to developers at the same time, and act on whichever answers first.

## Key Takeaways

- A step-shaped drop in client-only fields, coinciding with an IDE release while server-side active users hold, points at measurement.
- GitHub cannot backfill the October 2026 gap, and CLI history in that window cannot be corrected.
- The `last_known_ide_version` field in per-user reports lets you split the dip cohort from the rest.
- Update affected IDEs fast: each day on an affected version is data that never returns.
- A gradual, cross-version decline is still a behavior question.

## Related

- [Cohort Segmentation in the Copilot Usage Metrics API](../../human/cohort-segmentation-copilot-usage-metrics.md)
- [Per-Agent App Attribution in Copilot Metrics](../../human/per-agent-app-attribution-copilot-metrics.md)
- [Vendor-Emitted Telemetry Signal Tiers](../../observability/vendor-emitted-telemetry-signal-tiers.md)
- [Agent Headcount as a Vanity Metric](agent-headcount-vanity-metric.md)
- [Perceived Model Degradation](perceived-model-degradation.md)
