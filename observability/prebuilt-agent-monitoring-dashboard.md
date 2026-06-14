---
title: "Prebuilt Agent Monitoring Dashboard"
description: "Ship a default Grafana view with the agent stack to close the OTel-emitter-to-consumer gap — but only when backend, model class, and emitter conditions hold."
tags:
  - observability
  - tool-agnostic
  - workflows
  - testing-verification
aliases:
  - shipped agent dashboard
  - default agent monitoring view
  - templated OTel dashboard
last_reviewed: 2026-06-02
maturity: established
---

# Prebuilt Agent Monitoring Dashboard

> A dashboard shipped with an agent stack turns an unused OTel emitter into a glanceable surface, given a shared backend, stable models, and verified telemetry.

A prebuilt agent monitoring dashboard is a JSON or template artefact distributed with an agent harness — Grafana, Datadog, Honeycomb, or equivalent — that visualises a fixed panel set (per-model latency, token cost, tool-call rate, session count) against the metrics the harness already emits. The dashboard is the *consumer* in the OTel pipeline; its panel set defines which spans, metrics, and attributes the upstream emitter must produce.

## When This Pattern Applies

The pattern pays off only when all of these hold:

- **An OTel emitter is already wired and verified.** Without `CLAUDE_CODE_ENABLE_TELEMETRY=1` and a reachable OTLP collector ([Agent Observability with OpenTelemetry](agent-observability-otel.md)), the dashboard renders empty — broken instrumentation, not a healthy agent. Wire and verify the emitter first.
- **A shared monitoring backend exists.** VS Code 1.121 ships against Azure Managed Grafana fed via OTel Collector to Application Insights ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121)); Anthropic's reference stack uses self-hosted Prometheus + Grafana ([anthropics/claude-code-monitoring-guide](https://github.com/anthropics/claude-code-monitoring-guide)). A dashboard with no shared audience is a dotfile.
- **The model class is stable.** Per-model latency and cost panels assume a fixed model list; routing across Sonnet, Haiku, and Opus tiers expands the dimension faster than panel definitions track.

## The Converged Panel Set

Two independent shipped examples — VS Code's Azure Managed Grafana template and Anthropic's `working-dashboard.json` — converge on a narrow default view. VS Code visualises "agent operations, token usage, chat sessions, tool calls, and per-model response time and time to first token (TTFT)" ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121)). Anthropic's eight-panel layout (Total Cost, Cost by Model, Token Usage by Type, Active Users, and more) is driven by three counters: `claude_code_cost_usage_USD_total`, `claude_code_token_usage_tokens_total`, `claude_code_lines_of_code_count_total` ([working-dashboard.json](https://github.com/anthropics/claude-code-monitoring-guide/blob/main/grafana/dashboards/working-dashboard.json)).

The intersection — per-model cost, token usage by type, session count, tool-call rate, per-model latency or TTFT — is the minimum opinionated panel set. Anything beyond it should be added from a real incident, not predicted.

## How The Panels Force The Telemetry Contract

Every panel becomes a requirement on the emitter:

