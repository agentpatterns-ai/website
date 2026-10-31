---
title: "Count Agent Usage at the Model-Provider Boundary"
description: "Count model requests where the provider serves them. Copilot's totals_by_client reaches tools outside the IDE that often send no editor telemetry, under the limits GitHub states."
term: "Provider-Boundary Usage Attribution"
aliases:
  - totals_by_client
  - provider-side request counting
  - server-side usage attribution
tags:
  - copilot
  - human-factors
  - observability
last_reviewed: 2026-10-29
maturity: emerging
status: current
---

# Count Agent Usage at the Model-Provider Boundary

> Count model requests where the provider serves them, because tools outside the IDE often send no editor telemetry and vanish from the IDE breakdown.

Send the coverage questions to the provider-side count: which tools sent traffic, how many sessions and requests each sent, what those requests cost in tokens, and which models they used. Send the in-editor questions to editor telemetry, because the server-side record "can't see what happens in the editor" ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)). Provider-boundary usage attribution answers those four and nothing more, so swapping it in for editor telemetry drops a dimension either way.

On 23 October 2026 the Copilot usage metrics API added a `totals_by_client` array to the enterprise, organization, enterprise-user and organization-user reports, in both the 1-day and 28-day versions ([GitHub Changelog, 2026-10-23](https://github.blog/changelog/2026-10-23-usage-metrics-api-adds-usage-from-tools-like-opencode)). GitHub gives a measurement reason rather than a feature reason: "More developers now use Copilot as the model provider behind tools outside the IDE. Because those tools often don't send editor telemetry, their usage was missing from `totals_by_ide` and hard to account for."

## What each entry carries

| Field | Meaning |
|---|---|
| `client` | The tool that sent the requests, for example `opencode`, `claude_code`, `codex`, `zed`, `copilot_cli`, `github_app`, `cloud_agent`, `code_review`, `vscode`, `jetbrains`, and `other` for unrecognized clients |
| `request_count` | Successful model requests from that client |
| `session_count` | Distinct sessions from that client |
| `token_usage` | Prompt tokens, output tokens, and average tokens per request |
| `totals_by_model` | The same request and token metrics per model, each carrying a `model_selection_mode` |

`model_selection_mode` separates the models a developer requested directly (`user_selected`) from the ones auto chose (`auto`) and the ones the product chose (`product_selected`). Modes GitHub does not yet report individually appear as `other`, and values it cannot normalize appear as `unknown` ([GitHub Changelog, 2026-10-23](https://github.blog/changelog/2026-10-23-usage-metrics-api-adds-usage-from-tools-like-opencode)).

Two reading rules come with the array. It "is an empty array when there is no usage to report", so an empty result means no reported usage. In the aggregated 28-day reports it "appears in each `day_totals` entry" (same source), so a 28-day query reads it per day.

## Which measurement point sees what

GitHub states the asymmetry directly. The detailed breakdowns "come from telemetry that each IDE sends". The separate record GitHub keeps "when Copilot handles a request" is data that "reliably shows who was active, but it can't see what happens in the editor" ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)).

Route each question accordingly. Tool mix, session and request volume, token volume and model mix sit at the provider boundary. Lines of code and accepted suggestions do not, and GitHub says they "can only come from the editor, so client-side gaps won't disappear entirely" (same source).

## Why it works

Coverage at a measurement point depends on whether the measurement event is the work itself. Editor telemetry is a separate report the client has to emit. When the reports disagree with other Copilot data, GitHub says "the gap is usually on the client side" and lists five such conditions: telemetry turned off in the IDE, a proxy or firewall blocking the Copilot telemetry endpoint, an out-of-date IDE or extension, a client that changed how it sends telemetry, and a client that sends no Copilot telemetry at all ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)). GitHub describes the fix as a move to the server side: "Counting requests on the server closes that gap" ([GitHub Changelog, 2026-10-23](https://github.blog/changelog/2026-10-23-usage-metrics-api-adds-usage-from-tools-like-opencode)).

In October 2026 the client-side path failed. Several IDEs moved Copilot agent sessions to the Copilot SDK, and those sessions "didn't identify which IDE they came from, so usage metrics couldn't attribute them correctly". Most of that activity "was left out of reports", and GitHub could not repair it afterwards: "We can't backfill missing data." The charge for the same activity went through untouched: "Billing isn't affected. This issue only changed how agent activity was attributed in usage metrics, not what you were charged" ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)).

