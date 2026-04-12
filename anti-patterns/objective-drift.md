---
title: "Objective Drift: When Agents Lose Sight of the Goal"
description: "Objective drift occurs when context compression loses task specifics, causing agents to solve a subtly different problem than originally assigned."
tags:
  - agent-design
  - context-engineering
  - source:opendev-paper
aliases:
  - goal drift
  - task drift
---

# Objective Drift: When Agents Lose the Thread

> After context compression, agents can continue working productively on a subtly wrong objective — the original intent lost in summarisation.

## Why It Happens

Summarisation favours high-frequency content. A constraint ("do not change public method signatures") appears once; the core task ("refactor for DI") recurs across many messages — the constraint is discarded as noise ([LangChain](https://blog.langchain.com/context-management-for-deepagents/)). Downstream steps compound the error: each tool call is consistent with the compressed objective, so the agent builds toward the wrong target with no internal signal.

A second trigger is instruction fade-out: models deprioritize initial instructions as history grows, even when they remain present ([Bui, 2026 §3.2](https://arxiv.org/abs/2603.05344)).

## Detection and Mitigation

Signals: the agent "completes" without satisfying the original requirement, output format diverges from spec, or a subtly different problem is solved.

**Preserve intent in structured summaries.** A named `session_intent` field survives compression better than prose — [LangChain recommends](https://blog.langchain.com/context-management-for-deepagents/) structured summaries that retain task objectives.

**Anchor constraints in system prompt.** System-prompt content is less likely to be paraphrased away during summarisation.

**Bounded tasks.** The [Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md) bounds each session to one task; each restart re-reads the original specification from disk.

**[Event-driven reminders](../instructions/event-driven-system-reminders.md).** Re-inject objectives at decision points ([Bui, 2026 §2.3.4](https://arxiv.org/abs/2603.05344)).

## Example

A long-running agent is given the task: "Refactor the `UserService` class to use dependency injection. Do not change any public method signatures." After dozens of tool calls the context is compressed. The prose summary retains "refactor UserService for DI" but drops the constraint about method signatures. The agent subsequently renames `get_user_by_id` to `find_user` — coherent with the refactor goal, but violating the original constraint.

The mitigation is a structured session intent file written before the agent starts, preserved verbatim through compression:

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

This combination — structured intent file plus system-prompt anchor — ensures the exact constraints survive summarisation and remain attended to throughout the session.

## When This Backfires

- **Short sessions**: `session_intent.json` adds overhead for sessions that will never reach compaction.
- **Exploratory tasks**: Strict anchoring prevents legitimate course corrections mid-session.
- **Compaction policy mismatch**: Structured summaries only help if the compressor preserves named fields; many paraphrase them anyway.

## Key Takeaways

- Objective drift occurs when summarisation loses task specifics or instructions fade from attention.
- The agent appears productive but solves the wrong problem — drift is subtle, not obvious.
- Structured summaries with a named session-intent field resist drift better than prose.
- [Event-driven reminders](../instructions/event-driven-system-reminders.md) counter fade-out by re-injecting objectives at decision points.
- Bounded sessions ([Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md)) prevent drift from accumulating across iterations.

## Related

- [The Ralph Wiggum Loop](../agent-design/ralph-wiggum-loop.md)
- [Agent Backpressure](../agent-design/agent-backpressure.md)
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Post-Compaction Re-read Protocol](../instructions/post-compaction-reread-protocol.md) — restores instruction compliance after compaction
- [Event-Driven System Reminders](../instructions/event-driven-system-reminders.md) — counters fade-out by injecting targeted reminders
- [Context Compression Strategies: Offloading and Summarisation](../context-engineering/context-compression-strategies.md) — tiered compression that preserves task intent through summarisation
- [Context Poisoning](context-poisoning.md) — hallucinated facts compound through context
- [Distractor Interference](distractor-interference.md) — irrelevant instructions reduce compliance
- [The Kitchen Sink Session](session-partitioning.md) — mixing unrelated tasks fills context with noise
- [Assumption Propagation](assumption-propagation.md) — early misunderstandings compound over time, similar to how drift compounds after compression
- [The Infinite Context Anti-Pattern](infinite-context.md) — context overload dilutes attention, accelerating drift
- [Token Preservation Backfire](token-preservation-backfire.md) — token-saving instructions create a competing objective that undermines task completion
- [Spec Complexity Displacement](spec-complexity-displacement.md) — constraints that grow too complex to track reliably, compounding drift risk
