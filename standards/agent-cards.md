---
title: "Agent Cards: Capability Discovery Standard for AI Agents"
description: "Machine-readable JSON file at a well-known URL that advertises agent capabilities, supported protocols, and skills for programmatic multi-agent discovery."
tags:
  - agent-design
---

# Agent Cards: Capability Discovery Standard for AI Agents

> A machine-readable JSON descriptor published at a well-known URL that advertises an agent's capabilities, supported protocols, authentication requirements, and skills — enabling automated discovery without documentation or hardcoded integrations.

## What Agent Cards Solve

Orchestrators in multi-agent systems need to discover what sub-agents can do. Without a standard format, this requires reading documentation, hardcoding capability lists, or manual configuration per agent. Agent cards provide a structured capability contract — analogous to [OpenAPI specs for HTTP APIs](openapi-agent-tool-spec.md) — that a client agent can read programmatically.

The A2A protocol [formalized agent cards](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) as its discovery mechanism. The concept is useful independently of A2A: any system that needs machine-readable capability advertisements can publish an agent card.

## Publishing Location

Agent cards are hosted at a well-known path under the agent's base URL:

`{base-url}/.well-known/agent-card.json`

Clients retrieve the card via a simple HTTP GET request. This follows the [RFC 8615](https://www.rfc-editor.org/rfc/rfc8615) well-known URI convention.

## Card Structure

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

## Skills Schema

Each [skill](https://github.com/google/A2A/blob/main/docs/specification.md#agentskill) describes a specific capability the agent can perform:

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

Skills carry their own input and output modes, overriding the card-level defaults. Tags enable filtering — a client agent searching for "security" capabilities matches this skill without parsing the description.

## Capabilities Declaration

The [capabilities object](https://github.com/google/A2A/blob/main/docs/specification.md#agentcapabilities) declares protocol-level features the agent supports:

- **`streaming`**: SSE-based real-time update delivery
- **`pushNotifications`**: Webhook-based update delivery to client endpoints
- **`extendedAgentCard`**: Support for the `GetExtendedAgentCard` operation, returning richer cards after authentication

Client agents read these flags to select the appropriate communication pattern before sending any task.

## Authentication

Agent cards declare authentication requirements using two fields: `securitySchemes` defines available schemes in OpenAPI-compatible format; `security` specifies which schemes apply. Supported scheme types:

- API keys
- OAuth2 (with flow types, token URLs, scopes)
- Mutual TLS
- OpenID Connect

This allows client agents to determine authentication requirements before attempting a connection.

## Static vs Dynamic Cards

**Static cards** are fixed JSON files suitable for agents with a single capability set for all callers. Serve as a static file with standard HTTP caching.

**Dynamic cards** are generated per-request based on the caller's identity or permissions. An agent may expose different skills to different callers — an authenticated enterprise user sees internal skills that anonymous callers do not. A2A supports this through the `GetExtendedAgentCard` operation, which returns a [richer card after authentication](https://github.com/google/A2A/blob/main/docs/specification.md).

## Card Signing

Agent cards may be [digitally signed using JWS (RFC 7515)](https://github.com/google/A2A/blob/main/docs/specification.md) to verify authenticity and integrity. The card JSON is canonicalized per RFC 8785 before signing, ensuring consistent hash values regardless of property ordering.

Signing is relevant in federated environments where a client agent needs to verify that a card was published by the claimed provider, not a man-in-the-middle.

## When This Backfires

Agent cards add friction that outweighs their value in three common situations:

- **Single-consumer integrations**: When exactly one client calls one agent, a shared config file or environment variable is simpler than maintaining a published well-known URL with correct caching headers.
- **Rapidly-changing capability sets**: Static cards become stale when skills are added or removed frequently. Dynamic cards add server complexity that requires careful cache invalidation.
- **Cold-start bootstrapping**: The card solves *what* an agent can do once you know its base URL, not *how to find that URL*. Discovery registries or service meshes still require out-of-band coordination.
- **A2A schema coupling**: Card consumers written against an early A2A schema version may break when the spec evolves; the `url` → `supportedInterfaces` rename in the spec is one example of this drift.

## Key Takeaways

- Publish agent cards at `/.well-known/agent-card.json` for automated discovery by client agents.
- Skills carry structured metadata (id, tags, input/output modes) that enable programmatic capability matching.
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
