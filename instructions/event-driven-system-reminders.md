---
title: "Event-Driven System Reminders for AI Agent Development"
description: "Combat instruction fade-out by injecting targeted reminders at specific agent execution events rather than bloating the static system prompt."
tags:
  - context-engineering
  - instructions
  - source:opendev-paper
---

# Event-Driven System Reminders

> Inject targeted guidance at specific points during agent execution to combat instruction fade-out and reinforce safety constraints without bloating the static system prompt.

## The Problem: Instruction Fade-Out

Static system prompts lose effectiveness over extended sessions. The model progressively deprioritizes initial instructions as conversation history grows — even when those instructions remain present in context ([Bui, 2025 §3.2](https://arxiv.org/abs/2603.05344)).

This is distinct from context compression. Instructions may survive compaction but still fail to influence behavior because they occupy a low-attention region of the context ([Bui, 2025 §3.2](https://arxiv.org/abs/2603.05344)). Research on long-context LLMs confirms that models attend most reliably to content at the beginning and end of context, with degraded recall for middle-positioned content ([Liu et al., 2023](https://arxiv.org/abs/2307.03172)).

## Event Detectors

Rather than repeating all instructions continuously, event detectors monitor for specific conditions that warrant targeted re-injection ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)):

- **Repeated tool failures** — the agent is stuck in a retry loop
- **Approaching token budget** — context pressure requires strategy adjustment
- **Safety violations** — dangerous commands attempted or approval denied
- **Extended execution time** — long-running sessions where fade-out is likely

Each detector triggers reminder injection at the next decision point rather than interrupting mid-execution.

## Template Resolution

Triggered events are matched against reminder templates that combine static guidance with dynamic variables — current file, last error, iteration count, tool failure count. Templates fall into three categories ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)):

- **Safety guardrails** — reinforce constraints on destructive operations
- **Tool-usage guidance** — redirect tool selection when the agent is using the wrong approach
- **Error-recovery strategies** — provide escalating recovery tactics

## Escalating Severity via Guardrail Counters

Guardrail counters track violation frequency and escalate reminder severity accordingly ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)):

| Count | Severity | Tone |
|-------|----------|------|
| 1 | Advisory | Suggest alternative approach |
| 2--3 | Warning | State constraint explicitly |
| 4+ | Mandatory | Require compliance, block progress |

This graduated response avoids overreacting to a single misstep while preventing persistent violations.

## User-Role Injection

Reminders are injected as user messages rather than appended to the system prompt. User messages appear in conversation history and remain in the model's attention window more reliably than system prompt additions. This placement also allows explicit user commands to override reminders when appropriate ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)).

## Graceful Degradation

If an event detector fails, the system continues without reminder injection. Reminders are additive safety — not critical-path requirements. The agent operates with its baseline system prompt, which remains functional. This prevents reminder infrastructure failures from cascading into agent failures ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)).

## Example

The following shows a minimal Python implementation of event-driven reminder injection. A `ReminderMiddleware` class wraps the message list, monitors tool call outcomes, and injects a user-role message when a detector fires.

```python
class ReminderMiddleware:
    TOOL_FAILURE_THRESHOLD = 3

    TEMPLATES = {
        "repeated_tool_failure": (
            "You have called `{tool}` {count} times without success. "
            "Stop retrying. Review what you know and try a different approach."
        ),
        "approaching_token_budget": (
            "You are approaching the context limit. Summarise your findings "
            "so far in under 200 words before continuing."
        ),
    }

    def __init__(self):
        self.tool_failure_counts: dict[str, int] = {}

    def record_tool_result(self, tool_name: str, is_error: bool) -> str | None:
        if not is_error:
            self.tool_failure_counts.pop(tool_name, None)
            return None
        self.tool_failure_counts[tool_name] = (
            self.tool_failure_counts.get(tool_name, 0) + 1
        )
        count = self.tool_failure_counts[tool_name]
        if count >= self.TOOL_FAILURE_THRESHOLD:
            return self.TEMPLATES["repeated_tool_failure"].format(
                tool=tool_name, count=count
            )
        return None

    def inject(self, messages: list, reminder: str) -> list:
        # Inject as a user message so it lands in the attention window
        return messages + [{"role": "user", "content": reminder}]
```

A reminder is only generated when the failure count crosses the threshold. The `inject` method appends it as a `user` message — not a system prompt addition — consistent with the user-role injection pattern described above. If `record_tool_result` is never called (e.g., the detector crashes), `messages` is returned unchanged, preserving graceful degradation.

## When This Backfires

Event-driven reminders add value for long-running, multi-step agents but introduce real costs in simpler contexts:

- **Short sessions**: Reminder infrastructure is pure overhead when a session rarely exceeds a few dozen exchanges. Instruction fade-out is negligible; detector and template machinery adds complexity without benefit.
- **Detector false positives**: A badly tuned failure threshold fires on normal retry behavior, injecting redundant guidance into a functioning flow. Accumulated user-role injections consume tokens and can themselves occupy low-attention context positions — recreating the problem they're meant to solve.
- **Template drift**: If reminder templates are not kept consistent with the system prompt, injected user messages can contradict baseline instructions, producing confused behavior that is harder to debug than simple fade-out.
- **Context token pressure**: Each injected reminder consumes tokens. Under tight context budgets, frequent reminder injection accelerates the context pressure it aims to mitigate ([Bui, 2025 §2.3.4](https://arxiv.org/abs/2603.05344)).

Prefer event-driven reminders for long-running or safety-critical agents. For short-lived, well-scoped tasks, a well-structured static system prompt is lower risk.

## Key Takeaways

- Static system prompts fade in effectiveness over extended sessions; event-driven reminders counter this.
- Detect specific conditions (repeated failures, budget pressure, safety violations) rather than injecting reminders on a schedule.
- Escalate reminder severity via guardrail counters: advisory, then warning, then mandatory.
- Inject reminders as user messages for better attention persistence than system prompt additions.
- Design reminders as additive safety — detector failures must not break the agent.

## Related

- [Objective Drift: When Agents Lose the Thread](../anti-patterns/objective-drift.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](../tool-engineering/hooks-lifecycle-events.md)
- [Steering Running Agents](../agent-design/steering-running-agents.md)
- [Domain-Specific System Prompts](domain-specific-system-prompts.md)
- [Post-Compaction Re-read Protocol](post-compaction-reread-protocol.md)
- [Context Compression Strategies: Offloading and Summarisation](../context-engineering/context-compression-strategies.md) — the compression mechanism that event-driven reminders complement
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why adding more instructions past a threshold degrades compliance; reminders counter this without adding static rules
