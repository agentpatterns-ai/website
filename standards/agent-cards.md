---
title: "Agent Cards: Capability Discovery Standard for AI Agents"
description: "Machine-readable JSON file at a well-known URL that advertises agent capabilities, supported protocols, and skills for programmatic multi-agent discovery."
tags:
  - agent-design
  - tool-agnostic
  - standards
  - multi-agent
last_reviewed: 2026-06-13
maturity: adopted
---

# Agent Cards: Capability Discovery Standard for AI Agents

> A machine-readable JSON descriptor at a well-known URL advertising an agent's capabilities, protocols, authentication, and skills — enabling automated discovery without docs or hardcoded integrations.

## What agent cards solve

Orchestrators in multi-agent systems need to discover what sub-agents can do. Without a standard format, discovery means reading docs, hardcoding capability lists, or keeping per-agent config. An agent card gives a client agent a structured capability contract it reads programmatically. The card works like an [OpenAPI spec for HTTP APIs](openapi-agent-tool-spec.md).

The A2A protocol [formalized agent cards](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) as its discovery mechanism. The concept works on its own too, for any system that needs machine-readable capability advertisements.

## Publishing location

Agent cards live at a well-known path under the agent's base URL:

`{base-url}/.well-known/agent-card.json`

Clients fetch the card with an HTTP GET, following the [RFC 8615 well-known URI convention](https://www.rfc-editor.org/rfc/rfc8615).

## Card structure

An [agent card](https://github.com/google/A2A/blob/main/docs/specification.md) contains these top-level fields:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Agent identifier |
| `description` | string | What the agent does |
| `supportedInterfaces` | array | Service endpoints with protocol bindings |
| `version` | string | Agent version |
| `provider` | object | Organization name and URL |
| `capabilities` | object | Feature flags (streaming, push notifications, extended cards) |
| `securitySchemes` | object | Authentication scheme definitions (OpenAPI-compatible) |
| `security` | array | Which security schemes apply to the agent |
| `defaultInputModes` | string[] | Accepted MIME types for input |
| `defaultOutputModes` | string[] | Produced MIME types for output |
| `skills` | array | Individual capability units |

## Skills schema

Each [skill](https://github.com/google/A2A/blob/main/docs/specification.md#agentskill) describes one capability the agent can perform:

```json
{
  "id": "code-review",
  "name": "Code Review",
  "description": "Reviews pull requests for bugs, style, and security issues",
  "tags": ["review", "security", "code-quality"],
  "examples": ["Review PR #42 for security issues"],
  "inputModes": ["text/plain", "application/json"],
  "outputModes": ["text/plain", "text/markdown"]
}
```

Per-skill `inputModes` and `outputModes` override the card-level defaults. Tags let a client filter: a client searching for "security" matches this skill without parsing descriptions.

## Capabilities declaration

The [capabilities object](https://github.com/google/A2A/blob/main/docs/specification.md#agentcapabilities) declares protocol-level features:

- `streaming`: real-time update delivery over SSE
- `pushNotifications`: webhook delivery to client endpoints
- `extendedAgentCard`: support for `GetExtendedAgentCard`, which returns richer cards after authentication

Clients read these flags to pick a communication pattern before they send a task.

## Authentication

Two fields declare auth. `securitySchemes` defines the available schemes in OpenAPI-compatible format, and `security` specifies which ones apply. Supported scheme types:

- API keys
- OAuth2 (flow types, token URLs, scopes)
- Mutual TLS
- OpenID Connect

Clients work out the auth requirements before they attempt a connection.

## Static vs dynamic cards

Static cards are fixed JSON files for agents with one capability set for all callers. You serve them as a static file with standard HTTP caching.

Dynamic cards are generated per request, based on caller identity or permissions. They expose different skills to different callers. For example, authenticated enterprise users see internal skills hidden from anonymous callers. A2A supports this through [`GetExtendedAgentCard`](https://github.com/google/A2A/blob/main/docs/specification.md), which returns a richer card after authentication.

## Card signing

Cards may be [signed with JWS (RFC 7515)](https://github.com/google/A2A/blob/main/docs/specification.md) for authenticity and integrity. The JSON is canonicalized per RFC 8785 before signing, which produces consistent hashes whatever the property order.

Signing matters in federated environments, where a client must verify the card came from the claimed provider rather than a man-in-the-middle.

## When this backfires

Agent cards add friction that outweighs their value in four situations:

- Single-consumer integrations: when one client calls one agent, a shared config or env var beats maintaining a well-known URL with correct caching.
- Rapidly changing capability sets: static cards go stale as [skills](agent-skills-standard.md) change, and dynamic cards add server complexity and cache-invalidation risk.
- Cold-start bootstrapping: the card tells you what an agent does once you know its base URL, not how to find that URL. Registries or service meshes still need out-of-band coordination. The [Agentic Resource Discovery](agentic-resource-discovery.md) draft spec is one proposed answer at the federated-search layer above agent cards.
- A2A schema coupling: consumers written against an early A2A version may break as the spec evolves. The `url` to `supportedInterfaces` rename is one example.

## Key Takeaways

- Publish agent cards at `/.well-known/agent-card.json` for automated discovery by client agents.
- [Skills](agent-skills-standard.md) carry structured metadata (id, tags, input/output modes) that enable programmatic capability matching.
- Capability flags (streaming, push notifications, extended cards) let clients select communication patterns before sending tasks.
- Use dynamic cards when different callers should see different skill sets based on authentication.
- Card signing (JWS) provides integrity verification for federated multi-agent environments.

## Example

A complete agent card for a code-review agent published at `https://review.example.com/.well-known/agent-card.json`:

```json
{
  "name": "CodeReviewAgent",
  "description": "Automated code review for pull requests — checks style, bugs, and security vulnerabilities",
  "version": "1.2.0",
  "provider": {
    "organization": "Acme Engineering",
    "url": "https://acme.example.com"
  },
  "supportedInterfaces": [
    {
      "url": "https://review.example.com",
      "protocolBinding": "HTTP+JSON"
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "extendedAgentCard": true
  },
  "securitySchemes": {
    "bearerAuth": {
      "type": "http",
      "scheme": "bearer"
    }
  },
  "security": [{"bearerAuth": []}],
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/markdown"],
  "skills": [
    {
      "id": "security-review",
      "name": "Security Review",
      "description": "Scans diffs for injection vulnerabilities, hardcoded secrets, and insecure dependencies",
      "tags": ["security", "vulnerabilities", "secrets"],
      "examples": ["Review PR #42 for security issues"],
      "inputModes": ["application/json"],
      "outputModes": ["text/markdown"]
    },
    {
      "id": "style-review",
      "name": "Style Review",
      "description": "Checks code against team style guide and suggests formatting fixes",
      "tags": ["style", "linting", "formatting"],
      "examples": ["Check this diff against our style guide"],
      "inputModes": ["text/plain"],
      "outputModes": ["text/plain"]
    }
  ]
}
```

An orchestrator agent discovers this card via `GET /.well-known/agent-card.json`, filters skills by the `security` tag, confirms that `streaming` is supported, and sends a review task over an SSE connection.

## Related

- [Agent-to-Agent (A2A) Protocol](a2a-protocol.md)
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [llms.txt: Making Your Project Discoverable to AI Agents](llms-txt.md)
- [AGENTS.md: A README for AI Coding Agents](agents-md.md)
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md)
