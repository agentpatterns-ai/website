---
title: "MCP Client Design: Building Robust Host-Side Logic"
term: "MCP Client Design"
description: "Best practices for MCP client lifecycle management, multi-server routing, tool caching, security hardening, and observability in agent hosts."
aliases:
  - MCP host-side logic
  - MCP client implementation
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - tool-engineering
  - mcp
last_reviewed: 2026-06-13
maturity: adopted
---

# MCP Client Design: Building Robust Host-Side Logic

> MCP client design is the host-side logic that connects to MCP servers, negotiates capabilities, routes tool calls, caches descriptions, and degrades gracefully on failure.

## Host, client, server

MCP separates three participants. Each client handles one server connection with its own session state, capabilities, and transport:

| Role | Responsibility |
|------|---------------|
| Host | The AI application; creates and manages client instances |
| Client | One instance per server connection; handles protocol lifecycle |
| Server | Exposes tools, resources, and prompts over MCP |

## Connection lifecycle

Initialization is three steps ([MCP spec](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle)):

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: initialize (protocol version, capabilities)
    Server-->>Client: capabilities response
    Client->>Server: notifications/initialized
    Note over Client,Server: Session active — tool calls permitted
```

Client rules: do not batch `initialize`; send no non-ping requests before the capability response; disconnect on unsupported versions; use only negotiated features.

### Shutdown

Shutdown differs by transport:

| Transport | Shutdown sequence |
|-----------|------------------|
| stdio | Close stdin, wait for server exit, send SIGTERM, then SIGKILL |
| Streamable HTTP | Send HTTP DELETE with session ID; closing the connection also signals termination |

## Multi-server tool routing

MCP defines no collision resolution. When servers share a tool name, the host picks one of three strategies:

- Namespace by server ID. Maintain a `serverId -> tools[]` map, then route `tools/call` to the owning client.
- Priority ordering. Assign precedence so the higher-priority server wins on collision.
- User disambiguation. Ask the user, in interactive sessions only.

## Tool description caching

Two approaches cut `tools/list` latency and tokens:

- Static caching. Cache `tools/list` locally, then re-fetch on `notifications/tools/list_changed`, TTL expiry, or explicit refresh.
- Dynamic discovery. Expose a search interface so the agent fetches schemas only for matched tools at call time. Anthropic's Tool Search Tool reports about 85% token reduction against loading all definitions upfront ([advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).

## Timeout and cancellation

On timeout, send `notifications/cancelled` with the request ID, stop waiting, and log it. Progress notifications may reset the clock, so enforce a hard maximum to prevent stalling.

### Health checks

Either side can send `ping` to verify liveness. Multiple failures trigger reconnection or session reset. Keep ping frequency configurable, because aggressive pinging wastes resources.

## Streamable HTTP session management

For remote servers using Streamable HTTP:

- Servers may assign `Mcp-Session-Id` at init, and clients must include it on later requests
- On a 404 for a known session, the client must reinitialize, because the session expired or was invalidated
- SSE event IDs and `Last-Event-ID` enable resumability after disconnects, which prevents message loss

This session handling applies to spec revisions before `2026-07-28`, which removed `Mcp-Session-Id` and the handshake that minted it. See [Stateless MCP: One Request per Tool Call](../standards/stateless-mcp.md).

## Security

### Tool description integrity

A server can change descriptions after approval without re-consent — a "rug pull" attack. Two defenses help:

- Version-pin descriptions. Hash the manifest at approval, then flag any post-approval change.
- Treat descriptions as untrusted. Poisoned descriptions can steer the model to exfiltrate data or trigger unintended actions.

### Authorization

OAuth 2.1 for remote servers: PKCE with S256, [Dynamic Client Registration (RFC 7591)](https://datatracker.ietf.org/doc/html/rfc7591), and [Resource Indicators (RFC 8707)](https://datatracker.ietf.org/doc/html/rfc8707) against confused-deputy attacks.

### Defense layers

| Layer | What it protects | Implementation |
|-------|-----------------|----------------|
| Sandboxing | Host system | Container/VM isolation, network egress default-deny |
| Authorization | Server identity | OAuth 2.1, per-client consent, resource indicators |
| Tool integrity | Model reasoning | Description hashing, version pinning, change detection |
| Monitoring | Operational safety | Audit trails, behavioral baselines, anomaly detection |

### Local server hardening

Local Streamable HTTP servers must validate `Origin`, bind to localhost, and require auth. This prevents DNS rebinding.

## Observability

| Metric | Why it matters |
|--------|---------------|
| Session init success/failure rate | Flaky connections surface as tool call failures |
| `tools/list` latency | Slow discovery delays agent startup |
| `call_tool` latency (avg, p95) | Identifies slow or degraded servers |
| Error rate per tool and server | Surfaces reliability issues per integration |
| Tool registry size (token count) | Tracks context window cost of tool descriptions |

## When this backfires

Caching stales tool schemas. Static TTL caching fails against servers that push frequent updates. If a required parameter changes between refreshes, the agent issues malformed calls. Short TTLs or `notifications/tools/list_changed` cut the risk but raise `tools/list` traffic.

Tool list churn invalidates provider prompt caches. Providers key prompt caching on the tool list, so mid-session changes raise per-turn costs. Avoid designs that shift the visible tool set between turns.

The full routing stack adds overhead on single-server agents. Namespace maps (the `serverId -> tools[]` table), priority ordering, and per-server lifecycle yield no benefit with one server. Apply multi-server routing only when collision risk is real.

OAuth 2.1 PKCE assumes a capable HTTP client. CLI or embedded agents may lack the browser or system capabilities the flow expects.

## Key Takeaways

- One client per server connection — each owns its lifecycle, capabilities, and transport state.
- Cache `tools/list` and refresh on `notifications/tools/list_changed` or TTL; treat every description as untrusted.
- Namespace tool names by server ID; apply priority routing only when collisions are real.
- Pin OAuth 2.1 with PKCE S256, Dynamic Client Registration, and Resource Indicators for remote servers.
- Track init success, `tools/list` latency, per-tool error rates, and registry token count — these expose degradation before users do.

## Example

A TypeScript host with namespace routing and cached tool lists:

```typescript
interface ServerSession {
  id: string;
  client: McpClient;
  tools: Map<string, ToolDefinition>;
  lastToolsFetch: number;
}

