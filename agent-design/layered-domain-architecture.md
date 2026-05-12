---
title: "Layered Domain Architecture: A Prescriptive Default for Agent-Built Code"
description: "Pin a fixed intra-domain layer order — Types → Config → Repo → Service → Runtime → UI — with directional dependency rules enforced by a linter so agents place new code in the same slot every session."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - forward-only layer stack
  - prescriptive layer ontology
---

# Layered Domain Architecture

> Pin one intra-domain layer order — `Types → Config → Repo → Service → Runtime → UI` — with downward-only dependencies enforced by a linter, so an agent places new code in the same slot every session instead of inventing a new ad-hoc layout each time.

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

Two rules close the model ([ARCHITECTURE.md template](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/repo-template/ARCHITECTURE.md)): *"Lower layers must not depend on higher layers"* and *"UI must not bypass runtime or service contracts."* Data access enters exclusively through Repo; *"shared utilities must remain generic and must not accumulate domain logic."*

## Cross-Cutting Concerns Enter Through Adapters

Auth, telemetry, external APIs, and feature flags are not "the Repo of another layer" — they are cross-cutting. The SOP routes them through explicit providers or adapters so they do not become ambient imports that any layer can reach for: *"Cross-cutting concerns should enter through explicit providers or adapters. Shared utils stay outside the domain and should not accumulate domain logic"* ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)). The ARCHITECTURE.md template maintains a named-boundary table for each concern so the agent sees one approved entry point per concern, not a global menu.

## Mechanical Enforcement Is Not Optional

The SOP is explicit that a rule that lives only in documentation decays: *"Add one executable guardrail for the highest-cost violation"* and *"At least one important boundary is enforced mechanically"* ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)). The two ecosystem-standard linters:

- **Python**: [`import-linter`](https://github.com/seddonym/import-linter/blob/main/docs/contract_types/layers.md) `layers` contract — *"Layers contracts enforce a 'layered architecture', where higher layers may depend on lower layers, but not the other way around."* The contract takes an ordered list of modules and refuses cross-direction imports, including indirect imports through unrelated modules.
- **JS/TS**: [`dependency-cruiser`](https://github.com/sverweij/dependency-cruiser) — declarative `forbidden` rules; *"validates [dependencies] against (your own) rules"* and *"reports violated rules"* at lint time and in CI.

The check belongs in CI and in a pre-commit hook. A boundary that only fails after merge is a boundary the agent has already crossed.

## Why Agents Benefit

A fixed layer ontology shrinks the placement decision an agent makes when adding new code. Without it, every new function is a four-way search: `utils/`, `services/`, `helpers/`, or a new module — and agents tend to pick locally plausible homes (the file they were last editing, or a generic dumping ground), so the codebase accretes parallel hierarchies across sessions. With a fixed forward-only stack, placement collapses to a single question: *"which layer owns this responsibility?"* Fowler describes the same mechanism for the three-layer case — *"[the layering] allows me to reduce the scope of my attention by allowing me to think about the three topics relatively independently"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)) — and the agent benefit is identical: at every placement step the search space narrows to one layer's API surface. The mechanical linter closes the loop so the rule survives the agent's session.

The SOP's definition-of-done captures the test directly: *"A fresh agent can tell which layer owns a change"* ([walkinglabs SOP](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/sops/layered-domain-architecture.md)).

## When This Backfires

The fixed layer order is an *intra-domain* default, not a top-level decomposition. It backfires when:

- **The codebase has more than one bounded context.** Fowler's correction: *"As an application grows, each layer can get sufficiently complex on its own that you need to modularize further… once any of these layers gets too big you should split your top level into domain oriented modules which are internally layered"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)). A flat top-level `services/`, `repos/`, `ui/` hides cross-domain reaches that the linter cannot see. Decompose by domain first; apply the layer order *inside* each domain.
- **The system is event-driven, pipeline, or batch.** Runtime/UI collapses (no UI; the "request" is an event) and Service often calls Runtime adapters as peers. Forcing the six layers produces empty shells and DTO ping-pong. Drop the layers that do not pay rather than synthesizing them.
- **The project is small or short-lived.** Fowler explicitly scopes layering to "information-rich" programs. On a one-screen CLI or a one-week prototype the six-layer setup is overhead and the agent spends most of its turns generating boilerplate between layers.
- **The rule is documentation-only.** A layer order written in `ARCHITECTURE.md` but unenforced is invisible to the agent at edit time. The SOP's *"Definition Of Done"* requires that *"at least one important boundary is enforced mechanically"* — the linter is the boundary, the doc is the rationale.

A second organizational failure: do not let the layer ontology shape teams. Fowler names it as an anti-pattern: *"separating development teams by these layers… separating the layers into teams adds distance between developers and users"* ([Fowler, 2015](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)).

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
- [Scaffold Architecture Taxonomy for Coding Agents](scaffold-architecture-taxonomy.md)
- [Agent-First Software Design](agent-first-software-design.md)
