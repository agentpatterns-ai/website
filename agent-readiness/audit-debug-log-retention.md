---
title: "Audit Debug Log Retention"
description: "Inventory agent debug-log surfaces, validate persistence settings, secret-redaction policy, and disk-pressure guards, emit per-surface findings."
tags:
  - tool-agnostic
  - observability
  - security
aliases:
  - debug log audit
  - agent log retention audit
  - PII redaction audit
---

Packaged as: `.claude/skills/agent-readiness-audit-debug-log-retention/`

# Audit Debug Log Retention

> Inventory agent debug-log surfaces, validate persistence settings, secret-redaction policy, and disk-pressure guards, emit per-surface findings.

!!! info "Harness assumption"
    Surfaces vary by harness: Copilot's Agent Debug Log panel (`github.copilot.chat.agentDebugLog.*`), Claude Code's `OTEL_LOG_RAW_API_BODIES` and shell-snapshot files under `~/.claude/`, transcript exports, and any project-side log writers under `logs/`, `.cache/`, or `.scratch/`. Translate paths if your harness differs. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Run when the project enables raw-event capture, OTel bodies, or transcript persistence. Skip projects that run agents fully ephemerally with no on-disk session state.

Raw event logs capture verbatim prompts, tool inputs, and tool outputs. Claude Code's monitoring reference notes that tool-content capture "can include raw file contents from Read tool results and Bash command output" and recommends backend-side redaction ([Claude Code monitoring](https://docs.claude.com/en/docs/claude-code/monitoring-usage)). Without redaction and retention bounds, secrets pasted into context, API keys in bash output, and PII in fetched URLs persist as readable text. Rules from [`agent-debug-log-panel`](../observability/agent-debug-log-panel.md) and [`agent-observability-otel`](../observability/agent-observability-otel.md).

## Step 1 — Locate Log-Writing Surfaces

```bash
# Copilot debug log persistence settings
grep -rE "github\.copilot\.chat\.agentDebugLog" \
  .vscode/ ~/.config/Code/User/ 2>/dev/null | head -5

# Claude Code OTel raw-body export and shell snapshots
env | grep -E "OTEL_LOG_RAW_API_BODIES|CLAUDE_CODE_.*LOG" 2>/dev/null
ls -1 ~/.claude/shell-snapshots 2>/dev/null | wc -l
ls -1 ~/.claude/projects/*/sessions 2>/dev/null | head -5

# Project-side log writers
find . -type d \( -name "logs" -o -name ".scratch" -o -name "session-logs" \) \
  ! -path "*/node_modules/*" 2>/dev/null

grep -rE "logging\.FileHandler|RotatingFileHandler|open\(.*\.log" \
  .claude/ scripts/ src/ 2>/dev/null | head -10
```

Capture every writer found: path, retention setting (if any), redaction policy.

## Step 2 — Persistence Setting Awareness

