---
title: "Frameworks"
description: "Multi-page sections that synthesize atomic patterns into named, coherent ways of operating with AI coding assistants."
---

# Frameworks

> Multi-page expositions that synthesize atomic patterns into named, coherent ways of operating. A framework is a pattern language, not a pattern.

Individual docs pages describe atomic patterns. A framework is a named collection of patterns that together form a thesis about how to work — bigger than one page, smaller than a discipline.

## Frameworks vs. Training

| | Training (`docs/training/`) | Frameworks (`docs/frameworks/`) |
|---|---|---|
| Shape | Sequential tutorial | Orbital essays around a thesis |
| Reading order | Fixed (L0 → L1 → L2 → …) | Any order |
| Goal | Teach a skill | Articulate a way of operating |
| Completion | Reader finishes the path | Reader adopts the framework |

## Inclusion Criteria

A concept qualifies as a framework when it meets **all** of:

1. **Multi-page scope** — decomposes into ≥4 distinct pages that do not trivially collapse into each other
2. **Cross-section synthesis** — each page links to ≥2 atomic patterns in different `docs/` topic sections; frameworks compose, they do not duplicate
3. **Named artifact** — the framework has a noun-phrase identity practitioners cite by name, declared in the index `aliases:` frontmatter
4. **Unifying thesis** — the index states one claim every sub-page supports; no sub-page is orthogonal
5. **Evidence of use** — ≥1 real-world practitioner, implementation, or case study

Frameworks are captured as epics via `/save-epic` (≥4 angles required) and expanded to constituent idea issues via `/expand-epic`.
