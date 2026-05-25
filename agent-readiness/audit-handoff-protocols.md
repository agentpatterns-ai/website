---
title: "Audit Handoff Protocols"
description: "Locate every multi-agent handoff boundary, validate that upstream agents declare an output schema and downstream agents reference it, detect raw-transcript forwarding and rigid schemas hiding uncertainty, emit per-handoff findings."
tags:
  - tool-agnostic
  - multi-agent
  - verification
aliases:
  - handoff schema audit
  - agent handoff audit
  - sub-agent return-shape audit
---

Packaged as: `.claude/skills/agent-readiness-audit-handoff-protocols/`

# Audit Handoff Protocols

> Locate handoff boundaries, validate output-schema declarations on upstream agents and schema references on downstream agents, detect raw-transcript forwarding, emit per-handoff findings.

!!! info "Harness assumption"
    Handoff boundaries appear as: sub-agent return blocks (`.claude/agents/*.md`), command files dispatching to multiple agents (`.claude/commands/*.md`), and orchestrator scripts that read upstream agent output. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the project defines fewer than two agents and no orchestrator dispatches to sub-agents — there are no handoffs to audit. Run when sub-agents fan out, or commands stage work across agents.

Each agent in a multi-stage pipeline operates in its own context window. Without a declared output schema at every handoff, the downstream agent reads either an unstructured prose dump (information loss) or a full transcript (context bloat). The MAST taxonomy of 1,600+ multi-agent traces names inter-agent misalignment as one of three primary failure categories ([MAST](https://arxiv.org/abs/2503.13657), via [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md)). Rules from [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md), [`sub-agents-fan-out`](../multi-agent/sub-agents-fan-out.md), [`bounded-batch-dispatch`](../multi-agent/bounded-batch-dispatch.md).

## Step 1 — Locate Handoff Boundaries

```bash
# Sub-agents and the commands that dispatch to them
SUBAGENTS=$(find . -path "*/.claude/agents/*.md" ! -path "*/.claude/worktrees/*")
COMMANDS=$(find . -path "*/.claude/commands/*.md" ! -path "*/.claude/worktrees/*")

# Orchestrator scripts that consume sub-agent output
grep -rlE "subagent_type|Agent\(|Task\(.*subagent" \
  .claude/skills/ scripts/ 2>/dev/null | head -20
```

For each, capture: which agent emits, which agent consumes, persistence medium (in-process return, file, GitHub issue/PR comment).

If no boundary is found, abort the audit with "no handoffs to audit".

## Step 2 — Output Schema Declaration

Every upstream agent should explicitly declare its output shape — either inside the body prose or in frontmatter (`returns:` field, schema reference, or output-template block).

```bash
for agent in $SUBAGENTS; do
  BODY=$(awk '/^---$/{c++; next} c==2{print}' "$agent")
  HAS_SCHEMA=false
  echo "$BODY" | grep -qiE "^## (returns|output|return shape|output schema)" && HAS_SCHEMA=true
  echo "$BODY" | grep -qE '```(json|yaml)' && HAS_SCHEMA=true
  yq -e '.returns // .output_schema // .output_template' "$agent" >/dev/null 2>&1 && HAS_SCHEMA=true
  [[ "$HAS_SCHEMA" == "false" ]] \
    && echo "high|$agent|no output schema declared|add a 'Returns:' section with field names, types, and one example"
done
```

A sub-agent without a declared return shape forces every downstream caller to parse prose. From [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md): structured handoffs eliminate parse-time ambiguity.

## Step 3 — Required Field Coverage

The handoff payload should carry at least: scope of work completed, conclusions / findings, items the next agent must address, unresolved questions. Missing fields cause downstream agents to fabricate.

```bash
for agent in $SUBAGENTS; do
  BODY=$(awk '/^---$/{c++; next} c==2{print}' "$agent")
  # Look for the four canonical fields by name or keyword
  for field in "completed|done|scope" "findings|conclusions|results" "needs.attention|next.steps|remediation" "unresolved|open.questions|caveats"; do
    echo "$BODY" | grep -qiE "$field" \
      || echo "medium|$agent|output schema missing $field|add the field; downstream cannot infer it from prose"
  done
done
```

Severity is `medium`, not `high`: not every sub-agent needs all four (a pure-extract sub-agent has no `unresolved`). Prune false positives before reporting.

## Step 4 — Raw-Transcript Forwarding

A downstream agent that consumes the upstream's full transcript inflates its context with reasoning the agent didn't produce. Detect commands and scripts that pipe full session output forward without summarizing.

```bash
grep -rE "stdout.*\| .*Agent|--full-transcript|raw_session" \
  .claude/commands/ .claude/skills/ scripts/ 2>/dev/null \
  | awk -F: '{print "high|"$1"|raw transcript forwarded to downstream agent|summarize at the boundary; pass conclusions, not exploration"}'

# Heuristic: command file that dispatches to ≥2 agents and concatenates outputs
for cmd in $COMMANDS; do
  COUNT=$(grep -cE "Agent\(|subagent_type:" "$cmd")
  CONCAT=$(grep -cE "concat|append.*output|combine.*results" "$cmd")
  [[ $COUNT -ge 2 && $CONCAT -gt 0 ]] \
    && echo "medium|$cmd|concatenates multi-agent output without per-stage summarization|summarize each agent's return at the boundary"
done
```

Reference: [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md) §Anti-Pattern: Raw Transcript Forwarding.

## Step 5 — Schema Rigidity vs Uncertainty Preservation

A rigid schema (named JSON fields with string values) suggests certainty even when upstream conclusions were tentative. Cases that need to preserve hedging:

```bash
for agent in $SUBAGENTS; do
  BODY=$(awk '/^---$/{c++; next} c==2{print}' "$agent")
  # Heuristic: research / scout / explore agents need uncertainty fields
  echo "$agent" | grep -qiE "research|scout|explore|investigate" || continue
  echo "$BODY" | grep -qiE "confidence|uncertain|tentative|hedge|qualifier|caveat|provisional" \
    || echo "medium|$agent|research-class agent without uncertainty markers|add a confidence/uncertainty field so downstream does not over-trust prose findings"
done
```

Reference: [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md) §When This Backfires (rigid schemas hiding uncertainty).

## Step 6 — Persistence Medium Match

Pipelines that span sessions (research → drafting → review across days) need a durable handoff medium, not in-process return. Pipelines that complete in one session do not.

```bash
for agent in $SUBAGENTS; do
  BODY=$(awk '/^---$/{c++; next} c==2{print}' "$agent")
  # Cross-session marker: agent runs from CI / scheduled / multi-day pipeline
  echo "$BODY" | grep -qiE "schedule|cron|workflow|multi.day|cross.session" \
    && ! echo "$BODY" | grep -qiE "issue|pr comment|gh.*comment|file:|markdown.file" \
    && echo "medium|$agent|cross-session pipeline without durable handoff medium|persist handoff to GitHub issue / PR comment / sidecar file"
done
```

Reference: [`agent-handoff-protocols`](../multi-agent/agent-handoff-protocols.md) §Persistent Handoff Media.

## Step 7 — Downstream Schema Reference

The receiving agent must reference the upstream schema by name in its system prompt — otherwise the contract is one-sided and the downstream parses opportunistically.

```bash
for cmd in $COMMANDS; do
  REFERENCED=$(grep -oE 'returns from [a-z-]+|output of [a-z-]+|<schema:[a-z-]+>' "$cmd" | head -5)
  AGENTS_DISPATCHED=$(grep -oE 'subagent_type:\s*"?[a-z-]+"?' "$cmd" | sed 's/.*: *"\?//; s/"$//' | sort -u)
  [[ -n "$AGENTS_DISPATCHED" && -z "$REFERENCED" ]] \
    && echo "medium|$cmd|dispatches to sub-agents without referencing their output schema|name the schema explicitly so the contract is bidirectional"
done
```

## Step 7b — Topology Ceilings and Risk-Aware Routing

Multi-agent fleets fail past stable ceilings, not gradually. Two ceilings recur often enough to surface as audit findings:

- **CRDT-backed parallel workspaces**: skip when the parallelizable task share is small or the fleet exceeds the 5-agent verified ceiling ([`crdt-observation-driven-coordination`](../multi-agent/crdt-observation-driven-coordination.md)). Above 5 agents, observation cost outpaces CRDT merge benefit.
- **Risk-aware routing on uncertain handoffs**: when a router selects between downstream agents on inferred capability, use a risk-aware score (`mean − λ·stddev`) rather than mean alone — low-evidence contexts have wide posteriors and a mean-only router forces premature switching ([`contextual-capability-calibration`](../multi-agent/contextual-capability-calibration.md)).

```bash
# Detect parallel-fan-out sites that already exceed the CRDT ceiling
for cmd in $COMMANDS; do
  N=$(grep -cE "Agent\(|subagent_type:" "$cmd")
  [[ $N -gt 5 ]] && grep -qiE "crdt|workspace|merge" "$cmd" \
    && echo "medium|$cmd|fan-out of $N agents exceeds the 5-agent CRDT ceiling|narrow scope or switch to non-CRDT coordination"
done

# Detect routers that select on `mean` only (no risk term)
grep -rE "argmax|max_score|select.*confidence|highest_score" \
  .claude/skills/ scripts/ 2>/dev/null \
  | grep -vE "stddev|sigma|risk|lambda|posterior" \
  | head | awk -F: '{print "low|"$1"|router selects on mean alone|add a risk term (mean − λ·stddev) for low-evidence contexts"}'
```

## Step 8 — Per-Handoff Scorecard

```markdown
# Audit Report — Handoff Protocols

## Per-handoff scorecard

| Boundary | Schema | Required fields | Summarized | Uncertainty | Persisted | Top issue |
|----------|:------:|:---------------:|:----------:|:-----------:|:---------:|-----------|
| <upstream> → <downstream> | ✅ | ⚠️ | ✅ | ❌ | n/a | <one-line> |

## Findings

| Severity | Boundary | Finding | Suggested fix |
|----------|----------|---------|---------------|
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Handoff Protocols — <repo>

| Boundaries | Pass | Warn | Fail | Raw transcripts |
|-----------:|-----:|-----:|-----:|----------------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing output schema declarations>
```

## Remediation

- [Bootstrap Sub-Agent Template](bootstrap-subagent-template.md) — Step 3 (return-shape contract) is the bootstrap-side fix for missing output schemas
- For commands dispatching to multiple sub-agents, retrofit a `## Returns` section per agent and reference it in the dispatching command's prompt

## Related

- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Sub-Agents for Fan-Out](../multi-agent/sub-agents-fan-out.md)
- [Bounded Batch Dispatch](../multi-agent/bounded-batch-dispatch.md)
- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md)
- [Audit Sub-Agent Definitions](audit-subagent-definitions.md)
- [Bootstrap Sub-Agent Template](bootstrap-subagent-template.md)
