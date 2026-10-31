---
title: "Agent Observability with OpenTelemetry and Trajectory Logging"
description: "Wire up OpenTelemetry on Claude Code, add LangSmith trajectory tracing, and build audit trails that survive context resets — for cost visibility and compliance."
term: "Agent Observability"
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
last_reviewed: 2026-10-28
maturity: established
---

# Agent Observability with OpenTelemetry and Trajectory Logging

> Agent observability combines OpenTelemetry metrics, trajectory tracing, and audit trails to give cost attribution, compliance evidence, and debugging data that survives context resets.

Learn it hands-on: [Attributing the Context](https://learn.agentpatterns.ai/observability/attributing-the-context/) — guided lesson with quizzes.

!!! info "Also known as"
    Trajectory Logging via Progress Files, Progress File Pattern, Audit Trail for Agent Decisions

## Enable OTel on Claude Code

Claude Code ships native OTel support. One environment variable enables it, then you configure the exporter.

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

For faster setup feedback, reduce export intervals:

```bash
export OTEL_METRIC_EXPORT_INTERVAL=10000   # 10 s (default: 60 000 ms)
export OTEL_LOGS_EXPORT_INTERVAL=5000      # 5 s (default: 5 000 ms)
```

Reset before production — short intervals add overhead.

### Lock telemetry org-wide via managed settings

Use the [managed settings file](https://code.claude.com/docs/en/settings#settings-files) (higher precedence than user config, MDM-distributable):

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

## Metrics and events schema

Claude Code exports [metrics](https://code.claude.com/docs/en/monitoring-usage#metrics) (time-series counters) and [events](https://code.claude.com/docs/en/monitoring-usage#events) (structured log records; require `OTEL_LOGS_EXPORTER`).

### Key metrics

| Metric | What it measures |
|--------|-----------------|
| `claude_code.cost.usage` | USD cost per API request, tagged by `model` + `user.account_uuid` + `organization.id` |
| `claude_code.token.usage` | Token count by `type` (`input`, `output`, `cacheRead`, `cacheCreation`) and `model` |
| `claude_code.session.count` | Sessions started — adoption signal |
| `claude_code.code_edit_tool.decision` | Edit/Write/NotebookEdit accept/reject counts |
| `claude_code.lines_of_code.count` | Lines added or removed |
| `claude_code.active_time.total` | Active seconds, split `user` vs `cli` |

All carry: `session.id`, `user.account_uuid`, `organization.id`, `user.email`, `terminal.type`.

### Key events

| Event name | Fired when |
|------------|-----------|
| `claude_code.user_prompt` | User submits a prompt |
| `claude_code.api_request` | API call completes — includes `cost_usd`, `duration_ms`, token counts |
| `claude_code.api_error` | API call fails — includes `status_code`, `error`, `attempt` |
| `claude_code.tool_decision` | Tool permission decided — includes `tool_name`, `decision`, `source` |
| `claude_code.tool_result` | Tool finishes — includes `success`, `duration_ms`, `decision_source` |
| `claude_code.safety_event` | A permission rule, auto mode, a safety check, a hook or the sandbox stops, prompts on, or sends back a tool call (introduced in 2.1.307; 2.1.312 stops sending it) |

All events in a prompt cycle share a `prompt.id` (UUID v4), excluded from metrics (unbounded cardinality) — event-level queries only.

## Cost dashboards

`claude_code.cost.usage` supports per-user (`user.account_uuid`), per-team (`OTEL_RESOURCE_ATTRIBUTES="team.id=platform"`), and per-model attribution. For unique-user counts, prefer ClickHouse or Datadog — the [official monitoring docs](https://code.claude.com/docs/en/monitoring-usage#backend-considerations) note Prometheus suits time-series aggregations while columnar stores handle distinct-counts. Values are approximations. Reconcile them against the billing console.

## Prometheus and Grafana monitoring stack

The [claude-code-monitoring-guide](https://github.com/anthropics/claude-code-monitoring-guide) ships a Docker Compose stack with OTel Collector, Prometheus, and Grafana pre-configured — a starting point before integrating into an existing platform.

## Compliance audit trail via tool decision events

`claude_code.tool_decision` records permission decisions. Its `source` can be `config`, `hook`, `user_permanent`, `user_temporary`, `user_abort`, or `user_reject`. `config` includes several mechanisms, including auto mode; it does not identify the specific check ([monitoring reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event)).

Claude Code 2.1.307 adds `claude_code.safety_event` for calls stopped, prompted, or sent back by permission rules, auto mode, safety checks, hooks, or the sandbox ([changelog](https://code.claude.com/docs/en/changelog#2-1-307)). That entry lists no attribute schema. The [monitoring reference](https://code.claude.com/docs/en/monitoring-usage#safety-event) now documents it, including `category`, `decision`, and `tool_use_id`. Some refused calls have no safety event, so retain tool-decision records too. However, the [2.1.312 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21312) says Claude Code stopped sending this event. The monitoring reference still documents it. Treat the schema as version-dependent and verify emission on your installed build before relying on it.

Pair these with `tool_result` events and store them in Elasticsearch, Loki, or ClickHouse. Enable `OTEL_LOG_TOOL_DETAILS=1` for detailed tool parameters; rejected calls need the matching `tool_decision` event rather than a result ([monitoring reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event)). `tool_parameters` may include secrets — configure backend redaction.

### Interpret classifier fields before counting denials

`classifier_verdict` and `permission_mode` require Claude Code 2.1.301. Use 2.1.302 as the practical minimum for `classifier_category`. That release fixes missing categories on server-reviewed blocks ([tool-decision reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event), [2.1.302 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21302)).

The [documented verdicts](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event) distinguish these outcomes:

- `allow`: the classifier approved the call.
- `block`: the classifier blocked it, or its check failed partway through. A partial outage can therefore increase block counts.
- `no_verdict`: the check ran without a usable verdict, so Claude Code denied the call. This does not establish that the call was unsafe.
- `unavailable`: the classifier request failed, or server-side review returned no safety verdict. Claude Code denied the call.

Missing `classifier_verdict` does not establish that the classifier was uninvolved. The [reference lists four omission cases](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event):

- An allow or deny permission rule decided the call.
- Auto mode approved without asking the classifier.
- The user answered a prompt after repeated blocks.
- A `-p` run without `--permission-prompt-tool` denied the call after repeated blocks.

The [verdict field](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event) can also appear when the classifier reviews plan-mode commands.

`permission_mode` records the mode when the permission check began. For a subagent call, it records the subagent's mode ([field reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event)).

`OTEL_LOG_TOOL_DETAILS=1` exports Bash commands, MCP server/tool names, skill and user-authored workflow names, and tool input in events and trace attributes. Assess that content's exposure before enabling it ([configuration reference](https://code.claude.com/docs/en/monitoring-usage#common-configuration-variables)). With this flag, `classifier_category` appears only for `block` when the classifier names exactly one built-in rule. It excludes user-written rules and multiple-rule matches; an absent category cannot rule out a classifier block ([category reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event)).

Check the client version and `OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT` before interpreting missing fields. From 2.1.302, a low limit can evict `permission_mode`, `classifier_category`, then `classifier_verdict`. From 2.1.310, `parent_agent_id`, `agent_id`, then `request_id` drop before those fields, if present. Before the 2.1.302 fix, new attributes could evict `tool_use_id`, `tool_source`, and `tool_parameters` ([attribute-limit reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event), [2.1.302 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#21302)).

On 2026-10-28, the [monitoring reference](https://code.claude.com/docs/en/monitoring-usage#tool-decision-event) still directs readers to `safety_event.category` and `rule_source`, joined by `tool_use_id`. The conflicting 2.1.312 changelog claim described above would remove this attribution route. Verify the installed build before relying on that join.

Use aggregate category counts to select calls for review. Require per-call evidence that a block was wrong before proposing a narrower guard. Frequency alone cannot justify loosening permissions; keep that judgment separate from measuring the [auto-permission classifier](../patterns/agent-design/classifier-gated-auto-permission.md).

## LangSmith trajectory tracing for LangChain agents

[LangSmith](https://docs.langchain.com/langsmith/trace-with-langchain) records each agent action with tool name, inputs, outputs, latency, and token counts.

Other runtimes have their own vendor write-ups. Braintrust documents tracing for Cloudflare Agents ([Trace and improve Cloudflare Agents](https://www.braintrust.dev/blog/cloudflare-agents), 2026-08-05).

## Progress files as human-readable audit trails

OTel traces are machine-readable. For human-readable trails that survive context resets, use the [trajectory logging pattern](trajectory-logging-progress-files.md): `claude-progress.txt` read at session start and written at end, with git commits providing a diff-linked trail. Watch for [goal drift](../patterns/anti-patterns/objective-drift.md) via diffs. The [post-compaction re-read protocol](../instructions/post-compaction-reread-protocol.md) restores compliance.

## Why it works

`prompt.id` groups events from one prompt. Structured events let teams query permission outcomes and costs without parsing progress messages ([monitoring reference](https://code.claude.com/docs/en/monitoring-usage#events)).

## When this backfires

- Label cardinality explosion: per-request IDs as metric labels create unbounded time series. `prompt.id` is excluded from metrics for this reason — apply the same discipline to custom `OTEL_RESOURCE_ATTRIBUTES`.
- Secrets in tool parameters: `tool_parameters` on `tool_result` events may include credentials. Without backend redaction, `OTEL_LOG_TOOL_DETAILS=1` leaks secrets.
- Context loss across agent boundaries: `TRACEPARENT` propagates only to direct subprocesses. Agents communicating via queues, webhooks, or separate processes produce data islands, not end-to-end traces.
- Cost approximations as billing data: `claude_code.cost.usage` values are estimates — chargebacks built on them drift from actual invoices.

## FAQ

**Why is `claude_code.cost.usage` unreliable for billing?**

`claude_code.cost.usage` is a per-request USD estimate tagged by model, account, and organization — useful for dashboards, but the [official monitoring docs](https://code.claude.com/docs/en/monitoring-usage#backend-considerations) flag it as an approximation. Chargebacks or invoices built directly on it will drift from what you're actually billed, so reconcile the values against the billing console before using them for anything financial.

**Why does OTel use a push model instead of pull-based scraping for agent traffic?**

Agents emit bursts of activity across many tool calls in short-lived sessions, and pull-based scraping can miss those bursts between scrape intervals. OTel's push-based model sends metrics and events as they happen, so a session that starts and finishes between polls still gets captured — which is why Claude Code exports via OTLP push rather than waiting to be scraped.

**Why do traces go missing when agents communicate through queues or webhooks?**

`TRACEPARENT` propagates automatically only to direct subprocesses, so a trace stays intact as long as one process calls another directly. Once agents hand work off through a queue, webhook, or separate process instead, that propagation breaks — you get disconnected data islands rather than one end-to-end trace, and correlating them back together requires custom instrumentation.

**Can OTel tool-result events leak secrets?**

Yes. `tool_result` events carry `tool_parameters`, which can include credentials or other sensitive values passed to a tool. Enabling `OTEL_LOG_TOOL_DETAILS=1` without backend redaction in your logging pipeline (Elasticsearch, Loki, ClickHouse) means those secrets flow straight into your observability backend — configure redaction before turning this on in production.

## Key Takeaways

- `CLAUDE_CODE_ENABLE_TELEMETRY=1` + an exporter (`prometheus`, `otlp`, or `console`) — no code changes required.
- `prompt.id` correlates all events from a single prompt; `claude_code.cost.usage` by `user.account_uuid` + `model` gives cost attribution.
- `claude_code.tool_decision` with `source` is a ready-made compliance audit trail.
- OTel metrics, LangSmith traces, and [progress files](trajectory-logging-progress-files.md) complement each other: cost/perf, failure analysis, and context-portable audit trails.
- Enforce telemetry org-wide via managed settings (MDM).

## Related

- [OpenTelemetry for Agent Observability](../standards/opentelemetry-agent-observability.md)
- [Agent Harness](../patterns/agent-design/agent-harness.md)
- [Agent Debugging](agent-debugging.md)
- [Agent Debug Log Panel](agent-debug-log-panel.md)
- [Loop Detection](loop-detection.md)
- [Event Sourcing for Agents](event-sourcing-for-agents.md)
- [Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