class McpHost {
  private sessions: Map<string, ServerSession> = new Map();

  async routeToolCall(toolName: string): Promise<ServerSession> {
    // Namespace lookup: find which server owns this tool
    for (const [id, session] of this.sessions) {
      if (session.tools.has(toolName)) return session;
    }
    throw new Error(`No server provides tool: ${toolName}`);
  }

  async refreshToolsIfStale(session: ServerSession, ttlMs = 300_000) {
    if (Date.now() - session.lastToolsFetch > ttlMs) {
      const response = await session.client.listTools();
      session.tools = new Map(response.tools.map(t => [t.name, t]));
      session.lastToolsFetch = Date.now();
    }
  }
}
```

One `ServerSession` per MCP server; tool calls route through the namespace map; lists refresh only on TTL expiry or a `listChanged` notification.

## Related

- [MCP Client/Server Architecture](mcp-client-server-architecture.md)
- [MCP Server Design](mcp-server-design.md)
- [MCP: The Plumbing Behind Agent Tool Access](../standards/mcp-protocol.md)
- [MCP Elicitation: Servers Requesting Structured Input Mid-Task](mcp-elicitation.md)
- [Judging MCP Capability Readiness by Client Adoption](mcp-capability-readiness.md)
- [MCP LLM Sampling: Servers Requesting AI Inference Mid-Tool](mcp-llm-sampling.md)
- [MCP Tool Result Persistence via _meta Annotation](mcp-result-persistence-annotation.md)
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
