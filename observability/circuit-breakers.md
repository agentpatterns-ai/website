---
title: "Circuit Breakers for Agent Loops"
description: "Circuit breakers stop agent loops when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior signal a halt."
aliases:
  - Loop Detection & Stopping
tags:
  - agent-design
  - tool-agnostic
---

# Circuit Breakers for Agent Loops

> **Also known as:** Loop Detection & Stopping. For the complementary technique of detecting repetitive edits within a session, see [Loop Detection](loop-detection.md).

> Stop agents automatically when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior are signals to halt and surface the failure rather than continue.

## The Loop Problem

Agents in open-ended loops consume resources without progress — applying the same incorrect fix, retrying a flaky test 20 times. Without stopping conditions, loops run until the context window fills or the session is killed, leaving degraded context and unusable partial output.

## Stopping Signals

Five signals warrant a circuit break:

**1. Iteration limit reached.** The agent has taken N steps without completing the task. N varies by task type. Claude Code sub-agents support a `maxTurns` field ([docs](https://code.claude.com/docs/en/sub-agents)) that enforces this at the runtime level.

**2. Repeated failure.** The same tool call fails repeatedly with the same error. A 429 three times in a row will continue to 429. A test failing for a logic error will continue to fail.

**3. Repetition detected.** The agent is doing the same thing it already did — fetching the same URL, reading the same file, attempting the same fix. Repetition without new information is a stuck loop.

**4. Context budget exceeded.** The context window is approaching the zone where output quality degrades — the "dumb zone." Stopping before it is better than continuing into degraded reasoning. Chroma's [Context Rot](https://research.trychroma.com/context-rot) study tested 18 frontier models including GPT-4.1, Claude Opus 4, and Gemini 2.5, and found that every model degrades as input length grows — non-uniformly, with the onset depending on task similarity and distractor density. There is no universal percentage; monitor for the degradation pattern on your task and trip the breaker when recall or coherence drops, not at a fixed token count.

**5. Cost threshold exceeded.** The task has consumed more than the expected budget — cost overrun often correlates with loops.

## Graceful Degradation

When a circuit breaker trips, the agent should:

1. Stop executing new actions
2. Return partial results completed before the break
3. Explain what triggered the stop and what remains incomplete
4. Escalate to a human if the pipeline has a human gate

Partial results are more useful than nothing. Return what you have; do not discard completed work.

## Configuration

| Signal | Configuration | Enforcement |
|--------|-------------|-------------|
| Iteration limit | `maxTurns` in agent frontmatter | Runtime |
| Cost threshold | Session budget settings | Runtime |
| Error rate | Agent instruction + hook | Instruction / hook |
| Repetition | Agent instruction + hook | Instruction / hook |
| Context usage | Agent instruction | Instruction |

Runtime enforcement (maxTurns, cost budgets) cannot be overridden by the model. Instruction-level enforcement depends on the model following instructions — less reliable for safety-critical stops. Hooks offer a middle ground: deterministic scripts that monitor and signal a stop.

Circuit breakers are the enforcement mechanism for [context health](../context-engineering/context-window-dumb-zone.md) — without them, context management guidelines are advisory rather than operational limits.

## Example

The following Claude Code sub-agent definition combines a runtime-enforced `maxTurns` limit with an instruction-level check for repeated failure. Both signals are present so that the agent stops whether the loop is caused by hitting the turn ceiling or by a recurring error pattern.

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

## When This Backfires

Circuit breakers are failure-mode detectors, not correctness guarantees — set too aggressively, they become the failure mode. A reasonable practitioner would push back in at least three situations:

- **Iteration limits trip on legitimate work.** Setting `maxTurns` low enough to catch pathological loops also cuts off legitimate multi-step refactors or research tasks — several production frameworks have open issues where agents halt mid-task on "stopped due to max iterations" even when making forward progress ([openai-agents-python#844](https://github.com/openai/openai-agents-python/issues/844), [langflow#10607](https://github.com/langflow-ai/langflow/issues/10607)). Raise the ceiling for task classes that legitimately need 50+ turns.
- **Repetition detection flags valid re-reads.** Re-reading the same file after an edit, or refetching a URL after a 429 backoff, are normal behaviors, not stuck loops. Naive "did we already fetch this?" heuristics fire on both.
- **Cost thresholds penalize exploration.** Exploratory research agents legitimately consume variable budgets. A hard cost cap trips on successful discovery runs as readily as on loops — the signal is cost *without progress*, not cost alone.
- **Instruction-level stops are model-dependent.** Signals 2, 3, and 5 rely on the model reading its own circuit-breaker rules and obeying them. If the model ignores the instruction mid-reasoning, the stop never fires. For safety-critical stops, prefer runtime enforcement (`maxTurns`, hooks) over instructions.

The steelman: if your agent population already fails gracefully on its own — returns partial results, detects its own thrash — adding another stopping layer mostly creates false positives. Instrument first; add breakers where instrumentation shows real loops, not prophylactically.

## Key Takeaways

- Five stopping signals: iteration limit, repeated failure, repetition, context budget, cost threshold
- `maxTurns` provides runtime-enforced iteration limits; instruction-based checks can be overridden by the model
- Graceful degradation: return partial results + failure explanation, never discard completed work

## Related

- [Agent Circuit Breaker](../agent-design/agent-circuit-breaker.md) — tool-level state machine that blocks calls to degraded external tools; complementary to loop-level breakers here
- [Loop Detection](loop-detection.md)
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../workflows/human-in-the-loop.md)
- [Idempotent Agent Operations: Safe to Retry](../agent-design/idempotent-agent-operations.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Context Window Management: The Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Agent Debugging: Diagnosing Bad Agent Output](agent-debugging.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
- [Event Sourcing for Agents: Separating Cognitive Intention](event-sourcing-for-agents.md)
