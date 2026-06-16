---
title: "Layered Domain Architecture: A Prescriptive Default for Agent-Built Code"
term: "Layered Domain Architecture"
description: "Pin a fixed intra-domain layer order — Types → Config → Repo → Service → Runtime → UI — with directional dependency rules enforced by a linter so agents place new code in the same slot every session."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - forward-only layer stack
  - prescriptive layer ontology
last_reviewed: 2026-06-12
maturity: established
---

# Layered Domain Architecture

> Layered domain architecture pins one intra-domain order with downward-only dependencies a linter enforces, so an agent slots new code into the same layer every session.

## The Default Layer Order

The [walkinglabs/learn-harness-engineering SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md) prescribes this directional flow within a business domain:

`Types → Config → Repo → Service → Runtime → UI`

| Layer | Owns | May depend on |
|-------|------|---------------|
| Types | Domain types, value objects, errors | nothing inside the domain |
| Config | Static configuration, feature flags, environment shape | Types |
| Repo | Repositories and adapters — the only DB / external-state surface | Types, Config |
| Service | Domain logic and use cases | Types, Config, Repo |
| Runtime | Request/event handlers, schedulers, transports | Types, Config, Repo, Service |
| UI | Views, CLI, API responses | everything below |

Two rules close the model ([ARCHITECTURE.md template](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/repo-template/ARCHITECTURE.md)): *"Lower layers must not depend on higher layers"* and *"UI must not bypass runtime or service contracts."* Data access enters exclusively through Repo, and shared utilities stay generic.

## Cross-Cutting Concerns Enter Through Adapters

Auth, telemetry, external APIs, and feature flags are not "the Repo of another layer" — they are cross-cutting. The SOP routes them through *"explicit providers or adapters"* so they never become ambient imports any layer can reach for ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)). The ARCHITECTURE.md template keeps a named-boundary table per concern, so the agent sees one approved entry point per concern, not a global menu.

## Mechanical Enforcement Is Not Optional

A rule that lives only in documentation decays; the SOP requires *"one executable guardrail for the highest-cost violation"* ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)). Two ecosystem-standard linters cover it:

- **Python**: [`import-linter`](https://github.com/seddonym/import-linter/blob/main/docs/contract_types/layers.md) `layers` contracts *"enforce a 'layered architecture', where higher layers may depend on lower layers, but not the other way around"* — refusing cross-direction imports, including indirect ones through unrelated modules.
- **JS/TS**: [`dependency-cruiser`](https://github.com/sverweij/dependency-cruiser) — declarative `forbidden` rules that validate dependencies against your own rules and report violations at lint time and in CI.

Run the check in CI *and* a pre-commit hook. A boundary that only fails after merge is one the agent has already crossed.

## Why Agents Benefit

A fixed layer ontology shrinks the placement decision. Without it, every new function is a four-way search — `utils/`, `services/`, `helpers/`, or a new module — and agents pick locally plausible homes (the file last edited, a generic dumping ground), so the codebase accretes parallel hierarchies across sessions. A forward-only stack collapses placement to one question: *"which layer owns this responsibility?"* Fowler names the mechanism for the three-layer case — the layering *"allows me to reduce the scope of my attention"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)) — and each placement step narrows the search to one layer's API surface. The linter closes the loop so the rule survives the session, which is the SOP's definition-of-done: *"A fresh agent can tell which layer owns a change"* ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)).

## When This Backfires

The fixed layer order is an *intra-domain* default, not a top-level decomposition. It backfires when:

- **The codebase has more than one bounded context.** Fowler's correction: once a layer *"gets too big you should split your top level into domain oriented modules which are internally layered"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)). A flat top-level `services/`, `repos/`, `ui/` hides cross-domain reaches the linter cannot see. Decompose by domain first; apply the layer order *inside* each domain.
- **The system is event-driven, pipeline, or batch.** Runtime/UI collapses (no UI; the "request" is an event) and Service often calls Runtime adapters as peers. Forcing six layers produces empty shells and DTO ping-pong. Drop the layers that do not pay — a [scaffold-architecture-taxonomy](harness-design-dimensions.md) choice rather than a fixed default.
- **The project is small or short-lived.** Fowler scopes layering to "information-rich" programs. On a one-screen CLI or a one-week prototype the six-layer setup is pure overhead.
- **The rule is documentation-only.** An unenforced layer order in `ARCHITECTURE.md` is invisible to the agent at edit time — the linter is the boundary, the doc is the rationale.

A second failure is organizational: do not let the layer ontology shape teams. Fowler names *"separating development teams by these layers"* an anti-pattern that *"adds distance between developers and users"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)).

## Example

A Python service with a single `billing` domain. The intra-domain layout follows the prescribed order and the linter contract refuses cross-direction imports:

```ini
# .importlinter
[importlinter]
root_package = billing

[importlinter:contract:billing-layers]
name = billing layers
type = layers
layers =
    billing.ui
    billing.runtime
    billing.service
    billing.repo
    billing.config
    billing.types
```

An agent that drafts a new `billing/service/refund.py` may import from `billing.repo`, `billing.config`, and `billing.types`; an `import` from `billing.runtime` or `billing.ui` is refused at lint time, before the change can land. The agent gets feedback within its own loop rather than after merge.

When the codebase later grows a second domain `subscriptions`, the top-level structure becomes `billing/` and `subscriptions/` — each carrying its own internal six-layer order — rather than a global `services/`, `repos/`, `ui/`. A second contract enforces no cross-domain repo or service reaches without going through an adapter.

## Key Takeaways

- Pin the order `Types → Config → Repo → Service → Runtime → UI` inside a domain and forbid upward imports; the SOP and the import-linter `layers` contract make the rule executable, not aspirational.
- The mechanism is decision-space reduction: a fixed slot for every responsibility collapses placement from a search to a lookup, and the lint contract survives the agent's session ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html); [import-linter](https://github.com/seddonym/import-linter/blob/main/docs/contract_types/layers.md)).
- Cross-cutting concerns route through named adapters from `ARCHITECTURE.md`, not ambient imports — one approved entry point per concern.
- This is an intra-domain default. Multi-domain systems decompose by domain first, then layer inside; event-driven, batch, and prototype codebases drop the layers that do not pay rather than synthesizing them.

## Related

- [Separation of Knowledge and Execution in Agent Systems](separation-of-knowledge-and-execution.md)
- [Layered Mutability: Governing Persistent Self-Modifying Agents](layered-mutability.md)
- [Discrete Phase Separation](discrete-phase-separation.md)
- [Scaffold Architecture Taxonomy for Coding Agents](harness-design-dimensions.md)
- [Agent-First Software Design](agent-first-software-design.md)
