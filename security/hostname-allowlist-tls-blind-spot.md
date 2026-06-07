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
last_reviewed: 2026-06-03
---

# Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot

> A hostname-allowlist proxy that does not terminate TLS enforces what the client says the destination is, not what the destination actually is.

A network-egress proxy that allowlists by hostname without terminating TLS decides from the client-supplied SNI (or HTTP `CONNECT` argument), then forwards opaque bytes — it has no key material to read the inner HTTP `Host` header the CDN actually routes by. Broad entries like `github.com` or `s3.amazonaws.com` become bridges to any other tenant of the same CDN backplane, defeating the allowlist for code inside the sandbox.

## Where the Asymmetry Lives

In a normal HTTPS request the destination appears in three places — the DNS query, the TLS Server Name Indication (SNI) extension, and the HTTPS `Host` header — and ordinarily all three match ([Fifield et al., PETS 2015](http://www.icir.org/vern/papers/meek-PETS-2015.pdf)). A proxy without TLS termination sees only the first two; the `Host` header is inside the encrypted record stream.

Claude Code's sandboxed Bash proxy documents this: it *"enforces the allowlist based on the requested hostname and does not terminate or inspect TLS traffic,"* so broad domains *"can create paths for data exfiltration"* via [domain fronting](https://en.wikipedia.org/wiki/Domain_fronting) ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#security-limitations)). The Agent SDK's secure-deployment guide names the same gap for the standalone runtime ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#sandbox-runtime)).

## Why It Works

The proxy and the CDN route from different sources of truth. Domain fronting exploits the gap directly: SNI says `allowed.com` and passes the proxy, inner `Host` says `attacker-tenant.allowed.com` (a sibling tenant on the same CDN), and the CDN routes by `Host` ([Fifield et al., PETS 2015 §2](http://www.icir.org/vern/papers/meek-PETS-2015.pdf)). MITRE catalogues this as Proxy: Domain Fronting (T1090.004), with SSL/TLS Inspection (M1020) as the canonical mitigation ([MITRE ATT&CK T1090.004](https://attack.mitre.org/techniques/T1090/004/)).

The threat model is prompt-injection-driven exfil, not well-behaved code. The allowlist still catches accidents — a typo'd request to a denied host fails — but against an adversary who crafts a request inside the sandbox, it enforces only what that adversary wrote into the SNI field.

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

Each broad entry covers a shared-CDN backplane: `*.github.io` tenants ride Fastly behind `github.com`; arbitrary CloudFront and AWS customers share `*.cloudfront.net` and `s3.amazonaws.com`. An agent crafting `SNI=github.com, Host=attacker-tenant.example.com` (attacker on the same CDN) passes the hostname check, and the CDN routes the decrypted request to the attacker's origin. Domainless fronting (a blank SNI) bypasses some CDN mismatch checks, and HTTP/2 and HTTP/3/QUIC weaken enforcement further — proxies cannot read the inner SNI from QUIC, and some HTTP/2 stacks skip the mismatch check entirely ([Compass Security, March 2025](https://blog.compass-security.com/2025/03/bypassing-web-filters-part-4-host-header-spoofing-domain-fronting-detection-bypasses/)).

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

The proxy runs outside the sandbox, terminates TLS, inspects the decrypted `Host` header (and body, headers, URL) against policy, then re-encrypts to the real destination — returning the response via a leaf cert signed by the corporate CA in the sandbox's trust store. The Agent SDK guide names three requirements: run the proxy outside the container, install its CA cert in the agent's trust store, and set `HTTP_PROXY`/`HTTPS_PROXY` ([Securely deploying AI agents §Traffic forwarding](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)).

## When This Backfires

TLS termination is not free; treating it as the default closes one gap by opening others.

- **Single-tenant allowlists with no broad-CDN entries.** If the allowlist holds only single-tenant origins (`api.anthropic.com`, a private registry, `pypi.org`), there is no shared CDN to front through. The teaching targets broad entries (`github.com`, `s3.amazonaws.com`, `*.cloudfront.net`, `*.azureedge.net`).
- **The CA private key becomes an oversized credential.** The CA in the sandbox trust store lets whoever operates the proxy read `git push`, `npm install`, `gh auth`, and `aws sts` traffic in plaintext. On laptops where the threat model is "trusted operator, trusted repos," mismanaging that key is worse than the residual fronting risk.
- **Major CDNs already enforce SNI/Host match.** Cloudflare disabled fronting in 2015, Google and CloudFront in April 2018, Azure in 2021-2022, Fastly in 2024 ([Wikipedia: Domain fronting §Disabling](https://en.wikipedia.org/wiki/Domain_fronting#Disabling)). Pure fronting through `github.com` is harder in 2026 than the original framing suggests; the broader class — domainless fronting, HTTP/2 mismatch, HTTP/3 QUIC inner SNI — survives.
- **Tools that bypass the system trust store.** Go binaries hard-bake their CA bundle (`gh`, `gcloud`, `terraform`) and Node.js `fetch()` ignores proxy env vars by default ([Securely deploying AI agents](https://code.claude.com/docs/en/agent-sdk/secure-deployment#traffic-forwarding)). Claude Code's fix — listing such tools in `excludedCommands` to run outside the sandbox ([sandboxing docs §Troubleshooting](https://code.claude.com/docs/en/sandboxing#troubleshooting)) — makes each exception a hole the proxy never sees.
- **TLS termination is one layer, not the layer.** It closes SNI/Host mismatch but not query-string exfil to allowlisted endpoints, authenticated misuse of attached credentials, DNS tunnelling, or covert header channels — vectors the [Agent Network Egress Policy](agent-network-egress-policy.md) page enumerates.
- **Regulated workloads that forbid plaintext access to user-bearing TLS.** Healthcare, finance, and some government regimes treat operator plaintext access to authenticated traffic as a compliance issue. Route that work through a [scoped-credentials proxy](scoped-credentials-proxy.md) that keeps credentials outside the sandbox without decrypting inside it ([Securely deploying AI agents §Custom tools](https://code.claude.com/docs/en/agent-sdk/secure-deployment#custom-tools)).

The matcher itself is also a trust boundary. Two Claude Code disclosures in 2025-2026 show the same "allowlist enforces what the client supplied" gap empirically: CVE-2025-66479 made `allowedDomains: []` disable the proxy entirely; a SOCKS5 null-byte injection in v2.0.24-v2.1.89 defeated wildcard allowlists via an `endsWith()` check that accepted `attacker.com\x00.allowed.com` while `getaddrinfo()` truncated at the null byte ([SecurityWeek, 2026-05-20](https://www.securityweek.com/anthropic-silently-patches-claude-code-sandbox-bypass/); [Aonan Guan PoC](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)). Defence in depth needs a lower-layer enforcement point — OS netns, a forward proxy at the container boundary, a cloud egress gateway — that does not trust the agent process's parser.

## Audit Questions

For any sandbox depending on a hostname-allowlist proxy as an egress boundary:

1. Does the allowlist contain any broad CDN entry (`github.com`, `s3.amazonaws.com`, `*.cloudfront.net`, `*.azureedge.net`, `*.akamaiedge.net`)?
2. Does the threat model include prompt injection from untrusted content (web fetches, MCP outputs, uploaded or processed files)?
3. Does the proxy terminate and inspect TLS, or only decide from the client-supplied SNI?
4. If TLS termination is enabled, is the CA private key handled with the same hygiene as cloud root credentials?
5. Is the matcher pinned to a patched runtime, and is there a lower-layer enforcement point if it fails?

A "yes" to 1 and 2 with a "no" to 3 puts the deployment in the gap this anti-pattern names.

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
