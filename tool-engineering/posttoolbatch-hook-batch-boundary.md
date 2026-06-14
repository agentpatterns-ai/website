---
title: "PostToolBatch Hook: Once-Per-Decision-Cycle Injection at the Batch Boundary"
term: "PostToolBatch Hook"
description: "PostToolBatch fires exactly once after a full parallel tool batch resolves, before the next model call — the right injection point for conventions and validations that should run once per decision cycle, not N times per call."
tags:
  - tool-engineering
  - instructions
  - claude
aliases:
  - PostToolBatch hook event
  - batch-boundary hook
  - once-per-batch injection
last_reviewed: 2026-06-03
maturity: established
---

# PostToolBatch Hook: Once-Per-Decision-Cycle Injection at the Batch Boundary

> `PostToolBatch` fires once after a parallel tool batch resolves and before the next model call — the cardinality match for per-decision-cycle work.

## What It Is

`PostToolBatch` is a Claude Agent SDK hook event that fires "after a full batch of parallel tool calls resolves, before the next model call" — verbatim from the available-hooks table ([Claude Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks)). It fires **exactly once with the full batch**, in contrast to `PostToolUse`, which fires once per tool, concurrently on parallel batches ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

The hook is **TypeScript SDK only** at this writing; the Python SDK does not expose it ([available-hooks table](https://code.claude.com/docs/en/agent-sdk/hooks)).

## Where It Sits in the Lifecycle

A turn runs: model emits `tool_use` blocks → SDK executes them (read-only concurrently, stateful sequentially) → all results return as one user message → next model call ([Agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop); [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)). The window between "last tool resolves" and "next model call" is the batch boundary, which `PostToolBatch` exposes as a first-class event:

| Event | Fires | Cardinality per cycle |
|-------|-------|----------------------|
| `PreToolUse` | Before each tool call | N (once per call) |
| `PostToolUse` | After each tool call | N (once per call, concurrent on parallel batches) |
| **`PostToolBatch`** | After the full batch resolves, before next model call | **1** |
| `Stop` | When the agent emits a turn with no tool calls | 1 per session end |

The cardinality column is the load-bearing distinction: a per-call hook that must fire once per cycle forces session-keyed dedup, which the batch event removes.

## Input and Output Schema

The hook receives the standard envelope plus a `tool_calls` array containing each call in the batch ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)):

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "hook_event_name": "PostToolBatch",
  "tool_calls": [
    {
      "tool_name": "Read",
      "tool_input": { "path": "file1.txt" },
      "output": "contents..."
    },
    {
      "tool_name": "Read",
      "tool_input": { "path": "file2.txt" },
      "output": "contents..."
    }
  ]
}
```

`PostToolBatch` has **no matcher support** — it always fires on every batch completion, alongside `UserPromptSubmit`, `Stop`, and `MessageDisplay` in the no-matcher category. It returns the same decision shape as `PostToolUse`: top-level `decision: "block"` halts the loop before the next model call, and `hookSpecificOutput.additionalContext` appends text the model reads on its next turn ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

## Example: Re-emit Conventions Once Per Cycle

A common use is re-injecting project conventions after every batch so the model sees them at each decision point without the per-call hook tax:

```typescript
import { HookCallback, PostToolBatchHookInput } from "@anthropic-ai/claude-agent-sdk";

const reinjectConventions: HookCallback = async (input) => {
  const batch = input as PostToolBatchHookInput;

  return {
    hookSpecificOutput: {
      hookEventName: "PostToolBatch",
      additionalContext: [
        "Reminder before your next decision:",
        "- Use uv, not pip",
        "- Use bun, not npm",
        `- Batch just executed ${batch.tool_calls.length} calls`,
      ].join("\n"),
    },
  };
};
```

Wired with no matcher (the event has none), the hook fires once per cycle whether the batch had one tool or twenty. The equivalent `PostToolUse` implementation would fire N times and need session-keyed dedup to avoid spamming the model with duplicate reminders.

## Why It Works

The Claude API issues parallel tool calls inside one assistant turn, and the SDK collects all results before the next request ([Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)). Two consequences follow:

1. The boundary between "batch resolved" and "next model call" is the only point where the harness can inject content the model reads **exactly once per decision cycle**.
2. Per-tool hooks (`PostToolUse`) fire inside that boundary, once per tool, so anything they emit via `additionalContext` either duplicates N times or has to be deduplicated by hand.

`PostToolBatch` matches the firing cardinality of the work — the same principle that makes `PreCompact` the right place for compaction guards and `Stop` the right place for completion checks, each event sized to one logical occurrence per cycle ([PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md)).

## When This Backfires

- **Python SDK consumers.** `PostToolBatch` is TypeScript SDK only ([available-hooks table](https://code.claude.com/docs/en/agent-sdk/hooks)). Python SDK code has no equivalent — either accept the per-call `PostToolUse` workaround or pin the harness to TypeScript.
- **Single-tool batches dominate the session.** When the model rarely emits parallel calls (simple Q&A agents, or `disable_parallel_tool_use=true`), `PostToolBatch` and `PostToolUse` collapse to the same firing rate — a code path with no observable benefit ([Parallel tool use § disabling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)).
- **Per-tool granularity is the actual need.** Side effects that target a specific tool — "lint after every `Edit`", "audit every `Bash`" — need the per-call event. Filtering the `tool_calls` array in a batch handler re-implements `PostToolUse` worse, with no matcher and an extra dispatch layer.
- **Permission gating.** `PostToolBatch` runs after the batch executes; it cannot block a specific call from running. "Deny this command" rules belong in `PreToolUse`, where the decision happens before execution ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). The batch hook can still halt the loop via `decision: "block"`, but only after the side effects occurred.
- **Mid-batch ordering signal is lost.** When a hook must react to the *order* tools ran (a sequential `Edit` → `Bash test` → `Read` cascade), `PostToolBatch` fires after all resolve. The ordering is recoverable from `tool_calls[]`, but the per-event timing is not — for true per-tool-completion timing, stay on `PostToolUse`.
- **Hook-plumbing bugs surface in this family.** Tracking issues on the related per-tool events ([anthropics/claude-code#3179](https://github.com/anthropics/claude-code/issues/3179), [anthropics/claude-code#3983](https://github.com/anthropics/claude-code/issues/3983)) show hook reliability has had rough edges. The batch hook is newer than `PostToolUse`; verify it fires in your harness before relying on it for enforcement.

## Key Takeaways

- `PostToolBatch` fires once per parallel tool batch, before the next model call — the cardinality match for once-per-decision-cycle work ([Claude Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks)).
- `PostToolUse` fires per tool call; using it for batch-level work forces session-keyed dedup. `PostToolBatch` removes the dedup requirement.
- Input contains a `tool_calls` array with the full batch; no matcher support — the event always fires on every batch.
- Decision controls: top-level `decision: "block"` halts before the next model call; `hookSpecificOutput.additionalContext` injects text the model reads next turn ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).
- TypeScript SDK only at this writing. Python SDK consumers must implement the per-call workaround.
- Wrong tool for per-tool granularity, for permission gating (use `PreToolUse`), and for mid-batch timing signals.

## Related

- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog](hook-catalog.md)
- [PostToolUse continueOnBlock: Refusal With a Load-Bearing Reason](posttooluse-continue-on-block.md)
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md)
- [MessageDisplay Hook: Transforming Assistant Text at the Display Boundary](messagedisplay-hook-assistant-text-transform.md)
