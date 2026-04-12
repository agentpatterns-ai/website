---
title: "Agent Observability: OTel, Cost Tracking, Trajectory Logs"
description: "Wire up OpenTelemetry on Claude Code, add LangSmith trajectory tracing, and build audit trails that survive context resets — for cost visibility and compliance."
tags:
  - agent-design
  - workflows
  - observability
  - cost-performance
  - claude
aliases:
  - Trajectory Logging via Progress Files
  - Progress File Pattern
  - Audit Trail for Agent Decisions
---

# Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging

> Agent observability combines OpenTelemetry metrics and events, trajectory tracing, and structured audit trails to give you cost attribution, compliance evidence, and debugging data that survives context resets — all without custom instrumentation.

!!! info "Also known as"
    Trajectory Logging via Progress Files, Progress File Pattern, Audit Trail for Agent Decisions

## Enable OTel on Claude Code

Claude Code ships native OpenTelemetry support. Set one env var to turn it on, then configure where the data goes.

```bash
# Minimum: enable telemetry
export CLAUDE_CODE_ENABLE_TELEMETRY=1

# Route metrics to Prometheus scrape endpoint
export OTEL_METRICS_EXPORTER=prometheus

# Or push metrics + events via OTLP/gRPC to a collector
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

To see data quickly during setup, reduce export intervals:

```bash
export OTEL_METRIC_EXPORT_INTERVAL=10000   # 10 s (default: 60 000 ms)
export OTEL_LOGS_EXPORT_INTERVAL=5000      # 5 s (default: 5 000 ms)
```

Reset to defaults before production; short intervals add overhead.

### Lock telemetry org-wide via managed settings

Lock settings org-wide via the [managed settings file](https://code.claude.com/docs/en/settings#settings-files) (higher precedence than user config, distributable via MDM):

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer example-token"
  }
}
```

## Metrics and Events Schema

