---
title: "Loop Detection for AI Agents: Stopping Micro-Loops"
description: "Loop detection tracks repeated file edits within a session and injects a prompt nudge when an agent is stuck in an unproductive cycle."
tags:
  - agent-design
  - workflows
  - source:opendev-paper
  - observability
aliases:
  - Loop Detection & Stopping
---
# Loop Detection

> **Also known as:** Loop Detection & Stopping. For the broader pattern of automatic stopping mechanisms (iteration limits, cost thresholds, context budgets), see [Circuit Breakers for Agent Loops](circuit-breakers.md). For budgeting the context window itself, see [Context Budget Allocation](../context-engineering/context-budget-allocation.md).

> Track file edit history within a session; when the same files are edited repeatedly without progress, signal the agent to try a different approach rather than continue repeating the same failing steps.

## The Micro-Loop Problem

Agents enter micro-loops: edit a file, run tests, observe failure, edit the same file, observe the same failure, repeat. Without intervention, the agent exhausts its context window retrying an approach that does not work. Each iteration looks like forward progress from the inside.

Loop detection middleware watches edit frequency and intervenes when repetition crosses a threshold — one of the harness-level interventions [LangChain credits](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) for moving their agent from rank 30 to rank 5 on Terminal Bench 2.0 without changing the underlying model.

## Detection Mechanism

Track edits per file path within the session. When the same file is edited beyond a configured threshold, flag it as a potential loop. LangChain's `LoopDetectionMiddleware` takes this shape, adding context like "consider reconsidering your approach" after N edits to the same file, with N left to the operator to tune ([LangChain, 2026](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

On detection:

1. Inject a prompt nudge: "You have edited `{file}` N times without passing tests. Consider whether a different approach is needed."
2. Optionally surface the last N test failure messages alongside the nudge so the agent is not reconsidering blind.

There is no published canonical threshold; lower values interrupt legitimate iterative refinement, higher values let more context burn before the nudge fires.

## What Counts as Progress

Edit count alone is an imperfect signal. Where test output is available, track whether failures decrease between edits:

- Same file edited, failures steady → likely loop
- Same file edited, failures decreasing → iterative refinement

Where test output is not available, edit count is the fallback.

## Implementation

Loop detection runs as middleware on Edit, Write, and Bash (for test execution). A PostToolUse hook is a natural implementation point:

```
PostToolUse(Edit | Write):
  increment edit_count[file_path]
  if edit_count[file_path] >= threshold:
    inject nudge prompt
```

Nudges should state the observation factually, avoid prescribing a specific alternative, and include recent failure context so the agent is not reasoning blind.

## Doom-Loop Detection

Edit-count tracking misses a distinct failure mode: the agent making the *same tool call* and receiving the *same error* repeatedly. Doom-loop detection targets this identical-failure pattern.

In the OPENDEV agent, doom-loop detection runs inside the decision/dispatch phase of each iteration, comparing the current tool call and error against recent history ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)). On repeated identical failures, it stops iteration entirely rather than nudging — identical failures will not self-resolve.

## Iteration Cap

Pattern-based detectors can miss non-identical but equally unproductive iterations. A hard iteration cap per conversation prevents runaway execution regardless of detection ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)).

Three layers protect against unproductive execution:

1. **Edit-count tracking** — catches repetitive editing of the same file
2. **Doom-loop detection** — catches identical tool-call/error pairs
3. **Iteration cap** — catches all remaining runaway execution

## Distinction from the Ralph Wiggum Loop

The [Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md) describes a cross-session failure pattern: an agent restarts with fresh context and repeats the same approach that already failed in a prior session. The fix is session-level continuity — reading prior session artifacts before acting.

Loop detection addresses an intra-session pattern: repetition within a single context window. The intervention is a prompt nudge, not a session restart. Both produce similar symptoms but require different fixes.

## Example

A PostToolUse hook that detects edit loops and injects a nudge:

```python
# hooks/loop_detector.py
from collections import defaultdict

edit_counts = defaultdict(int)
THRESHOLD = 5

def post_tool_use(tool_name, tool_input, tool_result):
    if tool_name not in ("Edit", "Write"):
        return None
    file_path = tool_input.get("file_path", "")
    edit_counts[file_path] += 1
    if edit_counts[file_path] >= THRESHOLD:
        return {
            "type": "user",
            "content": (
                f"You have edited `{file_path}` {edit_counts[file_path]} times. "
                "Consider whether a different approach is needed before editing again."
            ),
        }
    return None
```

Register in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "python hooks/loop_detector.py" }] }
    ]
  }
}
```

## When This Backfires

Loop detection is not free. Across 220 instrumented agent runs, only half of 12 automated loop interventions actually reduced their target signal; one generated 13x more signals than it suppressed by triggering its own detector ([boucle2026, 2026](https://dev.to/boucle2026/how-to-tell-if-your-ai-agent-is-stuck-with-real-data-from-220-loops-4d4h)). Failure modes to watch for:

- **False positives on legitimate iteration**: tight refactors on a single file look identical to an edit loop from a counter's view. Thresholds tuned for loops interrupt focused iteration.
- **Nudge pollution**: every injected nudge consumes context the agent could use for code, and on agents already near the context limit it accelerates the failure it was meant to prevent.
- **Detector-on-detector amplification**: if one layer fires on output another produces, signals multiply instead of settling.
- **Problems no nudge can fix**: missing requirements or wrong architecture encode a human decision; no threshold fixes them.

Measure whether a specific intervention reduces the signal it targets, and remove ones that do not.

## Key Takeaways

- Track edit count per file path within a session; flag when a threshold is exceeded
- Inject a factual nudge on detection — state the observation, do not prescribe the fix
- Doom-loop detection catches identical tool-call/error pairs and terminates iteration
- Three layers: edit-count tracking, doom-loop detection, iteration cap
- Distinguish from the Ralph Wiggum Loop: loop detection is intra-session, not cross-session
- Measure intervention effectiveness — roughly half of automated loop responses do not help or actively worsen outcomes ([boucle2026, 2026](https://dev.to/boucle2026/how-to-tell-if-your-ai-agent-is-stuck-with-real-data-from-220-loops-4d4h))

## Related

- [Circuit Breakers for Agent Loops](circuit-breakers.md)
- [Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md)
- [Trajectory Logging and Progress Files](trajectory-logging-progress-files.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Reasoning Budget Allocation](../agent-design/reasoning-budget-allocation.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [PostToolUse Hook for BSD/GNU Tool Miss Detection](../tool-engineering/posttooluse-bsd-gnu-detection.md)
- [Agent Debugging](agent-debugging.md)
- [Agent Observability: OTel, Cost Tracking, Trajectory Logs](agent-observability-otel.md)
- [Making Application Observability Legible to Agents](observability-legible-to-agents.md)
- [Event Sourcing for Agents](event-sourcing-for-agents.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
