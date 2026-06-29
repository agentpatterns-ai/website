---
title: "Agent-to-Agent (A2A) Protocol for AI Agent Development"
description: "An open standard enabling agents across different frameworks to discover capabilities, delegate tasks, and exchange structured results over HTTP."
tags:
  - agent-design
  - tool-agnostic
  - standards
last_reviewed: 2026-06-28
maturity: adopted
---

# Agent-to-Agent (A2A) Protocol

> An open protocol for inter-agent communication — enabling agents built on different frameworks to discover capabilities, delegate tasks, and exchange structured results over HTTP.

## What A2A solves

MCP connects agents to tools. A2A connects agents to agents. When a client needs capabilities it does not have, A2A gives it a standard way to discover a remote agent, delegate a task, track the task lifecycle, and collect structured results. Neither agent has to share a framework, runtime, or orchestrator.

Google frames peer delegation as a way to keep each agent's working context clean: handing a task to a specialist agent [avoids polluting the delegating agent's context and preserves data privacy](https://developers.googleblog.com/en/how-a2a-is-building-a-world-of-collaborative-agents/), because the remote agent sees only the task it was given rather than the caller's full state. The same Google write-up surveys cross-domain use cases — spanning enterprise workflow automation and multi-vendor agent teams — to argue the standard is not tied to any one application.

Google [introduced A2A in April 2025](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) with 50+ partners including Atlassian, Salesforce, SAP, LangChain, and ServiceNow, and released the specification as open source.

## Core concepts

### Agent Cards

An [Agent Card](https://a2a-protocol.org/latest/specification/) is a JSON metadata document that advertises an agent's identity, capabilities, skills, endpoint, and auth requirements. Clients read the card to decide whether a remote agent can handle a task.

Agent Cards declare:

- Skills: functional capabilities with descriptions
- Security schemes: API keys, OAuth2, mutual TLS, OpenID Connect
- Capabilities: boolean flags for streaming, push notifications, and extended cards
- Interfaces: supported protocol bindings (JSON-RPC, gRPC, HTTP/REST)

Optional cryptographic signing lets clients verify a card.

### Task lifecycle

Every A2A interaction produces a [Task](https://a2a-protocol.org/latest/specification/) — a stateful object that progresses through defined states:

| State | Meaning |
|-------|---------|
| `working` | Agent is processing |
| `input-required` | Agent needs more information from the client |
| `auth-required` | Agent needs authentication credentials |
| `completed` | Task finished successfully |
| `failed` | Task finished with an error |
| `canceled` | Task was canceled by the client |
| `rejected` | Agent declined the task |

This state machine gives client agents deterministic handling logic for every outcome.

### Messages, parts, and artifacts

Communication uses messages with a role (`user` or `agent`) and a collection of parts, the atomic content units. Parts support text, file references, structured data, and forms, so agents can negotiate content types and exchange rich media.

Completed tasks produce artifacts: structured output composed of parts. Artifacts are the deliverables, such as generated code, analysis results, and transformed data.

## Update delivery

A2A supports three [update delivery patterns](https://a2a-protocol.org/latest/specification/):

- Polling: the client calls `GetTask` periodically. Simple, with higher latency.
- Streaming: real-time event delivery over persistent connections using `SendStreamingMessage`. Requires `capabilities.streaming: true` in the Agent Card.
- Push notifications (webhooks): the server sends an HTTP POST to client-registered endpoints. Requires `capabilities.pushNotifications: true`.

## A2A vs MCP vs direct orchestration

| Dimension | MCP | A2A | Direct Orchestration |
|-----------|-----|-----|---------------------|
| Connects | Agents to tools | Agents to agents | Agents to agents |
| Discovery | Server manifest | Agent Cards | Hardcoded |
| State model | Stateless calls | Stateful task lifecycle | Framework-specific |
| Cross-vendor | Yes | Yes | No |
| When to use | Adding tool capabilities | Delegating to autonomous agents | Tightly coupled agent systems |

Use A2A to delegate across organizational or framework boundaries, MCP to call tools, and direct orchestration when all agents share a framework.

The framework-agnostic claim holds end-to-end across runtimes, not just on paper: Google published a [worked example wiring a Python agent and a Go agent into one team over A2A](https://developers.googleblog.com/en/build-cross-language-multi-agent-team-with-google-agent-development-kit-and-a2a/), with each language's agent exposing an Agent Card the other consumes over HTTP — a concrete heterogeneous-runtime demonstration of agents collaborating without a shared stack.

## Protocol foundation

A2A runs over [HTTP, SSE, and JSON-RPC](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/). Core operations include `SendMessage`, `GetTask`, `ListTasks`, `CancelTask`, and `SubscribeToTask`. [`A2A-` prefixed HTTP headers](https://a2a-protocol.org/latest/specification/) carry version negotiation and extension declarations.

The protocol is asynchronous-first: operations return immediately while processing continues. A `blocking` parameter on `SendMessage` covers simple request-response flows.

## Example

This example shows a minimal A2A exchange. A client agent reads a remote agent's Agent Card, sends a task, and polls until completion.

Agent Card, served at `https://data-agent.example.com/.well-known/agent.json`:

```json
{
  "name": "data-analysis-agent",
  "description": "Performs statistical analysis and generates reports from CSV data.",
  "url": "https://data-agent.example.com",
  "skills": [
    {
      "id": "analyze-csv",
      "name": "Analyze CSV",
      "description": "Accepts a CSV file URL, returns a summary statistics report."
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "securitySchemes": {
    "apiKey": { "type": "apiKey", "in": "header", "name": "X-API-Key" }
  }
}
```

Client agent — sends a task and polls for completion:

```python
import httpx, time

BASE = "https://data-agent.example.com"
HEADERS = {"X-API-Key": "sk-data-agent-key", "Content-Type": "application/json"}

# Send the task
resp = httpx.post(f"{BASE}/tasks/send", headers=HEADERS, json={
    "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Analyze https://data.example.com/sales_q4.csv"}]
    }
})
task_id = resp.json()["id"]

# Poll until terminal state
while True:
    task = httpx.get(f"{BASE}/tasks/{task_id}", headers=HEADERS).json()
    if task["status"]["state"] in ("completed", "failed", "canceled", "rejected"):
        break
    time.sleep(2)

# Extract artifact from completed task
if task["status"]["state"] == "completed":
    report = task["artifacts"][0]["parts"][0]["text"]
    print(report)
```

The client handles each terminal state explicitly, giving deterministic error handling whatever the remote agent produces.

## When this backfires

A2A is the wrong choice in three common situations:

- Tightly coupled single-framework systems: when agents share a runtime and memory, HTTP overhead and task-lifecycle complexity add latency and code over native framework calls. Direct orchestration is cheaper.
- Simple tool access: A2A wraps tool semantics in a full agent boundary. For a function call rather than an autonomous agent, use MCP.
- High-frequency or low-latency paths: every A2A operation carries HTTP overhead, which is too costly for control loops, real-time collaboration, or sub-second decision cycles.

A2A also pushes security enforcement to each agent implementation. The protocol does not centrally audit what agents expose or access, so you must handle cross-agent access control externally with RBAC or a gateway.

Practitioners have flagged a further constraint at scale. Because A2A uses direct HTTP connections between peers, large agent meshes incur [O(n²) connectivity overhead](https://www.hivemq.com/blog/a2a-enterprise-scale-agentic-ai-collaboration-part-1/) — each new agent adds configuration, authentication, and monitoring against every existing peer. For large deployments, this has prompted teams to layer A2A on top of an [event mesh or publish/subscribe backbone](https://solace.com/blog/why-googles-agent2agent-needs-an-event-mesh/) rather than rely on point-to-point calls alone.

## Key Takeaways

- A2A standardizes agent-to-agent communication the way MCP standardizes agent-to-tool communication.
- Agent Cards provide machine-readable capability discovery — agents find and evaluate each other without human configuration.
- The task lifecycle state machine (`working` / `input-required` / `completed` / `failed`) gives client agents deterministic handling for every outcome.
- A2A and MCP are complementary, not competing — a system can use both simultaneously.
- Use A2A for cross-framework agent delegation; use direct orchestration for tightly coupled single-framework systems.

## Related

- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent Composition Patterns](../agent-design/agent-composition-patterns.md)
- [Orchestrator-Worker Pattern](../multi-agent/orchestrator-worker.md)
