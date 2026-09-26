---
title: "Route Agent Peers by Enrolled Identity, Not Card Name"
term: "Enrolled-Identity Routing"
description: "Six of seven tested A2A hosts sent a request addressed to a trusted peer to an attacker-controlled endpoint that had registered the same display name. The fix is identity enrollment, not name hygiene."
tags:
  - security
  - multi-agent
  - tool-agnostic
  - arxiv
aliases:
  - agent name collision attack
  - origin-bound agent identity
  - presentational agent names
last_reviewed: 2026-09-24
maturity: emerging
status: current
---

# Route Agent Peers by Enrolled Identity, Not Card Name

> A peer's display name is text that peer controls. Key a route on it and a resolver tie-break decides which endpoint receives the request.

Multi-agent hosts read a remote Agent Card and turn it into a local agent, a generated tool, a workflow target, or a broker topic. When the key for that local object is the card's `name` field, two peers can claim one key. Across seven pinned open-source implementations, "in all six client-style integrations, dispatch selected B's bound client or endpoint while the legitimate A binding was not invoked" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)). The seventh, Solace Agent Mesh, collapsed both peers onto one broker address. A2A permits the mapping without requiring it: the spec "neither requires name uniqueness nor instructs a host to build routes[card.name]".

## Five conditions decide whether this is your problem

All five are necessary, so a mesh that breaks one has no collision surface ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)):

1. Both peers are admitted to the same host, registry, tool set, workflow, or broker namespace.
2. The attacker can publish or refresh its own card, or has compromised an admitted peer that can.
3. Its registration wins the resolver by order, normalization, or broker binding state.
4. Something later selects the peer by that ambiguous local name. "A client that sends directly to a fixed endpoint has no collision surface."
5. A trust differential exists. "If A and B are fully interchangeable for every routed task, the impact can shrink to correctness or availability."

Condition 1 also sets the threat model: "The attacker is inside the agent admission boundary but remains outside A and the host." Signed cards and a vetted registry do not close this, because the attacker already passed both.

## What to change

Give every admitted peer an identifier the operator or registry controls, bind it to the authenticated origin, and resolve every route through it. "Names may appear in user interfaces and model context, but workflow edges, tool registries, authorization, and broker topics should resolve through the stable ID" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)). Attach credentials after that resolution, never from a card-derived name. Where a name-only API is unavoidable, reject exact and normalization-equivalent duplicates instead of picking a winner. Carry the identifier past the process edge too: "An in-memory stable registry does not help if two peers can bind the same name-derived broker route."

## Why it works

What makes a duplicate dangerous is the position it occupies, not the duplication. A collision becomes exploitable "when the host instead uses the card name as an authority-bearing selector, permits two distinct peers to share it, and then uses the ambiguous value to select a transport or execution object" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)). Resolution then runs on registration timing — first match in an agent tree, last write in a client map, last-retained in a function-tool registry — and timing is not an authorization property. An enrolled identifier moves the selector to a value the peer cannot write, so the resolver's tie-break never runs on attacker input. Seven inspected paths avoided the substitution, with controls that differ and are not equally strong: Agno routes by an operator-controlled identifier, several frameworks reject duplicate names, and python-a2a only suffixes collisions. The control exists in shipped code, but not every variant of it is sufficient.

## When this backfires

The measured damage is narrower than "name collision" suggests: "The number of demonstrated direct A-specific credential transfers in these tested bindings was 0," and "No tested target transferred an A-owned in-process tool object to B or deterministically executed a privileged A or host action solely because of the name collision" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)). The proven outcome is a request delivered to the wrong peer. Score the deployment path, not the duplicate.

Four situations where the work does not pay:

- Clients that post to a configured URL with no name lookup. Condition 4 fails, so enrollment adds a namespace and buys nothing.
- Meshes with no trust differential between peers, where a duplicate is a correctness bug and duplicate rejection at registration is the cheaper control.
- Deployments where only the operator authors cards and no registry accepts self-published refreshes. Conditions 2 and 3 both fail.
- Any partial fix that leaves the graph usable. Suffixing the loser is the common one: it "prevents silent replacement but can create unstable aliases; a stable authenticated identifier is preferable". Logging a warning is weaker still, because "a warning is not a security control if the ambiguous graph remains usable".

The subtlest is an identifier added without an origin binding: "A stable but self-asserted ID can still be stolen."

Read the prevalence numbers with the paper's own caveat. The corpus "is purposive rather than statistically representative", and a code search that found the unsafe assignment across 83 public repositories "measures propagation, not prevalence".

## Example

**Before** — the shape the study found in at least six first-party A2A sample paths, which "fetched cards from configured addresses, stored connection objects under card.name, and later dispatched by that key" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)):

```python
clients[card.name] = A2AClient(card.url)   # remote text becomes the routing key
target = clients[requested_name]           # a later peer replaces both card and transport
```

**After** — three implementations the same study inspected and found not vulnerable, each keeping the selector off the card:

| Implementation | Control |
|---|---|
| Agno | "routing uses an operator-controlled agent identifier rather than the card display name" |
| Strands Agents SDK TypeScript | "exact and normalized-equivalent tool names are rejected" |
| Microsoft Agent Framework Python | "duplicate workflow executor identifiers are rejected" |

The regression test is one case: "Register two distinct origins or resources with identical and normalization-equivalent names. Registration must fail clearly, or stable-ID dispatch must remain bound to the intended endpoint regardless of order" ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)).

## Key Takeaways

- A remote display name is peer-controlled text. Six of seven tested A2A hosts routed a trusted peer's request to an attacker-controlled endpoint that reused the name ([Arun Kumar, arXiv:2609.27624v1](https://arxiv.org/abs/2609.27624v1)).
- Route on an identifier the operator or registry assigns and bind it to the authenticated origin. Keep the name for interfaces and model context only.
- Attach credentials and delegated scopes after identity resolution, never from a card-derived name.
- The proven impact is wrong-peer delivery, not privilege inheritance. The study demonstrated zero credential transfers and zero tool transfers.
- Name hygiene is not the fix. Suffixing creates unstable aliases and a warning leaves the ambiguous graph usable.

## Related

- [Agent Cards: Capability Discovery Standard for AI Agents](../standards/agent-cards.md) — the card format whose `name` field this page tells you not to route on
- [Closed-World Tool Call Resolution Before the Permission Gate](closed-world-tool-call-resolution.md) — the same collapse one layer down, where two MCP servers share a tool name inside one host registry
- [Designing Agent Plugins to Survive Co-Installation](../patterns/agent-design/plugin-co-installation-safety.md) — name prefixing as the remedy when the colliding parties are installed bundles rather than routable peers
- [Entity Binding Failures in Tool-Augmented Agents](../patterns/anti-patterns/entity-binding-failures.md) — the model binding the wrong entity from an ambiguous reference, with no router in the path
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](per-caller-identity-for-agent-tool-calls.md) — which identity a call carries once the route is settled
