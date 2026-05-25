---
title: "Bootstrap OpenTelemetry Initialization"
description: "Detect telemetry support, generate a managed-settings template that enables Claude Code's OTel exporter, configure metrics and tool-decision events, and validate exporter reachability before declaring complete."
tags:
  - tool-agnostic
  - observability
aliases:
  - OTel bootstrap
  - Claude Code telemetry init
  - agent observability scaffold
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-otel-init/`

# Bootstrap OpenTelemetry Initialization

> Detect telemetry support, generate a managed-settings template enabling the OTel exporter, route metrics and tool-decision events, and validate exporter reachability.

!!! info "Harness assumption"
    The runbook configures Claude Code's built-in OpenTelemetry exporter via env vars and `.claude/settings.json` per [Agent Observability in Practice](../observability/agent-observability-otel.md) §Enable OTel on Claude Code. Cursor, Aider, Copilot CLI, and Gemini CLI expose telemetry through different switches — translate Steps 2 and 3 to those switches if running on a different harness. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip this runbook on solo-developer projects with no central telemetry backend. The bootstrap installs scaffolding only when an OTLP-compatible collector (Prometheus scrape endpoint, OTel collector, Datadog Agent, or LangSmith) is reachable from the agent's environment.

Without telemetry, every cost regression, tool-decision drift, and idle-state bug surfaces as a user complaint instead of a metric. The runbook turns the guidance in [Agent Observability in Practice](../observability/agent-observability-otel.md) §Cost Dashboards and §Compliance Audit Trail into config a session can ship today.

## Step 1 — Detect Existing Telemetry

```bash
# Existing config
test -f .claude/settings.json && jq '{
  telemetry: .env.CLAUDE_CODE_ENABLE_TELEMETRY,
  exporters: (.env | with_entries(select(.key | startswith("OTEL_"))))
}' .claude/settings.json

# Reachable backends from the agent host
nc -z localhost 4317 2>/dev/null && echo "OTLP gRPC localhost:4317 reachable"
nc -z localhost 4318 2>/dev/null && echo "OTLP HTTP localhost:4318 reachable"
nc -z localhost 9090 2>/dev/null && echo "Prometheus localhost:9090 reachable"
test -n "${OTEL_EXPORTER_OTLP_ENDPOINT:-}" && echo "Endpoint already in env: $OTEL_EXPORTER_OTLP_ENDPOINT"

# Cluster managed settings (Claude Code reads /etc/claude-code/managed-settings.json)
test -f /etc/claude-code/managed-settings.json && jq '.env' /etc/claude-code/managed-settings.json
```

Decision rules:

- **Telemetry already enabled and exporter reachable** → audit current config against the schema below; skip generation if clean.
- **No reachable backend** → defer the bootstrap; ship without an exporter and the agent simply emits to stderr, paying token cost without observability gain.
- **Managed settings file exists at `/etc/claude-code/managed-settings.json`** → write to that path (org-wide); otherwise write to `.claude/settings.json` (project-local).

## Step 2 — Generate Settings Template

`.claude/settings.json` (or merge into existing):

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
    "OTEL_METRIC_EXPORT_INTERVAL": "60000",
    "OTEL_LOGS_EXPORT_INTERVAL": "5000",
    "OTEL_RESOURCE_ATTRIBUTES": "service.name=claude-code,deployment.environment=dev"
  }
}
```

Substitute the discovered endpoint into `OTEL_EXPORTER_OTLP_ENDPOINT`. Keep `OTEL_METRIC_EXPORT_INTERVAL` ≥ 60000 ms — shorter intervals push high-cardinality metric churn that backends drop. Keep `OTEL_LOGS_EXPORT_INTERVAL` ≤ 5000 ms so tool-decision events surface within a single user wait.

For Prometheus-only setups, replace the OTLP block with `prometheus`:

```json
{
  "env": {
    "OTEL_METRICS_EXPORTER": "prometheus",
    "OTEL_EXPORTER_PROMETHEUS_PORT": "9464"
  }
}
```

Merge with `jq` if the file exists — never overwrite:

