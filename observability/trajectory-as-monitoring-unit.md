---
title: "Trajectory as the Monitoring Unit for Production Agents"
description: "An MLOps stack monitors one prediction at a time. When agents reach production the instrumentation keeps working and the interpretation stops, so the monitored unit moves to the trajectory."
term: "Trajectory-Level Monitoring"
tags:
  - observability
  - tool-agnostic
aliases:
  - trajectory as the monitoring unit
  - migrating model monitoring to agent monitoring
  - what MLOps monitoring misses for agents
last_reviewed: 2026-09-01
maturity: adopted
---

# Trajectory as the Monitoring Unit for Production Agents

> For multi-step agents taking real actions, failure is a property of the run, so the monitoring unit moves from prediction to trajectory.

An MLOps monitoring stack watches one prediction at a time. Amazon SageMaker Model Monitor "automatically detects data, concept, bias, and feature attribution drift in models in real-time" ([Nigenda et al., arxiv 2111.13657v3](https://arxiv.org/abs/2111.13657v3)), and each of those four is defined over a model's inputs and outputs rather than over a sequence of steps. Point that stack at an agent and every collector keeps working. What stops working is the conclusion you draw from a green dashboard.

## When this applies

The shift is worth paying for under three conditions, and it is waste below them:

- The agent runs multiple steps and calls tools, so a run has a shape a single prediction does not.
- The agent takes actions with side effects, so a wrong run costs more than a wrong answer.
- The same task runs often enough to populate a reliability metric across repeated trials.

Miss any one and the inherited stack is still the right instrument. A one-call classification endpoint has a trajectory of length one, so every trajectory metric collapses back to its per-prediction equivalent.

## What stays valid and what goes blind

Keep the collectors. Change what you read into them.

| Inherited signal | Still answers | Blind to |
|---|---|---|
| Cost per request | Budget per call | Cost compounding across a run's steps |
| Latency percentiles | Infrastructure health | A fast run that did the wrong thing |
| Error rate | Crashes and timeouts | A run where every step returned cleanly |
| Input drift | Degradation from shifting inputs | Policy change from an edited prompt or tool schema |
| Per-call accuracy | Quality of one model call | Run-to-run inconsistency on the same task |

## Why it works

Per-prediction statistics cannot be sufficient statistics for a sequence-level property. An agent's failure lives in which tools ran, in what order, and what state changed, so no aggregate computed one prediction at a time can express it.

Reliability then collapses across trials in a way an average conceals. τ-bench reports that "even state-of-the-art function calling agents (like gpt-4o) succeed on <50% of the tasks, and are quite inconsistent (pass^8 <25% in retail)" ([Yao et al., arxiv 2406.12045v1](https://arxiv.org/abs/2406.12045v1)). A per-call accuracy metric reports the first number and cannot express the second.

The run can also end wrong with every step mechanically successful. False success is "common but varies by setting": 45 to 48% of failures in single-control tau2-bench domains, 3% in dual-control telecom, and 75.8% among AppWorld self-assessing coding-agent trajectories that make an explicit status claim ([Advani, arxiv 2606.09863v1](https://arxiv.org/abs/2606.09863v1)). The spread is the point, and it is why the conditions above decide whether any of this pays. Anthropic names the path from one bad step to a divergent run: "One step failing can cause agents to explore entirely different trajectories, leading to unpredictable outcomes" ([multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).

## What to instrument instead

Attach agent spans to the collector you already run. The OpenTelemetry GenAI conventions define `gen_ai.operation.name` values including `invoke_agent`, `execute_tool`, `chat`, `plan`, and `retrieval`, so a run becomes a span tree rather than a row ([semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)). [Agent Observability with OpenTelemetry](agent-observability-otel.md) covers the wiring.

Three replacements carry the weight:

- Reliability across repeated trials rather than average accuracy, using the `pass^k` shape τ-bench defines.
- Trajectory completion measured against environment state rather than the agent's own closing message.
- A gate on actions with side effects, placed before the action commits.

## When this backfires

Capturing the trajectory does not buy detection. The obvious reader for it is an LLM judge, and judges fail: "no configuration across 5 judges, 5 prompt strategies, and full task specifications exceeds AUROC 0.65 on tau2-bench," against 0.83 for lightweight TF-IDF detectors on the same data ([Advani, arxiv 2606.09863v1](https://arxiv.org/abs/2606.09863v1)). A team that ships spans and calls the problem solved has bought storage.

Four more conditions make the move a loss:

- Low volume starves the metric. `pass^k` needs repeated independent trials of one task, and τ-bench's headline figure runs eight each. A `pass^k` over two trials is noise wearing a reliability label.
- Read-only agents have nothing to gate, which removes the highest-value replacement control.
- Harnesses that hide their steps give you a partial trajectory, which is worse than none because it renders complete.
- Spans are self-reported. AgentSight argues existing tools "observe either an agent's high-level intent (via LLM prompts) or its low-level actions (e.g., system calls), but cannot correlate these two views" ([Zheng et al., arxiv 2508.02736v2](https://arxiv.org/abs/2508.02736v2)). Verify state against the environment where the question is whether the agent did what it claims.

Every `gen_ai.*` span and attribute also still carries the Development status badge in the conventions above, so the schema you build on will move.

## Key Takeaways

- Do not retire the MLOps collectors. Retire the inference that a green dashboard means a correct run.
- Build the side-effect gate first. It is the only replacement control that prevents damage instead of reporting it after the fact.
- Measure completion against environment state. An agent's closing message is the thing most likely to be wrong.
- Budget for a detector, not just a span store, and calibrate it on your own traces before trusting it.

## Related

- [Agent Observability with OpenTelemetry](agent-observability-otel.md) — the OTel wiring and cost attribution this page attaches to
- [Failure-Aware Observability for Multi-Agent LLM Systems](failure-aware-observability-multi-agent.md) — a six-signal taxonomy for diagnosing a run mid-trajectory
- [Traces Need Feedback to Power Learning](traces-need-feedback-to-power-learning.md) — why a trace without an attached verdict cannot label itself
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — halting a run on stalled progress, cost, or repetition
- [Trajectory Logging via Progress Files and Git History](trajectory-logging-progress-files.md) — a replayable audit trail across sessions
