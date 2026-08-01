---
title: "Objective Drift: When Agents Lose Sight of the Goal"
term: "Objective Drift"
description: "Objective drift occurs when context compression loses task specifics, causing agents to solve a subtly different problem than originally assigned."
tags:
  - agent-design
  - context-engineering
  - source:opendev-paper
  - tool-agnostic
  - anti-pattern
aliases:
  - goal drift
  - task drift
last_reviewed: 2026-05-27
maturity: established
---

# Objective Drift: When Agents Lose the Thread

> After context compression, agents can continue working productively on a subtly wrong objective — the original intent lost in summarization.

Learn it hands-on: work through the [Objective Drift guided lesson](https://learn.agentpatterns.ai/anti-patterns/objective-drift/), which includes quizzes.

## Why it happens

Summarization favors high-frequency content. A constraint such as "do not change public method signatures" appears once. The core task, "refactor for DI", recurs across many messages. So summarization discards the constraint as noise ([LangChain on context management](https://blog.langchain.com/context-management-for-deepagents/)). Downstream steps compound the error. Each tool call is consistent with the compressed objective, so the agent builds toward the wrong target with no internal signal.

A second trigger is instruction fade-out. Models deprioritize the initial instructions as history grows, even when those instructions remain present ([Bui, 2026 §3.2](https://arxiv.org/abs/2603.05344)).

## Detection and mitigation

Watch for these signals: the agent "completes" without satisfying the original requirement, the output format diverges from the spec, or the agent solves a subtly different problem.

Preserve intent in structured summaries. A named `session_intent` field survives compression better than prose. [LangChain recommends](https://blog.langchain.com/context-management-for-deepagents/) structured summaries that keep task objectives. A [session recap](../agent-design/session-recap.md) formalizes this as a fixed-schema, agent-authored artifact, written at each boundary: compaction, resume, or fork.

Anchor constraints in the system prompt. System-prompt content is less likely to be paraphrased away during summarization.

Use bounded tasks. The [Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md) bounds each session to one task. Each restart re-reads the original specification from disk.

Add [event-driven reminders](../../instructions/event-driven-system-reminders.md). Re-inject objectives at decision points ([Bui, 2026 §2.3.4](https://arxiv.org/abs/2603.05344)).

## Example

A long-running agent receives this task: "Refactor the `UserService` class to use dependency injection. Do not change any public method signatures." After dozens of tool calls, compaction compresses the context. The prose summary keeps "refactor UserService for DI" but drops the constraint about method signatures. The agent then renames `get_user_by_id` to `find_user`. That fits the refactor goal, but it violates the original constraint.

The fix is a structured session-intent file. You write it before the agent starts, and it survives compression verbatim:

```json
// session_intent.json — written by the orchestrator, re-read after compaction
{
  "objective": "Refactor UserService to use dependency injection",
  "constraints": [
    "Do not change any public method signatures",
    "Do not modify files outside src/services/user_service.py and its tests"
  ],
  "completion_criteria": "All existing tests pass; no public method signatures changed",
  "created_at": "2025-11-14T09:00:00Z"
}
```

The system prompt instructs the agent to re-read `session_intent.json` at the start of every new message and before any file modification:

```python
SYSTEM_PROMPT = """
You are a refactoring agent. Before each action:
1. Read session_intent.json
2. Confirm your planned action satisfies all constraints listed there
3. If any constraint would be violated, stop and report instead of proceeding
"""
```

Together, the structured intent file and the system-prompt anchor keep the exact constraints through summarization and hold the agent's attention on them all session.

## When this backfires

- Short sessions: `session_intent.json` adds overhead for sessions that never reach compaction.
- Exploratory tasks: strict anchoring blocks legitimate course corrections mid-session.
- Compaction policy mismatch: structured summaries only help if the compressor keeps named fields, and many paraphrase them anyway.

## FAQ

**Why does compression drop the constraint rather than the main task?**

Summarization favors high-frequency content. A constraint such as "do not change public method signatures" appears once, while the core task recurs across many messages, so the compressor discards the constraint as noise. Downstream steps then compound the error: each tool call is consistent with the compressed objective, so the agent builds toward the wrong target with no internal signal.

**How is instruction fade-out different from losing text to summarization?**

Fade-out needs no deletion. Models deprioritize the initial instructions as history grows, even when those instructions remain present in context ([Bui, 2026 §3.2](https://arxiv.org/abs/2603.05344)). That makes it a second, independent trigger for drift, and it calls for a different counter: [event-driven reminders](../../instructions/event-driven-system-reminders.md) that re-inject objectives at decision points.

**When is a session-intent file not worth writing?**

On short sessions that never reach compaction, where it is pure overhead, and on exploratory tasks, where strict anchoring blocks legitimate mid-session course corrections. It also fails on a compaction-policy mismatch: structured summaries only survive if the compressor keeps named fields, and many compressors paraphrase them anyway, leaving the intent no better protected than prose.

## Key Takeaways

- Objective drift occurs when summarization loses task specifics or instructions fade from attention.
- The agent appears productive but solves the wrong problem — drift is subtle, not obvious.
- Structured summaries with a named session-intent field resist drift better than prose.
- [Event-driven reminders](../../instructions/event-driven-system-reminders.md) counter fade-out by re-injecting objectives at decision points.
- Bounded sessions ([Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md)) prevent drift from accumulating across iterations.

## Related

- [The Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md)
- [Attention Latch: When Agents Stay Anchored to Stale Instructions](../agent-design/attention-latch.md) — the structural over-squashing mechanism behind instruction fade-out
- [Post-Compaction Re-read Protocol](../../instructions/post-compaction-reread-protocol.md) — restores instruction compliance after compaction
- [Event-Driven System Reminders](../../instructions/event-driven-system-reminders.md) — counters fade-out by injecting targeted reminders
- [Context Compression Strategies: Offloading and Summarization](../../context-engineering/context-compression-strategies.md) — tiered compression that preserves task intent through summarization
- [Context Poisoning](context-poisoning.md) — hallucinated facts compound through context
- [Distractor Interference](distractor-interference.md) — irrelevant instructions reduce compliance
- [The Kitchen Sink Session](session-partitioning.md) — mixing unrelated tasks fills context with noise
- [Assumption Propagation](assumption-propagation.md) — early misunderstandings compound over time, similar to how drift compounds after compression
- [The Infinite Context Anti-Pattern](infinite-context.md) — context overload dilutes attention, accelerating drift
- [Token Preservation Backfire](token-preservation-backfire.md) — token-saving instructions create a competing objective that undermines task completion
- [Spec Complexity Displacement](spec-complexity-displacement.md) — constraints that grow too complex to track reliably, compounding drift risk
