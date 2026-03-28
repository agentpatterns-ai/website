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

> **Also known as:** Loop Detection & Stopping. For the broader pattern of automatic stopping mechanisms (iteration limits, cost thresholds, context budgets), see [Circuit Breakers for Agent Loops](circuit-breakers.md).

> Track file edit history within a session; when the same files are edited repeatedly without progress, signal the agent to try a different approach rather than continue repeating the same failing steps.

## The Micro-Loop Problem

Agents can enter micro-loops: edit a file, run tests, observe failure, edit the same file, observe the same failure, repeat. Without intervention, the agent exhausts its context window retrying an approach that does not work. The pattern is invisible from a prompt perspective — each iteration looks like forward progress to the agent.

Loop detection middleware monitors edit frequency and intervenes when repetition crosses a threshold. Per [LangChain's deep agent benchmark post](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/), this is one of the key harness-level interventions that improve agent reliability without model changes.

## Detection Mechanism

Track a count of edits per file path within the session. When the same file is edited beyond a threshold (for example, five times), flag it as a potential loop [unverified].

On detection:

1. Inject a prompt nudge into the agent's context: "You have edited `{file}` N times without passing tests. Consider whether a different approach is needed."
2. Optionally surface the last N test failure messages alongside the nudge, so the agent has full context when reconsidering.

The threshold is configurable. Five edits is a reasonable starting point; lower thresholds increase false positives, higher thresholds delay intervention.

## What Counts as Progress

Edit count alone is an imperfect signal. A more precise detector tracks whether test outcomes improve between edits:

- Same file edited, tests still failing at the same rate → likely loop
- Same file edited, test failures decreasing → iterative refinement, not a loop

Where test output is available, incorporate it into the detection logic. Where it is not, edit count is the fallback signal.

## Implementation

Loop detection runs as middleware monitoring tool calls — specifically Edit, Write, and Bash (for test execution). A PostToolUse hook is a natural implementation point:

```
PostToolUse(Edit | Write):
  increment edit_count[file_path]
  if edit_count[file_path] >= threshold:
    inject nudge prompt
```

The nudge message should state the observation factually, avoid prescribing a specific alternative, and include recent failure context so the agent is not reasoning blind.

## Doom-Loop Detection

Edit-count tracking catches repetitive editing but misses a distinct failure mode: the agent making the *same tool call* and receiving the *same error* repeatedly. Doom-loop detection targets this identical-failure pattern.

In the OPENDEV agent, doom-loop detection runs inside the decision/dispatch phase of each iteration ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)). The detector compares the current tool call and error against recent history. On repeated identical failures, it stops iteration entirely rather than injecting a nudge — identical failures will not self-resolve.

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

## Key Takeaways

- Track edit count per file path within a session; flag when a threshold is exceeded
- Inject a factual nudge on detection — state the observation, do not prescribe the fix
- Doom-loop detection catches identical tool-call/error pairs and terminates iteration
- Three layers: edit-count tracking, doom-loop detection, iteration cap
- Distinguish from the Ralph Wiggum Loop: loop detection is intra-session, not cross-session

## Unverified Claims

- Five edits as a reasonable starting threshold for loop detection [unverified]

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
- [Event Sourcing for Agents](event-sourcing-for-agents.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