Claude Code exports [metrics](https://code.claude.com/docs/en/monitoring-usage#metrics) (time-series counters) and [events](https://code.claude.com/docs/en/monitoring-usage#events) (structured log records, require `OTEL_LOGS_EXPORTER`).

### Key metrics

| Metric | What it measures |
|--------|-----------------|
| `claude_code.cost.usage` | USD cost per API request, tagged by `model` + `user.account_uuid` + `organization.id` |
| `claude_code.token.usage` | Token count by `type` (`input`, `output`, `cacheRead`, `cacheCreation`) and `model` |
| `claude_code.session.count` | Sessions started — adoption signal |
| `claude_code.code_edit_tool.decision` | Edit/Write/NotebookEdit accept or reject counts |
| `claude_code.lines_of_code.count` | Lines added or removed |
| `claude_code.active_time.total` | Active time in seconds, split `user` vs `cli` |

Standard attributes on all: `session.id`, `user.account_uuid`, `organization.id`, `user.email`, `terminal.type`.

### Key events

| Event name | Fired when |
|------------|-----------|
| `claude_code.user_prompt` | User submits a prompt |
| `claude_code.api_request` | API call completes — includes `cost_usd`, `duration_ms`, token counts |
| `claude_code.api_error` | API call fails — includes `status_code`, `error`, `attempt` |
| `claude_code.tool_decision` | Tool permission decided — includes `tool_name`, `decision`, `source` |
| `claude_code.tool_result` | Tool finishes — includes `success`, `duration_ms`, `decision_source` |

All events in a prompt cycle share a `prompt.id` (UUID v4) for correlation. `prompt.id` is excluded from metrics (unbounded cardinality) — use it for event-level queries only.

## Cost Dashboards

`claude_code.cost.usage` supports per-user (`user.account_uuid`), per-team (`OTEL_RESOURCE_ATTRIBUTES="team.id=platform"`), and per-model attribution. For unique-user counts, prefer ClickHouse or Datadog over Prometheus — the [official monitoring docs](https://code.claude.com/docs/en/monitoring-usage#backend-considerations) note Prometheus is suited to time-series aggregations, while columnar stores handle efficient distinct-count queries. Cost values are approximations — use the billing console for authoritative figures.

## Prometheus + Grafana Monitoring Stack

The [claude-code-monitoring-guide](https://github.com/anthropics/claude-code-monitoring-guide) ships a ready-to-use Docker Compose stack with OpenTelemetry Collector, Prometheus, and Grafana pre-configured. Clone and start it, then run Claude Code with the Prometheus exporter:

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=prometheus
```

Use as a starting point before integrating into an existing platform.

## Compliance Audit Trail via Tool Decision Events

`claude_code.tool_decision` records every tool permission decision: `tool_name`, `decision` (`accept`/`reject`), and `source` (`config` = allow/deny rule; `hook` = PreToolUse hook; `user_permanent` = standing permission). This stream answers "what tool ran, when, by whom, under what authorization" — no custom instrumentation required.

Pair with `tool_result` events (which carry `tool_parameters`) for full audit completeness; store in Elasticsearch, Loki, or ClickHouse. **Note**: `tool_parameters` may include secrets — configure your backend to redact it.

## LangSmith Trajectory Tracing for LangChain Agents

LangSmith records each agent action as a trace entry (tool name, inputs, outputs, latency, tokens, cost). Traces can be replayed, diffed, and fed back as improvement signal. Retrieving traces, running parallel error-analysis agents over them, and synthesizing harness changes is a natural automation loop on top of this data.

## Progress Files as Human-Readable Audit Trails

OTel traces are machine-readable. For human-readable audit trails that survive context resets, use the [trajectory logging pattern](trajectory-logging-progress-files.md): `claude-progress.txt` read at session start and written at end, with git commits at each task providing a diff-linked audit trail. Watch for [goal drift](../anti-patterns/objective-drift.md) (repeated clarifications, premature completion post-compaction) via diffs. When post-compaction drift is detected, the [post-compaction re-read protocol](../instructions/post-compaction-reread-protocol.md) restores behavioral compliance.

## Why It Works

OTel's push-based export model fits agent workloads because agents are long-running processes that emit bursts of activity across many tool calls. A pull-based model (e.g., Prometheus scraping) risks missing short-lived sessions or under-sampling bursty cost spikes. The `prompt.id` correlation attribute is structurally necessary because a single user prompt can trigger dozens of API calls and tool executions — without a shared identifier, reconstructing what caused a cost spike or failure is infeasible post-hoc. Structured audit trails (rather than log-level text) let teams query "which tool decisions fired under which authorization source" without parsing free text.

## When This Backfires

- **Label cardinality explosion**: Using `prompt.id` or other per-request identifiers as metric labels creates an ever-growing number of time series. The official docs exclude `prompt.id` from metrics for this reason — enforce the same discipline on custom attributes added via `OTEL_RESOURCE_ATTRIBUTES`.
- **Secrets in tool parameters**: `tool_parameters` on `tool_result` events may include Bash commands or MCP arguments that contain credentials. Without backend redaction, enabling `OTEL_LOG_TOOL_DETAILS=1` leaks secrets into your telemetry store.
- **Context loss across agent boundaries**: OTel traces propagate via `TRACEPARENT` only to direct subprocesses. Agents that communicate via queues, webhooks, or separate processes break the trace context chain — you get islands of trace data rather than end-to-end visibility.
- **Cost approximations masquerade as billing data**: `claude_code.cost.usage` values are estimates. Teams that build chargebacks or budget alerts directly on metric values will drift from actual invoices over time; always reconcile against the billing console.

## Key Takeaways

- `CLAUDE_CODE_ENABLE_TELEMETRY=1` + an exporter (`prometheus`, `otlp`, or `console`) — no code changes required.
- `prompt.id` correlates all events from a single prompt; `claude_code.cost.usage` by `user.account_uuid` + `model` gives cost attribution.
- `claude_code.tool_decision` with `source` is a ready-made compliance audit trail.
- OTel metrics, LangSmith traces, and [progress files](trajectory-logging-progress-files.md) complement each other: cost/perf, failure analysis, and context-portable audit trails.
- Enforce telemetry org-wide via managed settings (MDM).

## Related

- [OpenTelemetry for Agent Observability](../standards/opentelemetry-agent-observability.md)
- [Agent Harness](../agent-design/agent-harness.md)
- [Agent Debugging](agent-debugging.md)
- [Circuit Breakers for Agent Loops](circuit-breakers.md)
- [Loop Detection](loop-detection.md)
- [Event Sourcing for Agents](event-sourcing-for-agents.md)
- [Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [LLM-as-Judge Evaluation with Human Spot-Checking](../workflows/llm-as-judge-evaluation.md)
- [Visible Thinking in AI-Assisted Development](visible-thinking-ai-development.md)
