---
title: "Audit Premature Completion"
description: "Sample recent agent-authored PRs, run the test suite against pre-patch and post-patch trees, classify each PR on the fixed-correct-code / failing-tests-remain matrix, and emit per-PR findings with reproduction-first remediations."
tags:
  - tool-agnostic
  - testing-verification
aliases:
  - fixing correct code audit
  - premature termination audit
  - inflated resolution audit
---

Packaged as: `.claude/skills/agent-readiness-audit-premature-completion/`

# Audit Premature Completion

> Sample recent agent-authored PRs, run the test suite against pre-patch and post-patch trees, classify on the fixed-correct-code / failing-tests-remain matrix, and emit reproduction-first remediations.

!!! info "Harness assumption"
    The runbook reads PRs from a Git host (GitHub, GitLab) via a CLI (`gh`, `glab`) and runs the project's test suite locally. Agent attribution is detected via PR author, branch prefix, or commit-message marker — translate per repo convention. See [Assumptions](index.md#assumptions).

[Premature Completion](../anti-patterns/premature-completion.md) names a failure mode four independent teams have measured: agents declare done on first-signal-of-progress while failing tests remain or before any test was run. SRI Lab found agents patch already-passing code **>50%** of the time across frontier models on 235 tasks; SWE-EVO surfaced **6.2 pp** of reported SWE-Bench resolutions as patches that fail untouched tests ([premature-completion.md §Four Names for the Same Failure](../anti-patterns/premature-completion.md)). This runbook turns the diagnostic into a recurring audit a project can run on its own agent traffic.

## Step 1 — Sample Agent-Authored PRs

```bash
# GitHub: PRs authored by an agent or its proxy account, last 90 days
AGENT_LOGINS=("claude[bot]" "github-actions[bot]" "copilot-swe-agent" "${AGENT_USER:-}")
for login in "${AGENT_LOGINS[@]}"; do
  [ -z "$login" ] && continue
  gh pr list --state all --search "author:${login} created:>$(date -d '90 days ago' +%Y-%m-%d)" \
    --json number,title,baseRefName,headRefName,mergedAt,closedAt --limit 200
done | jq -s 'add | unique_by(.number)'
```

Sample N=30 PRs (or all if fewer) stratified by outcome — merged, closed-not-merged, open. Drop PRs that touch only docs or only config.

## Step 2 — Reconstruct Pre-Patch and Post-Patch Trees

For each sampled PR, check out two trees: the merge-base and the head.

```bash
for pr in $PR_NUMBERS; do
  WT="/tmp/audit-pc/$pr"
  rm -rf "$WT" && mkdir -p "$WT"

  # Pre-patch: merge-base of head against base
  HEAD=$(gh pr view "$pr" --json headRefOid -q .headRefOid)
  BASE=$(gh pr view "$pr" --json baseRefOid -q .baseRefOid)
  MB=$(git merge-base "$BASE" "$HEAD")
  git worktree add "$WT/pre" "$MB"
  git worktree add "$WT/post" "$HEAD"
done
```

Use worktrees, not stash-based switching — the audit must run multiple PRs in parallel and contaminating the working tree corrupts the result.

## Step 3 — Run the Test Suite Against Both Trees

Discover the project's test command from `Makefile`, `package.json` scripts, `pyproject.toml`, or `justfile` (same detection used by [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) §Step 1).

```bash
TEST_CMD="${TEST_CMD:-$(jq -r '.scripts.test // empty' package.json 2>/dev/null)}"
[ -z "$TEST_CMD" ] && TEST_CMD="$(grep -E '^test:' Makefile 2>/dev/null | head -1 | cut -d: -f2-)"
[ -z "$TEST_CMD" ] && { echo "FAIL: no test command discovered"; exit 1; }

run_tests() {
  ( cd "$1" && timeout 600 bash -c "$TEST_CMD" >"$1/.audit.log" 2>&1; echo $? > "$1/.audit.exit" )
}

for pr in $PR_NUMBERS; do
  run_tests "/tmp/audit-pc/$pr/pre"
  run_tests "/tmp/audit-pc/$pr/post"
done
```

Cap each invocation at 10 minutes. Tests that hang or time out are flagged but not classified — premature-completion is about declared-done, not declared-stuck.

