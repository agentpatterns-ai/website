---
title: "Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot"
description: "A hostname-allowlist proxy that does not terminate TLS enforces only the client-supplied destination; broad allowlist entries on shared-CDN domains open domain-fronting and similar exfil paths."
aliases:
  - hostname allowlist TLS blind spot
  - non-TLS-terminating proxy domain fronting
  - SNI-only allowlist exfiltration
tags:
  - security
  - tool-agnostic
last_reviewed: 2026-05-30
---

# Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot

> A hostname-allowlist proxy that does not terminate TLS enforces what the client says the destination is, not what the destination actually is.

A network-egress proxy that allowlists by hostname without terminating TLS makes its decision from the client-supplied SNI (or HTTP `CONNECT` argument) before the encrypted connection is established. Once the proxy allows the connection, it forwards opaque bytes — it has no key material to read the inner HTTP `Host` header that the CDN actually routes by. Broad entries like `github.com` or `s3.amazonaws.com` then become bridges to any other tenant of the same CDN backplane, defeating the allowlist for code running inside the sandbox.

## Where the Asymmetry Lives

In a normal HTTPS request, the destination domain appears in three places: the DNS query, the TLS Server Name Indication (SNI) extension, and the HTTPS `Host` header. Ordinarily all three match ([Fifield et al., PETS 2015](http://www.icir.org/vern/papers/meek-PETS-2015.pdf)). A hostname-allowlist proxy without TLS termination can only see the first two — both are pre-encryption metadata the client supplies. The `Host` header is inside the TLS record stream.

Claude Code's sandboxed Bash proxy documents the limitation directly: *"The built-in proxy enforces the allowlist based on the requested hostname and does not terminate or inspect TLS traffic"* ([Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing#how-sandboxing-works)). The docs name the consequence in the same section: *"Allowing broad domains such as `github.com` can create paths for data exfiltration. Because the proxy makes its allow decision from the client-supplied hostname without inspecting TLS, code running inside the sandbox can potentially use [domain fronting](https://en.wikipedia.org/wiki/Domain_fronting) or similar techniques to reach hosts outside the allowlist"* ([Claude Code sandboxing docs §Security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations)).

The Agent SDK's secure-deployment guide reinforces the same gap for the standalone sandbox runtime: *"The proxy allowlists domains based on the client-supplied hostname and does not terminate or inspect encrypted traffic. Code running inside the sandbox can potentially use domain fronting or similar techniques to reach hosts outside the allowlist"* ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#sandbox-runtime)).

## Why It Works

The proxy and the CDN see different hostnames and route from different sources of truth. Domain fronting exploits the gap directly: SNI says `allowed.com` and passes the proxy, inner `Host` says `attacker-tenant.allowed.com` (or a sibling tenant on the same CDN), and the CDN routes by `Host` ([Fifield et al., PETS 2015 §2](http://www.icir.org/vern/papers/meek-PETS-2015.pdf)). MITRE catalogues this as Proxy: Domain Fronting (T1090.004) under Command and Control, with M1020 SSL/TLS Inspection as the canonical mitigation: *"If it is possible to inspect HTTPS traffic, the captures can be analyzed for connections that appear to be domain fronting"* ([MITRE ATT&CK T1090.004](https://attack.mitre.org/techniques/T1090/004/)).

The threat model that activates the gap is prompt-injection-driven exfil, not well-behaved code. The allowlist still protects against accidents — a typo'd subprocess request to a denied host fails as expected — but against an adversary inside the sandbox who can craft a request, it enforces only what that adversary wrote into the SNI field.

## Anti-Pattern Example

**Before — broad CDN entry treated as an egress boundary:**

```json
{
  "sandbox": {
    "enabled": true,
    "network": {
      "allowedDomains": [
        "github.com",
        "*.cloudfront.net",
        "s3.amazonaws.com",
        "api.anthropic.com"
      ]
    }
  }
}
```

Each broad entry covers a shared-CDN backplane: GitHub Pages and many `*.github.io` tenants ride Fastly behind `github.com`; arbitrary CloudFront customers share `*.cloudfront.net`; arbitrary AWS accounts share `s3.amazonaws.com`. A prompt-injected agent that crafts a request with `SNI=github.com, Host=attacker-tenant.example.com` (where the attacker tenant is on the same CDN) passes the proxy's hostname check, and the CDN routes the decrypted request to the attacker's origin. Domainless fronting — leaving the SNI field blank — bypasses some CDN-side mismatch checks ([MITRE ATT&CK T1090.004](https://attack.mitre.org/techniques/T1090/004/)). HTTP/2 and HTTP/3/QUIC paths weaken CDN-side enforcement further: TLS-inspection proxies cannot read the inner SNI from HTTP/3 QUIC traffic and some HTTP/2 implementations skip the mismatch check entirely ([Compass Security, March 2025](https://blog.compass-security.com/2025/03/bypassing-web-filters-part-4-host-header-spoofing-domain-fronting-detection-bypasses/)).

**After — TLS-terminating proxy plus a CA cert in the sandbox trust store:**

```json
{
  "sandbox": {
    "enabled": true,
    "network": {
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}
```

The corporate proxy runs outside the sandbox, terminates the TLS connection, inspects the decrypted `Host` header (and request body, headers, URL) against policy, re-encrypts to the actual destination with its own client cert, and returns the response over the original TLS session using a leaf cert signed by the corporate CA installed in the sandbox's trust store ([Securely deploying AI agents §Traffic forwarding](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)). The Agent SDK guide names the three requirements: *"Running the proxy outside the agent's container; Installing the proxy's CA certificate in the agent's trust store (so the agent trusts the proxy's certificates); Configuring `HTTP_PROXY`/`HTTPS_PROXY` to route traffic through the proxy"* ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)).

## When This Backfires

TLS termination is not free, and treating it as the default closes one gap by opening others.

- **Single-tenant allowlists with no broad-CDN entries.** If the allowlist contains only single-tenant origins (`api.anthropic.com`, a private registry, `pypi.org`), there is no shared CDN to front through. The teaching targets broad shared-CDN entries (`github.com`, `s3.amazonaws.com`, `*.cloudfront.net`, `*.azureedge.net`).
- **The CA private key becomes an oversized credential.** The CA installed in the sandbox trust store lets whoever operates the proxy observe `git push`, `npm install`, `gh auth`, and `aws sts` traffic in plaintext. Mismanaging that key is a worse outcome than the residual fronting risk on developer laptops where the threat model is "trusted operator, trusted repos".
- **Major CDNs already enforce SNI/Host match.** Cloudflare disabled fronting in 2015; Google and Amazon (CloudFront) in April 2018; Azure in 2021-2022; Fastly in 2024 ([Wikipedia: Domain fronting §Disabling](https://en.wikipedia.org/wiki/Domain_fronting#Disabling)). Pure fronting through `github.com` (Fastly) is harder in 2026 than the original framing suggests; the broader class — domainless fronting, HTTP/2 mismatch handling, HTTP/3 QUIC inner SNI — survives.
- **Tools that bypass the system trust store.** Go binaries hard-bake their CA bundle (`gh`, `gcloud`, `terraform`); the Agent SDK guide notes *"Node.js `fetch()` ignores these variables by default; in Node 24+ you can set `NODE_USE_ENV_PROXY=1` to enable support"* ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)). Claude Code documents the fallout: *"tools such as `gh`, `gcloud`, and `terraform` may fail TLS verification under Seatbelt. List these tools in `excludedCommands` to run them outside the sandbox"* ([Claude Code sandboxing docs §Troubleshooting](https://code.claude.com/docs/en/sandboxing#troubleshooting)). Each `excludedCommands` exception is a hole the TLS-terminating proxy never sees.
- **TLS termination is one layer, not the layer.** It closes SNI/Host mismatch but not query-string exfil to allowlisted endpoints, authenticated misuse of credentials the proxy attaches, DNS tunnelling, or covert channels in header values — vectors the [Agent Network Egress Policy](agent-network-egress-policy.md) page enumerates. Replacing one misconception ("hostname allowlist is the boundary") with another ("TLS termination is the boundary") gains little.
- **Regulated workloads that forbid plaintext access to user-bearing TLS.** Healthcare, finance, and some government regimes treat operator plaintext access to authenticated traffic as a regulatory issue. Route authenticated work through a [scoped-credentials proxy](scoped-credentials-proxy.md) or external-tool-mediation pattern that keeps credentials outside the sandbox without decrypting inside it ([Securely deploying AI agents §Custom tools](https://code.claude.com/docs/en/agent-sdk/secure-deployment#custom-tools)).

The matcher itself is also a trust boundary. Two Claude Code disclosures in 2025-2026 show the failure mode empirically — not domain fronting strictly, but the same "the allowlist enforces what the client supplied" gap. CVE-2025-66479 made `allowedDomains: []` disable the proxy entirely. A SOCKS5 hostname null-byte injection in v2.0.24-v2.1.89 defeated wildcard allowlists by exploiting an `endsWith()` check that accepted `attacker.com\x00.allowed.com` while `getaddrinfo()` truncated at the null byte ([SecurityWeek, 2026-05-20](https://www.securityweek.com/anthropic-silently-patches-claude-code-sandbox-bypass/); [Aonan Guan PoC](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)). Defence in depth needs a lower-layer enforcement point — OS netns, forward proxy at the container boundary, cloud egress gateway — that does not trust the agent process's parser.

## Audit Questions

For any sandbox that depends on a hostname-allowlist proxy as an egress boundary:

1. Does the allowlist contain any broad CDN entry (`github.com`, `s3.amazonaws.com`, `*.cloudfront.net`, `*.azureedge.net`, `*.akamaiedge.net`)?
2. Does the threat model include prompt injection from untrusted content (web fetches, MCP server outputs, user-uploaded files, processed documents)?
3. Does the proxy terminate and inspect TLS, or only decide from the client-supplied SNI?
4. If TLS termination is enabled, is the CA private key handled with the same hygiene as cloud root credentials?
5. Is the allowlist matcher pinned to a patched runtime, and is there a lower-layer enforcement point in case the matcher fails?

A "yes" to questions 1 and 2 with a "no" to question 3 puts the deployment in the gap this anti-pattern names.

## Key Takeaways

- A hostname-allowlist proxy without TLS termination enforces the client-supplied destination, not the actual destination
- Broad shared-CDN entries (`github.com`, `s3.amazonaws.com`, `*.cloudfront.net`) are the high-risk allowlist entries; single-tenant origins are not
- The fix is a TLS-terminating proxy with a CA cert in the sandbox trust store — and the CA private key becomes a credential of equal weight to the cloud keys it lets the proxy observe
- Major CDNs enforce SNI/Host match from their side, but variants (domainless fronting, HTTP/2 mismatch handling, HTTP/3 QUIC inner SNI) and matcher bugs (CVE-2025-66479, SOCKS5 null-byte) keep the broader class alive
- TLS termination is one layer; query-string exfil, redirect chains, DNS tunnelling, and authenticated misuse still bypass it — pair with [Agent Network Egress Policy](agent-network-egress-policy.md), [URL Exfiltration Guard](url-exfiltration-guard.md), and lower-layer enforcement

## Related

- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
