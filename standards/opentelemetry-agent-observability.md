---
title: "OpenTelemetry for AI Agent Observability and Tracing"
description: "Vendor-neutral standard for tracing LLM calls, tool invocations, and sub-agent handoffs using OpenTelemetry GenAI semantic conventions."
tags:
  - agent-design
  - testing-verification
  - observability
aliases:
  - OTel for agents
  - OpenTelemetry GenAI conventions
---

# OpenTelemetry for AI Agent Observability and Tracing

> OpenTelemetry provides a vendor-neutral standard for tracing LLM calls, tool invocations, and sub-agent handoffs — making agent execution trees visible in any observability backend.

## Why OTel for Agents

OpenTelemetry instruments agent systems by attaching spans to LLM calls, tool invocations, and sub-agent handoffs — producing a trace tree that any compatible backend (Datadog, Grafana, Jaeger, etc.) can ingest and visualize. Ad-hoc logging lacks this structure: it’s fragile, non-composable, and locked to a single backend.

The OpenTelemetry GenAI SIG defines [semantic conventions for generative AI systems](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — standardized attribute names, span types, metrics, and events that make AI observability comparable across vendors.

## GenAI Semantic Conventions

The [GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) define standard span attributes for LLM interactions. Note that some early attributes have been deprecated as the conventions mature:

| Attribute | Purpose |
|-----------|---------|
| `gen_ai.system` | Provider identifier (deprecated; replaced by `gen_ai.provider.name`) |
| `gen_ai.request.model` | Model invoked |
| `gen_ai.usage.input_tokens` | Tokens consumed in the request |
| `gen_ai.usage.output_tokens` | Tokens generated in the response |
| `gen_ai.operation.name` | Operation type (`chat`, `create_agent`, `invoke_agent`) |
| `gen_ai.provider.name` | Provider name |

Provider-specific conventions exist for [Anthropic, OpenAI, AWS Bedrock, Azure AI Inference, and MCP](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

## Agent Span Types

The [agent span conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) define two primary span types:

**Create Agent** (`gen_ai.operation.name = create_agent`): Captures agent initialization with attributes for agent ID, name, description, version, and requested model.

**Invoke Agent** (`gen_ai.operation.name = invoke_agent`): Captures agent execution with conversation ID, input/output types, token usage metrics, temperature, and finish reasons.

Agent-specific attributes include `gen_ai.agent.id`, `gen_ai.agent.name`, `gen_ai.agent.description`, and `gen_ai.agent.version`.

## Trace Structure for Multi-Agent Runs

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

## Instrumentation Approaches

Frameworks instrument OTel in [two ways](https://opentelemetry.io/blog/2025/ai-agent-observability/):

**Baked-in instrumentation**: The framework emits OTel traces natively (e.g., CrewAI). Simpler adoption, but couples the framework to OTel versions.

**External instrumentation libraries**: Separate packages add OTel spans around framework calls (e.g., Traceloop, Langtrace). Decoupled maintenance, but potential fragmentation.

Both approaches produce interoperable traces via shared semantic conventions.

## What to Capture

| Signal | Value |
|--------|-------|
| Token usage per call | Cost tracking and budget enforcement |
| Latency per span | Bottleneck identification |
| Tool call inputs/outputs | Debugging incorrect tool usage |
| Error types and rates | Reliability measurement |
| Model and temperature | Reproducibility |
| Conversation/session ID | Multi-turn correlation |

Token usage and latency are the minimum viable signals. Tool I/O and model parameters add debugging depth at the cost of trace size.

## Detecting Problems from Traces

Structured traces enable automated detection of agent problems:

- **Loop patterns**: Repeated identical tool calls or LLM requests within a trace indicate stuck agents
- **Cost anomalies**: Token usage spikes per trace compared to historical baselines
- **Latency drift**: Increasing span durations within a session suggest context window pressure [unverified]
- **Error cascades**: Tool failures that propagate through sub-agent chains

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
- Trace trees make multi-agent execution visible: which agent decided what, where time was spent, and where failures occurred.
- Token usage and latency per span are the minimum viable signals for agent observability.
- Frameworks either bake in OTel instrumentation or support it through external libraries — both produce interoperable traces.
- Structured traces enable automated detection of loops, cost anomalies, and error cascades.

## Related

- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Cost-Aware Agent Design](../agent-design/cost-aware-agent-design.md)
- [Agent Transcript Analysis](../verification/agent-transcript-analysis.md)
- [Escape Hatches: Unsticking Stuck Agents](../workflows/escape-hatches.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
