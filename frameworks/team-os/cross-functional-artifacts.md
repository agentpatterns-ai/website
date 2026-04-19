---
title: "Cross-Functional Knowledge Artifacts"
description: "A per-discipline artifact matrix pinned to a feature-index routing file lets one coding agent answer cross-functional questions across PM, analytics, engineering, and operations."
tags:
  - context-engineering
  - workflows
  - human-factors
  - tool-agnostic
---

# Cross-Functional Knowledge Artifacts

> One coding agent can answer across disciplines when every discipline commits the same shape of artifact and a single routing index joins them by feature.

Team OS treats the repo as a shared brain, which only pays off if each discipline contributes in a form the agent can compose. The lever is a per-discipline **artifact matrix** — each role owns a subfolder with fixed filename conventions — pinned to a root `feature-index.yaml` mapping every feature to its artifacts across roles ([source](https://www.news.aakashg.com/p/claude-code-team-os)). Shape consistency, not content richness, lets the agent join analytics to product to engineering in one query.

## Preconditions

Skip these and the matrix degrades to a folder tree nobody trusts:

- **Markdown + Git literacy in at least one lead per discipline.** Docs-as-code adoption stalls without it; Grab shipped a WYSIWYG + preview layer before non-engineering contributors engaged ([Grab Engineering](https://engineering.grab.com/facilitating-docs-as-code-with-markdown)).
- **Convention enforced via hierarchical `CLAUDE.md` and lint**, not prose style guides. A root `CLAUDE.md` routes the agent to per-folder files pinning filename patterns, frontmatter, and the feature-index entry ([hierarchical CLAUDE.md](../../instructions/hierarchical-claude-md.md), [CLAUDE.md convention](../../instructions/claude-md-convention.md)).
- **Launch gate.** No feature ships until its metrics, queries, schemas, and playbooks are committed ([source](https://www.news.aakashg.com/p/claude-code-team-os)). Without this, the matrix decays silently — synthesis queries miss artifacts nobody committed.
- **Skill-enforced shape at write-time.** Free-form content in any one discipline breaks aggregation across all. See [skill authoring patterns](../../tool-engineering/skill-authoring-patterns.md) and [consistent-format customer capture](consistent-format-customer-capture.md).

## The Mechanism

Three elements compose the matrix:

1. **`feature-index.yaml` at the repo root** — a hand-maintained YAML mapping each feature to its PRD, RFC, schemas, queries, dashboards, investigations, and ticket IDs. This is the explicit join key; the agent does not infer relationships from filenames.
2. **Per-discipline subfolders** under `product-development/` (`product/`, `analytics/`, `engineering/`, `data-engineering/`) and a sibling `team/` — each owning its artifact taxonomy ([functional folder taxonomy](functional-folder-taxonomy.md)).
3. **Skill files that enforce shape** (`.claude/skills/customer-call-summary.md`, `.claude/skills/funnel-analysis.md`) — dictating frontmatter, section order, and required fields so artifacts are greppable across instances ([source](https://www.news.aakashg.com/p/claude-code-team-os)).

Retrieval becomes deterministic: glob the folder for the artifact type, read the feature-index for cross-discipline siblings, compose. No embeddings required for structured lookups.

## Why It Works

Consistent shape converts retrieval from a similarity problem into a lookup: glob a folder, read a YAML key. Embedding distance does not encode path hierarchy or schema membership; the feature-index encodes those relationships explicitly, making them queryable in O(1) ([structured domain retrieval](../../context-engineering/structured-domain-retrieval.md)).

## The Artifact Matrix

Paths and artifact types are drawn from the [Team OS example repo](https://github.com/in-the-weeds-hannah-stulberg/team-os-example-repo) and the [Aakash Gupta writeup](https://www.news.aakashg.com/p/claude-code-team-os).

| Discipline | Canonical artifact shape | Enforcement mechanism | Synthesis query unlocked |
|------------|--------------------------|------------------------|--------------------------|
| **Analytics** | `analytics/{area}/metrics/`, `queries/{area}/*.sql`, `schemas/`, `playbooks/*.md`, `investigations/{date}-{slug}.md`, `data-catalog.yaml` | `analytics/CLAUDE.md` + analyst-audited `playbooks/` define methodology | "How do we calculate generation success rate? Show the metric definition, the SQL, and the schema." |
| **Product** | `product/PRDs/{area}/{feature}.md`, `customers/{account}/{date}-call.md`, `competitive-research/`, `strategy/`, `launch-emails/` | `customer-call-summary.md` skill dictates frontmatter + sections for every call | "Who did I meet with over the last two weeks and what did I learn?" |
| **Engineering** | `engineering/rfcs/{area}/{feature}-rfc.md`, `plans/{area}/{feature}.md`, `bug-investigations/bug-{date}-{slug}/investigation-plan.md` | `engineering/CLAUDE.md` + filename conventions by area | "Summarize the RFC and linked plan for the credit-depletion feature." |
| **Data engineering** | `data-engineering/rfcs/`, `plans/` — sharded by product area, mirrors engineering shape | Shared filename convention with engineering; pinned via feature-index | "What schema changes are planned for billing this quarter?" |
| **Operations / Team** | `team/onboarding/`, `team/retros/`, roster + Slack IDs in root `CLAUDE.md` | Root `CLAUDE.md` keeps the team roster under ~500 tokens ([source](https://www.news.aakashg.com/p/claude-code-team-os)) | "Who owns analytics for billing and what is their Slack handle?" |

Design stays in Figma as a feature-index link rather than relocating into the repo; tickets remain in Jira. The index is a link hub for those, not an artifact store.

## N=1 Caveat

Primary evidence for the full matrix is one practitioner (Hannah Stulberg, PM at DoorDash) in one writeup and a reference repo. Individual mechanisms — hierarchical `CLAUDE.md`, skill-enforced shapes, structured retrieval — are corroborated elsewhere. The integrated cross-discipline synthesis claim is single-witness. Treat the matrix as a case study to adapt, not a measured standard.

## Example

**Demonstrated (within-discipline synthesis)**: The source writeup documents this working query against the analytics subfolder ([source](https://www.news.aakashg.com/p/claude-code-team-os)):

> *"How do we calculate generation success rate? Show the metric definition, the SQL, and the schema."*

The agent resolves this by reading `analytics/metrics/generation-success-rate.md`, pulling `analytics/queries/billing/generation-success.sql`, and joining the `schemas/` entry for the relevant table — three artifacts, one glob pattern per type, zero embedding inference.

**Aspirational (cross-discipline synthesis)**: With a populated feature-index, a query like *"Why did churn spike after the pricing RFC?"* would have the agent read `feature-index.yaml` for `billing/credit-usage`, pull the engineering RFC, the analytics churn investigation, and the credit-burn SQL, then compose one answer citing all three. This cross-discipline join is the design target — not demonstrated verbatim in the source material.

## When This Backfires

- **Small teams** — overhead is fixed; synthesis benefit scales with artifact count. Below ~3 disciplines and ~10 active features, a shared root `CLAUDE.md` and docs folder delivers comparable retrieval at lower cost.
- **Inconsistent artifact quality** — one undisciplined discipline poisons cross-discipline queries for every feature it touches. Enforce the launch gate.
- **No git-fluent anchor per discipline** — Markdown/Git literacy in at least one role is required for shape conventions to hold ([Grab Engineering](https://engineering.grab.com/facilitating-docs-as-code-with-markdown)).

## Key Takeaways

- The routing index + per-discipline subfolders + skill-enforced shape are the three mutually-dependent mechanisms. Dropping any one collapses cross-discipline synthesis.
- Preconditions dominate outcomes. Markdown/Git friction for non-engineers is the most common failure mode ([Grab](https://engineering.grab.com/facilitating-docs-as-code-with-markdown), [docs-as-code guide](https://www.writethedocs.org/guide/docs-as-code/)); convention must be enforced by instruction files and lint, not prose.
- Primary evidence is N=1. The matrix and mechanism are sound; generalization is not yet measured.
- Multi-discipline synthesis queries are the payoff but the weakest-demonstrated claim — build the matrix to unlock them, do not assume they arrive for free.

## Related

- [Team OS](index.md) — the parent framework this matrix anchors
- [Functional folder taxonomy](functional-folder-taxonomy.md) — the ownership cut the matrix rides on
- [Consistent-format customer capture](consistent-format-customer-capture.md) — the per-discipline deep dive for one row of this matrix
- [Hierarchical CLAUDE.md](../../instructions/hierarchical-claude-md.md) — how root and per-folder conventions are delivered to the agent
- [Structured domain retrieval](../../context-engineering/structured-domain-retrieval.md) — why consistent shape enables deterministic retrieval
- [Skill authoring patterns](../../tool-engineering/skill-authoring-patterns.md) — the write-time enforcement layer for artifact shape
- [Plan mode for knowledge artifacts](plan-mode-knowledge-artifacts.md) — using plan mode to author PRDs, strategy memos, and architectural briefs in the Team OS structure
- [Plan files as resumable artifacts](plan-files-resumable-artifacts.md) — sibling artifact pattern for committing plan state across sessions and cross-functional review
