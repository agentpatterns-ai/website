---
title: "Loop Detection for AI Agents: Stopping Micro-Loops"
term: "Loop Detection for AI Agents"
description: "Loop detection tracks repeated file edits within a session and injects a prompt nudge when an agent is stuck in an unproductive cycle."
tags:
  - agent-design
  - workflows
  - source:opendev-paper
  - observability
  - tool-agnostic
aliases:
  - Loop Detection & Stopping
last_reviewed: 2026-06-13
maturity: established
---

# Loop Detection for AI Agents: Stopping Micro-Loops

> Loop detection tracks repeated file edits within a session and nudges the agent to change approach when those edits stop making progress.

Learn it hands-on: [Catching the Wasted Run](https://learn.agentpatterns.ai/observability/catching-the-wasted-run/) — a guided lesson with quizzes.

Also known as: Loop Detection & Stopping. For the broader pattern of automatic stopping mechanisms (iteration limits, cost thresholds, context budgets), see [Circuit Breakers for Agent Loops](circuit-breakers.md). To budget the context window itself, see [Context Budget Allocation](../context-engineering/context-budget-allocation.md).

## The micro-loop problem

Agents enter micro-loops: edit a file, run tests, see the failure, edit the same file, see the same failure, repeat. Without intervention, the agent exhausts its context window retrying an approach that does not work. Each iteration looks like forward progress from the inside.

Loop detection middleware watches edit frequency and steps in when repetition crosses a threshold. It is one of the harness-level interventions [LangChain credits](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) for moving their agent from rank 30 to rank 5 on Terminal Bench 2.0 without changing the underlying model.

## Detection mechanism

Track edits per file path within the session. When the same file is edited beyond a set threshold, flag it as a potential loop. LangChain's `LoopDetectionMiddleware` takes this shape. It adds context like "consider reconsidering your approach" after N edits to the same file, with N left to the operator to tune ([LangChain, 2026](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

On detection:

1. Inject a prompt nudge: "You have edited `{file}` N times without passing tests. Consider whether a different approach is needed."
2. Optionally surface the last N test failure messages alongside the nudge so the agent is not reconsidering blind.

There is no published canonical threshold. Lower values interrupt legitimate iterative refinement. Higher values let more context burn before the nudge fires.

## What counts as progress

Edit count alone is an imperfect signal. Where test output is available, track whether failures fall between edits:

- Same file edited, failures steady → likely loop
- Same file edited, failures falling → iterative refinement

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

## Doom-loop detection

Edit-count tracking misses a distinct failure mode: the agent making the same tool call and getting the same error over and over. Doom-loop detection targets this identical-failure pattern.

In the OPENDEV agent, doom-loop detection runs inside the decision and dispatch phase of each iteration. It compares the current tool call and error against recent history ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)). On repeated identical failures, it stops iteration entirely rather than nudging, because identical failures will not self-resolve.

## Iteration cap

Pattern-based detectors can miss iterations that differ each time but are just as unproductive. A hard iteration cap per conversation prevents runaway execution whether or not a detector fires ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)).

Three layers protect against unproductive execution:

1. Edit-count tracking catches repeated editing of the same file.
2. Doom-loop detection catches identical tool-call and error pairs.
3. Iteration cap catches all remaining runaway execution.

## Distinction from the Ralph Wiggum Loop

The [Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md) describes a cross-session failure pattern: an agent restarts with fresh context and repeats the same approach that already failed in a prior session. The fix is session-level continuity — [reading prior session artifacts](trajectory-logging-progress-files.md) before acting.

Loop detection addresses an intra-session pattern: repetition within a single context window. The intervention is a prompt nudge, not a session restart. Both produce similar symptoms but need different fixes.

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

## When this backfires

Loop detection is not free. Across 220 instrumented agent runs, only half of 12 automated loop interventions reduced their target signal. One generated 13x more signals than it suppressed by triggering its own detector ([boucle2026, 2026](https://dev.to/boucle2026/how-to-tell-if-your-ai-agent-is-stuck-with-real-data-from-220-loops-4d4h)). Watch for these failure modes:

- False positives on legitimate iteration: to a counter, a tight refactor on a single file looks the same as an edit loop. Thresholds tuned for loops interrupt focused iteration.
- Nudge pollution: every injected nudge consumes context the agent could use for code. On agents already near the [context limit](../context-engineering/context-window-dumb-zone.md), it speeds up the failure it was meant to prevent.
- Detector-on-detector amplification: if one layer fires on output another produces, signals multiply instead of settling.
- Problems no nudge can fix: missing requirements or wrong architecture encode a human decision, and no threshold fixes them.

Measure whether a given intervention reduces the signal it targets, and remove the ones that do not.

## FAQ

**What edit-count threshold should trigger the nudge?**

There is no published canonical threshold; LangChain's middleware leaves N to the operator to tune. The tradeoff runs both ways — a low value interrupts legitimate iterative refinement, while a high one lets more context burn before the nudge fires. Tune it against your own runs rather than adopting a number from a reference implementation.

**How do I distinguish a real loop from focused iteration?**

Edit count alone cannot. Where test output is available, track whether failures fall between edits: the same file edited with failures holding steady is likely a loop, while the same file edited with failures falling is iterative refinement. Edit count is the fallback for cases where test output is not available.

**What does a nudge cost when it fires wrongly?**

Every injected nudge consumes context the agent could otherwise spend on code, so on an agent already near the [context limit](../context-engineering/context-window-dumb-zone.md), a false positive speeds up the failure it was meant to prevent. Detectors can also amplify each other when one fires on output another produces, and no threshold fixes missing requirements or wrong architecture.

## Key Takeaways

- Track edit count per file path within a session; flag when a threshold is exceeded
- Inject a factual nudge on detection — state the observation, do not prescribe the fix
- Doom-loop detection catches identical tool-call/error pairs and terminates iteration
- Three layers: edit-count tracking, doom-loop detection, iteration cap
- Distinguish from the Ralph Wiggum Loop: loop detection is intra-session, not cross-session
- Measure intervention effectiveness — roughly half of automated loop responses do not help or actively worsen outcomes ([boucle2026, 2026](https://dev.to/boucle2026/how-to-tell-if-your-ai-agent-is-stuck-with-real-data-from-220-loops-4d4h))

## Related

- [Circuit Breakers for Agent Loops](circuit-breakers.md)
- [Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md)
- [Trajectory Logging and Progress Files](trajectory-logging-progress-files.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Agent Debugging](agent-debugging.md)
- [Agent Observability: OTel, Cost Tracking, Trajectory Logs](agent-observability-otel.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md)
