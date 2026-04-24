---
title: "OAuth Client ID Metadata Documents (CIMD) for MCP Servers"
description: "CIMD replaces static OAuth client pre-registration with a URL that dereferences to a JSON metadata document — the registration mechanism MCP recommends for cloud-hosted servers."
tags:
  - agent-design
  - security
  - tool-agnostic
aliases:
  - Client ID Metadata Documents
  - OAuth CIMD
---

# OAuth Client ID Metadata Documents (CIMD) for MCP Servers

> CIMD makes an OAuth `client_id` a URL that dereferences to a JSON metadata document — so any MCP client can authenticate to any MCP-exposing auth server without a prior registration step.

## The M×N Registration Problem

Production MCP servers exposing databases, APIs, and infrastructure use OAuth to mediate access ([Anthropic: Building agents that reach production systems with MCP](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)). Traditional OAuth requires each client to register with each authorization server, either manually or through Dynamic Client Registration (DCR, [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)). As the MCP ecosystem grows, DCR puts every AS in the business of persisting, lifecycling, and invalidating an unbounded registry of clients it may never see again ([MCP blog: Evolving OAuth Client Registration](https://blog.modelcontextprotocol.io/posts/client_registration/)).

CIMD ([draft-ietf-oauth-client-id-metadata-document-00](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html), October 2025) removes the registration step. The client publishes a JSON metadata document once at a stable HTTPS URL; the AS dereferences that URL on demand. Nothing persists on the AS side.

## Document Structure

The `client_id` is a URL that MUST use HTTPS, contain a path, and have no fragment, username, or password. The document it resolves to is a JSON object using fields from the [IANA OAuth client metadata registry](https://www.iana.org/assignments/oauth-parameters/oauth-parameters.xhtml#client-metadata):

```json
{
  "client_id": "https://client.example.com/oauth/client.json",
  "client_name": "Example MCP Client",
  "redirect_uris": ["https://client.example.com/oauth/callback"],
  "token_endpoint_auth_method": "private_key_jwt",
  "jwks_uri": "https://client.example.com/jwks.json",
  "grant_types": ["authorization_code", "refresh_token"]
}
```

The `client_id` field MUST match the document URL exactly. Shared-secret auth methods (`client_secret_basic`, `client_secret_post`, `client_secret_jwt`) are forbidden — there is no shared secret to bootstrap. Confidential clients authenticate with `private_key_jwt` against the `jwks_uri` published in the document ([§4.1, §6.2](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html)).

## How MCP Uses CIMD

The [MCP 2025-11-25 authorization spec](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) makes MCP servers OAuth 2.1 resource servers and requires them to implement [RFC 9728 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728). MCP clients and authorization servers SHOULD support CIMD, and the client-registration priority order is:

1. Pre-registered client info if available
2. CIMD if the AS advertises `client_id_metadata_document_supported: true` in its RFC 8414 metadata
3. DCR as fallback
4. Manual `client_id` entry

Anthropic recommends CIMD as the default for new MCP server implementations and has shipped it in MCP SDKs, Claude.ai, and Claude Code ([Claude blog](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp)). [Claude Managed Agents Vaults](https://platform.claude.com/docs/en/managed-agents/vaults) persist the issued OAuth tokens per-user and inject them into each MCP connection.

## Trust Model and Limits

CIMD anchors client identity to DNS and TLS: whoever controls the domain controls the `client_id`. That is a smaller leap than it sounds — the AS already trusts DNS+TLS for HTTPS itself — but it shifts threats:

- **Domain control is not trustworthiness.** CIMD proves the app controls its hosting origin; it does not prove the app is safe. Authorization servers still need domain reputation checks, allowlists, and unknown-domain warnings ([MCP Authorization spec §Client ID Metadata Document Security](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)).
- **Localhost impersonation is unsolved.** A malicious app on `http://localhost` can impersonate a legitimate desktop client using the same redirect. The MCP working group is layering [Software Statements (RFC 7591 §2.3)](https://datatracker.ietf.org/doc/html/rfc7591) on top of CIMD for non-web clients ([MCP blog: Evolving OAuth Client Registration](https://blog.modelcontextprotocol.io/posts/client_registration/)).
- **SSRF is introduced.** The AS must now make outbound HTTPS fetches at auth time. The IETF draft requires blocking private/loopback addresses and caps response size at 5 KB ([§6.5, §6.6](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html)).
- **Metadata hosting becomes an auth dependency.** If the metadata document is unreachable, the AS SHOULD abort the authorization request (§4.3). DCR-registered clients are not affected by their own infra outages.
- **Key rotation is observable.** If the `jwks_uri` or its contents change between fetches, the AS MAY revoke tokens or consent (§6.3). Caches should respect [RFC 9111](https://datatracker.ietf.org/doc/html/rfc9111) and MUST NOT cache error responses.

## When to Choose CIMD

| Situation | Use |
|-----------|-----|
| Unbounded MCP client/server mesh, cloud-hosted | CIMD |
| Small set of internal MCP servers, controlled AS | Pre-registration or DCR + allowlist |
| Desktop/mobile clients needing impersonation resistance | CIMD + Software Statement |
| Air-gapped AS or no outbound HTTPS | Pre-registration (CIMD requires fetches) |
| Short-lived ephemeral clients (CI runners, per-PR agents) | Pre-registration (CIMD needs stable URLs) |

## Example

A real MCP server interop bug demonstrates CIMD's sharp edges in production: [anthropics/claude-code issue #37747](https://github.com/anthropics/claude-code/issues/37747) reported authorization failures against a CIMD-supporting provider because the client's metadata document listed `redirect_uris` without the port number, and the AS rejected the non-exact match. The IETF draft requires exact redirect URI matching ([§4.5](https://www.ietf.org/archive/id/draft-ietf-oauth-client-id-metadata-document-00.html), citing [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)), so any drift between the registered value and the runtime request breaks the flow. The fix is mechanical — write the exact redirect URI the client actually uses, including port — but the failure mode is silent until a user tries to authenticate.

## Key Takeaways

- CIMD replaces OAuth client pre-registration with URL dereference — the `client_id` is the metadata document URL.
- MCP's 2025-11-25 spec says clients and authorization servers SHOULD support CIMD; it is Anthropic's recommended auth for MCP servers.
- CIMD solves the operational half of client identity (no persistent registry). Trustworthiness, localhost impersonation, and desktop-client identity still need Software Statements and AS policy.
- New costs: SSRF surface, metadata-hosting availability, exact-match discipline on `redirect_uris`, and key-rotation signalling via `jwks_uri`.

## Related

- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md)
- [Agent Cards: Capability Discovery Standard](agent-cards.md)
- [MCP Server Design: A Server Author's Checklist](../tool-engineering/mcp-server-design.md)
- [MCP Client Design](../tool-engineering/mcp-client-design.md)
- [MCP Client-Server Architecture](../tool-engineering/mcp-client-server-architecture.md)
