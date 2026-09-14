---
title: "Treating Agent Delegation as Routing, Not Authorization"
term: "Delegation as Routing"
description: "A2A establishes identity at the transport layer, so a delegation hop drops it. An agent two hops from the user authenticates its caller and cannot tell who started the chain."
tags:
  - anti-pattern
  - security
  - multi-agent
  - tool-agnostic
  - arxiv
aliases:
  - multi-hop identity loss
  - A2A delegation identity gap
  - transport-bound agent identity
last_reviewed: 2026-09-13
maturity: emerging
---

# Treating Agent Delegation as Routing, Not Authorization

> A2A binds identity to the transport, so a delegation hop drops it and the agent two hops out cannot tell who started the chain.

## When this bites

Three conditions have to hold together before the gap is real, and most deployments fail at least one.

First, the chain runs longer than one hop. A client calling one remote agent loses nothing: the connection carrying the identity carries the task.

Second, it leaves your trust domain. Inside one, the [Transaction Tokens draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-transaction-tokens-08) already propagates "user identity, workload identity and authorization context throughout the Call Chain" as short-lived signed JWTs. That draft scopes itself to a trusted domain, which is the line an A2A delegation crosses.

Last, the mesh admits agents you did not build. A fixed roster behind mutual TLS removes the rogue-agent half, because nobody new can advertise a capability.

## Why it works (identity is a property of the connection)

The specification puts identity outside the message. A2ABreak reads it back: "The specification states that payloads do not carry user or client identity directly and that identity is established at the transport layer (spec section §7.2)." Credentials ride the connection instead, "authentication is strictly hop-by-hop", and so "each agent knows only its immediate caller's identity" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)).

Two failures follow. A malicious intermediate agent can reuse what it forwards, since the design allows "a malicious intermediary to silently harvest forwarded credentials". And no downstream agent can key a policy on the original principal, because "No delegation context token, principal identity field, or chain-of-custody primitive exists" in the protocol ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)).

Signing the Agent Card does not close this. The JWS signature "authenticates identity but does not attest capability: it confirms who published the card, not whether the advertised skills are truthful" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)). A second paper reaches it independently: agents "delegate to other agents via Agent-to-Agent (A2A), yet neither protocol verifies agent identity" ([Prakash, 2026](https://arxiv.org/abs/2603.24775v1)).

That is a scoping decision, not a bug. The specification treats "context ownership, delegation provenance, capability attestation, credential scoping, as implementation concerns rather than protocol-level invariants" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)).

## When this backfires

Turning the paper's finding list into a work queue costs more than it returns, and the design it criticizes has a case.

The analysis is specification-only. It assumes full compliance, validates against no running system, and scored "a precision of 73.3% (11 TP out of 15 non-duplicate candidates)" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)). Four candidates in fifteen did not survive a human read.

It also ships no mitigations, deferring them: "Future work should design and formally evaluate concrete protocol extensions that mitigate these vulnerabilities while preserving backward compatibility" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)).

The layering choice has a defense. A client "authenticates using the scheme declared in the AgentCard (OAuth 2.0, API keys, mTLS)" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)), so operators reuse identity machinery they already run rather than grow a second one inside an application protocol.

## Example

A user starts a task with Agent A. Agent A delegates onward, and an agent further down the chain enters `auth-required` and asks for a credential. That request travels back up.

A2ABreak walks the return path: "Agent A receives the authorization request with no information about who triggered it or on whose behalf, and forwards it to the User. The User is presented with an authorization request that appears to originate from Agent A, with no protocol-supplied means to verify the actual requester, the delegation depth, or whether the request is legitimate" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)).

The issuer is blind from the other side: "credential providers cannot make informed authorization decisions, as the original principal's identity and the delegation chain are invisible to them" ([Lotfi et al., 2026](https://arxiv.org/abs/2609.10871v1)). The user approves a request whose real destination nobody in the loop can name.

## Key Takeaways

- Count the hops before you worry. One hop loses no identity; the gap opens at the second.
- Inside one trust domain, reach for Transaction Tokens rather than waiting on the protocol.
- A signed Agent Card proves the publisher, not the capability. Verify advertised skills some other way before delegating sensitive work.
- Before acting on any single A2ABreak finding, re-derive it against your own deployment. Roughly one candidate in four did not survive expert review, and the paper leaves you to design the fix.

## Related

- [Agent-to-Agent (A2A) Protocol](../../standards/a2a-protocol.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](../../standards/agent-cards.md)
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](../../security/per-caller-identity-for-agent-tool-calls.md)
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](../../security/monotonic-capability-attenuation.md)
- [MCP Allowlist by Label, Not by Identity (serverName Trap)](mcp-allowlist-label-vs-identity.md)
