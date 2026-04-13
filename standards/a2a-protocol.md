---
title: "Agent-to-Agent (A2A) Protocol for AI Agent Development"
description: "An open standard enabling agents across different frameworks to discover capabilities, delegate tasks, and exchange structured results over HTTP."
tags:
  - agent-design
---

# Agent-to-Agent (A2A) Protocol

> An open standard for inter-agent communication — enabling agents built on different frameworks to discover capabilities, delegate tasks, and exchange structured results over HTTP.

## What A2A Solves

MCP connects agents to tools. A2A connects agents to agents. When a client agent needs capabilities it does not have, A2A provides a standard way to discover a remote agent, delegate a task, track its lifecycle, and collect structured results — without requiring both agents to share a framework, runtime, or orchestrator.

Google [introduced A2A in April 2025](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) with 50+ technology partners including Atlassian, Salesforce, SAP, LangChain, and ServiceNow. A2A was [released as open source on GitHub](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/).

## Core Concepts

### Agent Cards

An [Agent Card](https://a2a-protocol.org/latest/specification/) is a JSON metadata document that advertises an agent's identity, capabilities, skills, endpoint, and authentication requirements. Client agents read the card to determine whether a remote agent can handle a given task.

Agent Cards declare:

- **Skills**: Functional capabilities with descriptions
- **Security schemes**: API keys, OAuth2, mutual TLS, OpenID Connect
- **Capabilities**: Boolean flags for streaming, push notifications, extended cards
- **Interfaces**: Supported protocol bindings (JSON-RPC, gRPC, HTTP/REST)

Optional cryptographic signing enables card verification.

### Task Lifecycle

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

### Messages, Parts, and Artifacts

Communication uses **messages** with a role (`user` or `agent`) and a collection of **parts** — the atomic content units. Parts support text, file references, structured data, and forms. This enables agents to negotiate content types and exchange rich media.

Completed tasks produce **artifacts** — structured output composed of parts. Artifacts are the deliverables: generated code, analysis results, transformed data.

## Update Delivery

A2A supports three [update delivery patterns](https://a2a-protocol.org/latest/specification/):

- **Polling**: Client calls `GetTask` periodically. Simple, higher latency.
- **Streaming**: Real-time event delivery via persistent connections using `SendStreamingMessage`. Requires `capabilities.streaming: true` in the Agent Card.
- **Push notifications (webhooks)**: Server sends HTTP POST to client-registered endpoints. Requires `capabilities.pushNotifications: true`.

## A2A vs MCP vs Direct Orchestration

| Dimension | MCP | A2A | Direct Orchestration |
|-----------|-----|-----|---------------------|
| Connects | Agents to tools | Agents to agents | Agents to agents |
| Discovery | Server manifest | Agent Cards | Hardcoded |
| State model | Stateless calls | Stateful task lifecycle | Framework-specific |
| Cross-vendor | Yes | Yes | No |
| When to use | Adding tool capabilities | Delegating to autonomous agents | Tightly coupled agent systems |

Use A2A when agents need to delegate to autonomous agents across organizational or framework boundaries. Use MCP when agents need to call tools. Use direct orchestration when all agents share a framework and tight coupling is acceptable.

## Protocol Foundation

A2A is built on [HTTP, SSE, and JSON-RPC](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/). Core operations include `SendMessage`, `GetTask`, `ListTasks`, `CancelTask`, and `SubscribeToTask`. Service parameters use [`A2A-` prefixed HTTP headers](https://a2a-protocol.org/latest/specification/) for version negotiation and extension declaration.

The protocol is asynchronous-first: operations return immediately while background processing continues. `SendMessage` supports a `blocking` parameter for simple request-response flows.

## Example

The following shows a minimal A2A exchange: a client agent reads a remote agent's Agent Card, sends a task, and polls until completion.

**Agent Card** (served at `https://data-agent.example.com/.well-known/agent.json`):

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

**Client agent** — sends a task and polls for completion:

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

The client agent handles each terminal state explicitly — `completed`, `failed`, `canceled`, `rejected` — providing deterministic error handling regardless of what the remote agent produces.

## When This Backfires

A2A is the wrong choice in three common situations:

- **Tightly coupled single-framework systems**: If all agents share a runtime, framework, and memory space, the HTTP round-trip overhead and task-lifecycle complexity of A2A add latency and code surface with no benefit over native framework calls. Direct orchestration is cheaper.
- **Simple tool access**: A2A wraps tool-call semantics in a full agent boundary. When you need a function call — not an autonomous agent — use MCP. Adding A2A just to call a deterministic function creates unnecessary infrastructure.
- **High-frequency or low-latency paths**: Every A2A operation carries HTTP overhead. Polling adds one request per tick; streaming holds a persistent connection. For control loops, real-time collaboration, or sub-second decision cycles, this latency is prohibitive.

A2A also pushes security enforcement to each agent implementation: the protocol does not centrally audit what agents expose or access, so cross-agent access control must be handled externally via RBAC or a gateway.

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
