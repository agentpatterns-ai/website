---
title: "The Post-Authorization Execution Trust Gap in Remote MCP"
term: "Post-Authorization Execution Trust Gap"
description: "An OAuth grant on a remote MCP server names the client and the audience, never the workload that runs the call. Six failure modes it leaves open."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - post-authorization execution trust gap
  - attested capability leases
  - execution-time trust for MCP tool calls
last_reviewed: 2026-09-06
maturity: emerging
---

# The Post-Authorization Execution Trust Gap in Remote MCP

> An OAuth grant on a remote MCP server names the client and the audience, never the workload that runs the call.

The post-authorization execution trust gap is the interval between authorizing a remote Model Context Protocol server and executing a tool call on it, during which the provider-side workload can change without invalidating the grant. OAuth answers "whether a client or user may access a resource", but "does not establish that the concrete provider-side workload executing a later invocation is still the execution unit that the relying party intended to trust". So an endpoint stays authorized after execution shifts to a substituted workload or traverses an undeclared downstream component ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)).

Treat the gap as a checklist before an architecture. The machinery that closes it is provider-side, so a consumer of someone else's server cannot build it.

## What the grant leaves open

Six attack classes follow from the gap ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)):

| Failure mode | What it does |
|---|---|
| Credential replay or transfer | Reuses authority for another sender or invocation |
| Workload substitution | Replaces "the serving process, container, virtual machine, enclave, image, configuration, or dependency state after authorization" |
| Stale appraisal reuse | Exploits the interval between an earlier appraisal and a later execution decision |
| Invocation-boundary misuse | Consumes valid authority for a different operation, object, or parameter range |
| Undeclared delegation | Forwards execution to a downstream component outside the authorized path |
| Receipt violations | Removes or forges the execution evidence a high-impact operation requires |

The paper's abstract names four; its body enumerates six.

## Why it works

Checking at the invocation point works because the appraisal and the authority get consumed in the same operation, which leaves no window between them. Connect-time attestation records workload state once and admits every later call on that record, so an adversary occupies the interval. ACLE-MCP instead issues a short-lived, sender-constrained lease that binds the expected workload to the invocation boundary, consumed by a provider-side Execution Gate immediately before the protected handler runs ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)).

An ablation isolates the causal claim. Against 190 attacks expected to be denied, the complete design blocks 100%. Remove the freshness checks and blocking falls to 89.47%, reopening time-of-check-to-time-of-use and stale appraisal reuse. Removing downstream constraints drops it to 84.21%, and receipt validation to 78.95%. Benign-task success holds at 100% throughout, so the loss comes from missing checks, not from blocking normal work ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)).

The mode comparison matters more if you are vetting a server. Across six execution-misuse families, OAuth-only and connect-time attestation each block none, and connect-time attestation measured a higher pooled p95 than the complete design, 17.30 ms against 15.34 ms. Buying attestation once, at connect time, is the worst trade in the table.

## When this backfires

- You do not operate the server. The Execution Gate is "provider-controlled", and the appraisal reads evidence from the provider-side workload, so the scheme needs the provider to run it. A consumer of a third-party service cannot deploy it alone, whatever the lease issuer's own placement. The failure modes still make good vendor questions; the architecture does not.
- The calls carry no side effects. The complete design raises request-level pooled p95 from 12.20 ms to 15.34 ms, an increase of 25.7%, and low-risk calls "may remain on the ordinary OAuth path when both Host and Provider policies permit" ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)).
- You want that number as a budget. The measured ordering is not monotonic in work done. Two intermediate modes came in faster than OAuth-only, at 11.06 ms and 11.57 ms, while checking more ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)). Read 25.7% as an order of magnitude.
- Prompt injection is your live threat. The prototype "excludes prompt injection, incorrect Host-side planning, and compromise of the Verifier or lease issuer" ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)). A team that adopts leases and calls its MCP risk covered has moved effort off the class that fires.
- The gate becomes the entire trust root. Enforcement assumes a non-bypassable provider-side gate, and an attacker who controls that gate or all routing paths defeats the scheme ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)).

All six misuse families are author-constructed, sender proof and workload appraisal are simulated in the main harness, and the authors call the results a demonstration of "prototype-level feasibility rather than production readiness" ([Ding et al., 2026](https://arxiv.org/abs/2609.02690v1)). Invocation-time checking narrows the window without closing it. Time-of-check-to-time-of-use remains open in remote attestation, and its provably secure fix targets hybrid hardware and software architectures for low-end embedded devices ([De Oliveira Nunes et al., 2021](https://arxiv.org/abs/2005.03873v2)) — not hardware you own on someone else's cloud.

## Key Takeaways

- OAuth authorizes the endpoint. It never establishes which workload executes a later call, and the grant survives a change of that workload.
- Six failure modes name what the grant leaves open: credential replay or transfer, workload substitution, stale appraisal reuse, invocation-boundary misuse, undeclared delegation, and receipt violations.
- Connect-time attestation is the worst measured option. It blocked zero of six misuse families at a higher p95 than the full invocation-time design.
- Vet a remote MCP server against the failure modes today. Reach for the architecture only when you run the server, the calls have side effects, and 25.7% added p95 is affordable.

## Related

- [Execution-Layer Security Invariants for MCP Runtimes](mcp-execution-security-invariants.md) — eight named runtime invariants for the same execution layer, checked in code rather than assumed
- [Authorization Continuity Across Agent Mutation](authorization-continuity-across-agent-mutation.md) — the mirror case, where a grant outlives a change to the agent rather than to the provider workload
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — epoch-bound handles on the client side that reject stale replay before side effects
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — a single policy evaluation point on the consumer side of the same boundary
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) — short-lived tokens minted from a runtime's own workload identity
