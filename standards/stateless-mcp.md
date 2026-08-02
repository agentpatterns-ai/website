---
title: "Stateless MCP: One Request per Tool Call"
description: "The 2026-07-28 MCP revision drops the initialize handshake and Mcp-Session-Id, so a tool call is one self-describing HTTP request any server instance can answer."
tags:
  - standards
  - tool-agnostic
  - agent-design
  - mcp
term: "Stateless MCP"
aliases:
  - stateless MCP transport
  - MCP 2026-07-28 specification
last_reviewed: 2026-08-02
maturity: adopted
---

# Stateless MCP: One Request per Tool Call

> A tool call is a single self-describing HTTP request, so any MCP server instance can answer it without shared session state.

The [2026-07-28 Model Context Protocol specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) retired the `initialize`/`initialized` exchange and the `Mcp-Session-Id` header. Each request now carries its protocol version, client identity, and client capabilities in a `_meta` object, and names its operation in the `Mcp-Method` and `Mcp-Name` HTTP headers. The maintainers state the consequence directly: "any request can now land on any server instance behind a plain round-robin load balancer without needing shared storage."

The payoff is conditional. It lands when you run more than one instance, when your tool surface is small enough that context cost is not the binding constraint, and when you do not depend on the features this revision deprecated. Outside those conditions the revision is a migration bill.

## What changed on the wire

Three headers carry what the handshake used to establish. [SEP-2243](https://modelcontextprotocol.io/seps/2243-http-standardization) standardizes two of them; it treats the third as already in circulation, since "clients already include headers like `Mcp-Protocol-Version`".

- `Mcp-Method` mirrors the JSON-RPC `method`, for example `tools/call`. SEP-2243 requires it on all requests and notifications.
- `Mcp-Name` mirrors `params.name` or `params.uri` — the tool, resource, or prompt — and SEP-2243 requires it on `tools/call`, `resources/read`, and `prompts/get`.
- `MCP-Protocol-Version` names the spec revision, for example `2026-07-28`. It predates this revision; with no handshake to settle it, "each request carries an `Mcp-Protocol-Version` header" ([AgentCore Gateway](https://aws.amazon.com/blogs/machine-learning/how-agentcore-gateway-supports-the-mcp-2026-07-28-spec/)).

Because the method and target sit in headers, a gateway, rate limiter, or web application firewall routes and meters on them "instead of parsing JSON bodies" ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)). The headers duplicate fields in the body, and SEP-2243 closes the gap that would open if the two disagreed: servers that process the request body "MUST reject requests where the values specified in the headers do not match the values in the request body". Optional `Mcp-Param-*` headers, bound to tool parameters via `x-mcp-header`, "follow the same validation rules as standard headers".

Two more changes follow from dropping the session ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)). Server-initiated elicitation, sampling, and roots requests no longer need a held-open stream: under Multi Round-Trip Requests the server returns `resultType: "input_required"` and the client retries the original call with `inputResponses` attached. List responses from `tools/list`, `prompts/list`, `resources/list`, and `resources/read` now carry `ttlMs` and `cacheScope`, so clients cache tool catalogs across reconnects.

## Why it works

Removing protocol sessions deletes an affinity requirement rather than deleting work. Under the older spec the server minted an `Mcp-Session-Id` during `initialize`, so every later request from that client had to reach the instance holding that state, enforced with sticky load balancing, a shared session store, or gateway body inspection. Making each request self-describing means the request carries everything a handler needs, which is the ordinary HTTP scaling property applied to a protocol that had opted out of it ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)).

State that must persist is relocated, not removed. The maintainers' pattern is to "mint an explicit handle from a tool and have the model pass it back as an argument", which they argue "works better than session state hidden in the transport - the model can see the handle and thread it between tools" ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)).

## When this backfires

- One instance, low traffic: sticky routing costs nothing when there is nothing to be sticky about, so the migration buys no scaling and adds work.
- Context-bound agents: statelessness does not reduce tool-schema tokens. Anthropic measured a five-server setup at roughly 55,000 tokens across 58 tool definitions, and 134,000 tokens internally before optimization ([Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)). Deferred tool loading addresses that cost separately.
- Genuinely stateful tools: handles now ride in tool arguments the model must carry forward. A dropped or mangled handle turns a transport guarantee into a prompt-reliability problem.
- Servers built on deprecated features: Roots, Sampling, Logging, and the legacy HTTP+SSE transport are deprecated with a minimum twelve-month window, and Tasks moved into an extension ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)). Those servers migrate twice.
- Gateways that route on headers without enforcing them: the routing benefit assumes the server rejects header and body disagreement. Without that check, `Mcp-Name` becomes an authorization surface that need not match what the server executes.

## Migrating a running server

JSON-RPC bodies, tool and resource semantics, and the endpoint shape all stay. Four assumptions have to go:

- That an `initialize` call preceded this request. Read protocol version and client info from `_meta` on every request instead.
- That a session ID identifies the caller. Mint an explicit handle from a tool where continuity is needed.
- That capabilities were negotiated once. Clients that want them up front call `server/discover`.
- That a long-lived stream is available for server-initiated prompts. Replace it with Multi Round-Trip Requests.

Emit and validate the two routing headers on every request. The maintainers concede "there will be some migration cost, especially for developers that did depend on session identifiers" ([MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)).

## Example

The release candidate published the two shapes side by side, reproduced by [Simon Willison](https://simonwillison.net/2026/Jul/31/stateless-mcp/).

**Before** — two requests, the first only to mint a session:

```http
POST /mcp HTTP/1.1
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"initialize",
 "params":{"protocolVersion":"2025-11-25","capabilities":{},
 "clientInfo":{"name":"my-app","version":"1.0"}}}

POST /mcp HTTP/1.1
Mcp-Session-Id: 1868a90c-3a3f-4f5b
Content-Type: application/json

{"jsonrpc":"2.0","id":2,"method":"tools/call",
 "params":{"name":"search","arguments":{"q":"otters"}}}
```

**After** — one request that describes itself:

```http
POST /mcp HTTP/1.1
MCP-Protocol-Version: 2026-07-28
Mcp-Method: tools/call
Mcp-Name: search
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"search","arguments":{"q":"otters"},
 "_meta":{"io.modelcontextprotocol/clientInfo":{"name":"my-app","version":"1.0"}}}}
```

## Key Takeaways

- The 2026-07-28 revision removed the `initialize` handshake and `Mcp-Session-Id`, so a tool call is one self-describing request.
- The two headers SEP-2243 adds, `Mcp-Method` and `Mcp-Name`, let gateways route and meter without reading the body, and servers reject header and body disagreement.
- Operationally you drop the session store, the sticky routing, and a chunk of client and server code.
- Statelessness does not reduce tool-definition token cost, which is the separate reason teams reach for skills or a shell.
- Roots, Sampling, Logging, and HTTP+SSE are deprecated on a twelve-month clock, so migration is scheduled work rather than optional work.

## Related

- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
- [OAuth Client ID Metadata Documents (CIMD) for MCP Servers](oauth-client-id-metadata-documents.md)
- [Tool Calling Schema Standards for AI Agent Development](tool-calling-schema-standards.md)
- [MCP Client Design: Building Robust Host-Side Logic](../tool-engineering/mcp-client-design.md)
- [Five Design Decisions for MCP Servers and Clients](../tool-engineering/mcp-client-server-architecture.md)
