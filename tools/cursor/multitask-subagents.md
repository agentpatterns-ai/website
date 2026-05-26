---
title: "Cursor /multitask: Async Subagent Dispatch in the Editor"
description: "Cursor 3.2's /multitask command runs async subagents from inside an editor session — parallelising queued prompts and decomposing large tasks across a fleet of background subagents."
tags:
  - cursor
  - multi-agent
  - agent-design
aliases:
  - cursor multitask
  - cursor async subagents
  - multitask slash command
applies_to: "cursor@3.x"
last_reviewed: 2026-05-27
status: current
---
# Cursor /multitask: Async Subagent Dispatch in the Editor

> Dispatch async subagents from the editor session — parallelise queued prompts and let Cursor break a large task across a background subagent fleet.

Cursor 3.2 (April 24, 2026) added `/multitask` to the [Agents Window](agents-window.md). Instead of queueing prompts, `/multitask` spawns async subagents that run in parallel and can decompose a request into chunks "for a fleet of async subagents to tackle simultaneously" ([Cursor changelog](https://cursor.com/changelog)).

## What /multitask Actually Does

Two behaviours, both routed through async subagents ([Cursor changelog](https://cursor.com/changelog)):

1. **Queue parallelisation** — stacked prompts run concurrently as background subagents instead of sequentially.
2. **Auto-decomposition** — a larger request is split into chunks, each dispatched to its own subagent.

Each subagent runs in its own context window with no access to prior conversation history; the parent must pass required context in the dispatch prompt ([Cursor subagents docs](https://cursor.com/docs/subagents)).

## Foreground vs Background — `/multitask` Uses Background

Cursor subagents have two execution modes ([Cursor subagents docs](https://cursor.com/docs/subagents)):

| Mode | Behaviour | When |
|------|-----------|------|
| Foreground | Blocks the parent until the subagent returns | Sequential tasks where the parent needs the output |
| Background | Returns immediately; subagent runs independently | Long-running or parallel workstreams |

`/multitask` is background dispatch — the parent stays interactive while subagents write state and can be resumed by agent ID.

## How Results Surface

Each subagent returns "a final message with its results" to the parent ([Cursor subagents docs](https://cursor.com/docs/subagents)). In the Agents Window each surfaces as a separate entry to inspect, promote, or resume by agent ID.

The parent's context window only receives the final summary — intermediate output (file searches, command logs, browser snapshots) stays inside the subagent. This is the same context-isolation mechanism the built-in `Explore`, `Bash`, and `Browser` subagents use ([Cursor subagents docs](https://cursor.com/docs/subagents)).

## /multitask vs Adjacent Surfaces

Cursor 3.2 ships `/multitask` alongside improved worktrees and [multi-root workspaces](multi-root-workspaces.md) ([Cursor changelog](https://cursor.com/changelog)). The three surfaces solve different isolation problems:

| Surface | Isolation | Use when |
|---------|-----------|----------|
| `/multitask` | Context only | Async parallelism, edits land in the foreground checkout |
| `/worktree` | Filesystem (separate git checkout) | Subagents edit overlapping files or you need clean diffs per task |
| Agents Window tabs | Visual / session | Driving multiple sessions manually rather than dispatching from one |

`/multitask` and `/worktree` compose. For risky parallel edits, dispatch with `/multitask` against worktree-isolated subagents; for read-mostly fan-out, `/multitask` alone is enough.

## Cross-Tool Comparison

```mermaid
graph TD
    subgraph Cursor["Cursor 3.2"]
        C1[Editor] -->|/multitask| C2[Async subagent fleet]
        C2 --> C3[Final messages to parent]
    end
    subgraph Claude["Claude Code"]
        K1[Parent] -->|Task background:true| K2[Background subagent]
        K2 --> K3[Monitor streams events]
    end
    subgraph Copilot["Copilot CLI"]
        G1[Parent] -->|/agent name| G2[Temporary subagent]
        G2 --> G3[Torn down]
    end
```

| | Cursor `/multitask` | Claude Code background | Copilot CLI agents |
|---|---|---|---|
| Surface | Slash command in editor | `background: true` frontmatter | `/agent <name>` |
| Auto-decomposition | Yes | No | No |
| Result surfacing | Final messages plus resumable IDs | [Monitor streams events](../../multi-agent/async-non-blocking-subagent-dispatch.md) | Torn down per invocation |
| Filesystem isolation | Compose with `/worktree` | `Worktree` tool separate | None built-in |
| Recursion depth | N — nested since Cursor 2.5 ([docs](https://cursor.com/docs/subagents)) | 1 | 1 |

Sources: [Cursor subagents docs](https://cursor.com/docs/subagents), [Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents), [Cross-tool subagent comparison](../../multi-agent/cross-tool-subagent-comparison.md).

## When /multitask Backfires

`/multitask` specialises [async non-blocking subagent dispatch](../../multi-agent/async-non-blocking-subagent-dispatch.md) — those caveats apply, plus editor-specific failure modes.

- **No productive parent work during the wait** — Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) chose synchronous dispatch because "asynchronicity adds challenges in result coordination, state consistency, and error propagation across the subagents."
- **Tightly-coupled refactor** — subagents lose shared context, produce inconsistent edits, and the user pays merge cost without parallelism gain.
- **Sequential dependencies** — B must consume A's output; async degrades to effectively-synchronous with extra bookkeeping.
- **Small task count (1–2 items)** — coordination overhead exceeds payoff.
- **Overlapping file edits without `/worktree`** — multiple subagents writing the same file produce manual-merge work; Cursor 3.2 shipped improved worktrees alongside `/multitask` for this reason ([Cursor changelog](https://cursor.com/changelog)).
- **Single-purpose, repeatable actions** — Cursor's docs recommend a Skill instead ([Cursor subagents docs](https://cursor.com/docs/subagents)).
- **No cost ceiling on auto-decomposition** — practitioners report accidentally spawning dozens of subagents and burning through subscription quota; there is no in-IDE affordance to promote a background subagent to a full window for plan-mode follow-up, and subagent errors do not always bubble up ([Cursor Forum — Multi-task friction](https://forum.cursor.com/t/multi-task-friction-experience/160569), [Cursor Forum — Better subagent control](https://forum.cursor.com/t/better-subagent-control-in-the-cursor-ide/161413)). Cap fan-out manually.

## Example

A developer asks Cursor to update the docs site, run the linter, and regenerate the OpenAPI spec from one prompt:

**Without `/multitask`** — three queued prompts run sequentially. The developer waits for each before the next starts.

**With `/multitask`**:

```
/multitask Update the docs index, run the lint suite, and regenerate the OpenAPI spec from src/api
```

Cursor decomposes the request into three independent chunks, dispatches one async subagent per chunk, and surfaces each as a separate entry in the Agents Window. The developer keeps the editor session interactive — drafting the next prompt or reviewing earlier diffs — while the fleet runs. As each subagent finishes, its summary returns to the parent.

If the docs update and OpenAPI regeneration touch overlapping files, compose with `/worktree` so each subagent runs in an isolated checkout and merges land via separate branches.

## Key Takeaways

- `/multitask` runs async background subagents in parallel from the editor session — for queue parallelisation and auto-decomposition of one large request
- Each subagent has its own context window; only the final summary returns to the parent, preserving the parent's planning capacity
- `/multitask` gives context isolation only — compose with `/worktree` when subagents will edit overlapping files
- Justified when the parent has follow-up work during the wait; sequential dispatch is simpler for one-prompt sessions
- Cross-tool: Claude Code uses `background: true` plus the [Monitor tool](../claude/monitor-tool.md); Copilot CLI tears down subagents per invocation; Cursor adds explicit auto-decomposition

## Related

- [Cursor 3 Agents Window](agents-window.md) — the UI host for `/multitask`, with `/worktree` and `/best-of-n`
- [Async Non-Blocking Subagent Dispatch](../../multi-agent/async-non-blocking-subagent-dispatch.md) — the tool-agnostic pattern this specialises
- [Cross-Tool Subagent Comparison](../../multi-agent/cross-tool-subagent-comparison.md) — broader comparison of subagent definition formats and isolation models
- [Sub-Agents for Fan-Out Research](../../multi-agent/sub-agents-fan-out.md) — the underlying fan-out primitive
