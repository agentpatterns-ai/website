---
title: "Sizing Vendor-Emitted Agent Telemetry by Signal Tier"
description: "GitHub Copilot exports OTel traces, metrics, and events. Classify each agent surface by the tier it emits before you build an alert or dashboard on it."
term: "Telemetry Signal Tier"
tags:
  - observability
  - copilot
  - agent-design
aliases:
  - signal tier sizing
  - vendor-emitted agent telemetry
  - hosted agent telemetry gap
last_reviewed: 2026-09-23
maturity: emerging
---

# Sizing Vendor-Emitted Agent Telemetry by Signal Tier

> Classify each agent surface by the signal tier its vendor emits, because the tier decides which diagnostic question the telemetry can answer.

A telemetry signal tier is the strongest shape a vendor emits for one agent surface: a joined trace, a detached trace, or counters alone. Sizing by tier means reading the vendor's signal tables surface by surface and writing down which question each tier supports, before any of it becomes a dashboard panel. Do this before you build something durable: an alert, a shared dashboard, a triage runbook. If you are switching telemetry on to look around, skip the exercise and read the traces.

The GitHub Copilot app added OpenTelemetry export through enterprise-managed settings on 22 September 2026. Administrators "Configure the `telemetry` property in your enterprise's `managed-settings.json` file to enable export and specify the endpoint that will receive the data" ([GitHub Changelog](https://github.blog/changelog/2026-09-22-opentelemetry-in-the-github-copilot-app)). The client emits the data and sends it where you point it, with "no phone-home behavior" ([VS Code documentation](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)). So you get vendor-authored instrumentation rather than a vendor-hosted feed, and it is uneven across surfaces.

## The three tiers, applied to Copilot

Copilot sends traces, metrics, and events ([GitHub Docs](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/opentelemetry)). Which of the three a surface gets is the tier.

| Tier | What you get | Copilot surface | Question it answers |
|---|---|---|---|
| Joined trace | An `invoke_agent` parent with `chat`, `execute_tool`, and `execute_hook` children, plus subagent context propagation | Foreground agent, Copilot SDK, Claude agent | Which step in this session was slow or failed |
| Detached trace | A full span tree that starts its own root and does not link back to the session that launched it | Copilot CLI terminal sessions | What happened inside this process |
| Counters only | Metrics and events, no spans | Cloud and remote agents | How many sessions started, and how many notified PR-ready |

The middle tier is a stated limit rather than an oversight. "Terminal traces appear as independent root traces under service `github-copilot` and are not linked to extension traces" ([VS Code documentation](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)). The bottom tier catches people out. That same reference documents trace structure for the Copilot SDK, the CLI, and Claude agents, and never for cloud agents. Those appear only as the counters `copilot_chat.cloud.session.count` and `copilot_chat.cloud.pr_ready.count`, plus the event `copilot_chat.cloud.session.invoke`. A trace-shaped dashboard aimed at the hosted coding agent renders empty.

One more cut runs underneath all three tiers. Prompts, responses, and tool arguments are excluded by default and need an opt-in to content capture, which the documentation warns "can include sensitive information such as code, file contents, and user prompts" ([VS Code documentation](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)).

## Why it works

Signal tier predicts diagnostic power because each projection drops specific telemetry factors, and the dropped factors are the ones causal attribution needs. TelemetrySuffBench renders agent traces through seven factor masks and reports that "Metadata, OpenTelemetry-compatible, and OpenInference-compatible views preserve 99.5% to 100% detection F1 but limit origin-step accuracy to at most 0.5%" ([Zhu and Pu, 2026](https://arxiv.org/abs/2608.07899v1)). Such a view retains "only canonical identity, tool, observation, status, and relation fields", so decision content and provenance mapping fall out of it. The ablation isolates the cause: "removing decision content reduces origin-step accuracy to zero for every model".

Copilot's default export makes that exact cut, so the default configuration is a detection-grade signal by construction and no amount of dashboard work converts it into a localization-grade one. Part of the gap survives configuration entirely. Across six vendor SDK regimes, reasoning trace is a regime-independent gap ([Solozobov, 2026](https://arxiv.org/abs/2605.12078v1)).

## When this backfires

- Content capture is off the table. In a regulated or secret-bearing codebase the opt-in stays false, so the localization tier is unreachable by policy, and a runbook ending in "open the trace and find the bad step" never pays off.
- The tiers move under you. The GenAI span conventions are marked "Status: Development", not stable ([OpenTelemetry semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)). Copilot already dual-emits a legacy `copilot_chat.*` namespace beside the canonical `github.copilot.*` one ([VS Code documentation](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)). A later release can also raise a surface's tier, so a gap analysis can outlive the product it describes.
- Volume is low. At a handful of agent sessions a week, the VS Code Agent Debug Log panel shows the same SDK hierarchy as a trace viewer and costs nothing to read.
- Detection is the whole requirement. If the question is only whether runs fail and what they cost, the default tier already reaches 99.5% to 100% detection F1 ([Zhu and Pu, 2026](https://arxiv.org/abs/2608.07899v1)) and the sizing pass buys you nothing.

## Example

An enterprise wants an alert on agent failure rate and a panel showing which tool calls fail most. The tiering pass splits that request in two.

Failure rate is available at every tier. The `error.type` attribute rides the spans, and the agent activity metrics, `copilot_chat.agent.edit_response.count` among them, track code changes across every surface including cloud agents ([VS Code documentation](https://code.visualstudio.com/docs/agents/guides/monitoring-agents)).

Failing tool calls need joined traces, through `execute_tool` spans carrying `gen_ai.tool.name`. Cloud agents contribute nothing there, so the panel gets scoped to `service.name = copilot-chat` and labeled as covering editor sessions, instead of shipping as a fleet-wide view that omits the hosted agent.

## Key Takeaways

- Read the vendor's signal tables per surface, not the feature announcement. Copilot's changelog says traces; the reference says cloud agents get counters.
- Convention-shaped telemetry is strong at detection and weak at localization, because the projection drops decision content ([Zhu and Pu, 2026](https://arxiv.org/abs/2608.07899v1)).
- Label a dashboard with the surfaces it covers. A fleet-wide claim built on joined traces excludes the hosted agent silently.
- Skip the sizing pass when you are exploring, when volume is low, or when detection is all you need.

## Related

- [Prebuilt Agent Monitoring Dashboard](prebuilt-agent-monitoring-dashboard.md) — the inverse problem, where the panel set dictates what the emitter must produce.
- [Subagent OTel Trace Correlation via `agent_id` Attribute](subagent-otel-trace-correlation.md) — recovering identity when span lineage breaks across a boundary.
- [Agent Observability with OpenTelemetry and Trajectory Logging](agent-observability-otel.md) — the self-instrumented case, where you choose the attributes.
- [Debugging the Tool-Call Loop Before Reaching for a Framework](tool-call-loop-instrumentation.md) — per-hop instrumentation when you own the loop.