```bash
TEMPLATE=$(jq -n '{env:{
  CLAUDE_CODE_ENABLE_TELEMETRY:"1",
  OTEL_METRICS_EXPORTER:"otlp",
  OTEL_LOGS_EXPORTER:"otlp",
  OTEL_EXPORTER_OTLP_PROTOCOL:"grpc",
  OTEL_EXPORTER_OTLP_ENDPOINT:"http://localhost:4317",
  OTEL_METRIC_EXPORT_INTERVAL:"60000",
  OTEL_LOGS_EXPORT_INTERVAL:"5000"
}}')
jq --argjson t "$TEMPLATE" '.env = ((.env // {}) + $t.env)' \
  .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

## Step 3 — Lock Org-Wide via Managed Settings

For org deployments, write the same env block to `/etc/claude-code/managed-settings.json` per [`audit-debug-log-retention`](audit-debug-log-retention.md) §Managed-settings precedence. Managed settings take precedence over user `.claude/settings.json`, preventing per-developer opt-out.

```bash
sudo install -m 0644 /dev/null /etc/claude-code/managed-settings.json
echo '{"env":{"CLAUDE_CODE_ENABLE_TELEMETRY":"1"}}' | \
  sudo tee /etc/claude-code/managed-settings.json >/dev/null
# Then merge the OTLP env vars with jq as in Step 2.
```

## Step 4 — Validate Exporter Reachability

Before declaring done, prove the exporter actually emits. The smoke test must run from the same host the agent runs on, with the new env loaded.

```bash
# Reload env
source .claude/settings.json 2>/dev/null || true
export $(jq -r '.env | to_entries[] | "\(.key)=\(.value)"' .claude/settings.json | xargs)

# OTLP gRPC reachability
nc -z "${OTEL_EXPORTER_OTLP_ENDPOINT#*://}" 2>/dev/null \
  && echo "OK: OTLP endpoint reachable" \
  || { echo "FAIL: OTLP endpoint unreachable — check collector"; exit 1; }

# Prometheus pull (if using prometheus exporter)
test -n "${OTEL_EXPORTER_PROMETHEUS_PORT:-}" && \
  curl -fsS "http://localhost:${OTEL_EXPORTER_PROMETHEUS_PORT}/metrics" | head -5
```

Run a single agent turn that calls one tool, then confirm at least one of the keyed metrics appears at the backend within `OTEL_METRIC_EXPORT_INTERVAL`. Per [Agent Observability in Practice](../observability/agent-observability-otel.md) §Key metrics, the metrics that must surface are:

- `claude_code.token.usage` (input, output, cache_read, cache_creation)
- `claude_code.cost.usage` (USD per session)
- `claude_code.tool_decision` (tool name, accept/reject/error)
- `claude_code.session.count`

If only `session.count` appears, the agent did not call a tool during the smoke turn — re-run with a turn that invokes a tool.

## Step 5 — Wire Cost Dashboards

A telemetry pipeline with no dashboards is theatre — the metrics exist but no one looks. Generate one starter Prometheus query per dimension and commit them to `ops/dashboards/claude-code.promql`:

```promql
# Cost per session (last 1h)
sum by (session_id) (rate(claude_code_cost_usage_total[1h]))

# Tool reject rate (last 6h) — flag agents the user keeps overriding
sum by (tool_name) (rate(claude_code_tool_decision_total{decision="reject"}[6h]))
  / sum by (tool_name) (rate(claude_code_tool_decision_total[6h]))

# Cache-read share (cache health) — should rise above 0.5 within 10 turns
sum(rate(claude_code_token_usage_total{type="cache_read"}[15m]))
  / sum(rate(claude_code_token_usage_total[15m]))
```

Attach a per-team alert on cost-per-session breaching the org's threshold, per [Agent Observability in Practice](../observability/agent-observability-otel.md) §Cost Dashboards.

## Step 6 — Pair with Retention and Redaction

Persisted telemetry that includes raw tool inputs is a secret-leakage surface. Before this runbook is complete, run [`audit-debug-log-retention`](audit-debug-log-retention.md) on the new exporter target to confirm the backend redacts the fields it ingests. Skipping this step lands the project in regulatory drift the moment a token shows up in an HTTP body.

## Idempotency

Re-running merges new env keys; never overwrites existing values unless the discovered endpoint changed. The smoke test in Step 4 is read-only.

## Output Schema

```markdown
# Bootstrap OTel Initialization — <repo>

| Action | File | Notes |
|--------|------|-------|
| Modified | .claude/settings.json | added 7 OTEL_* env vars |
| Created | /etc/claude-code/managed-settings.json | org-wide enable |
| Created | ops/dashboards/claude-code.promql | 3 starter queries |

Smoke test: <pass/fail>
Endpoint: <url>
Metrics observed: <list>
```

## Related

- [Agent Observability in Practice](../observability/agent-observability-otel.md)
- [Audit Debug-Log Retention](audit-debug-log-retention.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
