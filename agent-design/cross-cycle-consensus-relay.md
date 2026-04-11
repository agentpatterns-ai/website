<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->
---
title: "Cross-Cycle Consensus Relay"
description: "A structured relay document that agents read at cycle start and write at cycle end, preserving decisions and forward momentum across multi-session autonomous loops."
tags:
  - agent-design
  - memory
  - tool-agnostic
aliases:
  - consensus relay document
  - cross-session relay pattern
---

# Cross-Cycle Consensus Relay

> A structured relay document that agents read at cycle start and write at cycle end, preserving decisions and forward momentum across multi-session autonomous loops.

## The Problem

Long-running autonomous loops — agents working over hours or days across repeated sessions — fail in three predictable ways when cross-session state is unstructured:

- **Drift**: Each restart discards prior decisions. The agent restarts without awareness of what was already resolved.
- **Repetition**: Agents re-debate questions settled in earlier cycles, wasting tokens and compute on resolved trade-offs.
- **Stalls**: Without a convergence signal, loops spin indefinitely without producing output.

A progress file records what happened. The relay addresses why it happened and what must happen next — a reasoning contract, not a log.

## Relay Document Schema

The relay document is a single markdown file structured to drive the *next* cycle's reasoning, not to archive the current one. Every field serves a forward purpose:

| Field | Purpose |
|---|---|
| **Current Phase** | Progress checkpoint — where in the overall workflow |
| **What We Did This Cycle** | Recent history — compact, not exhaustive |
| **Key Decisions Made** | Institutional memory with rationale — prevents repetition |
| **Active Projects** | In-flight work state — what is underway |
| **Metrics** | Performance tracking — quantified progress signals |
| **Next Action** | Single directive for the following cycle |
| **Open Questions** | Forward pressure points — unresolved issues to carry forward |

Keep the relay under ~2,000 tokens to preserve context window space for agent reasoning. Archive older decisions to `memories/archive/` as the document grows. Commit the relay to Git after each cycle for audit trail and human inspection.

## Atomic Write Protocol

Write the relay atomically to prevent partial-write corruption on crash or restart:

```bash
cat > memories/.consensus.tmp << 'EOF'
## Current Phase
Implementation — auth module complete, starting profile page

## Key Decisions Made
- JWT over sessions: simpler deployment (2026-04-09)
- Postgres over SQLite: concurrent write requirement (2026-04-09)

## Next Action
Implement POST /profile endpoint with validation

## Open Questions
- Rate limiting strategy for profile updates?
EOF
mv memories/.consensus.tmp memories/consensus.md
```

Write to a temp file in the same directory, then rename. The rename is atomic on POSIX filesystems — the relay is either fully updated or unchanged, never in a partial state.

## Convergence Detection

Compare the **Next Action** field across consecutive cycles. If two cycles produce identical directives, the agent is stalling — it cannot make progress without intervention.

When a stall is detected, inject a direction-change signal into the next cycle's prompt:

```bash
prev_action=$(sed -n '/## Next Action/{n;p}' memories/prev_consensus.md)
curr_action=$(sed -n '/## Next Action/{n;p}' memories/consensus.md)

if [ "$prev_action" = "$curr_action" ]; then
  STALL_SIGNAL="STALL DETECTED: previous cycle produced same next action. You must change approach."
fi
```

The [nibzard/awesome-agentic-patterns catalog](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/cross-cycle-consensus-relay.md) defines escalating convergence rules that complement stall detection: Cycle 1 brainstorms with ranked options, Cycle 2 selects a winner and validates via pre-mortem, Cycle 3 and beyond ship artifacts only — discussion is prohibited after the decision cycle.

## Relay vs. Progress File

| Aspect | Relay Document | Progress File |
|---|---|---|
| Primary purpose | Drive next-cycle reasoning | Record completed work |
| Key Decisions field | Yes — with rationale | No |
| Next Action field | Yes — single directive | No |
| Convergence detection | Via Next Action comparison | Not applicable |
| Structure | Schema-disciplined | Flexible |
| Token budget | ~2,000 token cap | Grows with project |

The relay complements a [progress file](agent-harness.md) and [trajectory logging](../observability/trajectory-logging-progress-files.md) — it does not replace them. Run both: the relay guides reasoning; the progress file tracks completion status.

## Trade-offs

**Advantages**: full context recovery after crashes; prevents drift through structured handoff; human-readable for inspection; Git-diffable for audit.

**Limitations**: schema discipline must be consistent — degraded structure degrades reasoning; single-file relay becomes a bottleneck for loops running faster than once per minute; relay size grows and requires periodic archiving.

## Example

A minimal loop wrapper that reads the relay at cycle start and writes it atomically at cycle end:

```bash
#!/usr/bin/env bash
# cycle-runner.sh

RELAY="memories/consensus.md"
PREV_RELAY="memories/prev_consensus.md"
MAX_CYCLES=10
CYCLE=0

while [[ $CYCLE -lt $MAX_CYCLES ]]; do
  echo "=== Cycle $((CYCLE + 1)) ==="

  # Stall detection
  STALL_SIGNAL=""
  if [[ -f "$PREV_RELAY" ]]; then
    prev=$(sed -n '/## Next Action/{n;p}' "$PREV_RELAY")
    curr=$(sed -n '/## Next Action/{n;p}' "$RELAY")
    if [[ "$prev" = "$curr" ]]; then
      STALL_SIGNAL="STALL DETECTED: repeat next action. Change approach."
    fi
  fi

  cp "$RELAY" "$PREV_RELAY"

  # Run agent cycle with relay context
  claude -p "$(cat PROMPT.md)" \
    --context "$(cat "$RELAY")" \
    --context "$STALL_SIGNAL"

  # Atomic relay write performed by agent at cycle end
  CYCLE=$((CYCLE + 1))
done
```

The agent is responsible for writing the relay at cycle end using the temp-file-rename pattern. The runner is responsible for stall detection and injecting correction signals.

## Key Takeaways

- The relay is a reasoning contract — every field directs next-cycle reasoning, not past-cycle archiving.
- Atomic writes (temp file + rename) prevent partial-write corruption across crashes.
- Stall detection — comparing consecutive Next Action fields — provides a mechanical convergence signal.
- Keep the relay under ~2,000 tokens; archive older decisions separately.
- Use the relay alongside progress files and trajectory logging, not instead of them.

## Related

- [Agent Harness: Initializer and Coding Agent](agent-harness.md) — the initializer/coding agent pattern that the relay extends with consensus structure
- [Session Initialization Ritual](session-initialization-ritual.md) — startup sequence that reads the relay before acting
- [The Ralph Wiggum Loop](ralph-wiggum-loop.md) — fresh-context iteration pattern that the relay enables across cycles
- [Convergence Detection in Iterative Refinement](convergence-detection.md) — convergence signals for within-session refinement loops
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md) — progress file pattern that complements the relay
- [Loop Strategy Spectrum](loop-strategy-spectrum.md) — choosing between accumulated, compressed, and fresh context across loops
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — failure recovery strategies for long-running agent loops
- [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md) — tracking agent progress across the multi-session loops this pattern enables
- [Idempotent Agent Operations](idempotent-agent-operations.md) — design operations for safe retry across relay cycles
