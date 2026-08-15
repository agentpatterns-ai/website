---
title: "Per-Agent-App Attribution in the Copilot Usage Metrics API"
description: "The Copilot Usage Metrics API reports activity per agent app, matching the metric to a per-app install decision — usable only under the four limits GitHub states."
aliases:
  - totals_by_3rd_party_agent
  - copilot agent app activity
  - per agent app attribution
tags:
  - copilot
  - human-factors
  - observability
last_reviewed: 2026-08-08
maturity: emerging
status: current
---

# Per-Agent-App Attribution in the Copilot Usage Metrics API

> The Copilot Usage Metrics API reports activity per agent app, a breakdown that fits the per-app install decision under four stated limits.

On 7 August 2026 the Copilot Usage Metrics API gained an optional `totals_by_3rd_party_agent` array carrying "one entry per recognized agent app", in the enterprise, organization, enterprise-user, and organization-user reports over both 1-day and 28-day periods ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-usage-metrics-api-adds-agent-app-activity)).

## Read the breakdown under four limits

GitHub states each of these in the changelog. Every one of them breaks a naive dashboard.

- Never sum the two interaction counters. The nested `user_initiated_interaction_count` counts agent app job starts; the top-level field of the same name counts explicit prompts from other telemetry. GitHub calls them distinct.
- The array is not a partition. Activity from agents that cannot be identified is omitted, and multiple apps belonging to one agent collapse into a single entry, so per-app shares carry an unmeasured residual and do not reconstruct the total.
- An absent array is not zero activity. The field is excluded from reports that have no agent activity at all, so a consumer must distinguish a missing key from a silent app.
- Per-user rows are thinner. `session_count` appears only in the enterprise and organization reports; user-level entries carry interaction counts alone.

## What each entry carries

| Field | Meaning | Scope |
|---|---|---|
| `agent_name` | The agent's display name | All four reports |
| `agent_id` | Identifier stable across reporting periods | All four reports |
| `user_initiated_interaction_count` | Agent app job starts | All four reports |
| `session_count` | Agent sessions | Enterprise and organization only |

Agent apps are partner AI agents installed from the GitHub Marketplace and enabled by an administrator, invoked by assigning an issue, mentioning the agent in a pull request comment, or picking it in the Agents interface ([GitHub Changelog, 2026-06-02](https://github.blog/changelog/2026-06-02-extend-github-with-agent-apps/)). Claude and Codex are named among the agents the new dimension reports ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-usage-metrics-api-adds-agent-app-activity)).

## Why it works

The intervention is per app, so the metric has to be per app or it cannot be joined to the decision. An enterprise owner installs, enables, and removes one GitHub App at a time, a capability that only reached third-party apps on the same day the metrics dimension shipped ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-enterprises-can-now-install-third-party-github-apps)). An activity total summed over apps has no join key to that action: two inventories with identical totals can differ completely in composition, and composition is the only thing an administrator can change. `agent_id` is specified as stable across reporting periods, which is what turns a snapshot into a longitudinal series per app. This is the same conditional-over-marginal recovery that [cohort segmentation](cohort-segmentation-copilot-usage-metrics.md) performs on the user population, applied instead to the agent inventory.

## When this backfires

- Low agent-app volume. Across 25,264 agentic pull requests in 2,361 popular GitHub repositories, the median repository produced one to two agentic pull requests per three-month window ([Raida & Hou, 2026, arXiv:2607.14037v2](https://arxiv.org/abs/2607.14037v2)). At that base rate a 1-day or 28-day per-app split ranks noise.
- Retiring an app on low activity. In Microsoft's early-2026 rollout, first use spread primarily through social networks and retention was associated more with engineers' coding activity than with demographics ([Murphy-Hill et al., 2026, arXiv:2607.01418v1](https://arxiv.org/abs/2607.01418v1)). An app that never reached the right teams reports the same number as one nobody wants.
- Reading activity as value. Experienced open-source developers in a randomized trial took 19% longer with early-2025 AI tools while estimating a 20% speedup ([Becker et al., 2025, arXiv:2507.09089v2](https://arxiv.org/abs/2507.09089v2)), so the intuition a reader brings to a per-app chart is an unreliable prior.
- Shipping it without an outcome measure. Activity per app is an output metric, and unpaired it becomes the [agent headcount vanity metric](../patterns/anti-patterns/agent-headcount-vanity-metric.md) on a new axis. The impact dashboard's return-on-investment section, released the same day, reports cost per developer per month and pull requests per developer per month, though GitHub calls the figures "estimates based on AI credit consumption" against a salary "modeling input rather than actual payroll data" and says to treat them as directional ([GitHub Changelog, 2026-08-07](https://github.blog/changelog/2026-08-07-copilot-impact-dashboard-adds-a-return-on-investment-section)).

## Example

Both counters share a name, which is where the double count comes from.

**Before** — summing the nested counter into the top-level one:

```text
top-level  user_initiated_interaction_count  = 4120
per-agent  user_initiated_interaction_count  =  860   (summed over the array)

total interactions = 4120 + 860 = 4980                # wrong
```

**After** — keeping the two counters apart and naming the residual:

```text
prompts from other telemetry (top-level counter)  = 4120
agent app job starts (per-agent counter)          =  860
unidentified agent activity                       =  not reported
```

The first form invents 860 interactions that were never prompts. The second keeps the two populations apart and marks the omitted activity as unknown rather than zero.

## Key Takeaways

- Query `totals_by_3rd_party_agent` on the 28-day report rather than the 1-day one, unless the inventory generates enough daily volume to clear the noise floor.
- Keep the nested and top-level `user_initiated_interaction_count` in separate columns permanently; a single "interactions" column is already wrong.
- Label the unidentified-agent residual explicitly in any share-of-activity view, because the array does not sum to the total.
- Key longitudinal series on `agent_id`, not `agent_name`, since only the identifier is specified as stable across periods.
- Gate every retire-or-renew decision on a paired outcome number. The activity count answers which app is used, never whether the use paid back.

## Related

- [Cohort Segmentation in the Copilot Usage Metrics API](cohort-segmentation-copilot-usage-metrics.md) — the same diagnostic move on the same API, applied to the user population instead of the agent inventory.
- [Agent Headcount as a Vanity Metric](../patterns/anti-patterns/agent-headcount-vanity-metric.md) — what per-app activity degenerates into when no outcome metric sits beside it.
- [Copilot vs Claude Billing Semantics](copilot-vs-claude-billing-semantics.md) — the credit consumption that gives each agent app in the inventory a cost to weigh against its activity.
- [Rolling Out CLI Coding Agents at Organization Scale](org-scale-cli-agent-rollout.md) — why social reach confounds a low adoption number, and what to measure instead of seat count.
- [Human-Equivalent Hours for Autonomous Coding Agent Productivity](human-equivalent-hours-agent-productivity.md) — a denominator for the outcome half of the pairing this page requires.
- [Delegating Delivery Stages to GitHub Agent Apps](../workflows/agent-apps-delivery-stage-delegation.md) — the install decision this metric is joined to, decided per delivery stage.