For Copilot, both settings default to `false` ([Copilot settings reference](https://code.visualstudio.com/docs/copilot/reference/copilot-settings)). If the project enables `fileLogging.enabled` in checked-in settings, the user may be silently shipping raw events to disk.

```bash
SETTINGS=".vscode/settings.json"
if [[ -f "$SETTINGS" ]]; then
  ENABLED=$(jq -r '."github.copilot.chat.agentDebugLog.fileLogging.enabled" // false' "$SETTINGS")
  REDACT=$(grep -E 'redact|sanitize|scrub' "$SETTINGS")
  if [[ "$ENABLED" == "true" && -z "$REDACT" ]]; then
    echo "high|$SETTINGS|fileLogging.enabled=true with no redaction policy referenced|either disable persistence or document the redaction backend"
  fi
fi
```

For Claude Code, `OTEL_LOG_RAW_API_BODIES=true` exports verbatim API bodies to whatever OTel backend is configured. The backend, not the agent, is responsible for redaction:

```bash
[[ "${OTEL_LOG_RAW_API_BODIES:-}" == "true" ]] \
  && [[ -z "${OTEL_EXPORTER_OTLP_HEADERS:-}" ]] \
  && echo "medium|env|OTEL_LOG_RAW_API_BODIES=true without an authenticated exporter|raw bodies could route to an unintended backend; pin the destination"
```

## Step 3 — Secret and PII Redaction

For each log writer, scan a sample of recent output for known secret shapes. The audit should run against the captured logs themselves, not just the writer config.

```bash
SAMPLES=$(find ~/.claude/projects/*/sessions -type f -name "*.jsonl" -mmin -1440 2>/dev/null | head -3)
SAMPLES="$SAMPLES $(find logs/ .scratch/ -type f -name "*.log" -o -name "*.jsonl" 2>/dev/null | head -3)"

for log in $SAMPLES; do
  python3 - "$log" <<'PY'
import re, sys
text = open(sys.argv[1], errors='ignore').read(2_000_000)
patterns = {
    'aws_access_key': r'AKIA[0-9A-Z]{16}',
    'github_pat':     r'ghp_[A-Za-z0-9]{36}',
    'github_oauth':   r'gho_[A-Za-z0-9]{36}',
    'slack_token':    r'xox[baprs]-[A-Za-z0-9-]{10,}',
    'private_key':    r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    'anthropic_key':  r'sk-ant-[A-Za-z0-9_-]{40,}',
    'jwt':            r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',
}
for label, p in patterns.items():
    if re.search(p, text):
        print(f'high|{sys.argv[1]}|{label} pattern present in log|rotate the credential and add a redaction filter')
PY
done
```

Cross-link to [`audit-secrets-in-context`](audit-secrets-in-context.md) — a high finding here also escalates that audit's severity, since the secret was at one point agent-readable.

## Step 3b — Backend-Side Redaction Rules

When raw bodies route to Datadog, Loki, or an OTel collector, redaction is the backend's job — Claude Code does not strip secrets before export ([Claude Code monitoring](https://docs.claude.com/en/docs/claude-code/monitoring-usage)). The audit must verify a redaction processor is wired on the specific high-risk fields, not just a generic regex sweep.

The fields that carry the highest exposure per [Agent Observability in Practice §Key events](../observability/agent-observability-otel.md):

- `claude_code.tool_parameters` — verbatim Read tool results, Bash command output
- `claude_code.api.request.body` — full prompt text including pasted secrets
- `claude_code.api.response.body` — full assistant text including reflected credentials
- `attributes.user.message` and `attributes.assistant.message` — same content, different schema per backend

```bash
# OTel collector config
find . /etc/otel /etc/otelcol -maxdepth 3 -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null \
  | xargs grep -lE "processors:|attributes:" 2>/dev/null | while read cfg; do
  for field in tool_parameters api.request.body api.response.body user.message assistant.message; do
    grep -qE "$field" "$cfg" || \
      echo "medium|$cfg|no redaction processor for $field|add a 'transform' or 'attributes' processor that masks the field before export"
  done
done

# Datadog agent log_pipelines or processing_rules
find . -name "datadog.yaml" -o -name "datadog-agent.yaml" 2>/dev/null | while read cfg; do
  grep -qE "log_processing_rules|processors" "$cfg" || \
    echo "medium|$cfg|no log_processing_rules block|add mask_sequences for AKIA, ghp_, sk-ant-, BEGIN PRIVATE KEY"
done

# Loki promtail / vector sinks
find . -name "promtail*.yaml" -o -name "vector.toml" -o -name "vector.yaml" 2>/dev/null | while read cfg; do
  grep -qE "replace|mask|redact" "$cfg" || \
    echo "medium|$cfg|no replace/mask transform|add a stage that drops or masks high-risk fields"
done
```

A reference OTel `attributes` processor that masks the four fields:

```yaml
processors:
  attributes/redact:
    actions:
      - key: claude_code.tool_parameters
        action: hash      # or 'delete' if the field has no diagnostic value
      - key: claude_code.api.request.body
        action: delete
      - key: claude_code.api.response.body
        action: delete
      - pattern: "(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-ant-[A-Za-z0-9_-]{40,})"
        action: hash
```

Wire the processor into the `traces` and `logs` pipelines that handle Claude Code exports. A processor defined but not referenced by a pipeline does nothing — the audit must check both.

## Step 3c — PII Beyond Secrets

Secret patterns catch credentials but miss PII pasted by users (email addresses, account IDs, customer names) and by tools (web fetches that include user records). The audit ships a PII pattern set the project can extend.

```python
PII_PATTERNS = {
    'email':        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
    'phone_e164':   r'\+\d{7,15}',
    'ssn_us':       r'\b\d{3}-\d{2}-\d{4}\b',
    'credit_card':  r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2})[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
    'ip_address':   r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'uuid':         r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',
}
```

PII findings warn rather than block by default — projects in regulated domains (HIPAA, GDPR, PCI) escalate to high. Document the project's domain in `AGENTS.md` so the audit knows which severity to apply.

## Step 4 — Retention Bound

Persisted logs grow with session length. A writer with no rotation, no max-size, and no max-age fills the disk and extends the secret-exposure window indefinitely.

```bash
for log_dir in $LOG_DIRS; do
  TOTAL=$(du -sk "$log_dir" 2>/dev/null | awk '{print $1}')
  OLDEST=$(find "$log_dir" -type f -printf '%T@\n' 2>/dev/null | sort -n | head -1)
  AGE_DAYS=$(( ($(date +%s) - ${OLDEST%.*}) / 86400 ))
  [[ $TOTAL -gt 524288 ]] \
    && echo "medium|$log_dir|exceeds 512 MB on disk|add log rotation (size-based or age-based)"
  [[ $AGE_DAYS -gt 30 ]] \
    && echo "low|$log_dir|oldest log is $AGE_DAYS days|add max-age policy or document why retention is required"
done
```

## Step 5 — Default-Off Posture

For surfaces that are `false` by default in upstream documentation, the audit flags any project that enables them in checked-in config without a paired retention policy and redaction filter. Default-off is the documented position because of the privacy exposure ([VS Code 1.116 release notes](https://code.visualstudio.com/updates/v1_116), [Copilot settings reference](https://code.visualstudio.com/docs/copilot/reference/copilot-settings)).

```bash
for setting_file in .vscode/settings.json .claude/settings.json; do
  [[ -f "$setting_file" ]] || continue
  jq -r 'paths(scalars) as $p | select(getpath($p) == true) | $p | join(".")' "$setting_file" 2>/dev/null \
    | grep -E "agentDebugLog|raw.?body|fileLogging|verbose" \
    | awk -v f="$setting_file" '{print "low|"f"|"$0" enabled in checked-in settings|confirm retention and redaction policy are documented"}'
done
```

## Step 6 — Per-Surface Scorecard

```markdown
# Audit Report — Debug Log Retention

## Per-surface scorecard

| Surface | Persistence | Redaction | Retention bound | Default-off respected | Top issue |
|---------|:-----------:|:---------:|:---------------:|:---------------------:|-----------|
| <name> | ✅ | ❌ | ⚠️ | ✅ | <one-line> |

## Findings

| Severity | Surface | Finding | Suggested fix |
|----------|---------|---------|---------------|
```

## Idempotency

Read-only. The secret scan in Step 3 reads sample log files but emits no logs of its own.

!!! warning
    A `high` finding here means a live credential exists in agent-readable logs. Treat exactly as [`audit-secrets-in-context`](audit-secrets-in-context.md): halt other work, rotate, then purge the log file from history.

## Output Schema

```markdown
# Audit Debug Log Retention — <repo>

| Surfaces | Pass | Warn | Fail | Secrets | Logs > 30d |
|---------:|-----:|-----:|-----:|--------:|-----------:|
| <n> | <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing redaction or retention bound>
```

## Remediation

- For each writer with no redaction, route output through a sanitizer that strips the patterns from Step 3 before write
- For unbounded log directories, configure rotation: `RotatingFileHandler(maxBytes=10_000_000, backupCount=5)` for Python, `logrotate` for system-level
- For `OTEL_LOG_RAW_API_BODIES`, pin the exporter endpoint and verify the backend redacts at ingest

## Related

- [Agent Debug Log Panel](../observability/agent-debug-log-panel.md)
- [Agent Observability: OTel](../observability/agent-observability-otel.md)
- [OpenTelemetry for AI Agent Observability](../standards/opentelemetry-agent-observability.md)
- [Audit Secrets in Context](audit-secrets-in-context.md)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
