---
title: "Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny"
term: "Agent Network Egress Policy"
description: "Restrict which domains agent tools can reach via harness-enforced allow and deny lists; remove the model from the network trust boundary."
aliases:
  - agent domain allowlist
  - agent firewall policy
  - harness egress policy
tags:
  - security
  - tool-agnostic
  - agent-design
last_reviewed: 2026-06-12
maturity: established
---

# Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny

> Restrict which domains agent tools can reach via harness-enforced allow and deny lists; remove the model from the network trust boundary.

Agent tools that perform network I/O — fetch, integrated browser, MCP servers, shell commands that call `curl` or `wget` — are a primary exfiltration and lateral-movement channel. An admin-controlled domain policy moves the decision out of the model and into the harness runtime: the request is rejected before it leaves the process, regardless of what the model produced.

## Why the Model Cannot Be the Trust Boundary

A successfully injected prompt can instruct an agent to fetch any URL. If the decision to connect lives in the model, injection defeats egress control. Moving the check to the harness makes isolation structural rather than probabilistic — the same reasoning that applies to [tool-access filtering](blast-radius-containment.md): the runtime filters reachable destinations before the model issues a request.

Three tools converged on the same primitive in April 2026:

- **Claude Code v2.1.113** added `sandbox.network.deniedDomains`, a denylist that overrides any `sandbox.network.allowedDomains` wildcard ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).
- **GitHub** shipped organization firewall settings for the Copilot cloud agent: a recommended allowlist plus an org-wide custom allowlist, with a knob controlling whether repo admins may add entries ([GitHub changelog](https://github.blog/changelog/2026-04-03-organization-firewall-settings-for-copilot-cloud-agent)).
- **VS Code 1.116** added three group-policy keys: `ChatAgentNetworkFilter`, `ChatAgentAllowedNetworkDomains`, `ChatAgentDeniedNetworkDomains`. With the filter enabled and both lists empty, all domains are blocked ([VS Code 1.116 release notes](https://code.visualstudio.com/updates/v1_116)).

Delivery differs — `settings.json`, organization settings, Group Policy — but the primitive is identical: runtime-enforced domain policy at the harness.

## Allow-First vs. Deny-First

| Posture | When to use | Default behavior |
|---------|-------------|------------------|
| Allow-first + default-deny | Regulated workloads (FedRAMP, EU residency), high-sensitivity data, cloud agent runners | All traffic blocked unless explicitly allowed |
| Deny-first | Interactive developer loops with broad legitimate tool use, narrow known-bad blocks | All traffic allowed unless explicitly denied |

All three tools default toward allow-first: VS Code blocks everything when the filter is on and both lists are empty, the Copilot cloud agent runs allow-first under org control, and Claude Code's `deniedDomains` layers over an allowlist wildcard so denials take precedence ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Combine both lists when the allowlist must be broad — allow `*.corp.example` while denying a known-bad subdomain within it.

## What Egress Policy Does Not Solve

Domain policy narrows reachable destinations. It does not address every exfiltration vector:

- **Query-string exfiltration to allowlisted domains.** Prompt-injected fetch of a legitimate target still encodes user data in the URL; pair with a [public-web index gate](url-exfiltration-guard.md).
- **Redirect chains.** A trusted domain that 3xx-redirects to an attacker bypasses a static allowlist unless the agent refuses redirects ([URL Exfiltration Guard](url-exfiltration-guard.md)).
- **Authenticated misuse.** The allowlist decides *whether* a request reaches a destination; a [scoped-credentials proxy](scoped-credentials-proxy.md) decides *which* credentials attach.
- **Non-harness subprocesses.** The policy only covers tools the harness mediates. A subprocess that opens a raw socket or bundles its own HTTP client bypasses the check unless the [sandbox sits below the harness](sandbox-rules-harness-tools.md) — OS-level network namespaces or a forward proxy at the container boundary.
- **Non-URL channels.** DNS tunnelling, timing side channels, and covert channels in headers to allowlisted endpoints are unconstrained.
- **Parser bugs in the allowlist check itself.** The policy is only as strong as the code that enforces it (see [The Matcher Itself Is a Trust Boundary](#the-matcher-itself-is-a-trust-boundary) below). Defence-in-depth requires a lower-layer enforcement point — OS netns, forward proxy, or cloud egress gateway — that does not trust the agent process's parser.

## The Matcher Itself Is a Trust Boundary

The check now lives in the harness, so the matcher becomes the trust boundary — one bug there bypasses every policy. In May 2026, Aonan Guan disclosed a SOCKS5 hostname null-byte injection in Claude Code: a crafted `attacker.com\0.google.com` passed the JavaScript `endsWith()` allowlist while `getaddrinfo()` truncated at the null byte and dialed the attacker. Every release from v2.0.24 through v2.1.89 was vulnerable; Anthropic silently patched in v2.1.90 with no CVE or changelog note ([The Register, 2026-05-20](https://www.theregister.com/security/2026/05/20/even-claude-agrees-hole-in-its-sandbox-was-real-and-dangerous/5243662); [Aonan Guan PoC](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)). The earlier `allowedDomains: []` regression (CVE-2025-66479) had the same character. Pin to patched runtimes, watch disclosures for the harness you depend on, and assume the matcher will fail at least once over the deployment's lifetime.

## Delivery Through Managed Settings

Domain policy is organization-level configuration, not per-user preference — deliver it through a managed-settings channel (MDM, Group Policy, admin console, or CI runner environment). For Claude Code, pair it with [`forceRemoteSettingsRefresh`](fail-closed-remote-settings-enforcement.md) so the agent refuses to start on a stale policy. The Copilot cloud agent inherits org-level policy to repos via hybrid mode ([GitHub changelog](https://github.blog/changelog/2026-04-03-organization-firewall-settings-for-copilot-cloud-agent)).

## Example

A regulated team runs Claude Code against an internal package registry and needs to block general internet access while allowing approved API hosts. The managed settings combine an allowlist for explicit destinations with a denylist that overrides accidental wildcard breadth:

```json
{
  "sandbox": {
    "network": {
      "allowedDomains": [
        "*.internal.corp.example",
        "api.anthropic.com",
        "registry.npmjs.org"
      ],
      "deniedDomains": [
        "telemetry.internal.corp.example",
        "public-mirror.internal.corp.example"
      ]
    }
  },
  "forceRemoteSettingsRefresh": true
}
```

Denies override the `*.internal.corp.example` wildcard for two known-bad subdomains ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The VS Code and Copilot equivalents use the keys and org settings described above.

## Key Takeaways

- Move egress decisions out of the model: the harness rejects connections before injection can bias them.
- Allow-first with default-deny fits regulated deployments; deny-first fits broad tool use with narrow blocks.
- Denylists must take precedence over allowlist wildcards; all three tools model this.
- Domain policy composes with — not replaces — URL exfiltration guards, credentials proxies, and managed-settings enforcement.
- Deliver the policy through MDM, Group Policy, or the tool's admin console, not per-user config.

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md)
- [Selective Network Sandbox Mode](selective-network-sandbox-mode.md)
- [MCP Runtime Control Plane](mcp-runtime-control-plane.md)
- [Docker Sandbox Adoption for Agent Workloads](docker-sbx-adoption.md)
