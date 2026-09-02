---
title: "Public Placeholder Credentials with a Fail-Closed Injecting Proxy"
term: "Public Placeholder Credentials"
description: "The sandbox holds a fixed public placeholder instead of the user's token; a TLS-terminating proxy injects the real credential per protocol and rejects any request where the placeholder appears outside an approved authentication field."
aliases:
  - public placeholder credential injection
  - fail-closed credential injecting proxy
  - placeholder outside authentication field
tags:
  - security
  - agent-design
  - tool-agnostic
last_reviewed: 2026-09-01
maturity: emerging
---

# Public Placeholder Credentials with a Fail-Closed Injecting Proxy

> A fixed, public placeholder in the sandbox lets the proxy inject the real credential and reject any request carrying that placeholder out of place.

Three conditions have to hold before this pattern is available to you. The proxy must terminate TLS, because injection and inspection both need plaintext. It must be able to parse each protocol it carries, since the injection point differs per protocol. And you must accept that it defends against credential disclosure only: the generated code still runs with the user's authority.

Where those hold, Vercel's v0 runs the design in production against Snowflake. Generated code gets "a fixed, public, 72-byte string that grants no access" written where the token would go, so standard Snowflake SDK and CLI flows work unchanged ([Vercel, 2026-08-20](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

## The firewall does the routing

"The sandbox cannot talk to Snowflake directly. When code inside it sends a request to the user's Snowflake account host, the sandbox firewall forwards that request to the v0 Snowflake proxy," and that firewall "terminates TLS with a certificate authority unique to each sandbox, which lets the proxy read and rewrite traffic" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

Identity resolves before any credential is fetched. The proxy "verifies the sandbox's OIDC token, looks up the v0 chat the sandbox belongs to, restores the user session bound to that chat, and retrieves a fresh Snowflake credential" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)). Nothing in the sandbox names which user's token it wants.

## Injection is structural, per protocol

The proxy does not search and replace. Snowflake requests "reach the proxy in three shapes, and each shape puts authentication in a different place". For SQL API calls the token goes into the `Authorization: Bearer` header, and "the body remains caller-controlled SQL and is not rewritten". For login flows the proxy "parses the JSON request body, sets the token structurally at the login token field, and serializes the body again". The third shape needs no rule, because "post-login session requests authenticate with Snowflake-managed session tokens, so the proxy has nothing to inject" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

Those session tokens do live in the sandbox, but each "belongs to a single authenticated session", and Snowflake "expires the session server-side after four hours of inactivity by default". Tearing down the sandbox "takes the token with it" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

## The rejection rules are the load-bearing half

Five conditions fail a request closed. The proxy "rejects any request where: The sandbox is not bound to a chat; No user-scoped credential can be obtained; The Snowflake account host cannot be derived; The placeholder appears outside an approved authentication field; A structured login body cannot be parsed safely" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

The fourth is what separates this from textual masking. Claude Code's sandbox proxy also swaps a placeholder for a real credential on egress, but the placeholder there is "a per-session sentinel value" and substitution on an `injectHosts` destination is unconditional. Its `maskDuplicates` option will even replace copies "found outside the matched spans" ([Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). Substituting a misplaced sentinel and rejecting a misplaced placeholder are opposite postures toward the same event.

## Why it works

The design splits the authority to see a credential from the authority to use one, and puts the split somewhere the sandboxed code cannot address, since the firewall forwards to the proxy whether the code cooperates or not ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)). Making the placeholder public is what buys the second half. A constant that grants no access cannot leak, so its presence in generated code, logs, and query results costs nothing. Because it is a known constant that belongs in exactly one field per protocol, its appearance anywhere else is deterministic evidence of misuse rather than a signal to score. That is why the proxy can afford to reject on it instead of guessing.

## When this backfires

- The agent still spends the credential. This stops the sandbox seeing the token, not using it. Every query the generated code issues carries the user's authority by design, and sandboxed execution "contains blast radius but does not prevent unauthorized actions" ([Before the Tool Call, arXiv 2603.20953v1](https://arxiv.org/abs/2603.20953v1)). Agent frameworks share the gap: an audit of LangChain/LangGraph, LlamaIndex, and the Stripe Agent Toolkit found "all three provide capability gating by default, but none provides a deterministic fail-closed per-call value authorization gate by default" ([Capability Gates Are Not Authorization, arXiv 2606.28679v1](https://arxiv.org/abs/2606.28679v1)).
- No TLS termination, no pattern. The proxy "substitutes the credential inside request contents, so it has to see them"; without `network.tlsTerminate`, "the sentinel reaches the server unchanged and authentication fails", and Claude Code "reports this misconfiguration at startup" ([Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). Interception is its own trust decision: the same capability that "lets the proxy read and rewrite traffic" gives its operator plaintext view of everything the sandbox sends ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)). A proxy that cannot terminate TLS is stuck with the [hostname-allowlist blind spot](hostname-allowlist-tls-blind-spot.md) instead.
- Signature-covering auth defeats substitution. Swapping a header cannot fix a request whose signature covers the payload. Claude Code's proxy has to re-sign SigV4 requests after substituting, and three request forms it cannot re-sign at all ([Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing#re-sign-aws-requests)).
- Coverage is per-protocol engineering. The fifth rejection rule fires when "a structured login body cannot be parsed safely", so an unparseable protocol is blocked traffic rather than degraded traffic. Every new third-party API is another integration.
- The guard has no observed true positive. In its first 15 days the proxy "attached credentials server-side for roughly 13,000 requests and recorded zero placeholder-misuse rejections" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)). That measures traffic, not detection. A guard that has never fired reads exactly like a guard that is misconfigured, and no adversarial test is reported.

## Example

Two SQL API requests leave the sandbox carrying the same public placeholder. The proxy's decision turns on where that string sits. The source describes the two positions but not the vendor's request schema, so the sketch below names only the fields the rules act on.

Injected, because the placeholder sits in the approved authentication field and nowhere else:

```
Authorization: Bearer PLACEHOLDER_72_BYTE_PUBLIC_STRING
body: caller-controlled SQL, not rewritten
```

Rejected, because the placeholder also appears in the body. This is the shape an exfiltration attempt takes when generated code is steered into echoing the credential back through a query result:

```
Authorization: Bearer PLACEHOLDER_72_BYTE_PUBLIC_STRING
body: caller-controlled SQL selecting the literal PLACEHOLDER_72_BYTE_PUBLIC_STRING
```

The second request never reaches Snowflake: "if the placeholder appears in the SQL payload, the proxy rejects the request before it reaches Snowflake and logs it as placeholder misuse". v0's first proxy did substitute blindly, and the post is explicit about what that cost: "if a query contains the placeholder as a string literal, blind replacement turns that query into one containing the real OAuth token. If the database then returns that string, the real token comes back into the sandbox as query output" ([Vercel](https://vercel.com/blog/how-v0-authenticates-to-snowflake-without-exposing-the-users-oauth-token)).

## Key Takeaways

- Publishing the placeholder is the choice that matters: a string granting no access is safe to leak and unambiguous when it turns up misplaced
- The rejection rule, not the injection, is the security control; injection on its own only relocates the secret
- Injection must be structural and per protocol, so budget one integration per third-party API rather than one proxy for all of them
- TLS termination is mandatory here, which makes the proxy operator a party to every request it carries
- A hidden credential keeps its full scope, so authorization of the call stays a separate layer

## Related

- [Sandbox Credential Masking: Authenticate Without Seeing the Secret](sandbox-credential-masking.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot](hostname-allowlist-tls-blind-spot.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md)
