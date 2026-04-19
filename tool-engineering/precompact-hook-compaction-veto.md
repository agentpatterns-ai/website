---
title: "PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries"
description: "Claude Code's PreCompact hook can block compaction by exiting with code 2 or returning `decision: block`, turning automatic context compression into a guarded event that defers until a safe checkpoint."
tags:
  - tool-engineering
  - context-engineering
  - claude
aliases:
  - PreCompact veto
  - compaction block hook
---

# PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries

> `PreCompact` can block compaction — exiting with code 2 or returning `{"decision": "block"}` defers context compression until the agent reaches a safer checkpoint.

## What Changed

Claude Code v2.1.105 ([2026-04-13](https://code.claude.com/docs/en/changelog)) added `PreCompact` hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision": "block"}`. That makes `PreCompact` a control hook — not just an observability point — for the compaction lifecycle ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

Compaction summarises older turns to free context space. The summary paraphrases structured artefacts (specs, plans, tool outputs) that the agent may still need verbatim ([Context Compression Strategies](../context-engineering/context-compression-strategies.md); [Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). The veto turns that loss from an unconditional event into one the hook controls.

## Input and Decision Schema

`PreCompact` receives the usual hook envelope plus a `trigger` field ([hooks reference](https://code.claude.com/docs/en/hooks)):

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../transcript.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "PreCompact",
  "trigger": "auto"
}
```

| Field | Value |
|-------|-------|
| `trigger` | `"manual"` (user ran `/compact`) or `"auto"` (harness-initiated) |

The hook signals block via either channel ([hooks reference](https://code.claude.com/docs/en/hooks)):

| Channel | Block | Allow |
|---------|-------|-------|
| Exit code | `exit 2` | `exit 0` |
| JSON stdout | `{"decision": "block", "reason": "..."}` | Omit `decision` |

With JSON output, `reason` surfaces to Claude as an explanation of why compaction was deferred. Exit code 2 instead feeds stderr to Claude.

## When to Block

Block when compaction would force the agent to redo in-flight work:

- **Mid-edit** — a file edit has been planned from tool output the summary would paraphrase
- **Mid-test** — a failing test's stack trace still needs to be read verbatim
- **Mid-plan** — a structured plan hasn't been written to disk yet

Allow at natural checkpoints:

- Test suite green and staged changes committed
- Sub-task complete, plan updated on disk
- User turn boundary with no pending tool calls

## Matcher: Separate Auto from Manual

Restrict blocks to `trigger: "auto"`. The user pressing `/compact` is a deliberate instruction — vetoing it fights the user. The [hooks reference](https://code.claude.com/docs/en/hooks) documents `manual` and `auto` as the matcher values for `PreCompact`.

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/defer-auto-compaction.sh"
          }
        ]
      }
    ]
  }
}
```

## The Release Condition

An indefinite block exhausts the context window. Every hook that vetoes compaction must define an explicit release condition — a sentinel the harness has crossed before the hook allows the next compaction through. Without it, the window fills and the session terminates harder than a summary would have.

Two practical forms:

- **Sentinel file** — the agent's workflow touches `.claude/compaction-safe` at a checkpoint; the hook allows compaction when the file exists and is recent
- **Counter-based timeout** — the hook tracks consecutive block attempts and forces an allow after N retries, taking the summary rather than the crash

## Example

The hook below blocks automatic compaction until a sentinel file (`.claude/compaction-safe`) has been touched within the last 30 seconds. The agent's CLAUDE.md instructs it to touch the sentinel at each sub-task checkpoint. After three consecutive blocks, the hook allows compaction regardless to prevent exhaustion.

**`.claude/hooks/defer-auto-compaction.sh`**:

```bash
#!/usr/bin/env bash
set -euo pipefail

SENTINEL="$CLAUDE_PROJECT_DIR/.claude/compaction-safe"
COUNTER="$CLAUDE_PROJECT_DIR/.claude/.compact-block-count"
MAX_BLOCKS=3
STALENESS=30

INPUT=$(cat)
TRIGGER=$(echo "$INPUT" | jq -r '.trigger')

# Never block manual compaction — the user asked for it
[ "$TRIGGER" = "auto" ] || { echo '{}'; exit 0; }

# Read and increment the block counter
COUNT=$(cat "$COUNTER" 2>/dev/null || echo 0)
COUNT=$((COUNT + 1))

# Force allow after MAX_BLOCKS to prevent window exhaustion
if [ "$COUNT" -gt "$MAX_BLOCKS" ]; then
  echo 0 > "$COUNTER"
  echo '{}'
  exit 0
fi

# Allow if sentinel is fresh — the agent checkpointed recently
if [ -f "$SENTINEL" ]; then
  AGE=$(( $(date +%s) - $(stat -c %Y "$SENTINEL") ))
  if [ "$AGE" -lt "$STALENESS" ]; then
    echo 0 > "$COUNTER"
    echo '{}'
    exit 0
  fi
fi

# Block — defer to the next checkpoint
echo "$COUNT" > "$COUNTER"
cat <<EOF
{
  "decision": "block",
  "reason": "Deferring auto-compaction until next checkpoint. Touch .claude/compaction-safe when the current sub-task is done (attempt $COUNT of $MAX_BLOCKS)."
}
EOF
```

The hook combines the matcher (auto only), a task-level release condition (sentinel file), and a hard ceiling (max retries) so the window cannot be starved.

## Diagram

```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant H as PreCompact Hook
    participant FS as Sentinel File

    CC->>CC: Context pressure hits threshold
    CC->>H: PreCompact (trigger=auto)
    H->>FS: Read .claude/compaction-safe age
    alt Sentinel fresh OR retries exhausted
        H-->>CC: exit 0 (allow)
        CC->>CC: Compact and resume
    else Mid-task, sentinel stale
        H-->>CC: {"decision": "block", "reason": "..."}
        CC->>CC: Continue; reason shown to Claude
        CC->>FS: Agent checkpoints → touch sentinel
        CC->>H: PreCompact (next attempt)
        H-->>CC: exit 0 (allow)
    end
```

## When This Backfires

- **No release condition** — a veto without a defined unblock path blocks every subsequent compaction until the context window exhausts and the session terminates. The hook must always define a sentinel, counter, or timeout.
- **Vetoing manual compaction** — `/compact` is a deliberate user action; blocking it fights the user. Scope the matcher to `trigger: "auto"` unless there is a specific reason to intercept manual compaction.
- **High-velocity tool output** — sessions generating large tool payloads (repo-wide greps, large file reads) cross the 99% threshold quickly; blocking past that point forces the harness to truncate arbitrarily, which is worse than the summary would have been ([Context Compression Strategies](../context-engineering/context-compression-strategies.md)).
- **Low compaction frequency** — for short sessions where compaction rarely fires, the hook wiring and sentinel tracking are pure overhead. Prefer the simpler [Post-Compaction Re-read Protocol](../instructions/post-compaction-reread-protocol.md) when recovery is cheaper than prevention.
- **Stale sentinel logic** — a sentinel file that the agent forgets to touch (or that a hook race condition leaves stale) blocks compaction even at safe points. Pair the sentinel check with the retry counter so a bug in one doesn't strand the session.

> **"Block" cancels; it does not defer.** `{"decision": "block"}` cancels the current compaction — the harness does not auto-retry the same trigger. A retry only happens when the next trigger fires (pressure re-crosses the threshold, or the user reissues `/compact`), which is why the sentinel-plus-counter pattern above is mandatory: the hook's own bookkeeping is what re-evaluates on the next trigger. Edge case: if auto-compaction fired to *recover* from an API context-limit error, blocking surfaces that error and fails the in-flight request ([practitioner report: block cancels instead of deferring](https://github.com/MemPalace/mempalace/issues/856); [block prevents compaction at context limit](https://github.com/MemPalace/mempalace/issues/906)). Near window exhaustion, prefer allowing compaction or using `systemMessage` for advisory instructions rather than `decision: "block"`.

## Key Takeaways

- `PreCompact` became a control hook in Claude Code v2.1.105 — exit 2 or `{"decision": "block"}` vetoes compaction ([changelog](https://code.claude.com/docs/en/changelog)).
- Scope the matcher to `trigger: "auto"` — vetoing user-initiated `/compact` fights the user.
- Every block needs an explicit release condition: sentinel file, retry counter, or timeout. Indefinite blocking exhausts the context window.
- The `reason` field in the JSON response surfaces to Claude, letting the model reason about what to do next instead of silently retrying.
- Prevent-the-loss (`PreCompact` veto) and recover-after-loss ([Post-Compaction Re-read Protocol](../instructions/post-compaction-reread-protocol.md)) are complementary — use the veto at critical checkpoints, the re-read at session resume.

## Related

- [Claude Code Hooks](../tools/claude/hooks-lifecycle.md)
- [Post-Compaction Re-read Protocol](../instructions/post-compaction-reread-protocol.md)
- [Context Compression Strategies](../context-engineering/context-compression-strategies.md)
- [Manual Compaction as Dumb Zone Mitigation](../context-engineering/manual-compaction-dumb-zone-mitigation.md)
- [StopFailure Hook](stopfailure-hook.md)
- [Conditional Hook Execution](conditional-hook-execution.md)
- [Hook Catalog](hook-catalog.md)
- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
