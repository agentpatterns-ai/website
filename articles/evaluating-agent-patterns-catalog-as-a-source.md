---
title: "Evaluating Agent Patterns Catalog as a Source"
description: "Source assessment of agentpatternscatalog.org — a CC BY 4.0 pattern-language catalog for agentic systems with strong shape and one-author caveats."
aliases:
  - agentpatternscatalog.org evaluation
  - agent patterns catalog source review
tags:
  - human-factors
  - tool-agnostic
last_reviewed: 2026-05-31
---

# Evaluating Agent Patterns Catalog as a Source

> A CC BY 4.0 catalog of 421 agentic patterns — useful as a citation index when co-cited with primary sources, not as an MCP server.

[Agent Patterns Catalog](https://www.agentpatternscatalog.org/) (`agentpatternscatalog.org`) is a community-licensed reference catalog for agentic-systems design patterns, maintained by independent operator Marco Nissen and grounded in the open [`agentpatternscatalog/patterns`](https://github.com/agentpatternscatalog/patterns) GitHub repository ([support page](https://www.agentpatternscatalog.org/support/)). It earns inclusion in our research source list with explicit guard-rails — cite by URL with attribution, co-cite the linked primary source on the same claim, do not wire its hosted MCP server, and distinguish it from Liu et al.'s academic catalogue of the same name ([arxiv 2405.10467](https://arxiv.org/abs/2405.10467)).

## What the catalog is

The catalog frames itself as *"A Pattern Language for Agentic Systems"* — a direct nod to Christopher Alexander's 1977 *A Pattern Language* ([catalog home](https://www.agentpatternscatalog.org/)). At time of evaluation it advertises 421 patterns, 161 compositions, 49 methodologies, 14 books (chapter-style groupings), and 90 trainings, all surfaced through a typed-relation graph: each pattern declares `specialises`, `complements`, or `alternative-to` links to its neighbours.

Each pattern page follows a Gang of Four / POSA convention: Context, Problem (italicised pressure statement), Forces, When to use, When not to use, Example, Solution (*"Therefore: …"*), What it gives you, What it costs you, References, and Provenance with GitHub commit hash, added-on date, and last-updated date. The [Toolformer pattern page](https://www.agentpatternscatalog.org/patterns/toolformer/) shows commit `4fa1213`, added 2026-04-30, last updated 2026-05-21 — provenance is per-page, not site-wide.

Machine-readable surfaces are first-class: [`patterns.json`](https://www.agentpatternscatalog.org/support/patterns.json) and [`compositions.json`](https://www.agentpatternscatalog.org/support/compositions.json) are CORS-open with a 5-minute cache, and an [llms-full.txt](https://www.agentpatternscatalog.org/support/llms-full.txt) dump targets LLM consumption.

## Why It Works as a citation source

The catalog reduces our research-fetch cost on pattern-shaped topics by serving as a **low-cost index over the primary sources we would cite anyway**. Each pattern page links out to the underlying primary references — Toolformer to [arxiv 2302.04761](https://arxiv.org/abs/2302.04761), Agent Skills to [Anthropic's agent-skills documentation](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview) — so it functions as a pre-structured starting point, not as the authority on the claim itself. This is the same mechanism that justifies our existing inclusion of [`nibzard/awesome-agentic-patterns`](https://github.com/nibzard/awesome-agentic-patterns) in `SOURCES.md`: the index is cited as the discovery surface, the primary source is cited for the claim.

The catalog's CC BY 4.0 licence and explicit attribution string (*"Agent Patterns Catalog — agentpatternscatalog.org"*) match the link-and-attribute posture our [editorial inclusion criteria](../about.md) already require — no per-page negotiation needed. Operator identity is named (Marco Nissen, [marco-nissen.com](https://marco-nissen.com)), privacy posture is minimal (server-side access logs only, no third-party trackers), and per-pattern provenance is stamped with a verifiable GitHub commit hash.

The structural match also helps. Our [`anti-patterns/`](../anti-patterns/index.md) and [`fallacies/`](../fallacies/index.md) sections already follow a context-pressure-consequence shape; the catalog's [Prompt Bloat anti-pattern](https://www.agentpatternscatalog.org/patterns/prompt-bloat/) maps onto that shape without translation, which makes cross-checking our framings against an outside catalog cheap rather than costly.

## When This Backfires

Three failure modes turn the catalog from a useful index into a liability:

**Wholesale reproduction.** CC BY 4.0 permits redistribution with attribution, but copying pattern bodies into our pages dilutes our editorial voice and produces duplicate content — a GEO and AEO negative, and a violation of our existing arxiv-style ToU posture. The acceptable form is short quote plus link, never paragraph-scale reproduction.

**Treating it as authoritative on disputed claims.** The [GitHub repository](https://github.com/agentpatternscatalog/patterns) shows commits authored solely by Marco Nissen, with 148 commits on `main`, 1 star, and 0 forks at evaluation time. This is normal for a young single-maintainer catalog, but it means peer review is light. On topics where the academic literature is unsettled (multi-agent coordination, memory architectures, evaluation methodology) the catalog is one signal among many, not the closing argument. Co-cite a primary source on the same claim or do not make the claim.

**Wiring the hosted MCP server.** The catalog exposes a hosted Model Context Protocol endpoint at `https://mcp.agentpatternscatalog.org/mcp` with tools like `find_pattern`, `recommend_recipe`, and `pattern_for_symptom` ([Use page](https://www.agentpatternscatalog.org/use/)). Adding it to a sub-agent that also holds repo-read access would close the [lethal trifecta](../security/lethal-trifecta-threat-model.md) on that principal — private data, untrusted content, egress — and is exactly the scenario our `AGENTS.md` MCP-onboarding gate exists to prevent. Per the gate, any new `.mcp.json` server with private-data access must run through `agent-readiness-audit-lethal-trifecta` before merge. This evaluation is a **citation-source decision, not an MCP-wiring decision** — the catalog goes in `SOURCES.md`, not `.mcp.json`.

A fourth, smaller risk is name collision: search engines conflate this catalog with Liu et al.'s peer-reviewed [Agent Design Pattern Catalogue](https://arxiv.org/abs/2405.10467) (CSIRO Data61, 18 architectural patterns). They are distinct artefacts with overlapping vocabulary. Citations must disambiguate.

## Recommendation

**Use as a source — with guard-rails.**

1. **Add to `SOURCES.md`** with a one-line caveat in the same form as the existing `nibzard/awesome-agentic-patterns` entry: individual patterns cited as research sources; no verbatim catalogue text; co-cite the linked primary source.
2. **Cite by pattern-page URL** with the recommended attribution string. Do not reproduce pattern bodies.
3. **Always co-cite** the pattern's linked primary source on the same claim. The catalog is the index, not the authority.
4. **Do not wire the MCP server** without first running `agent-readiness-audit-lethal-trifecta`.
5. **Disambiguate** the site catalog from Liu et al.'s CSIRO catalogue in any citation that names "Agent Patterns Catalog."

The strongest near-term uses are: scanning the [anti-patterns book](https://www.agentpatternscatalog.org/patterns/prompt-bloat/) for failure modes our own `anti-patterns/` and `fallacies/` sections have not yet named; checking the [Agent Skills pattern](https://www.agentpatternscatalog.org/patterns/agent-skills/) cross-references for tool implementations we have not covered (Cline, OpenHands, Continue are all called out as first-class); and mining the typed-relation graph for sibling-link suggestions when authoring new pages in [`patterns/`](../patterns/index.md) or [`agent-design/`](../agent-design/index.md).

## Key Takeaways

- The catalog is CC BY 4.0, single-maintainer, GoF-shaped, and grounded in a public GitHub repository — adequate for citation, light on peer review.
- Use it as an *index over primary sources*, not as the authority on a claim. Always co-cite the underlying reference.
- Do not wire its hosted MCP server without running the lethal-trifecta audit; the citation decision and the MCP decision are separate.
- Add to `SOURCES.md` with the same posture used for `nibzard/awesome-agentic-patterns`: cited individually, summarised in our own words, never reproduced wholesale.

## Related

- [AI Abundance Reshapes Software Engineering Identity](ai-abundance-engineering-identity.md)
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
- [Audit: Lethal Trifecta](../agent-readiness/audit-lethal-trifecta.md)
