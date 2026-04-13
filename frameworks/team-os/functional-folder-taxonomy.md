---
title: "Functional Folder Taxonomy"
description: "Name top-level folders after business functions so Claude Code's lazy CLAUDE.md discovery turns the repo path into a selector for function-scoped instructions, conventions, and glossaries."
tags:
  - agent-design
  - context-engineering
  - instructions
  - tool-agnostic
---

# Functional Folder Taxonomy

> The folder path is the routing substrate: a coding agent loads function-scoped `CLAUDE.md` based on where a query or file lands, so naming top-level folders after business functions selects the instruction surface without any in-prompt branching.

## The Mechanism: Folder Path as Routing Substrate

Claude Code's memory system loads subdirectory memory files lazily. From the [memory docs](https://code.claude.com/docs/en/memory): *"Claude also discovers CLAUDE.md and CLAUDE.local.md files in subdirectories under your current working directory. Instead of loading them at launch, they are included when Claude reads files in those subdirectories."* The path of a file being read therefore selects the instructions that accompany it — cheaper than in-prompt branching and more precise than a single monolithic root file. See [hierarchical CLAUDE.md](../../instructions/hierarchical-claude-md.md) for the atomic pattern and [progressive disclosure](../../agent-design/progressive-disclosure-agents.md) for the generalised shape.

Naming top-level folders after **business functions** (product, analytics, engineering, design, data-engineering) maps agent queries to the function whose conventions, glossary, and artifact schemas apply. The root `CLAUDE.md` stays a thin doc-index; function-level files carry function-specific rules — following [AGENTS.md as a table of contents](../../instructions/agents-md-as-table-of-contents.md).

## The Verified Structure

The canonical reference is Hannah Stulberg's [Team OS example repo](https://github.com/in-the-weeds-hannah-stulberg/team-os-example-repo/tree/main). The layout is **two-level**: top-level for out-of-scope or shared concerns, with function folders nested under `product-development/`.

```
team-os-example-repo/
├── .claude/
├── CLAUDE.md                        # doc index + team roster
├── product-development/
│   ├── CLAUDE.md                    # product-development conventions
│   ├── feature-index.yaml           # cross-function feature manifest
│   ├── product/
│   │   ├── CLAUDE.md
│   │   ├── PRDs/CLAUDE.md
│   │   └── customers/CLAUDE.md
│   ├── analytics/CLAUDE.md
│   ├── engineering/CLAUDE.md
│   ├── design/CLAUDE.md
│   └── data-engineering/CLAUDE.md
└── team/
    └── CLAUDE.md                    # roles, cadences, roster
```

The repo ships 30+ `CLAUDE.md` files nested down to sub-domain level (customer accounts, PRD collections). Each is a **navigation map, not a content file** — it points at the artifacts in its folder rather than restating them.

## Ownership Boundaries

Stulberg's rule on the [Aakash Gupta podcast](https://www.aakashg.com/hannah-stulberg-podcast/): *"each of the functional leads takes ownership of their area"* but *"the team as a whole needs to agree on the way to structure the information."* The function curates its own folder; the taxonomy itself is a cross-team artifact. CODEOWNERS enforces the review boundary; the shared root `CLAUDE.md` and `feature-index.yaml` are co-owned.

## The `feature-index.yaml` Seam

Function-first layout shreds a single launch across 4+ folders. The reference repo resolves this with a manifest — the root `CLAUDE.md` directs: *"When looking up artifacts for a specific feature (PRDs, RFCs, plans, schemas, dashboards, experiments, tickets), check `product-development/feature-index.yaml` first. It maps every feature to all related artifacts in one place."* Treat the manifest as load-bearing, not optional; without it, cross-function coordination depends on the agent stitching the feature view from folder paths alone.

## When NOT to Use

The pattern is **qualified**, not universal. Prefer feature-first or flat layouts when:

- **Matrixed staffing.** Staff spanning two functions (design engineer, data-PM) produce artifacts with no clean owner folder — see [Conway's Law caveats](https://alexkondov.com/conways-law/).
- **Frequent reorgs.** Each function reshape forces mass artifact migration and breaks cross-links ([Rappin on Conway's Law](https://noelrappin.com/blog/2024/04/conways-law/)).
- **Feature- or launch-dominant delivery.** When the unit of work is a single initiative spanning all functions, `features/<name>/{prd.md, queries.sql, rfc.md}` keeps related artifacts co-located.
- **Code-majority repos.** For engineering-dominant repos, package-by-feature (Screaming Architecture) beats folder-by-function. Team OS applies to knowledge-majority repos.
- **Cross-function PR velocity.** When a single change naturally touches 3+ folders, CODEOWNERS coordination drag dominates turnaround ([Aviator](https://www.aviator.co/blog/code-reviews-at-scale/)).
- **Regulated or PII-bearing content.** HR, legal, and finance artifacts need access controls the repo cannot enforce at folder granularity.
- **Tiny teams (≤3 contributors).** One author per function makes the ownership boundary a no-op; a flat repo with a single `CLAUDE.md` wins until the team roughly doubles.

## Example

Stulberg's DoorDash setup: a PM query about a customer call resolves to `product-development/product/customers/accounts/<account>/`. Claude Code loads that leaf `CLAUDE.md` (account-specific context and question format), plus the ancestors — `product-development/product/customers/CLAUDE.md` (customer-research conventions), `product-development/product/CLAUDE.md` (PM glossary and artifact schemas), `product-development/CLAUDE.md` (cross-function conventions and `feature-index.yaml` pointer), and the root index. A query about a SQL dashboard lands in `product-development/analytics/` and loads an entirely different conventions stack — without any of the PM-specific rules crowding the context window ([source](https://www.news.aakashg.com/p/claude-code-team-os)).

## Key Takeaways

- The mechanism is lazy subdirectory `CLAUDE.md` loading — the folder path is a selector, not a convention.
- The verified Stulberg layout is **two-level**: top-level `.claude/`, `product-development/`, `team/`; function folders nest under `product-development/`.
- Each folder's `CLAUDE.md` is a navigation map, not a content file.
- `feature-index.yaml` is the load-bearing seam that lets function-first coexist with feature-level coordination.
- The pattern fails on matrixed teams, frequent reorgs, feature-dominant work, code-majority repos, high cross-function PR velocity, regulated content, and very small teams.

## Related

- [Team OS](index.md) — the framework this page composes into
- [Hierarchical CLAUDE.md](../../instructions/hierarchical-claude-md.md) — the atomic pattern for path-scoped instruction loading
- [AGENTS.md as a table of contents](../../instructions/agents-md-as-table-of-contents.md) — the pointer-map discipline each folder's memory file follows
- [Progressive disclosure agents](../../agent-design/progressive-disclosure-agents.md) — the generalised shape this implements through filesystem structure
- [Cross-functional artifacts](cross-functional-artifacts.md) — the sibling pattern on artifact types that span function folders