## Step 4 — Classify Each PR

For each PR build the 2×2 matrix of pre/post test outcomes:

| Pre | Post | Classification |
|----:|----:|----------------|
| pass | pass | **Fixed correct code** — patch had no observable effect (high signal of premature completion if the PR claimed a fix) |
| fail | pass | **Real fix** — expected outcome |
| fail | fail | **Premature completion** — patch did not resolve the failing tests |
| pass | fail | **Regression** — separate failure mode; flag but do not classify under this audit |

```python
import json, subprocess, pathlib

def classify(pr):
    pre = (pathlib.Path(f"/tmp/audit-pc/{pr}/pre/.audit.exit").read_text().strip() == "0")
    post = (pathlib.Path(f"/tmp/audit-pc/{pr}/post/.audit.exit").read_text().strip() == "0")
    if pre and post: return "fixed-correct-code"
    if not pre and post: return "real-fix"
    if not pre and not post: return "premature-completion"
    return "regression"
```

The audit's two headline metrics:

- **False-completion rate** = (fixed-correct-code + premature-completion) / (real-fix + fixed-correct-code + premature-completion). Expected baseline from [premature-completion.md](../anti-patterns/premature-completion.md): >50% on weak models, near zero on frontier. Project-specific gate: ≤ 5%.
- **Inflated-resolution delta** = premature-completion count / total claimed-fix PRs. Per [arxiv 2503.15223](https://arxiv.org/html/2503.15223v1) the SWE-Bench baseline is 6.2 pp.

## Step 5 — Cross-Check Against Pre-Completion Hook Coverage

A project running [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) on every Stop event should never ship a `premature-completion` row — the hook would have blocked the agent at task boundary. A finding here while the hook is wired means one of:

1. The hook's checklist does not include the failing tests (Coding-task `tests` command points at the wrong runner).
2. The agent committed-and-stopped without a Stop event firing (e.g., the harness terminated abnormally).
3. The discovered test command runs only a subset (e.g., `pytest tests/unit/` while the failing test lives in `tests/integration/`).

Each cross-check is a separate finding. Do not collapse them.

## Step 6 — Emit Findings

```markdown
# Audit Report — Premature Completion

## Headline metrics

| Metric | Value | Gate |
|--------|------:|------|
| False-completion rate | <pct>% | ≤ 5% |
| Inflated-resolution delta | <pct>% | ≤ 1% |
| Hook coverage paradox | <count> | 0 |

## Per-PR findings

| PR | Title | Pre | Post | Classification |
|----|-------|:---:|:----:|----------------|

## Top fixes

| Severity | Finding | Source page | Suggested mitigation |
|----------|---------|-------------|----------------------|
| high | <n> PRs classified premature-completion | premature-completion.md §Mitigations That Work | Wire reproduction-first prompt + runtime-enforced verification |
```

## Step 7 — Hand Off

For high false-completion rates, point the user at the three evidence-backed mitigations from [premature-completion.md §Mitigations That Work](../anti-patterns/premature-completion.md):

1. Reproduction-first prompt — moves GPT-5.4 mini from 24% to 77% on the SRI Lab task.
2. Runtime-enforced verification — ForgeCode reports 81.8% on TermBench 2.0 with this change.
3. Pre-completion checklists as harness variables — install via [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md).

Mitigations that look operational but do not work alone are listed in [premature-completion.md §Mitigations That Don't Work Alone](../anti-patterns/premature-completion.md) — do not propose them as remediations.

## Idempotency

Re-running on the same PR set with the same test command produces identical output. Re-running after a mitigation produces a delta showing the rate change.

## Output Schema

```markdown
# Audit Premature Completion — <repo>

| PRs sampled | Real fix | Fixed correct code | Premature completion | Regression |
|------------:|--------:|-------------------:|---------------------:|-----------:|
| <n> | <n> | <n> | <n> | <n> |

False-completion rate: <pct>%
Top fix: <one-liner>
```

## Related

- [Premature Completion](../anti-patterns/premature-completion.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md)
- [Audit Eval Suite](audit-eval-suite.md)
- [Audit Hooks Coverage](audit-hooks-coverage.md)
