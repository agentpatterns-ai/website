---
title: "Bootstrap Incident-to-Eval Pipeline"
description: "Detect existing incident sources, scaffold an incident-to-eval pipeline that converts production failures into regression eval cases with severity tiers, generate the CI gate that blocks deploys on P0 failures."
tags:
  - tool-agnostic
  - testing-verification
  - evals
aliases:
  - failure to eval pipeline
  - production regression evals scaffold
  - incident eval synthesis
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-incident-to-eval/`

# Bootstrap Incident-to-Eval Pipeline

> Convert each production incident involving an LLM feature into a regression eval case. Scaffold the extraction template, the eval-case schema, and the tiered CI gate that blocks deploys on P0 regressions.

!!! info "Harness assumption"
    Pairs with the eval suite from [`bootstrap-eval-suite`](bootstrap-eval-suite.md) — assumes `evals/` exists and a runner is wired. If not, run that runbook first.

!!! info "Applicability"
    Apply when the project ships an LLM feature to real users, has any structured incident reporting (postmortems, error logs, ticket history), and a CI/CD pipeline. Skip pre-launch projects where production incidents do not yet exist.

Manually authored evals reflect what developers *think* will go wrong; production incidents reveal what *actually* goes wrong. Each incident is a candidate regression case. Rules from [`incident-to-eval-synthesis`](../verification/incident-to-eval-synthesis.md), [`golden-query-pairs-regression`](../verification/golden-query-pairs-regression.md), and [`eval-driven-development`](../workflows/eval-driven-development.md).

## Step 1 — Detect Incident Sources

```bash
# Postmortems
find . -path "*/postmortems/*.md" -o -path "*/incidents/*.md" 2>/dev/null

# Issue tracker (GitHub) — issues labelled bug/incident/regression
gh issue list --label "bug,incident,regression" --state all --limit 100 --json number,title,labels 2>/dev/null

# Error monitoring (best-effort heuristics)
test -f sentry.properties && echo "sentry configured"
grep -rE "OTLP|otel|opentelemetry" --include="*.{yaml,yml,json,toml}" 2>/dev/null

# Existing eval suite
test -d evals && find evals -name "*.{yaml,json,py}" | head -20
```

Decision rules:

- No postmortems, no labelled bug issues, no error monitoring → no signal source. Defer this runbook; ship `bootstrap-eval-suite` with a synthetic seed and revisit after first incident.
- Postmortems exist but no eval suite → run [`bootstrap-eval-suite`](bootstrap-eval-suite.md) first; come back here.
- Both exist → proceed.

## Step 2 — Scaffold the Extraction Template

Create `evals/incidents/_template.yaml`:

```yaml
# Incident → eval extraction template.
# One file per incident. Filename: incident-<id>.yaml.
incident_id: <e.g. INC-2026-0042>
date: <YYYY-MM-DD>
source: <postmortem url | issue url | log id>

failure_mode: <short label, e.g. hallucinated_policy, wrong_tool_selection, format_drift>

input:
  description: <one sentence describing what triggered the failure>
  payload: |
    <minimal reproducible input>

actual_output: |
  <verbatim output that exhibited the failure>

expected_output: |
  <what should have happened, per domain expert>

acceptance_criteria:
  - <criterion 1>
  - <criterion 2>

grader: <assertion | regex | llm_judge | hybrid>
severity: <P0 | P1 | P2>
tags: [<tag1>, <tag2>]

root_cause: |
  <one paragraph: why the model produced the wrong output>

evict_when: <condition under which this case is no longer relevant — e.g. "model upgraded past v5", "feature deprecated">
```

Severity assignment:

| Severity | Definition | CI behavior |
|----------|------------|-------------|
| P0 | Safety violation, data leak, complete task failure | Blocks release at any failure |
| P1 | Quality regression, accuracy drop on known-good case | Warns; explicit override required |
| P2 | Style or formatting drift | Logs only |

Reference: [`incident-to-eval-synthesis` §Tiered Blocking](../verification/incident-to-eval-synthesis.md#tiered-blocking-in-cicd).

## Step 3 — Scaffold the Cost-Benefit Filter

Not every incident becomes an eval. Create `evals/incidents/INTAKE.md`:

```markdown
# Incident Intake Filter

