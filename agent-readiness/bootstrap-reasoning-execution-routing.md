---
title: "Bootstrap Reasoning–Execution Model Routing"
description: "Configure the agent harness to route reasoning to a frontier model and execution to a fast/cheap model, pin model IDs per role to defeat alias drift, and emit a smoke-test that proves the routing is live before declaring complete — invoke when adopting a multi-model harness or when token cost is dominated by execution-class calls."
tags:
  - tool-agnostic
  - cost-performance
  - agent-design
aliases:
  - model routing bootstrap
  - reasoning execution split
  - per-role model pinning
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-reasoning-execution-routing/`

# Bootstrap Reasoning–Execution Model Routing

> Configure model routing across the agent harness — frontier model for reasoning/planning, fast/cheap model for execution — pin model IDs per role to prevent alias drift, and validate with a smoke-test before declaring done.

!!! info "Harness assumption"
    Claude Code today is the canonical target. The harness exposes per-role model selection via `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL` (and provider-specific equivalents on Bedrock, Vertex, Foundry). For Cursor, Aider, Copilot, and Gemini, translate to that harness's model-config schema — see [`harness-translation`](harness-translation.md).

!!! info "Applicability"
    Skip when the harness offers only one model tier (no fast/cheap counterpart) or when the agent's workload is uniformly one class. Run when token cost is dominated by execution-class work, when reasoning quality regresses on cheap-model defaults, or when sub-agents already differ by purpose (planner vs executor).

The reasoning–execution split is the foundational pattern for scaling agentic systems ([arXiv:2602.10479](https://arxiv.org/abs/2602.10479), via [`cognitive-reasoning-execution-separation`](../agent-design/cognitive-reasoning-execution-separation.md)). Routing reasoning to a frontier model while keeping execution on fast/cheap models captures the cost lever the split enables — without the routing wired, the architecture exists in name only. Rules from [`cognitive-reasoning-execution-separation`](../agent-design/cognitive-reasoning-execution-separation.md), [`feature-flags`](../tools/claude/feature-flags.md), [`managed-settings-drop-in`](../tools/claude/managed-settings-drop-in.md), and [`agent-teams`](../tools/claude/agent-teams.md).

## Step 1 — Detect Current Routing

```bash
# Claude Code: detect already-set model env vars
env | grep -E '^ANTHROPIC_(DEFAULT_(OPUS|SONNET|HAIKU)_MODEL|API_KEY|MODEL)=' \
  | grep -v API_KEY

