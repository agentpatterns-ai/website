---
title: "Observability for AI Agents: Tracing and Debugging"
description: "Tracing, debugging, loop detection, circuit breakers, and logging patterns for understanding what agents are doing and diagnosing failures."
tags:
  - observability
---

# Observability

> Tracing, debugging, loop detection, and logging patterns for understanding agent behavior.

## Pages

- [Agent Debug Log Panel: Chronological Event Inspection for Session Debugging](agent-debug-log-panel.md) — A persistent, chronological event-log surface separate from the user-facing transcript — lets operators replay and debug past agent sessions from the same events the agent saw
- [Agent Debugging](agent-debugging.md) — A systematic process for tracing why an agent produced wrong, incomplete, or unexpected output
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — OpenTelemetry metrics, trajectory tracing, and structured audit trails for cost attribution, compliance, and debugging that survives context resets
- [Cost-Aware Tracing for Skill Distillation](cost-aware-tracing-skill-distillation.md) — Per-step USD cost paired with redundancy flags lets a distillation pipeline distinguish necessary steps from incidental ones — prune patches transfer; preserve patches do not
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — Stop agents automatically when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior signal a halt
- [Event Sourcing for Agents](event-sourcing-for-agents.md) — Agents emit structured intentions in validated JSON; a deterministic orchestrator validates, persists, and applies effects for replay-verifiable execution
- [Harness Bug Detection Patterns](harness-bug-postmortem-patterns.md) — Three detection gaps — idle-state evals, internal-vs-public build parity, per-model ablation — drawn from Anthropic's April 2026 Claude Code postmortem
- [Loop Detection](loop-detection.md) — Track repeated file edits within a session and signal the agent to try a different approach when it enters an unproductive cycle
- [Making Observability Legible to Agents](observability-legible-to-agents.md) — Wire browser automation, application metrics, and structured logs into agent context so agents can reason about system behavior from real signals
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md) — Capture a full, replayable audit trail of agent decisions across sessions using only a progress file, git commits, and a bootstrap script
- [In-Session Transcript Search](transcript-search.md) — Claude Code's Ctrl+O transcript mode plus `/`, `n`, `N` turns a long session transcript into a navigable index — the in-session counterpart to offline transcript analysis
- [Visible Thinking in AI-Assisted Development](visible-thinking-ai-development.md) — When AI handles production speed, meaningful commits, signal-rich PRs, and clear branch naming become the primary quality differentiators