| Panel | Required upstream contract |
|-------|---------------------------|
| Cost by Model | `claude_code.cost.usage` carries bounded-cardinality `model` label ([metrics docs](https://code.claude.com/docs/en/monitoring-usage#metrics)) |
| Per-Model TTFT | API-request span records `time_to_first_token_ms` and `model` |
| Token Usage by Type | `claude_code.token.usage` carries `type` (`input`/`output`/`cacheRead`/`cacheCreation`) |
| Active Users | `user.account_uuid` set on every metric, bounded by org user count |
| Tool Call Rate | `claude_code.tool_decision` carries `decision` (`accept`/`reject`) and `tool_name` |

Treating the dashboard as a schema check — does the panel render? — surfaces emitter drift the moment a panel goes empty.

## Why It Works

A shipped dashboard inverts the activation-energy problem in observability adoption: teams enable OTel exporters but rarely build the visualisation layer, so events sit in a backend nobody opens. A default view gives the team a surface to glance at and forces the emitter to be calibrated against a real consumer. VS Code 1.121 frames it as the import target for "an end-to-end setup" of agent monitoring ([release notes](https://code.visualstudio.com/updates/v1_121)) — unblocker, not destination.

OTel bootstrap and observability-calibration runbooks lean on the same mechanism: define the consumer before tuning the emitter.

## When This Backfires

- **Solo developer or pre-production project.** No shared audience, no chargeback story, no SLO — the import overhead exceeds the value.
- **Backend mismatch.** Each shipped example targets one stack — Azure Managed Grafana plus App Insights for VS Code ([release notes](https://code.visualstudio.com/updates/v1_121)), self-hosted Prometheus plus Grafana for Anthropic ([claude-code-monitoring-guide](https://github.com/anthropics/claude-code-monitoring-guide)). Teams on Datadog, Honeycomb, or Grafana Cloud must port panels and often metric names; porting cost can exceed building from scratch.
- **Model routing breaks the label set.** A per-model latency panel assumes a static model list; routing across Sonnet, Haiku, and Opus tiers leaves stale dimensions on the wall.
- **No upstream emitter.** Without `CLAUDE_CODE_ENABLE_TELEMETRY=1` and an OTLP-compatible backend ([Agent Observability with OpenTelemetry](agent-observability-otel.md)), the dashboard is empty — a fault indicator only works if the emitter is verified separately.
- **Calibration drift.** The panels encode last-quarter's failure modes. Without a planted-bug calibration loop, the dashboard diverges from current failure patterns and becomes a confidence trap.
- **Infrastructure metrics measure cost, not correctness.** The converged panel set tracks latency, cost, tokens, and call rates — emitter health and resource spend, not whether the agent's output is right. An agent can hallucinate, call an unauthorized tool, or drift behaviorally while every panel stays green, so practitioners now treat these infra metrics as insufficient on their own ([OpenTelemetry: AI agent observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)). Pair the dashboard with output-quality and eval signals; a green board is not a correctness guarantee.

## Example

Anthropic's `working-dashboard.json` ships eight Grafana panels driven by three Prometheus counters ([source](https://github.com/anthropics/claude-code-monitoring-guide/blob/main/grafana/dashboards/working-dashboard.json)):

```json
{
  "title": "Total Cost",
  "type": "stat",
  "unit": "currencyUSD",
  "targets": [{
    "expr": "sum(increase(claude_code_cost_usage_USD_total[$__range]))"
  }]
}
```

```json
{
  "title": "Cost by Model",
  "type": "piechart",
  "targets": [{
    "expr": "sum by (model)(increase(claude_code_cost_usage_USD_total[$__range]))",
    "legendFormat": "{{model}}"
  }]
}
```

The dashboard's three required metric series — `claude_code_cost_usage_USD_total`, `claude_code_token_usage_tokens_total`, `claude_code_lines_of_code_count_total` — match the canonical Claude Code metric names ([monitoring usage docs](https://code.claude.com/docs/en/monitoring-usage#metrics)). A team that imports the dashboard against a misconfigured emitter sees empty panels — which is the intended feedback loop.

## Key Takeaways

- Ship the dashboard with the harness when an OTel emitter is wired, the backend is shared, and the model class is stable.
- The converged panel set across VS Code 1.121 and Anthropic's reference is per-model cost, token usage by type, session count, tool-call rate, and per-model latency or TTFT — narrow on purpose.
- The panel set is the upstream telemetry contract; an empty panel signals an emitter drift faster than schema assertions.
- These panels track cost and emitter health, not correctness — pair them with output-quality signals so a green board is not mistaken for a correct agent.
- Default dashboards become wallpaper without a planted-bug calibration loop that keeps the panels aligned with current failure modes.

## Related

- [Agent Observability with OpenTelemetry](agent-observability-otel.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Observability Feedback Loop: A 7-Step Debug Runbook](observability-feedback-loop.md)
