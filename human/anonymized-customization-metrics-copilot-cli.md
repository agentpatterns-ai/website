---
title: "Anonymized Customization Metrics in the Copilot CLI"
description: "Before the 22 October 2026 release the Copilot usage metrics API counted CLI customization use but withheld the names you wrote, so it could not tell you which customization to retire."
term: "anonymized customization metrics"
aliases:
  - totals_by_custom_agent
  - distinct_skill_use_count
  - copilot cli customization metrics
tags:
  - copilot
  - human-factors
  - observability
last_reviewed: 2026-10-25
maturity: emerging
status: current
---

# Anonymized Customization Metrics in the Copilot CLI

> Before the 22 October 2026 release the Copilot usage metrics API counted how often CLI customizations ran without naming any customization your organization wrote.

On 22 October 2026 the five `totals_by_*` arrays began to "show the configured name of a customer-defined item instead of `other` or `custom`" ([GitHub Changelog, 2026-10-22](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)). The anonymization below holds for earlier report days, and later only where a documented condition still groups an item (see [named customization metrics](named-customization-metrics-copilot.md)). The counts "are calculated the same way as before" (same source).

On 17 September 2026 the Copilot usage metrics API gained ten fields for Copilot CLI customizations: five arrays listing "up to five items with the most recorded activity" with an `interaction_count` each, and five fields that "count the number of different items used" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). Neither half named anything your team wrote. "To protect privacy, customer-defined names are not shown. Skills, custom agents, MCP servers, and plugins are grouped under `other`", and customer-defined slash commands appeared under `custom` (same source). For that period the payload said how much customization happened and how varied it was, never which of your files earned its maintenance.

## What the ten fields carry

| Field | Counts | Resolution |
|---|---|---|
| `totals_by_skill`, `totals_by_slash_cmd`, `totals_by_plugin` | Invocations | Top five, yours merged |
| `totals_by_custom_agent` | Custom agent starts | Top five, yours merged |
| `totals_by_mcp` | Connect and reconnect attempts | Top five, yours merged |
| The five `distinct_*_use_count` fields | Different items used | Whole inventory |

They appear in "enterprise and organization per-user and aggregate 1-day reports, per-user 28-day reports, and the `day_totals` entries in aggregate 28-day reports" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)).

## The retirement decision has no join key

Retiring a customization acts on one file, and for customer-defined items the report's finest resolution is one entry per category. A falling `other` count fits every agent losing a little use, or one dying while another grows.

No array counts instruction files such as `AGENTS.md` or `.github/copilot-instructions.md` ([GitHub Changelog, 2025-08-28](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/)). They load into context rather than run, so there is no invocation event to meter.

## What the fields do settle

GitHub says administrators can "identify which Copilot CLI customizations are gaining traction, find enablement gaps, and focus investment on automations that developers find valuable" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). Three reads survive the anonymization.

- Inventory breadth over time. The distinct counts include items outside the top five, and in an aggregate report "each item used by anyone in the enterprise or organization counts once, not once per user" (same source). Track the trend, not the level.
- Enablement gaps per person. In a per-user report "each item that user used counts once" (same source), so a developer at zero distinct custom agents is an onboarding question with a name attached.
- Named ranking for recognized GitHub-provided items, which were the only class the arrays named in this period (same source).

## Why it works

The metric fails the retirement decision because its resolution is coarser than the decision's unit, and it is coarser on purpose. GitHub gave privacy as the reason for withholding the names ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). A release five weeks later reported the names anyway, without restating that reason, so the trade was revisable after all ([GitHub Changelog, 2026-10-22](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)). A distinct count never needed identity, so it stays answerable when every item is called `other`. Compare [per-agent-app attribution](per-agent-app-attribution-copilot-metrics.md), where the reporting unit and the administrator's install-or-remove action are the same object, so the metric joins to the decision.

## When this backfires

- Reading a rising `other` entry as one customization gaining traction. It is the whole customer-defined category, so it moves when any file moves.
- Confusing zero with missing. "Empty arrays and zero counts indicate no matching activity. The fields are null or absent when customization data is unavailable" ([GitHub Changelog, 2026-09-17](https://github.blog/changelog/2026-09-17-agentic-cli-customizations-now-in-the-usage-metrics-api)). Retiring on missing data deletes a file in use.
- Adding plugin totals to skill totals. Plugin interactions already appear in the skill totals, and GitHub says "you should not add the two together" (same source).
- Reading MCP `interaction_count` as tool-call volume. It rises "only when Copilot CLI attempts to connect or reconnect to the server" (same source), so an unstable server outranks a heavily used stable one.
- Small inventories, where the anonymization stops working. If one custom agent exists across the organization, the `other` entry counts that agent, and a per-user report names who ran it.

## Example

A team wants to retire two of its five custom agents.

**Before** — treating the array as a per-agent read:

```text
totals_by_custom_agent    one entry, labelled "other", interaction_count 412
distinct_custom_agent_use_count    3

reading: "412 starts across our agents, 3 of 5 used, retire the other 2"
```

The count of 3 says three distinct agents ran. The payload names none of them.

**After** — reading the two questions the payload answers:

```text
inventory breadth:  3 distinct custom agents used this period, up from 2
per-file identity:  not reported
retirement input:   local invocation logs, or a deliberate removal trial
```

The second form keeps the real breadth trend and sends the per-file question to a source that can answer it.

## Key Takeaways

- Store the customer-defined `other` entry under a column name that says so, such as `custom_agent_other_total`, so nobody later reads it as one agent.
- Derive the 28-day organization view from the `day_totals` entries, which is where these fields sit in an aggregate 28-day report. Do not sum the daily distinct counts: an item used on twelve days would be counted twelve times.
- For report days before 22 October 2026, instrument the per-file question yourself. The bucket in an already-processed report day does not gain names retroactively ([GitHub Changelog, 2026-10-22](https://github.blog/changelog/2026-10-22-custom-skills-agents-and-mcp-servers-in-usage-metrics-api)).

## Related

- [Named Customization Metrics in the Copilot Usage Metrics API](named-customization-metrics-copilot.md) — the October 2026 change that reports the names, and the four conditions that decide whether one appears
- [Per-Agent-App Attribution in the Copilot Usage Metrics API](per-agent-app-attribution-copilot-metrics.md) — the contrast case, where the reporting unit matches the decision's unit
- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — recovering a segmented shape from the same API
- [Reading a Vendor-Computed AI Coding ROI Dashboard](vendor-computed-roi-copilot-impact-dashboard.md) — which decisions a first-party panel can settle
- [The Agent Headcount Vanity Metric](../patterns/anti-patterns/agent-headcount-vanity-metric.md) — what an activity count becomes when nothing joins it to an outcome
