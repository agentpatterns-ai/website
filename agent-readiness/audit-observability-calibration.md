---
title: "Audit Observability Calibration"
description: "Detect planted-bug fixtures, score coverage across the five canonical layers, validate the diagnosing harness consumes signals only, and surface unreached layers as calibration gaps mapped to missing instrumentation signals."
tags:
  - tool-agnostic
  - testing-verification
  - observability
  - instructions
  - agent-readiness
aliases:
  - planted-bug calibration audit
  - observability diagnostic legibility audit
  - signal calibration probe audit
last_reviewed: 2026-05-27
---

Packaged as: `.claude/skills/agent-readiness-audit-observability-calibration/`

# Audit Observability Calibration

> Detect planted-bug fixtures, score coverage across the five canonical layers (parsing, persistence, IPC, async race, concurrency), validate the diagnosing harness reads signals only, and surface unreached layers as calibration gaps mapped to missing signals.

!!! info "Harness assumption"
    The project ships a planted-bug fixture catalogue under `evals/observability/`, `evals/planted-bugs/`, or `tests/observability/`, plus a diagnosing-agent runner that takes captured signals (logs, traces, metrics, transcripts) as input and emits a layer guess. The diagnosing harness must not hold a Read tool against `src/` or any application source — signals only. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the project has no observability stack at all: no OTel exporter, no structured logging, no metrics emission. There is nothing to calibrate. Skip pre-production prototypes where instrumentation refactors out-pace any fixture catalogue. Run when [`bootstrap-otel-init`](bootstrap-otel-init.md) or [`audit-debug-log-retention`](audit-debug-log-retention.md) confirm an instrumentation substrate exists.

[`bootstrap-otel-init`](bootstrap-otel-init.md) and [`audit-debug-log-retention`](audit-debug-log-retention.md) cover the plumbing — exporters, retention, redaction. [`audit-eval-suite`](audit-eval-suite.md) evaluates application behaviour. None of them check whether the captured signals are actually diagnostic: whether an agent reading only logs, metrics, and traces can name the responsible layer of a known failure within N steps. This audit converts that question into a mechanical check. Source: [`planted-bug-observability-calibration`](../verification/planted-bug-observability-calibration.md).

## Step 1 — Locate the Fixture Catalogue

```bash
# Common locations for planted-bug fixtures
FIXTURES_DIR=$(find . -maxdepth 6 -type d \
  \( -name "observability" -path "*/evals/*" \
  -o -name "planted-bugs" -o -name "planted_bugs" \
  -o -name "observability" -path "*/tests/*" \
  -o -name "calibration-fixtures" \) \
  ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | head -3)

# Common naming patterns inside the catalogue
FIXTURES=$(find $FIXTURES_DIR -type f \
  \( -name "*planted*" -o -name "*fixture*" -o -name "*probe*" \) \
  2>/dev/null)

# Diagnosing-agent runner
RUNNER=$(find . -maxdepth 6 -type f \
  \( -name "diagnose*.py" -o -name "diagnose*.sh" -o -name "calibration-runner*" \
  -o -name "diagnosing-agent*" \) ! -path "*/node_modules/*" 2>/dev/null | head -1)

[[ -z "$FIXTURES_DIR" ]] \
  && echo "high|.|no planted-bug fixture catalogue found|run bootstrap-planted-bug-fixtures or add evals/observability/"
[[ -n "$FIXTURES_DIR" && -z "$RUNNER" ]] \
  && echo "high|$FIXTURES_DIR|fixtures present but no diagnosing-agent runner|add a runner that consumes signals only"
```

If no catalogue exists, the rest of the audit is moot — abort with the high finding and point to the paired bootstrap. Otherwise capture: fixture count, layer labels per fixture, runner path.

## Step 2 — Coverage Across the Five Canonical Layers

The source page names five layers that give broad calibration coverage: **parsing, persistence, IPC, async race, concurrency**. Each missing layer is a finding — a fixture catalogue that covers only parsing failures calibrates against a fake distribution.

```bash
declare -A LAYERS=(
  [parsing]="parsing|parse|tokeniz|lexer|input.size|truncat"
  [persistence]="persistence|persist|write.*read|stale.*read|transaction"
  [ipc]="ipc|inter.process|queue|message.drop|producer.consumer"
  [async_race]="async.race|race.condition|ordering|timestamp.reversal|second.writer"
  [concurrency]="concurrency|lock|mutex|semaphore|lock.hold|deadlock"
)

for layer in "${!LAYERS[@]}"; do
  pattern="${LAYERS[$layer]}"
  HIT=$(grep -rliE "$pattern" $FIXTURES_DIR 2>/dev/null | head -1)
  [[ -z "$HIT" ]] \
    && echo "medium|$FIXTURES_DIR|no fixture for $layer layer|add a deterministic $layer probe per planted-bug-observability-calibration §Building a Fixture Catalogue"
done
```

