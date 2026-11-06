---
title: "Reading Agent Spend Back by Team Needs Dated Group Records"
term: "Cohort Spend Readback"
description: "A team cost report can group past agent spend correctly only by the group membership recorded on the day of the spend, so identity retention sets its reach."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - per-team agent spend report
  - cohort cost report
  - dated identity record
last_reviewed: 2026-11-05
maturity: emerging
---

# Reading Agent Spend Back by Team Needs Dated Group Records

> A team spend report must join each day's spend to that day's group membership, so identity retention sets how far back it reaches.

Cohort spend readback answers where past agent spend went, by team, developer, or day. A spend cap acts before a call and decides whether it happens. A readback acts afterwards, and it answers the question a team lead gets asked about last month. Claude Code 2.1.317 added "a cost report to the Claude apps gateway admin API" that reads "past spend over a date range in total, per developer, per day or per IdP group" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-317)).

The per-group view depends on a second change in the same release: "a daily record of each developer's IdP groups on Claude apps gateways with `admin:` set, kept for `admin.identity_retention_days`, which the cost report groups by" (same source).

## Why current membership gives the wrong answer

People move teams. Their spend stays on the day it happened. The spend limits reference describes "the principal's last-seen IdP groups" ([spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)). Group last month by that row and a developer who moved on the 20th bills the whole month to the new team. Last-seen groups also go stale: 2.1.295 fixed the admin spend view "showing a developer's old groups and group cap after their session stopped carrying groups" ([changelog](https://code.claude.com/docs/en/changelog#2-1-295)).

GitHub documents the same failure for Copilot team metrics. A single-day membership snapshot "attributes the full 28 days of activity to whichever teams the user happens to belong to on the join day", so GitHub tells readers to "join daily activity with daily user-teams, then aggregate to your desired window" ([GitHub Docs](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/team-level-metrics)).

## Retention sets the reach

The gateway keeps spend and identity for different lengths of time, on purpose:

| Record | Holds | Default retention |
|---|---|---|
| `spend` | Period-to-date counters per principal, keyed by OIDC `sub` | `admin.spend_retention_months`, 13 |
| `principal_emails` | Last-seen email, display name, and groups, which are PII | `admin.identity_retention_days`, 90 since last activity |
| Daily group record (2.1.317) | Each developer's IdP groups per day | `admin.identity_retention_days` |

The config reference gives the reason: identity retention is "Deliberately shorter than spend retention so a deprovisioned identity ages out while its anonymous spend counters remain" ([gateway config](https://code.claude.com/docs/en/claude-apps-gateway-config#admin)). The changelog does not say what the report returns for a day whose group record has aged out, so run a range older than your setting before a quarterly review depends on it.

Raising the window buys reach, and the gateway then keeps a longer per-person history of team membership, which is PII.

Pick the grouping from the decision. A per-developer view fits a conversation with one heavy user, and gateway caps already target one developer by OIDC `sub`. Per-day fits finding the date a cost moved. Per-group fits a team budget, the same unit as an `rbac_group` cap ([spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)).

## Why it works

Grouping past spend by team is a join between a spend record and a membership record, and it is correct only when both carry the same date. A membership record cannot be rebuilt for a day nobody recorded it. AWS shows this with cost allocation tags: after a backfill from January 2023 for a tag first applied in June, "January 2023 to May 2023 will not have tag values associated because the `Project` tag was not present in the AWS Resources" ([AWS](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-allocation-backfill.html)). A cohort report can reach back only as far as the dated identity record does.

## When this backfires

- A warehouse already keeps dated group history. Read per-developer spend by `sub` and join it there, so membership has one retention policy and one erasure path. For per-developer AWS cost attribution on Bedrock, `session_name: email` makes "each developer's requests reach AWS under their own assumed-role session" ([gateway config](https://code.claude.com/docs/en/claude-apps-gateway-config#per-developer-aws-cost-attribution)).
- The report is used as an invoice. The gateway's amounts "are USD estimates, a circuit breaker rather than an invoice" ([spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)), and 2.1.286 fixed the meter "pricing 1-hour prompt cache writes at the cheaper 5-minute rate" ([changelog](https://code.claude.com/docs/en/changelog#2-1-286)).
- Group rows are summed into an org total. Copilot users "on multiple teams contribute to each team they belong to" ([GitHub Docs](https://docs.github.com/en/copilot/reference/copilot-usage-metrics/team-level-metrics)). The Claude changelog does not say how the gateway counts them, so check the group sum against the total first.
- A group is small. Copilot excludes "Teams with fewer than 5 seated Copilot users" from its membership report (same source). The [Claude changelog](https://code.claude.com/docs/en/changelog#2-1-317) states no small-group suppression rule. Verify what the report shows for a small group before you expose it.
- The erasure runbook predates 2.1.317. The spend limits page still calls `principal_emails` "the only table holding their email, name, and groups" ([spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits)). The daily group record is new, and the changelog does not say where it lives.

## Key Takeaways

- A spend cap decides whether a call happens. A cost report explains where past spend went. The Claude apps gateway has offered both since 2.1.317.
- Group past spend by the membership recorded on the day of the spend. A last-seen group row moves a team-mover's spend to the new team.
- On defaults, spend is kept 13 months and identity 90 days. Run a range older than 90 days before a quarterly review relies on the per-group view.
- A longer identity window buys reach and costs a longer PII record. A warehouse with dated group history may be the better home.

## Related

- [Client-Keyed Gateway Controls: Where a Spend Cap's Trust Comes From](client-keyed-gateway-controls.md) — the enforcement half: what a gateway cap keys on and who can select it
- [Centralized LLM Gateway for Per-Dimension Agent Budgets](../../observability/llm-gateway-per-dimension-budgets.md) — the per-user and per-team budgets that act before a call
- [Progressive Spend Threshold Alerting for Agent Cost Governance](progressive-spend-threshold-alerting.md) — alerts during the period, before a cap or a readback
- [Cohort Segmentation in the Copilot Usage Metrics API](../../human/cohort-segmentation-copilot-usage-metrics.md) — the Copilot API's cohort view of the user population, beside its team join
