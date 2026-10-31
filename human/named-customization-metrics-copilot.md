---
title: "Named Customization Metrics in the Copilot Usage Metrics API"
description: "The Copilot usage metrics API now prints the names your organization gave its customizations, under four conditions that decide whether a given name appears at all."
term: "named customization metrics"
aliases:
  - totals_by_skill named entries
  - configured name reporting
  - copilot customization name metrics
tags:
  - copilot
  - human-factors
  - observability
last_reviewed: 2026-10-25
maturity: emerging
status: current
---

# Named Customization Metrics in the Copilot Usage Metrics API

> GitHub now reports the names your organization gave its Copilot customizations, and four conditions decide whether a given name appears.

Read a named entry under four conditions: report day, reporting surface and version, name shape, and rank. A missing name does not establish disuse.

GitHub's 22 October release makes five arrays report configured customer names: `totals_by_skill`, `totals_by_custom_agent`, `totals_by_mcp`, `totals_by_slash_cmd`, and `totals_by_plugin`. It leaves `interaction_count` and `distinct_*_use_count` calculations unchanged ([GitHub Changelog, 2026-10-22](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)).

The change includes enterprise and organization per-user 1-day and 28-day reports, aggregate 1-day reports, and `day_totals` in aggregate 28-day reports. These are the four shapes the [September customization fields](anonymized-customization-metrics-copilot-cli.md) named. The October list says "including", so it does not establish that these are the only report shapes.

## The four conditions a name must pass

- Report day. "Names appear starting with report days processed after this release. Earlier days still show `other` or `custom`" ([October changelog](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)).
- Reporting surface and version. Coverage includes Copilot CLI interactive sessions and prompt mode, the Copilot app, SDK clients, and ACP integrations. Prompt mode, the app, and ACP require CLI 1.0.97 or later. SDK clients require SDK v1.0.21 or later. IDE integrations outside the Copilot SDK do not report names (same source).
- Name shape. Names are trimmed and limited to 128 characters. "Names that look like file paths stay grouped under `other` or `custom`" (same source).
- Rank. Each array includes up to 25 entries per record, increased from five. "Any remaining activity is combined into a trailing `other` entry" (same source).

Later report days meet the history condition without changing an integration. Upgrading clears a version floor only on a supported surface. It does not remove the non-SDK IDE exclusion. Name shape and rank require separate checks.

## One label, three documented causes

September grouped all customer-defined skills, agents, MCP servers, and plugins under `other` ([September changelog](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). October documents three reasons for residual grouping: an earlier report day, a path-shaped name, or activity beyond the entry cap. The residual now combines those causes.

The changelog does not state where unsupported-surface or below-version activity goes. It also warns that telemetry can undercount activity when clients are outdated or telemetry is blocked. Do not assume such activity appears under `other` or disappears entirely.

## What the documentation says about privacy

September said "To protect privacy, customer-defined names are not shown" ([September changelog](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). October reports names without a privacy rationale. It does give an exposure instruction: "Review names before sharing reports outside your organization" ([October changelog](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)).

Neither entry explains whether a name reveals anything about an individual. Neither establishes that reports are safe or unsafe to circulate. The review step remains the report holder's responsibility.

## Why it works

A named entry joins an interaction count to a configured customization. That lets administrators examine adoption of an internal skill, agent, or MCP server, the use GitHub describes in its October announcement. September's category bucket could not identify that item.

The conditions limit this join. Historical days, path-shaped names, and activity beyond the cap still contribute to residual entries. Named entries alone therefore need not sum to all activity. Distinct counts retain their earlier meaning and include items beyond the named list.

## When this backfires

- A trend crosses the release. A newly visible name can reflect changed reporting. Mark the release date before interpreting adoption.
- An IDE integration does not use the SDK. Upgrading its version alone does not establish coverage.
- A naming convention uses paths. Check configured names before treating absence as disuse.
- The inventory exceeds the cap. Inspect the residual alongside the named list.
- A report leaves the organization. Follow GitHub's name-review instruction before sharing it.

## Example

GitHub's documented routing gives three checks before a retirement decision ([October changelog](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)):

| Observed condition | What the announcement establishes |
|---|---|
| Earlier report day | Customer names remain grouped under `other` or `custom` |
| Path-shaped configured name | The name stays grouped even after the release |
| IDE integration outside the SDK | Names are not reported; the activity's destination is unspecified |

Check the report day, configured name, integration type, and applicable version outside the payload. A version check alone cannot settle the third row.

## Key Takeaways

- Store named and residual entries together with the report day.
- Compare distinct counts with named entries before treating the list as a complete inventory.
- Check the reporting surface first, then its version. Passing time clears no surface exclusion.
- The privacy explanation changed without a published resolution. Review names before sharing reports.

## Related

- [Anonymized Customization Metrics in the Copilot CLI](anonymized-customization-metrics-copilot-cli.md) — the September behavior this change supersedes, and the distinct-count reads that survive it
- [Per-Agent-App Attribution in the Copilot Usage Metrics API](per-agent-app-attribution-copilot-metrics.md) — the same API's other named breakdown, read under the four limits GitHub states for it
- [Reading a Client-Version Metric Dip as Lost Adoption](../patterns/anti-patterns/client-version-metric-dip-as-adoption-loss.md) — the version-floor condition as a standalone misreading, from an earlier release
- [Reading a Vendor-Computed AI Coding ROI Dashboard](vendor-computed-roi-copilot-impact-dashboard.md) — which decisions a first-party panel over this data can settle
