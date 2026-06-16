---
title: "Designing for Agent Consumers (Agent Experience)"
term: "Agent Experience"
description: "Design your public SDK, CLI, API, and docs so an agent consumer can discover, invoke, and recover from them — the Agent Experience (AX) discipline."
tags:
  - tool-engineering
  - tool-agnostic
aliases:
  - "Agent Experience discipline"
  - "designing for agent consumers"
last_reviewed: 2026-06-13
maturity: established
---

# Designing for Agent Consumers (Agent Experience)

> Design your public SDK, CLI, API, and docs so an agent consumer can discover, invoke, and recover from them — it reads the surface literally.

Agent Experience (AX) is the discipline of designing the **external developer surface you ship** — SDK, CLI, API, docs — so an AI coding agent can use it correctly as a first-class consumer. The term was coined by Netlify's Mathias Biilmann in January 2025 as "the holistic experience AI agents will have as the user of a product or platform" ([Biilmann, *Introducing AX*](https://biilmann.blog/articles/introducing-ax/)); Microsoft's 2026 series applies it to coding agents reading your technology ([Mastykarz, *How AI coding agents actually use your technology*](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)).

## When This Applies

AX is a design concern only when you **own an external surface that agents consume**. It earns its cost when:

- You ship an SDK, CLI, API, or public docs that agents call on a developer's behalf.
- The surface is stable enough that agent-legible signatures and [structured errors](rfc9457-machine-readable-errors.md) will not be rewritten next sprint.

It does not apply to internal-only apps with no third-party agent traffic, to single-human tools where agent-shaping competes with human affordances, or to pre-PMF surfaces still in flux. In those cases the rules below are overhead.

## AX Is Not Harness Engineering

AX shapes the surface the agent *calls from outside*. It is distinct from the two adjacent concerns this site already covers:

- [Harness Engineering](../agent-design/harness-engineering.md) shapes the **agent's own scaffold** — context window, tools, loop — which the library author does not own.
- The [AX Stack](../agent-design/ax-stack-layered-model.md) and [AX/UX/DX Triad](../agent-design/ax-ux-dx-triad.md) are **internal diagnostics**: where a failure lives, and how to route data to the model versus the user. They sit inside the harness, not on your public surface.

AX is the surface-design discipline that those diagnostics point *at* when the failure is "the SDK itself is not legible to an agent."

## The Design Rules

Each rule maps to a tactic page that develops it in depth:

1. **Write errors as recovery instructions, not status codes.** Agents "have no intuition to fall back on. They take your error message literally"; a cryptic `Error: operation failed` leaves the agent unable to self-correct ([Mastykarz](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)). Emit typed, structured errors with an explicit next step — see [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md).
2. **Size responses to the decision, not to completeness.** "Return too much content and the model ignores parts of it or gets confused. Return too little, and the model fills gaps with assumptions" — 3,000 tokens of docs where 200 suffice "pushed other relevant context out of the window" ([Mastykarz](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)). See [Token-Efficient Tool Design](token-efficient-tool-design.md).
3. **Name capabilities in the developer's intent vocabulary.** Discoverability is semantic: the model must bridge intent ("authentication") to your surface ("configure identity provider settings") by interpretation ([Mastykarz](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)). See [Write Tool Descriptions Like Onboarding Docs](tool-descriptions-as-onboarding.md).
4. **Keep machine-readable signatures current and discoverable.** Stale training data gives the agent "high confidence, stale information," routing it to obsolete patterns instead of your real surface ([Mastykarz](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)). Ship structured signatures (OpenAPI, typed schemas, `--help`) — see [OpenAPI Documentation Smells](openapi-documentation-smells.md).
5. **Make the full surface reachable headlessly.** An agent can only invoke what is exposed without a human in the loop — see [Headless-First Services](headless-first-services.md).

## Why It Works

An agent's only contact with your product is the literal bytes of your surface — signatures, descriptions, output, and errors — with no intuition to repair ambiguity. Because the agent "take[s] your error message literally" ([Mastykarz](https://developer.microsoft.com/blog/how-ai-coding-agents-actually-use-your-technology)), surface legibility decides whether it recovers or guesses. It needs machine-readable, structured interfaces rather than the human-readable affordances a GUI offers ([Nordic APIs](https://nordicapis.com/what-is-agent-experience-ax/)) — treating the surface as a contract read by a literal consumer is what separates AX from generic SDK polish.

## When This Backfires

- **No agent traffic.** If no agent calls your surface, structured errors and response-sizing are overhead that competes with human-facing affordances.
- **Unstable surface.** Investing in [agent-legible signatures](openapi-documentation-smells.md) before the surface stabilises pays for a design that will be rewritten.
- **The umbrella replaces the tactic.** AX adds no new rule on its own — it names a discipline and routes to tactics. A team that reads only this page and skips the tactic pages it points to has bought a buzzword, not a fix.

## Key Takeaways

- AX is the discipline of designing your **external** SDK/CLI/API/docs surface for an agent consumer — distinct from [harness engineering](../agent-design/harness-engineering.md), which shapes the agent's own scaffold.
- The agent reads your surface literally and has no intuition to repair ambiguity, so errors, response size, naming, and signatures are the design surface.
- It applies only when you own a stable surface agents consume; otherwise the rules are overhead.
- The page names the discipline and routes to tactic pages — apply the linked rules, do not stop at the umbrella.

## Related

- [Headless-First Services: APIs for Agent Consumers](headless-first-services.md) — exposing the full surface so an agent can reach every flow without a browser.
- [Machine-Readable Error Responses (RFC 9457)](rfc9457-machine-readable-errors.md) — the structured-error tactic behind rule 1.
- [AX Stack: Layered Model](../agent-design/ax-stack-layered-model.md) — the internal diagnostic that names the technology-surface layer this discipline designs.
- [AX/UX/DX Triad](../agent-design/ax-ux-dx-triad.md) — separating the agent, user, and developer audiences inside the harness; AX-as-discipline is its outward-facing complement.
- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — applying HCI principles to the interface an agent calls.
- [Human-Facing Docs in the Agent Era: Mental Models Over Reference](../human/human-docs-mental-models-agent-era.md) — the human-facing counterpart; what prose docs retain once agents absorb the machine-readable reference load.