Each fixture should be deterministic (same input, same failure, every time) and carry a signature that an agent could conceivably reach from instrumentation alone — input-size and empty output for parsing, write-read pairs across a transaction boundary for persistence, producer/consumer counts for IPC, ordering reversal for async race, lock-hold-duration outliers for concurrency.

## Step 3 — Validate the Diagnosing Harness Consumes Signals Only

A diagnosing harness with source-tree read access is a false-pass condition: the agent reaches the layer by reading code, not by reading signals. The catalogue then certifies nothing about instrumentation.

```bash
# The runner and any sub-agent it dispatches must not hold a Read tool against src/
# nor open application source files directly.

# Claude Code sub-agent tool allowlists
DIAG_AGENTS=$(grep -lE 'name:.*diagnos|name:.*calibrat' .claude/agents/*.md 2>/dev/null)
for agent in $DIAG_AGENTS; do
  # Tools should be limited to signal-reading: log files, trace exports, metric dumps
  TOOLS=$(grep -E '^tools:' "$agent" | head -1)
  echo "$TOOLS" | grep -qE 'Read|Glob|Grep' \
    && echo "high|$agent|diagnosing sub-agent has source-read tools|restrict tools to signal-only readers; drop Read/Glob/Grep against src/"
done

# Runner source: any open() against src/, app/, lib/ paths is a false-pass signal
if [[ -n "$RUNNER" ]]; then
  grep -qE 'open\(["'\''](src|app|lib)/|read.*src/|Path\(["'\''](src|app|lib)/' "$RUNNER" \
    && echo "high|$RUNNER|diagnosing runner reads application source|the harness must consume signals only — strip source-tree access"
fi

# A signal-only harness reads from logs/, traces/, metrics/, transcripts/, or the OTel collector
HAS_SIGNAL_INPUT=$(grep -lE 'logs/|traces/|metrics/|transcripts/|otel|jaeger|loki' "$RUNNER" 2>/dev/null)
[[ -n "$RUNNER" && -z "$HAS_SIGNAL_INPUT" ]] \
  && echo "medium|$RUNNER|runner has no obvious signal input path|confirm the harness reads logs/traces/metrics, not application state"
```

Source-visible diagnosing inverts the calibration: the agent succeeds because it can spelunk, and the instrumentation gap stays hidden until a real incident.

## Step 4 — Re-Run the Catalogue Against the Current Stack

A catalogue that exists but has not run against the current observability config measures nothing. Re-execute the runner and check per-fixture pass/fail. Any fixture where the diagnosing agent fails to name the responsible layer within N=10 steps is a **calibration gap** finding, mapped to the missing signal.

```bash
N_STEPS=${CALIBRATION_STEP_BUDGET:-10}

# Standard runner contract: emits one JSON line per fixture
# {"fixture": "parser_silent_truncation", "expected_layer": "parsing",
#  "agent_layer": "parsing", "steps_taken": 4, "pass": true}
RESULTS=$(bash "$RUNNER" --step-budget "$N_STEPS" --json 2>/dev/null)

echo "$RESULTS" | python3 - <<'PY'
import json, sys
SIGNAL_MAP = {
  'parsing':     'add a WARN log on the empty/truncated path; counter on truncation events; span attribute for input size',
  'persistence': 'add transaction-id correlation across write and read; span attribute for read version vs write version',
  'ipc':         'add producer/consumer queue-depth metric per channel; correlation id on enqueue and dequeue',
  'async_race':  'add a timestamp + ordering trace attribute on every writer; metric for ordering-reversal events',
  'concurrency': 'add lock-hold-duration histogram per lock site; span for lock acquire and release',
}
for line in sys.stdin:
    try:
        r = json.loads(line)
    except Exception:
        continue
    if not r.get('pass'):
        layer = r.get('expected_layer', 'unknown')
        fix = SIGNAL_MAP.get(layer, 'add instrumentation that names this layer in the signal stream')
        print(f"high|{r['fixture']}|calibration gap on {layer} layer (agent reached '{r.get('agent_layer')}' in {r.get('steps_taken')} steps)|{fix}")
PY
```

The remediation is at the instrumentation layer, not the application layer. The planted bug stays planted; the logs, spans, metrics, or correlation IDs change. From the source page: "fixing the bug is not the goal — the bug exists to test the signals."

## Step 5 — Re-Run on Every Instrumentation Change

A catalogue is a regression suite for the observability stack. Instrumentation refactors, log-level changes, span attribute renames, and new MCP server additions all shift what a diagnosing agent can see. If the catalogue is not re-run on those changes, it certifies a stack that no longer exists.