# Per-sub-agent model: frontmatter `model:` field
grep -lE '^model:' .claude/agents/*.md 2>/dev/null

# Per-skill recommended model
grep -lE '^model:|recommended-model:' .claude/skills/**/SKILL.md 2>/dev/null
```

If at least one sub-agent already sets a `model:` field that differs from the harness default, the project has partial routing. Capture the current state before changing anything.

## Step 2 — Classify Sub-Agents and Skills by Role

```bash
for f in .claude/agents/*.md; do
  body=$(awk '/^---$/{c++; next} c==2{print}' "$f")
  case "$body" in
    *plan*|*reason*|*decompose*|*analyze*|*review*|*audit*|*assess*) role=reasoning ;;
    *execute*|*apply*|*write*|*format*|*lint*|*compile*) role=execution ;;
    *) role=ambiguous ;;
  esac
  echo "$role | $f"
done
```

Reasoning roles: planning, decomposition, multi-step review, audit, assessment, prompt-injection analysis. Execution roles: file edits, format passes, lint runs, predictable refactors, single-turn extractions.

## Step 3 — Pin Model IDs

Pin specific model versions, not aliases. Aliases drift silently — `claude-sonnet-latest` resolves to a different version next quarter and any eval baseline you carried no longer applies ([`feature-flags`](../tools/claude/feature-flags.md)).

```bash
cat > .claude/managed-settings.json.example <<'JSON'
{
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5-20251001"
  }
}
JSON
```

For Bedrock, Vertex, or Foundry deployments, replace the value with the provider-specific full model ID — alias resolution rules differ per platform ([`feature-flags`](../tools/claude/feature-flags.md)).

## Step 4 — Wire the Per-Role Override

```yaml
# .claude/agents/<reasoning-agent>.md frontmatter
---
name: planner
description: "Decompose a multi-step task into tool-call sequences with explicit dependencies."
model: opus
tools: [Read, Grep, Glob]
---

# .claude/agents/<execution-agent>.md frontmatter
---
name: file-formatter
description: "Apply formatting rules to a single file."
model: haiku
tools: [Read, Edit]
---
```

For ambiguous roles (single sub-agent doing both), default to the project's standard tier (`sonnet`) and split into two agents only when the cost or quality data justifies the refactor.

## Step 5 — Routing Smoke Test

Before declaring complete, prove the routing is live. Without the smoke-test, env vars or frontmatter values can be wrong without anyone noticing until a model evaluation run produces unexpected results.

```bash
# Inspect a recent session log to confirm models were selected per role
# Claude Code OTel: tool-decision events include model_id
jq '.events[] | select(.name == "claude_code.tool_decision")
   | {tool: .attributes.tool_name, model: .attributes.model_id, role: .attributes.subagent_type}' \
   "$CLAUDE_OTEL_OUT" | head -20
```

If OTel is not yet wired, run [`bootstrap-otel-init`](bootstrap-otel-init.md) first — without telemetry there is no evidence of which model handled which call. Heuristic alternative: dispatch a known reasoning-class sub-agent and an execution-class sub-agent in test mode and inspect the response-headers `x-model` value if the SDK surfaces it.

## Step 6 — Cost & Quality Baseline

Capture pre/post numbers so the routing change is auditable. Without a baseline, "reasoning routed to opus" is opinion, not policy.

```bash
# 14-day baseline: total tokens, total cost, average wall-clock per task
gh api graphql -f query='
  query { repository(owner:"...", name:"...") {
    object(expression:"main") { ... on Commit { history(first:50) { nodes { messageHeadline } } } }
  } }'

# Compare reasoning vs execution model spend (OTel claude_code.api.tokens_total grouped by model_id)
```

Document the baseline alongside the routing change — see the eval suite contract in [`bootstrap-eval-suite`](bootstrap-eval-suite.md).

## Step 7 — Register the Routing in AGENTS.md

Routing is not discoverable from sub-agent files alone — surface it in `AGENTS.md` so future contributors and audits see the policy.

```markdown
## Model routing

- Reasoning sub-agents (planner, reviewer, assess-*) → `claude-opus-4-7`
- Execution sub-agents (formatter, lint-runner, single-file edits) → `claude-haiku-4-5-20251001`
- Default tier (un-tagged sub-agents) → `claude-sonnet-4-6`
- Pin model IDs in `.claude/managed-settings.json`; do not use `*-latest` aliases.
```

## Step 8 — Validation Checklist

```bash
# 1. Pinned models, not aliases
grep -E 'ANTHROPIC_DEFAULT_.*=.*latest' .claude/managed-settings.json && echo "FAIL: alias instead of pinned ID"

# 2. Every reasoning-class sub-agent has model: opus|sonnet
for f in $(grep -l 'plan\|reason\|decompose\|review\|audit' .claude/agents/*.md); do
  yq -e '.model' "$f" >/dev/null 2>&1 || echo "FAIL: $f missing model: field"
done

# 3. AGENTS.md documents the policy
grep -qi 'model routing' AGENTS.md || echo "FAIL: routing policy not surfaced in AGENTS.md"
```

## Idempotency

Re-runnable. Step 1 detects the existing state; Steps 3–7 produce no diff when the routing is already aligned.

## Output Schema

```markdown
# Bootstrap Reasoning–Execution Routing — <repo>

| Sub-agents tagged | Reasoning | Execution | Pinned models | OTel evidence |
|------------------:|----------:|----------:|:-------------:|:-------------:|
| <n> | <n> | <n> | ✅/❌ | ✅/❌ |

Top fix: <one-liner — usually pin a model ID instead of an alias, or add OTel before declaring complete>
```

## Remediation

- [`bootstrap-otel-init`](bootstrap-otel-init.md) — required for the routing smoke-test (Step 5)
- [`bootstrap-eval-suite`](bootstrap-eval-suite.md) — measure quality regression after routing change; pair with per-model ablation in [`audit-eval-suite`](audit-eval-suite.md)
- [`audit-debug-log-retention`](audit-debug-log-retention.md) — model-id is a cost-attribution field; ensure it survives log redaction

## Related

- [Cognitive Reasoning vs Execution](../agent-design/cognitive-reasoning-execution-separation.md)
- [Feature Flags (Claude Code)](../tools/claude/feature-flags.md)
- [Managed Settings Drop-In](../tools/claude/managed-settings-drop-in.md)
- [Agent Teams (Claude Code)](../tools/claude/agent-teams.md)
- [Bootstrap OTel Init](bootstrap-otel-init.md)
- [Audit Eval Suite](audit-eval-suite.md)
