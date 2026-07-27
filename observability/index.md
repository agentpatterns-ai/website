---
title: "Observability for AI Agents: Tracing and Debugging"
description: "Tracing, debugging, loop detection, circuit breakers, and logging patterns for understanding what agents are doing and diagnosing failures."
tags:
  - observability
  - index
last_reviewed: 2026-05-27
---

# Observability

> Tracing, debugging, loop detection, and logging patterns for understanding agent behavior.

## Pages

- [Agent Debug Log Panel: Chronological Event Inspection for Session Debugging](agent-debug-log-panel.md) — A persistent, chronological event-log surface separate from the user-facing transcript — lets operators replay and debug past agent sessions from the same events the agent saw
- [Agent Debugging](agent-debugging.md) — A systematic process for tracing why an agent produced wrong, incomplete, or unexpected output
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md) — OpenTelemetry metrics, trajectory tracing, and structured audit trails for cost attribution, compliance, and debugging that survives context resets
- [Agent-Reactive Bugs at the Model-Harness Boundary](agent-reactive-bugs.md) — A failure class that surfaces only when a specific model output meets harness code that mishandles it — diagnosed from paired model-output and harness-reaction traces, not from either side alone
- [Centralized LLM Gateway for Per-Dimension Agent Budgets](llm-gateway-per-dimension-budgets.md) — Route every coding-agent model call through one proxy that enforces spend caps by organization, workspace, user, and API key across hourly-to-monthly windows, wired to traces
- [Context-Usage Attribution: Per-Source Breakdown of Agent Context](context-usage-attribution.md) — An always-on observability surface that breaks the context window into rules, skills, MCP returns, subagent transcripts, and conversation history — so operators prune the right source instead of guessing
- [Cost-Aware Tracing for Skill Distillation](cost-aware-tracing-skill-distillation.md) — Per-step USD cost paired with redundancy flags lets a distillation pipeline distinguish necessary steps from incidental ones — prune patches transfer; preserve patches do not
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — Stop agents automatically when progress stalls — repeated errors, escalating costs, context exhaustion, or circular behavior signal a halt
- [Event-Loop Contention in Async Agent Fan-Out](event-loop-contention-async-fan-out.md) — Adding concurrent agents raises end-to-end latency when per-response CPU work serializes on one event loop — how to tell it apart from provider throttling and connection-pool exhaustion
- [Event Sourcing for Agents](event-sourcing-for-agents.md) — Agents emit structured intentions in validated JSON; a deterministic orchestrator validates, persists, and applies effects for replay-verifiable execution
- [Failure-Aware Observability for Multi-Agent LLM Systems](failure-aware-observability-multi-agent.md) — A six-signal trace taxonomy — tool reliability, execution recovery, orchestration loops, evidence availability, information change, budget pressure — that maps recurring multi-agent failure modes to online observability so wasted runs are caught mid-trajectory
- [Harness Bug Detection Patterns](harness-bug-postmortem-patterns.md) — Three detection gaps — idle-state evals, internal-vs-public build parity, per-model ablation — drawn from Anthropic's April 2026 Claude Code postmortem
- [Harness Preflight Doctor Command for Agent Diagnostics](harness-preflight-doctor-command.md) — A dedicated doctor command validates a harness's auth, MCP reachability, config, tools, and version drift in one deterministic preflight pass before the agent starts work
- [Loop Detection](loop-detection.md) — Track repeated file edits within a session and signal the agent to try a different approach when it enters an unproductive cycle
- [Making Observability Legible to Agents](observability-legible-to-agents.md) — Wire browser automation, application metrics, and structured logs into agent context so agents can reason about system behavior from real signals
- [Observability Feedback Loop: A 7-Step Debug Runbook](observability-feedback-loop.md) — A named runbook — query, correlate, reason, implement, restart, rerun, verify — that closes the loop on agent debugging by tying the verification predicate to the originating signal
- [Prebuilt Agent Monitoring Dashboard](prebuilt-agent-monitoring-dashboard.md) — Ship a templated Grafana view with the agent stack to close the OTel-emitter-to-consumer gap — under the conditions of a shared backend, stable model class, and verified emitter
- [Strained Coherence as a Pre-Failure Signal in Agent Trajectories](strained-coherence-pre-failure-signal.md) — A trajectory judge flags spans where the agent acknowledges a conflict then proceeds anyway; a late-stage triage signal that works only on verbose backbones and erodes under direct optimisation pressure against the judge
- [Subagent OTel Trace Correlation via agent_id Attribute](subagent-otel-trace-correlation.md) — Propagate a stable agent identifier as both an HTTP header on outgoing API requests and an OTEL span attribute so multi-agent traces become queryable by agent identity, independent of span lineage
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md) — Capture a full, replayable audit trail of agent decisions across sessions using only a progress file, git commits, and a bootstrap script
- [Trajectory Pre-Filter for Failure Diagnosis (TrajAudit)](trajectory-prefilter-failure-diagnosis.md) — Wrap the failure-investigator LLM with a pattern-matching noise filter and a test-report-seeded preliminary diagnosis so long-context attention concentrates on failure-relevant trajectory spans
- [Traces Need Feedback to Power Learning](traces-need-feedback-to-power-learning.md) — A trace records what the agent did; only a verdict attached to it labels whether it was right — couple them at write time so the trace store doubles as an eval corpus
- [In-Session Transcript Search](transcript-search.md) — Claude Code's Ctrl+O transcript mode plus `/`, `n`, `N` turns a long session transcript into a navigable index — the in-session counterpart to offline transcript analysis
- [Visible Thinking in AI-Assisted Development](../human/visible-thinking-ai-development.md) — When AI handles production speed, meaningful commits, signal-rich PRs, and clear branch naming become the primary quality differentiators
