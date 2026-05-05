---
title: "Audit Eval Suite"
description: "Locate the project's eval suite, validate scaffold completeness, score case provenance and discrimination, and check coverage of three structural detection gaps — idle-state, build parity, and per-model ablation."
tags:
  - tool-agnostic
  - evals
  - testing-verification
aliases:
  - eval suite audit
  - evals quality check
  - eval coverage audit
---

Packaged as: `.claude/skills/agent-readiness-audit-eval-suite/`

# Audit Eval Suite

> Locate the eval suite, validate scaffold completeness and case provenance, score discrimination, and check coverage of idle-state, build-parity, and per-model ablation gaps.

!!! info "Harness assumption"
    Suite shape matches [`bootstrap-eval-suite`](bootstrap-eval-suite.md): cases under `evals/cases/*.yaml`, runner at `evals/run.sh`, grader at `evals/grader.py`, CI at `.github/workflows/evals.yml`. Translate paths if the project uses a different layout. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the project has no agent-customizable unit (skill, sub-agent, system-prompt fragment) — there is nothing to evaluate. Run [`bootstrap-eval-suite`](bootstrap-eval-suite.md) first if a unit exists but no suite does.

An eval suite that runs is not the same as an eval suite that discriminates. A scaffold can pass `run.sh` without testing whether the unit actually changes the outcome. Three structural gaps from the [April 2026 Claude Code postmortem](https://www.anthropic.com/engineering/april-23-postmortem) — idle-state, build parity, per-model ablation — escape standard suites because the suites only sweep input space. Rules from [`skill-evals`](../verification/skill-evals.md), [`harness-bug-postmortem-patterns`](../observability/harness-bug-postmortem-patterns.md), [`synthetic-ground-truth-fallacy`](../fallacies/synthetic-ground-truth-fallacy.md).

## Step 1 — Locate the Suite

```bash
find . -maxdepth 6 -type d \( -name "evals" -o -name "evaluations" -o -name "eval" \) \
  ! -path "*/node_modules/*" ! -path "*/.git/*"

CASES=$(find evals/cases -name "*.yaml" 2>/dev/null)
test -f evals/run.sh    || echo "high|no evals/run.sh|run bootstrap-eval-suite"
test -f evals/grader.py || echo "high|no evals/grader.py|run bootstrap-eval-suite"
test -f .github/workflows/evals.yml || echo "medium|no CI gate|wire evals into PR checks"
```

If no suite exists, abort and point to [`bootstrap-eval-suite`](bootstrap-eval-suite.md). Otherwise capture: case count, P0/P1/P2 split, runner contract, CI presence.

## Step 2 — Case Schema Validation

Every case must declare the fields the grader requires: `id`, `priority`, `axis`, `unit_under_test`, `input.user_message`, `expected.with_unit`, `expected.baseline`, and at least one assertion.

```bash
for case in $CASES; do
  python3 - "$case" <<'PY'
import sys, yaml
c = yaml.safe_load(open(sys.argv[1])) or {}
required = ['id', 'priority', 'axis', 'unit_under_test']
for r in required:
    if not c.get(r):
        print(f'high|{sys.argv[1]}|missing {r}|add the field')
if c.get('priority') not in ('P0', 'P1', 'P2'):
    print(f'high|{sys.argv[1]}|invalid priority {c.get("priority")}|use P0/P1/P2')
if c.get('axis') not in ('trigger-precision', 'output-quality'):
    print(f'medium|{sys.argv[1]}|axis is {c.get("axis")}|use trigger-precision or output-quality')
if not (c.get('input', {}) or {}).get('user_message'):
    print(f'high|{sys.argv[1]}|missing input.user_message|verbatim user input required')
asserts = c.get('assertions') or []
if not asserts:
    print(f'high|{sys.argv[1]}|no assertions|add at least one discriminating or structural assertion')
PY
done
```

## Step 3 — Discrimination Check

A case that does not differ between `with_unit` and `baseline` cannot signal whether the unit had any effect. Every case should carry at least one `discriminating` assertion.

```bash
for case in $CASES; do
  KIND=$(yq '.assertions[].kind' "$case" 2>/dev/null | sort -u)
  echo "$KIND" | grep -q discriminating \
    || echo "high|$case|no discriminating assertion|add fail_if comparing with_unit and baseline"
done
```

Without discrimination, the suite measures only that the unit runs, not that it does something. From [`skill-evals`](../verification/skill-evals.md): both axes (trigger precision *and* output quality) need explicit checks.

## Step 4 — Provenance Stamping

Cases authored by an LLM without human verification create feedback loops that degrade across generations ([`synthetic-ground-truth-fallacy`](../fallacies/synthetic-ground-truth-fallacy.md)). The runner must refuse to count `llm-only` unverified cases toward the P0 gate.

```bash
for case in $CASES; do
  AUTH=$(yq '.authored_by // ""' "$case")
  VER=$(yq '.verified_by // ""' "$case")
  [[ -z "$AUTH" ]] && echo "medium|$case|no authored_by stamp|mark human / llm-assisted / llm-only"
  [[ "$AUTH" == "llm-only" && -z "$VER" ]] \
    && echo "high|$case|llm-only without verified_by|human-verify or downgrade priority"
done
```

Cross-check `evals/run.sh` for an enforcement clause that excludes unverified `llm-only` cases from the P0 fail count:

```bash
grep -qE 'llm-only.*verified_by|verified_by.*null' evals/run.sh \
  || echo "medium|evals/run.sh|no provenance gate|add filter that drops unverified llm-only from P0"
```

## Step 5 — Idle-State Coverage

The thinking-history bug compounded only after 1h idle then resumed turns ([Anthropic postmortem](https://www.anthropic.com/engineering/april-23-postmortem)). Standard fresh-session evals miss it.

```bash
grep -lE "idle|warm|resumed|session_age|stale" evals/cases/*.yaml >/dev/null 2>&1 \
  || echo "medium|evals|no idle-state cases|add at least one case that exercises a resumed/idle session"
```

If the harness has any cache, TTL, or persisted-state primitive, idle-state cases are required. If sessions are stateless across turns, the gap does not apply — note in the report and skip.

## Step 6 — Build-Parity Coverage

Internal-only experiments and CLI suppressions can mask public regressions ([Anthropic postmortem](https://www.anthropic.com/engineering/april-23-postmortem)). Cases must run against the public-artifact build, not a developer build with internal flags enabled.

```bash
grep -qE "build:\s*public|artifact|release.build|public.build" evals/run.sh evals/cases/*.yaml 2>/dev/null \
  || echo "medium|evals|no build-parity declaration|run evals against the published artifact, not the dev build"

# Internal feature flags leaking into eval runs
grep -rE "INTERNAL_|EXPERIMENT_|DEV_ONLY" evals/ 2>/dev/null \
  | head -5 \
  | awk -F: '{print "low|"$1"|references internal flag "$2"|confirm the flag is set the same way in production"}'
```

If the project ships only one build, declare so in the report and skip.

## Step 7 — Per-Model Ablation Coverage

The verbosity-reduction prompt regressed quality 3% for both Opus 4.6 and 4.7; the original aggregate eval showed no regression. Per-model runs surfaced it ([Anthropic postmortem](https://www.anthropic.com/engineering/april-23-postmortem)).

```bash
MODELS=$(yq '.models // [] | length' evals/run.sh evals/config.yaml 2>/dev/null | sort -u | tail -1)
[[ -z "$MODELS" || "$MODELS" -lt 2 ]] \
  && echo "high|evals|fewer than 2 model families in matrix|add a second family (e.g., one Sonnet + one Opus, or Anthropic + OpenAI) and report per-model deltas"

grep -qE "per.model|per_model|matrix:.*model" evals/run.sh .github/workflows/evals.yml 2>/dev/null \
  || echo "medium|evals|no per-model reporting|emit deltas separately, not aggregated"
```

A single-model suite cannot detect regressions that surface only on a model rotation. From [`bootstrap-eval-suite`](bootstrap-eval-suite.md) Step 8b.

## Step 8 — Reviewer-Model Awareness

When the suite uses an LLM-as-judge assertion, the reviewer model is itself a harness variable. The thinking-history bug was caught by Opus 4.7 review and missed by Opus 4.6 ([Anthropic postmortem](https://www.anthropic.com/engineering/april-23-postmortem)).

```bash
grep -lE "kind:\s*judge" evals/cases/*.yaml 2>/dev/null | while read case; do
  RM=$(yq '.assertions[] | select(.kind == "judge") | .reviewer_model // ""' "$case")
  [[ -z "$RM" ]] && echo "medium|$case|judge assertion without reviewer_model|pin the reviewer model and rotate per release"
done
```

## Step 8b — Grader Calibration Dataset

Per [Evaluator Templates §Calibration Is Not Optional](../verification/evaluator-templates.md), an LLM judge that has not been calibrated against a paired human-graded set drifts silently across model rotations and prompt edits — the suite reports green while real quality regresses. The audit requires every judge prompt to ship with at least 20 paired (input, golden grade) examples and a calibration script that asserts judge agreement above a documented threshold.

```bash
# Locate calibration datasets paired with judge prompts
find evals -path "*/calibration/*.yaml" -o -name "calibration.yaml" 2>/dev/null

# Per judge prompt, count paired examples
for judge in $(grep -lE "kind:\s*judge" evals/cases/*.yaml 2>/dev/null); do
  PROMPT_ID=$(yq '.assertions[] | select(.kind == "judge") | .prompt_id // .judge_id // ""' "$judge" | head -1)
  [[ -z "$PROMPT_ID" ]] && continue
  CAL=$(find evals/calibration -name "${PROMPT_ID}*.yaml" 2>/dev/null | head -1)
  if [[ -z "$CAL" ]]; then
    echo "high|$judge|judge prompt $PROMPT_ID has no calibration dataset|create evals/calibration/${PROMPT_ID}.yaml with ≥20 human-graded examples"
  else
    N=$(yq '.examples // [] | length' "$CAL")
    [[ "$N" -lt 20 ]] && echo "medium|$CAL|only $N calibration examples (≥20 required)|add more golden cases until ≥20"
  fi
done

# Calibration runner exists and asserts agreement
grep -qE "calibrate|agreement|kappa|cohen" evals/run.sh evals/calibrate.sh 2>/dev/null \
  || echo "medium|evals|no calibration runner|add evals/calibrate.sh that runs each judge against its calibration set and exits non-zero if agreement < threshold"
```

A judge with no calibration dataset is a finding even when the case-side reviewer_model is pinned — the pin only stabilizes the model, not the prompt-to-rubric drift. Calibration runs belong on every release of the unit under test, not only on every model rotation.

## Step 9 — CI Gate Behavior

Confirm the gate exits non-zero on any P0 failure and reports per-case status:

```bash
grep -qE "FAIL_P0|exit 1.*P0|P0.*exit" evals/run.sh \
  || echo "high|evals/run.sh|no P0 fail gate|runner does not block merge on P0 fail; add exit 1 path"

grep -qE "name:\s*evals\b" .github/workflows/evals.yml >/dev/null 2>&1 \
  && grep -qE "required.*true|branch.protection" .github/workflows/evals.yml \
  || echo "low|.github/workflows/evals.yml|gate may not be a required check|set as required on default branch"
```

## Step 10 — Per-Case Scorecard

```markdown
# Audit Report — Eval Suite

## Coverage scorecard

| Dimension | Status | Notes |
|-----------|:------:|-------|
| Cases ≥ 5 | ✅/⚠️/❌ | <count>, P0:<n> P1:<n> P2:<n> |
| Discrimination | ✅/⚠️/❌ | <n> cases without discriminating assertion |
| Provenance | ✅/⚠️/❌ | <n> llm-only unverified |
| Idle-state | ✅/⚠️/❌/n/a | <one-line> |
| Build parity | ✅/⚠️/❌/n/a | <one-line> |
| Per-model ablation | ✅/⚠️/❌ | <n> models in matrix |
| CI P0 gate | ✅/⚠️/❌ | <one-line> |

## Findings

| Severity | File | Finding | Suggested fix |
|----------|------|---------|---------------|
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Eval Suite — <repo>

| Cases | Pass | Warn | Fail | Models | Idle | Build | P0 gate |
|------:|-----:|-----:|-----:|-------:|:----:|:-----:|:-------:|
| <n> | <n> | <n> | <n> | <n> | ✅/❌ | ✅/❌ | ✅/❌ |

Top fix: <one-liner — usually missing per-model ablation or discrimination>
```

## Remediation

- [Bootstrap Eval Suite](bootstrap-eval-suite.md) — scaffold the suite if missing; Step 8b adds per-model + provenance
- [Bootstrap Incident-to-Eval Pipeline](bootstrap-incident-to-eval.md) — feed regressions back into the suite as P0/P1/P2 cases
- For idle-state and build-parity, add cases mined from the project's own incident log

## Related

- [Eval-Driven Development](../workflows/eval-driven-development.md)
- [Skill Evals](../verification/skill-evals.md)
- [Harness Bug Postmortem Patterns](../observability/harness-bug-postmortem-patterns.md)
- [Nonstandard Errors in AI Agents](../verification/nonstandard-errors-ai-agents.md)
- [Synthetic Ground-Truth Fallacy](../fallacies/synthetic-ground-truth-fallacy.md)
- [Bootstrap Eval Suite](bootstrap-eval-suite.md)
- [Bootstrap Incident-to-Eval Pipeline](bootstrap-incident-to-eval.md)
