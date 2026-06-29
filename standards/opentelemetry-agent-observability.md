---
title: "OpenTelemetry for AI Agent Observability and Tracing"
description: "Vendor-neutral standard for tracing LLM calls, tool invocations, and sub-agent handoffs using OpenTelemetry GenAI semantic conventions."
tags:
  - agent-design
  - testing-verification
  - observability
  - tool-agnostic
  - standards
aliases:
  - OTel for agents
  - OpenTelemetry GenAI conventions
last_reviewed: 2026-06-13
maturity: established
---

# OpenTelemetry for AI Agent Observability and Tracing

> OpenTelemetry provides a vendor-neutral standard for tracing LLM calls, tool invocations, and sub-agent handoffs — making agent execution trees visible in any observability backend.

## Why OTel for agents

OpenTelemetry instruments agent systems by attaching spans to LLM calls, tool invocations, and sub-agent handoffs. This produces a trace tree that any compatible backend, such as Datadog, Grafana, or Jaeger, can ingest and visualize. Ad-hoc logging is fragile, hard to compose, and locked to a single backend.

The mechanism is semantic conventions. The [OpenTelemetry GenAI SIG](https://opentelemetry.io/docs/specs/semconv/gen-ai/) defines standard attribute names, span types, metrics, and events for AI systems. Because every instrumented framework writes to the same attribute schema, backends correlate spans across agent boundaries, frameworks, and vendors without bespoke parsing. A span’s `gen_ai.operation.name`, `gen_ai.usage.input_tokens`, and parent/child relationships encode the execution tree natively. This removes per-backend log parsers and lets you correlate multi-agent traces through shared trace context.

## GenAI semantic conventions

The [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) define standard span attributes for LLM interactions. Some early attributes are deprecated as the conventions mature:

| Attribute | Purpose |
|-----------|---------|
| `gen_ai.system` | Provider identifier (deprecated; replaced by `gen_ai.provider.name`) |
| `gen_ai.request.model` | Model invoked |
| `gen_ai.usage.input_tokens` | Tokens consumed in the request |
| `gen_ai.usage.output_tokens` | Tokens generated in the response |
| `gen_ai.operation.name` | Operation type (`chat`, `create_agent`, `invoke_agent`) |
| `gen_ai.provider.name` | Provider name |

Provider-specific conventions cover [Anthropic, OpenAI, Bedrock, Azure AI Inference, and MCP](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

## Agent span types

The [agent span conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) define two primary span types:

Create Agent (`gen_ai.operation.name = create_agent`) covers agent initialization. It carries attributes for agent ID, name, description, version, and requested model.

Invoke Agent (`gen_ai.operation.name = invoke_agent`) covers agent execution. It carries conversation ID, input and output types, token usage, temperature, and finish reasons.

Agent-specific attributes include `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.description`, and `gen_ai.agent.version`.

## Trace structure for multi-agent runs

A well-instrumented agent system produces a trace tree:

```
Root span: user request
  ├── invoke_agent: orchestrator
  │   ├── chat: LLM call (model selection, token count)
  │   ├── execute_tool: file_read (latency, output size)
  │   ├── chat: LLM call (reasoning step)
  │   └── invoke_agent: sub-agent handoff
  │       ├── chat: LLM call
  │       └── execute_tool: api_call
  └── final response
```

Each span carries timing, token counts, and error state.

## Instrumentation approaches

Frameworks instrument OTel in [two ways](https://opentelemetry.io/blog/2025/ai-agent-observability/):

Baked-in instrumentation means the framework emits OTel traces natively, for example CrewAI. Adoption is simpler, but it couples the framework to OTel versions.

External instrumentation libraries are separate packages that add OTel spans around framework calls, for example Traceloop and Langtrace. Maintenance stays decoupled, but you risk fragmentation.

Both approaches produce interoperable traces through shared semantic conventions.

## What to capture

| Signal | Value |
|--------|-------|
| Token usage per call | Cost tracking and budget enforcement |
| Latency per span | Bottleneck identification |
| Tool call inputs/outputs | Debugging incorrect tool usage |
| Error types and rates | Reliability measurement |
| Model and temperature | Reproducibility |
| Conversation/session ID | Multi-turn correlation |

Token usage and latency are the minimum viable signals. Tool input and output and model parameters add debugging depth, at the cost of larger traces.

## Detecting problems from traces

Structured traces let you detect agent problems automatically:

- Loop patterns: repeated identical tool calls or LLM requests within a trace point to stuck agents
- Cost anomalies: token usage spikes per trace against historical baselines
- Latency drift: rising span durations within a session can signal a growing prompt or slower model throughput
- Error cascades: tool failures that propagate through sub-agent chains

## When this backfires

OTel instrumentation is not cost-free:

- Telemetry volume at scale: AI workloads generate [10–50× more telemetry](https://oneuptime.com/blog/post/2026-04-01-ai-workload-observability-cost-crisis/view) than traditional services, because every LLM call produces token-level metrics, prompt and response events, and nested tool spans. Storage costs scale with trace depth, and capturing full prompt and response bodies adds more.
- PII exposure: prompts often contain user data. Forwarding raw tool inputs and LLM prompt content to observability backends [without sanitization](../security/pii-tokenization-in-agent-context.md) creates compliance risk under GDPR, HIPAA, and similar regulations.
- Setup overhead for prototypes: OTel SDK configuration, exporter setup, and collector deployment add days to weeks of effort. For experimental or short-lived agents, a lightweight structured log to stdout is faster to iterate on.
- Spec instability: GenAI semantic conventions are still stabilizing, and attribute names are already deprecated, for example `gen_ai.system` to `gen_ai.provider.name`. Baked-in instrumentation in frameworks can lag upstream spec changes.

## Example

Minimal Python example using the OTel SDK to instrument an LLM call with GenAI semantic conventions:

```python
from opentelemetry import trace
from opentelemetry.semconv.ai import SpanAttributes  # opentelemetry-semantic-conventions-ai

tracer = trace.get_tracer("my-agent")

with tracer.start_as_current_span("chat") as span:
    span.set_attribute(SpanAttributes.GEN_AI_SYSTEM, "anthropic")
    span.set_attribute(SpanAttributes.GEN_AI_REQUEST_MODEL, "claude-3-5-sonnet-20241022")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    span.set_attribute(SpanAttributes.GEN_AI_USAGE_INPUT_TOKENS, response.usage.input_tokens)
    span.set_attribute(SpanAttributes.GEN_AI_USAGE_OUTPUT_TOKENS, response.usage.output_tokens)
```

For sub-agent handoffs, wrap the child agent call in an `invoke_agent` span and propagate the trace context so the parent trace links to the child execution tree.

## Key Takeaways

- OpenTelemetry GenAI semantic conventions provide standard attribute names (`gen_ai.*`) for LLM calls, tool invocations, and agent spans.
- Trace trees make [multi-agent execution visible](../observability/agent-observability-otel.md): which agent decided what, where time was spent, and where failures occurred.
- Token usage and latency per span are the minimum viable signals for agent observability.
- Frameworks either bake in OTel instrumentation or support it through external libraries — both produce interoperable traces.
- Structured traces enable automated detection of loops, cost anomalies, and error cascades.

## Related

- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Cost-Aware Agent Design](../token-engineering/cost-aware-agent-design.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [Escape Hatches: Unsticking Stuck Agents](../workflows/escape-hatches.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