## When this backfires

- The target is an editor outcome. Accepted suggestions and lines of code are absent from the server-side record, and GitHub expects that to stay true, so a program measured on either one cannot migrate to this array ([GitHub Changelog, 2026-10-06](https://github.blog/changelog/2026-10-06-update-your-ide-to-restore-agent-activity-in-copilot-usage-metrics)).
- The decision needs a verified identity. Clients "are identified by the integration ID they send with each request", and GitHub says to "Treat `client` as a best-effort grouping, not a verified identity" ([GitHub Changelog, 2026-10-23](https://github.blog/changelog/2026-10-23-usage-metrics-api-adds-usage-from-tools-like-opencode)). That carries a support decision. It does not carry blocking a tool or charging a team for one.
- The comparison is per prompt. "`request_count` counts model calls, not prompts. One prompt can trigger several model calls, so don't compare this field directly with prompt or interaction counts" (same source). Read as prompts per developer, it overstates by a multiple the report does not give you.
- The chart claims to show which models developers chose. Copilot code review and Copilot cloud agent report `product_selected` because the product chooses the model, and Copilot code review models are reported as `unknown` (same source). Unfiltered traffic credits those product choices to people.
- The reader treats the array as a census of agent usage. It measures "model traffic, meaning requests and tokens, from any tool that uses Copilot", so a tool pointed at a different provider is absent, and a tool GitHub does not yet recognize is pooled into `other` (same source).

The move can also cost attribution before it adds any. When GitHub first used server-side telemetry to find active users that client telemetry had missed, it was "increasing your daily active user (DAU) coverage" while "the dimensional breakdowns (such as `totals_by_ide` and `totals_by_feature`) won't yet reflect these users, so a larger share of activity may appear unattributed" ([GitHub Changelog, 2026-06-15](https://github.blog/changelog/2026-06-15-copilot-usage-metrics-now-include-more-of-your-active-users/)). Its stated posture is to hold both signals: "Combining server-side and client-side signals means a single client-side hiccup no longer erases a user from your reports" (same source).

## Example

Attributing model choice needs the selection mode in the filter, not in a footnote.

**Before** — every row summed into a single developer-model-choice chart:

```text
sum(request_count) group by model
```

**After** — filtered to the mode that records a developer's own request:

```text
sum(request_count) group by model
  where model_selection_mode = 'user_selected'

# 'auto'             -> auto chose the model
# 'product_selected' -> the product chose it (Copilot code review, cloud agent)
# model = 'unknown' for Copilot code review; selection mode remains 'product_selected'
```

The first form reads product and router decisions as developer preference. The second answers the question that was asked, and leaves the other modes as their own series.

## Key Takeaways

- Query `totals_by_client` for tool mix, session and request volume, token volume and model mix. Query `totals_by_ide` for what happened in the editor. Neither one substitutes for the other.
- Name `request_count` as model calls in every column header that carries it, and never divide it out into a prompt rate.
- Filter `totals_by_model` on `model_selection_mode` before any chart claims to show developer model choice.
- `client` supports a tool-support decision and stops short of blocking or chargeback, because the integration ID behind it is sent by the client.
- Read an empty `totals_by_client` as no reported usage, and read the 28-day array from each `day_totals` entry.

## Related

- [Per-Agent-App Attribution in the Copilot Usage Metrics API](per-agent-app-attribution-copilot-metrics.md) — the other array in this API, which counts agent app job starts rather than model traffic from any tool.
- [Reading a Client-Version Metric Dip as Lost Adoption](../patterns/anti-patterns/client-version-metric-dip-as-adoption-loss.md) — the incident this page's mechanism rests on, read as a rule for diagnosing a falling curve.
- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — the same API applied to the user population instead of the tool inventory.
- [Reading Copilot Feature Engagement by Its Threshold](copilot-feature-engagement-threshold.md) — another breakdown in this API whose unit has to be read before it is charted.
- [Copilot vs Claude Billing Semantics](copilot-vs-claude-billing-semantics.md) — what the request-level billing path meters, which is the record that survived the October 2026 attribution break.
