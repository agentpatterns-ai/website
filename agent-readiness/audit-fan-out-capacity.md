---
title: "Audit Fan-Out Capacity"
description: "Locate parallel agent dispatch sites, extract batch size N and concurrency caps, validate against the project's rate-limit tier and cost budget, detect missing staggering and 429-retry storms, and emit per-site capacity findings."
tags:
  - tool-agnostic
  - multi-agent
  - cost-performance
aliases:
  - bounded batch dispatch audit
  - fan-out concurrency audit
  - agent rate-limit audit
---

Packaged as: `.claude/skills/agent-readiness-audit-fan-out-capacity/`

# Audit Fan-Out Capacity

> Locate parallel agent dispatch sites, extract batch size N, validate against rate-limit tier and cost budget, detect missing staggering and retry storms, emit per-site capacity findings.

!!! info "Harness assumption"
    The runbook scans for fan-out patterns in the dispatching code (orchestrator scripts, slash commands that spawn sub-agents, CI matrix jobs that run agents in parallel). The patterns are language- and framework-agnostic — translate the regexes for your own dispatcher syntax. See [Assumptions](index.md#assumptions).

[Bounded Batch Dispatch](../multi-agent/bounded-batch-dispatch.md) §The Control Variable identifies batch size N as the single tuning knob against API rate limits and cost budget. Mis-set N is the most common multi-agent failure: too high triggers 429 storms; too low collapses throughput; uncalibrated combined with simultaneous launch causes the thundering-herd pattern documented in [Staggered Agent Launch](../multi-agent/staggered-agent-launch.md). This runbook audits every fan-out site for capacity correctness.

## Step 1 — Locate Fan-Out Sites

```bash
# Slash commands and orchestrator scripts spawning sub-agents
grep -rEn "spawn|dispatch|fan[_-]?out|parallel|background" \
  .claude/commands .claude/agents .github/workflows scripts 2>/dev/null \
  | grep -vE "//|^\s*#"

# Reference frame: project's bounded-batch helper
grep -rEn "batch[_-]?size|max[_-]?concurrency|MAX_PARALLEL|PARALLEL_AGENTS|N_WORKERS" \
  . --include="*.py" --include="*.ts" --include="*.js" --include="*.sh" 2>/dev/null

# CI matrix dispatching agents
find .github/workflows -name "*.y*ml" -exec grep -lE "matrix:|max-parallel:" {} \;
```

For each hit, capture the dispatcher path, the line, and the apparent N (literal, env var, or computed expression).

## Step 2 — Extract the Project's Rate-Limit Tier

The audit needs the API tier to know what N is safe. Pull from project config or env:

```bash
# Anthropic API tier (config or env)
test -n "${ANTHROPIC_TIER:-}" && echo "tier=$ANTHROPIC_TIER"
grep -hE "ANTHROPIC_TIER|tier\s*[:=]" .env* config/* 2>/dev/null

# OpenAI tier
test -n "${OPENAI_TIER:-}" && echo "tier=$OPENAI_TIER"

# Documented in AGENTS.md or CLAUDE.md
grep -nE "tier|rate[ -]?limit|RPM|TPM" AGENTS.md CLAUDE.md 2>/dev/null
```

If no tier is documented, fail the audit at this step — the project cannot calibrate N without knowing the ceiling. Recommend recording tier and per-model RPM/TPM in `AGENTS.md` (per [`bootstrap-agents-md`](bootstrap-agents-md.md)).

## Step 3 — Validate N Against the Tier

Apply the rule from [Bounded Batch Dispatch §When This Backfires](../multi-agent/bounded-batch-dispatch.md): keep N at 60–80% of the RPM ceiling. The expected RPM during a batch is approximately `N × retries_per_call`.

```python
def classify_n(n, rpm_ceiling, retries=1.5):
    expected_rpm = n * retries
    ratio = expected_rpm / rpm_ceiling
    if ratio > 1.0: return "high",   "N exceeds RPM ceiling — 429 storm guaranteed"
    if ratio > 0.8: return "medium", "N above 80% headroom — retry burst will trip ceiling"
    if ratio < 0.2 and n > 1: return "low", "N below 20% headroom — throughput unnecessarily capped"
    return "ok", ""
```

A finding here means rewrite N as a function of the documented tier rather than hard-coding the literal:

```python
N = int(0.7 * RATE_LIMIT_RPM / EXPECTED_RETRIES)
```

## Step 4 — Detect Cost-Budget Mis-Sizing

[Bounded Batch Dispatch §The Control Variable](../multi-agent/bounded-batch-dispatch.md) ties total cost to `queue_size × avg_tokens × price`. If the dispatcher does not compute and emit this estimate before launch, runs blow past budget invisibly.

```bash
# Look for an upfront cost estimate near the dispatch site
awk '/spawn|dispatch|fan[_-]?out/{lo=NR-5; hi=NR+15} \
     NR>=lo && NR<=hi && /cost|budget|token.*price|estimate/{print FILENAME":"NR": "$0}' \
     .claude/commands/*.md scripts/*.py 2>/dev/null
```

Findings:

- **No upfront estimate** → medium. Add a pre-dispatch print of `queue_size × N × avg_tokens × price`.
- **Estimate exists but no abort gate** → medium. Wire a `MAX_BUDGET_USD` env that fails the dispatch if the estimate exceeds it.

## Step 5 — Detect Thundering-Herd and Missing Stagger

[Staggered Agent Launch](../multi-agent/staggered-agent-launch.md) §When to Upgrade documents the failure: simultaneous spawn pushes a multi-second burst over the per-second token bucket even when the per-minute average is safe. The fix is per-agent stagger or file-locking on shared resources.

```bash
# Spawn calls in tight loops without stagger
grep -nE "(for|while).*spawn|background.*<<|&\s*$" \
  .claude/commands/*.md scripts/*.sh 2>/dev/null

# Look for sleep/jitter near spawn
grep -nE "sleep [0-9]|jitter|stagger" \
  .claude/commands/*.md scripts/*.sh 2>/dev/null
```

A spawn loop with no `sleep`, `jitter`, or queue-based pacing is a finding — high severity if the same loop also writes to a shared resource (file, database row, branch) without locking.

## Step 6 — Detect Wait-For-Any Pretending to Be Wait-For-All

Per [Bounded Batch Dispatch §Why Not a True Sliding Window](../multi-agent/bounded-batch-dispatch.md), LLM orchestrators expose only `wait-for-all` semantics. Code that *claims* to implement a sliding window inside an orchestrator typically replaces an in-flight agent with a new one mid-batch — but the orchestrator's wait blocks until the entire group is done, so the replacement does not actually parallelize.

Detection:

- A loop that calls `Task` (or the orchestrator's spawn primitive) inside a `while pending < N` block is a false sliding window. Flag and recommend either fixed-batch or moving the queue worker outside the LLM context.

## Step 7 — Emit Findings

```markdown
# Audit Report — Fan-Out Capacity

## Tier and ceiling
| Provider | Tier | RPM | TPM |
|----------|------|----:|----:|
| <provider> | <tier> | <rpm> | <tpm> |

## Per-site findings
| File | Line | N | Tier headroom | Stagger | Cost gate | Severity |
|------|-----:|--:|--------------:|:-------:|:---------:|----------|

## Top fixes
| Severity | Finding | Source page | Suggested rewrite |
|----------|---------|-------------|-------------------|
| high | N exceeds RPM ceiling at <file:line> | bounded-batch-dispatch.md §The Control Variable | rewrite N = int(0.7 × RPM / retries) |
```

## Step 8 — Hand Off

For high findings, propose the one-line N rewrite the user can land. For thundering-herd findings, point at [`bootstrap-loop-detector-hook`](bootstrap-loop-detector-hook.md) and the staggering pattern in [Staggered Agent Launch](../multi-agent/staggered-agent-launch.md). For missing cost gates, propose the env variable and pre-dispatch check.

## Idempotency

Read-only. Re-running on a clean repo produces no findings. Re-running after a fix produces a delta showing which sites moved into the `ok` band.

## Output Schema

```markdown
# Audit Fan-Out Capacity — <repo>

| Sites | N ok | N too high | N too low | Missing stagger | Missing cost gate |
|------:|-----:|-----------:|----------:|----------------:|------------------:|
| <n> | <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually a hard-coded N above tier headroom>
```

## Related

- [Bounded Batch Dispatch](../multi-agent/bounded-batch-dispatch.md)
- [Staggered Agent Launch](../multi-agent/staggered-agent-launch.md)
- [Async Non-Blocking Subagent Dispatch](../multi-agent/async-non-blocking-subagent-dispatch.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
- [Audit Subagent Definitions](audit-subagent-definitions.md)
