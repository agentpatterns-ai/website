---
title: "Monotonic Capability Attenuation for Composition-Safe Tool Use"
term: "Monotonic Capability Attenuation"
description: "Attach a sink-specific capability budget to every value and intersect budgets through tool composition so authority can only shrink — closes the permission-laundering gap when manifests are expert-authored and flows are explicit."
aliases:
  - ChainCaps capability budget
  - composition-safe tool use
  - permission laundering defense
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-03
maturity: emerging
---

# Monotonic Capability Attenuation for Composition-Safe Tool Use

> Tag every value with a sink-specific capability budget and intersect budgets through composition — authority can only shrink, closing permission laundering.

## When This Recommendation Applies

The pattern produces a real security delta only inside these conditions ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)):

- **Expert-crafted manifests are feasible** — budgets authored by someone who understands the threat model.
- **Attacks are explicit-flow** — the adversary exfiltrates data the proxy can see (arguments, return values, chained inputs), not via timing or side channels.
- **All tool traffic traverses one observation point** — off-protocol egress (`curl` shellouts, raw HTTP, headless browsers) bypasses the proxy.
- **A token-budget margin exists** — capability metadata on every value compounds proxy overhead.

Outside these conditions, the mechanism degrades or fails silently. See [When This Backfires](#when-this-backfires).

## What Permission Laundering Is

An agent reads a confidential document, summarises it, sends the summary externally. Each per-tool check passes — read is allowed, summarise is content-agnostic, send-email is permitted to that recipient — yet the chained effect is exfiltration. The vulnerability is the composition itself, which synthesises authority no single value ever held ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)).

This is distinct from prompt injection (which corrupts the instruction channel) and from [overreaching tool calls](permission-framework-over-model.md) (which exceed scope at one call): permission laundering chains legal calls into an illegal outcome.

## How Monotonic Attenuation Works

Every value carries a **sink-specific capability budget** — the set of sinks it may reach (`{file-read, summarise}` for a confidential document; `{external-email, log}` for a user-typed recipient). The runtime tracks budgets per value, not per tool ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)).

Composition propagates budgets by **intersection**: when a tool consumes inputs `A` and `B`, its output carries `budget(A) ∩ budget(B)` — reachable by a sink only if *every* input was. Authority strictly attenuates: a value loses sinks through composition, never gains them.

```mermaid
graph TD
    D[Confidential doc<br/>budget: read, summarise]
    R[User recipient<br/>budget: external-email]
    D -->|summarise| S[Summary<br/>budget: read, summarise]
    S -->|send-email| C{budget ∩<br/>send-email?}
    R -->|send-email| C
    C -->|empty intersection| B[Denied]

    style D fill:#fbca04
    style R fill:#0e8a16,color:#fff
    style B fill:#b60205,color:#fff
```

The check at `send-email` reduces to set membership: is `external-email` in `budget(summary)`? The summary inherited the document's budget by intersection, so it is not, and the call is denied. As a transparent MCP proxy the mechanism needs no change to agent or tool servers — it sees every call, intersects budgets, and gates each sink ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)).

## Why It Works

Composition is the lever permission laundering exploits — per-tool checks each pass while the chained effect is unsafe. Monotonic intersection denies any composition that synthesises new authority, and because intersection is local the proxy needs no global plan: each interception is a set-membership check against the value's accumulated budget. The enforcement boundary shifts from "per-tool" to "per-value lifetime," the layer at which laundering occurs. This mirrors [CaMeL](camel-control-data-flow-injection.md), which encodes the same logic via a Python interpreter. Across 82 tasks on five frontier models, attack success drops from 25–68% to 0–4.8% with 96–100% benign completion preserved ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)).

## When This Backfires

The mechanism degrades or fails outside its operating envelope.

- **Naive manifests collapse the defense.** Blocking rate falls to 27.3% when budgets are authored without security expertise — close to no defense ([Jiang et al., 2026](https://arxiv.org/abs/2605.26542)). The paper names manifest quality "the dominant deployment bottleneck"; teams without a dedicated security function inherit the naive number by default.
- **Implicit flows escape.** The scope is bounded to "explicit-flow composition safety under trusted manifests and proxy-visible data movement." Causality laundering — exfiltrating data through denial signals — is invisible because no budgeted value changes hands ([Causality Laundering, 2026](https://arxiv.org/abs/2604.04035)).
- **Conjunctive emergent capability is missed.** Per-value intersection cannot detect two individually-safe values combining into an unsafe end-state. A formal result reports 42.6% of 900 real multi-tool trajectories contain at least one conjunctive dependency ([Safety is Non-Compositional, 2026](https://arxiv.org/abs/2603.15973)).
- **Off-protocol egress bypasses the proxy.** Any side channel that skips the [MCP runtime control plane](mcp-runtime-control-plane.md) — direct shell `curl`, embedded SDK calls, cached state — sits outside the mechanism's reach.
- **Token budgets compound.** Capability metadata on every value compounds the [35× MCP proxy overhead](https://www.mindstudio.ai/blog/mcp-vs-cli-agentic-workflows-token-overhead-reliability) over equivalent CLI tools; agents near context ceilings cannot absorb it without truncating reasoning.

When these conditions fail, a pragmatic alternative is to remove a leg of the [lethal trifecta](lethal-trifecta-threat-model.md) — disable egress, narrow private-data scope, or sandbox untrusted input — which closes the gap deterministically with no manifest authoring debt.

## Relation to CaMeL and the MCP Control Plane

Monotonic capability attenuation, [CaMeL](camel-control-data-flow-injection.md), and the [MCP Runtime Control Plane](mcp-runtime-control-plane.md) sit at three layers of one architecture:

| Pattern | Enforcement layer | Mechanism | Manifest authoring |
|---------|------------------|-----------|--------------------|
| [CaMeL](camel-control-data-flow-injection.md) | Dual-LLM with custom Python interpreter | Capability labels on values; policies checked at tool-call time | Per-tool policies authored alongside tool definitions |
| Monotonic capability attenuation | Transparent MCP proxy between agent and tools | Per-value capability budgets; intersection across composition | Per-sink budgets; expert-crafted required for 100% blocking |
| [MCP Runtime Control Plane](mcp-runtime-control-plane.md) | Proxy between agent and tools | Identity, rate-limit, tool-name policy per call | Identity/policy rules per tool surface |

The patterns compose: the control plane gates on identity, capability budgets gate on composition, and CaMeL-style separation handles instruction-vs-data integrity. None alone covers the others' failure modes.

## Key Takeaways

- Monotonic capability attenuation closes the permission-laundering gap by tagging every value with a sink-specific budget and intersecting budgets through composition — authority can only shrink.
- Attack success drops from 25–68% to 0–4.8% across 82 tasks on five frontier models when manifests are expert-crafted, with 96–100% benign completion preserved.
- Manifest quality is the deciding variable: naive manifests reach 27.3% blocking, expert-crafted reach 100%. Teams without security-engineering capacity will deploy the naive number.
- The mechanism is bounded to explicit-flow attacks under trusted manifests and proxy-visible data movement. Implicit flows, conjunctive emergent capabilities, and off-protocol egress are not addressed.
- A transparent MCP proxy is the deployment vehicle. The 35× token overhead of MCP versus CLI tools compounds when every value carries capability metadata — confirm context-budget margin before adopting.
- Pair with [lethal-trifecta](lethal-trifecta-threat-model.md) leg removal and [CaMeL](camel-control-data-flow-injection.md) control/data separation as a layered posture; neither alone covers the others' failure modes.

## Related

- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
