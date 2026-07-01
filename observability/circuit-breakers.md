---
title: "Circuit Breakers for Agent Loops"
term: "Circuit Breakers"
description: "Circuit breakers stop agent loops when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior signal a halt."
aliases:
  - Loop Detection & Stopping
tags:
  - agent-design
  - tool-agnostic
  - observability
last_reviewed: 2026-07-01
maturity: adopted
---

# Circuit Breakers for Agent Loops

> Circuit breakers stop agent loops when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior signal a halt rather than continuation.

Related lesson: [Cost Controls and Circuit Breakers](https://learn.agentpatterns.ai/harness-engineering/cost-controls-and-circuit-breakers/) — this concept features in a hands-on lesson with quizzes.

> Also known as: Loop Detection and Stopping. To detect repetitive edits within a session, see [Loop Detection](loop-detection.md).

## The loop problem

Agents in open-ended loops consume resources without making progress. They apply the same wrong fix, or retry a flaky test 20 times. Without stopping conditions, a loop runs until the context window fills or the session is killed. That leaves degraded context and unusable partial output.

## Stopping signals

Five signals warrant a circuit break:

1. Iteration limit reached. The agent has taken N steps without completing the task. N varies by task type. Claude Code sub-agents support a `maxTurns` field ([Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents)) that enforces this at the runtime level.
2. Repeated failure. The same tool call fails repeatedly with the same error. A 429 three times in a row will continue to 429. A test failing for a logic error will continue to fail. A stalled stream is the same signal at the transport layer: Claude Code's streaming idle watchdog, now on by default, aborts and retries a response stream that produces no events for 5 minutes — a runtime breaker the model cannot override, disabled with `CLAUDE_ENABLE_STREAM_WATCHDOG=0` ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).
3. Repetition detected. The agent is doing what it already did — fetching the same URL, reading the same file, attempting the same fix. Repetition without new information is a stuck loop.
4. Context budget exceeded. The context window is approaching the ["dumb zone"](../context-engineering/context-window-dumb-zone.md) where output quality degrades. Chroma's [Context Rot](https://research.trychroma.com/context-rot) study tested 18 frontier models including GPT-4.1, Claude Opus 4, and Gemini 2.5. It found every model degrades non-uniformly as input grows, with onset depending on task similarity and distractor density. Trip the breaker when recall or coherence drops on your task, not at a fixed token count.
5. Cost threshold exceeded. The task has consumed more than the expected budget. Cost overrun often correlates with loops.

## Graceful degradation

When a circuit breaker trips, the agent should:

1. Stop running new actions.
2. Return the partial results finished before the break.
3. Explain what triggered the stop and what remains incomplete.
4. Escalate to a human if the pipeline has a human gate.

Partial results are more useful than nothing. Return what you have. Do not discard completed work.

## Configuration

| Signal | Configuration | Enforcement |
|--------|-------------|-------------|
| Iteration limit | `maxTurns` in agent frontmatter | Runtime |
| Cost threshold | Session budget settings | Runtime |
| Error rate | Agent instruction + hook | Instruction / hook |
| Repetition | Agent instruction + hook | Instruction / hook |
| Context usage | Agent instruction | Instruction |

The model cannot override runtime enforcement (maxTurns, cost budgets). Instruction-level enforcement depends on the model obeying instructions, so it is less reliable for safety-critical stops. Hooks offer a middle ground: deterministic scripts that monitor and trigger a stop.

Circuit breakers are the enforcement mechanism for [context health](../context-engineering/context-window-dumb-zone.md) — without them, context management guidelines are advisory rather than operational limits.

## Example

This Claude Code sub-agent definition combines a runtime-enforced `maxTurns` limit with an instruction-level check for repeated failure. Both signals are present, so the agent stops whether it hits the turn ceiling or runs into a recurring error.

```yaml
# .claude/agents/research-agent.md frontmatter
---
name: research-agent
description: Fetches and summarises web sources for a given topic
tools:
  - WebFetch
  - Read
  - Write
maxTurns: 20
---
```

```markdown
# Research Agent System Prompt

You are a research agent. Fetch and summarise up to 5 sources for the given topic.

## Circuit-breaker rules

1. **Iteration limit** — enforced by `maxTurns: 20` above; you will be stopped automatically.
2. **Repeated failure** — if the same URL returns an error three times in a row, skip it,
   note it as unreachable, and move to the next source. Do not retry indefinitely.
3. **Repetition detection** — if you find yourself fetching a URL you have already fetched
   this session, stop and return what you have collected so far.
4. **Partial results** — when you stop for any reason before completing all 5 sources,
   return the summaries you have already written plus a short note explaining what
   triggered the stop and which sources were not completed.
```

The `maxTurns: 20` field is enforced at the Claude Code runtime level and cannot be overridden by model reasoning. The instruction-level checks handle error-rate and repetition signals, which the runtime does not detect automatically.

## When this backfires

Circuit breakers detect failure modes; they do not guarantee correctness. Set too aggressively, they become the failure mode. A reasonable practitioner would push back in at least three situations:

- Iteration limits trip on legitimate work. Setting `maxTurns` low enough to catch pathological loops also cuts off legitimate multi-step refactors or research tasks. Several production frameworks have open issues where agents halt mid-task on "stopped due to max iterations" even when making forward progress ([openai-agents-python#844](https://github.com/openai/openai-agents-python/issues/844), [langflow#10607](https://github.com/langflow-ai/langflow/issues/10607)). Raise the ceiling for task classes that legitimately need 50+ turns.
- Repetition detection flags valid re-reads. Re-reading the same file after an edit, or refetching a URL after a 429 backoff, are normal behaviors, not stuck loops. Naive "did we already fetch this?" heuristics fire on both.
- Cost thresholds penalize exploration. Exploratory research agents legitimately consume variable budgets. A hard cost cap trips on successful discovery runs as readily as on loops. The signal is cost without progress, not cost alone.
- Instruction-level stops are model-dependent. Signals 2, 3, and 5 rely on the model reading its own circuit-breaker rules and obeying them. If the model ignores the instruction mid-reasoning, the stop never fires. For safety-critical stops, prefer runtime enforcement (`maxTurns`, hooks) over instructions.

The steelman: if your agents already fail gracefully on their own — return partial results, detect their own thrash — then another stopping layer mostly creates false positives. Instrument first. Add breakers where instrumentation shows real loops, not as a precaution.

## Key Takeaways

- Five stopping signals: iteration limit, repeated failure, repetition, context budget, cost threshold
- `maxTurns` provides runtime-enforced iteration limits; instruction-based checks can be overridden by the model
- Graceful degradation: return partial results + failure explanation, never discard completed work

## Related

- [Agent Circuit Breaker](../agent-design/agent-circuit-breaker.md) — tool-level state machine that blocks calls to degraded external tools; complementary to loop-level breakers here
- [Loop Detection](loop-detection.md)
- [Centralized LLM Gateway for Per-Dimension Agent Budgets](llm-gateway-per-dimension-budgets.md) — the fleet-wide budget control that complements this per-loop cost breaker
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../workflows/human-in-the-loop.md)
- [Idempotent Agent Operations: Safe to Retry](../agent-design/idempotent-agent-operations.md)
- [Context Window Management: The Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Agent Debugging: Diagnosing Bad Agent Output](agent-debugging.md)
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