Apply this filter before opening a new `incident-<id>.yaml`.

| Failure type | Eval strategy | Skip? |
|---|---|---|
| Deterministic format error (wrong JSON, missing field) | assertion / regex | No — cheap |
| Semantic failure (wrong fact, hallucination) | llm_judge | No |
| Security / safety violation | mandatory P0 | No, regardless of frequency |
| One-off transient issue (corrupt input, network blip) | — | Skip; fix upstream |
| Pre-existing bug unrelated to the LLM | — | Skip; route to normal bug tracker |

If the incident clears the filter, copy `_template.yaml` to `incident-<id>.yaml` and fill in.
```

## Step 4 — Scaffold the Runner Hook

Add an entry point that walks `evals/incidents/`, runs each case, and groups results by severity. If [`bootstrap-eval-suite`](bootstrap-eval-suite.md) already shipped a runner, extend it; otherwise create `evals/run-incidents.py`:

```python
#!/usr/bin/env python3
"""Run all incident-derived eval cases. Emit results grouped by severity."""
import json, sys, yaml, glob

CASES = glob.glob("evals/incidents/incident-*.yaml")
results = {"P0": [], "P1": [], "P2": []}

for path in CASES:
    with open(path) as f:
        case = yaml.safe_load(f)
    severity = case.get("severity", "P2")
    # Substitute project's runner here:
    passed = run_case(case)  # noqa: F821
    results[severity].append({"id": case["incident_id"], "passed": passed, "path": path})

summary = {sev: {"total": len(cs), "failed": sum(1 for c in cs if not c["passed"])} for sev, cs in results.items()}
print(json.dumps({"summary": summary, "results": results}, indent=2))

# Exit code: 1 if any P0 failed, 0 otherwise
sys.exit(1 if summary["P0"]["failed"] > 0 else 0)
```

The exit code is the CI gate: P0 failures block; P1/P2 are reported but do not block.

## Step 5 — Wire CI

Add a job to `.github/workflows/evals.yml` (create if absent):

```yaml
name: Incident Evals
on:
  pull_request:
  push:
    branches: [main]

jobs:
  incident-evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run incident-derived evals
        run: python evals/run-incidents.py | tee evals/results.json
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: incident-eval-results
          path: evals/results.json
```

P0 failures cause the job to fail (non-zero exit). Branch protection on `main` should require this job.

## Step 6 — Seed with One Real Incident

A pipeline with no cases is theatre. Pick the most recent qualifying postmortem or labelled issue and walk it through the template. If the team has not yet had an incident, ship the scaffold and document the wait:

```markdown
# evals/incidents/README.md

This directory captures incident-derived regression cases. Pipeline live since <YYYY-MM-DD>.

Cases: 0 (no qualifying incident yet — pipeline ready).
```

When the first incident lands, populate `incident-<id>.yaml` and watch the gate fire.

## Step 7 — Document in AGENTS.md

```markdown
## Incident-to-eval pipeline

Production incidents are converted to regression eval cases under `evals/incidents/`. Severity tiers (P0/P1/P2) drive CI behavior — see `evals/incidents/INTAKE.md`. New incidents that match the intake filter MUST land an eval case before the underlying fix merges.
```

## Idempotency

Re-running detects existing template, INTAKE.md, runner, and CI workflow; only creates files that are missing. Existing incident cases are never touched.

## Output Schema

```markdown
# Bootstrap Incident-to-Eval Pipeline — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | evals/incidents/_template.yaml | extraction template |
| Created | evals/incidents/INTAKE.md | cost-benefit filter |
| Created | evals/run-incidents.py | runner entry point |
| Modified | .github/workflows/evals.yml | added incident-evals job |
| Modified | AGENTS.md | added pipeline pointer |

Seed cases: <n>
```

## Related

- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md)
- [Golden Query Pairs Regression](../verification/golden-query-pairs-regression.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
- [Bootstrap Eval Suite](bootstrap-eval-suite.md)
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md)
