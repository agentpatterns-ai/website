---
title: "Bootstrap Eval Suite"
description: "Detect candidate units to test, mine real signals from issues and incidents, scaffold paired baseline/with-skill cases, generate a runner and CI gate, and ship the incident-to-eval template."
tags:
  - tool-agnostic
  - evals
  - testing-verification
aliases:
  - scaffold eval suite
  - evaluation harness bootstrap
  - skill eval suite scaffold
---

Packaged as: [`.claude/skills/agent-readiness-bootstrap-eval-suite`](../../.claude/skills/agent-readiness-bootstrap-eval-suite/SKILL.md)

# Bootstrap Eval Suite

> Detect units to test, mine real signals, scaffold paired cases, generate runner and CI gate, ship the incident-to-eval template.

!!! info "Harness assumption"
    Generated case files reference `.claude/skills/` and `.claude/agents/`. The runner and grader are harness-pluggable — see the `run_unit` contract in `evals/grader.py`. Translate the unit-loading mechanism to your harness; the case schema and discriminating-assertion model are tool-agnostic. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Defer this runbook until the project has an agent-customizable unit (skill, sub-agent, system-prompt fragment) worth measuring. Eval suites measure a unit under test — without one, the suite has nothing to discriminate against, and the scaffold becomes maintenance debt.

Without an eval suite, every prompt change, model upgrade, and skill rewrite is a guess. This runbook produces the minimum scaffold a team needs to start measuring — a small live suite — not the production-grade infrastructure a mature project ends up with. Cases are mined from real signals (issues, incidents, support tickets), never invented.

## Step 1 — Detect Existing Evals and Candidates

```bash
# Existing evals
find . -maxdepth 6 -type d \( -name "evals" -o -name "evaluations" -o -name "eval" \)

# Candidate units to test
find . -path "*/.claude/skills/*/SKILL.md" -o -path "*/.claude/agents/*.md"

# Existing CI gating on evals
grep -rE "evals|evaluation" .github/workflows/ 2>/dev/null

# Real signals to mine for cases
test -d .git && git log --since="6 months ago" --grep="fix\|bug\|incident\|regression" --oneline | head -50
gh issue list --state closed --label bug --limit 30 2>/dev/null
gh issue list --state closed --label incident --limit 30 2>/dev/null
```

Decision rules:

- **`evals/` exists** → audit, do not overwrite; merge new cases only
- **No skills/agents to test** → defer this runbook (see the Applicability note above). If the project intends to ship a skill, run [`bootstrap-skill-template`](bootstrap-skill-template.md) first; a system-prompt fragment or sub-agent is also a valid unit. If no agent-customizable unit is planned, this runbook does not apply.
- **No mineable signals** → ask the user for 5–10 representative tasks; do not invent

## Step 2 — Identify the Unit Under Test

Ask the user (or infer from context): which skill, prompt, or sub-agent does the suite measure? The first eval suite covers exactly one unit — adding a second unit is a follow-up.

## Step 3 — Mine Real Cases

For each candidate signal, capture:

- The user message that triggered the failure
- What the unit produced (or failed to produce)
- What the unit should have produced
- The class of failure (trigger precision vs output quality)

Aim for 5–10 cases. Quality beats coverage — a small live suite beats a large dead one.

## Step 4 — Generate Directory Structure

```
evals/
├── README.md
├── cases/
│   ├── <case-id>.yaml
│   └── ...
├── grader.py
├── run.sh
└── incident-template.md
```

Create:

```bash
mkdir -p evals/cases
```

## Step 5 — Scaffold Case Files

Each case follows this exact schema. The two axes — output quality (does it work?) and trigger precision (does the description activate it?) — are the [skill-evals](../verification/skill-evals.md) framework:

```yaml
# evals/cases/<descriptive-id>.yaml
id: <descriptive-id>
priority: P0          # P0 blocks merge, P1 warns, P2 reports only
axis: trigger-precision   # or: output-quality
unit_under_test: <skill-name>

input:
  user_message: |
    <verbatim message that triggered the failure>
  context_files: []   # optional: list of files preloaded into context

expected:
  with_unit:
    skill_invoked: <skill-name>
    output_contains: ["<substring>", "<substring>"]
    structural:
      - kind: cmd
        run: "<command that must exit 0>"
  baseline:           # what happens without the unit
    skill_invoked: null   # or: <other skill> if a different one should fire

assertions:
  - kind: discriminating
    fail_if: "with_unit.skill_invoked == baseline.skill_invoked"
  - kind: structural
    cmd: "<deterministic check>"
  # Reserve LLM-as-judge for genuinely subjective output:
  # - kind: judge
  #   rubric: "<≤5-line rubric>"
  #   pass_if: "score >= 4 and not 'hallucination' in rationale"
```

Generate one case per mined signal. Use real input verbatim; do not paraphrase.

## Step 6 — Generate the Runner

`evals/run.sh`:

