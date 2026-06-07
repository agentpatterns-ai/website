---
title: "Effort-Aware Hooks: Reading the Reasoning Tier from PreToolUse and PostToolUse"
description: "Claude Code v2.1.133 added the active effort level to hook input JSON, letting deterministic gates branch on the harness's reasoning tier without inferring it from prompt content."
tags:
  - tool-engineering
  - cost-performance
  - claude
aliases:
  - tier-aware hooks
  - reasoning-effort hooks
  - effort level hook input
last_reviewed: 2026-06-03
---

# Effort-Aware Hooks: Reading the Reasoning Tier from PreToolUse and PostToolUse

> Claude Code v2.1.133 exposes the active effort level as a first-class hook input, so deterministic gates can branch on the reasoning tier without parsing transcripts.

## The Signal

Claude Code [v2.1.133, May 7, 2026](https://code.claude.com/docs/en/changelog) added two equivalent surfaces to every hook: an `effort` object in the JSON stdin payload, and a `$CLAUDE_EFFORT` environment variable (also set for Bash tool commands).

The [hooks reference](https://code.claude.com/docs/en/hooks) documents `effort` as an object with a `level` field carrying the active tier — `"low"`, `"medium"`, `"high"`, `"xhigh"`, or `"max"` — present on tool-use events including `PreToolUse`, `PostToolUse`, `Stop`, and `SubagentStop`. Two properties matter. The level is the *downgraded* level — when requested effort exceeds what the active model supports, the field reports what actually ran. And the field is absent on session-level events outside a tool-use context, so a `UserPromptSubmit` hook cannot read it.

## Asymmetry Rule

A tier-aware hook is safe when it gets *stricter* at higher tiers and dangerous when it gets *weaker* at lower tiers. A security gate that relaxes deny-rules at `low` is a gate an attacker bypasses by running cheaper. The Anthropic effort docs reinforce why: ["Effort is a behavioral signal, not a strict token budget"](https://platform.claude.com/docs/en/build-with-claude/effort) — the level reflects what the model will spend, not what an invariant requires.

| Direction | Safe? | Example |
|-----------|-------|---------|
| Stricter at higher tiers | Yes | Require eval-suite pass on `xhigh` |
| Looser at lower tiers | No (security) | Skip secret scan on `low` |
| Different threshold per tier | Conditional | Loop-detector limits scaled to call volume |
| Pure observability per tier | Yes | Tag every metric with `effort.level` |

## Three Concrete Uses

### Loop-Detector Threshold Scaling

The bootstrap loop detector hook counts per-file edits at `PostToolUse` and escalates from nudge → pause → block. Lower-effort runs naturally make fewer tool calls — the [effort docs](https://platform.claude.com/docs/en/build-with-claude/effort) note that lower levels "combine multiple operations into fewer tool calls" and "make fewer tool calls." A static threshold tuned for `xhigh` produces false negatives at `low`. The fix is to scale the threshold by tier (read `$CLAUDE_EFFORT`, pick from a table) — never to disable the detector.

### Pre-Completion Check Selection

The bootstrap pre-completion hook runs deterministic checks at `Stop`. Effort-aware variants require a stricter checklist when the operator paid for a stricter run: every tier runs the standard set (lint, build, test); `high` adds a slow check; `xhigh` / `max` add the slowest. Higher tiers add; no tier subtracts.

### Telemetry Labelling

The cheapest pattern is observational. Emit `effort.level` as a label on every hook-side metric and trace span (see [agent observability with OpenTelemetry](../observability/agent-observability-otel.md)). Cost dashboards then filter by tier without inferring it from transcript content. The hook never blocks differently.

## Calibration Drift

The default effort level changes silently across versions. As of [v2.1.117](https://code.claude.com/docs/en/model-config#adjust-effort-level), the default is `xhigh` on Opus 4.7 and `high` on Opus 4.6 / Sonnet 4.6. A hook with thresholds calibrated against `high`-tier traffic on Opus 4.6 now applies to `xhigh`-tier traffic on Opus 4.7 by default, with no project setting changed. Branch on `effort.level` directly rather than on which model is configured, and re-calibrate tier-shaped thresholds when the Claude Code version is bumped.

The Claude Code docs are explicit about cross-model semantics: ["The effort scale is calibrated per model, so the same level name does not represent the same underlying value across models"](https://code.claude.com/docs/en/model-config#adjust-effort-level). A hook that branches identically on `level === "high"` against Sonnet 4.6 and Opus 4.7 is treating two different things as one.

## Tool-Agnostic Restatement

The structural primitive — the harness exposes its reasoning-tier selection to deterministic gates — generalizes beyond Claude Code. The Anthropic API's [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) carries the same five levels at the SDK boundary. When a harness lacks a structural signal, the only fallback is to infer tier from prompt content — forfeiting the determinism that makes hooks worth running.

## When This Backfires

- **Tier-induced flakiness.** "The same change passes on `low` and fails on `high`" turns the cheap signal into noise. Keep gates uniform; vary *what tasks route to which tier* at the agent or model-routing level.
- **Multi-model fleets.** Read both `effort.level` and the model identifier when thresholds depend on absolute capability — the same level name has different semantics across models.
- **Inferred-tier security gates.** Security gates ignore `effort` entirely, or get stricter — never weaker.

## Example

A `PostToolUse` loop detector that scales its block threshold by tier. The script reads `$CLAUDE_EFFORT` (set by Claude Code v2.1.133+), falls back to `high` when the variable is absent (older versions, non-tool events), and never lowers the threshold below the floor — the asymmetry rule applied to a counter.

```bash
#!/usr/bin/env bash
# .claude/hooks/loop-detector.sh
# PostToolUse — scale block threshold by reasoning tier.

set -euo pipefail

# Floor: never block before this many edits, regardless of tier.
FLOOR=5

case "${CLAUDE_EFFORT:-high}" in
  low)    BLOCK_AFTER=$FLOOR ;;
  medium) BLOCK_AFTER=6 ;;
  high)   BLOCK_AFTER=8 ;;
  xhigh)  BLOCK_AFTER=12 ;;
  max)    BLOCK_AFTER=16 ;;
  *)      BLOCK_AFTER=8 ;;
esac

# ... existing per-file edit-count logic, comparing against $BLOCK_AFTER
```

The threshold scales upward with tier (more thinking → more legitimate exploration → higher tolerance for repeat edits) but never drops below the floor. A `low`-tier run gets the same hard floor as `high`; an `xhigh` run gets headroom. The block decision still fires deterministically — only the threshold is tier-shaped.

## Key Takeaways

- `effort.level` is a first-class hook input in Claude Code v2.1.133+, available on `PreToolUse`, `PostToolUse`, `Stop`, and `SubagentStop`, and as `$CLAUDE_EFFORT` for hook and Bash subprocesses.
- The level is the *downgraded* level (what actually ran), not the requested level — useful for accuracy, but means the same code path runs against different upstream requests.
- Asymmetry rule: tier-aware hooks may add strictness at higher tiers; they must not subtract it at lower ones, especially for security gates.
- Default-tier changes between Claude Code versions silently move which branch fires most often — re-calibrate tier-shaped thresholds on every harness upgrade.
- The same level name has different semantics across models; pair `effort.level` with the model identifier when thresholds depend on absolute capability rather than relative tier.

## Related

- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Heuristic-Based Effort Scaling in Agent Prompts](../agent-design/heuristic-effort-scaling.md)
- [Agent Observability with OpenTelemetry](../observability/agent-observability-otel.md)
