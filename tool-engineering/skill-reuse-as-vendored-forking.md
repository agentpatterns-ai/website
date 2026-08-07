---
title: "Skill Reuse as Vendored Forking"
term: "Vendored Skill Fork"
description: "Reusing a SKILL.md is a one-time near-verbatim copy that silently forks from its source — bind project specifics at adoption and track upstream only where the contract is coupled to a moving source."
aliases:
  - vendored skill fork
  - one-time skill copy
  - skill fork on adoption
tags:
  - tool-engineering
  - agent-design
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-07-03
maturity: emerging
---

# Skill Reuse as Vendored Forking

> A reused SKILL.md is a one-time verbatim copy that silently forks from its source — treat it as a vendored dependency, not a live one.

Reusing a skill from a registry is not subscribing to it. The first large-scale study of `SKILL.md` files as software artifacts found that adoption "largely behaves as a one-time copy that developers rarely synchronise with upstream revisions" ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)). Across 2,462 recovered reuse links, 1,841 (74.8%) were adopted near-verbatim at ≥0.99 body similarity; only 25.2% diverged at all on entry ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)). You own the copy the moment you make it, and it will not keep itself current.

## When the vendored-fork stance pays off

The discipline is worth its overhead only under the conditions the reuse data marks out ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)):

- The skill will outlive the task. 53% of reused skills are never modified after adoption, so whatever you bind at copy time is what runs for the life of the skill — get the project-specific paths, references, and activation triggers right up front, because nobody revisits them.
- The source keeps moving. Among skills never locally updated, 40.2% had their upstream source updated after adoption, with the change never pulled in; among locally-updated skills whose upstream also changed, 62.3% diverged independently rather than re-incorporating the upstream fix. Only these coupled-to-a-moving-source skills justify an upstream-change subscription.
- Provenance matters for review or audit. A verbatim copy carries no record of where it came from unless you add one; multi-author libraries need that link to review or re-sync later.

If none of these hold — a stable, general-purpose skill you will never touch again — copy-and-forget is the rational low-cost choice, and adding tracking machinery is pure overhead.

## What actually changes on adoption

The changes adopters make are narrow, which is why the vendored-fork framing fits. They are overwhelmingly additive — additions outnumber removals 2.7 to 1 — and re-ground the skill to its host project: reworking operational specs, rewiring reference pointers, supplying activation metadata ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)).

The behavioral contract stays near-untouched. How a skill interacts with users, monitors runtime state, and recovers from failures rank lowest in revision — user interaction changed in 1.6% of customization diffs, runtime-state monitoring in 0.5% ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)). Adopters inherit those rules almost verbatim, so the adoption review is small and specific: check the bindings, spot-check the inherited contract, stop there.

## Why it works

Skills are "editable natural language interleaved with executable code," which makes them "unusually mutable" compared to versioned packages, and no reliable distribution or sync path exists — so adoption defaults to a one-time copy rather than a tracked dependency ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)). A supply–demand split explains the shape of the edits that do happen: centralized registry skills encode broadly reusable, general-purpose coding capability whose behavioral contract is already correct, while adopters only re-ground project-specific bindings to their host project ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)). The correct general contract arrives ready to inherit, so effort clusters on bindings — exactly how a vendored library's interface survives untouched while its call sites adapt.

## When this backfires

- Throwaway or prototype skills. Provenance records, upstream-change subscriptions, and version pinning are wasted ceremony on a skill used once and discarded — see [Throwaway Prototype Skill](../workflows/throwaway-prototype-skill.md).
- Fast-moving upstream you want to track. Freezing a copy is the wrong call when the skill wraps a rapidly-fixed API. The 40.2% who silently miss upstream fixes ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)) are the cautionary case, but the remedy is a live link — a submodule or package that pulls fixes — not more fork discipline.
- Small solo libraries. With a handful of skills you wrote and nobody else adopted, there is no upstream to sync and no provenance to track; the ritual is overhead, the same small-library caveat [Skill Library Evolution](skill-library-evolution.md) draws.
- Mistaking near-verbatim for safe. A copy that matches its source at ≥0.99 similarity ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)) still inherits any latent defect in the source verbatim; high similarity is a drift signal, not a correctness guarantee.

## Example

Record the fork at adoption so a later reviewer can tell what is inherited from what is local. This provenance block sits at the top of the copied `SKILL.md`; the angle-bracketed parts are what you fill in per adoption:

```markdown
## Provenance
- Source: <registry>/<skill> @ <version-or-commit> (adopted <date>)
- Upstream: <repo URL>
- Local bindings (this fork owns these):
  - migrations path rebound from ./migrations to db/migrations
  - added activation triggers: "schema change", "add column"
- Inherited verbatim — re-review before editing:
  - failure-recovery and rollback steps
  - user-confirmation prompts before destructive actions
```

The block names the source and pinned version, separates the bindings this fork owns from the behavioral contract it inherits, and keeps the upstream link a later reviewer needs to re-sync — the tracking a one-time copy otherwise loses.

## Key Takeaways

- A reused skill is a fork the moment you copy it: 74.8% of reuse is near-verbatim and 53% is never modified again, so bind project specifics at adoption ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)).
- Only subscribe to upstream for skills coupled to a moving source — 40.2% of unmodified copies already miss upstream fixes ([Gao et al., 2026](https://arxiv.org/abs/2607.00911)); the rest are copy-and-forget by design.
- The edits that happen are additive and re-ground bindings; the user-interaction, runtime, and failure contract is inherited near-verbatim, so keep the adoption review small and specific.
- Skip the machinery for throwaway skills, solo libraries, and fast-moving upstreams where a live dependency beats a frozen fork.
- Record provenance and version at copy time — a verbatim fork loses the link back to its source unless you write it down.

## Related

- [Skill Library Evolution](skill-library-evolution.md) — the lifecycle-governance view of the same libraries; this page is the empirical account of how reuse actually behaves within it
- [Skill Library Technical Debt](skill-library-technical-debt.md) — the library-time debt that additive-only, never-resynced forks accumulate
- [Skill Authoring Patterns](skill-authoring-patterns.md) — how to write the skill that later gets forked; this page covers what happens to it after adoption
- [Contractual Skill Files](../instructions/contractual-skill-files.md) — structuring the inherited contract as named fields so a reviewer can check a fork's bindings fast
- [Tool Cloning and Provenance Assessment](tool-cloning-provenance-assessment.md) — why raw marketplace counts overstate diversity when most entries are near-verbatim clones
- [Skill Packs: Registry Distribution Needs Pinning Discipline](../instructions/skill-pack-registry-distribution.md) — the distribution side: what a registry pack's update channel does and does not give a team