```bash
#!/usr/bin/env bash
# Run every case twice (with and without the unit) and diff outcomes.
# Output: per-case pass/fail; aggregate exit code = 1 if any P0 fails.
set -euo pipefail

UNIT="${1:-}"
[[ -z "$UNIT" ]] && { echo "usage: $0 <unit-name>"; exit 2; }

FAIL_P0=0
RESULTS=()

for case in evals/cases/*.yaml; do
  ID=$(yq '.id' "$case")
  PRI=$(yq '.priority' "$case")

  WITH=$(python3 evals/grader.py --case "$case" --mode with-unit --unit "$UNIT")
  BASE=$(python3 evals/grader.py --case "$case" --mode baseline --unit "$UNIT")
  RESULT=$(python3 evals/grader.py --case "$case" --with "$WITH" --baseline "$BASE")

  STATUS=$(echo "$RESULT" | jq -r '.status')
  RESULTS+=("$(jq -nc --arg id "$ID" --arg pri "$PRI" --arg s "$STATUS" '{id:$id,priority:$pri,status:$s}')")

  [[ "$STATUS" == "fail" && "$PRI" == "P0" ]] && FAIL_P0=$((FAIL_P0+1))
done

printf '%s\n' "${RESULTS[@]}" | jq -s '.'
[[ $FAIL_P0 -gt 0 ]] && exit 1 || exit 0
```

`evals/grader.py` is the assertion engine. Implement at minimum:

```python
# evals/grader.py — outline
import argparse, json, subprocess, yaml, sys

def run_unit(case, mode, unit):
    """Invoke the agent harness against the case input. Mode controls whether
    the unit is loaded. Returns the agent's response as a structured dict."""
    # Implementation depends on the harness:
    # - Claude Code: subprocess with `--skip-skills <unit>` for baseline
    # - Cursor: equivalent flag
    # - API direct: include / exclude the system prompt fragment
    raise NotImplementedError("wire to your harness")

def grade(case, with_, baseline):
    failures = []
    for a in case["assertions"]:
        kind = a["kind"]
        if kind == "discriminating":
            # Confirm the unit changed the outcome
            if eval(a["fail_if"], {"with_unit": with_, "baseline": baseline}):
                failures.append(a)
        elif kind == "structural":
            r = subprocess.run(a["cmd"], shell=True, capture_output=True)
            if r.returncode != 0:
                failures.append({"kind": "structural", "stderr": r.stderr.decode()})
        elif kind == "judge":
            # Invoke an LLM with the rubric; pass_if condition decides
            ...
    return {"status": "pass" if not failures else "fail", "failures": failures}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    p.add_argument("--mode")
    p.add_argument("--unit")
    p.add_argument("--with")
    p.add_argument("--baseline")
    args = p.parse_args()
    case = yaml.safe_load(open(args.case))
    if args.mode:
        print(json.dumps(run_unit(case, args.mode, args.unit)))
    else:
        result = grade(case, json.loads(getattr(args, "with")), json.loads(args.baseline))
        print(json.dumps(result))
```

The `run_unit` function wires to whatever harness the project uses. Document that contract in `evals/README.md`.

## Step 7 — Generate the CI Gate

For projects on GitHub Actions, `.github/workflows/evals.yml`:

```yaml
name: evals
on:
  pull_request:
    paths:
      - '.claude/skills/**'
      - '.claude/agents/**'
      - 'evals/**'
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml
      - run: bash evals/run.sh <unit-name>
```

Adapt to the project's CI: GitLab CI, CircleCI, Buildkite, or self-hosted runners need equivalent definitions; the `run.sh` invocation is what matters. Match the runner OS to a Unix-shell environment (the runner is bash). For Windows-only CI, port `run.sh` to PowerShell or run under WSL. Set the workflow as a required check on the default branch.

## Step 8 — Ship the Incident-to-Eval Template

`evals/incident-template.md`:

```markdown
# Incident → Eval Case

## Incident

- **Date**: <YYYY-MM-DD>
- **Symptom**: <one sentence>
- **Trigger**: <what the user did to surface it>
- **Root cause**: <one sentence>

## Case construction

- **Axis**: <trigger-precision | output-quality>
- **Priority**: <P0 | P1 | P2>
- **User message**: <verbatim>
- **Expected with unit**: <structural assertions that would have caught this>
- **Expected baseline**: <what without-unit produces>

## Discriminating assertion

`<fail_if expression>`

## File created

`evals/cases/<id>.yaml`
```

The [incident-to-eval](../verification/incident-to-eval-synthesis.md) loop is the maintenance mechanism. Without it the suite ages out.

## Step 9 — Smoke Test

Run the suite locally:

```bash
bash evals/run.sh <unit-name>
```

Confirm at least one case passes (P0) and the runner exits 0 when expected. If everything fails, the runner is wired wrong; debug before merging.

## Idempotency

Re-running adds new cases; never overwrites existing ones. Existing cases are touched only if their underlying signal (issue / incident) changes.

## Output Schema

```markdown
# Bootstrap Eval Suite — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | evals/run.sh | mode 0755 |
| Created | evals/grader.py | <n> lines |
| Created | evals/cases/<id>.yaml | <n> cases (P0: <n>, P1: <n>) |
| Created | evals/incident-template.md | |
| Created | .github/workflows/evals.yml | |

Local run: <n>/<n> P0 pass
```

## Related

- [Eval-Driven Development](../workflows/eval-driven-development.md)
- [Skill Evals](../verification/skill-evals.md)
- [Incident-to-Eval Synthesis](../verification/incident-to-eval-synthesis.md)
- [Layered Accuracy Defense](../verification/layered-accuracy-defense.md)
