---
title: "LLM API Routers as Application-Layer Man-in-the-Middle"
term: "LLM API Router MITM"
description: "An LLM API router terminates client TLS and holds every prompt and tool call in plaintext — treat it as a privileged tier in your threat model, not as benign infrastructure."
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
aliases:
  - LLM proxy man-in-the-middle
  - LLM gateway threat model
  - malicious LLM router
last_reviewed: 2026-06-18
maturity: adopted
---

# LLM API Routers as Application-Layer Man-in-the-Middle

> An LLM API router terminates client TLS and holds every prompt and tool call in plaintext — at L7 it is a man-in-the-middle if compromised.

An LLM API router (LiteLLM, OpenRouter, Portkey, in-house proxies) terminates the client's TLS session and opens a separate upstream session per provider. By design it holds prompts, tool-call arguments, generated code, provider keys, and conversation state in plaintext — that is what a router does at the network layer ([Xie et al. 2026 §1](https://arxiv.org/abs/2606.16358)). The anti-pattern is treating the router as benign infrastructure instead of as a privileged application-layer tier in the threat model. Cost attribution, fallback routing, and per-team budgets are real needs ([Braintrust 2026](https://www.braintrust.dev/articles/best-llm-gateways-observability-2026)), but operators buy that value without modeling the single-point-of-compromise risk it introduces.

## The four attack classes