```bash
# CI must re-run the catalogue when bootstrap-otel-init or audit-hooks-coverage
# files change. Look for a workflow that gates on those paths.

WORKFLOWS=$(find .github/workflows -type f -name "*.yml" 2>/dev/null)
GATE=$(grep -lE 'observability.*calibration|planted.*bug|calibration.*probe' $WORKFLOWS 2>/dev/null)

[[ -z "$GATE" ]] \
  && echo "medium|.github/workflows|no CI job re-runs the calibration catalogue|add a workflow triggered on changes to .claude/settings.json, otel config, or observability/*"

# Path-based triggers should include the instrumentation surfaces
if [[ -n "$GATE" ]]; then
  grep -qE 'paths:.*(otel|hooks|settings\.json|observability)' "$GATE" \
    || echo "low|$GATE|calibration workflow has no path filter|trigger on changes to instrumentation surfaces, not on every push"
fi
```

A drift signal worth catching: the catalogue passes in isolation but fails after a log-level rotation from `DEBUG` to `INFO`. The fixture didn't change; the visibility budget did.

## Step 6 — Findings Output

```markdown
# Audit Report — Observability Calibration

## Coverage scorecard

| Layer | Fixture present | Last run | Pass | Top issue |
|-------|:---------------:|:--------:|:----:|-----------|
| Parsing      | YES | <ts> | PASS | <one-line> |
| Persistence  | YES | <ts> | FAIL | <one-line> |
| IPC          | NO  | —    | —    | no fixture |
| Async race   | YES | <ts> | PASS | <one-line> |
| Concurrency  | NO  | —    | —    | no fixture |

## Findings

| Severity | Layer | Finding | Missing signal |
|----------|-------|---------|----------------|
```

## Output Schema

```markdown
# Audit Observability Calibration — <repo>

| Layers covered | Fixtures pass | Calibration gaps | Source-visible diagnosing |
|---------------:|--------------:|-----------------:|:-------------------------:|
| <n>/5 | <n>/<total> | <n> | yes/no |

Top fix: <one-liner — usually a missing fixture layer or a missing signal on one layer>
```

## Decision Rule

- **High** — project has OTel or structured-logging instrumentation but no planted-bug calibration **and** has had at least one ambiguous incident in the last 90 days (an incident where the team could not name the responsible layer from signals alone within the diagnostic budget)
- **High** — diagnosing harness has source-tree read access (false-pass condition)
- **High** — calibration gap on any layer where instrumentation exists but does not name the layer
- **Medium** — partial layer coverage (1–4 of 5 layers represented) with no incident pressure; or catalogue not re-run on instrumentation changes
- **Low** — catalogue exists and passes but no CI gate ties it to instrumentation changes

Severity escalates when paired with a [`audit-debug-log-retention`](audit-debug-log-retention.md) high finding — verbose unredacted logs that also fail calibration are noise, not observability.

## Idempotency

Read-only on detection (Steps 1–3, 5). Step 4 executes the runner, which submits fixture inputs to the application under test — those should be flagged as dev-flag-gated probes per the source page so the catalogue does not produce production-visible failures.

!!! warning
    A calibration gap means an agent reading current signals cannot diagnose a known failure. Treat as a verification regression: file a P1 instrumentation issue and re-run the audit after the fix lands. Do not close the catalogue gap by removing the fixture — that hides the gap.

## Remediation

- No catalogue → run `bootstrap-planted-bug-fixtures` (paired bootstrap, see issue #3477) or scaffold the five canonical fixtures from [`planted-bug-observability-calibration`](../verification/planted-bug-observability-calibration.md) §Building a Fixture Catalogue
- Missing layer → add a deterministic fixture per the table in the source page; signature must be reachable from instrumentation alone
- Source-visible diagnosing → tighten the runner's tool allowlist to signal readers only (`logs/`, `traces/`, OTel collector queries); drop `Read`/`Glob`/`Grep` against application source
- Calibration gap → add the named signal (correlation ID, span attribute, log level, metric granularity) for the failing layer; do not patch the planted bug
- Catalogue not re-run on instrumentation change → wire a CI job that triggers on changes to `.claude/settings.json`, OTel collector config, hook scripts, and any `observability/` path

## Related

- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](../verification/planted-bug-observability-calibration.md) — the source teaching; mechanism, pass criterion, fixture catalogue, anti-patterns
- [Audit Debug Log Retention](audit-debug-log-retention.md) — sibling audit on the plumbing side; high findings there often co-occur with calibration gaps
- [Bootstrap OTel Init](bootstrap-otel-init.md) — paired bootstrap for the instrumentation substrate this audit calibrates
- [Audit Eval Suite](audit-eval-suite.md) — eval suite quality on the application side; this audit applies the same shape to the observability stack
- [Audit Hooks Coverage](audit-hooks-coverage.md) — re-run the catalogue whenever hook coverage changes
- [Making Observability Legible to Agents](../observability/observability-legible-to-agents.md) — wiring signals into agent context so diagnosing harnesses have data to reason over