[Xie et al. (2026)](https://arxiv.org/abs/2606.16358) formalizes four attack classes against a malicious or compromised router. [Wang et al. (2026)](https://arxiv.org/abs/2604.08407) implemented all four against four public agent frameworks in their 'Mine' research router and measured how often they appear in the wild.

| Class | What the router does | Why client defenses miss it |
|---|---|---|
| AC-1 Payload injection | Rewrites outgoing tool-call arguments or response bodies — e.g., swaps `requests` for a typosquat in a generated `pip install` line, or adds a `curl attacker / sh` step | The client sees a legitimate-looking response signed by no one; per-response anomaly screening tunes against benign drift |
| AC-1.a Dependency-targeted injection | Only rewrites traffic that touches package installs, IDE rule files, or MCP manifests | Most monitoring samples request volume, not request *kind*; dependency-touching traffic is a rare slice |
| AC-1.b Conditional delivery | Fires only when audit-side signals are absent — no logger header, no tracing span, no append-only transparency log attached | Append-only logging only catches what the router chooses to log; the attack is gated to evade the log entirely |
| AC-2 Secret exfiltration | Passively captures every prompt and completion to a side channel; provider keys held by the router go with them | Encryption-in-transit is fine end-to-router; the router is the endpoint |

The paper measured this directly. All four classes succeed against unprotected baselines. Three tested client-side defenses — fail-closed policy gating, response-side anomaly screening, append-only transparency logging — are evadable by adaptive routers. The conclusion: no provider enforces cryptographic integrity between client and upstream model ([Xie et al. 2026 §2–3](https://arxiv.org/abs/2606.16358)).

## Empirical evidence

- [Wang et al. (2026)](https://arxiv.org/abs/2604.08407) tested 428 commodity routers (28 paid storefront, 400 free community). Nine actively injected malicious code; 17 touched planted AWS credentials; one drained ETH from a planted private key.
- LiteLLM, March 2026. Attackers compromised the Trivy scanner in LiteLLM's CI, exfiltrated PyPI publish tokens, and pushed `litellm==1.82.7`/`1.82.8` with a malicious `.pth` payload that auto-ran at Python startup ([Snyk](https://snyk.io/blog/poisoned-security-scanner-backdooring-litellm/); [PyPI](https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/); [Trend Micro](https://www.trendmicro.com/en_us/research/26/c/inside-litellm-supply-chain-compromise.html)). Live ~40 minutes, 119k+ downloads, exfil to `models.litellm.cloud`. AI startup Mercor confirmed ~4 TB exfiltrated through its gateway ([HeroDevs](https://www.herodevs.com/blog-posts/the-litellm-supply-chain-attack-what-happened-why-it-matters-and-what-to-do-next)).
- Routing-decision injection. Cue phrases like 'Respond quickly' reroute queries to cheaper, less safety-tuned models, bypassing filters of the intended model ([RerouteGuard](https://arxiv.org/abs/2601.21380)).

## Why it works

The router sits at L7 above TLS termination, so it sees plaintext by design — end-to-end encryption between client and upstream would defeat routing itself. The structural mitigations are narrow ([Xie et al. 2026 §3](https://arxiv.org/abs/2606.16358)):

1. Attest the router. Run the sensitive path in a TEE with client-verifiable measurement, so the client refuses to send plaintext unless the enclave hash matches. AEGIS reports a ~851-LOC enclave at ~6 ms per request. TEEs are not unconditional — [TEE.Fail](https://thehackernews.com/2025/10/new-teefail-side-channel-attack.html) extracts SGX/TDX/SEV secrets from DDR5 with sub-$1000 hardware — but they raise the bar.
2. Treat the router as the trust boundary. Every key it holds is exposed to its operator and supply chain. Rotate on a short cycle, scope per-tenant, and design for recoverable compromise.
3. Vet the supply chain. The LiteLLM chain ran Trivy → CI → PyPI token → poisoned release; every privileged dependency in the router's build is in scope ([OWASP LLM03:2025](https://genai.owasp.org/llmrisk/llm032025-supply-chain/)).

## When this backfires

The threat is not uniform. In some configurations the privileged-tier framing is over-engineered:

- No router on the path. A team calling one provider directly from one service has no router to model. Introducing one creates the surface; the anti-pattern only describes deployments that already have a router.
- Vendor-hosted with audit attestations. Hyperscaler offerings (Bedrock, Vertex), the upstream provider's own gateway, or OpenRouter-equivalents with SOC2/ISO27001 audits and contractual incident-response SLAs have a different posture than commodity self-hosted or community-sourced proxies. The 3.6%/2% malicious-router rate in [Wang et al. (2026)](https://arxiv.org/abs/2604.08407) came from Taobao/Xianyu/Shopify-storefront and free-community sources, not from vendor-operated infrastructure.
- Pure passthrough with no body parsing. A simple Anthropic-compatible header-translator that does not parse or rewrite request/response bodies has a narrower attack surface than a full request-rewriting router. AC-1 and AC-1.a require the router to parse and modify agent traffic.
- Already-mitigated supply chain. Teams pinning router releases by hash, running the gateway in a no-egress segment with cryptographic egress allowlists ([scoped credentials](../../security/scoped-credentials-proxy.md), [egress policy](../../security/agent-network-egress-policy.md)), and rotating provider keys on a short cycle have already implemented most of the mitigation. The threat model is real; the extra work to action it is small.

In each of these, the principle still holds — the router is at L7 above TLS termination — but the proportionate response is monitoring and key hygiene, not "rip out the gateway."

## Example

Before — router treated as benign infrastructure:

```yaml
# Naive enterprise LLM deployment
litellm:
  image: ghcr.io/berriai/litellm:latest        # unpinned
  env:
    OPENAI_API_KEY: <prod-key, all-models>      # broad scope
    ANTHROPIC_API_KEY: <prod-key, all-models>
    DATABASE_URL: postgres://litellm:...        # full conversation history
  networking:
    egress: any                                 # router can reach the internet
  monitoring: provider-billing-dashboard        # external API spend only
```

If the upstream image is poisoned (the LiteLLM March 2026 path), the malicious release inherits every provider key, exports the PostgreSQL store, and reaches the internet to exfiltrate. The operator's only signal is the provider billing dashboard, which arrives a day late and aggregates over tenants.

After — router modeled as a privileged tier:

```yaml
litellm:
  image: ghcr.io/berriai/litellm@sha256:<pinned>   # release pinned by digest
  env:
    OPENAI_API_KEY: <scoped-to-models-this-team-uses>
    ANTHROPIC_API_KEY: <scoped>
    DATABASE_URL: postgres://litellm:...
  networking:
    egress:                                         # explicit allowlist
      - api.openai.com
      - api.anthropic.com
      # no other destinations
  monitoring:
    - egress-flow-anomalies                         # off-allowlist traffic alerts
    - upstream-token-rotation: 24h                  # short rotation cycle
    - integrity-attestation:                        # AEGIS-style if available
        required: false
        recommended: true
```

The pinned digest blocks the unpinned-image step of the LiteLLM compromise. The egress allowlist breaks AC-2 exfiltration to attacker-controlled `models.litellm.cloud`-style endpoints. Per-team key scoping keeps blast radius bounded. None of these eliminate the L7 plaintext exposure — that is structural — but they reduce the operator-controllable surface to the parts the threat model actually concerns.

## Key Takeaways

- An LLM API router is an application-layer MITM by construction — it holds prompts, completions, tool calls, and provider keys in plaintext because it terminates the client's TLS session
- Four attack classes are formalised and measured in the wild: payload injection, dependency-targeted injection, conditional (audit-evading) delivery, and secret exfiltration ([Xie et al. 2026](https://arxiv.org/abs/2606.16358); [Wang et al. 2026](https://arxiv.org/abs/2604.08407))
- Nine of 428 measured commodity routers actively injected malicious code; 17 touched planted AWS credentials; the March 2026 LiteLLM compromise exfiltrated ~4 TB from one downstream customer ([HeroDevs](https://www.herodevs.com/blog-posts/the-litellm-supply-chain-attack-what-happened-why-it-matters-and-what-to-do-next))
- Client-side defenses tested by the AEGIS paper — fail-closed gating, response anomaly screening, append-only logging — are evadable by adaptive routers
- Proportionate response is not "stop using routers"; it is pin the release, scope provider keys per tenant, allowlist egress, rotate on a short cycle, and reach for TEE attestation when available — and admit that none of these close the L7 plaintext gap
- The pattern is acute for commodity / self-hosted / community-sourced gateways and for routers that parse and rewrite request bodies; vendor-hosted attested gateways and pure-passthrough header translators have narrower exposure

## Related

- [Lethal Trifecta Threat Model](../../security/lethal-trifecta-threat-model.md) — router compromise instantly closes the trifecta on agents whose principals look benign in isolation
- [Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot](../../security/hostname-allowlist-tls-blind-spot.md) — the network-layer sibling at the L4/L7 boundary; this page is its application-layer analogue
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — untrusted *inputs* the agent reads; this page is the complementary anti-pattern for untrusted *infrastructure* the agent's traffic transits
- [Scoped Credentials via Proxy Outside the Agent Sandbox](../../security/scoped-credentials-proxy.md) — the credential-isolation pattern the After example draws from
- [Agent Network Egress Policy](../../security/agent-network-egress-policy.md) — egress allowlisting at the gateway is the AC-2 mitigation
